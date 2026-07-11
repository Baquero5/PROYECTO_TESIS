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

export default function ErrorDistribution({ errors = [] }) {
    if (errors.length === 0) {
        return (
            <div style={{ height: '350px', padding: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <p style={{ color: 'var(--gray-500)' }}>Datos de errores no disponibles</p>
            </div>
        );
    }

    const bins = 15;
    const min = Math.min(...errors);
    const max = Math.max(...errors);
    const binWidth = (max - min) / bins;

    const histogram = Array(bins).fill(0);
    errors.forEach(err => {
        const idx = Math.min(Math.floor((err - min) / binWidth), bins - 1);
        histogram[idx]++;
    });

    const labels = histogram.map((_, i) => {
        const start = min + i * binWidth;
        return `${start.toFixed(1)}`;
    });

    const chartData = {
        labels,
        datasets: [{
            label: 'Frecuencia',
            data: histogram,
            backgroundColor: 'rgba(239, 68, 68, 0.6)',
            borderColor: 'rgb(239, 68, 68)',
            borderWidth: 1,
            borderRadius: 4,
        }],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
        },
        scales: {
            y: {
                beginAtZero: true,
                title: { display: true, text: 'Frecuencia' },
            },
            x: {
                title: { display: true, text: 'Error' },
            },
        },
    };

    return (
        <div style={{ height: '350px', padding: '16px' }}>
            <Bar data={chartData} options={options} />
        </div>
    );
}
