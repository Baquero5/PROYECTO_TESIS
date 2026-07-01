import { useState, useEffect } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';
import { exportToCSV, exportToExcel, exportToPDF } from '../services/exportService';

export default function Reportes() {
    const [loading, setLoading] = useState(true);
    const [toast, setToast] = useState(null);
    const [datos, setDatos] = useState({
        productos: [],
        categorias: [],
        proveedores: [],
        inventario: [],
        ventas: [],
        alertas: [],
        predicciones: [],
    });

    useEffect(() => {
        loadAllData();
    }, []);

    const loadAllData = async () => {
        try {
            const [prodRes, catRes, provRes, invRes, ventRes, alertRes, predRes] = await Promise.allSettled([
                api.get('/products?limit=2000'),
                api.get('/categorias'),
                api.get('/proveedores'),
                api.get('/inventario'),
                api.get('/ventas'),
                api.get('/alertas'),
                api.get('/predicciones'),
            ]);

            if (prodRes.status === 'fulfilled') setDatos(prev => ({ ...prev, productos: prodRes.value.data }));
            if (catRes.status === 'fulfilled') setDatos(prev => ({ ...prev, categorias: catRes.value.data }));
            if (provRes.status === 'fulfilled') setDatos(prev => ({ ...prev, proveedores: provRes.value.data }));
            if (invRes.status === 'fulfilled') setDatos(prev => ({ ...prev, inventario: invRes.value.data }));
            if (ventRes.status === 'fulfilled') setDatos(prev => ({ ...prev, ventas: ventRes.value.data }));
            if (alertRes.status === 'fulfilled') setDatos(prev => ({ ...prev, alertas: alertRes.value.data }));
            if (predRes.status === 'fulfilled') setDatos(prev => ({ ...prev, predicciones: predRes.value.data }));
        } catch (err) {
            setToast({ message: 'Error al cargar datos', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const modules = [
        {
            key: 'productos',
            title: 'Productos',
            icon: '📦',
            columns: [
                { key: 'codigo', label: 'Código' },
                { key: 'nombre', label: 'Nombre' },
                { key: 'precio_venta', label: 'Precio Venta' },
                { key: 'estado', label: 'Estado' },
            ],
            getExportData: (items) => items.map(p => ({
                codigo: p.codigo,
                nombre: p.nombre,
                precio_venta: `$${p.precio_venta}`,
                estado: p.estado,
            })),
        },
        {
            key: 'inventario',
            title: 'Inventario',
            icon: '📊',
            columns: [
                { key: 'codigo', label: 'Código' },
                { key: 'nombre', label: 'Producto' },
                { key: 'stock_actual', label: 'Stock Actual' },
                { key: 'stock_minimo', label: 'Stock Mínimo' },
                { key: 'stock_maximo', label: 'Stock Máximo' },
            ],
            getExportData: (items) => items.map(inv => {
                const prod = datos.productos.find(p => p.id_producto === inv.id_producto);
                return {
                    codigo: prod?.codigo || inv.id_producto,
                    nombre: prod?.nombre || '-',
                    stock_actual: inv.stock_actual,
                    stock_minimo: inv.stock_minimo,
                    stock_maximo: inv.stock_maximo,
                };
            }),
        },
        {
            key: 'ventas',
            title: 'Ventas',
            icon: '💰',
            columns: [
                { key: 'id_venta', label: 'ID Venta' },
                { key: 'fecha', label: 'Fecha' },
                { key: 'total', label: 'Total' },
            ],
            getExportData: (items) => items.map(v => ({
                id_venta: `#${v.id_venta}`,
                fecha: v.fecha_venta || '-',
                total: `$${v.total}`,
            })),
        },
        {
            key: 'alertas',
            title: 'Alertas',
            icon: '⚠️',
            columns: [
                { key: 'id_alerta', label: 'ID' },
                { key: 'tipo', label: 'Tipo' },
                { key: 'estado', label: 'Estado' },
                { key: 'fecha', label: 'Fecha' },
            ],
            getExportData: (items) => items.map(a => ({
                id_alerta: `#${a.id_alerta}`,
                tipo: a.tipo_alerta,
                estado: a.estado,
                fecha: a.fecha_alerta ? new Date(a.fecha_alerta).toLocaleDateString() : '-',
            })),
        },
        {
            key: 'predicciones',
            title: 'Predicciones',
            icon: '🔮',
            columns: [
                { key: 'id_prediccion', label: 'ID' },
                { key: 'id_producto', label: 'Producto ID' },
                { key: 'demanda_estimada', label: 'Demanda Estimada' },
                { key: 'horizonte', label: 'Horizonte' },
                { key: 'fecha', label: 'Fecha' },
            ],
            getExportData: (items) => items.map(p => ({
                id_prediccion: `#${p.id_prediccion}`,
                id_producto: p.id_producto,
                demanda_estimada: p.demanda_estimada,
                horizonte: `${p.horizonte_dias || '-'} días`,
                fecha: p.fecha_prediccion || '-',
            })),
        },
    ];

    const handleExportAll = (format) => {
        modules.forEach(mod => {
            const data = mod.getExportData(datos[mod.key] || []);
            if (data.length === 0) return;

            if (format === 'csv') exportToCSV(data, mod.columns, `reporte_${mod.key}`);
            if (format === 'excel') exportToExcel(data, mod.columns, `reporte_${mod.key}`, mod.title);
            if (format === 'pdf') exportToPDF(data, mod.columns, `reporte_${mod.key}`, `Reporte de ${mod.title}`);
        });
        setToast({ message: `Reportes exportados en formato ${format.toUpperCase()}`, type: 'success' });
    };

    if (loading) return <div className="content-area"><p>Cargando datos...</p></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Centro de Reportes</h3>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <button className="btn btn-outline" onClick={() => handleExportAll('csv')}>
                            📄 Exportar Todo CSV
                        </button>
                        <button className="btn btn-outline" onClick={() => handleExportAll('excel')}>
                            📊 Exportar Todo Excel
                        </button>
                        <button className="btn btn-outline" onClick={() => handleExportAll('pdf')}>
                            📕 Exportar Todo PDF
                        </button>
                    </div>
                </div>
                <p style={{ color: 'var(--gray-600)', fontSize: '0.9rem', marginBottom: '20px' }}>
                    Exporta reportes individuales de cada módulo o todos los datos de una vez.
                </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '16px' }}>
                {modules.map(mod => {
                    const data = mod.getExportData(datos[mod.key] || []);
                    return (
                        <div key={mod.key} className="card">
                            <div className="card-header">
                                <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <span>{mod.icon}</span> {mod.title}
                                </h3>
                            </div>
                            <div style={{ marginBottom: '16px' }}>
                                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>
                                    {data.length}
                                </div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--gray-500)' }}>
                                    registros disponibles
                                </div>
                            </div>
                            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                                <button
                                    className="btn btn-outline"
                                    style={{ fontSize: '0.75rem', padding: '6px 10px' }}
                                    onClick={() => {
                                        exportToCSV(data, mod.columns, `reporte_${mod.key}`);
                                        setToast({ message: `CSV de ${mod.title} exportado`, type: 'success' });
                                    }}
                                >
                                    CSV
                                </button>
                                <button
                                    className="btn btn-outline"
                                    style={{ fontSize: '0.75rem', padding: '6px 10px' }}
                                    onClick={() => {
                                        exportToExcel(data, mod.columns, `reporte_${mod.key}`, mod.title);
                                        setToast({ message: `Excel de ${mod.title} exportado`, type: 'success' });
                                    }}
                                >
                                    Excel
                                </button>
                                <button
                                    className="btn btn-outline"
                                    style={{ fontSize: '0.75rem', padding: '6px 10px' }}
                                    onClick={() => {
                                        exportToPDF(data, mod.columns, `reporte_${mod.key}`, `Reporte de ${mod.title}`);
                                        setToast({ message: `PDF de ${mod.title} exportado`, type: 'success' });
                                    }}
                                >
                                    PDF
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
