import { useState, useEffect, useRef, useCallback } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';
import ExportButtons from '../components/ExportButtons';

export default function HistorialPredicciones() {
    const [registros, setRegistros] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [toast, setToast] = useState(null);
    const [visibleCount, setVisibleCount] = useState(25);
    const [loadingMore, setLoadingMore] = useState(false);
    const [filterProducto, setFilterProducto] = useState('');
    const [filterSubcategoria, setFilterSubcategoria] = useState('');
    const [filterModelo, setFilterModelo] = useState('');
    const tableContainerRef = useRef(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const res = await api.get('/historial-predicciones?skip=0&limit=1000');
            setRegistros(res.data.registros);
        } catch (err) {
            setToast({ message: 'Error al cargar historial', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const uniqueProductos = [...new Map(registros.map(r => [r.codigo_producto, r.nombre_producto])).entries()]
        .map(([codigo, nombre]) => ({ codigo, nombre }))
        .sort((a, b) => a.nombre.localeCompare(b.nombre));

    const uniqueSubcategorias = [...new Set(registros.map(r => r.nombre_subcategoria).filter(Boolean))].sort();
    const uniqueModelos = [...new Set(registros.map(r => r.nombre_modelo).filter(Boolean))].sort();

    const filtered = registros.filter(r => {
        const matchSearch = !search ||
            (r.nombre_producto || '').toLowerCase().includes(search.toLowerCase()) ||
            (r.codigo_producto || '').toLowerCase().includes(search.toLowerCase()) ||
            (r.nombre_modelo || '').toLowerCase().includes(search.toLowerCase()) ||
            (r.motivo || '').toLowerCase().includes(search.toLowerCase());
        const matchProducto = !filterProducto || r.codigo_producto === filterProducto;
        const matchSubcategoria = !filterSubcategoria || r.nombre_subcategoria === filterSubcategoria;
        const matchModelo = !filterModelo || r.nombre_modelo === filterModelo;
        return matchSearch && matchProducto && matchSubcategoria && matchModelo;
    }).sort((a, b) => (a.fecha_archivado || '').localeCompare(b.fecha_archivado || ''));

    const handleScroll = useCallback(() => {
        const container = tableContainerRef.current;
        if (!container || loadingMore) return;
        if (container.scrollTop + container.clientHeight >= container.scrollHeight - 50) {
            if (visibleCount < filtered.length) {
                setLoadingMore(true);
                setTimeout(() => {
                    setVisibleCount(prev => Math.min(prev + 25, filtered.length));
                    setLoadingMore(false);
                }, 300);
            }
        }
    }, [visibleCount, filtered.length, loadingMore]);

    useEffect(() => {
        const container = tableContainerRef.current;
        if (container) {
            container.addEventListener('scroll', handleScroll);
            return () => container.removeEventListener('scroll', handleScroll);
        }
    }, [handleScroll]);

    useEffect(() => {
        setVisibleCount(25);
    }, [search, filterProducto, filterSubcategoria, filterModelo]);

    const formatDate = (d) => {
        if (!d) return '-';
        return new Date(d).toLocaleDateString('es-EC', { day: '2-digit', month: 'short', year: 'numeric' });
    };

    const formatDateTime = (d) => {
        if (!d) return '-';
        return new Date(d).toLocaleString('es-EC', {
            day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    };

    if (loading && registros.length === 0) {
        return (
            <div style={{ padding: '2rem', textAlign: 'center' }}>
                <div className="loading-spinner"></div>
                <p>Cargando historial...</p>
            </div>
        );
    }

    return (
        <div style={{ padding: '1.5rem' }}>
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <div>
                    <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0 }}>Historial de Predicciones</h1>
                    <p style={{ color: '#6b7280', margin: '0.25rem 0 0 0', fontSize: '0.9rem' }}>
                        Registro de predicciones archivadas ({filtered.length} en total)
                    </p>
                </div>
                <ExportButtons
                    data={filtered}
                    filename="historial_predicciones"
                    moduleName="historial_predicciones"
                    columns={[
                        { key: 'fecha_archivado', label: 'Fecha Archivo' },
                        { key: 'nombre_producto', label: 'Producto' },
                        { key: 'codigo_producto', label: 'Codigo' },
                        { key: 'nombre_modelo', label: 'Modelo' },
                        { key: 'periodo', label: 'Periodo' },
                        { key: 'demanda_estimada', label: 'Demanda' },
                        { key: 'confianza_min', label: 'Confianza Min' },
                        { key: 'confianza_max', label: 'Confianza Max' },
                        { key: 'horizonte_dias', label: 'Horizonte' },
                        { key: 'motivo', label: 'Motivo' },
                    ]}
                />
            </div>

            <div style={{ display: 'flex', gap: '12px', marginBottom: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
                <select
                    value={filterProducto}
                    onChange={(e) => setFilterProducto(e.target.value)}
                    style={{ padding: '0.5rem 0.75rem', border: '1px solid #d1d5db', borderRadius: '0.5rem', fontSize: '0.85rem', minWidth: '180px' }}
                >
                    <option value="">Todos los productos</option>
                    {uniqueProductos.map(p => (
                        <option key={p.codigo} value={p.codigo}>{p.codigo} - {p.nombre}</option>
                    ))}
                </select>

                <select
                    value={filterSubcategoria}
                    onChange={(e) => setFilterSubcategoria(e.target.value)}
                    style={{ padding: '0.5rem 0.75rem', border: '1px solid #d1d5db', borderRadius: '0.5rem', fontSize: '0.85rem', minWidth: '160px' }}
                >
                    <option value="">Todas las subcategorías</option>
                    {uniqueSubcategorias.map(s => (
                        <option key={s} value={s}>{s}</option>
                    ))}
                </select>

                <select
                    value={filterModelo}
                    onChange={(e) => setFilterModelo(e.target.value)}
                    style={{ padding: '0.5rem 0.75rem', border: '1px solid #d1d5db', borderRadius: '0.5rem', fontSize: '0.85rem', minWidth: '140px' }}
                >
                    <option value="">Todos los modelos</option>
                    {uniqueModelos.map(m => (
                        <option key={m} value={m}>{m}</option>
                    ))}
                </select>

                <input
                    type="text"
                    placeholder="Buscar..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    style={{
                        padding: '0.5rem 0.75rem',
                        border: '1px solid #d1d5db',
                        borderRadius: '0.5rem',
                        fontSize: '0.85rem',
                        flex: 1,
                        minWidth: '150px'
                    }}
                />
            </div>

            <div style={{
                background: 'white', borderRadius: '0.75rem',
                border: '1px solid #e5e7eb', overflow: 'hidden'
            }}>
                <div ref={tableContainerRef} style={{ overflowX: 'auto', maxHeight: '600px', overflowY: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                        <thead style={{ position: 'sticky', top: 0, zIndex: 1 }}>
                            <tr style={{ background: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
                                <th style={thStyle}>Fecha Archivo</th>
                                <th style={thStyle}>Producto</th>
                                <th style={thStyle}>Modelo</th>
                                <th style={thStyle}>Periodo</th>
                                <th style={{...thStyle, textAlign: 'right'}}>Demanda</th>
                                <th style={{...thStyle, textAlign: 'right'}}>Rango Confianza</th>
                                <th style={{...thStyle, textAlign: 'right'}}>Horizonte</th>
                                <th style={thStyle}>Motivo</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.length === 0 ? (
                                <tr>
                                    <td colSpan="8" style={{ padding: '2rem', textAlign: 'center', color: '#9ca3af' }}>
                                        No hay registros en el historial
                                    </td>
                                </tr>
                            ) : filtered.slice(0, visibleCount).map((reg) => (
                                <tr key={reg.id_historial} style={{ borderBottom: '1px solid #f3f4f6' }}>
                                    <td style={tdStyle}>{formatDateTime(reg.fecha_archivado)}</td>
                                    <td style={tdStyle}>
                                        <div>
                                            <div style={{ fontWeight: 600 }}>{reg.nombre_producto}</div>
                                            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{reg.codigo_producto}</div>
                                        </div>
                                    </td>
                                    <td style={tdStyle}>{reg.nombre_modelo}</td>
                                    <td style={tdStyle}>{reg.periodo || '-'}</td>
                                    <td style={{...tdStyle, textAlign: 'right', fontWeight: 600}}>
                                        {reg.demanda_estimada?.toLocaleString()}
                                    </td>
                                    <td style={{...tdStyle, textAlign: 'right'}}>
                                        {reg.confianza_min != null && reg.confianza_max != null
                                            ? `${reg.confianza_min.toLocaleString()} - ${reg.confianza_max.toLocaleString()}`
                                            : '-'}
                                    </td>
                                    <td style={{...tdStyle, textAlign: 'right'}}>{reg.horizonte_dias} días</td>
                                    <td style={tdStyle}>
                                        <span style={{
                                            padding: '0.2rem 0.5rem',
                                            borderRadius: '9999px',
                                            fontSize: '0.75rem',
                                            fontWeight: 600,
                                            background: reg.motivo === 'REEMPLAZADA' ? '#fef3c7' : '#e0e7ff',
                                            color: reg.motivo === 'REEMPLAZADA' ? '#92400e' : '#3730a3'
                                        }}>
                                            {reg.motivo}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                {loadingMore && (
                    <div style={{ padding: '1rem', textAlign: 'center', color: '#6b7280', fontSize: '0.85rem' }}>
                        Cargando más registros...
                    </div>
                )}
                {visibleCount >= filtered.length && filtered.length > 0 && (
                    <div style={{ padding: '0.75rem', textAlign: 'center', color: '#9ca3af', fontSize: '0.8rem', borderTop: '1px solid #f3f4f6' }}>
                        Mostrando {filtered.length} de {filtered.length} registros
                    </div>
                )}
            </div>
        </div>
    );
}

const thStyle = {
    padding: '0.75rem 1rem',
    textAlign: 'left',
    fontWeight: 600,
    color: '#374151',
    fontSize: '0.8rem',
    textTransform: 'uppercase',
    letterSpacing: '0.05em'
};

const tdStyle = {
    padding: '0.75rem 1rem',
    color: '#1f2937'
};
