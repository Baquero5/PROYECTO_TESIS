import { useState, useEffect, useRef } from 'react';
import api from '../services/api';

export default function NotificationBell() {
    const [alertas, setAlertas] = useState([]);
    const [count, setCount] = useState(0);
    const [open, setOpen] = useState(false);
    const ref = useRef(null);

    useEffect(() => {
        loadAlerts();
        const interval = setInterval(loadAlerts, 30000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        const handleClick = (e) => {
            if (ref.current && !ref.current.contains(e.target)) {
                setOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, []);

    const loadAlerts = async () => {
        try {
            const [alertasRes, countRes] = await Promise.allSettled([
                api.get('/alertas/no-leidas'),
                api.get('/alertas/contador'),
            ]);
            if (alertasRes.status === 'fulfilled') setAlertas(alertasRes.value.data);
            if (countRes.status === 'fulfilled') setCount(countRes.value.data.count);
        } catch (err) {
            // silent
        }
    };

    const markAsRead = async (id) => {
        try {
            await api.put(`/alertas/${id}/marcar-leida`);
            setAlertas(prev => prev.filter(a => a.id_alerta !== id));
            setCount(prev => Math.max(0, prev - 1));
        } catch (err) {
            // silent
        }
    };

    const markAllRead = async () => {
        try {
            await api.put('/alertas/marcar-todas-leidas');
            setAlertas([]);
            setCount(0);
        } catch (err) {
            // silent
        }
    };

    const getProducto = (id) => {
        // Simple fallback - will use product name from alert message
        return `Producto #${id}`;
    };

    return (
        <div ref={ref} style={{ position: 'relative' }}>
            <button
                onClick={() => setOpen(!open)}
                style={{
                    position: 'relative',
                    background: 'none',
                    border: 'none',
                    fontSize: '1.3rem',
                    cursor: 'pointer',
                    padding: '8px',
                    borderRadius: '8px',
                    transition: 'background 0.2s',
                }}
                onMouseEnter={(e) => e.target.style.background = 'var(--gray-200)'}
                onMouseLeave={(e) => e.target.style.background = 'none'}
            >
                🔔
                {count > 0 && (
                    <span style={{
                        position: 'absolute',
                        top: '2px',
                        right: '2px',
                        background: '#ef4444',
                        color: 'white',
                        borderRadius: '50%',
                        width: '18px',
                        height: '18px',
                        fontSize: '0.65rem',
                        fontWeight: 'bold',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        border: '2px solid var(--gray-100)',
                    }}>
                        {count > 99 ? '99+' : count}
                    </span>
                )}
            </button>

            {open && (
                <div style={{
                    position: 'absolute',
                    top: '100%',
                    right: 0,
                    marginTop: '8px',
                    width: '360px',
                    maxHeight: '420px',
                    background: 'var(--gray-100)',
                    borderRadius: '12px',
                    boxShadow: 'var(--shadow-lg)',
                    border: '1px solid var(--gray-200)',
                    zIndex: 1000,
                    overflow: 'hidden',
                }}>
                    <div style={{
                        padding: '12px 16px',
                        borderBottom: '1px solid var(--gray-200)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                    }}>
                        <strong style={{ fontSize: '0.9rem' }}>Notificaciones</strong>
                        {alertas.length > 0 && (
                            <button
                                onClick={markAllRead}
                                style={{
                                    background: 'none',
                                    border: 'none',
                                    color: 'var(--primary)',
                                    fontSize: '0.75rem',
                                    cursor: 'pointer',
                                }}
                            >
                                Marcar todas leídas
                            </button>
                        )}
                    </div>

                    <div style={{ maxHeight: '340px', overflow: 'auto' }}>
                        {alertas.length === 0 ? (
                            <div style={{
                                padding: '32px 16px',
                                textAlign: 'center',
                                color: 'var(--gray-500)',
                                fontSize: '0.85rem',
                            }}>
                                Sin notificaciones nuevas
                            </div>
                        ) : (
                            alertas.map(alerta => (
                                <div
                                    key={alerta.id_alerta}
                                    style={{
                                        padding: '12px 16px',
                                        borderBottom: '1px solid var(--gray-200)',
                                        cursor: 'pointer',
                                        transition: 'background 0.2s',
                                        display: 'flex',
                                        gap: '10px',
                                        alignItems: 'flex-start',
                                    }}
                                    onMouseEnter={(e) => e.currentTarget.style.background = 'var(--gray-200)'}
                                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                    onClick={() => markAsRead(alerta.id_alerta)}
                                >
                                    <span style={{ fontSize: '1.2rem' }}>
                                        {alerta.tipo_alerta === 'CRITICA' ? '🔴' : '🟡'}
                                    </span>
                                    <div style={{ flex: 1, minWidth: 0 }}>
                                        <div style={{
                                            fontSize: '0.8rem',
                                            fontWeight: 'bold',
                                            color: alerta.tipo_alerta === 'CRITICA' ? 'var(--danger)' : 'var(--warning)',
                                            marginBottom: '2px',
                                        }}>
                                            {alerta.tipo_alerta}
                                        </div>
                                        <div style={{
                                            fontSize: '0.8rem',
                                            color: 'var(--gray-700)',
                                            overflow: 'hidden',
                                            textOverflow: 'ellipsis',
                                            whiteSpace: 'nowrap',
                                        }}>
                                            {alerta.mensaje || `Producto #${alerta.id_producto}`}
                                        </div>
                                        <div style={{
                                            fontSize: '0.7rem',
                                            color: 'var(--gray-500)',
                                            marginTop: '2px',
                                        }}>
                                            {alerta.fecha_alerta ? new Date(alerta.fecha_alerta).toLocaleString() : ''}
                                        </div>
                                    </div>
                                    <button
                                        onClick={(e) => { e.stopPropagation(); markAsRead(alerta.id_alerta); }}
                                        style={{
                                            background: 'none',
                                            border: 'none',
                                            color: 'var(--gray-400)',
                                            cursor: 'pointer',
                                            fontSize: '0.9rem',
                                            padding: '2px',
                                        }}
                                        title="Marcar como leída"
                                    >
                                        ✓
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
