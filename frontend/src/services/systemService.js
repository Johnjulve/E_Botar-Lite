import api from './api';
import { API_ENDPOINTS } from '../constants';

export const DEFAULT_FEATURE_FLAGS = Object.freeze({
  data_export: true,
  user_registration: true,
  google_login: true,
  staff_preview_disabled_features: true,
});

export const DEFAULT_BRANDING = Object.freeze({
  institution_name: 'SURIGAO DEL NORTE',
  institution_name_line2: 'STATE UNIVERSITY',
  institution_logo_url: null,
  app_name: 'E-Botar Lite',
  institution_full_name: 'SURIGAO DEL NORTE STATE UNIVERSITY',
  feature_flags: DEFAULT_FEATURE_FLAGS,
});

export const systemService = {
  getBranding: async () => {
    try {
      const response = await api.get(API_ENDPOINTS.BRANDING);
      const data = response.data || {};
      return {
        ...DEFAULT_BRANDING,
        ...data,
      };
    } catch {
      return { ...DEFAULT_BRANDING };
    }
  },

  getBrandingAssets: async () => {
    try {
      const response = await api.get('/common/branding/assets/');
      return response.data?.assets || [];
    } catch {
      return [];
    }
  },

  activateBrandingAsset: (assetId) =>
    api.post(`/common/branding/assets/${encodeURIComponent(assetId)}/activate/`),

  deleteBrandingAsset: (assetId) =>
    api.delete(`/common/branding/assets/${encodeURIComponent(assetId)}/`),

  getVersion: () => api.get(API_ENDPOINTS.VERSION),

  getSystemLogs: (params = {}) => api.get(API_ENDPOINTS.SYSTEM_LOGS, { params }),

  getAcademicYear: async () => {
    try {
      const response = await api.get('/common/academic-year/');
      return response.data;
    } catch {
      return {
        academic_year: '2025-2026',
        display: 'A.Y 2025-2026',
      };
    }
  },

  updateAcademicYear: async (academicYear) => {
    const response = await api.put('/common/academic-year/', {
      academic_year: academicYear,
    });
    return response.data;
  },

  generateAcademicYearOptions: () => {
    const currentYear = new Date().getFullYear();
    const options = [];
    for (let i = -2; i <= 5; i++) {
      const year1 = currentYear + i;
      const year2 = year1 + 1;
      options.push(`${year1}-${year2}`);
    }
    return options;
  },
};

export const logService = {
  getSystemLogs: (params = {}) => api.get(API_ENDPOINTS.SYSTEM_LOGS, { params }),
};

export default systemService;
