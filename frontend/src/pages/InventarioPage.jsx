import { useState, useEffect } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';
import ExportButtons from '../components/ExportButtons';

export default function Inventario() {
    const [inventario, setInventario] = useState([]);
    const [productos, setProductos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [showMovimientoModal, setShowMovimientoModal] = useState(false);
    const [selectedProducto, setSelectedProducto] = useState(null);
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState('todos');
    const [formData, setFormData] = useState({
        id_producto: '', stock_actual: '', stock_minimo: '', stock_maximo: ''
    });
    const [movimientoData, setMovimientoData] = useState({
        cantidad: '', tipo: 'ENTRADA', observacion: ''
    });
    const [errors, setErrors] = useState({});
    const [toast, setToast] = useState(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [invRes, prodRes] = await Promise.all([
                api.get('/inventario'),
                api.get('/products?limit=2000')
            ]);
            setInventario(invRes.data);
            setProductos(prodRes.data);
        } catch (err) {
            setToast({ message: 'Error al cargar datos', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const validateInventario = () => {
        const newErrors = {};
        if (!formData.id_producto) {
            newErrors.id_producto = 'Seleccione un producto';
        }
        if (formData.stock_actual !== '' && parseInt(formData.stock_actual) < 0) {
            newErrors.stock_actual = 'No puede ser negativo';
        }
        if (formData.stock_minimo !== '' && parseInt(formData.stock_minimo) < 0) {
            newErrors.stock_minimo = 'No puede ser negativo';
        }
        if (formData.stock_maximo !== '' && parseInt(formData.stock_maximo) < 0) {
            newErrors.stock_maximo = 'No puede ser negativo';
        }
        if (formData.stock_maximo && formData.stock_minimo && parseInt(formData.stock_minimo) >= parseInt(formData.stock_maximo)) {
            newErrors.stock_minimo = 'Debe ser menor que el máximo';
        }
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const validateMovimiento = () => {
        const newErrors = {};
        if (!movimientoData.cantidad || parseInt(movimientoData.cantidad) <= 0) {
            newErrors.cantidad = 'Ingrese una cantidad válida (mínimo 1)';
        }
        if (movimientoData.tipo === 'SALIDA' && selectedProducto) {
            if (parseInt(movimientoData.cantidad) > selectedProducto.stock_actual) {
                newErrors.cantidad = `Stock insuficiente (disponible: ${selectedProducto.stock_actual})`;
            }
        }
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validateInventario()) {
            setToast({ message: 'Complete los campos correctamente', type: 'warning' });
            return;
        }
        try {
            const data = {
                id_producto: parseInt(formData.id_producto),
                stock_actual: parseInt(formData.stock_actual) || 0,
                stock_minimo: parseInt(formData.stock_minimo) || 0,
                stock_maximo: parseInt(formData.stock_maximo) || 0
            };
            await api.post('/inventario', data);
            setToast({ message: 'Registro de inventario creado', type: 'success' });
            setShowModal(false);
            setFormData({ id_producto: '', stock_actual: '', stock_minimo: '', stock_maximo: '' });
            setErrors({});
            loadData();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al guardar', type: 'error' });
        }
    };

    const handleMovimiento = async (e) => {
        e.preventDefault();
        if (!validateMovimiento()) {
            setToast({ message: 'Complete la cantidad correctamente', type: 'warning' });
            return;
        }
        try {
            await api.post(`/inventario/producto/${selectedProducto.id_producto}/movimiento`, {
                cantidad: parseInt(movimientoData.cantidad),
                tipo: movimientoData.tipo,
                observacion: movimientoData.observacion || null
            });
            setToast({ message: `${movimientoData.tipo} registrada exitosamente`, type: 'success' });
            setShowMovimientoModal(false);
            setMovimientoData({ cantidad: '', tipo: 'ENTRADA', observacion: '' });
            setSelectedProducto(null);
            setErrors({});
            loadData();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al registrar movimiento', type: 'error' });
        }
    };

    const openMovimiento = (inv, tipo) => {
        setSelectedProducto(inv);
        setMovimientoData({ cantidad: '', tipo, observacion: '' });
        setErrors({});
        setShowMovimientoModal(true);
    };

    const getProducto = (id) => productos.find(p => p.id_producto === id);

    const filtered = inventario.filter(inv => {
        const prod = getProducto(inv.id_producto);
        if (!prod) return false;
        const matchesSearch = prod.nombre.toLowerCase().includes(search.toLowerCase()) ||
                             prod.codigo.toLowerCase().includes(search.toLowerCase());
        if (filter === 'bajo') return matchesSearch && inv.stock_actual <= inv.stock_minimo;
        if (filter === 'normal') return matchesSearch && inv.stock_actual > inv.stock_minimo;
        return matchesSearch;
    });

    const getStockStatus = (inv) => {
        if (inv.stock_actual <= inv.stock_minimo) return { class: 'badge-danger', text: 'Bajo' };
        if (inv.stock_actual >= inv.stock_maximo * 0.8) return { class: 'badge-warning', text: 'Alto' };
        return { class: 'badge-success', text: 'Normal' };
    };

    const exportColumns = [
        { key: 'codigo', label: 'Código' },
        { key: 'nombre', label: 'Producto' },
        { key: 'stock_actual', label: 'Stock Actual' },
        { key: 'stock_minimo', label: 'Stock Mínimo' },
        { key: 'stock_maximo', label: 'Stock Máximo' },
        { key: 'estado', label: 'Estado' },
    ];

    const exportData = filtered.map(inv => {
        const prod = getProducto(inv.id_producto);
        const status = getStockStatus(inv);
        return {
            codigo: prod?.codigo || '',
            nombre: prod?.nombre || '',
            stock_actual: inv.stock_actual,
            stock_minimo: inv.stock_minimo,
            stock_maximo: inv.stock_maximo,
            estado: status.text,
        };
    });

    if (loading) return <div className="content-area"><p>Cargando...</p></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Gestión de Inventario</h3>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <ExportButtons
                            data={exportData}
                            columns={exportColumns}
                            moduleName="inventario"
                        />
                        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                            + Nuevo Registro
                        </button>
                    </div>
                </div>

                <div style={{ display: 'flex', gap: '12px', marginBottom: '16px', flexWrap: 'wrap' }}>
                    <input
                        type="text"
                        placeholder="Buscar producto..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        style={{ padding: '10px 12px', border: '1px solid var(--gray-300)', borderRadius: '8px', width: '300px', fontSize: '0.85rem' }}
                    />
                    <select
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        style={{ padding: '10px 12px', border: '1px solid var(--gray-300)', borderRadius: '8px', fontSize: '0.85rem' }}
                    >
                        <option value="todos">Todos</option>
                        <option value="bajo">Stock Bajo</option>
                        <option value="normal">Stock Normal</option>
                    </select>
                </div>

                <div className="table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Código</th>
                                <th>Producto</th>
                                <th>Stock Actual</th>
                                <th>Stock Mínimo</th>
                                <th>Stock Máximo</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.length === 0 ? (
                                <tr><td colSpan="7" style={{ textAlign: 'center', padding: '20px' }}>No hay registros</td></tr>
                            ) : filtered.map(inv => {
                                const prod = getProducto(inv.id_producto);
                                const status = getStockStatus(inv);
                                return (
                                    <tr key={inv.id_inventario}>
                                        <td><span className="badge badge-info">{prod?.codigo}</span></td>
                                        <td><strong>{prod?.nombre}</strong></td>
                                        <td style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{inv.stock_actual}</td>
                                        <td>{inv.stock_minimo}</td>
                                        <td>{inv.stock_maximo}</td>
                                        <td><span className={`badge ${status.class}`}>{status.text}</span></td>
                                        <td>
                                            <button className="btn" style={{ background: 'var(--success)', color: 'white', marginRight: '4px' }} onClick={() => openMovimiento(inv, 'ENTRADA')}>+ Entrada</button>
                                            <button className="btn" style={{ background: 'var(--warning)', color: 'white' }} onClick={() => openMovimiento(inv, 'SALIDA')}>- Salida</button>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>

                <div style={{ marginTop: '12px', fontSize: '0.8rem', color: 'var(--gray-500)' }}>
                    Total: {filtered.length} | Stock bajo: {inventario.filter(i => i.stock_actual <= i.stock_minimo).length}
                </div>
            </div>

            {showModal && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                    <div style={{ background: 'var(--gray-100)', borderRadius: '16px', padding: '32px', width: '100%', maxWidth: '480px', boxShadow: 'var(--shadow-lg)' }}>
                        <h3 style={{ marginBottom: '20px', fontSize: '1.2rem' }}>Nuevo Registro de Inventario</h3>
                        <form onSubmit={handleSubmit} noValidate>
                            <div className="form-group">
                                <label>Producto *</label>
                                <select value={formData.id_producto}
                                    onChange={(e) => { setFormData({ ...formData, id_producto: e.target.value }); setErrors({ ...errors, id_producto: '' }); }}
                                    className={errors.id_producto ? 'error' : ''}>
                                    <option value="">Seleccionar producto...</option>
                                    {productos.map(p => (
                                        <option key={p.id_producto} value={p.id_producto}>{p.codigo} - {p.nombre}</option>
                                    ))}
                                </select>
                                {errors.id_producto && <div className="field-error">{errors.id_producto}</div>}
                            </div>
                            <div className="grid-2">
                                <div className="form-group">
                                    <label>Stock Actual</label>
                                    <input type="number" min="0" value={formData.stock_actual}
                                        onChange={(e) => setFormData({ ...formData, stock_actual: e.target.value })}
                                        placeholder="0" />
                                </div>
                                <div className="form-group">
                                    <label>Stock Máximo</label>
                                    <input type="number" min="0" value={formData.stock_maximo}
                                        onChange={(e) => setFormData({ ...formData, stock_maximo: e.target.value })}
                                        placeholder="1000" />
                                </div>
                            </div>
                            <div className="form-group">
                                <label>Stock Mínimo</label>
                                <input type="number" min="0" value={formData.stock_minimo}
                                    onChange={(e) => { setFormData({ ...formData, stock_minimo: e.target.value }); setErrors({ ...errors, stock_minimo: '' }); }}
                                    placeholder="10"
                                    className={errors.stock_minimo ? 'error' : ''} />
                                {errors.stock_minimo && <div className="field-error">{errors.stock_minimo}</div>}
                            </div>
                            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '20px' }}>
                                <button type="button" className="btn btn-outline" onClick={() => setShowModal(false)}>Cancelar</button>
                                <button type="submit" className="btn btn-primary">Crear</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {showMovimientoModal && selectedProducto && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                    <div style={{ background: 'var(--gray-100)', borderRadius: '16px', padding: '32px', width: '100%', maxWidth: '420px', boxShadow: 'var(--shadow-lg)' }}>
                        <h3 style={{ marginBottom: '20px', fontSize: '1.2rem' }}>
                            {movimientoData.tipo === 'ENTRADA' ? 'Registrar Entrada' : 'Registrar Salida'}
                        </h3>
                        <p style={{ marginBottom: '16px', fontSize: '0.9rem', color: 'var(--gray-600)' }}>
                            Producto: <strong>{getProducto(selectedProducto.id_producto)?.nombre}</strong>
                            <br />Stock actual: <strong>{selectedProducto.stock_actual}</strong>
                        </p>
                        <form onSubmit={handleMovimiento} noValidate>
                            <div className="form-group">
                                <label>Cantidad *</label>
                                <input type="number" min="1" value={movimientoData.cantidad}
                                    onChange={(e) => { setMovimientoData({ ...movimientoData, cantidad: e.target.value }); setErrors({ ...errors, cantidad: '' }); }}
                                    placeholder="Cantidad"
                                    className={errors.cantidad ? 'error' : ''} />
                                {errors.cantidad && <div className="field-error">{errors.cantidad}</div>}
                            </div>
                            <div className="form-group">
                                <label>Observación</label>
                                <textarea value={movimientoData.observacion}
                                    onChange={(e) => setMovimientoData({ ...movimientoData, observacion: e.target.value })}
                                    rows="2" placeholder="Opcional..." />
                            </div>
                            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '20px' }}>
                                <button type="button" className="btn btn-outline" onClick={() => setShowMovimientoModal(false)}>Cancelar</button>
                                <button type="submit" className="btn btn-primary">Registrar</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
