import { useState, useEffect, useRef, useCallback } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';
import ExportButtons from '../components/ExportButtons';

export default function Ventas() {
    const [ventas, setVentas] = useState([]);
    const [productos, setProductos] = useState([]);
    const [inventario, setInventario] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [search, setSearch] = useState('');
    const [visibleCount, setVisibleCount] = useState(25);
    const [loadingMore, setLoadingMore] = useState(false);
    const tableContainerRef = useRef(null);
    const [detalles, setDetalles] = useState([]);
    const [ventaDetalle, setVentaDetalle] = useState(null);
    const [showDetalle, setShowDetalle] = useState(false);
    const [loadingDetalle, setLoadingDetalle] = useState(false);
    const [errors, setErrors] = useState({});
    const [toast, setToast] = useState(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [ventasRes, prodRes, invRes] = await Promise.all([
                api.get('/ventas'),
                api.get('/products?limit=2000'),
                api.get('/inventario')
            ]);
            setVentas(ventasRes.data);
            setProductos(prodRes.data);
            setInventario(invRes.data);
        } catch (err) {
            setToast({ message: 'Error al cargar datos', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const addDetalle = () => {
        setDetalles([...detalles, { id_producto: '', cantidad: 1, precio_unitario: 0 }]);
    };

    const updateDetalle = (index, field, value) => {
        const newDetalles = [...detalles];
        newDetalles[index][field] = value;
        if (field === 'id_producto') {
            const prod = productos.find(p => p.id_producto === parseInt(value));
            if (prod) newDetalles[index].precio_unitario = prod.precio_venta;
        }
        setDetalles(newDetalles);
        setErrors({ ...errors, detalles: '' });
    };

    const removeDetalle = (index) => {
        setDetalles(detalles.filter((_, i) => i !== index));
    };

    const getStock = (productoId) => {
        const inv = inventario.find(i => i.id_producto === productoId);
        return inv ? inv.stock_actual : 0;
    };

    const validate = () => {
        const newErrors = {};

        if (detalles.length === 0) {
            newErrors.detalles = 'Agregue al menos un producto a la venta';
        }

        detalles.forEach((det, idx) => {
            if (!det.id_producto) {
                newErrors[`producto_${idx}`] = 'Seleccione un producto';
            }
            if (!det.cantidad || parseInt(det.cantidad) <= 0) {
                newErrors[`cantidad_${idx}`] = 'Ingrese una cantidad válida (mínimo 1)';
            }
            if (det.precio_unitario !== '' && parseFloat(det.precio_unitario) < 0) {
                newErrors[`precio_${idx}`] = 'El precio no puede ser negativo';
            }
            const stock = getStock(parseInt(det.id_producto));
            if (det.id_producto && parseInt(det.cantidad) > stock) {
                newErrors[`cantidad_${idx}`] = `Stock insuficiente (disponible: ${stock})`;
            }
        });

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validate()) {
            setToast({ message: 'Corrija los errores en los productos', type: 'warning' });
            return;
        }
        try {
            const user = JSON.parse(localStorage.getItem('user'));
            await api.post('/ventas', {
                id_usuario: user.id_usuario,
                detalles: detalles.map(d => ({
                    id_producto: parseInt(d.id_producto),
                    cantidad: parseInt(d.cantidad),
                    precio_unitario: parseFloat(d.precio_unitario)
                }))
            });
            setToast({ message: 'Venta registrada exitosamente', type: 'success' });
            setShowModal(false);
            setDetalles([]);
            setErrors({});
            loadData();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al crear venta', type: 'error' });
        }
    };

    const filtered = ventas.filter(v =>
        v.id_venta.toString().includes(search)
    );

    const sorted = [...filtered].sort((a, b) => b.id_venta - a.id_venta);

    const handleScroll = useCallback(() => {
        const container = tableContainerRef.current;
        if (!container || loadingMore) return;
        if (container.scrollTop + container.clientHeight >= container.scrollHeight - 50) {
            if (visibleCount < sorted.length) {
                setLoadingMore(true);
                setTimeout(() => {
                    setVisibleCount(prev => Math.min(prev + 25, sorted.length));
                    setLoadingMore(false);
                }, 300);
            }
        }
    }, [visibleCount, sorted.length, loadingMore]);

    useEffect(() => {
        const container = tableContainerRef.current;
        if (container) {
            container.addEventListener('scroll', handleScroll);
            return () => container.removeEventListener('scroll', handleScroll);
        }
    }, [handleScroll]);

    useEffect(() => {
        setVisibleCount(25);
    }, [search]);

    const visibleVentas = sorted.slice(0, visibleCount);

    const getProducto = (id) => productos.find(p => p.id_producto === id);

    const verDetalle = async (ventaId) => {
        setLoadingDetalle(true);
        try {
            const response = await api.get(`/ventas/${ventaId}`);
            setVentaDetalle(response.data);
            setShowDetalle(true);
        } catch (err) {
            setToast({ message: 'Error al cargar detalle', type: 'error' });
        } finally {
            setLoadingDetalle(false);
        }
    };

    const exportColumns = [
        { key: 'id_venta', label: 'ID Venta' },
        { key: 'fecha', label: 'Fecha' },
        { key: 'total', label: 'Total' },
        { key: 'items', label: 'Items' },
    ];

    const exportData = filtered.map(venta => ({
        id_venta: `#${venta.id_venta}`,
        fecha: venta.fecha_venta || '-',
        total: `$${venta.total}`,
        items: venta.detalles?.length || 0,
    }));

    if (loading) return <div className="content-area"><p>Cargando...</p></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Gestión de Ventas</h3>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <ExportButtons
                            data={exportData}
                            columns={exportColumns}
                            moduleName="ventas"
                        />
                        <button className="btn btn-primary" onClick={() => { setDetalles([]); setErrors({}); setShowModal(true); }}>
                            + Nueva Venta
                        </button>
                    </div>
                </div>

                <div style={{ marginBottom: '16px' }}>
                    <input
                        type="text"
                        placeholder="Buscar por ID de venta..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        style={{ padding: '10px 12px', border: '1px solid var(--gray-300)', borderRadius: '8px', width: '300px', fontSize: '0.85rem' }}
                    />
                </div>

                <div className="table-container" ref={tableContainerRef} style={{ maxHeight: '500px', overflow: 'auto' }}>
                    <table className="data-table">
                        <thead style={{ position: 'sticky', top: 0, zIndex: 1 }}>
                            <tr>
                                <th style={{ background: 'var(--gray-200)' }}>ID</th>
                                <th style={{ background: 'var(--gray-200)' }}>Fecha</th>
                                <th style={{ background: 'var(--gray-200)' }}>Total</th>
                                <th style={{ background: 'var(--gray-200)' }}>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {visibleVentas.length === 0 ? (
                                <tr><td colSpan="4" style={{ textAlign: 'center', padding: '20px' }}>No hay ventas</td></tr>
                            ) : visibleVentas.map(venta => (
                                <tr key={venta.id_venta}>
                                    <td><span className="badge badge-info">#{venta.id_venta}</span></td>
                                    <td>{venta.fecha_venta || '-'}</td>
                                    <td><strong>${venta.total}</strong></td>
                                    <td>
                                        <button className="btn btn-outline" onClick={() => verDetalle(venta.id_venta)}>Ver Detalle</button>
                                    </td>
                                </tr>
                            ))}
                            {loadingMore && (
                                <tr>
                                    <td colSpan="4" style={{ textAlign: 'center', padding: '12px', color: 'var(--gray-500)' }}>
                                        Cargando más ventas...
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>

                <div style={{ marginTop: '12px', fontSize: '0.8rem', color: 'var(--gray-500)' }}>
                    Mostrando {visibleVentas.length} de {sorted.length} venta(s)
                </div>
            </div>

            {showModal && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                    <div style={{ background: 'var(--gray-100)', borderRadius: '16px', padding: '32px', width: '100%', maxWidth: '900px', maxHeight: '90vh', overflow: 'auto', boxShadow: 'var(--shadow-lg)' }}>
                        <h3 style={{ marginBottom: '20px', fontSize: '1.2rem' }}>Nueva Venta</h3>

                        {errors.detalles && (
                            <div style={{ padding: '12px', background: '#fef2f2', border: '1px solid #fca5a5', borderRadius: '8px', color: '#991b1b', marginBottom: '16px', fontSize: '0.85rem' }}>
                                {errors.detalles}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} noValidate>
                            <div style={{ marginBottom: '16px' }}>
                                <button type="button" className="btn btn-outline" onClick={addDetalle}>+ Agregar Producto</button>
                            </div>

                            {detalles.length === 0 ? (
                                <p style={{ color: 'var(--gray-500)', textAlign: 'center', padding: '20px' }}>Agrega productos a la venta</p>
                            ) : (
                                <table className="data-table" style={{ marginBottom: '16px' }}>
                                    <thead>
                                        <tr>
                                            <th>Producto</th>
                                            <th>Stock</th>
                                            <th>Cantidad</th>
                                            <th>Precio</th>
                                            <th>Subtotal</th>
                                            <th></th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {detalles.map((det, idx) => {
                                            const stock = getStock(parseInt(det.id_producto));
                                            return (
                                                <tr key={idx}>
                                                    <td>
                                                        <select value={det.id_producto}
                                                            onChange={(e) => updateDetalle(idx, 'id_producto', e.target.value)}
                                                            style={{ padding: '8px', borderRadius: '6px', border: `1px solid ${errors[`producto_${idx}`] ? 'var(--danger)' : 'var(--gray-300)'}`, minWidth: '200px' }}>
                                                            <option value="">Seleccionar...</option>
                                                            {productos.map(p => (
                                                                <option key={p.id_producto} value={p.id_producto}>{p.codigo} - {p.nombre}</option>
                                                            ))}
                                                        </select>
                                                        {errors[`producto_${idx}`] && <div className="field-error">{errors[`producto_${idx}`]}</div>}
                                                    </td>
                                                    <td>{stock}</td>
                                                    <td>
                                                        <input type="number" className="qty-input" min="1" max={stock} value={det.cantidad}
                                                            onChange={(e) => updateDetalle(idx, 'cantidad', e.target.value)}
                                                            style={{ padding: '8px', borderRadius: '6px', border: `1px solid ${errors[`cantidad_${idx}`] ? 'var(--danger)' : 'var(--gray-300)'}`, width: '80px' }} />
                                                        {errors[`cantidad_${idx}`] && <div className="field-error">{errors[`cantidad_${idx}`]}</div>}
                                                    </td>
                                                    <td>
                                                        <input type="number" step="0.01" value={det.precio_unitario}
                                                            readOnly
                                                            style={{ padding: '8px', borderRadius: '6px', border: '1px solid var(--gray-300)', width: '100px', backgroundColor: 'var(--gray-50)', color: 'var(--gray-500)', cursor: 'not-allowed' }} />
                                                    </td>
                                                    <td><strong>${(det.cantidad * det.precio_unitario).toFixed(2)}</strong></td>
                                                    <td>
                                                        <button type="button" className="btn" style={{ background: 'var(--danger)', color: 'white', padding: '4px 8px' }} onClick={() => removeDetalle(idx)}>X</button>
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            )}

                            {detalles.length > 0 && (
                                <div style={{ textAlign: 'right', marginBottom: '16px', fontSize: '1.1rem' }}>
                                    <strong>Total: ${detalles.reduce((sum, d) => sum + (d.cantidad * d.precio_unitario), 0).toFixed(2)}</strong>
                                </div>
                            )}

                            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '20px' }}>
                                <button type="button" className="btn btn-outline" onClick={() => setShowModal(false)}>Cancelar</button>
                                <button type="submit" className="btn btn-primary" disabled={detalles.length === 0}>Crear Venta</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {showDetalle && ventaDetalle && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                    <div style={{ background: 'var(--gray-100)', borderRadius: '16px', padding: '32px', width: '100%', maxWidth: '600px', maxHeight: '90vh', overflow: 'auto', boxShadow: 'var(--shadow-lg)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                            <h3 style={{ fontSize: '1.2rem' }}>Detalle Venta #{ventaDetalle.id_venta}</h3>
                            <button onClick={() => setShowDetalle(false)} style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: 'var(--gray-500)' }}>&times;</button>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px', padding: '12px', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                            <div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--gray-500)' }}>Fecha</div>
                                <div style={{ fontWeight: 'bold' }}>{ventaDetalle.fecha_venta}</div>
                            </div>
                            <div>
                                <div style={{ fontSize: '0.8rem', color: 'var(--gray-500)' }}>Total</div>
                                <div style={{ fontWeight: 'bold', color: 'var(--success)', fontSize: '1.1rem' }}>${ventaDetalle.total?.toLocaleString('es-EC', { minimumFractionDigits: 2 })}</div>
                            </div>
                        </div>

                        <h4 style={{ fontSize: '0.95rem', marginBottom: '12px', color: 'var(--gray-700)' }}>Productos</h4>
                        <div style={{ maxHeight: '300px', overflow: 'auto' }}>
                            <table className="data-table">
                                <thead style={{ position: 'sticky', top: 0, zIndex: 1 }}>
                                    <tr>
                                        <th style={{ background: 'var(--gray-200)' }}>Producto</th>
                                        <th style={{ background: 'var(--gray-200)' }}>Cant.</th>
                                        <th style={{ background: 'var(--gray-200)' }}>Precio</th>
                                        <th style={{ background: 'var(--gray-200)' }}>Subtotal</th>
                                    </tr>
                                </thead>
                            <tbody>
                                {ventaDetalle.detalles?.length === 0 ? (
                                    <tr><td colSpan="4" style={{ textAlign: 'center', padding: '16px', color: 'var(--gray-500)' }}>Sin detalles</td></tr>
                                ) : ventaDetalle.detalles?.map(det => {
                                    const prod = getProducto(det.id_producto);
                                    return (
                                        <tr key={det.id_detalle}>
                                            <td>{prod ? `${prod.codigo} - ${prod.nombre}` : `#${det.id_producto}`}</td>
                                            <td>{det.cantidad}</td>
                                            <td>${det.precio_unitario?.toFixed(2)}</td>
                                            <td><strong>${det.subtotal?.toFixed(2)}</strong></td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
                            <button className="btn btn-outline" onClick={() => setShowDetalle(false)}>Cerrar</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
