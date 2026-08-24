import api from './api';
import { API_ENDPOINTS } from '../constants';

export const candidateService = {
  getAll: (params = {}) => api.get(API_ENDPOINTS.CANDIDATES, { params }),
  getCandidatesByElection: (electionId) => api.get(API_ENDPOINTS.CANDIDATES, { params: { election_id: electionId } }),
  getByElectionCompact: (electionId) => api.get(API_ENDPOINTS.CANDIDATES, { params: { election_id: electionId } }),
  getById: (id) => api.get(`${API_ENDPOINTS.CANDIDATES}${id}/`),
  create: (formData) => api.post(API_ENDPOINTS.CANDIDATES, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  update: (id, formData) => api.put(`${API_ENDPOINTS.CANDIDATES}${id}/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  delete: (id) => api.delete(`${API_ENDPOINTS.CANDIDATES}${id}/`),
  toggleActive: (id) => api.post(`${API_ENDPOINTS.CANDIDATES}${id}/toggle_active/`),
};

export default candidateService;
