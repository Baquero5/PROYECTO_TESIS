import { useState } from 'react';
import { exportToCSV, exportToExcel, exportToPDF } from '../services/exportService';

export default function ExportButtons({ data, columns, moduleName, title }) {
    const [showDropdown, setShowDropdown] = useState(false);

    if (!data || data.length === 0) return null;

    const handleExport = (format) => {
        const titles = {
            inventario: 'Reporte de Inventario',
            ventas: 'Reporte de Ventas',
            prediccion: 'Reporte de Predicciones',
            alertas: 'Reporte de Alertas',
            productos: 'Reporte de Productos',
        };
        const pdfTitle = titles[moduleName] || title || 'Reporte';

        switch (format) {
            case 'csv':
                exportToCSV(data, columns, moduleName);
                break;
            case 'excel':
                exportToExcel(data, columns, moduleName);
                break;
            case 'pdf':
                exportToPDF(data, columns, moduleName, pdfTitle);
                break;
        }
        setShowDropdown(false);
    };

    return (
        <div style={{ position: 'relative', display: 'inline-block' }}>
            <button
                className="btn btn-outline"
                onClick={() => setShowDropdown(!showDropdown)}
                style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
                📥 Exportar
            </button>

            {showDropdown && (
                <>
                    <div
                        style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 99 }}
                        onClick={() => setShowDropdown(false)}
                    />
                    <div style={{
                        position: 'absolute',
                        top: '100%',
                        right: 0,
                        marginTop: '4px',
                        background: 'var(--gray-100)',
                        borderRadius: '8px',
                        boxShadow: 'var(--shadow-lg)',
                        border: '1px solid var(--gray-200)',
                        zIndex: 100,
                        minWidth: '160px',
                        overflow: 'hidden',
                    }}>
                        <button
                            onClick={() => handleExport('csv')}
                            style={{
                                display: 'block',
                                width: '100%',
                                padding: '10px 16px',
                                border: 'none',
                                background: 'none',
                                textAlign: 'left',
                                cursor: 'pointer',
                                fontSize: '0.85rem',
                                borderBottom: '1px solid var(--gray-200)',
                            }}
                            onMouseEnter={(e) => e.target.style.background = 'var(--gray-200)'}
                            onMouseLeave={(e) => e.target.style.background = 'none'}
                        >
                            📄 CSV
                        </button>
                        <button
                            onClick={() => handleExport('excel')}
                            style={{
                                display: 'block',
                                width: '100%',
                                padding: '10px 16px',
                                border: 'none',
                                background: 'none',
                                textAlign: 'left',
                                cursor: 'pointer',
                                fontSize: '0.85rem',
                                borderBottom: '1px solid var(--gray-200)',
                            }}
                            onMouseEnter={(e) => e.target.style.background = 'var(--gray-200)'}
                            onMouseLeave={(e) => e.target.style.background = 'none'}
                        >
                            📊 Excel
                        </button>
                        <button
                            onClick={() => handleExport('pdf')}
                            style={{
                                display: 'block',
                                width: '100%',
                                padding: '10px 16px',
                                border: 'none',
                                background: 'none',
                                textAlign: 'left',
                                cursor: 'pointer',
                                fontSize: '0.85rem',
                            }}
                            onMouseEnter={(e) => e.target.style.background = 'var(--gray-200)'}
                            onMouseLeave={(e) => e.target.style.background = 'none'}
                        >
                            📕 PDF
                        </button>
                    </div>
                </>
            )}
        </div>
    );
}
