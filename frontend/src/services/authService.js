import api from './api';
import { API_ENDPOINTS, STORAGE_KEYS } from '../constants';

export const authService = {
  login: async (username, password) => {
    const response = await api.post(API_ENDPOINTS.LOGIN, { username, password });
    if (response.data.access) {
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, response.data.access);
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, response.data.refresh);
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.data.user));
    }
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post(API_ENDPOINTS.REGISTER, userData);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER);
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem(STORAGE_KEYS.USER);
    return userStr ? JSON.parse(userStr) : null;
  },

  getMe: async () => {
    const response = await api.get(API_ENDPOINTS.ME);
    return response.data;
  },

  updateProfile: async (profileData) => {
    const isFormData = profileData instanceof FormData;
    const response = await api.patch(`${API_ENDPOINTS.PROFILES}me/`, profileData, {
      headers: isFormData ? { 'Content-Type': 'multipart/form-data' } : {},
    });
    return response.data;
  },

  getUserCount: () => api.get(API_ENDPOINTS.USER_COUNTS),

  getStudentCount: () => api.get(API_ENDPOINTS.USER_COUNTS),

  getUsers: (params = {}) => api.get(API_ENDPOINTS.USERS, { params }),

  getAllProfiles: (params = {}) => api.get(API_ENDPOINTS.USERS, { params }),

  getDirectory: (params = {}) => api.get(API_ENDPOINTS.USERS, { params }),

  getUserProfile: (profileId) => api.get(`${API_ENDPOINTS.USERS}${profileId}/`),

  updateUserProfile: (profileId, data) => api.patch(`${API_ENDPOINTS.USERS}${profileId}/`, data),

  getDepartments: () => api.get(API_ENDPOINTS.DEPARTMENTS),

  getCourses: () => api.get(API_ENDPOINTS.COURSES),

  getCoursesByDepartment: (dept) => api.get(API_ENDPOINTS.COURSES, { params: { department: dept } }),

  toggleUserActive: (userId) => api.post(`${API_ENDPOINTS.USERS}${userId}/toggle_active/`),

  toggleUserStaff: (userId) => api.post(`${API_ENDPOINTS.USERS}${userId}/toggle_staff/`),

  resetUserPassword: (userId, newPassword) => api.post(`${API_ENDPOINTS.USERS}${userId}/reset_password/`, { new_password: newPassword }),

  setUserVerified: (userId, isVerified) => api.patch(`${API_ENDPOINTS.USERS}${userId}/`, { is_verified: isVerified }),

  updateUserRole: (userId, role) => api.post(`${API_ENDPOINTS.USERS}${userId}/set_role/`, { role }),

  deleteUser: (userId) => api.delete(`${API_ENDPOINTS.USERS}${userId}/`),
};

export default authService;
