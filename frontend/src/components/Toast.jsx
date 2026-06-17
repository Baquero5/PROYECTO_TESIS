import { useEffect } from 'react';

export default function Toast({ message, type = 'error', onClose, duration = 4000 }) {
    useEffect(() => {
        const timer = setTimeout(() => {
            onClose();
        }, duration);
        return () => clearTimeout(timer);
    }, [duration, onClose]);

    const icons = {
        error: '✕',
        success: '✓',
        warning: '⚠',
        info: 'ℹ'
    };

    const colors = {
        error: { bg: '#fef2f2', border: '#fca5a5', text: '#991b1b', icon: '#ef4444' },
        success: { bg: '#f0fdf4', border: '#86efac', text: '#166534', icon: '#22c55e' },
        warning: { bg: '#fffbeb', border: '#fcd34d', text: '#92400e', icon: '#f59e0b' },
        info: { bg: '#eff6ff', border: '#93c5fd', text: '#1e40af', icon: '#3b82f6' }
    };

    const style = colors[type];

    return (
        <div style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            zIndex: 9999,
            animation: 'slideIn 0.3s ease',
        }}>
            <div style={{
                background: style.bg,
                border: `1px solid ${style.border}`,
                borderRadius: '12px',
                padding: '16px 20px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                boxShadow: '0 10px 25px rgba(0,0,0,0.15)',
                minWidth: '300px',
                maxWidth: '450px',
            }}>
                <div style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    background: style.icon,
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 'bold',
                    fontSize: '14px',
                    flexShrink: 0,
                }}>
                    {icons[type]}
                </div>
                <span style={{ color: style.text, fontSize: '0.9rem', flex: 1 }}>
                    {message}
                </span>
                <button
                    onClick={onClose}
                    style={{
                        background: 'none',
                        border: 'none',
                        color: style.text,
                        cursor: 'pointer',
                        fontSize: '1.2rem',
                        padding: '0 4px',
                        opacity: 0.6,
                    }}
                >
                    ×
                </button>
            </div>
        </div>
    );
}
