import { Bar } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function ModelComparisonChart({ data }) {
    if (!data) return null;

    const models = Object.keys(data);
    const metrics = ['mae', 'rmse', 'r2', 'mape'];
    const metricLabels = ['MAE', 'RMSE', 'R²', 'MAPE (%)'];

    const chartData = {
        labels: models.map(m => m.toUpperCase()),
        datasets: metrics.map((metric, idx) => ({
            label: metricLabels[idx],
            data: models.map(m => data[m]?.[metric] || 0),
            backgroundColor: [
                'rgba(59, 130, 246, 0.7)',
                'rgba(239, 68, 68, 0.7)',
                'rgba(16, 185, 129, 0.7)',
                'rgba(245, 158, 11, 0.7)',
            ][idx],
            borderColor: [
                'rgb(59, 130, 246)',
                'rgb(239, 68, 68)',
                'rgb(16, 185, 129)',
                'rgb(245, 158, 11)',
            ][idx],
            borderWidth: 2,
            borderRadius: 4,
        })),
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: { usePointStyle: true, padding: 15 },
            },
        },
        scales: {
            y: {
                beginAtZero: true,
                title: { display: true, text: 'Valor' },
            },
        },
    };

    return (
        <div style={{ height: '350px', padding: '16px' }}>
            <Bar data={chartData} options={options} />
        </div>
    );
}
