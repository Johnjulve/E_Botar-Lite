import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authService } from '../services';
import { STORAGE_KEYS } from '../constants';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogout = useCallback(() => {
    authService.logout();
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const userData = await authService.getMe();
      const updatedUser = {
        ...userData,
        student_id: userData.profile?.student_id,
        department_code: userData.profile?.department_code,
        department_name: userData.profile?.department_name,
        course_code: userData.profile?.course_code,
        course_name: userData.profile?.course_name,
        year_level: userData.profile?.year_level,
        section: userData.profile?.section,
        avatar_url: userData.profile?.avatar_url,
        is_profile_complete: userData.profile?.is_profile_complete,
      };
      setUser(updatedUser);
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(updatedUser));
      return updatedUser;
    } catch (error) {
      console.error('Failed to refresh user:', error);
      return null;
    }
  }, []);

  const initializeAuth = useCallback(async () => {
    try {
      const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
      const storedUser = localStorage.getItem(STORAGE_KEYS.USER);

      if (token && storedUser) {
        setUser(JSON.parse(storedUser));
        setIsAuthenticated(true);

        try {
          await refreshUser();
        } catch {
          handleLogout();
        }
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      handleLogout();
    } finally {
      setLoading(false);
    }
  }, [handleLogout, refreshUser]);

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  const login = async (username, password) => {
    try {
      const data = await authService.login(username, password);
      setUser(data.user);
      setIsAuthenticated(true);
      return { success: true, user: data.user };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.response?.data?.error || 'Login failed. Please verify credentials.',
      };
    }
  };

  const register = async (formData) => {
    try {
      const data = await authService.register(formData);
      return { success: true, data };
    } catch (error) {
      console.error('Registration error:', error);
      return {
        success: false,
        error: error.response?.data || 'Registration failed. Please check form errors.',
      };
    }
  };

  const isStaffOrAdmin = Boolean(user?.is_staff || user?.is_superuser);
  const isSuperUser = Boolean(user?.is_superuser);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated,
        isStaffOrAdmin,
        isSuperUser,
        login,
        register,
        logout: handleLogout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
