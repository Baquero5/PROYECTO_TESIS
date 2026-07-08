import { useState, useEffect } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';
import ExportButtons from '../components/ExportButtons';

export default function HistorialPredicciones() {
    const [registros, setRegistros] = useState([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(0);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [toast, setToast] = useState(null);
    const limit = 20;

    useEffect(() => {
        loadData();
    }, [page]);

    const loadData = async () => {
        setLoading(true);
        try {
            const res = await api.get(`/historial-predicciones?skip=${page * limit}&limit=${limit}`);
            setRegistros(res.data.registros);
            setTotal(res.data.total);
        } catch (err) {
            setToast({ message: 'Error al cargar historial', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const filtered = registros.filter(r =>
        (r.nombre_producto || '').toLowerCase().includes(search.toLowerCase()) ||
        (r.codigo_producto || '').toLowerCase().includes(search.toLowerCase()) ||
        (r.nombre_modelo || '').toLowerCase().includes(search.toLowerCase()) ||
        (r.motivo || '').toLowerCase().includes(search.toLowerCase())
    );

    const totalPages = Math.ceil(total / limit);

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
                        Registro de predicciones archivadas ({total} en total)
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

            <div style={{ marginBottom: '1rem' }}>
                <input
                    type="text"
                    placeholder="Buscar por producto, código, modelo..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    style={{
                        width: '100%', maxWidth: '400px',
                        padding: '0.5rem 0.75rem',
                        border: '1px solid #d1d5db',
                        borderRadius: '0.5rem',
                        fontSize: '0.875rem'
                    }}
                />
            </div>

            <div style={{
                background: 'white', borderRadius: '0.75rem',
                border: '1px solid #e5e7eb', overflow: 'hidden'
            }}>
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                        <thead>
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
                            ) : filtered.map((reg) => (
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
            </div>

            {totalPages > 1 && (
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem', marginTop: '1rem' }}>
                    <button
                        onClick={() => setPage(p => Math.max(0, p - 1))}
                        disabled={page === 0}
                        style={{
                            padding: '0.4rem 0.75rem',
                            border: '1px solid #d1d5db',
                            borderRadius: '0.375rem',
                            background: page === 0 ? '#f9fafb' : 'white',
                            cursor: page === 0 ? 'not-allowed' : 'pointer',
                            fontSize: '0.8rem'
                        }}
                    >
                        Anterior
                    </button>
                    <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>
                        Página {page + 1} de {totalPages}
                    </span>
                    <button
                        onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
                        disabled={page >= totalPages - 1}
                        style={{
                            padding: '0.4rem 0.75rem',
                            border: '1px solid #d1d5db',
                            borderRadius: '0.375rem',
                            background: page >= totalPages - 1 ? '#f9fafb' : 'white',
                            cursor: page >= totalPages - 1 ? 'not-allowed' : 'pointer',
                            fontSize: '0.8rem'
                        }}
                    >
                        Siguiente
                    </button>
                </div>
            )}
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
