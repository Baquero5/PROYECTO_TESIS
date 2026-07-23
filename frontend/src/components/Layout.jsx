import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useState } from 'react';
import NotificationBell from './NotificationBell';

const allMenuItems = [
    { path: '/dashboard', icon: '📈', label: 'Dashboard', roles: [1, 2] },
    { path: '/productos', icon: '📦', label: 'Productos', roles: [1, 2, 3] },
    { path: '/categorias', icon: '🏷️', label: 'Categorías', roles: [1, 2, 3] },
    { path: '/subcategorias', icon: '📋', label: 'Subcategorías', roles: [1, 2, 3] },
    { path: '/proveedores', icon: '🚚', label: 'Proveedores', roles: [1, 2, 3] },
    { path: '/inventario', icon: '📊', label: 'Inventario', roles: [1, 2, 3] },
    { path: '/ventas', icon: '💰', label: 'Ventas', roles: [1, 2, 3] },
    { path: '/alertas', icon: '⚠️', label: 'Alertas', roles: [1, 2, 3] },
    { path: '/prediccion', icon: '🔮', label: 'Predicción', roles: [1] },
    { path: '/historial-predicciones', icon: '📋', label: 'Historial Pred.', roles: [1, 2] },
    { path: '/modelos-ia', icon: '🤖', label: 'Modelos IA', roles: [1, 2] },
    { path: '/reportes', icon: '📥', label: 'Reportes', roles: [1, 2, 3] },
    { path: '/usuarios', icon: '👥', label: 'Usuarios', roles: [1] },
    { path: '/roles', icon: '🔐', label: 'Roles', roles: [1] },
];

export default function Layout() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [collapsed, setCollapsed] = useState(() => {
        return localStorage.getItem('sidebarCollapsed') === 'true';
    });
    const [darkMode, setDarkMode] = useState(() => {
        const saved = localStorage.getItem('darkMode') === 'true';
        if (saved) {
            document.documentElement.setAttribute('data-theme', 'dark');
        }
        return saved;
    });

    const menuItems = allMenuItems.filter(item => item.roles.includes(user?.id_rol));

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const toggleTheme = () => {
        const newMode = !darkMode;
        setDarkMode(newMode);
        localStorage.setItem('darkMode', String(newMode));
        if (newMode) {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
    };

    const toggleSidebar = () => {
        const newCollapsed = !collapsed;
        setCollapsed(newCollapsed);
        localStorage.setItem('sidebarCollapsed', String(newCollapsed));
    };

    const fullName = user ? `${user.nombres || ''} ${user.apellidos || ''}`.trim() : '';
    const initials = fullName
        ? fullName.split(' ').filter(Boolean).map(n => n[0]).join('').substring(0, 2).toUpperCase()
        : (user?.correo?.substring(0, 2) || 'U').toUpperCase();

    return (
        <div className="app-container">
            <aside className={`sidebar ${sidebarOpen ? 'open' : ''} ${collapsed ? 'collapsed' : ''}`}>
                <div className="sidebar-header">
                    <div className="sidebar-header-text">
                        {!collapsed && (
                            <>
                                <h2>SmartInventory</h2>
                                <p>IA para Optimización</p>
                            </>
                        )}
                        {collapsed && <span style={{ fontSize: '1.5rem' }}>📦</span>}
                    </div>
                    <button 
                        className="sidebar-toggle" 
                        onClick={toggleSidebar}
                        title={collapsed ? 'Expandir menú' : 'Colapsar menú'}
                    >
                        {collapsed ? '»' : '«'}
                    </button>
                </div>
                <ul className="nav-menu">
                    {menuItems.map((item) => (
                        <li key={item.path} className="nav-item">
                            <NavLink
                                to={item.path}
                                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                                onClick={() => setSidebarOpen(false)}
                                title={collapsed ? item.label : ''}
                            >
                                <span>{item.icon}</span> {!collapsed && item.label}
                            </NavLink>
                        </li>
                    ))}
                    <li className="nav-item" style={{ marginTop: '50px' }}>
                        <button
                            onClick={handleLogout}
                            className="nav-link"
                            title={collapsed ? 'Cerrar Sesión' : ''}
                            style={{
                                width: '100%',
                                background: 'none',
                                border: 'none',
                                color: '#f87171',
                                cursor: 'pointer',
                                textAlign: 'left',
                                fontSize: '0.9rem',
                            }}
                        >
                            <span>🚪</span> {!collapsed && 'Cerrar Sesión'}
                        </button>
                    </li>
                </ul>
            </aside>

            <main className="main-content" onClick={() => {
                if (window.innerWidth <= 768) setSidebarOpen(false);
            }}>
                <header className="top-header">
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <button className="mobile-toggle" onClick={(e) => { e.stopPropagation(); setSidebarOpen(!sidebarOpen); }}>
                            ☰
                        </button>
                        <div className="page-title">
                            <h1>Sistema de Predicción de Demanda</h1>
                            <p>Bienvenido, {fullName || user?.correo}</p>
                        </div>
                    </div>
                    <div className="header-actions">
                        <NotificationBell />
                        <button className="theme-toggle" onClick={toggleTheme}>
                            {darkMode ? '☀️' : '🌓'}
                        </button>
                            <div className="user-info">
                            <div className="user-avatar">{initials}</div>
                            <div>
                                <div className="user-name">{fullName || user?.correo}</div>
                                <div style={{ fontSize: '0.7rem', color: 'var(--gray-500)' }}>
                                    {user?.id_rol === 1 ? 'Administrador' : user?.id_rol === 2 ? 'Sistemas' : 'Vendedor'}
                                </div>
                            </div>
                        </div>
                    </div>
                </header>

                <Outlet />
            </main>
        </div>
    );
}
