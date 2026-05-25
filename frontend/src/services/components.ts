import apiClient from './api';

export const componentsApi = {
  list: (params?: { machine_id?: number; skip?: number; limit?: number }) =>
    apiClient.get('/components/', { params }),

  get: (id: number) =>
    apiClient.get(`/components/${id}`),

  create: (data: any) =>
    apiClient.post('/components/', data),

  update: (id: number, data: any) =>
    apiClient.put(`/components/${id}`, data),

  delete: (id: number) =>
    apiClient.delete(`/components/${id}`),

  getHealth: (id: number) =>
    apiClient.get(`/components/${id}/health`),
};
