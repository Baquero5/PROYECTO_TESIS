import { useState, useEffect } from 'react';
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

export default function Prediccion() {
    const [productos, setProductos] = useState([]);
    const [categorias, setCategorias] = useState([]);
    const [predicciones, setPredicciones] = useState([]);
    const [modelos, setModelos] = useState([]);
    const [modeloSeleccionado, setModeloSeleccionado] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedProduct, setSelectedProduct] = useState('');
    const [productosFiltrados, setProductosFiltrados] = useState([]);
    const [horizonte, setHorizonte] = useState('30');
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [progreso, setProgreso] = useState(null);
    const [toast, setToast] = useState(null);
    const [historialVentas, setHistorialVentas] = useState([]);
    const [loadingHistorial, setLoadingHistorial] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    useEffect(() => {
        if (selectedCategory === '') {
            setProductosFiltrados(productos);
        } else if (selectedCategory === 'all') {
            setProductosFiltrados(productos);
        } else {
            const filtrados = productos.filter(p => p.id_categoria === parseInt(selectedCategory));
            setProductosFiltrados(filtrados);
        }
        setSelectedProduct('');
    }, [selectedCategory, productos]);

    useEffect(() => {
        if (selectedProduct && selectedProduct !== 'all') {
            loadHistorial(selectedProduct);
        } else {
            setHistorialVentas([]);
        }
    }, [selectedProduct]);

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
            if (activo) setModeloSeleccionado(activo.id_modelo);
        }

        const hasError = [prodRes, predRes, modelosRes, catRes].some(r => r.status === 'rejected');
        if (hasError) setToast({ message: 'Algunos datos no se pudieron cargar', type: 'warning' });

        setLoading(false);
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
        if (selectedProduct === 'all') {
            return productosFiltrados.map(p => p.id_producto);
        } else if (selectedProduct) {
            return [parseInt(selectedProduct)];
        }
        return [];
    };

    const handleGenerar = async () => {
        if (!modeloSeleccionado) {
            setToast({ message: 'Seleccione un modelo IA', type: 'warning' });
            return;
        }

        const idsProductos = getProductosApredecir();
        if (idsProductos.length === 0) {
            setToast({ message: 'Seleccione al menos un producto', type: 'warning' });
            return;
        }

        if (idsProductos.length === 1) {
            await predecirProducto(idsProductos[0]);
        } else {
            await predecirLote(idsProductos);
        }
    };

    const predecirProducto = async (productoId) => {
        setGenerating(true);
        try {
            await api.post('/predicciones/predecir', {
                id_producto: productoId,
                horizonte_dias: parseInt(horizonte),
                id_modelo: parseInt(modeloSeleccionado)
            });
            setToast({ message: 'Predicción generada exitosamente', type: 'success' });
            loadData();
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
            const response = await api.post('/predicciones/predecir-lote', {
                ids_productos: idsProductos,
                horizonte_dias: parseInt(horizonte),
                id_modelo: parseInt(modeloSeleccionado)
            });

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
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al generar predicciones', type: 'error' });
        } finally {
            setGenerating(false);
            setTimeout(() => setProgreso(null), 3000);
        }
    };

    const prediccionesProducto = selectedProduct && selectedProduct !== 'all'
        ? predicciones.filter(p => p.id_producto === parseInt(selectedProduct))
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
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 15
                }
            },
            title: {
                display: false
            },
            tooltip: {
                mode: 'index',
                intersect: false
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
                    {modeloSeleccionado && <span className="badge badge-success">Modelo Seleccionado</span>}
                </div>

                <div className="grid-3" style={{ gap: '16px' }}>
                    <div className="form-group">
                        <label>Categoría</label>
                        <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)}>
                            <option value="">Todas las categorías</option>
                            {categorias.map(c => (
                                <option key={c.id_categoria} value={c.id_categoria}>{c.nombre}</option>
                            ))}
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Producto</label>
                        <select value={selectedProduct} onChange={(e) => setSelectedProduct(e.target.value)}>
                            <option value="">Todos los productos</option>
                            <option value="all">Todos los productos ({productosFiltrados.length})</option>
                            {productosFiltrados.map(p => (
                                <option key={p.id_producto} value={p.id_producto}>{p.codigo} - {p.nombre}</option>
                            ))}
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Modelo IA</label>
                        <select value={modeloSeleccionado} onChange={(e) => setModeloSeleccionado(e.target.value)}>
                            <option value="">Seleccionar modelo...</option>
                            {modelos.map(m => (
                                <option key={m.id_modelo} value={m.id_modelo}>
                                    {m.algoritmo} (R²: {m.r2?.toFixed(3) || 'N/A'})
                                    {m.estado === 'ACTIVO' ? ' - ACTIVO' : ''}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                <div className="grid-2" style={{ gap: '16px', marginTop: '16px' }}>
                    <div className="form-group">
                        <label>Horizonte de Predicción</label>
                        <select value={horizonte} onChange={(e) => setHorizonte(e.target.value)}>
                            <option value="7">7 días</option>
                            <option value="14">14 días</option>
                            <option value="30">30 días</option>
                            <option value="60">60 días</option>
                        </select>
                    </div>
                    <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end' }}>
                        <button
                            className="btn btn-primary"
                            onClick={handleGenerar}
                            disabled={generating || !modeloSeleccionado || !selectedProduct}
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

            {selectedProduct && selectedProduct !== 'all' && (
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Gráfico de Predicción</h3>
                        {loadingHistorial && <span style={{ fontSize: '0.8rem', color: 'var(--gray-500)' }}>Cargando historial...</span>}
                    </div>
                    {historialVentas.length === 0 && prediccionesProducto.length === 0 ? (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '300px', color: 'var(--gray-500)' }}>
                            <p>No hay datos disponibles para graficar. Genere una predicción primero.</p>
                        </div>
                    ) : (
                        <div style={{ height: '350px', padding: '16px' }}>
                            <Line data={prepareChartData()} options={chartOptions} />
                        </div>
                    )}
                </div>
            )}

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Historial de Predicciones</h3>
                    <ExportButtons
                        data={(selectedProduct && selectedProduct !== 'all' ? prediccionesProducto : predicciones).slice(0, 50).map(pred => {
                            const prod = getProducto(pred.id_producto);
                            return {
                                id_prediccion: `#${pred.id_prediccion}`,
                                producto: prod ? `${prod.codigo} - ${prod.nombre}` : `#${pred.id_producto}`,
                                periodo: pred.periodo || '-',
                                confianza_min: pred.confianza_min || '-',
                                demanda_estimada: pred.demanda_estimada,
                                confianza_max: pred.confianza_max || '-',
                                horizonte_dias: `${pred.horizonte_dias || '-'} días`,
                                fecha_prediccion: pred.fecha_prediccion || '-',
                            };
                        })}
                        columns={[
                            { key: 'id_prediccion', label: 'ID' },
                            { key: 'producto', label: 'Producto' },
                            { key: 'periodo', label: 'Periodo' },
                            { key: 'confianza_min', label: 'Demanda Min' },
                            { key: 'demanda_estimada', label: 'Demanda Estimada' },
                            { key: 'confianza_max', label: 'Demanda Max' },
                            { key: 'horizonte_dias', label: 'Horizonte' },
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
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Producto</th>
                                    <th>Periodo</th>
                                    <th>Demanda Min</th>
                                    <th>Demanda Estimada</th>
                                    <th>Demanda Max</th>
                                    <th>Horizonte</th>
                                    <th>Fecha</th>
                                </tr>
                            </thead>
                            <tbody>
                                {(selectedProduct && selectedProduct !== 'all' ? prediccionesProducto : predicciones).slice(0, 50).map(pred => {
                                    const prod = getProducto(pred.id_producto);
                                    return (
                                        <tr key={pred.id_prediccion}>
                                            <td>#{pred.id_prediccion}</td>
                                            <td>{prod ? `${prod.codigo} - ${prod.nombre}` : `#${pred.id_producto}`}</td>
                                            <td>{pred.periodo || '-'}</td>
                                            <td style={{ color: 'var(--warning)' }}>{pred.confianza_min || '-'}</td>
                                            <td><strong style={{ color: 'var(--primary)' }}>{pred.demanda_estimada}</strong></td>
                                            <td style={{ color: 'var(--success)' }}>{pred.confianza_max || '-'}</td>
                                            <td>{pred.horizonte_dias || '-'} días</td>
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
                                    <tr key={modelo.id_modelo} style={{ backgroundColor: modeloSeleccionado == modelo.id_modelo ? 'var(--primary-light)' : 'transparent' }}>
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
