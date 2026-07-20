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
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`;
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

export const exportToPDF = (data, columns, filename, title = 'Reporte', metadata = {}) => {
    const doc = new jsPDF('l', 'mm', 'a4');

    doc.setFontSize(18);
    doc.text(title, 14, 22);

    doc.setFontSize(10);
    let yPos = 30;

    doc.text(`Fecha: ${new Date().toLocaleDateString('es-ES')}`, 14, yPos);
    doc.text(`Total registros: ${data.length}`, 120, yPos);

    if (metadata.fechaInicio) {
        doc.text(`Fecha Inicio: ${metadata.fechaInicio}`, 14, yPos + 6);
    }
    if (metadata.fechaFin) {
        doc.text(`Fecha Fin: ${metadata.fechaFin}`, 120, yPos + 6);
    }
    if (metadata.modelo) {
        doc.text(`Modelo: ${metadata.modelo}`, 14, yPos + 12);
    }

    const startY = metadata.modelo ? yPos + 18 : (metadata.fechaInicio || metadata.fechaFin) ? yPos + 12 : yPos + 6;

    const tableColumns = columns.map(col => col.label);
    const sortedData = [...data].sort((a, b) => {
        const firstCol = columns[0]?.key;
        if (!firstCol) return 0;
        const valA = a[firstCol];
        const valB = b[firstCol];
        if (typeof valA === 'number' && typeof valB === 'number') return valA - valB;
        const idA = String(valA || '').replace('#', '');
        const idB = String(valB || '').replace('#', '');
        return Number(idA) - Number(idB) || idA.localeCompare(idB);
    });
    const tableRows = sortedData.map(row => columns.map(col => String(row[col.key] ?? '')));

    const centerColumns = columns
        .map((col, i) => i)
        .filter(i => {
            const key = columns[i].key;
            return ['id_prediccion', 'demanda_estimada', 'venta_promedio_por_dia', 'precio_venta',
                    'ingreso_esperado', 'ganancia_esperada', 'margen_porcentaje', 'fecha_prediccion'].includes(key);
        });

    const cellStyles = {};
    centerColumns.forEach(i => {
        cellStyles[i] = { halign: 'center' };
    });

    autoTable(doc, {
        head: [tableColumns],
        body: tableRows,
        startY: startY,
        styles: {
            fontSize: 8,
            cellPadding: 2,
        },
        headStyles: {
            fillColor: [59, 130, 246],
            textColor: 255,
            fontStyle: 'bold',
            halign: 'center',
        },
        alternateRowStyles: {
            fillColor: [249, 250, 251],
        },
        columnStyles: cellStyles,
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
