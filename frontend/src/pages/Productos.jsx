import { useState, useEffect, useRef, useCallback } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';

export default function Productos() {
    const [productos, setProductos] = useState([]);
    const [categorias, setCategorias] = useState([]);
    const [subcategorias, setSubcategorias] = useState([]);
    const [proveedores, setProveedores] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [search, setSearch] = useState('');
    const [filterCategoria, setFilterCategoria] = useState('');
    const [filterSubcategoria, setFilterSubcategoria] = useState('');
    const [filterProveedor, setFilterProveedor] = useState('');
    const [filterEstado, setFilterEstado] = useState('');
    const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
    const [visibleCount, setVisibleCount] = useState(20);
    const [loadingMore, setLoadingMore] = useState(false);
    const tableContainerRef = useRef(null);
    const [formData, setFormData] = useState({
        id_categoria: '', id_subcategoria: '', id_proveedor: '', codigo: '', nombre: '',
        descripcion: '', precio_compra: '', precio_venta: ''
    });
    const [errors, setErrors] = useState({});
    const [toast, setToast] = useState(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [prodRes, catRes, subRes, provRes] = await Promise.allSettled([
                api.get('/products'),
                api.get('/categorias'),
                api.get('/subcategorias'),
                api.get('/proveedores')
            ]);
            if (prodRes.status === 'fulfilled') setProductos(prodRes.value.data);
            if (catRes.status === 'fulfilled') setCategorias(catRes.value.data);
            if (subRes.status === 'fulfilled') setSubcategorias(subRes.value.data);
            if (provRes.status === 'fulfilled') setProveedores(provRes.value.data);
        } catch (err) {
            setToast({ message: 'Error al cargar datos', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const validate = () => {
        const newErrors = {};

        if (!formData.codigo.trim()) {
            newErrors.codigo = 'El código es obligatorio';
        } else if (formData.codigo.trim().length < 1) {
            newErrors.codigo = 'Mínimo 1 carácter';
        } else if (formData.codigo.trim().length > 50) {
            newErrors.codigo = 'Máximo 50 caracteres';
        }

        if (!formData.nombre.trim()) {
            newErrors.nombre = 'El nombre es obligatorio';
        } else if (formData.nombre.trim().length < 2) {
            newErrors.nombre = 'Mínimo 2 caracteres';
        } else if (formData.nombre.trim().length > 150) {
            newErrors.nombre = 'Máximo 150 caracteres';
        }

        if (!formData.id_categoria) {
            newErrors.id_categoria = 'Seleccione una categoría';
        }

        if (!formData.id_proveedor) {
            newErrors.id_proveedor = 'Seleccione un proveedor';
        }

        if (formData.descripcion && formData.descripcion.length > 500) {
            newErrors.descripcion = 'Máximo 500 caracteres';
        }

        if (formData.precio_compra !== '' && parseFloat(formData.precio_compra) < 0) {
            newErrors.precio_compra = 'No puede ser negativo';
        }

        if (formData.precio_venta !== '' && parseFloat(formData.precio_venta) < 0) {
            newErrors.precio_venta = 'No puede ser negativo';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validate()) {
            setToast({ message: 'Complete todos los campos requeridos', type: 'warning' });
            return;
        }
        try {
            const data = {
                ...formData,
                id_categoria: parseInt(formData.id_categoria),
                id_subcategoria: formData.id_subcategoria ? parseInt(formData.id_subcategoria) : null,
                id_proveedor: parseInt(formData.id_proveedor),
                precio_compra: parseFloat(formData.precio_compra) || 0,
                precio_venta: parseFloat(formData.precio_venta) || 0
            };
            if (editingId) {
                await api.put(`/products/${editingId}`, data);
                setToast({ message: 'Producto actualizado', type: 'success' });
            } else {
                await api.post('/products', data);
                setToast({ message: 'Producto creado', type: 'success' });
            }
            setShowModal(false);
            resetForm();
            loadData();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al guardar', type: 'error' });
        }
    };

    const handleEdit = (prod) => {
        setFormData({
            id_categoria: prod.id_categoria,
            id_subcategoria: prod.id_subcategoria || '',
            id_proveedor: prod.id_proveedor,
            codigo: prod.codigo,
            nombre: prod.nombre,
            descripcion: prod.descripcion || '',
            precio_compra: prod.precio_compra,
            precio_venta: prod.precio_venta
        });
        setEditingId(prod.id_producto);
        setErrors({});
        setShowModal(true);
    };

    const handleDelete = async (id) => {
        if (!window.confirm('¿Estás seguro de eliminar este producto?')) return;
        try {
            await api.delete(`/products/${id}`);
            setToast({ message: 'Producto eliminado', type: 'success' });
            loadData();
        } catch (err) {
            setToast({ message: 'Error al eliminar', type: 'error' });
        }
    };

    const resetForm = () => {
        setFormData({ id_categoria: '', id_subcategoria: '', id_proveedor: '', codigo: '', nombre: '', descripcion: '', precio_compra: '', precio_venta: '' });
        setEditingId(null);
        setErrors({});
    };

    const getCategoriaName = (id) => categorias.find(c => c.id_categoria === id)?.nombre || '-';
    const getSubcategoriaName = (id) => subcategorias.find(s => s.id_subcategoria === id)?.nombre || '-';
    const getProveedorName = (id) => proveedores.find(p => p.id_proveedor === id)?.razon_social || '-';

    const filtered = productos.filter(p => {
        const matchSearch = p.nombre.toLowerCase().includes(search.toLowerCase()) ||
            p.codigo.toLowerCase().includes(search.toLowerCase());
        const matchCategoria = !filterCategoria || p.id_categoria === parseInt(filterCategoria);
        const matchSubcategoria = !filterSubcategoria || p.id_subcategoria === parseInt(filterSubcategoria);
        const matchProveedor = !filterProveedor || p.id_proveedor === parseInt(filterProveedor);
        const matchEstado = filterEstado === '' || 
            (filterEstado === 'true' && p.estado) ||
            (filterEstado === 'false' && !p.estado);
        return matchSearch && matchCategoria && matchSubcategoria && matchProveedor && matchEstado;
    });

    const sorted = [...filtered].sort((a, b) => {
        if (!sortConfig.key) return 0;
        let aVal = a[sortConfig.key];
        let bVal = b[sortConfig.key];
        if (sortConfig.key === 'categoria') {
            aVal = getCategoriaName(a.id_categoria);
            bVal = getCategoriaName(b.id_categoria);
        } else if (sortConfig.key === 'subcategoria') {
            aVal = getSubcategoriaName(a.id_subcategoria);
            bVal = getSubcategoriaName(b.id_subcategoria);
        } else if (sortConfig.key === 'proveedor') {
            aVal = getProveedorName(a.id_proveedor);
            bVal = getProveedorName(b.id_proveedor);
        }
        if (aVal === null || aVal === undefined) return 1;
        if (bVal === null || bVal === undefined) return -1;
        if (typeof aVal === 'string') aVal = aVal.toLowerCase();
        if (typeof bVal === 'string') bVal = bVal.toLowerCase();
        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
    });

    const handleSort = (key) => {
        setSortConfig(prev => ({
            key,
            direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
        }));
        setVisibleCount(20);
    };

    const handleFilterChange = (setter) => (e) => {
        setter(e.target.value);
        setVisibleCount(20);
    };

    const getSortIcon = (key) => {
        if (sortConfig.key !== key) return '↕';
        return sortConfig.direction === 'asc' ? '↑' : '↓';
    };

    const handleScroll = useCallback(() => {
        const container = tableContainerRef.current;
        if (!container || loadingMore) return;
        if (container.scrollTop + container.clientHeight >= container.scrollHeight - 50) {
            if (visibleCount < sorted.length) {
                setLoadingMore(true);
                setTimeout(() => {
                    setVisibleCount(prev => Math.min(prev + 20, sorted.length));
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

    const visibleProducts = sorted.slice(0, visibleCount);

    if (loading) return <div className="content-area"><p>Cargando...</p></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Gestión de Productos</h3>
                    <button className="btn btn-primary" onClick={() => { resetForm(); setShowModal(true); }}>
                        + Nuevo Producto
                    </button>
                </div>

                <div style={{ marginBottom: '16px', display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
                    <input
                        type="text"
                        placeholder="Buscar por nombre o código..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        style={{ padding: '10px 12px', border: '1px solid var(--gray-300)', borderRadius: '8px', width: '250px', fontSize: '0.85rem' }}
                    />
                    <select
                        value={filterCategoria}
                        onChange={handleFilterChange(setFilterCategoria)}
                        style={{ padding: '10px 12px', border: '1px solid var(--gray-300)', borderRadius: '8px', fontSize: '0.85rem', minWidth: '150px' }}
                    >
                        <option value="">Todas las categorías</option>
                        {categorias.map(c => (
                            <option key={c.id_categoria} value={c.id_categoria}>{c.nombre}</option>
                        ))}
                    </select>
                    <select
                        value={filterSubcategoria}
                        onChange={handleFilterChange(setFilterSubcategoria)}
                        style={{ padding: '10px 12px', border: '1px solid var(--gray-300)', borderRadius: '8px', fontSize: '0.85rem', minWidth: '150px' }}
                    >
                        <option value="">Todas las subcategorías</option>
                        {subcategorias
                            .filter(s => !filterCategoria || s.id_categoria === parseInt(filterCategoria))
                            .map(s => (
                            <option key={s.id_subcategoria} value={s.id_subcategoria}>{s.nombre}</option>
                        ))}
                    </select>
                    <select
                        value={filterProveedor}
                        onChange={handleFilterChange(setFilterProveedor)}
                        style={{ padding: '10px 12px', border: '1px solid var(--gray-300)', borderRadius: '8px', fontSize: '0.85rem', minWidth: '150px' }}
                    >
                        <option value="">Todos los proveedores</option>
                        {proveedores.map(p => (
                            <option key={p.id_proveedor} value={p.id_proveedor}>{p.razon_social}</option>
                        ))}
                    </select>
                    <select
                        value={filterEstado}
                        onChange={handleFilterChange(setFilterEstado)}
                        style={{ padding: '10px 12px', border: '1px solid var(--gray-300)', borderRadius: '8px', fontSize: '0.85rem', minWidth: '120px' }}
                    >
                        <option value="">Todos</option>
                        <option value="true">Activos</option>
                        <option value="false">Inactivos</option>
                    </select>
                </div>

                <div className="table-container" ref={tableContainerRef} style={{ maxHeight: '500px', overflow: 'auto' }}>
                    <table className="data-table">
                        <thead style={{ position: 'sticky', top: 0, zIndex: 1 }}>
                            <tr>
                                <th onClick={() => handleSort('codigo')} style={{ cursor: 'pointer', userSelect: 'none', background: 'var(--gray-200)' }}>
                                    Código {getSortIcon('codigo')}
                                </th>
                                <th onClick={() => handleSort('nombre')} style={{ cursor: 'pointer', userSelect: 'none', background: 'var(--gray-200)' }}>
                                    Nombre {getSortIcon('nombre')}
                                </th>
                                <th onClick={() => handleSort('categoria')} style={{ cursor: 'pointer', userSelect: 'none', background: 'var(--gray-200)' }}>
                                    Categoría {getSortIcon('categoria')}
                                </th>
                                <th onClick={() => handleSort('subcategoria')} style={{ cursor: 'pointer', userSelect: 'none', background: 'var(--gray-200)' }}>
                                    Subcategoría {getSortIcon('subcategoria')}
                                </th>
                                <th onClick={() => handleSort('proveedor')} style={{ cursor: 'pointer', userSelect: 'none', background: 'var(--gray-200)' }}>
                                    Proveedor {getSortIcon('proveedor')}
                                </th>
                                <th onClick={() => handleSort('precio_compra')} style={{ cursor: 'pointer', userSelect: 'none', background: 'var(--gray-200)' }}>
                                    P. Compra {getSortIcon('precio_compra')}
                                </th>
                                <th onClick={() => handleSort('precio_venta')} style={{ cursor: 'pointer', userSelect: 'none', background: 'var(--gray-200)' }}>
                                    P. Venta {getSortIcon('precio_venta')}
                                </th>
                                <th onClick={() => handleSort('fecha_ingreso')} style={{ cursor: 'pointer', userSelect: 'none', background: 'var(--gray-200)' }}>
                                    F. Ingreso {getSortIcon('fecha_ingreso')}
                                </th>
                                <th onClick={() => handleSort('estado')} style={{ cursor: 'pointer', userSelect: 'none', background: 'var(--gray-200)' }}>
                                    Estado {getSortIcon('estado')}
                                </th>
                                <th style={{ background: 'var(--gray-200)' }}>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {visibleProducts.length === 0 ? (
                                <tr><td colSpan="10" style={{ textAlign: 'center', padding: '20px' }}>No hay productos</td></tr>
                            ) : visibleProducts.map(prod => (
                                <tr key={prod.id_producto}>
                                    <td><span className="badge badge-info">{prod.codigo}</span></td>
                                    <td><strong>{prod.nombre}</strong></td>
                                    <td>{getCategoriaName(prod.id_categoria)}</td>
                                    <td>{getSubcategoriaName(prod.id_subcategoria)}</td>
                                    <td>{getProveedorName(prod.id_proveedor)}</td>
                                    <td>${prod.precio_compra}</td>
                                    <td>${prod.precio_venta}</td>
                                    <td>{prod.fecha_ingreso ? new Date(prod.fecha_ingreso).toLocaleDateString() : '-'}</td>
                                    <td>
                                        <span className={`badge ${prod.estado ? 'badge-success' : 'badge-danger'}`}>
                                            {prod.estado ? 'Activo' : 'Inactivo'}
                                        </span>
                                    </td>
                                    <td>
                                        <button className="btn btn-outline" style={{ marginRight: '8px' }} onClick={() => handleEdit(prod)}>Editar</button>
                                        <button className="btn" style={{ background: 'var(--danger)', color: 'white' }} onClick={() => handleDelete(prod.id_producto)}>Eliminar</button>
                                    </td>
                                </tr>
                            ))}
                            {loadingMore && (
                                <tr>
                                    <td colSpan="10" style={{ textAlign: 'center', padding: '12px', color: 'var(--gray-500)' }}>
                                        Cargando más productos...
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>

                <div style={{ marginTop: '12px', fontSize: '0.8rem', color: 'var(--gray-500)', display: 'flex', justifyContent: 'space-between' }}>
                    <span>Mostrando {visibleCount} de {sorted.length} producto(s)</span>
                    {(search || filterCategoria || filterSubcategoria || filterProveedor || filterEstado) && (
                        <button 
                            onClick={() => { setSearch(''); setFilterCategoria(''); setFilterSubcategoria(''); setFilterProveedor(''); setFilterEstado(''); setVisibleCount(20); }}
                            style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', fontSize: '0.8rem' }}
                        >
                            Limpiar filtros
                        </button>
                    )}
                </div>
            </div>

            {showModal && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                    <div style={{ background: 'var(--gray-100)', borderRadius: '16px', padding: '32px', width: '100%', maxWidth: '560px', maxHeight: '90vh', overflow: 'auto', boxShadow: 'var(--shadow-lg)' }}>
                        <h3 style={{ marginBottom: '20px', fontSize: '1.2rem' }}>{editingId ? 'Editar Producto' : 'Nuevo Producto'}</h3>
                        <form onSubmit={handleSubmit} noValidate>
                            <div className="grid-2">
                                <div className="form-group">
                                    <label>Código *</label>
                                    <input type="text" value={formData.codigo}
                                        onChange={(e) => { setFormData({ ...formData, codigo: e.target.value }); setErrors({ ...errors, codigo: '' }); }}
                                        placeholder="Ej: PROD-001"
                                        className={errors.codigo ? 'error' : ''} />
                                    {errors.codigo && <div className="field-error">{errors.codigo}</div>}
                                </div>
                                <div className="form-group">
                                    <label>Nombre *</label>
                                    <input type="text" value={formData.nombre}
                                        onChange={(e) => { setFormData({ ...formData, nombre: e.target.value }); setErrors({ ...errors, nombre: '' }); }}
                                        placeholder="Nombre del producto"
                                        className={errors.nombre ? 'error' : ''} />
                                    {errors.nombre && <div className="field-error">{errors.nombre}</div>}
                                </div>
                            </div>
                            <div className="grid-2">
                                <div className="form-group">
                                    <label>Categoría *</label>
                                    <select value={formData.id_categoria}
                                        onChange={(e) => { setFormData({ ...formData, id_categoria: e.target.value, id_subcategoria: '' }); setErrors({ ...errors, id_categoria: '' }); }}
                                        className={errors.id_categoria ? 'error' : ''}>
                                        <option value="">Seleccionar...</option>
                                        {categorias.map(c => (
                                            <option key={c.id_categoria} value={c.id_categoria}>{c.nombre}</option>
                                        ))}
                                    </select>
                                    {errors.id_categoria && <div className="field-error">{errors.id_categoria}</div>}
                                </div>
                                <div className="form-group">
                                    <label>Subcategoría</label>
                                    <select value={formData.id_subcategoria}
                                        onChange={(e) => setFormData({ ...formData, id_subcategoria: e.target.value })}>
                                        <option value="">Seleccionar...</option>
                                        {subcategorias
                                            .filter(s => formData.id_categoria && s.id_categoria === parseInt(formData.id_categoria))
                                            .map(s => (
                                            <option key={s.id_subcategoria} value={s.id_subcategoria}>{s.nombre}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>
                            <div className="grid-2">
                                <div className="form-group">
                                    <label>Proveedor *</label>
                                    <select value={formData.id_proveedor}
                                        onChange={(e) => { setFormData({ ...formData, id_proveedor: e.target.value }); setErrors({ ...errors, id_proveedor: '' }); }}
                                        className={errors.id_proveedor ? 'error' : ''}>
                                        <option value="">Seleccionar...</option>
                                        {proveedores.map(p => (
                                            <option key={p.id_proveedor} value={p.id_proveedor}>{p.razon_social}</option>
                                        ))}
                                    </select>
                                    {errors.id_proveedor && <div className="field-error">{errors.id_proveedor}</div>}
                                </div>
                            </div>
                            <div className="form-group">
                                <label>Descripción</label>
                                <textarea value={formData.descripcion}
                                    onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                                    rows="2" placeholder="Descripción del producto..." />
                            </div>
                            <div className="grid-2">
                                <div className="form-group">
                                    <label>Precio Compra ($)</label>
                                    <input type="number" step="0.01" min="0" value={formData.precio_compra}
                                        onChange={(e) => { setFormData({ ...formData, precio_compra: e.target.value }); setErrors({ ...errors, precio_compra: '' }); }}
                                        placeholder="0.00"
                                        className={errors.precio_compra ? 'error' : ''} />
                                    {errors.precio_compra && <div className="field-error">{errors.precio_compra}</div>}
                                </div>
                                <div className="form-group">
                                    <label>Precio Venta ($)</label>
                                    <input type="number" step="0.01" min="0" value={formData.precio_venta}
                                        onChange={(e) => { setFormData({ ...formData, precio_venta: e.target.value }); setErrors({ ...errors, precio_venta: '' }); }}
                                        placeholder="0.00"
                                        className={errors.precio_venta ? 'error' : ''} />
                                    {errors.precio_venta && <div className="field-error">{errors.precio_venta}</div>}
                                </div>
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
