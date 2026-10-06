/**
 * ChangePasswordPage
 * Mandatory password reset page for newly imported students.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Row, Col, Form } from 'react-bootstrap';
import { useAuth } from '../../../hooks/useAuth';
import { useBranding } from '../../../hooks/useBranding';
import { authService } from '../../../services';
import './auth.css';

const ChangePasswordPage = () => {
  const navigate = useNavigate();
  const { app_name } = useBranding();
  const { user } = useAuth();

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);

    try {
      await authService.changePassword(password);
      
      // Update local storage so we don't infinitely redirect
      const storedUser = JSON.parse(localStorage.getItem('user'));
      if (storedUser) {
        storedUser.must_change_password = false;
        localStorage.setItem('user', JSON.stringify(storedUser));
      }
      
      // Force page reload to clear auth state and re-initialize seamlessly,
      // or just navigate to home which will hit AuthContext refresh
      window.location.href = '/';
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to change password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page d-flex align-items-center">
      <Container className="auth-container">
        <Row className="justify-content-center">
          <Col md={8} lg={6} xl={5}>
            <div className="auth-header">
              <h1>Action Required</h1>
              <p>Welcome to {app_name || 'E-Botar Lite'}. Please set a new password to activate your account.</p>
            </div>

            <div className="auth-card">
              {error && (
                <div className="auth-alert alert-danger" role="alert">
                  <i className="fas fa-exclamation-circle me-2"></i>
                  <span>{error}</span>
                </div>
              )}

              <Form onSubmit={handleSubmit} className="auth-form">
                <Form.Group className="mb-3">
                  <Form.Label>New Password</Form.Label>
                  <div className="auth-input-group">
                    <span className="auth-input-icon">
                      <i className="fas fa-lock"></i>
                    </span>
                    <Form.Control
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter new password"
                      required
                    />
                  </div>
                </Form.Group>

                <Form.Group className="mb-4">
                  <Form.Label>Confirm Password</Form.Label>
                  <div className="auth-input-group">
                    <span className="auth-input-icon">
                      <i className="fas fa-check-circle"></i>
                    </span>
                    <Form.Control
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Confirm new password"
                      required
                    />
                  </div>
                </Form.Group>

                <button
                  type="submit"
                  className="auth-btn auth-btn-primary w-100"
                  disabled={loading}
                >
                  {loading ? (
                    <span><i className="fas fa-spinner fa-spin me-2"></i>Updating...</span>
                  ) : (
                    'Update Password'
                  )}
                </button>
              </Form>
            </div>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default ChangePasswordPage;
