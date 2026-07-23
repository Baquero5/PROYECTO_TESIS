import { useState, useEffect } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';
import { useAuth } from '../context/AuthContext';

export default function Subcategorias() {
    const { user } = useAuth();
    const [subcategorias, setSubcategorias] = useState([]);
    const [categorias, setCategorias] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [search, setSearch] = useState('');
    const [filterCategoria, setFilterCategoria] = useState('');
    const [formData, setFormData] = useState({ id_categoria: '', nombre: '', descripcion: '' });
    const [errors, setErrors] = useState({});
    const [toast, setToast] = useState(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [subRes, catRes] = await Promise.allSettled([
                api.get('/subcategorias'),
                api.get('/categorias')
            ]);
            if (subRes.status === 'fulfilled') setSubcategorias(subRes.value.data);
            if (catRes.status === 'fulfilled') setCategorias(catRes.value.data);
        } catch (err) {
            setToast({ message: 'Error al cargar datos', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const validate = () => {
        const newErrors = {};
        if (!formData.id_categoria) {
            newErrors.id_categoria = 'Seleccione una categoría';
        }
        if (!formData.nombre.trim()) {
            newErrors.nombre = 'El nombre es obligatorio';
        } else if (formData.nombre.trim().length < 2) {
            newErrors.nombre = 'Mínimo 2 caracteres';
        } else if (formData.nombre.trim().length > 100) {
            newErrors.nombre = 'Máximo 100 caracteres';
        }
        if (formData.descripcion && formData.descripcion.length > 300) {
            newErrors.descripcion = 'Máximo 300 caracteres';
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
            const payload = {
                id_categoria: parseInt(formData.id_categoria),
                nombre: formData.nombre.trim(),
                descripcion: formData.descripcion || null
            };
            if (editingId) {
                await api.put(`/subcategorias/${editingId}`, payload);
                setToast({ message: 'Subcategoría actualizada exitosamente', type: 'success' });
            } else {
                await api.post('/subcategorias', payload);
                setToast({ message: 'Subcategoría creada exitosamente', type: 'success' });
            }
            setShowModal(false);
            setFormData({ id_categoria: '', nombre: '', descripcion: '' });
            setEditingId(null);
            setErrors({});
            loadData();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al guardar', type: 'error' });
        }
    };

    const handleEdit = (sub) => {
        setFormData({
            id_categoria: sub.id_categoria,
            nombre: sub.nombre,
            descripcion: sub.descripcion || ''
        });
        setEditingId(sub.id_subcategoria);
        setErrors({});
        setShowModal(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm('¿Estás seguro de eliminar esta subcategoría?')) return;
        try {
            await api.delete(`/subcategorias/${id}`);
            setToast({ message: 'Subcategoría eliminada', type: 'success' });
            loadData();
        } catch (err) {
            setToast({ message: 'Error al eliminar', type: 'error' });
        }
    };

    const openModal = () => {
        setEditingId(null);
        setFormData({ id_categoria: '', nombre: '', descripcion: '' });
        setErrors({});
        setShowModal(true);
    };

    const getNombreCategoria = (id) => {
        const cat = categorias.find(c => c.id_categoria === id);
        return cat ? cat.nombre : '-';
    };

    const filtered = subcategorias.filter(s => {
        const matchSearch = s.nombre.toLowerCase().includes(search.toLowerCase());
        const matchCategoria = filterCategoria === '' || s.id_categoria === parseInt(filterCategoria);
        return matchSearch && matchCategoria;
    });

    if (loading) return <div className="content-area"><p>Cargando...</p></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Gestión de Subcategorías</h3>
                    {user?.id_rol !== 3 && (
                        <button className="btn btn-primary" onClick={openModal}>
                            + Nueva Subcategoría
                        </button>
                    )}
                </div>

                <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                    <input
                        type="text"
                        placeholder="Buscar subcategoría..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        style={{ padding: '10px 12px', border: '1px solid var(--gray-300)', borderRadius: '8px', width: '300px', fontSize: '0.85rem' }}
                    />
                    <select
                        value={filterCategoria}
                        onChange={(e) => setFilterCategoria(e.target.value)}
                        style={{ padding: '10px 12px', border: '1px solid var(--gray-300)', borderRadius: '8px', fontSize: '0.85rem' }}
                    >
                        <option value="">Todas las categorías</option>
                        {categorias.map(c => (
                            <option key={c.id_categoria} value={c.id_categoria}>{c.nombre}</option>
                        ))}
                    </select>
                </div>

                <div className="table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nombre</th>
                                <th>Categoría</th>
                                <th>Descripción</th>
                                {user?.id_rol !== 3 && <th>Acciones</th>}
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.length === 0 ? (
                                <tr><td colSpan="5" style={{ textAlign: 'center', padding: '20px' }}>No hay subcategorías</td></tr>
                            ) : filtered.map(sub => (
                                <tr key={sub.id_subcategoria}>
                                    <td>{sub.id_subcategoria}</td>
                                    <td><strong>{sub.nombre}</strong></td>
                                    <td>{getNombreCategoria(sub.id_categoria)}</td>
                                    <td>{sub.descripcion || '-'}</td>
                                    {user?.id_rol !== 3 && (
                                        <td>
                                            <button className="btn btn-outline" style={{ marginRight: '8px' }} onClick={() => handleEdit(sub)}>Editar</button>
                                            <button className="btn" style={{ background: 'var(--danger)', color: 'white' }} onClick={() => handleDelete(sub.id_subcategoria)}>Eliminar</button>
                                        </td>
                                    )}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div style={{ marginTop: '12px', fontSize: '0.8rem', color: 'var(--gray-500)' }}>
                    Total: {filtered.length} subcategoría(s)
                </div>
            </div>

            {showModal && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                    <div style={{ background: 'var(--gray-100)', borderRadius: '16px', padding: '32px', width: '100%', maxWidth: '480px', boxShadow: 'var(--shadow-lg)' }}>
                        <h3 style={{ marginBottom: '20px', fontSize: '1.2rem' }}>{editingId ? 'Editar Subcategoría' : 'Nueva Subcategoría'}</h3>
                        <form onSubmit={handleSubmit} noValidate>
                            <div className="form-group">
                                <label>Categoría *</label>
                                <select
                                    value={formData.id_categoria}
                                    onChange={(e) => { setFormData({ ...formData, id_categoria: e.target.value }); setErrors({ ...errors, id_categoria: '' }); }}
                                    className={errors.id_categoria ? 'error' : ''}
                                >
                                    <option value="">Seleccionar categoría...</option>
                                    {categorias.map(c => (
                                        <option key={c.id_categoria} value={c.id_categoria}>{c.nombre}</option>
                                    ))}
                                </select>
                                {errors.id_categoria && <div className="field-error">{errors.id_categoria}</div>}
                            </div>
                            <div className="form-group">
                                <label>Nombre *</label>
                                <input
                                    type="text"
                                    value={formData.nombre}
                                    onChange={(e) => { setFormData({ ...formData, nombre: e.target.value }); setErrors({ ...errors, nombre: '' }); }}
                                    placeholder="Ej: Enlatados y Conservas"
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
