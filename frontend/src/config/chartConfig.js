const MONTHS_ES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

export const formatCurrency = (value) => {
    if (value == null || isNaN(value)) return '$0.00';
    return '$' + Number(value).toLocaleString('es-EC', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

export const formatNumber = (value) => {
    if (value == null || isNaN(value)) return '0';
    return Number(value).toLocaleString('es-EC');
};

export const formatPercent = (value) => {
    if (value == null || isNaN(value)) return '0%';
    return Number(value).toFixed(1) + '%';
};

export const formatDateShort = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return `${d.getDate()} ${MONTHS_ES[d.getMonth()]}`;
};

export const formatDateFull = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return `${d.getDate()} ${MONTHS_ES[d.getMonth()]} ${d.getFullYear()}`;
};

export const CHART_COLORS = {
    blue: { main: '#3b82f6', bg: 'rgba(59, 130, 246, 0.15)', border: 'rgba(59, 130, 246, 0.6)' },
    green: { main: '#10b981', bg: 'rgba(16, 185, 129, 0.15)', border: 'rgba(16, 185, 129, 0.6)' },
    yellow: { main: '#f59e0b', bg: 'rgba(245, 158, 11, 0.15)', border: 'rgba(245, 158, 11, 0.6)' },
    red: { main: '#ef4444', bg: 'rgba(239, 68, 68, 0.15)', border: 'rgba(239, 68, 68, 0.6)' },
    purple: { main: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.15)', border: 'rgba(139, 92, 246, 0.6)' },
    cyan: { main: '#06b6d4', bg: 'rgba(6, 182, 212, 0.15)', border: 'rgba(6, 182, 212, 0.6)' },
    pink: { main: '#ec4899', bg: 'rgba(236, 72, 153, 0.15)', border: 'rgba(236, 72, 153, 0.6)' },
    orange: { main: '#f97316', bg: 'rgba(249, 115, 22, 0.15)', border: 'rgba(249, 115, 22, 0.6)' },
};

export const PALETTE = [
    CHART_COLORS.blue.main,
    CHART_COLORS.green.main,
    CHART_COLORS.purple.main,
    CHART_COLORS.yellow.main,
    CHART_COLORS.red.main,
    CHART_COLORS.cyan.main,
    CHART_COLORS.pink.main,
    CHART_COLORS.orange.main,
];

export const baseTooltipConfig = {
    backgroundColor: 'rgba(15, 23, 42, 0.95)',
    titleColor: '#f8fafc',
    bodyColor: '#e2e8f0',
    borderColor: 'rgba(148, 163, 184, 0.3)',
    borderWidth: 1,
    cornerRadius: 10,
    padding: { top: 10, bottom: 10, left: 14, right: 14 },
    titleFont: { size: 13, weight: 'bold', family: 'Inter, system-ui, sans-serif' },
    bodyFont: { size: 12, family: 'Inter, system-ui, sans-serif' },
    titleMarginBottom: 8,
    bodySpacing: 6,
    boxPadding: 4,
    usePointStyle: true,
    displayColors: true,
};

export const baseAnimationConfig = {
    duration: 900,
    easing: 'easeOutQuart',
};

export const hoverAnimationConfig = {
    mode: 'index',
    intersect: false,
    animation: { duration: 200 },
};

export const baseChartOptions = ({
    titleText,
    xTitle,
    yTitle,
    xDisplay = true,
    yDisplay = true,
    yBeginAtZero = true,
    showLegend = true,
    legendPosition = 'top',
    formatYAs = 'number',
    maxXTicks = 15,
    isHorizontal = false,
} = {}) => ({
    responsive: true,
    maintainAspectRatio: false,
    animation: baseAnimationConfig,
    hover: hoverAnimationConfig,
    plugins: {
        legend: {
            display: showLegend,
            position: legendPosition,
            labels: {
                usePointStyle: true,
                padding: 16,
                font: { size: 12, family: 'Inter, system-ui, sans-serif' },
            },
        },
        title: {
            display: !!titleText,
            text: titleText || '',
            font: { size: 14, weight: '600', family: 'Inter, system-ui, sans-serif' },
            padding: { bottom: 12 },
        },
        tooltip: {
            ...baseTooltipConfig,
            callbacks: {
                title: (items) => {
                    if (!items.length) return '';
                    return items[0].label || '';
                },
                label: (context) => {
                    const label = context.dataset.label || '';
                    const value = context.parsed[isHorizontal ? 'x' : 'y'];
                    if (formatYAs === 'currency') {
                        return ` ${label}: ${formatCurrency(value)}`;
                    }
                    return ` ${label}: ${formatNumber(value)}`;
                },
            },
        },
    },
    scales: {
        x: {
            display: xDisplay,
            title: {
                display: !!xTitle,
                text: xTitle || '',
                font: { size: 12, weight: '500', family: 'Inter, system-ui, sans-serif' },
            },
            ticks: {
                maxTicksLimit: maxXTicks,
                maxRotation: 45,
                minRotation: 45,
                font: { size: 11, family: 'Inter, system-ui, sans-serif' },
            },
            grid: { color: 'rgba(148, 163, 184, 0.1)' },
        },
        y: {
            display: yDisplay,
            beginAtZero: yBeginAtZero,
            title: {
                display: !!yTitle,
                text: yTitle || '',
                font: { size: 12, weight: '500', family: 'Inter, system-ui, sans-serif' },
            },
            ticks: {
                font: { size: 11, family: 'Inter, system-ui, sans-serif' },
                callback: (value) => {
                    if (formatYAs === 'currency') return formatCurrency(value);
                    return formatNumber(value);
                },
            },
            grid: { color: 'rgba(148, 163, 184, 0.1)' },
        },
    },
    interaction: {
        mode: 'nearest',
        axis: isHorizontal ? 'y' : 'x',
        intersect: false,
    },
});

export const doughnutOptions = ({ showLegend = true, legendPosition = 'bottom' } = {}) => ({
    responsive: true,
    maintainAspectRatio: false,
    animation: { ...baseAnimationConfig, animateRotate: true, animateScale: true },
    cutout: '60%',
    plugins: {
        legend: {
            display: showLegend,
            position: legendPosition,
            labels: {
                usePointStyle: true,
                padding: 14,
                font: { size: 12, family: 'Inter, system-ui, sans-serif' },
            },
        },
        tooltip: {
            ...baseTooltipConfig,
            callbacks: {
                label: (context) => {
                    const label = context.label || '';
                    const value = context.parsed || 0;
                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                    const pct = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                    return ` ${label}: ${formatNumber(value)} (${pct}%)`;
                },
            },
        },
    },
});

export const barOptions = ({
    titleText,
    xTitle,
    yTitle,
    showLegend = false,
    isHorizontal = false,
    formatYAs = 'number',
    stacked = false,
} = {}) => ({
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: isHorizontal ? 'y' : 'x',
    animation: baseAnimationConfig,
    hover: hoverAnimationConfig,
    plugins: {
        legend: {
            display: showLegend,
            position: 'top',
            labels: {
                usePointStyle: true,
                padding: 16,
                font: { size: 12, family: 'Inter, system-ui, sans-serif' },
            },
        },
        title: {
            display: !!titleText,
            text: titleText || '',
            font: { size: 14, weight: '600', family: 'Inter, system-ui, sans-serif' },
        },
        tooltip: {
            ...baseTooltipConfig,
            callbacks: {
                label: (context) => {
                    const label = context.dataset.label || '';
                    const value = context.parsed[isHorizontal ? 'x' : 'y'];
                    if (formatYAs === 'currency') {
                        return ` ${label}: ${formatCurrency(value)}`;
                    }
                    return ` ${label}: ${formatNumber(value)}`;
                },
            },
        },
    },
    scales: {
        x: {
            stacked,
            display: true,
            title: {
                display: !!xTitle,
                text: xTitle || '',
                font: { size: 12, weight: '500', family: 'Inter, system-ui, sans-serif' },
            },
            ticks: {
                font: { size: 11, family: 'Inter, system-ui, sans-serif' },
                maxRotation: isHorizontal ? 0 : 45,
            },
            grid: { display: !isHorizontal, color: 'rgba(148, 163, 184, 0.1)' },
        },
        y: {
            stacked,
            display: true,
            beginAtZero: true,
            title: {
                display: !!yTitle,
                text: yTitle || '',
                font: { size: 12, weight: '500', family: 'Inter, system-ui, sans-serif' },
            },
            ticks: {
                font: { size: 11, family: 'Inter, system-ui, sans-serif' },
                callback: (value) => {
                    if (formatYAs === 'currency') return formatCurrency(value);
                    return formatNumber(value);
                },
            },
            grid: { color: isHorizontal ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.1)' },
        },
    },
    interaction: {
        mode: 'nearest',
        intersect: false,
    },
});

export const predictionTooltipCallbacks = {
    title: (items) => {
        if (!items.length) return '';
        const raw = items[0].label;
        return formatDateFull(raw) || raw;
    },
    label: (context) => {
        const label = context.dataset.label || '';
        const value = context.parsed.y;
        return ` ${label}: ${formatNumber(value)} unidades`;
    },
    afterBody: (items) => {
        if (!items.length) return '';
        const idx = items[0].dataIndex;
        const chart = items[0].chart;
        const confidenceMin = chart.data.datasets.find(d => d.label === 'Confianza Min');
        const confidenceMax = chart.data.datasets.find(d => d.label === 'Confianza Max');
        if (confidenceMin && confidenceMax) {
            const minVal = confidenceMin.data[idx];
            const maxVal = confidenceMax.data[idx];
            if (minVal != null && maxVal != null) {
                return ` Rango: ${formatNumber(minVal)} - ${formatNumber(maxVal)}`;
            }
        }
        return '';
    },
};

export const comparisonTooltipCallbacks = {
    title: (items) => {
        if (!items.length) return '';
        const raw = items[0].label;
        return formatDateFull(raw) || raw;
    },
    label: (context) => {
        const label = context.dataset.label || '';
        const value = context.parsed.y;
        return ` ${label}: ${formatNumber(value)} unidades`;
    },
};

export const revenueTooltipCallbacks = {
    title: (items) => {
        if (!items.length) return '';
        const raw = items[0].label;
        return formatDateFull(raw) || raw;
    },
    label: (context) => {
        const label = context.dataset.label || '';
        const value = context.parsed.y;
        if (label.toLowerCase().includes('ingreso') || label.toLowerCase().includes('ganancia') || label.toLowerCase().includes('costo')) {
            return ` ${label}: ${formatCurrency(value)}`;
        }
        return ` ${label}: ${formatNumber(value)} unidades`;
    },
};
