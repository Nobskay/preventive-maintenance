import apiClient from './api';

export const dashboardApi = {
  getSummary: () =>
    apiClient.get('/dashboard/summary'),

  getAllKPIs: (days: number = 90) =>
    apiClient.get('/dashboard/kpis', { params: { days } }),

  getMachineKPI: (machineId: number, days: number = 90) =>
    apiClient.get(`/dashboard/kpis/${machineId}`, { params: { days } }),

  getMachineHealth: () =>
    apiClient.get('/dashboard/machine-health'),

  getDowntimeTrends: (days: number = 30, machineId?: number) =>
    apiClient.get('/dashboard/downtime-trends', { params: { days, machine_id: machineId } }),

  getRecommendations: (machineId?: number, status?: string) =>
    apiClient.get('/dashboard/recommendations', { params: { machine_id: machineId, status } }),

  generateRecommendations: () =>
    apiClient.post('/dashboard/generate-recommendations'),
};
