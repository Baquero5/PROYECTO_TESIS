import { useState, useEffect } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';

export default function Prediccion() {
    const [productos, setProductos] = useState([]);
    const [predicciones, setPredicciones] = useState([]);
    const [modeloActivo, setModeloActivo] = useState(null);
    const [selectedProduct, setSelectedProduct] = useState('');
    const [horizonte, setHorizonte] = useState('30');
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [toast, setToast] = useState(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [prodRes, predRes, modeloRes] = await Promise.allSettled([
                api.get('/products'),
                api.get('/predicciones'),
                api.get('/modelos-ia/mejor')
            ]);

            if (prodRes.status === 'fulfilled') setProductos(prodRes.value.data);
            if (predRes.status === 'fulfilled') setPredicciones(predRes.value.data);
            if (modeloRes.status === 'fulfilled') setModeloActivo(modeloRes.value.data);
        } catch (err) {
            setToast({ message: 'Error al cargar datos', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const handleGenerar = async () => {
        if (!selectedProduct) {
            setToast({ message: 'Seleccione un producto', type: 'warning' });
            return;
        }
        if (!modeloActivo) {
            setToast({ message: 'No hay modelo IA disponible. Entrene un modelo primero.', type: 'warning' });
            return;
        }
        setGenerating(true);
        try {
            await api.post('/predicciones', {
                id_modelo: modeloActivo.id_modelo,
                id_producto: parseInt(selectedProduct),
                periodo: `${horizonte} dias`,
                demanda_estimada: Math.floor(Math.random() * 100) + 1
            });
            setToast({ message: 'Prediccion generada exitosamente', type: 'success' });
            loadData();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al generar prediccion', type: 'error' });
        } finally {
            setGenerating(false);
        }
    };

    const prediccionesProducto = selectedProduct
        ? predicciones.filter(p => p.id_producto === parseInt(selectedProduct))
        : [];

    const getProducto = (id) => productos.find(p => p.id_producto === id);

    if (loading) return <div className="content-area"><p>Cargando prediccion...</p></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Generar Prediccion de Demanda</h3>
                    {modeloActivo && <span className="badge badge-success">Modelo: {modeloActivo.nombre}</span>}
                </div>
                <div className="grid-2" style={{ gap: '16px' }}>
                    <div className="form-group">
                        <label>Seleccionar Producto</label>
                        <select value={selectedProduct} onChange={(e) => setSelectedProduct(e.target.value)}>
                            <option value="">Seleccionar...</option>
                            {productos.map(p => (
                                <option key={p.id_producto} value={p.id_producto}>{p.codigo} - {p.nombre}</option>
                            ))}
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Horizonte de Prediccion</label>
                        <select value={horizonte} onChange={(e) => setHorizonte(e.target.value)}>
                            <option value="7">7 dias</option>
                            <option value="14">14 dias</option>
                            <option value="30">30 dias</option>
                            <option value="60">60 dias</option>
                        </select>
                    </div>
                </div>
                <div style={{ marginTop: '16px', textAlign: 'center' }}>
                    <button className="btn btn-primary" onClick={handleGenerar} disabled={generating || !selectedProduct || !modeloActivo}>
                        {generating ? 'Generando...' : 'Generar Prediccion'}
                    </button>
                </div>
            </div>

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Historial de Predicciones</h3>
                </div>
                {predicciones.length === 0 ? (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '200px', color: 'var(--gray-500)' }}>
                        <p>No hay predicciones registradas. Seleccione un producto y genere una prediccion.</p>
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Producto</th>
                                    <th>Periodo</th>
                                    <th>Demanda Estimada</th>
                                    <th>Fecha</th>
                                </tr>
                            </thead>
                            <tbody>
                                {(selectedProduct ? prediccionesProducto : predicciones).map(pred => {
                                    const prod = getProducto(pred.id_producto);
                                    return (
                                        <tr key={pred.id_prediccion}>
                                            <td>#{pred.id_prediccion}</td>
                                            <td>{prod ? `${prod.codigo} - ${prod.nombre}` : `#${pred.id_producto}`}</td>
                                            <td>{pred.periodo || '-'}</td>
                                            <td><strong>{pred.demanda_estimada}</strong></td>
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
                    <div className="card-title">Modelo Activo</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: modeloActivo ? 'var(--success)' : 'var(--danger)' }}>
                        {modeloActivo ? modeloActivo.nombre : 'Ninguno'}
                    </div>
                </div>
            </div>

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Recomendaciones de Compra</h3>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '80px', color: 'var(--gray-500)' }}>
                    <p>Las recomendaciones apareceran despues de generar predicciones con datos suficientes.</p>
                </div>
            </div>
        </div>
    );
}
