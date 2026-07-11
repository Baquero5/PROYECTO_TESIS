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

export default function FeatureImportanceChart({ data }) {
    if (!data || !data.features || data.features.length === 0) return null;

    const sorted = [...data.features].sort((a, b) => a.importance - b.importance);

    const chartData = {
        labels: sorted.map(f => f.feature),
        datasets: [{
            label: 'Importancia',
            data: sorted.map(f => f.importance),
            backgroundColor: 'rgba(139, 92, 246, 0.7)',
            borderColor: 'rgb(139, 92, 246)',
            borderWidth: 2,
            borderRadius: 4,
        }],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
            legend: { display: false },
        },
        scales: {
            x: {
                beginAtZero: true,
                title: { display: true, text: 'Importancia' },
            },
        },
    };

    return (
        <div style={{ height: '350px', padding: '16px' }}>
            <Bar data={chartData} options={options} />
        </div>
    );
}
