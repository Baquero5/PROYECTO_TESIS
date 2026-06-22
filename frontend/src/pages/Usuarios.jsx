import { useState, useEffect } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';

export default function Usuarios() {
    const [usuarios, setUsuarios] = useState([]);
    const [roles, setRoles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [search, setSearch] = useState('');
    const [formData, setFormData] = useState({
        id_rol: '', nombres: '', apellidos: '', correo: '', password: '', estado: true
    });
    const [errors, setErrors] = useState({});
    const [toast, setToast] = useState(null);

    useEffect(() => { loadData(); }, []);

    const loadData = async () => {
        try {
            const [usrRes, rolRes] = await Promise.all([
                api.get('/auth/users'),
                api.get('/roles')
            ]);
            setUsuarios(usrRes.data);
            setRoles(rolRes.data);
        } catch (err) {
            setToast({ message: 'Error al cargar datos', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const validate = () => {
        const e = {};
        if (!formData.nombres.trim()) e.nombres = 'Obligatorio';
        if (!formData.apellidos.trim()) e.apellidos = 'Obligatorio';
        if (!formData.correo.trim()) e.correo = 'Obligatorio';
        else if (!/\S+@\S+\.\S+/.test(formData.correo)) e.correo = 'Email inválido';
        if (!editingId && !formData.password) e.password = 'Obligatorio';
        else if (!editingId && formData.password.length < 6) e.password = 'Mínimo 6 caracteres';
        if (!formData.id_rol) e.id_rol = 'Seleccione un rol';
        setErrors(e);
        return Object.keys(e).length === 0;
    };

    const handleSubmit = async (ev) => {
        ev.preventDefault();
        if (!validate()) { setToast({ message: 'Complete los campos', type: 'warning' }); return; }
        try {
            const data = { ...formData, id_rol: parseInt(formData.id_rol) };
            if (editingId) {
                if (!data.password) delete data.password;
                await api.put(`/auth/users/${editingId}`, data);
                setToast({ message: 'Usuario actualizado', type: 'success' });
            } else {
                await api.post('/auth/register', data);
                setToast({ message: 'Usuario creado', type: 'success' });
            }
            setShowModal(false);
            resetForm();
            loadData();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al guardar', type: 'error' });
        }
    };

    const handleEdit = (u) => {
        setFormData({
            id_rol: u.id_rol, nombres: u.nombres, apellidos: u.apellidos,
            correo: u.correo, password: '', estado: u.estado
        });
        setEditingId(u.id_usuario);
        setErrors({});
        setShowModal(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm('¿Eliminar este usuario?')) return;
        try {
            await api.delete(`/auth/users/${id}`);
            setToast({ message: 'Usuario eliminado', type: 'success' });
            loadData();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al eliminar', type: 'error' });
        }
    };

    const resetForm = () => {
        setFormData({ id_rol: '', nombres: '', apellidos: '', correo: '', password: '', estado: true });
        setEditingId(null);
        setErrors({});
    };

    const getRolName = (id) => roles.find(r => r.id_rol === id)?.nombre || '-';

    const filtered = usuarios.filter(u =>
        `${u.nombres} ${u.apellidos} ${u.correo}`.toLowerCase().includes(search.toLowerCase())
    );

    if (loading) return <div className="content-area"><p>Cargando...</p></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Gestión de Usuarios</h3>
                    <button className="btn btn-primary" onClick={() => { resetForm(); setShowModal(true); }}>
                        + Nuevo Usuario
                    </button>
                </div>
                <div style={{ marginBottom: '16px' }}>
                    <input type="text" placeholder="Buscar por nombre o email..." value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        style={{ padding: '10px 12px', border: '1px solid var(--gray-300)', borderRadius: '8px', width: '300px', fontSize: '0.85rem' }} />
                </div>
                <div className="table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Nombre</th>
                                <th>Email</th>
                                <th>Rol</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.length === 0 ? (
                                <tr><td colSpan="5" style={{ textAlign: 'center', padding: '20px' }}>No hay usuarios</td></tr>
                            ) : filtered.map(u => (
                                <tr key={u.id_usuario}>
                                    <td><strong>{u.nombres} {u.apellidos}</strong></td>
                                    <td>{u.correo}</td>
                                    <td><span className="badge badge-info">{getRolName(u.id_rol)}</span></td>
                                    <td>
                                        <span className={`badge ${u.estado ? 'badge-success' : 'badge-danger'}`}>
                                            {u.estado ? 'Activo' : 'Inactivo'}
                                        </span>
                                    </td>
                                    <td>
                                        <button className="btn btn-outline" style={{ marginRight: '8px' }} onClick={() => handleEdit(u)}>Editar</button>
                                        <button className="btn" style={{ background: 'var(--danger)', color: 'white' }} onClick={() => handleDelete(u.id_usuario)}>Eliminar</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                <div style={{ marginTop: '12px', fontSize: '0.8rem', color: 'var(--gray-500)' }}>
                    Total: {filtered.length} usuario(s)
                </div>
            </div>

            {showModal && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                    <div style={{ background: 'var(--gray-100)', borderRadius: '16px', padding: '32px', width: '100%', maxWidth: '500px', maxHeight: '90vh', overflow: 'auto' }}>
                        <h3 style={{ marginBottom: '20px' }}>{editingId ? 'Editar Usuario' : 'Nuevo Usuario'}</h3>
                        <form onSubmit={handleSubmit} noValidate>
                            <div className="grid-2">
                                <div className="form-group">
                                    <label>Nombres *</label>
                                    <input type="text" value={formData.nombres}
                                        onChange={(e) => { setFormData({ ...formData, nombres: e.target.value }); setErrors({ ...errors, nombres: '' }); }}
                                        className={errors.nombres ? 'error' : ''} />
                                    {errors.nombres && <div className="field-error">{errors.nombres}</div>}
                                </div>
                                <div className="form-group">
                                    <label>Apellidos *</label>
                                    <input type="text" value={formData.apellidos}
                                        onChange={(e) => { setFormData({ ...formData, apellidos: e.target.value }); setErrors({ ...errors, apellidos: '' }); }}
                                        className={errors.apellidos ? 'error' : ''} />
                                    {errors.apellidos && <div className="field-error">{errors.apellidos}</div>}
                                </div>
                            </div>
                            <div className="form-group">
                                <label>Email *</label>
                                <input type="email" value={formData.correo}
                                    onChange={(e) => { setFormData({ ...formData, correo: e.target.value }); setErrors({ ...errors, correo: '' }); }}
                                    className={errors.correo ? 'error' : ''} />
                                {errors.correo && <div className="field-error">{errors.correo}</div>}
                            </div>
                            <div className="form-group">
                                <label>{editingId ? 'Nueva Contraseña (vacío = sin cambio)' : 'Contraseña *'}</label>
                                <input type="password" value={formData.password}
                                    onChange={(e) => { setFormData({ ...formData, password: e.target.value }); setErrors({ ...errors, password: '' }); }}
                                    className={errors.password ? 'error' : ''} />
                                {errors.password && <div className="field-error">{errors.password}</div>}
                            </div>
                            <div className="form-group">
                                <label>Rol *</label>
                                <select value={formData.id_rol}
                                    onChange={(e) => { setFormData({ ...formData, id_rol: e.target.value }); setErrors({ ...errors, id_rol: '' }); }}
                                    className={errors.id_rol ? 'error' : ''}>
                                    <option value="">Seleccionar...</option>
                                    {roles.map(r => (
                                        <option key={r.id_rol} value={r.id_rol}>{r.nombre}</option>
                                    ))}
                                </select>
                                {errors.id_rol && <div className="field-error">{errors.id_rol}</div>}
                            </div>
                            <div className="form-group">
                                <label>
                                    <input type="checkbox" checked={formData.estado}
                                        onChange={(e) => setFormData({ ...formData, estado: e.target.checked })}
                                        style={{ marginRight: '8px' }} />
                                    Activo
                                </label>
                            </div>
                            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '20px' }}>
                                <button type="button" className="btn btn-outline" onClick={() => setShowModal(false)}>Cancelar</button>
                                <button type="submit" className="btn btn-primary">{editingId ? 'Actualizar' : 'Crear'}</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
