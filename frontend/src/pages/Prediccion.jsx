import { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';
import ExportButtons from '../components/ExportButtons';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

const COLORES_MODELOS = [
    { border: 'rgb(16, 185, 129)', bg: 'rgba(16, 185, 129, 0.1)', name: 'Verde' },
    { border: 'rgb(239, 68, 68)', bg: 'rgba(239, 68, 68, 0.1)', name: 'Rojo' },
];

export default function Prediccion() {
    const [productos, setProductos] = useState([]);
    const [categorias, setCategorias] = useState([]);
    const [predicciones, setPredicciones] = useState([]);
    const [modelos, setModelos] = useState([]);
    const [productosSeleccionados, setProductosSeleccionados] = useState([]);
    const [modelosSeleccionados, setModelosSeleccionados] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedSubcategory, setSelectedSubcategory] = useState('');
    const [subcategorias, setSubcategorias] = useState([]);
    const [productosFiltrados, setProductosFiltrados] = useState([]);
    const [fechaInicio, setFechaInicio] = useState('');
    const [fechaFin, setFechaFin] = useState('');
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [progreso, setProgreso] = useState(null);
    const [toast, setToast] = useState(null);
    const [kpis, setKpis] = useState(null);
    const [loadingKpis, setLoadingKpis] = useState(false);
    const [comparacion, setComparacion] = useState(null);
    const [showProductDropdown, setShowProductDropdown] = useState(false);
    const [showModelDropdown, setShowModelDropdown] = useState(false);
    const [productoSearch, setProductoSearch] = useState('');
    const productDropdownRef = useRef(null);
    const modelDropdownRef = useRef(null);

    useEffect(() => {
        loadData();
        loadKpis();
    }, []);

    useEffect(() => {
        const handleClickOutside = (e) => {
            if (productDropdownRef.current && !productDropdownRef.current.contains(e.target)) {
                setShowProductDropdown(false);
            }
            if (modelDropdownRef.current && !modelDropdownRef.current.contains(e.target)) {
                setShowModelDropdown(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    useEffect(() => {
        let filtrados = productos;
        if (selectedCategory && selectedCategory !== 'all') {
            filtrados = filtrados.filter(p => p.id_categoria === parseInt(selectedCategory));
        }
        if (selectedSubcategory && selectedSubcategory !== 'all') {
            filtrados = filtrados.filter(p => p.id_subcategoria === parseInt(selectedSubcategory));
        }
        if (productoSearch) {
            const search = productoSearch.toLowerCase();
            filtrados = filtrados.filter(p =>
                p.nombre.toLowerCase().includes(search) ||
                p.codigo.toLowerCase().includes(search)
            );
        }
        setProductosFiltrados(filtrados);
    }, [selectedCategory, selectedSubcategory, productoSearch, productos]);

    useEffect(() => {
        if (selectedCategory && selectedCategory !== 'all') {
            api.get(`/subcategorias?categoria_id=${selectedCategory}`).then(res => {
                setSubcategorias(res.data);
            }).catch(() => setSubcategorias([]));
        } else {
            setSubcategorias([]);
            setSelectedSubcategory('');
        }
    }, [selectedCategory]);

    const loadData = async () => {
        const [prodRes, predRes, modelosRes, catRes] = await Promise.allSettled([
            api.get('/products?limit=2000'),
            api.get('/predicciones'),
            api.get('/modelos-ia'),
            api.get('/categorias')
        ]);

        if (prodRes.status === 'fulfilled') setProductos(prodRes.value.data);
        if (predRes.status === 'fulfilled') setPredicciones(predRes.value.data);
        if (catRes.status === 'fulfilled') setCategorias(catRes.value.data);
        if (modelosRes.status === 'fulfilled') {
            const listaModelos = modelosRes.value.data;
            setModelos(listaModelos);
            const activo = listaModelos.find(m => m.estado === 'ACTIVO');
            if (activo) setModelosSeleccionados([activo.id_modelo]);
        }

        const hasError = [prodRes, predRes, modelosRes, catRes].some(r => r.status === 'rejected');
        if (hasError) setToast({ message: 'Algunos datos no se pudieron cargar', type: 'warning' });

        setLoading(false);
    };

    const loadKpis = async () => {
        setLoadingKpis(true);
        try {
            const response = await api.get('/predicciones/kpis');
            setKpis(response.data);
        } catch (err) {
            console.error('Error loading KPIs:', err);
        } finally {
            setLoadingKpis(false);
        }
    };

    const toggleProducto = (idProducto) => {
        setProductosSeleccionados(prev =>
            prev.includes(idProducto)
                ? prev.filter(id => id !== idProducto)
                : [...prev, idProducto]
        );
        setComparacion(null);
    };

    const toggleTodosProductos = () => {
        if (productosSeleccionados.length === productosFiltrados.length) {
            setProductosSeleccionados([]);
        } else {
            setProductosSeleccionados(productosFiltrados.map(p => p.id_producto));
        }
        setComparacion(null);
    };

    const toggleModelo = (idModelo) => {
        setModelosSeleccionados(prev =>
            prev.includes(idModelo)
                ? prev.filter(id => id !== idModelo)
                : prev.length < 2 ? [...prev, idModelo] : prev
        );
        setComparacion(null);
    };

    const calcularHorizonte = () => {
        if (!fechaInicio || !fechaFin) return 30;
        const inicio = new Date(fechaInicio);
        const fin = new Date(fechaFin);
        const diffTime = Math.abs(fin - inicio);
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    };

    const handleGenerar = async () => {
        if (modelosSeleccionados.length === 0) {
            setToast({ message: 'Seleccione al menos un modelo IA', type: 'warning' });
            return;
        }
        if (productosSeleccionados.length === 0) {
            setToast({ message: 'Seleccione al menos un producto', type: 'warning' });
            return;
        }
        if (!fechaInicio || !fechaFin) {
            setToast({ message: 'Seleccione rango de fechas', type: 'warning' });
            return;
        }

        setGenerating(true);
        const horizonte = calcularHorizonte();

        try {
            if (modelosSeleccionados.length === 2) {
                await predecirComparar(horizonte);
            } else if (productosSeleccionados.length === 1) {
                await predecirProducto(productosSeleccionados[0], horizonte);
            } else {
                await predecirLote(horizonte);
            }
        } finally {
            setGenerating(false);
        }
    };

    const predecirProducto = async (productoId, horizonte) => {
        const payload = {
            id_producto: productoId,
            horizonte_dias: horizonte,
            id_modelo: parseInt(modelosSeleccionados[0])
        };
        if (fechaInicio) payload.fecha_inicio = fechaInicio;

        await api.post('/predicciones/predecir', payload);
        setToast({ message: 'Prediccion generada exitosamente', type: 'success' });
        loadData();
        loadKpis();
    };

    const predecirLote = async (horizonte) => {
        setProgreso({ total: productosSeleccionados.length, actual: 0, exitosos: 0, fallidos: 0 });

        const payload = {
            ids_productos: productosSeleccionados,
            horizonte_dias: horizonte,
            id_modelo: parseInt(modelosSeleccionados[0])
        };
        if (fechaInicio) payload.fecha_inicio = fechaInicio;

        try {
            const response = await api.post('/predicciones/predecir-lote', payload);
            const resultado = response.data;
            setProgreso({
                total: resultado.total_productos,
                actual: resultado.total_productos,
                exitosos: resultado.exitosos,
                fallidos: resultado.fallidos
            });

            if (resultado.fallidos > 0) {
                setToast({ message: `${resultado.exitosos} exitos, ${resultado.fallidos} fallidos`, type: 'warning' });
            } else {
                setToast({ message: `${resultado.exitosos} predicciones generadas`, type: 'success' });
            }
            loadData();
            loadKpis();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al generar predicciones', type: 'error' });
        } finally {
            setTimeout(() => setProgreso(null), 3000);
        }
    };

    const predecirComparar = async (horizonte) => {
        const payload = {
            id_productos: productosSeleccionados,
            horizonte_dias: horizonte,
            id_modelos: modelosSeleccionados.map(Number),
            fecha_inicio: fechaInicio || undefined
        };

        try {
            const response = await api.post('/predicciones/predecir-comparar', payload);
            setComparacion(response.data);
            setToast({ message: 'Comparacion generada exitosamente', type: 'success' });

            for (const prodId of productosSeleccionados) {
                for (const modeloId of modelosSeleccionados) {
                    try {
                        await api.post('/predicciones/predecir', {
                            id_producto: prodId,
                            horizonte_dias: horizonte,
                            id_modelo: parseInt(modeloId),
                            fecha_inicio: fechaInicio || undefined
                        });
                    } catch (e) { /* ignore individual failures */ }
                }
            }
            loadData();
            loadKpis();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error en comparacion', type: 'error' });
        }
    };

    const getProducto = (id) => productos.find(p => p.id_producto === id);

    const prepareChartData = () => {
        if (!comparacion || !comparacion.productos || comparacion.productos.length === 0) return null;

        const primerProducto = comparacion.productos[0];
        if (!primerProducto || !primerProducto.modelos || primerProducto.modelos.length === 0) return null;

        const labels = primerProducto.modelos[0]?.predicciones?.map(p => p.fecha) || [];

        const datasets = primerProducto.modelos.map((modelo, idx) => {
            const color = COLORES_MODELOS[idx % COLORES_MODELOS.length];
            return {
                label: `${modelo.algoritmo} v${modelo.version || '?'} (R²: ${modelo.r2?.toFixed(3) || 'N/A'})`,
                data: modelo.predicciones.map(p => p.demanda_estimada),
                borderColor: color.border,
                backgroundColor: color.bg,
                fill: false,
                tension: 0.1,
                pointRadius: 3,
                borderWidth: 2
            };
        });

        return { labels, datasets };
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { position: 'top', labels: { usePointStyle: true, padding: 15 } },
            title: { display: false },
            tooltip: { mode: 'index', intersect: false }
        },
        scales: {
            x: {
                display: true,
                title: { display: true, text: 'Fecha' },
                ticks: { maxTicksLimit: 15, maxRotation: 45, minRotation: 45 }
            },
            y: {
                display: true,
                title: { display: true, text: 'Cantidad' },
                beginAtZero: true
            }
        },
        interaction: { mode: 'nearest', axis: 'x', intersect: false }
    };

    const getModeloById = (id) => modelos.find(m => m.id_modelo === id);

    if (loading) return <div className="content-area"><p>Cargando prediccion...</p></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Generar Prediccion de Demanda</h3>
                    {modelosSeleccionados.length > 0 && (
                        <span className="badge badge-success">
                            {modelosSeleccionados.length === 2 ? 'Comparacion' : 'Modelo Seleccionado'}
                        </span>
                    )}
                </div>

                <div className="grid-3" style={{ gap: '16px' }}>
                    <div className="form-group">
                        <label>Categoria</label>
                        <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)}>
                            <option value="">Todas las categorias</option>
                            <option value="all">Todas</option>
                            {categorias.map(c => (
                                <option key={c.id_categoria} value={c.id_categoria}>{c.nombre}</option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group" ref={productDropdownRef} style={{ position: 'relative' }}>
                        <label>Producto</label>
                        <div
                            onClick={() => setShowProductDropdown(!showProductDropdown)}
                            style={{
                                padding: '8px 12px',
                                border: '1px solid var(--gray-300)',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                backgroundColor: 'white',
                                minHeight: '38px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between'
                            }}
                        >
                            <span style={{ fontSize: '0.9rem', color: productosSeleccionados.length === 0 ? 'var(--gray-500)' : 'var(--gray-800)' }}>
                                {productosSeleccionados.length === 0
                                    ? 'Seleccionar productos...'
                                    : productosSeleccionados.length === productosFiltrados.length
                                        ? `Todos (${productosFiltrados.length})`
                                        : `${productosSeleccionados.length} seleccionado(s)`
                                }
                            </span>
                            <span style={{ fontSize: '0.7rem', color: 'var(--gray-500)' }}>{showProductDropdown ? '▲' : '▼'}</span>
                        </div>
                        {showProductDropdown && (
                            <div style={{
                                position: 'absolute',
                                top: 'calc(100% + 4px)',
                                left: 0,
                                right: 0,
                                backgroundColor: 'white',
                                border: '1px solid var(--gray-300)',
                                borderRadius: '6px',
                                boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                                zIndex: 1000,
                                maxHeight: '280px',
                                overflowY: 'auto',
                                overflowX: 'hidden'
                            }}>
                                <div style={{ padding: '8px', borderBottom: '1px solid var(--gray-200)', position: 'sticky', top: 0, backgroundColor: 'white', zIndex: 1 }}>
                                    <input
                                        type="text"
                                        placeholder="Buscar producto..."
                                        value={productoSearch}
                                        onChange={(e) => setProductoSearch(e.target.value)}
                                        style={{ width: '100%', padding: '6px 8px', border: '1px solid var(--gray-300)', borderRadius: '4px', fontSize: '0.85rem', boxSizing: 'border-box' }}
                                        onClick={(e) => e.stopPropagation()}
                                    />
                                </div>
                                <div
                                    style={{ padding: '8px 12px', borderBottom: '1px solid var(--gray-200)', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '600', fontSize: '0.85rem', cursor: 'pointer', backgroundColor: 'var(--bg-secondary)' }}
                                    onClick={toggleTodosProductos}
                                >
                                    <input
                                        type="checkbox"
                                        checked={productosSeleccionados.length === productosFiltrados.length && productosFiltrados.length > 0}
                                        onChange={toggleTodosProductos}
                                        onClick={(e) => e.stopPropagation()}
                                        style={{ width: '16px', height: '16px', cursor: 'pointer', flexShrink: 0 }}
                                    />
                                    <span>Todos ({productosFiltrados.length})</span>
                                </div>
                                {productosFiltrados.map(p => (
                                    <div
                                        key={p.id_producto}
                                        style={{ padding: '8px 12px', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.85rem', borderBottom: '1px solid var(--gray-100)' }}
                                        onClick={() => toggleProducto(p.id_producto)}
                                    >
                                        <input
                                            type="checkbox"
                                            checked={productosSeleccionados.includes(p.id_producto)}
                                            onChange={() => toggleProducto(p.id_producto)}
                                            onClick={(e) => e.stopPropagation()}
                                            style={{ width: '16px', height: '16px', cursor: 'pointer', flexShrink: 0 }}
                                        />
                                        <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.codigo} - {p.nombre}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="form-group" ref={modelDropdownRef} style={{ position: 'relative' }}>
                        <label>Modelo IA</label>
                        <div
                            onClick={() => setShowModelDropdown(!showModelDropdown)}
                            style={{
                                padding: '8px 12px',
                                border: '1px solid var(--gray-300)',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                backgroundColor: 'white',
                                minHeight: '38px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between'
                            }}
                        >
                            <span style={{ fontSize: '0.9rem', color: modelosSeleccionados.length === 0 ? 'var(--gray-500)' : 'var(--gray-800)' }}>
                                {modelosSeleccionados.length === 0
                                    ? 'Seleccionar modelo...'
                                    : modelosSeleccionados.length === 1
                                        ? (() => { const m = getModeloById(modelosSeleccionados[0]); return m ? `${m.algoritmo} (R²: ${m.r2?.toFixed(3) || 'N/A'})` : 'Modelo'; })()
                                        : `${modelosSeleccionados.length} modelos seleccionados`
                                }
                            </span>
                            <span style={{ fontSize: '0.7rem', color: 'var(--gray-500)' }}>{showModelDropdown ? '▲' : '▼'}</span>
                        </div>
                        {showModelDropdown && (
                            <div style={{
                                position: 'absolute',
                                top: 'calc(100% + 4px)',
                                left: 0,
                                right: 0,
                                backgroundColor: 'white',
                                border: '1px solid var(--gray-300)',
                                borderRadius: '6px',
                                boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                                zIndex: 1000
                            }}>
                                {modelos.filter(m => m.estado === 'ACTIVO').map(m => (
                                    <div
                                        key={m.id_modelo}
                                        onClick={() => toggleModelo(m.id_modelo)}
                                        style={{
                                            padding: '8px 12px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '8px',
                                            cursor: modelosSeleccionados.length >= 2 && !modelosSeleccionados.includes(m.id_modelo) ? 'not-allowed' : 'pointer',
                                            backgroundColor: modelosSeleccionados.includes(m.id_modelo) ? 'var(--primary-light)' : 'transparent',
                                            opacity: modelosSeleccionados.length >= 2 && !modelosSeleccionados.includes(m.id_modelo) ? 0.5 : 1,
                                            fontSize: '0.85rem',
                                            borderBottom: '1px solid var(--gray-100)'
                                        }}
                                    >
                                        <input
                                            type="checkbox"
                                            checked={modelosSeleccionados.includes(m.id_modelo)}
                                            disabled={modelosSeleccionados.length >= 2 && !modelosSeleccionados.includes(m.id_modelo)}
                                            onChange={() => toggleModelo(m.id_modelo)}
                                            onClick={(e) => e.stopPropagation()}
                                            style={{ width: '16px', height: '16px', cursor: 'pointer', flexShrink: 0 }}
                                        />
                                        <span style={{ whiteSpace: 'nowrap' }}>{m.algoritmo} (R²: {m.r2?.toFixed(3) || 'N/A'})</span>
                                    </div>
                                ))}
                                {modelos.filter(m => m.estado !== 'ACTIVO').length > 0 && (
                                    <div style={{ padding: '6px 12px', fontSize: '0.75rem', color: 'var(--gray-500)', borderTop: '1px solid var(--gray-200)' }}>
                                        Inactivos:
                                    </div>
                                )}
                                {modelos.filter(m => m.estado !== 'ACTIVO').map(m => (
                                    <div
                                        key={m.id_modelo}
                                        onClick={() => toggleModelo(m.id_modelo)}
                                        style={{
                                            padding: '6px 12px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '8px',
                                            cursor: 'pointer',
                                            opacity: 0.6,
                                            fontSize: '0.85rem'
                                        }}
                                    >
                                        <input
                                            type="checkbox"
                                            checked={modelosSeleccionados.includes(m.id_modelo)}
                                            onChange={() => toggleModelo(m.id_modelo)}
                                            onClick={(e) => e.stopPropagation()}
                                            style={{ width: '16px', height: '16px', cursor: 'pointer', flexShrink: 0 }}
                                        />
                                        <span style={{ whiteSpace: 'nowrap' }}>{m.algoritmo} (R²: {m.r2?.toFixed(3) || 'N/A'})</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                <div className="grid-3" style={{ gap: '16px', marginTop: '16px' }}>
                    <div className="form-group">
                        <label>Fecha de Inicio</label>
                        <input
                            type="date"
                            value={fechaInicio}
                            onChange={(e) => setFechaInicio(e.target.value)}
                            min={new Date().toISOString().split('T')[0]}
                            style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--gray-300)' }}
                        />
                    </div>
                    <div className="form-group">
                        <label>Fecha de Fin</label>
                        <input
                            type="date"
                            value={fechaFin}
                            onChange={(e) => setFechaFin(e.target.value)}
                            min={fechaInicio || new Date().toISOString().split('T')[0]}
                            style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--gray-300)' }}
                        />
                        {fechaInicio && fechaFin && (
                            <small style={{ color: 'var(--primary)', fontSize: '0.75rem', fontWeight: 'bold' }}>
                                Horizonte: {calcularHorizonte()} dias
                            </small>
                        )}
                    </div>
                    <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end' }}>
                        <button
                            className="btn btn-primary"
                            onClick={handleGenerar}
                            disabled={generating || modelosSeleccionados.length === 0 || productosSeleccionados.length === 0 || !fechaInicio || !fechaFin}
                            style={{ width: '100%', padding: '8px 16px', fontSize: '0.9rem' }}
                        >
                            {generating ? 'Generando...' : modelosSeleccionados.length === 2 ? 'Comparar Modelos' : 'Generar Prediccion'}
                        </button>
                    </div>
                </div>

                {progreso && (
                    <div style={{ marginTop: '16px', padding: '12px', backgroundColor: 'var(--bg-secondary)', borderRadius: '8px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                            <span>Progreso: {progreso.actual} / {progreso.total}</span>
                            <span>
                                <span style={{ color: 'var(--success)' }}>✓ {progreso.exitosos}</span>
                                {progreso.fallidos > 0 && <span style={{ color: 'var(--danger)', marginLeft: '12px' }}>✗ {progreso.fallidos}</span>}
                            </span>
                        </div>
                        <div style={{ height: '8px', backgroundColor: 'var(--gray-200)', borderRadius: '4px', overflow: 'hidden' }}>
                            <div style={{
                                height: '100%',
                                width: `${(progreso.actual / progreso.total) * 100}%`,
                                backgroundColor: progreso.exitosos === progreso.total ? 'var(--success)' : 'var(--primary)',
                                transition: 'width 0.3s ease'
                            }} />
                        </div>
                    </div>
                )}
            </div>

            {comparacion && comparacion.productos && comparacion.productos.length > 0 && (
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Comparacion de Modelos</h3>
                        <span className="badge badge-info">{comparacion.productos.length} producto(s)</span>
                    </div>

                    {comparacion.productos.length === 1 && (
                        <div style={{ height: '350px', padding: '16px' }}>
                            <Line data={prepareChartData()} options={chartOptions} />
                        </div>
                    )}

                    {comparacion.productos.map((prod) => (
                        <div key={prod.id_producto} style={{ marginBottom: '24px', padding: '16px', backgroundColor: 'var(--bg-secondary)', borderRadius: '8px' }}>
                            <h4 style={{ marginBottom: '12px', color: 'var(--primary)' }}>{prod.nombre}</h4>

                            <div className="table-container">
                                <table className="data-table">
                                    <thead>
                                        <tr>
                                            <th>Fecha</th>
                                            {prod.modelos.map((m, idx) => (
                                                <th key={m.id_modelo} style={{ color: COLORES_MODELOS[idx]?.border }}>
                                                    {m.algoritmo} (R²: {m.r2?.toFixed(3) || 'N/A'})
                                                </th>
                                            ))}
                                            {prod.modelos.length === 2 && <th>Diferencia %</th>}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {prod.modelos[0]?.predicciones?.slice(0, 15).map((pred, i) => {
                                            const val0 = prod.modelos[0]?.predicciones?.[i]?.demanda_estimada || 0;
                                            const val1 = prod.modelos[1]?.predicciones?.[i]?.demanda_estimada || 0;
                                            const diff = val0 > 0 ? Math.abs(val1 - val0) / val0 * 100 : 0;
                                            return (
                                                <tr key={i}>
                                                    <td>{pred.fecha}</td>
                                                    {prod.modelos.map((m, idx) => (
                                                        <td key={m.id_modelo} style={{ fontWeight: 'bold', color: COLORES_MODELOS[idx]?.border }}>
                                                            {m.predicciones?.[i]?.demanda_estimada || 0}
                                                        </td>
                                                    ))}
                                                    {prod.modelos.length === 2 && (
                                                        <td style={{ color: diff > 10 ? 'var(--warning)' : 'var(--gray-600)', fontWeight: diff > 10 ? 'bold' : 'normal' }}>
                                                            {diff.toFixed(1)}%
                                                        </td>
                                                    )}
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                    <tfoot>
                                        <tr style={{ fontWeight: 'bold', backgroundColor: 'var(--gray-100)' }}>
                                            <td>Promedio</td>
                                            {prod.modelos.map((m, idx) => {
                                                const preds = m.predicciones || [];
                                                const avg = preds.length > 0 ? Math.round(preds.reduce((s, p) => s + p.demanda_estimada, 0) / preds.length) : 0;
                                                return (
                                                    <td key={m.id_modelo} style={{ color: COLORES_MODELOS[idx]?.border }}>
                                                        {avg}
                                                    </td>
                                                );
                                            })}
                                            {prod.modelos.length === 2 && <td>-</td>}
                                        </tr>
                                    </tfoot>
                                </table>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {modelosSeleccionados.length === 1 && productosSeleccionados.length === 1 && (() => {
                const prediccionesProducto = predicciones.filter(p => p.id_producto === productosSeleccionados[0]);
                if (prediccionesProducto.length === 0) return null;
                const prod = getProducto(productosSeleccionados[0]);
                return (
                    <div className="card">
                        <div className="card-header">
                            <h3 className="card-title">Grafico de Prediccion - {prod?.nombre}</h3>
                        </div>
                        <div style={{ height: '350px', padding: '16px' }}>
                            <Line
                                data={{
                                    labels: prediccionesProducto.map(p => p.fecha_prediccion),
                                    datasets: [{
                                        label: 'Demanda Estimada',
                                        data: prediccionesProducto.map(p => p.demanda_estimada),
                                        borderColor: 'rgb(16, 185, 129)',
                                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                                        fill: false,
                                        tension: 0.1,
                                        pointRadius: 4,
                                        borderWidth: 2
                                    }, {
                                        label: 'Confianza Min',
                                        data: prediccionesProducto.map(p => p.confianza_min),
                                        borderColor: 'rgba(245, 158, 11, 0.5)',
                                        fill: '+1',
                                        tension: 0.1,
                                        pointRadius: 0,
                                        borderDash: [5, 5]
                                    }, {
                                        label: 'Confianza Max',
                                        data: prediccionesProducto.map(p => p.confianza_max),
                                        borderColor: 'rgba(245, 158, 11, 0.5)',
                                        fill: false,
                                        tension: 0.1,
                                        pointRadius: 0,
                                        borderDash: [5, 5]
                                    }]
                                }}
                                options={chartOptions}
                            />
                        </div>
                    </div>
                );
            })()}

            {kpis && kpis.total_productos > 0 && (
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">KPIs de Rentabilidad</h3>
                        {loadingKpis && <span style={{ fontSize: '0.8rem', color: 'var(--gray-500)' }}>Calculando...</span>}
                    </div>
                    
                    <div className="grid-4" style={{ gap: '16px', marginBottom: '20px' }}>
                        <div className="card" style={{ backgroundColor: 'var(--primary-light)', borderLeft: '4px solid var(--primary)' }}>
                            <div className="card-title" style={{ fontSize: '0.85rem', color: 'var(--gray-600)' }}>Ingreso Total Esperado</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--primary)' }}>
                                ${kpis.ingreso_total_esperado.toLocaleString('es-EC', { minimumFractionDigits: 2 })}
                            </div>
                        </div>
                        <div className="card" style={{ backgroundColor: 'var(--success-light)', borderLeft: '4px solid var(--success)' }}>
                            <div className="card-title" style={{ fontSize: '0.85rem', color: 'var(--gray-600)' }}>Ganancia Total Esperada</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--success)' }}>
                                ${kpis.ganancia_total_esperada.toLocaleString('es-EC', { minimumFractionDigits: 2 })}
                            </div>
                        </div>
                        <div className="card" style={{ backgroundColor: 'var(--warning-light)', borderLeft: '4px solid var(--warning)' }}>
                            <div className="card-title" style={{ fontSize: '0.85rem', color: 'var(--gray-600)' }}>Costo Total Esperado</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--warning)' }}>
                                ${kpis.costo_total_esperado.toLocaleString('es-EC', { minimumFractionDigits: 2 })}
                            </div>
                        </div>
                        <div className="card" style={{ backgroundColor: 'var(--info-light)', borderLeft: '4px solid var(--info)' }}>
                            <div className="card-title" style={{ fontSize: '0.85rem', color: 'var(--gray-600)' }}>Productos con Prediccion</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--info)' }}>
                                {kpis.total_productos}
                            </div>
                        </div>
                    </div>

                    {kpis.producto_mayor_volumen && (
                        <div className="grid-3" style={{ gap: '16px', marginBottom: '20px' }}>
                            <div className="card" style={{ backgroundColor: 'var(--bg-secondary)', padding: '12px' }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--gray-500)', marginBottom: '4px' }}>Mayor Volumen de Venta</div>
                                <div style={{ fontWeight: 'bold', color: 'var(--primary)' }}>{kpis.producto_mayor_volumen.nombre}</div>
                                <div style={{ fontSize: '0.85rem', color: 'var(--gray-600)' }}>
                                    Demanda: {kpis.producto_mayor_volumen.demanda_total.toLocaleString()} unidades
                                </div>
                            </div>
                            <div className="card" style={{ backgroundColor: 'var(--bg-secondary)', padding: '12px' }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--gray-500)', marginBottom: '4px' }}>Mayor Rentabilidad</div>
                                <div style={{ fontWeight: 'bold', color: 'var(--success)' }}>{kpis.producto_mayor_rentabilidad.nombre}</div>
                                <div style={{ fontSize: '0.85rem', color: 'var(--gray-600)' }}>
                                    Ganancia: ${kpis.producto_mayor_rentabilidad.ganancia_esperada.toLocaleString('es-EC', { minimumFractionDigits: 2 })}
                                </div>
                            </div>
                            <div className="card" style={{ backgroundColor: 'var(--bg-secondary)', padding: '12px' }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--gray-500)', marginBottom: '4px' }}>Mayor Ingreso</div>
                                <div style={{ fontWeight: 'bold', color: 'var(--warning)' }}>{kpis.producto_mayor_ingreso.nombre}</div>
                                <div style={{ fontSize: '0.85rem', color: 'var(--gray-600)' }}>
                                    Ingreso: ${kpis.producto_mayor_ingreso.ingreso_esperado.toLocaleString('es-EC', { minimumFractionDigits: 2 })}
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Producto</th>
                                    <th>Demanda Est.</th>
                                    <th>Precio Venta</th>
                                    <th>Margen</th>
                                    <th>Ingreso Esperado</th>
                                    <th>Ganancia Esperada</th>
                                </tr>
                            </thead>
                            <tbody>
                                {kpis.productos.slice(0, 10).map(kpi => (
                                    <tr key={kpi.id_producto}>
                                        <td><strong>{kpi.nombre}</strong></td>
                                        <td>{kpi.demanda_total.toLocaleString()}</td>
                                        <td>${kpi.precio_venta.toFixed(2)}</td>
                                        <td style={{ color: kpi.margen_porcentaje > 20 ? 'var(--success)' : 'var(--warning)' }}>
                                            {kpi.margen_porcentaje.toFixed(1)}%
                                        </td>
                                        <td>${kpi.ingreso_esperado.toLocaleString('es-EC', { minimumFractionDigits: 2 })}</td>
                                        <td style={{ color: 'var(--success)', fontWeight: 'bold' }}>
                                            ${kpi.ganancia_esperada.toLocaleString('es-EC', { minimumFractionDigits: 2 })}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Historial de Predicciones</h3>
                    <ExportButtons
                        data={predicciones.slice(0, 50).map(pred => {
                            const prod = getProducto(pred.id_producto);
                            return {
                                id_prediccion: `#${pred.id_prediccion}`,
                                producto: prod ? `${prod.codigo} - ${prod.nombre}` : `#${pred.id_producto}`,
                                periodo: pred.periodo || '-',
                                demanda_estimada: pred.demanda_estimada,
                                precio_venta: pred.precio_venta ? `$${pred.precio_venta.toFixed(2)}` : '-',
                                ingreso_esperado: pred.ingreso_esperado ? `$${pred.ingreso_esperado.toLocaleString('es-EC', { minimumFractionDigits: 2 })}` : '-',
                                ganancia_esperada: pred.ganancia_esperada ? `$${pred.ganancia_esperada.toLocaleString('es-EC', { minimumFractionDigits: 2 })}` : '-',
                                margen_porcentaje: pred.margen_porcentaje ? `${pred.margen_porcentaje}%` : '-',
                                fecha_prediccion: pred.fecha_prediccion || '-',
                            };
                        })}
                        columns={[
                            { key: 'id_prediccion', label: 'ID' },
                            { key: 'producto', label: 'Producto' },
                            { key: 'demanda_estimada', label: 'Demanda' },
                            { key: 'precio_venta', label: 'Precio' },
                            { key: 'ingreso_esperado', label: 'Ingreso Esperado' },
                            { key: 'ganancia_esperada', label: 'Ganancia' },
                            { key: 'margen_porcentaje', label: 'Margen' },
                            { key: 'fecha_prediccion', label: 'Fecha' },
                        ]}
                        moduleName="prediccion"
                    />
                </div>
                {predicciones.length === 0 ? (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '200px', color: 'var(--gray-500)' }}>
                        <p>No hay predicciones registradas. Seleccione productos y genere una prediccion.</p>
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Producto</th>
                                    <th>Demanda</th>
                                    <th>Precio</th>
                                    <th>Ingreso Esperado</th>
                                    <th>Ganancia</th>
                                    <th>Margen</th>
                                    <th>Fecha</th>
                                </tr>
                            </thead>
                            <tbody>
                                {predicciones.slice(0, 50).map(pred => {
                                    const prod = getProducto(pred.id_producto);
                                    return (
                                        <tr key={pred.id_prediccion}>
                                            <td>#{pred.id_prediccion}</td>
                                            <td>{prod ? `${prod.codigo} - ${prod.nombre}` : `#${pred.id_producto}`}</td>
                                            <td><strong style={{ color: 'var(--primary)' }}>{pred.demanda_estimada}</strong></td>
                                            <td>${pred.precio_venta?.toFixed(2) || '-'}</td>
                                            <td style={{ color: 'var(--success)', fontWeight: 'bold' }}>
                                                ${pred.ingreso_esperado?.toLocaleString('es-EC', { minimumFractionDigits: 2 }) || '-'}
                                            </td>
                                            <td style={{ color: 'var(--success)' }}>
                                                ${pred.ganancia_esperada?.toLocaleString('es-EC', { minimumFractionDigits: 2 }) || '-'}
                                            </td>
                                            <td style={{ color: pred.margen_porcentaje > 20 ? 'var(--success)' : 'var(--warning)' }}>
                                                {pred.margen_porcentaje?.toFixed(1) || '-'}%
                                            </td>
                                            <td>{pred.fecha_prediccion || '-'}</td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <div className="grid-3">
                <div className="card">
                    <div className="card-title">Total Predicciones</div>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>{predicciones.length}</div>
                </div>
                <div className="card">
                    <div className="card-title">Productos con Predicciones</div>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--success)' }}>{new Set(predicciones.map(p => p.id_producto)).size}</div>
                </div>
                <div className="card">
                    <div className="card-title">Modelos Disponibles</div>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>{modelos.length}</div>
                    {modelos.length > 0 && (
                        <div style={{ fontSize: '0.8rem', color: 'var(--gray-500)', marginTop: '4px' }}>
                            {modelos.map(m => m.algoritmo).join(' | ')}
                        </div>
                    )}
                </div>
            </div>

            {modelos.length > 0 && (
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Detalle de Modelos</h3>
                    </div>
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Modelo</th>
                                    <th>Estado</th>
                                    <th>MAE</th>
                                    <th>RMSE</th>
                                    <th>R²</th>
                                    <th>MAPE</th>
                                </tr>
                            </thead>
                            <tbody>
                                {modelos.map(modelo => (
                                    <tr key={modelo.id_modelo} style={{ backgroundColor: modelosSeleccionados.includes(modelo.id_modelo) ? 'var(--primary-light)' : 'transparent' }}>
                                        <td><strong>{modelo.algoritmo}</strong></td>
                                        <td>
                                            <span className={`badge ${modelo.estado === 'ACTIVO' ? 'badge-success' : 'badge-secondary'}`}>
                                                {modelo.estado}
                                            </span>
                                        </td>
                                        <td>{modelo.mae?.toFixed(3) || 'N/A'}</td>
                                        <td>{modelo.rmse?.toFixed(3) || 'N/A'}</td>
                                        <td>{modelo.r2?.toFixed(3) || 'N/A'}</td>
                                        <td>{modelo.mape?.toFixed(1) || 'N/A'}%</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
