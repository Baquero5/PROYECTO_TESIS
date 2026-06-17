import { useState, useEffect } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';

export default function Dashboard() {
    const [stats, setStats] = useState({ total_products: 0, total_inventory_value: 0 });
    const [alertas, setAlertas] = useState([]);
    const [predicciones, setPredicciones] = useState([]);
    const [inventario, setInventario] = useState([]);
    const [loading, setLoading] = useState(true);
    const [toast, setToast] = useState(null);
    const [productos, setProductos] = useState([]);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            const [statsRes, alertasRes, predRes, invRes, prodRes] = await Promise.allSettled([
                api.get('/products/stats/summary'),
                api.get('/alertas/activas'),
                api.get('/predicciones'),
                api.get('/inventario'),
                api.get('/products')
            ]);

            if (statsRes.status === 'fulfilled') setStats(statsRes.value.data);
            if (alertasRes.status === 'fulfilled') setAlertas(alertasRes.value.data);
            if (predRes.status === 'fulfilled') setPredicciones(predRes.value.data);
            if (invRes.status === 'fulfilled') setInventario(invRes.value.data);
            if (prodRes.status === 'fulfilled') setProductos(prodRes.value.data);
        } catch (err) {
            setToast({ message: 'Error al cargar datos del dashboard', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const stockCritico = inventario.filter(i => i.stock_actual <= i.stock_minimo).length;
    const getProducto = (id) => productos.find(p => p.id_producto === id);

    if (loading) return <div className="content-area"><p>Cargando dashboard...</p></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="grid-4">
                <div className="kpi-card">
                    <div className="kpi-label">Total Productos</div>
                    <div className="kpi-value">{stats.total_products}</div>
                    <div className="kpi-change">Registrados en el sistema</div>
                </div>
                <div className="kpi-card" style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
                    <div className="kpi-label">Valor Inventario</div>
                    <div className="kpi-value">${stats.total_inventory_value}</div>
                    <div className="kpi-change">Valor total estimado</div>
                </div>
                <div className="kpi-card" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
                    <div className="kpi-label">Stock Critico</div>
                    <div className="kpi-value">{stockCritico}</div>
                    <div className="kpi-change">{stockCritico > 0 ? 'Requiere atencion' : 'Todo normal'}</div>
                </div>
                <div className="kpi-card" style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' }}>
                    <div className="kpi-label">Alertas Activas</div>
                    <div className="kpi-value">{alertas.length}</div>
                    <div className="kpi-change">{alertas.length > 0 ? 'Pendientes de revisar' : 'Sin alertas'}</div>
                </div>
            </div>

            <div className="grid-2">
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Predicciones Recientes</h3>
                    </div>
                    {predicciones.length === 0 ? (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '200px', color: 'var(--gray-500)' }}>
                            <p>Sin predicciones aun. Genere una prediccion para ver resultados.</p>
                        </div>
                    ) : (
                        <div className="table-container">
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Producto</th>
                                        <th>Periodo</th>
                                        <th>Demanda Estimada</th>
                                        <th>Fecha</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {predicciones.slice(0, 5).map(pred => {
                                        const prod = getProducto(pred.id_producto);
                                        return (
                                            <tr key={pred.id_prediccion}>
                                                <td><strong>{prod?.nombre || `#${pred.id_producto}`}</strong></td>
                                                <td>{pred.periodo || '-'}</td>
                                                <td><strong>{pred.demanda_estimada}</strong></td>
                                                <td>{pred.fecha_prediccion ? new Date(pred.fecha_prediccion).toLocaleDateString() : '-'}</td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Stock Critico</h3>
                    </div>
                    {stockCritico === 0 ? (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '200px', color: 'var(--gray-500)' }}>
                            <p>Todos los productos tienen stock suficiente.</p>
                        </div>
                    ) : (
                        <div className="table-container">
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Producto</th>
                                        <th>Stock Actual</th>
                                        <th>Stock Minimo</th>
                                        <th>Estado</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {inventario.filter(i => i.stock_actual <= i.stock_minimo).slice(0, 5).map(inv => {
                                        const prod = getProducto(inv.id_producto);
                                        return (
                                            <tr key={inv.id_inventario}>
                                                <td><strong>{prod?.nombre || `#${inv.id_producto}`}</strong></td>
                                                <td style={{ fontWeight: 'bold', color: 'var(--danger)' }}>{inv.stock_actual}</td>
                                                <td>{inv.stock_minimo}</td>
                                                <td><span className="badge badge-danger">Critico</span></td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Alertas Recientes</h3>
                </div>
                {alertas.length === 0 ? (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '80px', color: 'var(--gray-500)' }}>
                        <p>Sin alertas activas.</p>
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Tipo</th>
                                    <th>Producto</th>
                                    <th>Mensaje</th>
                                    <th>Estado</th>
                                    <th>Fecha</th>
                                </tr>
                            </thead>
                            <tbody>
                                {alertas.slice(0, 5).map(alerta => {
                                    const prod = getProducto(alerta.id_producto);
                                    return (
                                        <tr key={alerta.id_alerta}>
                                            <td><span className={`badge ${alerta.tipo_alerta === 'CRITICA' ? 'badge-danger' : 'badge-warning'}`}>{alerta.tipo_alerta}</span></td>
                                            <td>{prod?.nombre || `#${alerta.id_producto}`}</td>
                                            <td>{alerta.mensaje || '-'}</td>
                                            <td><span className={`badge ${alerta.estado === 'ACTIVA' ? 'badge-warning' : 'badge-success'}`}>{alerta.estado}</span></td>
                                            <td>{alerta.fecha_alerta ? new Date(alerta.fecha_alerta).toLocaleDateString() : '-'}</td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Resumen del Sistema</h3>
                </div>
                <div style={{ padding: '16px', color: 'var(--gray-600)', fontSize: '0.9rem' }}>
                    <p>Sistema operativo con {stats.total_products} productos registrados.</p>
                    {stockCritico > 0 && <p style={{ color: 'var(--danger)', fontWeight: 'bold' }}>{stockCritico} producto(s) con stock critico requieren reabastecimiento.</p>}
                    {alertas.length > 0 && <p style={{ color: 'var(--warning)' }}>{alertas.length} alerta(s) activa(s) pendientes de revision.</p>}
                </div>
            </div>
        </div>
    );
}
