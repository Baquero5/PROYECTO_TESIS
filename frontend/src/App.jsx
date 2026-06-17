import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute';
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

function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route
                        element={
                            <PrivateRoute>
                                <Layout />
                            </PrivateRoute>
                        }
                    >
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/productos" element={<Productos />} />
                        <Route path="/categorias" element={<Categorias />} />
                        <Route path="/proveedores" element={<Proveedores />} />
                        <Route path="/inventario" element={<Inventario />} />
                        <Route path="/ventas" element={<Ventas />} />
                        <Route path="/alertas" element={<Alertas />} />
                        <Route path="/prediccion" element={<Prediccion />} />
                    </Route>
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;
