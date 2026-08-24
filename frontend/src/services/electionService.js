import api from './api';
import { API_ENDPOINTS } from '../constants';

export const electionService = {
  getAll: (params = {}) => api.get(API_ENDPOINTS.ELECTIONS, { params }),
  getActive: () => api.get(API_ENDPOINTS.ACTIVE_ELECTIONS),
  getActiveCompact: () => api.get(API_ENDPOINTS.ACTIVE_ELECTIONS),
  getUpcoming: () => api.get(API_ENDPOINTS.UPCOMING_ELECTIONS),
  getFinished: () => api.get(API_ENDPOINTS.FINISHED_ELECTIONS),
  getFinishedCompact: () => api.get(API_ENDPOINTS.FINISHED_ELECTIONS),
  getById: (id) => api.get(`${API_ENDPOINTS.ELECTIONS}${id}/`),
  create: (data) => api.post(API_ENDPOINTS.ELECTIONS, data),
  update: (id, data) => api.put(`${API_ENDPOINTS.ELECTIONS}${id}/`, data),
  delete: (id) => api.delete(`${API_ENDPOINTS.ELECTIONS}${id}/`),
  togglePause: (id) => api.post(`${API_ENDPOINTS.ELECTIONS}${id}/toggle_pause/`),

  // Positions
  getPositions: () => api.get(API_ENDPOINTS.POSITIONS),
  createPosition: (data) => api.post(API_ENDPOINTS.POSITIONS, data),
  updatePosition: (id, data) => api.put(`${API_ENDPOINTS.POSITIONS}${id}/`, data),
  deletePosition: (id) => api.delete(`${API_ENDPOINTS.POSITIONS}${id}/`),

  // Parties
  getParties: () => api.get(API_ENDPOINTS.PARTIES),
  createParty: (formData) => api.post(API_ENDPOINTS.PARTIES, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  updateParty: (id, formData) => api.put(`${API_ENDPOINTS.PARTIES}${id}/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  deleteParty: (id) => api.delete(`${API_ENDPOINTS.PARTIES}${id}/`),
};

export default electionService;
