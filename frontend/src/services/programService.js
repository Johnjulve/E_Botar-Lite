/**
 * Program Service
 * Handles all program (department/course) related API calls
 */

import api from './api';
import { API_ENDPOINTS } from '../constants';

export const programService = {
  // Get all programs
  getAll: (params = {}) => api.get(API_ENDPOINTS.PROGRAMS, { params }),
  getAllPrograms: (params = {}) => api.get(API_ENDPOINTS.PROGRAMS, { params }),

  // Get program by ID
  getById: (id) => api.get(`${API_ENDPOINTS.PROGRAMS}${id}/`),

  // Get departments only
  getDepartments: () => api.get(API_ENDPOINTS.DEPARTMENTS),

  // Get courses only
  getCourses: (departmentCode = null) => {
    const params = departmentCode ? { department: departmentCode } : {};
    return api.get(API_ENDPOINTS.COURSES, { params });
  },

  // Create program
  create: (programData) => api.post(API_ENDPOINTS.PROGRAMS, programData),
  createProgram: (programData) => api.post(API_ENDPOINTS.PROGRAMS, programData),

  // Update program
  update: (id, programData) => api.put(`${API_ENDPOINTS.PROGRAMS}${id}/`, programData),
  updateProgram: (id, programData) => api.put(`${API_ENDPOINTS.PROGRAMS}${id}/`, programData),

  // Delete program
  delete: (id) => api.delete(`${API_ENDPOINTS.PROGRAMS}${id}/`),
  deleteProgram: (id) => api.delete(`${API_ENDPOINTS.PROGRAMS}${id}/`),

  // Import programs from CSV (supports preview-only validation mode)
  importCSV: (file, options = {}) => {
    const { previewOnly = false } = options;
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`${API_ENDPOINTS.PROGRAMS}import-csv/`, formData, {
      params: {
        preview_only: previewOnly,
      },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Export programs to CSV
  exportCSV: (programType = null) => {
    const params = programType ? { program_type: programType } : {};
    return api.get(`${API_ENDPOINTS.PROGRAMS}export-csv/`, {
      params,
      responseType: 'blob',
    });
  },
};

export default programService;
