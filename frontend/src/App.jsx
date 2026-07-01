import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import RoleRoute from './components/RoleRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Categorias from './pages/Categorias';
import Proveedores from './pages/Proveedores';
import Productos from './pages/Productos';
import Inventario from './pages/InventarioPage';
import Ventas from './pages/Ventas';
import Alertas from './pages/Alertas';
import Prediccion from './pages/Prediccion';
import ModelosIA from './pages/ModelosIA';
import Usuarios from './pages/Usuarios';
import Roles from './pages/Roles';
import Reportes from './pages/Reportes';

function AppRoutes() {
    const { user } = useAuth();
    const defaultRoute = user?.id_rol === 3 ? '/ventas' : '/dashboard';

    return (
        <Routes>
            <Route path="/login" element={<Login />} />
            <Route
                element={
                    <PrivateRoute>
                        <Layout />
                    </PrivateRoute>
                }
            >
                <Route path="/dashboard" element={
                    <RoleRoute allowedRoles={[1, 2]}>
                        <Dashboard />
                    </RoleRoute>
                } />
                <Route path="/productos" element={<Productos />} />
                <Route path="/categorias" element={<Categorias />} />
                <Route path="/proveedores" element={<Proveedores />} />
                <Route path="/inventario" element={<Inventario />} />
                <Route path="/ventas" element={<Ventas />} />
                <Route path="/alertas" element={
                    <RoleRoute allowedRoles={[1, 2]}>
                        <Alertas />
                    </RoleRoute>
                } />
                <Route path="/prediccion" element={
                    <RoleRoute allowedRoles={[1, 2]}>
                        <Prediccion />
                    </RoleRoute>
                } />
                <Route path="/modelos-ia" element={
                    <RoleRoute allowedRoles={[1, 2]}>
                        <ModelosIA />
                    </RoleRoute>
                } />
                <Route path="/usuarios" element={
                    <RoleRoute allowedRoles={[1, 2]}>
                        <Usuarios />
                    </RoleRoute>
                } />
                <Route path="/roles" element={
                    <RoleRoute allowedRoles={[1, 2]}>
                        <Roles />
                    </RoleRoute>
                } />
                <Route path="/reportes" element={
                    <RoleRoute allowedRoles={[1, 2]}>
                        <Reportes />
                    </RoleRoute>
                } />
            </Route>
            <Route path="/" element={<Navigate to={defaultRoute} replace />} />
            <Route path="*" element={<Navigate to={defaultRoute} replace />} />
        </Routes>
    );
}

function App() {
    return (
        <AuthProvider>
            <Router>
                <AppRoutes />
            </Router>
        </AuthProvider>
    );
}

export default App;
