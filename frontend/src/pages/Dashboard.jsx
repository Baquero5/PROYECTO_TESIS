import { useState, useEffect, useMemo } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    PointElement,
    LineElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
    Filler,
} from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale, LinearScale, BarElement, PointElement,
    LineElement, ArcElement, Title, Tooltip, Legend, Filler
);

const MONTHS_ES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

export default function Dashboard() {
    const [loading, setLoading] = useState(true);
    const [toast, setToast] = useState(null);
    const [stats, setStats] = useState({ total_products: 0, total_inventory_value: 0 });
    const [productos, setProductos] = useState([]);
    const [categorias, setCategorias] = useState([]);
    const [subcategorias, setSubcategorias] = useState([]);
    const [inventario, setInventario] = useState([]);
    const [ventas, setVentas] = useState([]);
    const [alertas, setAlertas] = useState([]);
    const [predicciones, setPredicciones] = useState([]);
    const [modelos, setModelos] = useState([]);

    useEffect(() => {
        loadAll();
    }, []);

    const loadAll = async () => {
        const results = await Promise.allSettled([
            api.get('/products/stats/summary'),
            api.get('/products?limit=2000'),
            api.get('/categorias'),
            api.get('/subcategorias'),
            api.get('/inventario'),
            api.get('/ventas'),
            api.get('/alertas/activas'),
            api.get('/predicciones'),
            api.get('/modelos-ia'),
        ]);

        const [s, p, c, sub, i, v, a, pr, m] = results;
        if (s.status === 'fulfilled') setStats(s.value.data);
        if (p.status === 'fulfilled') setProductos(p.value.data);
        if (c.status === 'fulfilled') setCategorias(c.value.data);
        if (sub.status === 'fulfilled') setSubcategorias(sub.value.data);
        if (i.status === 'fulfilled') setInventario(i.value.data);
        if (v.status === 'fulfilled') setVentas(v.value.data);
        if (a.status === 'fulfilled') setAlertas(a.value.data);
        if (pr.status === 'fulfilled') setPredicciones(pr.value.data);
        if (m.status === 'fulfilled') setModelos(m.value.data);

        setLoading(false);
    };

    const getProducto = (id) => productos.find(p => p.id_producto === id);
    const getCategoria = (id) => categorias.find(c => c.id_categoria === id);
    const getSubcategoria = (id) => subcategorias.find(s => s.id_subcategoria === id);

    const stockCritico = inventario.filter(i => i.stock_actual <= i.stock_minimo).length;
    const ventasTotales = ventas.reduce((sum, v) => sum + parseFloat(v.total || 0), 0);

    const ventasPorMes = useMemo(() => {
        const map = {};
        ventas.forEach(v => {
            const d = new Date(v.fecha_venta);
            const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
            map[key] = (map[key] || 0) + parseFloat(v.total || 0);
        });
        const keys = Object.keys(map).sort().slice(-6);
        return {
            labels: keys.map(k => {
                const [y, m] = k.split('-');
                return `${MONTHS_ES[parseInt(m) - 1]} ${y.slice(2)}`;
            }),
            datasets: [{
                label: 'Ventas ($)',
                data: keys.map(k => map[k]),
                backgroundColor: 'rgba(59, 130, 246, 0.7)',
                borderColor: '#3b82f6',
                borderWidth: 1,
                borderRadius: 6,
            }],
        };
    }, [ventas]);

    const productosPorSubcategoria = useMemo(() => {
        const counts = {};
        productos.forEach(p => {
            const sub = getSubcategoria(p.id_subcategoria);
            const name = sub?.nombre || 'Sin subcategoría';
            counts[name] = (counts[name] || 0) + 1;
        });
        const labels = Object.keys(counts);
        const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];
        return {
            labels,
            datasets: [{
                data: labels.map(l => counts[l]),
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 0,
            }],
        };
    }, [productos, subcategorias]);

    const topDemandados = useMemo(() => {
        const demand = {};
        predicciones.forEach(p => {
            demand[p.id_producto] = (demand[p.id_producto] || 0) + parseFloat(p.demanda_estimada || 0);
        });
        const sorted = Object.entries(demand)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 10);
        return {
            labels: sorted.map(([id]) => {
                const prod = getProducto(parseInt(id));
                const name = prod?.nombre || `#${id}`;
                return name.length > 18 ? name.slice(0, 16) + '...' : name;
            }),
            datasets: [{
                label: 'Demanda Total',
                data: sorted.map(([, v]) => v),
                backgroundColor: 'rgba(139, 92, 246, 0.7)',
                borderColor: '#8b5cf6',
                borderWidth: 1,
                borderRadius: 4,
            }],
        };
    }, [predicciones, productos]);

    const inventarioEstado = useMemo(() => {
        let critico = 0, bajo = 0, normal = 0;
        inventario.forEach(inv => {
            if (inv.stock_actual <= inv.stock_minimo) critico++;
            else if (inv.stock_actual <= inv.stock_minimo * 1.5) bajo++;
            else normal++;
        });
        return {
            labels: ['Normal', 'Bajo', 'Crítico'],
            datasets: [{
                data: [normal, bajo, critico],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 0,
            }],
        };
    }, [inventario]);

    const tendenciaPredicciones = useMemo(() => {
        const sorted = [...predicciones]
            .sort((a, b) => new Date(a.fecha_prediccion) - new Date(b.fecha_prediccion))
            .slice(-20);
        return {
            labels: sorted.map((p, i) => `P${i + 1}`),
            datasets: [
                {
                    label: 'Demanda Estimada',
                    data: sorted.map(p => p.demanda_estimada),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4,
                },
                {
                    label: 'Confianza Max',
                    data: sorted.map(p => p.confianza_max),
                    borderColor: '#10b981',
                    borderDash: [5, 5],
                    tension: 0.4,
                    pointRadius: 0,
                },
                {
                    label: 'Confianza Min',
                    data: sorted.map(p => p.confianza_min),
                    borderColor: '#ef4444',
                    borderDash: [5, 5],
                    tension: 0.4,
                    pointRadius: 0,
                },
            ],
        };
    }, [predicciones]);

    const modelosMetrics = useMemo(() => {
        if (modelos.length === 0) return null;
        return {
            labels: modelos.map(m => m.algoritmo),
            datasets: [
                {
                    label: 'MAE',
                    data: modelos.map(m => m.mae),
                    backgroundColor: 'rgba(59, 130, 246, 0.7)',
                    borderRadius: 4,
                },
                {
                    label: 'RMSE',
                    data: modelos.map(m => m.rmse),
                    backgroundColor: 'rgba(239, 68, 68, 0.7)',
                    borderRadius: 4,
                },
                {
                    label: 'R² (x100)',
                    data: modelos.map(m => (m.r2 || 0) * 100),
                    backgroundColor: 'rgba(16, 185, 129, 0.7)',
                    borderRadius: 4,
                },
            ],
        };
    }, [modelos]);

    if (loading) return <div className="content-area"><p>Cargando dashboard...</p></div>;

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
    };

    const chartOptionsLegend = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } },
    };

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="grid-4" style={{ marginBottom: '24px' }}>
                <div className="kpi-card">
                    <div className="kpi-label">Total Productos</div>
                    <div className="kpi-value">{stats.total_products}</div>
                    <div className="kpi-change">Registrados en el sistema</div>
                </div>
                <div className="kpi-card" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' }}>
                    <div className="kpi-label">Ventas Totales</div>
                    <div className="kpi-value">${ventasTotales.toLocaleString()}</div>
                    <div className="kpi-change">{ventas.length} venta(s) registrada(s)</div>
                </div>
                <div className="kpi-card" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
                    <div className="kpi-label">Stock Crítico</div>
                    <div className="kpi-value">{stockCritico}</div>
                    <div className="kpi-change">{stockCritico > 0 ? 'Requiere atención' : 'Todo normal'}</div>
                </div>
                <div className="kpi-card" style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' }}>
                    <div className="kpi-label">Alertas Activas</div>
                    <div className="kpi-value">{alertas.length}</div>
                    <div className="kpi-change">{alertas.length > 0 ? 'Pendientes' : 'Sin alertas'}</div>
                </div>
            </div>

            <div className="grid-2">
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Ventas por Mes</h3>
                    </div>
                    <div style={{ height: '280px', padding: '8px' }}>
                        {ventas.length > 0 ? (
                            <Bar data={ventasPorMes} options={chartOptions} />
                        ) : (
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--gray-500)' }}>
                                <p>Sin datos de ventas</p>
                            </div>
                        )}
                    </div>
                </div>
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Productos por Subcategoría</h3>
                    </div>
                    <div style={{ height: '280px', padding: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {productos.length > 0 ? (
                            <div style={{ width: '240px', height: '240px' }}>
                                <Doughnut data={productosPorSubcategoria} options={chartOptionsLegend} />
                            </div>
                        ) : (
                            <p style={{ color: 'var(--gray-500)' }}>Sin datos</p>
                        )}
                    </div>
                </div>
            </div>

            <div className="grid-2">
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Top 10 Productos Más Demandados</h3>
                    </div>
                    <div style={{ height: '300px', padding: '8px' }}>
                        {predicciones.length > 0 ? (
                            <Bar data={topDemandados} options={{ ...chartOptions, indexAxis: 'y' }} />
                        ) : (
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--gray-500)' }}>
                                <p>Genere predicciones para ver datos</p>
                            </div>
                        )}
                    </div>
                </div>
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Estado del Inventario</h3>
                    </div>
                    <div style={{ height: '300px', padding: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {inventario.length > 0 ? (
                            <div style={{ width: '220px', height: '220px' }}>
                                <Doughnut data={inventarioEstado} options={chartOptionsLegend} />
                            </div>
                        ) : (
                            <p style={{ color: 'var(--gray-500)' }}>Sin datos</p>
                        )}
                    </div>
                </div>
            </div>

            <div className="grid-2">
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Tendencia de Predicciones</h3>
                    </div>
                    <div style={{ height: '280px', padding: '8px' }}>
                        {predicciones.length > 0 ? (
                            <Line data={tendenciaPredicciones} options={{
                                ...chartOptionsLegend,
                                plugins: { legend: { position: 'bottom' } },
                                scales: { x: { display: false } },
                            }} />
                        ) : (
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--gray-500)' }}>
                                <p>Sin predicciones disponibles</p>
                            </div>
                        )}
                    </div>
                </div>
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Rendimiento Modelos IA</h3>
                    </div>
                    <div style={{ height: '280px', padding: '8px' }}>
                        {modelos.length > 0 ? (
                            <Bar data={modelosMetrics} options={chartOptionsLegend} />
                        ) : (
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--gray-500)' }}>
                                <p>Sin modelos entrenados</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <div className="grid-2">
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Stock Crítico</h3>
                    </div>
                    {stockCritico === 0 ? (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '120px', color: 'var(--gray-500)' }}>
                            <p>Todos con stock suficiente</p>
                        </div>
                    ) : (
                        <div className="table-container" style={{ maxHeight: '250px', overflow: 'auto' }}>
                            <table className="data-table">
                                <thead><tr><th>Producto</th><th>Actual</th><th>Mínimo</th></tr></thead>
                                <tbody>
                                    {inventario.filter(i => i.stock_actual <= i.stock_minimo).slice(0, 8).map(inv => {
                                        const prod = getProducto(inv.id_producto);
                                        return (
                                            <tr key={inv.id_inventario}>
                                                <td><strong>{prod?.nombre || `#${inv.id_producto}`}</strong></td>
                                                <td style={{ color: 'var(--danger)', fontWeight: 'bold' }}>{inv.stock_actual}</td>
                                                <td>{inv.stock_minimo}</td>
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
                        <h3 className="card-title">Últimas Ventas</h3>
                    </div>
                    {ventas.length === 0 ? (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '120px', color: 'var(--gray-500)' }}>
                            <p>Sin ventas registradas</p>
                        </div>
                    ) : (
                        <div className="table-container" style={{ maxHeight: '250px', overflow: 'auto' }}>
                            <table className="data-table">
                                <thead><tr><th>ID</th><th>Fecha</th><th>Total</th></tr></thead>
                                <tbody>
                                    {ventas.slice(-8).reverse().map(v => (
                                        <tr key={v.id_venta}>
                                            <td><span className="badge badge-info">#{v.id_venta}</span></td>
                                            <td>{v.fecha_venta ? new Date(v.fecha_venta).toLocaleDateString() : '-'}</td>
                                            <td><strong>${parseFloat(v.total).toLocaleString()}</strong></td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
