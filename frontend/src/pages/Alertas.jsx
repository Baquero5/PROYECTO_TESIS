import { useState, useEffect } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';

export default function Alertas() {
    const [alertas, setAlertas] = useState([]);
    const [productos, setProductos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState('todas');
    const [formData, setFormData] = useState({
        id_producto: '', tipo_alerta: 'PREVENTIVA', mensaje: ''
    });
    const [editData, setEditData] = useState({ estado: '', mensaje: '' });
    const [errors, setErrors] = useState({});
    const [toast, setToast] = useState(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [alertasRes, prodRes] = await Promise.all([
                api.get('/alertas'),
                api.get('/products')
            ]);
            setAlertas(alertasRes.data);
            setProductos(prodRes.data);
        } catch (err) {
            setToast({ message: 'Error al cargar datos', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const validate = () => {
        const newErrors = {};
        if (!formData.id_producto) {
            newErrors.id_producto = 'Seleccione un producto';
        }
        if (!formData.tipo_alerta) {
            newErrors.tipo_alerta = 'Seleccione un tipo de alerta';
        }
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validate()) {
            setToast({ message: 'Complete los campos correctamente', type: 'warning' });
            return;
        }
        try {
            const data = {
                id_producto: parseInt(formData.id_producto),
                tipo_alerta: formData.tipo_alerta,
                mensaje: formData.mensaje || null
            };
            await api.post('/alertas', data);
            setToast({ message: 'Alerta creada exitosamente', type: 'success' });
            setShowModal(false);
            setFormData({ id_producto: '', tipo_alerta: 'PREVENTIVA', mensaje: '' });
            setErrors({});
            loadData();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al crear alerta', type: 'error' });
        }
    };

    const handleEdit = (alerta) => {
        setEditingId(alerta.id_alerta);
        setEditData({ estado: alerta.estado, mensaje: alerta.mensaje || '' });
        setErrors({});
        setShowModal(true);
    };

    const handleUpdate = async (e) => {
        e.preventDefault();
        try {
            await api.put(`/alertas/${editingId}`, {
                estado: editData.estado,
                mensaje: editData.mensaje || null
            });
            setToast({ message: 'Alerta actualizada exitosamente', type: 'success' });
            setShowModal(false);
            setEditingId(null);
            setEditData({ estado: '', mensaje: '' });
            loadData();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al actualizar', type: 'error' });
        }
    };

    const handleResolver = async (id) => {
        try {
            await api.put(`/alertas/${id}`, { estado: 'RESUELTA' });
            setToast({ message: 'Alerta marcada como resuelta', type: 'success' });
            loadData();
        } catch (err) {
            setToast({ message: 'Error al resolver alerta', type: 'error' });
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('¿Estás seguro de eliminar esta alerta?')) return;
        try {
            await api.delete(`/alertas/${id}`);
            setToast({ message: 'Alerta eliminada', type: 'success' });
            loadData();
        } catch (err) {
            setToast({ message: 'Error al eliminar', type: 'error' });
        }
    };

    const openCreateModal = () => {
        setEditingId(null);
        setFormData({ id_producto: '', tipo_alerta: 'PREVENTIVA', mensaje: '' });
        setErrors({});
        setShowModal(true);
    };

    const getProducto = (id) => productos.find(p => p.id_producto === id);

    const filtered = alertas.filter(a => {
        const prod = getProducto(a.id_producto);
        const nombre = prod?.nombre || '';
        const matchesSearch = nombre.toLowerCase().includes(search.toLowerCase()) ||
                              (a.mensaje && a.mensaje.toLowerCase().includes(search.toLowerCase()));
        if (filter === 'activas') return matchesSearch && a.estado === 'ACTIVA';
        if (filter === 'criticas') return matchesSearch && a.tipo_alerta === 'CRITICA';
        if (filter === 'preventivas') return matchesSearch && a.tipo_alerta === 'PREVENTIVA';
        if (filter === 'resueltas') return matchesSearch && a.estado === 'RESUELTA';
        return matchesSearch;
    });

    const criticas = alertas.filter(a => a.tipo_alerta === 'CRITICA' && a.estado === 'ACTIVA');
    const preventivas = alertas.filter(a => a.tipo_alerta === 'PREVENTIVA' && a.estado === 'ACTIVA');

    if (loading) return <div className="content-area"><p>Cargando...</p></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="grid-2">
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Alertas Criticas</h3>
                        <span className="badge badge-danger">{criticas.length}</span>
                    </div>
                    {criticas.length === 0 ? (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100px', color: 'var(--gray-500)' }}>
                            <p>Sin alertas criticas activas.</p>
                        </div>
                    ) : (
                        <div className="table-container">
                            <table className="data-table">
                                <thead>
                                    <tr><th>Producto</th><th>Mensaje</th><th>Fecha</th><th>Accion</th></tr>
                                </thead>
                                <tbody>
                                    {criticas.map(a => {
                                        const prod = getProducto(a.id_producto);
                                        return (
                                            <tr key={a.id_alerta}>
                                                <td>{prod?.nombre || `#${a.id_producto}`}</td>
                                                <td>{a.mensaje || a.tipo_alerta}</td>
                                                <td>{a.fecha_alerta ? new Date(a.fecha_alerta).toLocaleDateString() : '-'}</td>
                                                <td><button className="btn" style={{ background: 'var(--success)', color: 'white', padding: '4px 8px', fontSize: '0.8rem' }} onClick={() => handleResolver(a.id_alerta)}>Resolver</button></td>
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
                        <h3 className="card-title">Alertas Preventivas</h3>
                        <span className="badge badge-warning">{preventivas.length}</span>
                    </div>
                    {preventivas.length === 0 ? (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100px', color: 'var(--gray-500)' }}>
                            <p>Sin alertas preventivas activas.</p>
                        </div>
                    ) : (
                        <div className="table-container">
                            <table className="data-table">
                                <thead>
                                    <tr><th>Producto</th><th>Mensaje</th><th>Fecha</th><th>Accion</th></tr>
                                </thead>
                                <tbody>
                                    {preventivas.map(a => {
                                        const prod = getProducto(a.id_producto);
                                        return (
                                            <tr key={a.id_alerta}>
                                                <td>{prod?.nombre || `#${a.id_producto}`}</td>
                                                <td>{a.mensaje || a.tipo_alerta}</td>
                                                <td>{a.fecha_alerta ? new Date(a.fecha_alerta).toLocaleDateString() : '-'}</td>
                                                <td><button className="btn" style={{ background: 'var(--success)', color: 'white', padding: '4px 8px', fontSize: '0.8rem' }} onClick={() => handleResolver(a.id_alerta)}>Resolver</button></td>
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
                    <h3 className="card-title">Gestion de Alertas</h3>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <input
                            type="text"
                            placeholder="Buscar alerta..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            style={{ padding: '10px 12px', border: '1px solid var(--gray-300)', borderRadius: '8px', fontSize: '0.85rem', width: '200px' }}
                        />
                        <select
                            value={filter}
                            onChange={(e) => setFilter(e.target.value)}
                            style={{ padding: '10px 12px', border: '1px solid var(--gray-300)', borderRadius: '8px', fontSize: '0.85rem' }}
                        >
                            <option value="todas">Todas</option>
                            <option value="activas">Solo Activas</option>
                            <option value="criticas">Solo Criticas</option>
                            <option value="preventivas">Solo Preventivas</option>
                            <option value="resueltas">Resueltas</option>
                        </select>
                        <button className="btn btn-primary" onClick={openCreateModal}>
                            + Nueva Alerta
                        </button>
                    </div>
                </div>
                {filtered.length === 0 ? (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '80px', color: 'var(--gray-500)' }}>
                        <p>No hay alertas para mostrar.</p>
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr><th>ID</th><th>Tipo</th><th>Producto</th><th>Mensaje</th><th>Estado</th><th>Fecha</th><th>Acciones</th></tr>
                            </thead>
                            <tbody>
                                {filtered.map(a => {
                                    const prod = getProducto(a.id_producto);
                                    return (
                                        <tr key={a.id_alerta}>
                                            <td>#{a.id_alerta}</td>
                                            <td><span className={`badge ${a.tipo_alerta === 'CRITICA' ? 'badge-danger' : 'badge-warning'}`}>{a.tipo_alerta}</span></td>
                                            <td><strong>{prod?.nombre || `#${a.id_producto}`}</strong></td>
                                            <td>{a.mensaje || '-'}</td>
                                            <td><span className={`badge ${a.estado === 'ACTIVA' ? 'badge-warning' : 'badge-success'}`}>{a.estado}</span></td>
                                            <td>{a.fecha_alerta ? new Date(a.fecha_alerta).toLocaleDateString() : '-'}</td>
                                            <td>
                                                <button className="btn btn-outline" style={{ marginRight: '4px' }} onClick={() => handleEdit(a)}>Editar</button>
                                                <button className="btn" style={{ background: 'var(--danger)', color: 'white' }} onClick={() => handleDelete(a.id_alerta)}>Eliminar</button>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                )}
                <div style={{ marginTop: '12px', fontSize: '0.8rem', color: 'var(--gray-500)' }}>
                    Total: {filtered.length} alerta(s) | Activas: {alertas.filter(a => a.estado === 'ACTIVA').length} | Criticas: {criticas.length}
                </div>
            </div>

            {showModal && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                    <div style={{ background: 'var(--gray-100)', borderRadius: '16px', padding: '32px', width: '100%', maxWidth: '480px', boxShadow: 'var(--shadow-lg)' }}>
                        <h3 style={{ marginBottom: '20px', fontSize: '1.2rem' }}>
                            {editingId ? 'Editar Alerta' : 'Nueva Alerta'}
                        </h3>
                        {editingId ? (
                            <form onSubmit={handleUpdate} noValidate>
                                <div className="form-group">
                                    <label>Estado</label>
                                    <select
                                        value={editData.estado}
                                        onChange={(e) => setEditData({ ...editData, estado: e.target.value })}
                                    >
                                        <option value="ACTIVA">ACTIVA</option>
                                        <option value="RESUELTA">RESUELTA</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label>Mensaje</label>
                                    <textarea
                                        value={editData.mensaje}
                                        onChange={(e) => setEditData({ ...editData, mensaje: e.target.value })}
                                        rows="3"
                                        placeholder="Descripcion de la alerta..."
                                    />
                                </div>
                                <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '20px' }}>
                                    <button type="button" className="btn btn-outline" onClick={() => { setShowModal(false); setEditingId(null); }}>Cancelar</button>
                                    <button type="submit" className="btn btn-primary">Actualizar</button>
                                </div>
                            </form>
                        ) : (
                            <form onSubmit={handleSubmit} noValidate>
                                <div className="form-group">
                                    <label>Producto *</label>
                                    <select
                                        value={formData.id_producto}
                                        onChange={(e) => { setFormData({ ...formData, id_producto: e.target.value }); setErrors({ ...errors, id_producto: '' }); }}
                                        className={errors.id_producto ? 'error' : ''}
                                    >
                                        <option value="">Seleccionar producto...</option>
                                        {productos.map(p => (
                                            <option key={p.id_producto} value={p.id_producto}>{p.codigo} - {p.nombre}</option>
                                        ))}
                                    </select>
                                    {errors.id_producto && <div className="field-error">{errors.id_producto}</div>}
                                </div>
                                <div className="form-group">
                                    <label>Tipo de Alerta *</label>
                                    <select
                                        value={formData.tipo_alerta}
                                        onChange={(e) => { setFormData({ ...formData, tipo_alerta: e.target.value }); setErrors({ ...errors, tipo_alerta: '' }); }}
                                        className={errors.tipo_alerta ? 'error' : ''}
                                    >
                                        <option value="PREVENTIVA">PREVENTIVA</option>
                                        <option value="CRITICA">CRITICA</option>
                                    </select>
                                    {errors.tipo_alerta && <div className="field-error">{errors.tipo_alerta}</div>}
                                </div>
                                <div className="form-group">
                                    <label>Mensaje</label>
                                    <textarea
                                        value={formData.mensaje}
                                        onChange={(e) => setFormData({ ...formData, mensaje: e.target.value })}
                                        rows="3"
                                        placeholder="Descripcion de la alerta..."
                                    />
                                </div>
                                <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '20px' }}>
                                    <button type="button" className="btn btn-outline" onClick={() => setShowModal(false)}>Cancelar</button>
                                    <button type="submit" className="btn btn-primary">Crear</button>
                                </div>
                            </form>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
