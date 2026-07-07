import { useRef } from 'react';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Filler,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler);

export default function SparkLine({ data = [], color = '#10b981', height = 32, width = 80, fillColor }) {
    const chartRef = useRef(null);

    const bg = fillColor || color + '30';

    const chartData = {
        labels: data.map((_, i) => i),
        datasets: [
            {
                data: data,
                borderColor: color,
                backgroundColor: bg,
                fill: true,
                tension: 0.4,
                borderWidth: 1.5,
                pointRadius: 0,
                pointHoverRadius: 0,
            },
        ],
    };

    const options = {
        responsive: false,
        maintainAspectRatio: false,
        animation: {
            duration: 800,
            easing: 'easeOutQuart',
        },
        plugins: {
            legend: { display: false },
            tooltip: { enabled: false },
        },
        scales: {
            x: { display: false },
            y: { display: false },
        },
        elements: {
            point: { radius: 0 },
        },
        layout: {
            padding: 0,
        },
    };

    return (
        <div style={{ width, height, lineHeight: 0 }}>
            <Line ref={chartRef} data={chartData} options={options} width={width} height={height} />
        </div>
    );
}
