import { useState, useEffect } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';
import { useAuth } from '../context/AuthContext';

export default function Proveedores() {
    const { user } = useAuth();
    const [proveedores, setProveedores] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [search, setSearch] = useState('');
    const [formData, setFormData] = useState({
        razon_social: '', ruc: '', telefono: '', correo: '', direccion: ''
    });
    const [errors, setErrors] = useState({});
    const [toast, setToast] = useState(null);

    useEffect(() => {
        loadProveedores();
    }, []);

    const loadProveedores = async () => {
        try {
            const response = await api.get('/proveedores');
            setProveedores(response.data);
        } catch (err) {
            setToast({ message: 'Error al cargar proveedores', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const validate = () => {
        const newErrors = {};

        if (!formData.razon_social.trim()) {
            newErrors.razon_social = 'La razón social es obligatoria';
        } else if (formData.razon_social.trim().length < 3) {
            newErrors.razon_social = 'Mínimo 3 caracteres';
        }

        if (!formData.ruc.trim()) {
            newErrors.ruc = 'El RUC es obligatorio';
        } else if (!/^\d{13}$/.test(formData.ruc)) {
            newErrors.ruc = 'El RUC debe tener exactamente 13 dígitos';
        }

        if (formData.correo && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.correo)) {
            newErrors.correo = 'Ingrese un correo válido';
        }

        if (formData.telefono && !/^\d{7,10}$/.test(formData.telefono)) {
            newErrors.telefono = 'Ingrese un número de teléfono válido (7-10 dígitos)';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validate()) {
            setToast({ message: 'Corrija los errores antes de continuar', type: 'warning' });
            return;
        }
        try {
            if (editingId) {
                await api.put(`/proveedores/${editingId}`, formData);
                setToast({ message: 'Proveedor actualizado exitosamente', type: 'success' });
            } else {
                await api.post('/proveedores', formData);
                setToast({ message: 'Proveedor creado exitosamente', type: 'success' });
            }
            setShowModal(false);
            resetForm();
            loadProveedores();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al guardar', type: 'error' });
        }
    };

    const handleEdit = (prov) => {
        setFormData({
            razon_social: prov.razon_social,
            ruc: prov.ruc,
            telefono: prov.telefono || '',
            correo: prov.correo || '',
            direccion: prov.direccion || ''
        });
        setEditingId(prov.id_proveedor);
        setErrors({});
        setShowModal(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm('¿Estás seguro de eliminar este proveedor?')) return;
        try {
            await api.delete(`/proveedores/${id}`);
            setToast({ message: 'Proveedor eliminado', type: 'success' });
            loadProveedores();
        } catch (err) {
            setToast({ message: 'Error al eliminar', type: 'error' });
        }
    };

    const resetForm = () => {
        setFormData({ razon_social: '', ruc: '', telefono: '', correo: '', direccion: '' });
        setEditingId(null);
        setErrors({});
    };

    const filtered = proveedores.filter(p =>
        p.razon_social.toLowerCase().includes(search.toLowerCase()) ||
        p.ruc.includes(search)
    );

    if (loading) return <div className="content-area"><p>Cargando...</p></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Gestión de Proveedores</h3>
                    {user?.id_rol !== 3 && (
                        <button className="btn btn-primary" onClick={() => { resetForm(); setShowModal(true); }}>
                            + Nuevo Proveedor
                        </button>
                    )}
                </div>

                <div style={{ marginBottom: '16px' }}>
                    <input
                        type="text"
                        placeholder="Buscar por nombre o RUC..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        style={{ padding: '10px 12px', border: '1px solid var(--gray-300)', borderRadius: '8px', width: '300px', fontSize: '0.85rem' }}
                    />
                </div>

                <div className="table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Razón Social</th>
                                <th>RUC</th>
                                <th>Teléfono</th>
                                <th>Correo</th>
                                {user?.id_rol !== 3 && <th>Acciones</th>}
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.length === 0 ? (
                                <tr><td colSpan="6" style={{ textAlign: 'center', padding: '20px' }}>No hay proveedores</td></tr>
                            ) : filtered.map(prov => (
                                <tr key={prov.id_proveedor}>
                                    <td>{prov.id_proveedor}</td>
                                    <td><strong>{prov.razon_social}</strong></td>
                                    <td>{prov.ruc}</td>
                                    <td>{prov.telefono || '-'}</td>
                                    <td>{prov.correo || '-'}</td>
                                    {user?.id_rol !== 3 && (
                                        <td>
                                            <button className="btn btn-outline" style={{ marginRight: '8px' }} onClick={() => handleEdit(prov)}>Editar</button>
                                            <button className="btn" style={{ background: 'var(--danger)', color: 'white' }} onClick={() => handleDelete(prov.id_proveedor)}>Eliminar</button>
                                        </td>
                                    )}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div style={{ marginTop: '12px', fontSize: '0.8rem', color: 'var(--gray-500)' }}>
                    Total: {filtered.length} proveedor(es)
                </div>
            </div>

            {showModal && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                    <div style={{ background: 'var(--gray-100)', borderRadius: '16px', padding: '32px', width: '100%', maxWidth: '520px', maxHeight: '90vh', overflow: 'auto', boxShadow: 'var(--shadow-lg)' }}>
                        <h3 style={{ marginBottom: '20px', fontSize: '1.2rem' }}>{editingId ? 'Editar Proveedor' : 'Nuevo Proveedor'}</h3>
                        <form onSubmit={handleSubmit} noValidate>
                            <div className="form-group">
                                <label>Razón Social *</label>
                                <input type="text" value={formData.razon_social}
                                    onChange={(e) => { setFormData({ ...formData, razon_social: e.target.value }); setErrors({ ...errors, razon_social: '' }); }}
                                    placeholder="Ej: Distribuidora XYZ"
                                    className={errors.razon_social ? 'error' : ''} />
                                {errors.razon_social && <div className="field-error">{errors.razon_social}</div>}
                            </div>
                            <div className="grid-2">
                                <div className="form-group">
                                    <label>RUC *</label>
                                    <input type="text" value={formData.ruc} maxLength="13"
                                        onChange={(e) => { setFormData({ ...formData, ruc: e.target.value }); setErrors({ ...errors, ruc: '' }); }}
                                        placeholder="13 dígitos"
                                        className={errors.ruc ? 'error' : ''} />
                                    {errors.ruc && <div className="field-error">{errors.ruc}</div>}
                                </div>
                                <div className="form-group">
                                    <label>Teléfono</label>
                                    <input type="text" value={formData.telefono} maxLength="10"
                                        onChange={(e) => { setFormData({ ...formData, telefono: e.target.value }); setErrors({ ...errors, telefono: '' }); }}
                                        placeholder="0999999999"
                                        className={errors.telefono ? 'error' : ''} />
                                    {errors.telefono && <div className="field-error">{errors.telefono}</div>}
                                </div>
                            </div>
                            <div className="form-group">
                                <label>Correo</label>
                                <input type="email" value={formData.correo}
                                    onChange={(e) => { setFormData({ ...formData, correo: e.target.value }); setErrors({ ...errors, correo: '' }); }}
                                    placeholder="proveedor@ejemplo.com"
                                    className={errors.correo ? 'error' : ''} />
                                {errors.correo && <div className="field-error">{errors.correo}</div>}
                            </div>
                            <div className="form-group">
                                <label>Dirección</label>
                                <textarea value={formData.direccion}
                                    onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
                                    rows="2" placeholder="Dirección completa..." />
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
