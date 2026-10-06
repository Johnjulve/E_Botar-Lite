import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from '../components/ProtectedRoute';

// Auth Pages
import LoginPage from '../modules/auth/pages/LoginPage';
import RegisterPage from '../modules/auth/pages/RegisterPage';
import ChangePasswordPage from '../modules/auth/pages/ChangePasswordPage';

// Election Pages
import ElectionListPage from '../modules/elections/pages/ElectionListPage';
import ElectionDetailsPage from '../modules/elections/pages/ElectionDetailsPage';

// Candidate Pages
import CandidateListPage from '../modules/candidates/pages/CandidateListPage';
import CandidateProfilePage from '../modules/candidates/pages/CandidateProfilePage';

// Voting Pages
import VotingPage from '../modules/voting/pages/VotingPage';
import MyVotesPage from '../modules/voting/pages/MyVotesPage';
import VerifyReceiptPage from '../modules/voting/pages/VerifyReceiptPage';

// Results Pages
import ResultsDetailsPage from '../modules/results/pages/ResultsDetailsPage';

// Profile Pages
import ProfilePage from '../modules/profile/pages/ProfilePage';
import ProfileEditPage from '../modules/profile/pages/ProfileEditPage';
import DashboardPage from '../modules/profile/pages/DashboardPage';

// Admin Pages
import {
  AdminDashboardPage,
  CandidateManagementPage,
  ElectionManagementPage,
  ElectionFormPage,
  PositionManagementPage,
  PartyManagementPage,
  ProgramManagementPage,
  UserManagementPage,
  VotingStatusPage,
  ReceiptAuditPage,
  SystemLogsPage,
} from '../modules/admin/pages';

import { useToast } from '../contexts/ToastContext';
import { useEffect } from 'react';

const AppRoutes = () => {
  const { addToast } = useToast();

  useEffect(() => {
    window.alert = (msg) => {
      addToast(msg, 'info');
    };
  }, [addToast]);

  return (
    <Routes>
      {/* Public Pages */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/" element={<DashboardPage />} />
      <Route path="/elections" element={<ElectionListPage />} />
      <Route path="/elections/:id" element={<ElectionDetailsPage />} />
      <Route path="/candidates" element={<CandidateListPage />} />
      <Route path="/candidates/:id" element={<CandidateProfilePage />} />
      <Route path="/results/:id" element={<ResultsDetailsPage />} />
      <Route path="/verify-receipt" element={<VerifyReceiptPage />} />

      <Route
        path="/change-password"
        element={
          <ProtectedRoute>
            <ChangePasswordPage />
          </ProtectedRoute>
        }
      />

      {/* Protected Student / Voter Pages */}
      <Route
        path="/vote/:id"
        element={
          <ProtectedRoute>
            <VotingPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/my-votes"
        element={
          <ProtectedRoute>
            <MyVotesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile/edit"
        element={
          <ProtectedRoute>
            <ProfileEditPage />
          </ProtectedRoute>
        }
      />

      {/* Protected Admin Pages */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute requireStaff={true}>
            <AdminDashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/elections"
        element={
          <ProtectedRoute requireStaff={true}>
            <ElectionManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/elections/new"
        element={
          <ProtectedRoute requireStaff={true}>
            <ElectionFormPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/elections/:id/edit"
        element={
          <ProtectedRoute requireStaff={true}>
            <ElectionFormPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/candidates"
        element={
          <ProtectedRoute requireStaff={true}>
            <CandidateManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/positions"
        element={
          <ProtectedRoute requireStaff={true}>
            <PositionManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/parties"
        element={
          <ProtectedRoute requireStaff={true}>
            <PartyManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/programs"
        element={
          <ProtectedRoute requireStaff={true}>
            <ProgramManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/users"
        element={
          <ProtectedRoute requireStaff={true}>
            <UserManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/voting-status"
        element={
          <ProtectedRoute requireStaff={true}>
            <VotingStatusPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/receipt-audit"
        element={
          <ProtectedRoute requireStaff={true}>
            <ReceiptAuditPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/logs"
        element={
          <ProtectedRoute requireStaff={true}>
            <SystemLogsPage />
          </ProtectedRoute>
        }
      />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;
