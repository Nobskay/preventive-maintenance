import apiClient from './api';

export const machinesApi = {
  list: (params?: { status?: string; machine_type?: string; skip?: number; limit?: number }) =>
    apiClient.get('/machines/', { params }),

  get: (id: number) =>
    apiClient.get(`/machines/${id}`),

  create: (data: any) =>
    apiClient.post('/machines/', data),

  update: (id: number, data: any) =>
    apiClient.put(`/machines/${id}`, data),

  delete: (id: number) =>
    apiClient.delete(`/machines/${id}`),

  getHealth: (id: number) =>
    apiClient.get(`/machines/${id}/health`),
};
