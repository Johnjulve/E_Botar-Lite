/**
 * LoginPage
 * User authentication page matching main design
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Form } from 'react-bootstrap';
import { LoadingSpinner } from '../../../components/common';
import { useAuth } from '../../../hooks/useAuth';
import { useBranding } from '../../../hooks/useBranding';
import { ROUTES } from '../../../constants';
import './auth.css';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();
  const { branding, app_name } = useBranding();

  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.username.trim()) {
      newErrors.username = 'Username or email is required';
    }
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setLoading(true);

    try {
      const result = await login(formData.username.trim(), formData.password);
      if (result.success) {
        navigate('/');
      } else {
        setErrorMessage(result.error || 'Invalid credentials.');
      }
    } catch {
      setErrorMessage('An unexpected error occurred. Please try again.');
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
              <h1>Welcome Back</h1>
              <p>Sign in to continue to {app_name || 'E-Botar Lite'}</p>
            </div>

            <div className="auth-card">
              {errorMessage && (
                <div className="auth-alert alert-danger" role="alert">
                  <i className="fas fa-exclamation-circle me-2"></i>
                  <span>{errorMessage}</span>
                  <button
                    type="button"
                    className="btn-close ms-auto"
                    onClick={() => setErrorMessage('')}
                    aria-label="Close"
                  ></button>
                </div>
              )}

              <Form onSubmit={handleSubmit} className="auth-form">
                <Form.Group className="form-group mb-3">
                  <Form.Label className="d-flex align-items-center gap-2">
                    <i className="fas fa-user text-muted"></i>
                    <span>Username or Email</span>
                  </Form.Label>
                  <Form.Control
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    isInvalid={!!errors.username}
                    placeholder="Enter your username or email"
                    disabled={loading}
                  />
                  {errors.username && (
                    <div className="invalid-feedback d-block">{errors.username}</div>
                  )}
                </Form.Group>

                <Form.Group className="form-group mb-4">
                  <Form.Label className="d-flex align-items-center gap-2">
                    <i className="fas fa-lock text-muted"></i>
                    <span>Password</span>
                  </Form.Label>
                  <div className="auth-password-wrap">
                    <Form.Control
                      type={showPassword ? 'text' : 'password'}
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      isInvalid={!!errors.password}
                      placeholder="Enter your password"
                      disabled={loading}
                    />
                    <button
                      type="button"
                      className="auth-password-toggle"
                      onClick={() => setShowPassword((p) => !p)}
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      tabIndex={-1}
                    >
                      <i className={showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'}></i>
                    </button>
                  </div>
                  {errors.password && (
                    <div className="invalid-feedback d-block">{errors.password}</div>
                  )}
                </Form.Group>

                <button
                  type="submit"
                  className={`auth-submit-btn ${loading ? 'auth-loading' : ''}`}
                  disabled={loading}
                >
                  {loading && <span className="auth-spinner me-2"></span>}
                  {loading ? 'Signing in...' : 'Sign In'}
                </button>
              </Form>


            </div>

            <div className="auth-footer text-center mt-4">
              <p className="text-muted small">
                <i className="fas fa-shield-alt me-1 text-success"></i>
                Secure, Transparent, and Immutable Blockchain Online Voting
              </p>
            </div>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default LoginPage;
