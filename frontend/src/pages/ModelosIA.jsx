import { useState, useEffect } from 'react';
import api from '../services/api';
import mlMetricsService from '../services/mlService';
import Toast from '../components/Toast';
import MetricCard from '../components/metrics/MetricCard';
import ModelComparisonChart from '../components/metrics/ModelComparisonChart';
import FeatureImportanceChart from '../components/metrics/FeatureImportanceChart';
import PredictionVsActual from '../components/metrics/PredictionVsActual';
import ErrorDistribution from '../components/metrics/ErrorDistribution';
import { Bar } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler,
} from 'chart.js';

ChartJS.register(
    CategoryScale, LinearScale, BarElement, PointElement,
    LineElement, Title, Tooltip, Legend, Filler
);

export default function ModelosIA() {
    const [modelos, setModelos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [toast, setToast] = useState(null);
    const [metrics, setMetrics] = useState(null);
    const [features, setFeatures] = useState(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [modelosRes, metricsRes, featuresRes] = await Promise.allSettled([
                api.get('/modelos-ia'),
                mlMetricsService.getAll(),
                mlMetricsService.getFeatures(),
            ]);

            if (modelosRes.status === 'fulfilled') setModelos(modelosRes.value.data);
            if (metricsRes.status === 'fulfilled') setMetrics(metricsRes.value.data);
            if (featuresRes.status === 'fulfilled') setFeatures(featuresRes.value.data);
        } catch {
            setToast({ message: 'Error al cargar datos', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    const handleActivar = async (modeloId) => {
        try {
            await api.put(`/modelos-ia/${modeloId}/activar`);
            setToast({ message: 'Modelo activado exitosamente', type: 'success' });
            loadData();
        } catch {
            setToast({ message: 'Error al activar modelo', type: 'error' });
        }
    };

    const handleDesactivar = async (modeloId) => {
        try {
            await api.put(`/modelos-ia/${modeloId}/desactivar`);
            setToast({ message: 'Modelo desactivado exitosamente', type: 'success' });
            loadData();
        } catch {
            setToast({ message: 'Error al desactivar modelo', type: 'error' });
        }
    };

    const prepareChartData = (metrica) => {
        return {
            labels: modelos.map(m => `${m.algoritmo} v${m.version || '1.0'}`),
            datasets: [{
                label: metrica.toUpperCase(),
                data: modelos.map(m => m[metrica] || 0),
                backgroundColor: modelos.map(m =>
                    m.estado === 'ACTIVO' ? 'rgba(16, 185, 129, 0.8)' : 'rgba(107, 114, 128, 0.5)'
                ),
                borderColor: modelos.map(m =>
                    m.estado === 'ACTIVO' ? 'rgb(16, 185, 129)' : 'rgb(107, 114, 128)'
                ),
                borderWidth: 2,
            }],
        };
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, title: { display: true, text: 'Valor' } } },
    };

    const ensemble = metrics?.ensemble;
    const mae = ensemble?.mae?.toFixed(4) || 'N/A';
    const rmse = ensemble?.rmse?.toFixed(4) || 'N/A';
    const r2 = ensemble?.r2 != null ? (ensemble.r2 * 100).toFixed(2) : 'N/A';
    const mape = ensemble?.mape?.toFixed(2) || 'N/A';

    if (loading) return <div className="content-area"><p>Cargando modelos...</p></div>;

    return (
        <div className="content-area">
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <div className="grid-4" style={{ marginBottom: '24px' }}>
                <MetricCard label="MAE" value={mae} color="var(--primary)" description="Error Absoluto Medio" />
                <MetricCard label="RMSE" value={rmse} color="var(--danger)" description="Error Cuadrático Medio" />
                <MetricCard label="R²" value={r2} suffix="%" color="var(--success)" description="Coef. Determinación" />
                <MetricCard label="MAPE" value={mape} suffix="%" color="var(--warning)" description="Error Porcentual" />
            </div>

            <div className="grid-3" style={{ gap: '16px', marginBottom: '24px' }}>
                {modelos.map(modelo => (
                    <div
                        key={modelo.id_modelo}
                        className="card"
                        style={{
                            borderLeft: modelo.estado === 'ACTIVO' ? '4px solid var(--success)' : '4px solid var(--gray-400)',
                            backgroundColor: modelo.estado === 'ACTIVO' ? 'var(--success-light)' : 'transparent',
                        }}
                    >
                        <div className="card-header">
                            <h3 className="card-title">{modelo.algoritmo} v{modelo.version || '1.0'}</h3>
                            <span className={`badge ${modelo.estado === 'ACTIVO' ? 'badge-success' : 'badge-secondary'}`}>
                                {modelo.estado}
                            </span>
                        </div>
                        <div style={{ padding: '16px' }}>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                                <div>
                                    <div style={{ fontSize: '0.8rem', color: 'var(--gray-500)' }}>MAE</div>
                                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--primary)' }}>
                                        {modelo.mae?.toFixed(3) || 'N/A'}
                                    </div>
                                </div>
                                <div>
                                    <div style={{ fontSize: '0.8rem', color: 'var(--gray-500)' }}>RMSE</div>
                                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--primary)' }}>
                                        {modelo.rmse?.toFixed(3) || 'N/A'}
                                    </div>
                                </div>
                                <div>
                                    <div style={{ fontSize: '0.8rem', color: 'var(--gray-500)' }}>R²</div>
                                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--success)' }}>
                                        {modelo.r2?.toFixed(3) || 'N/A'}
                                    </div>
                                </div>
                                <div>
                                    <div style={{ fontSize: '0.8rem', color: 'var(--gray-500)' }}>MAPE</div>
                                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--warning)' }}>
                                        {modelo.mape?.toFixed(1) || 'N/A'}%
                                    </div>
                                </div>
                            </div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--gray-500)', marginBottom: '12px' }}>
                                <div>Archivo: {modelo.archivo_modelo || 'N/A'}</div>
                                <div>Entrenado: {modelo.fecha_entrenamiento ? new Date(modelo.fecha_entrenamiento).toLocaleDateString() : 'N/A'}</div>
                            </div>
                            <div style={{ display: 'flex', gap: '8px' }}>
                                {modelo.estado === 'INACTIVO' ? (
                                    <button className="btn btn-success" style={{ flex: 1, fontSize: '0.8rem' }} onClick={() => handleActivar(modelo.id_modelo)}>
                                        Activar
                                    </button>
                                ) : (
                                    <button className="btn btn-secondary" style={{ flex: 1, fontSize: '0.8rem' }} onClick={() => handleDesactivar(modelo.id_modelo)}>
                                        Desactivar
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="grid-2" style={{ marginBottom: '24px' }}>
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Comparativa de Modelos</h3>
                    </div>
                    <ModelComparisonChart data={metrics?.comparativa} />
                </div>
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Importancia de Features</h3>
                    </div>
                    <FeatureImportanceChart data={features} />
                </div>
            </div>

            <div className="grid-2" style={{ marginBottom: '24px' }}>
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Predicción vs Valor Real</h3>
                    </div>
                    <PredictionVsActual />
                </div>
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Distribución de Errores</h3>
                    </div>
                    <ErrorDistribution />
                </div>
            </div>

            <div className="grid-3" style={{ gap: '16px', marginBottom: '24px' }}>
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">MAE</h3>
                    </div>
                    <div style={{ height: '200px', padding: '16px' }}>
                        <Bar data={prepareChartData('mae')} options={chartOptions} />
                    </div>
                    <div style={{ padding: '8px 16px', fontSize: '0.8rem', color: 'var(--gray-500)', textAlign: 'center' }}>
                        Menor es mejor
                    </div>
                </div>
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">RMSE</h3>
                    </div>
                    <div style={{ height: '200px', padding: '16px' }}>
                        <Bar data={prepareChartData('rmse')} options={chartOptions} />
                    </div>
                    <div style={{ padding: '8px 16px', fontSize: '0.8rem', color: 'var(--gray-500)', textAlign: 'center' }}>
                        Menor es mejor
                    </div>
                </div>
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">R²</h3>
                    </div>
                    <div style={{ height: '200px', padding: '16px' }}>
                        <Bar data={prepareChartData('r2')} options={chartOptions} />
                    </div>
                    <div style={{ padding: '8px 16px', fontSize: '0.8rem', color: 'var(--gray-500)', textAlign: 'center' }}>
                        Mayor es mejor (máx 1.0)
                    </div>
                </div>
            </div>

            {ensemble?.weights && (
                <div className="card" style={{ marginBottom: '24px' }}>
                    <div className="card-header">
                        <h3 className="card-title">Pesos del Ensemble</h3>
                    </div>
                    <div style={{ padding: '16px' }}>
                        <div style={{ display: 'flex', gap: '24px' }}>
                            <div style={{ flex: 1, textAlign: 'center' }}>
                                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>
                                    {(ensemble.weights.xgboost * 100).toFixed(0)}%
                                </div>
                                <div style={{ color: 'var(--gray-500)' }}>XGBoost</div>
                            </div>
                            <div style={{ flex: 1, textAlign: 'center' }}>
                                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--success)' }}>
                                    {(ensemble.weights.lightgbm * 100).toFixed(0)}%
                                </div>
                                <div style={{ color: 'var(--gray-500)' }}>LightGBM</div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Detalle de Modelos</h3>
                </div>
                <div className="table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Modelo</th>
                                <th>Estado</th>
                                <th>MAE</th>
                                <th>RMSE</th>
                                <th>R²</th>
                                <th>MAPE</th>
                                <th>Fecha</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {modelos.map(modelo => (
                                <tr key={modelo.id_modelo} style={{ backgroundColor: modelo.estado === 'ACTIVO' ? 'var(--success-light)' : 'transparent' }}>
                                    <td><strong>{modelo.algoritmo} v{modelo.version || '1.0'}</strong></td>
                                    <td>
                                        <span className={`badge ${modelo.estado === 'ACTIVO' ? 'badge-success' : 'badge-secondary'}`}>
                                            {modelo.estado}
                                        </span>
                                    </td>
                                    <td>{modelo.mae?.toFixed(3) || 'N/A'}</td>
                                    <td>{modelo.rmse?.toFixed(3) || 'N/A'}</td>
                                    <td style={{ color: 'var(--success)', fontWeight: 'bold' }}>{modelo.r2?.toFixed(3) || 'N/A'}</td>
                                    <td>{modelo.mape?.toFixed(1) || 'N/A'}%</td>
                                    <td>{modelo.fecha_entrenamiento ? new Date(modelo.fecha_entrenamiento).toLocaleDateString() : 'N/A'}</td>
                                    <td>
                                        {modelo.estado === 'INACTIVO' ? (
                                            <button className="btn btn-success" style={{ fontSize: '0.8rem' }} onClick={() => handleActivar(modelo.id_modelo)}>
                                                Activar
                                            </button>
                                        ) : (
                                            <button className="btn btn-secondary" style={{ fontSize: '0.8rem' }} onClick={() => handleDesactivar(modelo.id_modelo)}>
                                                Desactivar
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
