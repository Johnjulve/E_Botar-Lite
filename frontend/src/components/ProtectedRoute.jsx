/**
 * ProtectedRoute Component
 * Route wrapper that requires authentication
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import LoadingSpinner from './common/LoadingSpinner';

const ProtectedRoute = ({ children, requireAdmin = false, requireStaff = false }) => {
  const { user, isAuthenticated, isAdmin, isStaffOrAdmin, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <LoadingSpinner fullScreen text="Verifying authentication..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Intercept for mandatory password reset
  if (user?.must_change_password && location.pathname !== '/change-password') {
    return <Navigate to="/change-password" replace />;
  }

  // Admin-only routes (superuser only)
  if (requireAdmin && !isAdmin) {
    return <Navigate to="/" replace />;
  }

  // Staff routes (staff or admin can access)
  if (requireStaff && !isStaffOrAdmin) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default ProtectedRoute;
