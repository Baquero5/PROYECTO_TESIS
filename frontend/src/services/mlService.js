import api from './api';

const mlMetricsService = {
  getAll: () => api.get('/ml-metrics'),
  getComparativa: () => api.get('/ml-metrics/comparativa'),
  getEnsemble: () => api.get('/ml-metrics/ensemble'),
  getFeatures: () => api.get('/ml-metrics/features'),
  getCharts: () => api.get('/ml-metrics/charts'),
  getChart: (chartId) => api.get(`/ml-metrics/charts/${chartId}`, { responseType: 'blob' }),
  getSummary: () => api.get('/ml-metrics/summary'),
  getReporte: () => api.get('/ml-metrics/reporte'),
};

export default mlMetricsService;
