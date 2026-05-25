import apiClient from './api';

export const runtimeApi = {
  list: (machineId: number, params?: { skip?: number; limit?: number }) =>
    apiClient.get(`/runtime/${machineId}`, { params }),

  getLatest: (machineId: number) =>
    apiClient.get(`/runtime/${machineId}/latest`),

  create: (data: any) =>
    apiClient.post('/runtime/', data),

  createBatch: (data: any) =>
    apiClient.post('/runtime/batch', data),

  importCSV: (machineId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post(`/runtime/${machineId}/import-csv`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};
