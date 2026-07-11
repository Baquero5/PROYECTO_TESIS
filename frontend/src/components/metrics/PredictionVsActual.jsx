import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

export default function PredictionVsActual({ actual = [], predicted = [] }) {
    if (actual.length === 0 && predicted.length === 0) {
        return (
            <div style={{ height: '350px', padding: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <p style={{ color: 'var(--gray-500)' }}>Datos de predicción no disponibles</p>
            </div>
        );
    }

    const labels = actual.map((_, i) => `Muestra ${i + 1}`);

    const chartData = {
        labels,
        datasets: [
            {
                label: 'Valor Real',
                data: actual,
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 2,
            },
            {
                label: 'Predicción',
                data: predicted,
                borderColor: 'rgb(16, 185, 129)',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 2,
            },
        ],
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
                title: { display: true, text: 'Cantidad' },
            },
            x: {
                display: false,
            },
        },
    };

    return (
        <div style={{ height: '350px', padding: '16px' }}>
            <Line data={chartData} options={options} />
        </div>
    );
}
