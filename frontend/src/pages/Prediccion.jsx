import { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';
import ExportButtons from '../components/ExportButtons';
import MultiSelect from '../components/MultiSelect';
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

export default function Prediccion() {
    const [productos, setProductos] = useState([]);
    const [categorias, setCategorias] = useState([]);
    const [subcategorias, setSubcategorias] = useState([]);
    const [predicciones, setPredicciones] = useState([]);
    const [modelos, setModelos] = useState([]);
    const [modelosSeleccionados, setModelosSeleccionados] = useState([]);
    const [modeloActivoTab, setModeloActivoTab] = useState(null);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedSubcategory, setSelectedSubcategory] = useState('');
    const [selectedProducts, setSelectedProducts] = useState([]);
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

    useEffect(() => {
        loadData();
        loadKpis();
    }, []);

    useEffect(() => {
        let filtrados = productos;
        if (selectedCategory !== '' && selectedCategory !== 'all') {
            filtrados = filtrados.filter(p => p.id_categoria === parseInt(selectedCategory));
        }
        if (selectedSubcategory !== '' && selectedSubcategory !== 'all') {
            filtrados = filtrados.filter(p => p.id_subcategoria === parseInt(selectedSubcategory));
        }
        setProductosFiltrados(filtrados);
    }, [selectedCategory, selectedSubcategory, productos]);

    const prevCategoryRef = useRef(selectedCategory);
    useEffect(() => {
        if (prevCategoryRef.current !== selectedCategory) {
            setSelectedProducts([]);
            setSelectedSubcategory('');
            prevCategoryRef.current = selectedCategory;
        }
    }, [selectedCategory]);

    useEffect(() => {
        if (selectedProducts.length >= 1) {
            loadHistorial(selectedProducts[0]);
        } else {
            setHistorialVentas([]);
        }
    }, [selectedProducts]);

    useEffect(() => {
        if (modelosSeleccionados.length > 0 && !modelosSeleccionados.includes(modeloActivoTab)) {
            setModeloActivoTab(modelosSeleccionados[0]);
        }
    }, [modelosSeleccionados]);

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
            const activo = listaModelos.find(m => m.estado === 'ACTIVO');
            if (activo) setModelosSeleccionados([activo.id_modelo]);
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
        return selectedProducts;
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

        if (!fechaInicio || !fechaFin) {
            setToast({ message: 'Seleccione las fechas de inicio y fin', type: 'warning' });
            return;
        }

        if (new Date(fechaFin) <= new Date(fechaInicio)) {
            setToast({ message: 'La fecha de fin debe ser mayor a la fecha de inicio', type: 'warning' });
            return;
        }

        if (modelosSeleccionados.length === 1 && idsProductos.length === 1) {
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

    const predecirProducto = async (productoId) => {
        setGenerating(true);
        try {
            const horizonte = calcularHorizonte();
            const payload = {
                id_producto: productoId,
                horizonte_dias: horizonte,
                id_modelo: modelosSeleccionados[0]
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
                ids_modelos: modelosSeleccionados,
                horizonte_dias: horizonte
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

    const prediccionesProducto = selectedProducts.length > 0
        ? predicciones.filter(p => selectedProducts.includes(p.id_producto))
        : [];

    const prediccionesModeloActivo = modeloActivoTab
        ? prediccionesProducto.filter(p => p.id_modelo === modeloActivoTab)
        : prediccionesProducto;

    const getProducto = (id) => productos.find(p => p.id_producto === id);

    const coloresModelos = ['#2563eb', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

    const prepareChartData = () => {
        const historialLabels = historialVentas.map(h => h.fecha).sort();
        const historialDataMap = new Map(historialVentas.map(h => [h.fecha, h.cantidad]));
        const historialData = historialLabels.map(f => historialDataMap.get(f));

        // Si hay multiples modelos seleccionados, mostrar overlay
        const mostrarOverlay = modelosSeleccionados.length > 1;

        if (mostrarOverlay) {
            // Overlay: una linea por modelo
            const todosFechas = new Set(historialLabels);
            prediccionesProducto.forEach(p => todosFechas.add(p.fecha_prediccion));
            const allLabels = Array.from(todosFechas).sort();

            const datasets = [{
                label: 'Ventas Historicas',
                data: allLabels.map(f => {
                    const idx = historialLabels.indexOf(f);
                    return idx >= 0 ? historialData[idx] : null;
                }),
                borderColor: 'rgb(100, 116, 139)',
                backgroundColor: 'rgba(100, 116, 139, 0.1)',
                fill: false,
                tension: 0.1,
                pointRadius: 2,
                borderDash: [5, 5],
                borderWidth: 2
            }];

            modelosSeleccionados.forEach((modeloId, idx) => {
                const modelo = modelos.find(m => m.id_modelo === modeloId);
                const preds = prediccionesProducto.filter(p => p.id_modelo === modeloId);
                const nombreModelo = modelo ? `${modelo.algoritmo} v${modelo.version || '?'}` : `Modelo ${modeloId}`;
                const color = coloresModelos[idx % coloresModelos.length];
                datasets.push({
                    label: nombreModelo,
                    data: allLabels.map(f => {
                        const pred = preds.find(p => p.fecha_prediccion === f);
                        return pred ? pred.demanda_estimada : null;
                    }),
                    borderColor: color,
                    backgroundColor: color + '20',
                    fill: false,
                    tension: 0.1,
                    pointRadius: 4,
                    borderWidth: 2
                });
            });

            return { labels: allLabels, datasets };
        }

        // Modo simple: un solo modelo
        const modeloActivo = modeloActivoTab
            ? modelos.find(m => m.id_modelo === modeloActivoTab)
            : modelos.find(m => m.id_modelo === modelosSeleccionados[0]);
        const nombreModelo = modeloActivo ? `${modeloActivo.algoritmo} v${modeloActivo.version || '?'}` : 'Modelo IA';

        const prediccionesMap = new Map(prediccionesModeloActivo.map(p => [p.fecha_prediccion, p]));
        const predLabels = [...new Set(prediccionesModeloActivo.map(p => p.fecha_prediccion))].sort();
        const predData = predLabels.map(f => prediccionesMap.get(f)?.demanda_estimada);
        const predMin = predLabels.map(f => prediccionesMap.get(f)?.confianza_min);
        const predMax = predLabels.map(f => prediccionesMap.get(f)?.confianza_max);

        const allLabelsUnsorted = [...historialLabels, ...predLabels];
        const allLabels = [...allLabelsUnsorted].sort();

        const historialDataset = allLabels.map(f => {
            const idx = historialLabels.indexOf(f);
            return idx >= 0 ? historialData[idx] : null;
        });
        const predDataset = allLabels.map(f => {
            const idx = predLabels.indexOf(f);
            return idx >= 0 ? predData[idx] : null;
        });
        const fullMin = allLabels.map(f => {
            const idx = predLabels.indexOf(f);
            return idx >= 0 ? predMin[idx] : null;
        });
        const fullMax = allLabels.map(f => {
            const idx = predLabels.indexOf(f);
            return idx >= 0 ? predMax[idx] : null;
        });

        return {
            labels: allLabels,
            datasets: [
                {
                    label: 'Ventas Historicas',
                    data: historialDataset,
                    borderColor: 'rgb(100, 116, 139)',
                    backgroundColor: 'rgba(100, 116, 139, 0.1)',
                    fill: false,
                    tension: 0.1,
                    pointRadius: 2,
                    borderDash: [5, 5]
                },
                {
                    label: `${nombreModelo} - Limite Superior`,
                    data: fullMax,
                    borderColor: 'rgba(239, 68, 68, 0.6)',
                    backgroundColor: 'rgba(239, 68, 68, 0.08)',
                    fill: '+2',
                    tension: 0.1,
                    pointRadius: 0,
                    borderDash: [6, 3],
                    borderWidth: 1.5
                },
                {
                    label: `${nombreModelo} - Prediccion`,
                    data: predDataset,
                    borderColor: coloresModelos[0],
                    backgroundColor: coloresModelos[0] + '20',
                    fill: false,
                    tension: 0.1,
                    pointRadius: 4,
                    borderWidth: 2.5
                },
                {
                    label: `${nombreModelo} - Limite Inferior`,
                    data: fullMin,
                    borderColor: 'rgba(59, 130, 246, 0.6)',
                    backgroundColor: 'rgba(59, 130, 246, 0.08)',
                    fill: false,
                    tension: 0.1,
                    pointRadius: 0,
                    borderDash: [6, 3],
                    borderWidth: 1.5
                }
            ]
        };
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 20,
                    font: {
                        size: 12,
                        weight: 'bold'
                    }
                }
            },
            title: {
                display: false
            },
            tooltip: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    title: function(context) {
                        return context[0]?.label || '';
                    }
                }
            }
        },
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: 'Fecha'
                },
                ticks: {
                    maxTicksLimit: 15,
                    maxRotation: 45,
                    minRotation: 45
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: 'Cantidad'
                },
                beginAtZero: true
            }
        },
        interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
        }
    };

    if (loading) return <div className="content-area"><p>Cargando predicción...</p></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Generar Predicción de Demanda</h3>
                    {modelosSeleccionados.length > 0 && <span className="badge badge-success">Modelo Seleccionado</span>}
                </div>

                <div className="grid-2" style={{ gap: '16px' }}>
                    <div className="form-group" style={{ marginBottom: '12px' }}>
                        <label style={{ fontSize: '0.8rem', marginBottom: '4px' }}>Categoría</label>
                        <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)}
                            style={{ width: '100%', padding: '6px 10px', borderRadius: '6px', border: '1px solid var(--gray-300)', fontSize: '0.85rem' }}>
                            <option value="">Todas las categorías</option>
                            {categorias.map(c => (
                                <option key={c.id_categoria} value={c.id_categoria}>{c.nombre}</option>
                            ))}
                        </select>
                    </div>
                    <div className="form-group" style={{ marginBottom: '12px' }}>
                        <label style={{ fontSize: '0.8rem', marginBottom: '4px' }}>Subcategoría</label>
                        <select value={selectedSubcategory} onChange={(e) => setSelectedSubcategory(e.target.value)}
                            style={{ width: '100%', padding: '6px 10px', borderRadius: '6px', border: '1px solid var(--gray-300)', fontSize: '0.85rem' }}>
                            <option value="">Todas las subcategorías</option>
                            {subcategorias
                                .filter(s => selectedCategory === '' || selectedCategory === 'all' || s.id_categoria === parseInt(selectedCategory))
                                .map(s => (
                                <option key={s.id_subcategoria} value={s.id_subcategoria}>{s.nombre}</option>
                            ))}
                        </select>
                    </div>
                </div>

                <div className="grid-2" style={{ gap: '16px' }}>
                    <div className="form-group" style={{ marginBottom: '12px' }}>
                        <label style={{ fontSize: '0.8rem', marginBottom: '4px' }}>Productos ({productosFiltrados.length} disponibles)</label>
                        <MultiSelect
                            items={productosFiltrados.map(p => ({
                                value: p.id_producto,
                                label: `${p.codigo} - ${p.nombre}`
                            }))}
                            selectedIds={selectedProducts}
                            onSelectionChange={setSelectedProducts}
                            placeholder="Seleccionar productos..."
                            searchPlaceholder="Buscar producto..."
                            showSelectAll={true}
                        />
                    </div>
                    <div className="form-group" style={{ marginBottom: '12px' }}>
                        <label style={{ fontSize: '0.8rem', marginBottom: '4px' }}>Modelo IA</label>
                        <MultiSelect
                            items={modelos.filter(m => m.estado === 'ACTIVO').map(m => ({
                                value: m.id_modelo,
                                label: `${m.algoritmo} (R²: ${m.r2?.toFixed(3) || 'N/A'})`
                            }))}
                            selectedIds={modelosSeleccionados}
                            onSelectionChange={setModelosSeleccionados}
                            placeholder="Seleccionar modelo..."
                            searchPlaceholder="Buscar modelo..."
                            showSelectAll={false}
                        />
                    </div>
                </div>

                <div className="grid-3" style={{ gap: '16px', marginTop: '12px' }}>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label style={{ fontSize: '0.8rem', marginBottom: '4px' }}>Fecha de Inicio</label>
                        <input
                            type="date"
                            value={fechaInicio}
                            onChange={(e) => setFechaInicio(e.target.value)}
                            min={new Date().toISOString().split('T')[0]}
                            style={{ width: '100%', padding: '6px 10px', borderRadius: '6px', border: '1px solid var(--gray-300)', fontSize: '0.85rem' }}
                        />
                    </div>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label style={{ fontSize: '0.8rem', marginBottom: '4px' }}>Fecha de Fin</label>
                        <input
                            type="date"
                            value={fechaFin}
                            onChange={(e) => setFechaFin(e.target.value)}
                            min={fechaInicio || new Date().toISOString().split('T')[0]}
                            style={{ width: '100%', padding: '6px 10px', borderRadius: '6px', border: '1px solid var(--gray-300)', fontSize: '0.85rem' }}
                        />
                        {fechaInicio && fechaFin && (
                            <small style={{ color: 'var(--primary)', fontSize: '0.75rem', fontWeight: 'bold' }}>
                                Horizonte: {calcularHorizonte()} días
                            </small>
                        )}
                    </div>
                    <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end', marginBottom: 0 }}>
                        <button
                            onClick={handleGenerar}
                            disabled={generating}
                            style={{
                                width: '100%',
                                padding: '12px 24px',
                                fontSize: '0.9rem',
                                fontWeight: '600',
                                color: '#fff',
                                background: generating ? 'var(--gray-400)' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                border: 'none',
                                borderRadius: '50px',
                                cursor: generating ? 'not-allowed' : 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                gap: '8px',
                                boxShadow: generating ? 'none' : '0 4px 15px rgba(102, 126, 234, 0.4)',
                                transition: 'all 0.3s ease',
                                opacity: generating ? 0.7 : 1
                            }}
                            onMouseEnter={(e) => {
                                if (!generating) {
                                    e.target.style.transform = 'translateY(-2px)';
                                    e.target.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.5)';
                                }
                            }}
                            onMouseLeave={(e) => {
                                e.target.style.transform = 'translateY(0)';
                                e.target.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)';
                            }}
                        >
                            <span>{generating ? 'Generando...' : 'Generar Predicción'}</span>
                            <span style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                width: '28px',
                                height: '28px',
                                borderRadius: '50%',
                                background: 'rgba(255,255,255,0.2)',
                                fontSize: '1rem',
                                flexShrink: 0
                            }}>
                                {generating ? '⏳' : '→'}
                            </span>
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

            {prediccionesProducto.length > 0 && (
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Grafico de Prediccion</h3>
                        {loadingHistorial && <span style={{ fontSize: '0.8rem', color: 'var(--gray-500)' }}>Cargando historial...</span>}
                    </div>
                    {modelosSeleccionados.length > 1 && (
                        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', padding: '0 16px 12px' }}>
                            {modelosSeleccionados.map((modeloId, idx) => {
                                const modelo = modelos.find(m => m.id_modelo === modeloId);
                                return (
                                    <span key={modeloId} style={{
                                        display: 'inline-flex',
                                        alignItems: 'center',
                                        gap: '6px',
                                        padding: '4px 10px',
                                        borderRadius: '12px',
                                        fontSize: '0.75rem',
                                        fontWeight: '600',
                                        backgroundColor: coloresModelos[idx % coloresModelos.length] + '15',
                                        color: coloresModelos[idx % coloresModelos.length],
                                        border: `1px solid ${coloresModelos[idx % coloresModelos.length]}40`
                                    }}>
                                        <span style={{ width: '10px', height: '3px', backgroundColor: coloresModelos[idx % coloresModelos.length], borderRadius: '2px' }} />
                                        {modelo?.algoritmo} v{modelo?.version || '?'}
                                    </span>
                                );
                            })}
                        </div>
                    )}
                    {historialVentas.length === 0 && prediccionesProducto.length === 0 ? (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '300px', color: 'var(--gray-500)' }}>
                            <p>No hay datos disponibles para graficar. Genere una prediccion primero.</p>
                        </div>
                    ) : (
                        <div style={{ height: '350px', padding: '16px' }}>
                            <Line data={prepareChartData()} options={chartOptions} />
                        </div>
                    )}
                </div>
            )}

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
                            <div className="card-title" style={{ fontSize: '0.85rem', color: 'var(--gray-600)' }}>Productos con Predicción</div>
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
                        data={(modelosSeleccionados.length > 1 && modeloActivoTab
                            ? prediccionesModeloActivo
                            : selectedProducts.length > 0 ? prediccionesProducto : predicciones
                        ).slice(0, 200).map(pred => {
                            const prod = getProducto(pred.id_producto);
                            const modelo = modelos.find(m => m.id_modelo === pred.id_modelo);
                            return {
                                id_prediccion: `#${pred.id_prediccion}`,
                                producto: prod ? `${prod.codigo} - ${prod.nombre}` : `#${pred.id_producto}`,
                                modelo: modelo?.algoritmo || '-',
                                periodo: pred.periodo || '-',
                                demanda_estimada: pred.demanda_estimada,
                                venta_promedio_por_dia: pred.venta_promedio_por_dia?.toFixed(2) || '-',
                                precio_venta: pred.precio_venta ? `$${pred.precio_venta.toFixed(2)}` : '-',
                                ingreso_esperado: pred.ingreso_esperado ? `$${pred.ingreso_esperado.toLocaleString('es-EC', { minimumFractionDigits: 2 })}` : '-',
                                ganancia_esperada: pred.ganancia_esperada ? `$${pred.ganancia_esperada.toLocaleString('es-EC', { minimumFractionDigits: 2 })}` : '-',
                                margen_porcentaje: pred.margen_porcentaje ? `${pred.margen_porcentaje.toFixed(1)}%` : '-',
                                fecha_prediccion: pred.fecha_prediccion || '-',
                            };
                        })}
                        columns={[
                            { key: 'id_prediccion', label: 'ID' },
                            { key: 'producto', label: 'Producto' },
                            { key: 'modelo', label: 'Modelo' },
                            { key: 'demanda_estimada', label: 'Demanda' },
                            { key: 'venta_promedio_por_dia', label: 'Venta Prom/Dia' },
                            { key: 'precio_venta', label: 'Precio' },
                            { key: 'ingreso_esperado', label: 'Ingreso Esperado' },
                            { key: 'ganancia_esperada', label: 'Ganancia' },
                            { key: 'margen_porcentaje', label: 'Margen' },
                            { key: 'fecha_prediccion', label: 'Fecha' },
                        ]}
                        moduleName="prediccion"
                        metadata={{
                            fechaInicio: fechaInicio || (predicciones.length > 0 ? predicciones[0]?.fecha_prediccion : null),
                            fechaFin: fechaFin || (predicciones.length > 0 ? predicciones[predicciones.length - 1]?.fecha_prediccion : null),
                            modelo: modelosSeleccionados.length === 1
                                ? (modelos.find(m => m.id_modelo === modelosSeleccionados[0])?.algoritmo || '-')
                                : 'Múltiples modelos'
                        }}
                    />
                </div>
                {predicciones.length === 0 ? (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '200px', color: 'var(--gray-500)' }}>
                        <p>No hay predicciones registradas. Seleccione un producto y genere una predicción.</p>
                    </div>
                ) : (
                    <>
                        {predicciones.length > 0 && (
                            <div style={{ display: 'flex', gap: '24px', padding: '12px 16px', background: 'var(--primary-light)', borderRadius: '8px', marginBottom: '12px', fontSize: '0.9rem', color: 'var(--gray-700)', flexWrap: 'wrap' }}>
                                <span><strong>Rango:</strong> {predicciones[0]?.fecha_prediccion || '-'} al {predicciones[predicciones.length - 1]?.fecha_prediccion || '-'}</span>
                                <span><strong>Productos:</strong> {new Set(predicciones.map(p => p.id_producto)).size}</span>
                                <span><strong>Promedio ventas/dia:</strong> {(predicciones.reduce((sum, p) => sum + (p.venta_promedio_por_dia || 0), 0) / predicciones.length).toFixed(2)} uds</span>
                            </div>
                        )}
                        {modelosSeleccionados.length > 1 && (
                            <div style={{ display: 'flex', gap: '4px', marginBottom: '12px', borderBottom: '2px solid var(--gray-200)', paddingBottom: '0' }}>
                                {modelosSeleccionados.map((modeloId, idx) => {
                                    const modelo = modelos.find(m => m.id_modelo === modeloId);
                                    const isActive = modeloActivoTab === modeloId;
                                    return (
                                        <button
                                            key={modeloId}
                                            onClick={() => setModeloActivoTab(modeloId)}
                                            style={{
                                                padding: '8px 16px',
                                                border: 'none',
                                                borderBottom: isActive ? `3px solid ${coloresModelos[idx % coloresModelos.length]}` : '3px solid transparent',
                                                background: 'transparent',
                                                cursor: 'pointer',
                                                fontWeight: isActive ? '700' : '500',
                                                fontSize: '0.85rem',
                                                color: isActive ? coloresModelos[idx % coloresModelos.length] : 'var(--gray-500)',
                                                transition: 'all 0.2s',
                                            }}
                                        >
                                            {modelo?.algoritmo || `Modelo ${modeloId}`}
                                        </button>
                                    );
                                })}
                            </div>
                        )}
                        <div className="table-container" style={{ maxHeight: '520px', overflowY: 'auto' }}>
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Producto</th>
                                        {modelosSeleccionados.length > 1 && <th>Modelo</th>}
                                        <th>Demanda</th>
                                        <th>Venta Prom/Dia</th>
                                        <th>Precio</th>
                                        <th>Ingreso Esperado</th>
                                        <th>Ganancia</th>
                                        <th>Margen</th>
                                        <th>Fecha</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {(modelosSeleccionados.length > 1 && modeloActivoTab
                                        ? prediccionesModeloActivo
                                        : selectedProducts.length > 0 ? prediccionesProducto : predicciones
                                    ).sort((a, b) => (a.fecha_prediccion || '').localeCompare(b.fecha_prediccion || '')).slice(0, 200).map(pred => {
                                        const prod = getProducto(pred.id_producto);
                                        return (
                                            <tr key={pred.id_prediccion}>
                                                <td>#{pred.id_prediccion}</td>
                                                <td>{prod ? `${prod.codigo} - ${prod.nombre}` : `#${pred.id_producto}`}</td>
                                                {modelosSeleccionados.length > 1 && (
                                                    <td>
                                                        <span style={{
                                                            padding: '2px 8px',
                                                            borderRadius: '12px',
                                                            fontSize: '0.75rem',
                                                            fontWeight: 600,
                                                            background: coloresModelos[modelosSeleccionados.indexOf(pred.id_modelo) % coloresModelos.length] + '20',
                                                            color: coloresModelos[modelosSeleccionados.indexOf(pred.id_modelo) % coloresModelos.length]
                                                        }}>
                                                            {modelos.find(m => m.id_modelo === pred.id_modelo)?.algoritmo || `M${pred.id_modelo}`}
                                                        </span>
                                                    </td>
                                                )}
                                                <td><strong style={{ color: 'var(--primary)' }}>{pred.demanda_estimada}</strong></td>
                                                <td style={{ color: 'var(--info)', fontWeight: '600' }}>{pred.venta_promedio_por_dia?.toFixed(2) || '-'}</td>
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
                    </>
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
                    <div className="card-title">Modelos Activos</div>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>{modelos.filter(m => m.estado === 'ACTIVO').length}</div>
                    {modelos.filter(m => m.estado === 'ACTIVO').length > 0 && (
                        <div style={{ fontSize: '0.8rem', color: 'var(--gray-500)', marginTop: '4px' }}>
                            {modelos.filter(m => m.estado === 'ACTIVO').map(m => m.algoritmo).join(' | ')}
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
