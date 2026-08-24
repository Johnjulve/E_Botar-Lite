import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return {
    ...context,
    isAdmin: Boolean(context.user?.is_superuser),
    isStaff: Boolean(context.user?.is_staff),
    isStaffOrAdmin: Boolean(context.user?.is_staff || context.user?.is_superuser),
  };
};

export default useAuth;
