import { useState, useEffect } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';

export default function Categorias() {
    const [categorias, setCategorias] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [search, setSearch] = useState('');
    const [formData, setFormData] = useState({ nombre: '', descripcion: '' });
    const [errors, setErrors] = useState({});
    const [toast, setToast] = useState(null);

    useEffect(() => {
        loadCategorias();
    }, []);

    const loadCategorias = async () => {
        try {
            const response = await api.get('/categorias');
            setCategorias(response.data);
        } catch (err) {
            setToast({ message: 'Error al cargar categorías', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const validate = () => {
        const newErrors = {};
        if (!formData.nombre.trim()) {
            newErrors.nombre = 'El nombre es obligatorio';
        } else if (formData.nombre.trim().length < 2) {
            newErrors.nombre = 'El nombre debe tener al menos 2 caracteres';
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
                await api.put(`/categorias/${editingId}`, formData);
                setToast({ message: 'Categoría actualizada exitosamente', type: 'success' });
            } else {
                await api.post('/categorias', formData);
                setToast({ message: 'Categoría creada exitosamente', type: 'success' });
            }
            setShowModal(false);
            setFormData({ nombre: '', descripcion: '' });
            setEditingId(null);
            setErrors({});
            loadCategorias();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al guardar', type: 'error' });
        }
    };

    const handleEdit = (cat) => {
        setFormData({ nombre: cat.nombre, descripcion: cat.descripcion || '' });
        setEditingId(cat.id_categoria);
        setErrors({});
        setShowModal(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm('¿Estás seguro de eliminar esta categoría?')) return;
        try {
            await api.delete(`/categorias/${id}`);
            setToast({ message: 'Categoría eliminada', type: 'success' });
            loadCategorias();
        } catch (err) {
            setToast({ message: 'Error al eliminar', type: 'error' });
        }
    };

    const openModal = () => {
        setEditingId(null);
        setFormData({ nombre: '', descripcion: '' });
        setErrors({});
        setShowModal(true);
    };

    const filtered = categorias.filter(c =>
        c.nombre.toLowerCase().includes(search.toLowerCase())
    );

    if (loading) return <div className="content-area"><p>Cargando...</p></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Gestión de Categorías</h3>
                    <button className="btn btn-primary" onClick={openModal}>
                        + Nueva Categoría
                    </button>
                </div>

                <div style={{ marginBottom: '16px' }}>
                    <input
                        type="text"
                        placeholder="Buscar categoría..."
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
                                <th>Nombre</th>
                                <th>Descripción</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.length === 0 ? (
                                <tr><td colSpan="4" style={{ textAlign: 'center', padding: '20px' }}>No hay categorías</td></tr>
                            ) : filtered.map(cat => (
                                <tr key={cat.id_categoria}>
                                    <td>{cat.id_categoria}</td>
                                    <td><strong>{cat.nombre}</strong></td>
                                    <td>{cat.descripcion || '-'}</td>
                                    <td>
                                        <button className="btn btn-outline" style={{ marginRight: '8px' }} onClick={() => handleEdit(cat)}>Editar</button>
                                        <button className="btn" style={{ background: 'var(--danger)', color: 'white' }} onClick={() => handleDelete(cat.id_categoria)}>Eliminar</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div style={{ marginTop: '12px', fontSize: '0.8rem', color: 'var(--gray-500)' }}>
                    Total: {filtered.length} categoría(s)
                </div>
            </div>

            {showModal && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                    <div style={{ background: 'var(--gray-100)', borderRadius: '16px', padding: '32px', width: '100%', maxWidth: '480px', boxShadow: 'var(--shadow-lg)' }}>
                        <h3 style={{ marginBottom: '20px', fontSize: '1.2rem' }}>{editingId ? 'Editar Categoría' : 'Nueva Categoría'}</h3>
                        <form onSubmit={handleSubmit} noValidate>
                            <div className="form-group">
                                <label>Nombre *</label>
                                <input
                                    type="text"
                                    value={formData.nombre}
                                    onChange={(e) => { setFormData({ ...formData, nombre: e.target.value }); setErrors({ ...errors, nombre: '' }); }}
                                    placeholder="Ej: Electrónicos"
                                    className={errors.nombre ? 'error' : ''}
                                />
                                {errors.nombre && <div className="field-error">{errors.nombre}</div>}
                            </div>
                            <div className="form-group">
                                <label>Descripción</label>
                                <textarea
                                    value={formData.descripcion}
                                    onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                                    rows="3"
                                    placeholder="Descripción opcional..."
                                />
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
