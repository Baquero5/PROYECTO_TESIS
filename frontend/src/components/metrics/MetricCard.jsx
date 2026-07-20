export default function MetricCard({ label, value, suffix = '', color = 'var(--primary)', description }) {
    return (
        <div className="kpi-card" style={{ background: `linear-gradient(135deg, ${color} 0%, ${color}cc 100%)` }}>
            <div className="kpi-label">{label}</div>
            <div className="kpi-value">
                {value}{suffix}
            </div>
            {description && (
                <div className="kpi-change neutral">{description}</div>
            )}
        </div>
    );
}
