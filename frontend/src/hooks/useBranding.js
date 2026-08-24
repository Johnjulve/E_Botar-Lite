import { useContext } from 'react';
import { BrandingContext } from '../contexts/BrandingContext';

export const useBranding = () => {
  const context = useContext(BrandingContext);
  if (!context) {
    return {
      branding: {
        institution_name: 'University Student Council',
        institution_logo_url: null,
        primary_color: '#0b6e3b',
        academic_year: '2025-2026',
      },
      app_name: 'E-Botar Lite',
      loading: false,
    };
  }
  return {
    ...context,
    app_name: context.branding?.institution_name || 'E-Botar Lite',
  };
};

export default useBranding;
