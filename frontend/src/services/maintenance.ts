import apiClient from './api';

export const maintenanceApi = {
  list: (params?: { machine_id?: number; component_id?: number; event_type?: string; skip?: number; limit?: number }) =>
    apiClient.get('/maintenance-events/', { params }),

  get: (id: number) =>
    apiClient.get(`/maintenance-events/${id}`),

  create: (data: any) =>
    apiClient.post('/maintenance-events/', data),

  update: (id: number, data: any) =>
    apiClient.put(`/maintenance-events/${id}`, data),

  delete: (id: number) =>
    apiClient.delete(`/maintenance-events/${id}`),
};
