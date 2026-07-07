import { useState, useEffect, useRef, Component } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';
import ExportButtons from '../components/ExportButtons';
import ChartExportButton from '../components/ChartExportButton';
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
import {
    formatCurrency,
    formatNumber,
    baseTooltipConfig,
    CHART_COLORS,
    predictionTooltipCallbacks,
    comparisonTooltipCallbacks,
} from '../config/chartConfig';

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

class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }
    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }
    componentDidCatch(error, errorInfo) {
        console.error('Comparison render error:', error, errorInfo.componentStack);
    }
    render() {
        if (this.state.hasError) {
            return (
                <div style={{ padding: '16px', backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', margin: '16px' }}>
                    <p style={{ color: '#dc2626', fontWeight: 'bold' }}>Error al renderizar comparación</p>
                    <pre style={{ color: '#666', fontSize: '0.75rem', whiteSpace: 'pre-wrap' }}>{this.state.error?.message}{'\n'}{this.state.error?.stack}</pre>
                    <button className="btn btn-secondary" onClick={() => this.setState({ hasError: false })} style={{ marginTop: '8px' }}>
                        Reintentar
                    </button>
                </div>
            );
        }
        return this.props.children;
    }
}

export default function Prediccion() {
    const [showDropdown, setShowDropdown] = useState(false);
    const [showModeloDropdown, setShowModeloDropdown] = useState(false);
    const [productos, setProductos] = useState([]);
    const [categorias, setCategorias] = useState([]);
    const [subcategorias, setSubcategorias] = useState([]);
    const [predicciones, setPredicciones] = useState([]);
    const [modelos, setModelos] = useState([]);
    const [modelosSeleccionados, setModelosSeleccionados] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedSubcategory, setSelectedSubcategory] = useState('');
    const [productosSeleccionados, setProductosSeleccionados] = useState([]);
    const [productosFiltrados, setProductosFiltrados] = useState([]);
    const [fechaInicio, setFechaInicio] = useState('');
    const [fechaFin, setFechaFin] = useState('');
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [progreso, setProgreso] = useState(null);
    const [toast, setToast] = useState(null);
    const [historialVentas, setHistorialVentas] = useState([]);
    const [loadingHistorial, setLoadingHistorial] = useState(false);
    const [kpis, setKpis] = useState(null);
    const [loadingKpis, setLoadingKpis] = useState(false);
    const [modeloAlcance, setModeloAlcance] = useState(null);
    const [comparacion, setComparacion] = useState(null);

    const chartPrediccionRef = useRef(null);

    useEffect(() => {
        loadData();
        loadKpis();
        loadModeloAlcance();

        const handleClickOutside = (e) => {
            if (!e.target.closest('[data-dropdown-productos]')) {
                setShowDropdown(false);
            }
            if (!e.target.closest('[data-dropdown-modelo]')) {
                setShowModeloDropdown(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    useEffect(() => {
        let filtrados = productos;

        // Si el modelo tiene alcance, filtrar por subcategorías permitidas
        if (modeloAlcance && modeloAlcance.alcance && modeloAlcance.subcategorias && subcategorias.length > 0) {
            // Obtener IDs de subcategorías permitidas
            const allowedSubcatIds = subcategorias
                .filter(s => modeloAlcance.subcategorias.includes(s.nombre))
                .map(s => s.id_subcategoria);
            filtrados = filtrados.filter(p => allowedSubcatIds.includes(p.id_subcategoria));
        }

        if (selectedCategory && selectedCategory !== 'all') {
            filtrados = filtrados.filter(p => p.id_categoria === parseInt(selectedCategory));
        }
        if (selectedSubcategory && selectedSubcategory !== 'all') {
            filtrados = filtrados.filter(p => p.id_subcategoria === parseInt(selectedSubcategory));
        }
        setProductosFiltrados(filtrados);
    }, [selectedCategory, selectedSubcategory, productos, modeloAlcance, categorias, subcategorias]);

    useEffect(() => {
        if (productosSeleccionados.length === 1) {
            loadHistorial(productosSeleccionados[0]);
        } else {
            setHistorialVentas([]);
        }
    }, [productosSeleccionados]);

    const loadData = async () => {
        const [prodRes, predRes, modelosRes, catRes, subRes] = await Promise.allSettled([
            api.get('/products?limit=2000'),
            api.get('/predicciones'),
            api.get('/modelos-ia'),
            api.get('/categorias'),
            api.get('/subcategorias')
        ]);

        if (prodRes.status === 'fulfilled') setProductos(prodRes.value.data);
        if (predRes.status === 'fulfilled') setPredicciones(predRes.value.data);
        if (catRes.status === 'fulfilled') setCategorias(catRes.value.data);
        if (subRes.status === 'fulfilled') setSubcategorias(subRes.value.data);
        if (modelosRes.status === 'fulfilled') {
            const listaModelos = modelosRes.value.data;
            setModelos(listaModelos);
            if (listaModelos.length > 0) {
                setModelosSeleccionados(prev => {
                    if (prev.length === 0) {
                        const activo = listaModelos.find(m => m.estado === 'ACTIVO');
                        return activo ? [activo.id_modelo] : [listaModelos[0].id_modelo];
                    }
                    return prev;
                });
            }
        }

        const hasError = [prodRes, predRes, modelosRes, catRes, subRes].some(r => r.status === 'rejected');
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

    const loadModeloAlcance = async () => {
        try {
            const response = await api.get('/predicciones/modelos/alcance');
            if (response.data.alcance) {
                setModeloAlcance(response.data);
            }
        } catch (err) {
            // Endpoint no disponible o modelo general
            setModeloAlcance(null);
        }
    };

    const loadHistorial = async (productoId) => {
        setLoadingHistorial(true);
        try {
            const response = await api.get(`/ventas/producto/${productoId}/historial?days=90`);
            setHistorialVentas(response.data);
        } catch (err) {
            setHistorialVentas([]);
        } finally {
            setLoadingHistorial(false);
        }
    };

    const getProductosApredecir = () => {
        return productosSeleccionados;
    };

    const getResumenPredicciones = () => {
        const preds = productosSeleccionados.length > 0
            ? predicciones.filter(p => productosSeleccionados.includes(p.id_producto))
            : predicciones;
        if (preds.length === 0) return null;

        const fechas = preds.map(p => p.fecha_prediccion).filter(Boolean).sort();
        const fechaMin = fechas.length > 0 ? fechas[0] : null;
        const fechaMax = fechas.length > 0 ? fechas[fechas.length - 1] : null;
        const totalDemand = preds.reduce((sum, p) => sum + (p.demanda_estimada || 0), 0);
        const promDiario = preds.length > 0 ? (totalDemand / (preds.length || 1)).toFixed(1) : '0';
        const productosUnicos = new Set(preds.map(p => p.id_producto)).size;

        return {
            totalPredicciones: preds.length,
            productosIncluidos: productosUnicos,
            rangoFechas: fechaMin && fechaMax ? `${fechaMin} al ${fechaMax}` : 'Sin fecha',
            demandaTotal: totalDemand.toLocaleString(),
            promDiario
        };
    };

    const handleGenerar = async () => {
        if (modelosSeleccionados.length === 0) {
            setToast({ message: 'Seleccione un modelo IA', type: 'warning' });
            return;
        }

        const idsProductos = getProductosApredecir();
        if (idsProductos.length === 0) {
            setToast({ message: 'Seleccione al menos un producto', type: 'warning' });
            return;
        }

        const horizonte = calcularHorizonte();

        if (modelosSeleccionados.length === 2) {
            setGenerating(true);
            setProgreso({ total: idsProductos.length * 2, actual: 0, exitosos: 0, fallidos: 0 });
            try {
                for (const modeloId of modelosSeleccionados) {
                    for (const productoId of idsProductos) {
                        try {
                            const payload = { id_producto: productoId, horizonte_dias: horizonte, id_modelo: parseInt(modeloId) };
                            if (fechaInicio) payload.fecha_inicio = fechaInicio;
                            await api.post('/predicciones/predecir', payload);
                            setProgreso(prev => ({ ...prev, actual: prev.actual + 1, exitosos: prev.exitosos + 1 }));
                        } catch {
                            setProgreso(prev => ({ ...prev, actual: prev.actual + 1, fallidos: prev.fallidos + 1 }));
                        }
                    }
                }
                const response = await api.post('/predicciones/predecir-comparar', {
                    id_productos: idsProductos,
                    horizonte_dias: horizonte,
                    id_modelos: modelosSeleccionados.map(Number),
                    fecha_inicio: fechaInicio,
                });
                setComparacion(response.data);
                setProgreso(null);
                setToast({ message: 'Predicciones generadas y comparación lista', type: 'success' });
                loadData();
                loadKpis();
            } catch (err) {
                setToast({ message: err.response?.data?.detail || 'Error al generar predicciones', type: 'error' });
            } finally {
                setGenerating(false);
            }
            return;
        }

        if (idsProductos.length === 1) {
            await predecirProducto(idsProductos[0]);
        } else {
            await predecirLote(idsProductos);
        }
    };

    const calcularHorizonte = () => {
        if (!fechaInicio || !fechaFin) return 30;
        const inicio = new Date(fechaInicio);
        const fin = new Date(fechaFin);
        const diffTime = Math.abs(fin - inicio);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays;
    };

    const toggleModeloSeleccionado = (idModelo) => {
        setModelosSeleccionados(prev =>
            prev.includes(idModelo)
                ? prev.filter(id => id !== idModelo)
                : prev.length < 2 ? [...prev, idModelo] : prev
        );
        setComparacion(null);
    };

    const predecirProducto = async (productoId) => {
        setGenerating(true);
        try {
            const horizonte = calcularHorizonte();
            const payload = {
                id_producto: productoId,
                horizonte_dias: horizonte,
                id_modelo: parseInt(modelosSeleccionados[0])
            };
            
            if (fechaInicio) {
                payload.fecha_inicio = fechaInicio;
            }
            
            await api.post('/predicciones/predecir', payload);
            setToast({ message: 'Predicción generada exitosamente', type: 'success' });
            loadData();
            loadKpis();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al generar predicción', type: 'error' });
        } finally {
            setGenerating(false);
        }
    };

    const predecirLote = async (idsProductos) => {
        setGenerating(true);
        setProgreso({ total: idsProductos.length, actual: 0, exitosos: 0, fallidos: 0 });

        try {
            const horizonte = calcularHorizonte();
            const payload = {
                ids_productos: idsProductos,
                horizonte_dias: horizonte,
                id_modelo: parseInt(modelosSeleccionados[0])
            };
            
            if (fechaInicio) {
                payload.fecha_inicio = fechaInicio;
            }
            
            const response = await api.post('/predicciones/predecir-lote', payload);

            const resultado = response.data;
            setProgreso({
                total: resultado.total_productos,
                actual: resultado.total_productos,
                exitosos: resultado.exitosos,
                fallidos: resultado.fallidos
            });

            if (resultado.fallidos > 0) {
                setToast({
                    message: `${resultado.exitosos} éxitos, ${resultado.fallidos} fallidos`,
                    type: 'warning'
                });
            } else {
                setToast({
                    message: `${resultado.exitosos} predicciones generadas exitosamente`,
                    type: 'success'
                });
            }

            loadData();
            loadKpis();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al generar predicciones', type: 'error' });
        } finally {
            setGenerating(false);
            setTimeout(() => setProgreso(null), 3000);
        }
    };

    const prediccionesProducto = productosSeleccionados.length > 0
        ? predicciones.filter(p => productosSeleccionados.includes(p.id_producto))
        : [];

    const getProducto = (id) => productos.find(p => p.id_producto === id);

    const prepareChartData = () => {
        const historialLabels = historialVentas.map(h => h.fecha);
        const historialData = historialVentas.map(h => h.cantidad);

        const predLabels = prediccionesProducto.map(p => p.fecha_prediccion);
        const predData = prediccionesProducto.map(p => p.demanda_estimada);
        const predMin = prediccionesProducto.map(p => p.confianza_min);
        const predMax = prediccionesProducto.map(p => p.confianza_max);

        const allLabels = [...historialLabels, ...predLabels];

        const historialDataset = new Array(historialLabels.length).fill(null);
        const predDataset = new Array(historialLabels.length).fill(null);

        const fullHistorial = [...historialDataset, ...historialData];
        const fullPred = [...predDataset, ...predData];
        const fullMin = [...new Array(historialLabels.length).fill(null), ...predMin];
        const fullMax = [...new Array(historialLabels.length).fill(null), ...predMax];

        return {
            labels: allLabels,
            datasets: [
                {
                    label: 'Ventas Históricas',
                    data: fullHistorial,
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: false,
                    tension: 0.1,
                    pointRadius: 2
                },
                {
                    label: 'Demanda Estimada',
                    data: fullPred,
                    borderColor: 'rgb(16, 185, 129)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: false,
                    tension: 0.1,
                    pointRadius: 4,
                    borderWidth: 2
                },
                {
                    label: 'Confianza Min',
                    data: fullMin,
                    borderColor: 'rgba(245, 158, 11, 0.5)',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    fill: '+1',
                    tension: 0.1,
                    pointRadius: 0,
                    borderDash: [5, 5]
                },
                {
                    label: 'Confianza Max',
                    data: fullMax,
                    borderColor: 'rgba(245, 158, 11, 0.5)',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    fill: false,
                    tension: 0.1,
                    pointRadius: 0,
                    borderDash: [5, 5]
                }
            ]
        };
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 900,
            easing: 'easeOutQuart',
        },
        hover: {
            mode: 'index',
            intersect: false,
            animation: { duration: 200 },
        },
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 16,
                    font: { size: 12, family: 'Inter, system-ui, sans-serif' },
                }
            },
            title: { display: false },
            tooltip: {
                ...baseTooltipConfig,
                mode: 'index',
                intersect: false,
                callbacks: predictionTooltipCallbacks,
            }
        },
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: 'Fecha',
                    font: { size: 12, weight: '500', family: 'Inter, system-ui, sans-serif' },
                },
                ticks: {
                    maxTicksLimit: 15,
                    maxRotation: 45,
                    minRotation: 45,
                    font: { size: 11, family: 'Inter, system-ui, sans-serif' },
                },
                grid: { color: 'rgba(148, 163, 184, 0.1)' },
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: 'Cantidad',
                    font: { size: 12, weight: '500', family: 'Inter, system-ui, sans-serif' },
                },
                beginAtZero: true,
                ticks: {
                    font: { size: 11, family: 'Inter, system-ui, sans-serif' },
                    callback: (value) => formatNumber(value),
                },
                grid: { color: 'rgba(148, 163, 184, 0.1)' },
            }
        },
        interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false,
        }
    };

    if (loading) return <div className="content-area"><p>Cargando predicción...</p></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Generar Predicción de Demanda</h3>
                </div>

                {modeloAlcance && modeloAlcance.alcance && (
                    <div style={{
                        margin: '0 20px 16px',
                        padding: '12px 16px',
                        backgroundColor: 'var(--info-light)',
                        borderLeft: '4px solid var(--info)',
                        borderRadius: '6px',
                        fontSize: '0.85rem'
                    }}>
                        <strong style={{ color: 'var(--info)' }}>Modelo activo: {modeloAlcance.alcance}</strong>
                        <br />
                        <span style={{ color: 'var(--gray-600)' }}>
                            Alcance: {modeloAlcance.subcategorias?.join(', ')} ({modeloAlcance.total_productos} productos)
                        </span>
                        <br />
                        <small style={{ color: 'var(--gray-500)' }}>
                            Otros productos disponibles en el sistema pero fuera del alcance del modelo actual.
                        </small>
                    </div>
                )}

                <div className="grid-4" style={{ gap: '16px' }}>
                    <div className="form-group">
                        <label>Categoría</label>
                        <select
                            value={selectedCategory}
                            onChange={(e) => { setSelectedCategory(e.target.value); setSelectedSubcategory(''); }}
                            disabled={modeloAlcance && modeloAlcance.alcance}
                        >
                            {modeloAlcance && modeloAlcance.alcance ? (
                                <option value="">Alimentos (modelo acotado)</option>
                            ) : (
                                <>
                                    <option value="">Todas las categorías</option>
                                    {categorias.map(c => (
                                        <option key={c.id_categoria} value={c.id_categoria}>{c.nombre}</option>
                                    ))}
                                </>
                            )}
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Subcategoría</label>
                        <select value={selectedSubcategory} onChange={(e) => setSelectedSubcategory(e.target.value)}>
                            <option value="">Todas las subcategorías</option>
                            {subcategorias
                                .filter(s => {
                                    // Filtrar por categoría seleccionada
                                    if (selectedCategory && selectedCategory !== 'all' && s.id_categoria !== parseInt(selectedCategory)) return false;
                                    // Filtrar por alcance del modelo
                                    if (modeloAlcance && modeloAlcance.alcance && modeloAlcance.subcategorias) {
                                        return modeloAlcance.subcategorias.includes(s.nombre);
                                    }
                                    return true;
                                })
                                .map(s => (
                                    <option key={s.id_subcategoria} value={s.id_subcategoria}>{s.nombre}</option>
                                ))}
                        </select>
                    </div>
                    <div className="form-group" style={{ position: 'relative' }} data-dropdown-productos>
                        <label>Producto</label>
                        <div
                            onClick={() => setShowDropdown(!showDropdown)}
                            style={{
                                width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--gray-300)',
                                backgroundColor: 'white', cursor: 'pointer', minHeight: '38px', display: 'flex', alignItems: 'center',
                                justifyContent: 'space-between'
                            }}
                        >
                            <span style={{ fontSize: '0.9rem', color: productosSeleccionados.length > 0 ? 'var(--gray-900)' : 'var(--gray-500)' }}>
                                {productosSeleccionados.length === 0
                                    ? 'Seleccionar productos...'
                                    : productosSeleccionados.length === productosFiltrados.length
                                        ? `Todos (${productosFiltrados.length})`
                                        : `${productosSeleccionados.length} seleccionado(s)`
                                }
                            </span>
                            <span style={{ fontSize: '0.7rem', color: 'var(--gray-400)' }}>▼</span>
                        </div>
                        {showDropdown && (
                            <div style={{
                                position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 100,
                                backgroundColor: 'white', border: '1px solid var(--gray-300)', borderRadius: '6px',
                                boxShadow: '0 4px 12px rgba(0,0,0,0.15)', maxHeight: '200px', overflowY: 'auto', marginTop: '4px', fontSize: '0.75rem'
                            }}>
                                <label style={{ display: 'flex', alignItems: 'center', gap: '3px', padding: '1px 4px', cursor: 'pointer', fontWeight: 'bold', borderBottom: '1px solid var(--gray-200)', lineHeight: '1.2' }}>
                                    <input
                                        type="checkbox"
                                        checked={productosSeleccionados.length === productosFiltrados.length && productosFiltrados.length > 0}
                                        onChange={() => {
                                            if (productosSeleccionados.length === productosFiltrados.length) {
                                                setProductosSeleccionados([]);
                                            } else {
                                                setProductosSeleccionados(productosFiltrados.map(p => p.id_producto));
                                            }
                                        }}
                                        style={{ margin: 0, width: '13px', height: '13px' }}
                                    />
                                    Todos ({productosFiltrados.length})
                                </label>
                                {productosFiltrados.map(p => (
                                    <label key={p.id_producto} style={{ display: 'flex', alignItems: 'center', gap: '3px', padding: '0px 4px', cursor: 'pointer', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', lineHeight: '1.3' }}>
                                        <input
                                            type="checkbox"
                                            checked={productosSeleccionados.includes(p.id_producto)}
                                            onChange={() => {
                                                setProductosSeleccionados(prev =>
                                                    prev.includes(p.id_producto)
                                                        ? prev.filter(id => id !== p.id_producto)
                                                        : [...prev, p.id_producto]
                                                );
                                            }}
                                            style={{ margin: 0, width: '13px', height: '13px' }}
                                        />
                                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.codigo} - {p.nombre}</span>
                                    </label>
                                ))}
                            </div>
                        )}
                    </div>
                    <div className="form-group" style={{ position: 'relative' }} data-dropdown-modelo>
                        <label>Modelo IA</label>
                        <div
                            onClick={() => setShowModeloDropdown(!showModeloDropdown)}
                            style={{
                                width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--gray-300)',
                                backgroundColor: 'white', cursor: 'pointer', minHeight: '38px', display: 'flex', alignItems: 'center',
                                justifyContent: 'space-between'
                            }}
                        >
                            <span style={{ fontSize: '0.9rem', color: modelosSeleccionados.length > 0 ? 'var(--gray-900)' : 'var(--gray-500)' }}>
                                {modelosSeleccionados.length === 0
                                    ? 'Seleccionar modelo...'
                                    : modelosSeleccionados.length === 1
                                        ? (() => { const m = modelos.find(m => m.id_modelo == modelosSeleccionados[0]); return m ? `${m.algoritmo} (R²: ${m.r2?.toFixed(3) || 'N/A'})` : ''; })()
                                        : `${modelosSeleccionados.length} modelos seleccionados`
                                }
                            </span>
                            <span style={{ fontSize: '0.7rem', color: 'var(--gray-400)' }}>▼</span>
                        </div>
                        {showModeloDropdown && (
                            <div style={{
                                position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 100,
                                backgroundColor: 'white', border: '1px solid var(--gray-300)', borderRadius: '6px',
                                boxShadow: '0 4px 12px rgba(0,0,0,0.15)', maxHeight: '200px', overflowY: 'auto', marginTop: '4px', fontSize: '0.75rem'
                            }}>
                                {modelos.filter(m => m.estado === 'ACTIVO').map(m => (
                                    <label key={m.id_modelo} style={{ display: 'flex', alignItems: 'center', gap: '3px', padding: '1px 4px', cursor: 'pointer', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', lineHeight: '1.3', backgroundColor: modelosSeleccionados.includes(m.id_modelo) ? 'var(--primary-light, #e8f0fe)' : 'transparent' }}>
                                        <input
                                            type="checkbox"
                                            checked={modelosSeleccionados.includes(m.id_modelo)}
                                            onChange={() => toggleModeloSeleccionado(m.id_modelo)}
                                            style={{ margin: 0, width: '13px', height: '13px' }}
                                        />
                                        <span>{m.algoritmo} (R²: {m.r2?.toFixed(3) || 'N/A'})</span>
                                    </label>
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
                                Horizonte: {calcularHorizonte()} días
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
                            {generating ? 'Generando...' : 'Generar Predicción'}
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

            {productosSeleccionados.length > 0 && (
                <div className="card chart-card">
                    <div className="card-header">
                        <h3 className="card-title">Gráfico de Predicción</h3>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            {loadingHistorial && <span style={{ fontSize: '0.8rem', color: 'var(--gray-500)' }}>Cargando historial...</span>}
                            {prediccionesProducto.length > 0 && <ChartExportButton chartRef={chartPrediccionRef} filename="prediccion_demanda" />}
                        </div>
                    </div>
                    {historialVentas.length === 0 && prediccionesProducto.length === 0 ? (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '300px', color: 'var(--gray-500)' }}>
                            <p>No hay datos disponibles para graficar. Genere una predicción primero.</p>
                        </div>
                    ) : (
                        <div style={{ height: '380px', padding: '16px' }}>
                            <Line ref={chartPrediccionRef} data={prepareChartData()} options={chartOptions} />
                        </div>
                    )}
                </div>
            )}

            {comparacion && comparacion.productos && (
                <ErrorBoundary>
                <div className="card chart-card">
                    <div className="card-header">
                        <h3 className="card-title">
                            Comparación de Modelos ({comparacion.productos.length} producto{comparacion.productos.length > 1 ? 's' : ''})
                        </h3>
                    </div>

                    {comparacion.productos.map((producto) => {
                        const modelos = producto.modelos || [];
                        const predicciones0 = modelos[0]?.predicciones || [];
                        if (modelos.length === 0) return null;

                        return (
                        <div key={producto.id_producto} style={{ borderBottom: comparacion.productos.length > 1 ? '2px solid var(--gray-200)' : 'none', padding: '16px' }}>
                            {comparacion.productos.length > 1 && (
                                <h4 style={{ margin: '0 0 12px', fontSize: '1rem', color: 'var(--primary)' }}>
                                    {producto.nombre}
                                </h4>
                            )}

                            <div style={{ height: '320px' }}>
                                <Line
                                    data={{
                                        labels: predicciones0.map(p => p.fecha),
                                        datasets: modelos.map((m, i) => ({
                                            label: `${m.algoritmo} (R²: ${m.r2?.toFixed(3) || 'N/A'})`,
                                            data: (m.predicciones || []).map(p => p.demanda_estimada),
                                            borderColor: [CHART_COLORS.blue.main, CHART_COLORS.green.main, CHART_COLORS.yellow.main, CHART_COLORS.red.main, CHART_COLORS.purple.main][i % 5],
                                            backgroundColor: [CHART_COLORS.blue.bg, CHART_COLORS.green.bg, CHART_COLORS.yellow.bg, CHART_COLORS.red.bg, CHART_COLORS.purple.bg][i % 5],
                                            fill: false,
                                            tension: 0.1,
                                            pointRadius: 3,
                                            pointHoverRadius: 6,
                                            borderWidth: 2.5,
                                            pointBackgroundColor: [CHART_COLORS.blue.main, CHART_COLORS.green.main, CHART_COLORS.yellow.main, CHART_COLORS.red.main, CHART_COLORS.purple.main][i % 5],
                                            pointBorderColor: '#fff',
                                            pointBorderWidth: 2,
                                        })),
                                    }}
                                    options={{
                                        ...chartOptions,
                                        plugins: {
                                            ...chartOptions.plugins,
                                            tooltip: {
                                                ...baseTooltipConfig,
                                                mode: 'index',
                                                intersect: false,
                                                callbacks: comparisonTooltipCallbacks,
                                            },
                                        },
                                    }}
                                />
                            </div>

                            <div style={{ marginTop: '12px', overflowX: 'auto' }}>
                                <table className="data-table" style={{ fontSize: '0.8rem' }}>
                                    <thead>
                                        <tr>
                                            <th>Fecha</th>
                                            {modelos.map(m => (
                                                <th key={m.id_modelo} style={{ textAlign: 'center' }}>
                                                    {m.algoritmo}
                                                </th>
                                            ))}
                                            <th style={{ textAlign: 'center' }}>Diferencia %</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {predicciones0.map((_, idx) => {
                                            const vals = modelos.map(m => m.predicciones?.[idx]?.demanda_estimada || 0);
                                            const max = Math.max(...vals);
                                            const min = Math.min(...vals);
                                            const diff = min > 0 ? ((max - min) / min * 100).toFixed(1) : '0';
                                            return (
                                                <tr key={idx}>
                                                    <td>{predicciones0[idx]?.fecha}</td>
                                                    {modelos.map(m => (
                                                        <td key={m.id_modelo} style={{ textAlign: 'center' }}>
                                                            {m.predicciones?.[idx]?.demanda_estimada}
                                                        </td>
                                                    ))}
                                                    <td style={{ textAlign: 'center', color: parseFloat(diff) > 10 ? 'var(--warning)' : 'var(--gray-600)' }}>
                                                        {diff}%
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                    <tfoot>
                                        <tr style={{ fontWeight: 'bold', backgroundColor: 'var(--gray-100)' }}>
                                            <td>Promedio</td>
                                            {modelos.map(m => {
                                                const preds = m.predicciones || [];
                                                const prom = preds.length > 0 ? preds.reduce((s, p) => s + (p.demanda_estimada || 0), 0) / preds.length : 0;
                                                return (
                                                    <td key={m.id_modelo} style={{ textAlign: 'center' }}>
                                                        {prom.toFixed(1)}
                                                    </td>
                                                );
                                            })}
                                            <td></td>
                                        </tr>
                                    </tfoot>
                                </table>
                            </div>
                        </div>
                        );
                    })}
                </div>
                </ErrorBoundary>
            )}

            {kpis && kpis.total_productos > 0 && (
                <div className="card chart-card">
                    <div className="card-header">
                        <h3 className="card-title">KPIs de Rentabilidad</h3>
                        {loadingKpis && <span style={{ fontSize: '0.8rem', color: 'var(--gray-500)' }}>Calculando...</span>}
                    </div>
                    
                    <div className="grid-4" style={{ gap: '16px', marginBottom: '20px' }}>
                        <div className="kpi-card" style={{ background: 'linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%)' }}>
                            <div className="kpi-label">Ingreso Total Esperado</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                                {formatCurrency(kpis.ingreso_total_esperado)}
                            </div>
                        </div>
                        <div className="kpi-card" style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
                            <div className="kpi-label">Ganancia Total Esperada</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                                {formatCurrency(kpis.ganancia_total_esperada)}
                            </div>
                        </div>
                        <div className="kpi-card" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
                            <div className="kpi-label">Costo Total Esperado</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                                {formatCurrency(kpis.costo_total_esperado)}
                            </div>
                        </div>
                        <div className="kpi-card" style={{ background: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)' }}>
                            <div className="kpi-label">Productos con Predicción</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                                {formatNumber(kpis.total_productos)}
                            </div>
                        </div>
                    </div>

                    {kpis.producto_mayor_volumen && (
                        <div className="grid-3" style={{ gap: '16px', marginBottom: '20px' }}>
                            <div className="card" style={{ backgroundColor: 'var(--gray-50)', padding: '14px', borderLeft: '4px solid var(--primary)' }}>
                                <div style={{ fontSize: '0.75rem', color: 'var(--gray-500)', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Mayor Volumen de Venta</div>
                                <div style={{ fontWeight: 'bold', color: 'var(--primary)', marginBottom: '4px' }}>{kpis.producto_mayor_volumen.nombre}</div>
                                <div style={{ fontSize: '0.9rem', color: 'var(--gray-700)' }}>
                                    Demanda: <strong>{formatNumber(kpis.producto_mayor_volumen.demanda_total)}</strong> unidades
                                </div>
                            </div>
                            <div className="card" style={{ backgroundColor: 'var(--gray-50)', padding: '14px', borderLeft: '4px solid #10b981' }}>
                                <div style={{ fontSize: '0.75rem', color: 'var(--gray-500)', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Mayor Rentabilidad</div>
                                <div style={{ fontWeight: 'bold', color: '#10b981', marginBottom: '4px' }}>{kpis.producto_mayor_rentabilidad.nombre}</div>
                                <div style={{ fontSize: '0.9rem', color: 'var(--gray-700)' }}>
                                    Ganancia: <strong>{formatCurrency(kpis.producto_mayor_rentabilidad.ganancia_esperada)}</strong>
                                </div>
                            </div>
                            <div className="card" style={{ backgroundColor: 'var(--gray-50)', padding: '14px', borderLeft: '4px solid #f59e0b' }}>
                                <div style={{ fontSize: '0.75rem', color: 'var(--gray-500)', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Mayor Ingreso</div>
                                <div style={{ fontWeight: 'bold', color: '#f59e0b', marginBottom: '4px' }}>{kpis.producto_mayor_ingreso.nombre}</div>
                                <div style={{ fontSize: '0.9rem', color: 'var(--gray-700)' }}>
                                    Ingreso: <strong>{formatCurrency(kpis.producto_mayor_ingreso.ingreso_esperado)}</strong>
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
                                    <th>Prom. Diario</th>
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
                                        <td>{formatNumber(kpi.demanda_total)}</td>
                                        <td style={{ color: 'var(--info)', fontWeight: 'bold' }}>
                                            {kpi.venta_promedio_diaria?.toFixed(1) || '0.0'}/día
                                        </td>
                                        <td>{formatCurrency(kpi.precio_venta)}</td>
                                        <td style={{ color: kpi.margen_porcentaje > 20 ? 'var(--success)' : 'var(--warning)' }}>
                                            {kpi.margen_porcentaje.toFixed(1)}%
                                        </td>
                                        <td>{formatCurrency(kpi.ingreso_esperado)}</td>
                                        <td style={{ color: 'var(--success)', fontWeight: 'bold' }}>
                                            {formatCurrency(kpi.ganancia_esperada)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            <div className="card">
                {(() => {
                    const resumen = getResumenPredicciones();
                    if (!resumen) return null;
                    return (
                        <div style={{ padding: '16px', backgroundColor: 'var(--primary-light)', borderRadius: '8px 8px 0 0', borderBottom: '2px solid var(--primary)' }}>
                            <h4 style={{ margin: '0 0 12px 0', fontSize: '0.95rem', color: 'var(--primary)' }}>Resumen de Predicciones</h4>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
                                <div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--gray-500)' }}>Rango de Fechas</div>
                                    <div style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>{resumen.rangoFechas}</div>
                                </div>
                                <div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--gray-500)' }}>Productos Incluidos</div>
                                    <div style={{ fontWeight: 'bold', fontSize: '0.9rem', color: 'var(--primary)' }}>{resumen.productosIncluidos}</div>
                                </div>
                                <div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--gray-500)' }}>Total Predicciones</div>
                                    <div style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>{resumen.totalPredicciones}</div>
                                </div>
                                <div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--gray-500)' }}>Demanda Total Estimada</div>
                                    <div style={{ fontWeight: 'bold', fontSize: '0.9rem', color: 'var(--success)' }}>{resumen.demandaTotal} unidades</div>
                                </div>
                            </div>
                        </div>
                    );
                })()}
                <div className="card-header">
                    <h3 className="card-title">Historial de Predicciones</h3>
                    <ExportButtons
                        data={(productosSeleccionados.length > 0 ? prediccionesProducto : predicciones).slice(0, 200).map(pred => {
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
                        <p>No hay predicciones registradas. Seleccione un producto y genere una predicción.</p>
                    </div>
                ) : (
                    <div className="table-container" style={{ maxHeight: '520px', overflowY: 'auto' }}>
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
                                {(productosSeleccionados.length > 0 ? prediccionesProducto : predicciones).slice(0, 200).map(pred => {
                                    const prod = getProducto(pred.id_producto);
                                    return (
                                        <tr key={pred.id_prediccion}>
                                            <td>#{pred.id_prediccion}</td>
                                            <td>{prod ? `${prod.codigo} - ${prod.nombre}` : `#${pred.id_producto}`}</td>
                                            <td><strong style={{ color: 'var(--primary)' }}>{pred.demanda_estimada}</strong></td>
                                            <td>{formatCurrency(pred.precio_venta)}</td>
                                            <td style={{ color: 'var(--success)', fontWeight: 'bold' }}>
                                                {formatCurrency(pred.ingreso_esperado)}
                                            </td>
                                            <td style={{ color: 'var(--success)' }}>
                                                {formatCurrency(pred.ganancia_esperada)}
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

            <div className="grid-3" style={{ marginTop: '24px' }}>
                <div className="kpi-card" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' }}>
                    <div className="kpi-label">Total Predicciones</div>
                    <div className="kpi-value">{formatNumber(predicciones.length)}</div>
                </div>
                <div className="kpi-card" style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
                    <div className="kpi-label">Productos con Predicciones</div>
                    <div className="kpi-value">{formatNumber(new Set(predicciones.map(p => p.id_producto)).size)}</div>
                </div>
                <div className="kpi-card" style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' }}>
                    <div className="kpi-label">Modelos Disponibles</div>
                    <div className="kpi-value">{modelos.length}</div>
                    {modelos.length > 0 && (
                        <div style={{ fontSize: '0.8rem', opacity: 0.9, marginTop: '4px' }}>
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
