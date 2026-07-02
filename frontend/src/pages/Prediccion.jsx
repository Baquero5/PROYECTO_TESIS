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
                id_modelo: parseInt(modeloSeleccionado)
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
                id_modelo: parseInt(modeloSeleccionado)
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
                            disabled={generating || !modeloSeleccionado || !selectedProduct || !fechaInicio || !fechaFin}
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
                        data={(selectedProduct && selectedProduct !== 'all' ? prediccionesProducto : predicciones).slice(0, 200).map(pred => {
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
                                {(selectedProduct && selectedProduct !== 'all' ? prediccionesProducto : predicciones).slice(0, 200).map(pred => {
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
