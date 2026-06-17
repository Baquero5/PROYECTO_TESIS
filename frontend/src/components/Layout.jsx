import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useState } from 'react';

const menuItems = [
    { path: '/dashboard', icon: '📈', label: 'Dashboard' },
    { path: '/productos', icon: '📦', label: 'Productos' },
    { path: '/categorias', icon: '🏷️', label: 'Categorías' },
    { path: '/proveedores', icon: '🚚', label: 'Proveedores' },
    { path: '/inventario', icon: '📊', label: 'Inventario' },
    { path: '/ventas', icon: '💰', label: 'Ventas' },
    { path: '/alertas', icon: '⚠️', label: 'Alertas' },
    { path: '/prediccion', icon: '🔮', label: 'Predicción' },
];

export default function Layout() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [darkMode, setDarkMode] = useState(false);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const toggleTheme = () => {
        const newMode = !darkMode;
        setDarkMode(newMode);
        if (newMode) {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
    };

    const fullName = user ? `${user.nombres || ''} ${user.apellidos || ''}`.trim() : '';
    const initials = fullName
        ? fullName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
        : user?.correo?.substring(0, 2).toUpperCase() || 'U';

    return (
        <div className="app-container">
            <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    <h2>SmartInventory</h2>
                    <p>IA para Optimización</p>
                </div>
                <ul className="nav-menu">
                    {menuItems.map((item) => (
                        <li key={item.path} className="nav-item">
                            <NavLink
                                to={item.path}
                                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                                onClick={() => setSidebarOpen(false)}
                            >
                                <span>{item.icon}</span> {item.label}
                            </NavLink>
                        </li>
                    ))}
                    <li className="nav-item" style={{ marginTop: '50px' }}>
                        <button
                            onClick={handleLogout}
                            className="nav-link"
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
                            Cerrar Sesión
                        </button>
                    </li>
                </ul>
            </aside>

            <main className="main-content" onClick={() => {
                if (window.innerWidth <= 768) setSidebarOpen(false);
            }}>
                <header className="top-header">
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <button className="mobile-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
                            ☰
                        </button>
                        <div className="page-title">
                            <h1>Sistema de Predicción de Demanda</h1>
                            <p>Bienvenido, {fullName || user?.correo}</p>
                        </div>
                    </div>
                    <div className="header-actions">
                        <button className="theme-toggle" onClick={toggleTheme}>
                            {darkMode ? '☀️' : '🌓'}
                        </button>
                            <div className="user-info">
                            <div className="user-avatar">{initials}</div>
                            <div>
                                <div className="user-name">{fullName || user?.correo}</div>
                                <div style={{ fontSize: '0.7rem', color: 'var(--gray-500)' }}>
                                    {user?.id_rol === 1 ? 'Administrador' : 'Usuario'}
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
