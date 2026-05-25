import apiClient from './api';

export const alertsApi = {
  list: (params?: { machine_id?: number; active_only?: boolean; severity?: string; skip?: number; limit?: number }) =>
    apiClient.get('/alerts/', { params }),

  get: (id: number) =>
    apiClient.get(`/alerts/${id}`),

  create: (data: any) =>
    apiClient.post('/alerts/', data),

  resolve: (id: number, data?: { resolution_notes?: string }) =>
    apiClient.post(`/alerts/${id}/resolve`, data || {}),

  generate: () =>
    apiClient.post('/alerts/generate'),
};
