import { useState, useEffect, useMemo, useRef } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';
import SparkLine from '../components/SparkLine';
import ChartExportButton from '../components/ChartExportButton';
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
import {
    barOptions,
    doughnutOptions,
    baseChartOptions,
    formatCurrency,
    formatNumber,
    CHART_COLORS,
    PALETTE,
} from '../config/chartConfig';

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
    const [inventario, setInventario] = useState([]);
    const [ventas, setVentas] = useState([]);
    const [alertas, setAlertas] = useState([]);
    const [predicciones, setPredicciones] = useState([]);
    const [modelos, setModelos] = useState([]);
    const [reabastecimientos, setReabastecimientos] = useState([]);

    const refVentasMes = useRef(null);
    const refTopDemandados = useRef(null);
    const refTendencia = useRef(null);
    const refModelos = useRef(null);
    const refCatDoughnut = useRef(null);
    const refInvDoughnut = useRef(null);

    useEffect(() => {
        loadAll();
    }, []);

    const loadAll = async () => {
        const results = await Promise.allSettled([
            api.get('/products/stats/summary'),
            api.get('/products?limit=2000'),
            api.get('/categorias'),
            api.get('/inventario'),
            api.get('/ventas'),
            api.get('/alertas/activas'),
            api.get('/predicciones'),
            api.get('/modelos-ia'),
            api.get('/reabastecimiento/pendientes'),
        ]);

        const [s, p, c, i, v, a, pr, m, r] = results;
        if (s.status === 'fulfilled') setStats(s.value.data);
        if (p.status === 'fulfilled') setProductos(p.value.data);
        if (c.status === 'fulfilled') setCategorias(c.value.data);
        if (i.status === 'fulfilled') setInventario(i.value.data);
        if (v.status === 'fulfilled') setVentas(v.value.data);
        if (a.status === 'fulfilled') setAlertas(a.value.data);
        if (pr.status === 'fulfilled') setPredicciones(pr.value.data);
        if (m.status === 'fulfilled') setModelos(m.value.data);
        if (r.status === 'fulfilled') setReabastecimientos(r.value.data);

        setLoading(false);
    };

    const getProducto = (id) => productos.find(p => p.id_producto === id);
    const getCategoria = (id) => categorias.find(c => c.id_categoria === id);

    const stockCritico = inventario.filter(i => i.stock_actual <= i.stock_minimo).length;
    const ventasTotales = ventas.reduce((sum, v) => sum + parseFloat(v.total || 0), 0);

    const sparkVentasMes = useMemo(() => {
        const map = {};
        ventas.forEach(v => {
            const d = new Date(v.fecha_venta);
            const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
            map[key] = (map[key] || 0) + parseFloat(v.total || 0);
        });
        return Object.keys(map).sort().slice(-8).map(k => map[k]);
    }, [ventas]);

    const sparkStockCritico = useMemo(() => {
        const vals = [];
        inventario.forEach(inv => {
            const ratio = inv.stock_minimo > 0 ? inv.stock_actual / inv.stock_minimo : 1;
            vals.push(ratio);
        });
        return vals.slice(-8);
    }, [inventario]);

    const sparkAlertas = useMemo(() => {
        const byMonth = {};
        alertas.forEach(a => {
            if (a.fecha_creacion) {
                const d = new Date(a.fecha_creacion);
                const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
                byMonth[key] = (byMonth[key] || 0) + 1;
            }
        });
        const keys = Object.keys(byMonth).sort().slice(-8);
        return keys.length > 0 ? keys.map(k => byMonth[k]) : [alertas.length];
    }, [alertas]);

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
                backgroundColor: CHART_COLORS.blue.bg,
                borderColor: CHART_COLORS.blue.main,
                borderWidth: 2,
                borderRadius: 8,
                hoverBackgroundColor: CHART_COLORS.blue.main,
            }],
        };
    }, [ventas]);

    const productosPorCategoria = useMemo(() => {
        const counts = {};
        productos.forEach(p => {
            const cat = getCategoria(p.id_categoria);
            const name = cat?.nombre || 'Sin categoría';
            counts[name] = (counts[name] || 0) + 1;
        });
        const labels = Object.keys(counts);
        return {
            labels,
            datasets: [{
                data: labels.map(l => counts[l]),
                backgroundColor: PALETTE.slice(0, labels.length),
                borderWidth: 0,
                hoverOffset: 8,
            }],
        };
    }, [productos, categorias]);

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
                backgroundColor: CHART_COLORS.purple.bg,
                borderColor: CHART_COLORS.purple.main,
                borderWidth: 2,
                borderRadius: 6,
                hoverBackgroundColor: CHART_COLORS.purple.main,
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
                backgroundColor: [CHART_COLORS.green.main, CHART_COLORS.yellow.main, CHART_COLORS.red.main],
                borderWidth: 0,
                hoverOffset: 6,
            }],
        };
    }, [inventario]);

    const tendenciaPredicciones = useMemo(() => {
        const sorted = [...predicciones]
            .sort((a, b) => new Date(a.fecha_prediccion) - new Date(b.fecha_prediccion))
            .slice(-20);
        return {
            labels: sorted.map(p => {
                const d = new Date(p.fecha_prediccion);
                return `${d.getDate()} ${MONTHS_ES[d.getMonth()]}`;
            }),
            datasets: [
                {
                    label: 'Demanda Estimada',
                    data: sorted.map(p => p.demanda_estimada),
                    borderColor: CHART_COLORS.blue.main,
                    backgroundColor: CHART_COLORS.blue.bg,
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2.5,
                    pointRadius: 3,
                    pointBackgroundColor: CHART_COLORS.blue.main,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointHoverRadius: 6,
                },
                {
                    label: 'Confianza Max',
                    data: sorted.map(p => p.confianza_max),
                    borderColor: CHART_COLORS.green.main,
                    borderDash: [6, 4],
                    tension: 0.4,
                    pointRadius: 0,
                    borderWidth: 1.5,
                    fill: false,
                },
                {
                    label: 'Confianza Min',
                    data: sorted.map(p => p.confianza_min),
                    borderColor: CHART_COLORS.red.main,
                    borderDash: [6, 4],
                    tension: 0.4,
                    pointRadius: 0,
                    borderWidth: 1.5,
                    fill: false,
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
                    backgroundColor: CHART_COLORS.blue.main,
                    borderRadius: 6,
                },
                {
                    label: 'RMSE',
                    data: modelos.map(m => m.rmse),
                    backgroundColor: CHART_COLORS.red.main,
                    borderRadius: 6,
                },
                {
                    label: 'R² (x100)',
                    data: modelos.map(m => (m.r2 || 0) * 100),
                    backgroundColor: CHART_COLORS.green.main,
                    borderRadius: 6,
                },
            ],
        };
    }, [modelos]);

    if (loading) return <div className="content-area"><div className="loading-container"><div className="loading-spinner"></div><p>Cargando dashboard...</p></div></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="grid-4 kpi-grid" style={{ marginBottom: '24px' }}>
                <div className="kpi-card kpi-animate" style={{ animationDelay: '0ms' }}>
                    <div className="kpi-header-row">
                        <div className="kpi-label">Total Productos</div>
                        <SparkLine data={sparkVentasMes.length > 0 ? sparkVentasMes : [0]} color="#ffffff" height={28} width={60} fillColor="rgba(255,255,255,0.2)" />
                    </div>
                    <div className="kpi-value">{formatNumber(stats.total_products)}</div>
                    <div className="kpi-change">Registrados en el sistema</div>
                </div>
                <div className="kpi-card kpi-animate" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)', animationDelay: '80ms' }}>
                    <div className="kpi-header-row">
                        <div className="kpi-label">Ventas Totales</div>
                        <SparkLine data={sparkVentasMes.length > 0 ? sparkVentasMes : [0]} color="#93c5fd" height={28} width={60} fillColor="rgba(147, 197, 253, 0.2)" />
                    </div>
                    <div className="kpi-value">{formatCurrency(ventasTotales)}</div>
                    <div className="kpi-change">{ventas.length} venta(s) registrada(s)</div>
                </div>
                <div className="kpi-card kpi-animate" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', animationDelay: '160ms' }}>
                    <div className="kpi-header-row">
                        <div className="kpi-label">Stock Crítico</div>
                        <SparkLine data={sparkStockCritico.length > 0 ? sparkStockCritico : [0]} color="#fde68a" height={28} width={60} fillColor="rgba(253, 230, 138, 0.2)" />
                    </div>
                    <div className="kpi-value">{stockCritico}</div>
                    <div className="kpi-change">{stockCritico > 0 ? 'Requiere atención' : 'Todo normal'}</div>
                </div>
                <div className="kpi-card kpi-animate" style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)', animationDelay: '240ms' }}>
                    <div className="kpi-header-row">
                        <div className="kpi-label">Alertas Activas</div>
                        <SparkLine data={sparkAlertas.length > 0 ? sparkAlertas : [0]} color="#c4b5fd" height={28} width={60} fillColor="rgba(196, 181, 253, 0.2)" />
                    </div>
                    <div className="kpi-value">{alertas.length}</div>
                    <div className="kpi-change">{alertas.length > 0 ? 'Pendientes' : 'Sin alertas'}</div>
                </div>
            </div>

            <div className="grid-3 kpi-grid" style={{ marginBottom: '24px' }}>
                <div className="kpi-card kpi-animate" style={{ background: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)', animationDelay: '320ms' }}>
                    <div className="kpi-header-row">
                        <div className="kpi-label">Reabastecimientos</div>
                    </div>
                    <div className="kpi-value">{reabastecimientos.length}</div>
                    <div className="kpi-change">Pendientes de compra</div>
                </div>
            </div>

            <div className="grid-2">
                <div className="card chart-card">
                    <div className="card-header">
                        <h3 className="card-title">Ventas por Mes</h3>
                        <ChartExportButton chartRef={refVentasMes} filename="ventas_por_mes" />
                    </div>
                    <div style={{ height: '300px', padding: '12px 8px' }}>
                        {ventas.length > 0 ? (
                            <Bar ref={refVentasMes} data={ventasPorMes} options={barOptions({ formatYAs: 'currency' })} />
                        ) : (
                            <div className="chart-empty">
                                <p>Sin datos de ventas</p>
                            </div>
                        )}
                    </div>
                </div>
                <div className="card chart-card">
                    <div className="card-header">
                        <h3 className="card-title">Productos por Categoría</h3>
                        <ChartExportButton chartRef={refCatDoughnut} filename="productos_categoria" />
                    </div>
                    <div style={{ height: '300px', padding: '12px 8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {productos.length > 0 ? (
                            <div style={{ width: '260px', height: '260px' }}>
                                <Doughnut ref={refCatDoughnut} data={productosPorCategoria} options={doughnutOptions()} />
                            </div>
                        ) : (
                            <p className="chart-empty-text">Sin datos</p>
                        )}
                    </div>
                </div>
            </div>

            <div className="grid-2">
                <div className="card chart-card">
                    <div className="card-header">
                        <h3 className="card-title">Top 10 Productos Más Demandados</h3>
                        <ChartExportButton chartRef={refTopDemandados} filename="top_demandados" />
                    </div>
                    <div style={{ height: '320px', padding: '12px 8px' }}>
                        {predicciones.length > 0 ? (
                            <Bar ref={refTopDemandados} data={topDemandados} options={barOptions({ isHorizontal: true, showLegend: false })} />
                        ) : (
                            <div className="chart-empty">
                                <p>Genere predicciones para ver datos</p>
                            </div>
                        )}
                    </div>
                </div>
                <div className="card chart-card">
                    <div className="card-header">
                        <h3 className="card-title">Estado del Inventario</h3>
                        <ChartExportButton chartRef={refInvDoughnut} filename="inventario_estado" />
                    </div>
                    <div style={{ height: '320px', padding: '12px 8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {inventario.length > 0 ? (
                            <div style={{ width: '240px', height: '240px' }}>
                                <Doughnut ref={refInvDoughnut} data={inventarioEstado} options={doughnutOptions()} />
                            </div>
                        ) : (
                            <p className="chart-empty-text">Sin datos</p>
                        )}
                    </div>
                </div>
            </div>

            <div className="grid-2">
                <div className="card chart-card">
                    <div className="card-header">
                        <h3 className="card-title">Tendencia de Predicciones</h3>
                        <ChartExportButton chartRef={refTendencia} filename="tendencia_predicciones" />
                    </div>
                    <div style={{ height: '300px', padding: '12px 8px' }}>
                        {predicciones.length > 0 ? (
                            <Line ref={refTendencia} data={tendenciaPredicciones} options={{
                                ...baseChartOptions({
                                    showLegend: true,
                                    legendPosition: 'bottom',
                                    yTitle: 'Demanda',
                                    xDisplay: false,
                                }),
                                plugins: {
                                    ...baseChartOptions({ showLegend: true, legendPosition: 'bottom', yTitle: 'Demanda', xDisplay: false }).plugins,
                                    tooltip: {
                                        ...baseChartOptions({ showLegend: true, legendPosition: 'bottom', yTitle: 'Demanda', xDisplay: false }).plugins.tooltip,
                                        callbacks: {
                                            title: (items) => items.length ? `📅 ${items[0].label}` : '',
                                            label: (context) => ` ${context.dataset.label}: ${formatNumber(context.parsed.y)} unidades`,
                                        },
                                    },
                                },
                            }} />
                        ) : (
                            <div className="chart-empty">
                                <p>Sin predicciones disponibles</p>
                            </div>
                        )}
                    </div>
                </div>
                <div className="card chart-card">
                    <div className="card-header">
                        <h3 className="card-title">Rendimiento Modelos IA</h3>
                        {modelos.length > 0 && <ChartExportButton chartRef={refModelos} filename="rendimiento_modelos" />}
                    </div>
                    <div style={{ height: '300px', padding: '12px 8px' }}>
                        {modelos.length > 0 ? (
                            <Bar ref={refModelos} data={modelosMetrics} options={barOptions({ showLegend: true, legendPosition: 'bottom' })} />
                        ) : (
                            <div className="chart-empty">
                                <p>Sin modelos entrenados</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <div className="grid-3">
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Stock Crítico</h3>
                        {stockCritico > 0 && <span className="badge badge-danger">{stockCritico} producto(s)</span>}
                    </div>
                    {stockCritico === 0 ? (
                        <div className="card-empty">
                            <span className="card-empty-icon">✅</span>
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
                        {ventas.length > 0 && <span className="badge badge-info">{ventas.length} venta(s)</span>}
                    </div>
                    {ventas.length === 0 ? (
                        <div className="card-empty">
                            <span className="card-empty-icon">📭</span>
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
                                            <td>{v.fecha_venta ? new Date(v.fecha_venta).toLocaleDateString('es-EC') : '-'}</td>
                                            <td><strong>{formatCurrency(parseFloat(v.total))}</strong></td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Reabastecimientos Pendientes</h3>
                        {reabastecimientos.length > 0 && <span className="badge badge-warning">{reabastecimientos.length}</span>}
                    </div>
                    {reabastecimientos.length === 0 ? (
                        <div className="card-empty">
                            <span className="card-empty-icon">📦</span>
                            <p>Sin reabastecimientos pendientes</p>
                        </div>
                    ) : (
                        <div className="table-container" style={{ maxHeight: '250px', overflow: 'auto' }}>
                            <table className="data-table">
                                <thead><tr><th>Producto</th><th>Cantidad</th><th>Estado</th></tr></thead>
                                <tbody>
                                    {reabastecimientos.slice(0, 8).map(r => {
                                        const prod = getProducto(r.id_producto);
                                        return (
                                            <tr key={r.id_reabastecimiento}>
                                                <td><strong>{prod?.nombre || `#${r.id_producto}`}</strong></td>
                                                <td>{r.cantidad_sugerida}</td>
                                                <td><span className="badge badge-warning">{r.estado}</span></td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
