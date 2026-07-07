import { useState } from 'react';
import { saveAs } from 'file-saver';

export default function ChartExportButton({ chartRef, filename = 'grafico' }) {
    const [exporting, setExporting] = useState(false);
    const [showMenu, setShowMenu] = useState(false);

    const handleExport = async (format) => {
        if (!chartRef?.current) return;
        setExporting(true);
        setShowMenu(false);

        try {
            const chart = chartRef.current;

            if (format === 'png') {
                const image = chart.toBase64Image('image/png', 1.0);
                const arr = image.split(',');
                const mime = arr[0].match(/:(.*?);/)[1];
                const bstr = atob(arr[1]);
                const n = bstr.length;
                const u8arr = new Uint8Array(n);
                for (let i = 0; i < n; i++) u8arr[i] = bstr.charCodeAt(i);
                const blob = new Blob([u8arr], { type: mime });
                const date = new Date().toISOString().split('T')[0];
                saveAs(blob, `${filename}_${date}.png`);
            } else if (format === 'jpeg') {
                const image = chart.toBase64Image('image/jpeg', 0.92);
                const arr = image.split(',');
                const mime = arr[0].match(/:(.*?);/)[1];
                const bstr = atob(arr[1]);
                const n = bstr.length;
                const u8arr = new Uint8Array(n);
                for (let i = 0; i < n; i++) u8arr[i] = bstr.charCodeAt(i);
                const blob = new Blob([u8arr], { type: mime });
                const date = new Date().toISOString().split('T')[0];
                saveAs(blob, `${filename}_${date}.jpg`);
            }
        } catch (err) {
            console.error('Error exporting chart:', err);
        } finally {
            setExporting(false);
        }
    };

    return (
        <div className="chart-export-wrapper" style={{ position: 'relative', display: 'inline-block' }}>
            <button
                className="chart-export-btn"
                onClick={() => setShowMenu(!showMenu)}
                disabled={exporting}
                title="Exportar gráfico"
            >
                {exporting ? '⏳' : '📥'}
            </button>

            {showMenu && (
                <>
                    <div
                        style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 99 }}
                        onClick={() => setShowMenu(false)}
                    />
                    <div className="chart-export-menu">
                        <button onClick={() => handleExport('png')}>
                            🖼️ PNG (alta calidad)
                        </button>
                        <button onClick={() => handleExport('jpeg')}>
                            📷 JPEG (ligero)
                        </button>
                    </div>
                </>
            )}
        </div>
    );
}
