import apiClient from './api';

export const downtimeApi = {
  list: (params?: { machine_id?: number; severity?: string; unplanned_only?: boolean; skip?: number; limit?: number }) =>
    apiClient.get('/downtime/', { params }),

  get: (id: number) =>
    apiClient.get(`/downtime/${id}`),

  create: (data: any) =>
    apiClient.post('/downtime/', data),

  update: (id: number, data: any) =>
    apiClient.put(`/downtime/${id}`, data),

  delete: (id: number) =>
    apiClient.delete(`/downtime/${id}`),

  getTrends: (days: number = 30, machine_id?: number) =>
    apiClient.get('/downtime/trends/', { params: { days, machine_id } }),
};
