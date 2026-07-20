import { useState, useEffect } from 'react';
import api from '../services/api';
import Toast from '../components/Toast';

const PERMISO_MODULES = {
    'PRODUCTOS': ['CREAR', 'LEER', 'ACTUALIZAR', 'ELIMINAR'],
    'CATEGORIAS': ['CREAR', 'LEER', 'ACTUALIZAR', 'ELIMINAR'],
    'PROVEEDORES': ['CREAR', 'LEER', 'ACTUALIZAR', 'ELIMINAR'],
    'INVENTARIO': ['CREAR', 'LEER', 'ACTUALIZAR', 'ELIMINAR'],
    'VENTAS': ['CREAR', 'LEER', 'ACTUALIZAR', 'ELIMINAR'],
    'ALERTAS': ['CREAR', 'LEER', 'ACTUALIZAR', 'ELIMINAR'],
    'USUARIOS': ['CREAR', 'LEER', 'ACTUALIZAR', 'ELIMINAR'],
    'ROLES': ['CREAR', 'LEER', 'ACTUALIZAR', 'ELIMINAR'],
    'REPORTES': ['LEER'],
    'CONFIGURACION': ['CREAR', 'LEER', 'ACTUALIZAR', 'ELIMINAR'],
    'PREDICCION_IA': ['LEER'],
};

export default function Roles() {
    const [roles, setRoles] = useState([]);
    const [permisos, setPermisos] = useState([]);
    const [rolPermisos, setRolPermisos] = useState([]);
    const [selectedRol, setSelectedRol] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [formData, setFormData] = useState({ nombre: '', descripcion: '' });
    const [toast, setToast] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => { loadData(); }, []);

    const loadData = async () => {
        try {
            const [rolesRes, permisosRes] = await Promise.allSettled([
                api.get('/roles'),
                api.get('/permisos')
            ]);
            if (rolesRes.status === 'fulfilled') setRoles(rolesRes.value.data);
            if (permisosRes.status === 'fulfilled') setPermisos(permisosRes.value.data);
        } catch (err) {
            setToast({ message: 'Error al cargar datos', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const loadRolPermisos = async (rolId) => {
        try {
            const res = await api.get(`/permisos/rol/${rolId}`);
            setSelectedRol(rolId);
            setRolPermisos(res.data.map(p => p.id_permiso));
        } catch (err) {
            setToast({ message: 'Error al cargar permisos', type: 'error' });
        }
    };

    const togglePermiso = (permisoId) => {
        setRolPermisos(prev =>
            prev.includes(permisoId) ? prev.filter(id => id !== permisoId) : [...prev, permisoId]
        );
    };

    const toggleModule = (module) => {
        const modulePermisos = permisos.filter(p => p.codigo.startsWith(module + '_')).map(p => p.id_permiso);
        const allSelected = modulePermisos.every(id => rolPermisos.includes(id));
        if (allSelected) {
            setRolPermisos(prev => prev.filter(id => !modulePermisos.includes(id)));
        } else {
            setRolPermisos(prev => [...new Set([...prev, ...modulePermisos])]);
        }
    };

    const savePermisos = async () => {
        try {
            await api.post(`/permisos/rol/${selectedRol}`, { id_permisos: rolPermisos });
            setToast({ message: 'Permisos guardados correctamente', type: 'success' });
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al guardar', type: 'error' });
        }
    };

    const handleSubmitRol = async (ev) => {
        ev.preventDefault();
        if (!formData.nombre.trim()) {
            setToast({ message: 'El nombre del rol es obligatorio', type: 'warning' });
            return;
        }
        if (formData.nombre.trim().length < 2) {
            setToast({ message: 'El nombre debe tener al menos 2 caracteres', type: 'warning' });
            return;
        }
        if (formData.nombre.trim().length > 100) {
            setToast({ message: 'El nombre no puede exceder 100 caracteres', type: 'warning' });
            return;
        }
        try {
            if (editingId) {
                await api.put(`/roles/${editingId}`, formData);
                setToast({ message: 'Rol actualizado', type: 'success' });
            } else {
                await api.post('/roles', formData);
                setToast({ message: 'Rol creado', type: 'success' });
            }
            setShowModal(false);
            setFormData({ nombre: '', descripcion: '' });
            setEditingId(null);
            loadData();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al guardar', type: 'error' });
        }
    };

    const handleEditRol = (rol) => {
        setFormData({ nombre: rol.nombre, descripcion: rol.descripcion || '' });
        setEditingId(rol.id_rol);
        setShowModal(true);
    };

    const handleDeleteRol = async (id) => {
        if (!window.confirm('¿Eliminar este rol?')) return;
        try {
            await api.delete(`/roles/${id}`);
            setToast({ message: 'Rol eliminado', type: 'success' });
            if (selectedRol === id) { setSelectedRol(null); setRolPermisos([]); }
            loadData();
        } catch (err) {
            setToast({ message: err.response?.data?.detail || 'Error al eliminar', type: 'error' });
        }
    };

    if (loading) return <div className="content-area"><p>Cargando...</p></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Roles</h3>
                        <button className="btn btn-primary" onClick={() => { setFormData({ nombre: '', descripcion: '' }); setEditingId(null); setShowModal(true); }}>
                            + Nuevo Rol
                        </button>
                    </div>
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr><th>Nombre</th><th>Descripción</th><th>Acciones</th></tr>
                            </thead>
                            <tbody>
                                {roles.map(rol => (
                                    <tr key={rol.id_rol} style={{ cursor: 'pointer', background: selectedRol === rol.id_rol ? 'var(--primary-light)' : '' }}
                                        onClick={() => loadRolPermisos(rol.id_rol)}>
                                        <td><strong>{rol.nombre}</strong></td>
                                        <td>{rol.descripcion || '-'}</td>
                                        <td onClick={(e) => e.stopPropagation()}>
                                            <button className="btn btn-outline" style={{ marginRight: '8px' }} onClick={() => handleEditRol(rol)}>Editar</button>
                                            <button className="btn" style={{ background: 'var(--danger)', color: 'white' }} onClick={() => handleDeleteRol(rol.id_rol)}>Eliminar</button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">
                            Permisos {selectedRol ? `- ${roles.find(r => r.id_rol === selectedRol)?.nombre}` : ''}
                        </h3>
                        {selectedRol && (
                            <button className="btn btn-primary" onClick={savePermisos}>Guardar</button>
                        )}
                    </div>
                    {!selectedRol ? (
                        <p style={{ padding: '20px', color: 'var(--gray-500)', textAlign: 'center' }}>
                            Seleccione un rol para ver sus permisos
                        </p>
                    ) : (
                        <div style={{ padding: '16px' }}>
                            {Object.entries(PERMISO_MODULES).map(([module, actions]) => {
                                const modulePermisos = permisos.filter(p => p.codigo.startsWith(module + '_'));
                                const selectedCount = modulePermisos.filter(p => rolPermisos.includes(p.id_permiso)).length;
                                const allSelected = selectedCount === modulePermisos.length;

                                return (
                                    <div key={module} style={{ marginBottom: '16px' }}>
                                        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold', marginBottom: '6px', cursor: 'pointer' }}>
                                            <input type="checkbox" checked={allSelected}
                                                onChange={() => toggleModule(module)} />
                                            {module} <span style={{ fontWeight: 'normal', color: 'var(--gray-500)', fontSize: '0.8rem' }}>({selectedCount}/{modulePermisos.length})</span>
                                        </label>
                                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', paddingLeft: '24px' }}>
                                            {actions.map(action => {
                                                const codigo = `${module}_${action}`;
                                                const permiso = permisos.find(p => p.codigo === codigo);
                                                if (!permiso) return null;
                                                const checked = rolPermisos.includes(permiso.id_permiso);
                                                return (
                                                    <label key={codigo} style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', cursor: 'pointer', padding: '4px 8px', borderRadius: '4px', background: checked ? 'var(--primary-light)' : 'var(--gray-200)' }}>
                                                        <input type="checkbox" checked={checked}
                                                            onChange={() => togglePermiso(permiso.id_permiso)} />
                                                        {action}
                                                    </label>
                                                );
                                            })}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            </div>

            {showModal && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
                    <div style={{ background: 'var(--gray-100)', borderRadius: '16px', padding: '32px', width: '100%', maxWidth: '400px' }}>
                        <h3 style={{ marginBottom: '20px' }}>{editingId ? 'Editar Rol' : 'Nuevo Rol'}</h3>
                        <form onSubmit={handleSubmitRol}>
                            <div className="form-group">
                                <label>Nombre *</label>
                                <input type="text" value={formData.nombre}
                                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                                    placeholder="Ej: VENDEDOR" />
                            </div>
                            <div className="form-group">
                                <label>Descripción</label>
                                <input type="text" value={formData.descripcion}
                                    onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                                    placeholder="Descripción del rol" />
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
