import React, { createContext, useContext, useState, useEffect } from 'react';
import { systemService } from '../services';

export const BrandingContext = createContext(null);

export const BrandingProvider = ({ children }) => {
  const [branding, setBranding] = useState({
    institution_name: 'University Student Council',
    institution_logo_url: null,
    primary_color: '#0b6e3b',
    academic_year: '2025-2026',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBranding = async () => {
      try {
        const response = await systemService.getBranding();
        if (response.data) {
          setBranding(response.data);
        }
      } catch (error) {
        console.warn('Failed to load system branding settings:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchBranding();
  }, []);

  return (
    <BrandingContext.Provider value={{ branding, loading }}>
      {children}
    </BrandingContext.Provider>
  );
};
