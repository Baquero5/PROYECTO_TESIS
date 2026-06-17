import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import Toast from '../components/Toast';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [remember, setRemember] = useState(false);
    const [loading, setLoading] = useState(false);
    const [toast, setToast] = useState(null);
    const [errors, setErrors] = useState({});
    const { login } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        const savedEmail = localStorage.getItem('rememberedEmail');
        if (savedEmail) {
            setEmail(savedEmail);
            setRemember(true);
        }
    }, []);

    const validate = () => {
        const newErrors = {};

        if (!email.trim()) {
            newErrors.email = 'El correo es obligatorio';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            newErrors.email = 'Ingrese un correo válido';
        }

        if (!password) {
            newErrors.password = 'La contraseña es obligatoria';
        } else if (password.length < 6) {
            newErrors.password = 'La contraseña debe tener al menos 6 caracteres';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setToast(null);

        if (!validate()) {
            setToast({ message: 'Complete todos los campos correctamente', type: 'warning' });
            return;
        }

        setLoading(true);
        try {
            if (remember) {
                localStorage.setItem('rememberedEmail', email);
            } else {
                localStorage.removeItem('rememberedEmail');
            }
            await login(email, password);
            navigate('/dashboard');
        } catch (err) {
            if (err.response) {
                setToast({ message: err.response.data?.detail || 'Credenciales incorrectas', type: 'error' });
            } else if (err.request) {
                setToast({ message: 'No se pudo conectar al servidor', type: 'error' });
            } else {
                setToast({ message: 'Error al iniciar sesión', type: 'error' });
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="login-card">
                <div className="login-header">
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
                    <h1>SmartInventory AI</h1>
                    <p style={{ color: 'var(--gray-500)', marginTop: '8px', fontSize: '0.85rem' }}>
                        Sistema de Predicción de Demanda<br />y Optimización de Inventarios
                    </p>
                </div>

                <form onSubmit={handleSubmit} noValidate>
                    <div className="form-group">
                        <label>Correo Electrónico</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => { setEmail(e.target.value); setErrors({ ...errors, email: '' }); }}
                            placeholder="admin@sistema.com"
                            className={errors.email ? 'error' : ''}
                        />
                        {errors.email && <div className="field-error">{errors.email}</div>}
                    </div>
                    <div className="form-group">
                        <label>Contraseña</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => { setPassword(e.target.value); setErrors({ ...errors, password: '' }); }}
                            placeholder="••••••••"
                            className={errors.password ? 'error' : ''}
                        />
                        {errors.password && <div className="field-error">{errors.password}</div>}
                    </div>
                    <div className="form-group">
                        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                            <input
                                type="checkbox"
                                checked={remember}
                                onChange={(e) => setRemember(e.target.checked)}
                                style={{ width: 'auto' }}
                            />
                            Recordar sesión
                        </label>
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        className="btn btn-primary"
                        style={{ width: '100%', padding: '12px', fontSize: '1rem', marginTop: '8px', justifyContent: 'center' }}
                    >
                        {loading ? 'Entrando...' : 'Iniciar Sesión'}
                    </button>
                </form>

                <div className="text-center" style={{ marginTop: '24px' }}>
                    <p style={{ fontSize: '0.7rem', color: 'var(--gray-400)' }}>
                        © 2026 - Proyecto de Titulación<br />
                        Villa M. & Baquero V. | UNEMI
                    </p>
                </div>
            </div>
        </div>
    );
}
