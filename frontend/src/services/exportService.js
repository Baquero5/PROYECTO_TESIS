import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

const formatDate = () => {
    const now = new Date();
    return now.toISOString().split('T')[0];
};

const getFileName = (prefix, extension) => {
    return `${prefix}_${formatDate()}.${extension}`;
};

export const exportToCSV = (data, columns, filename) => {
    const headers = columns.map(col => col.label);
    const rows = data.map(row => columns.map(col => {
        const value = row[col.key];
        if (typeof value === 'string' && value.includes(',')) {
            return `"${value}"`;
        }
        return value ?? '';
    }));

    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, getFileName(filename, 'csv'));
};

export const exportToExcel = (data, columns, filename, sheetName = 'Datos') => {
    const headers = columns.map(col => col.label);
    const rows = data.map(row => columns.map(col => row[col.key] ?? ''));

    const worksheetData = [headers, ...rows];
    const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);

    worksheet['!cols'] = columns.map(col => ({
        wch: Math.max(col.label.length, 15)
    }));

    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);

    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    saveAs(blob, getFileName(filename, 'xlsx'));
};

export const exportToPDF = (data, columns, filename, title = 'Reporte') => {
    const doc = new jsPDF('l', 'mm', 'a4');

    doc.setFontSize(18);
    doc.text(title, 14, 22);

    doc.setFontSize(10);
    doc.text(`Fecha: ${new Date().toLocaleDateString('es-ES')}`, 14, 30);
    doc.text(`Total registros: ${data.length}`, 14, 36);

    const tableColumns = columns.map(col => col.label);
    const tableRows = data.map(row => columns.map(col => String(row[col.key] ?? '')));

    autoTable(doc, {
        head: [tableColumns],
        body: tableRows,
        startY: 42,
        styles: {
            fontSize: 8,
            cellPadding: 2,
        },
        headStyles: {
            fillColor: [59, 130, 246],
            textColor: 255,
            fontStyle: 'bold',
        },
        alternateRowStyles: {
            fillColor: [249, 250, 251],
        },
    });

    doc.save(getFileName(filename, 'pdf'));
};

export const exportModule = (data, columns, moduleName, format = 'all') => {
    if (data.length === 0) {
        alert('No hay datos para exportar');
        return;
    }

    if (format === 'csv' || format === 'all') {
        exportToCSV(data, columns, moduleName);
    }
    if (format === 'excel' || format === 'all') {
        exportToExcel(data, columns, moduleName);
    }
    if (format === 'pdf' || format === 'all') {
        const titles = {
            inventario: 'Reporte de Inventario',
            ventas: 'Reporte de Ventas',
            prediccion: 'Reporte de Predicciones',
            alertas: 'Reporte de Alertas',
            productos: 'Reporte de Productos',
        };
        exportToPDF(data, columns, moduleName, titles[moduleName] || 'Reporte');
    }
};

export const exportChartAsImage = (chartRef, filename = 'grafico', format = 'png') => {
    if (!chartRef?.current) {
        console.warn('No chart reference provided');
        return;
    }

    try {
        const chart = chartRef.current;
        const mimeType = format === 'jpeg' ? 'image/jpeg' : 'image/png';
        const quality = format === 'jpeg' ? 0.92 : 1.0;
        const image = chart.toBase64Image(mimeType, quality);

        const arr = image.split(',');
        const bstr = atob(arr[1]);
        const n = bstr.length;
        const u8arr = new Uint8Array(n);
        for (let i = 0; i < n; i++) {
            u8arr[i] = bstr.charCodeAt(i);
        }

        const blob = new Blob([u8arr], { type: mimeType });
        const date = new Date().toISOString().split('T')[0];
        const ext = format === 'jpeg' ? 'jpg' : 'png';
        saveAs(blob, `${filename}_${date}.${ext}`);
    } catch (err) {
        console.error('Error exporting chart as image:', err);
    }
};
