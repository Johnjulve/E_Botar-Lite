/**
 * RegisterPage
 * User registration page matching main design
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Form } from 'react-bootstrap';
import { useAuth } from '../../../hooks/useAuth';
import { useBranding } from '../../../hooks/useBranding';
import { programService } from '../../../services';
import { ROUTES } from '../../../constants';
import './auth.css';

const RegisterPage = () => {
  const navigate = useNavigate();
  const { register, isAuthenticated } = useAuth();
  const { branding, app_name } = useBranding();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    middle_name: '',
    last_name: '',
    department: '',
    course: '',
    year_level: '1st Year',
    section: 'A',
    password: '',
    password_confirm: '',
  });

  const [departments, setDepartments] = useState([]);
  const [courses, setCourses] = useState([]);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    const fetchPrograms = async () => {
      try {
        const [deptRes, courseRes] = await Promise.all([
          programService.getDepartments(),
          programService.getCourses(),
        ]);
        setDepartments(deptRes.data.results || deptRes.data || []);
        setCourses(courseRes.data.results || courseRes.data || []);
      } catch (err) {
        console.error('Failed to load academic programs:', err);
      }
    };
    fetchPrograms();
  }, []);

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
    if (!formData.username.trim()) newErrors.username = 'Username is required';
    if (!formData.email.trim()) newErrors.email = 'Email address is required';
    if (!formData.password) newErrors.password = 'Password is required';
    if (formData.password && formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }
    if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = 'Passwords do not match';
    }
    return newErrors;
  };

  const filteredCourses = formData.department
    ? courses.filter((c) => c.department === formData.department)
    : courses;

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
      const result = await register(formData);
      if (result.success) {
        setSuccessMessage('Registration successful! Redirecting to login...');
        setTimeout(() => navigate(ROUTES.LOGIN), 2000);
      } else {
        const err = result.error;
        if (typeof err === 'object') {
          const firstKey = Object.keys(err)[0];
          setErrorMessage(`${firstKey}: ${err[firstKey]}`);
        } else {
          setErrorMessage(err || 'Registration failed.');
        }
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
          <Col md={10} lg={9} xl={8}>
            <div className="auth-header">
              <h1>Create Your Account</h1>
              <p>Join {app_name || 'E-Botar Lite'} and participate in student elections</p>
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

              {successMessage && (
                <div className="auth-alert alert-success" role="alert">
                  <i className="fas fa-check-circle me-2"></i>
                  <span>{successMessage}</span>
                </div>
              )}

              <Form onSubmit={handleSubmit} className="auth-form">
                <div className="auth-two-column">
                  <Form.Group className="form-group">
                    <Form.Label>
                      <i className="fas fa-user text-muted me-1"></i>
                      Username <span className="text-danger">*</span>
                    </Form.Label>
                    <Form.Control
                      type="text"
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      isInvalid={!!errors.username}
                      placeholder="Choose a username"
                      disabled={loading}
                    />
                    {errors.username && (
                      <div className="invalid-feedback d-block">{errors.username}</div>
                    )}
                  </Form.Group>

                  <Form.Group className="form-group">
                    <Form.Label>
                      <i className="fas fa-envelope text-muted me-1"></i>
                      Email Address <span className="text-danger">*</span>
                    </Form.Label>
                    <Form.Control
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      isInvalid={!!errors.email}
                      placeholder="your.email@snsu.edu.ph"
                      disabled={loading}
                    />
                    {errors.email && (
                      <div className="invalid-feedback d-block">{errors.email}</div>
                    )}
                  </Form.Group>
                </div>

                <div className="auth-two-column">
                  <Form.Group className="form-group">
                    <Form.Label>
                      <i className="fas fa-id-card text-muted me-1"></i>
                      First Name
                    </Form.Label>
                    <Form.Control
                      type="text"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleChange}
                      placeholder="First name"
                      disabled={loading}
                    />
                  </Form.Group>

                  <Form.Group className="form-group">
                    <Form.Label>
                      <i className="fas fa-id-card text-muted me-1"></i>
                      Middle Name
                    </Form.Label>
                    <Form.Control
                      type="text"
                      name="middle_name"
                      value={formData.middle_name}
                      onChange={handleChange}
                      placeholder="Middle name"
                      disabled={loading}
                    />
                  </Form.Group>

                  <Form.Group className="form-group">
                    <Form.Label>
                      <i className="fas fa-id-card text-muted me-1"></i>
                      Last Name
                    </Form.Label>
                    <Form.Control
                      type="text"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleChange}
                      placeholder="Last name"
                      disabled={loading}
                    />
                  </Form.Group>
                </div>

                <div className="auth-two-column">
                  <Form.Group className="form-group">
                    <Form.Label>
                      <i className="fas fa-building text-muted me-1"></i>
                      Department / College
                    </Form.Label>
                    <Form.Select
                      name="department"
                      value={formData.department}
                      onChange={handleChange}
                      disabled={loading}
                    >
                      <option value="">-- Select College --</option>
                      {departments.map((d) => (
                        <option key={d.code} value={d.code}>
                          {d.name} ({d.code})
                        </option>
                      ))}
                    </Form.Select>
                  </Form.Group>

                  <Form.Group className="form-group">
                    <Form.Label>
                      <i className="fas fa-graduation-cap text-muted me-1"></i>
                      Degree Course
                    </Form.Label>
                    <Form.Select
                      name="course"
                      value={formData.course}
                      onChange={handleChange}
                      disabled={loading}
                    >
                      <option value="">-- Select Course --</option>
                      {filteredCourses.map((c) => (
                        <option key={c.code} value={c.code}>
                          {c.name} ({c.code})
                        </option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </div>

                <div className="auth-two-column">
                  <Form.Group className="form-group">
                    <Form.Label>
                      <i className="fas fa-calendar-alt text-muted me-1"></i>
                      Year Level
                    </Form.Label>
                    <Form.Select
                      name="year_level"
                      value={formData.year_level}
                      onChange={handleChange}
                      disabled={loading}
                    >
                      <option value="1st Year">1st Year</option>
                      <option value="2nd Year">2nd Year</option>
                      <option value="3rd Year">3rd Year</option>
                      <option value="4th Year">4th Year</option>
                      <option value="5th Year">5th Year</option>
                    </Form.Select>
                  </Form.Group>

                  <Form.Group className="form-group">
                    <Form.Label>
                      <i className="fas fa-layer-group text-muted me-1"></i>
                      Section
                    </Form.Label>
                    <Form.Control
                      type="text"
                      name="section"
                      value={formData.section}
                      onChange={handleChange}
                      placeholder="e.g. A, B, 1"
                      disabled={loading}
                    />
                  </Form.Group>
                </div>

                <div className="auth-two-column">
                  <Form.Group className="form-group">
                    <Form.Label>
                      <i className="fas fa-lock text-muted me-1"></i>
                      Password <span className="text-danger">*</span>
                    </Form.Label>
                    <div className="auth-password-wrap">
                      <Form.Control
                        type={showPassword ? 'text' : 'password'}
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        isInvalid={!!errors.password}
                        placeholder="Min. 8 characters"
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

                  <Form.Group className="form-group">
                    <Form.Label>
                      <i className="fas fa-lock text-muted me-1"></i>
                      Confirm Password <span className="text-danger">*</span>
                    </Form.Label>
                    <div className="auth-password-wrap">
                      <Form.Control
                        type={showConfirmPassword ? 'text' : 'password'}
                        name="password_confirm"
                        value={formData.password_confirm}
                        onChange={handleChange}
                        isInvalid={!!errors.password_confirm}
                        placeholder="Re-enter password"
                        disabled={loading}
                      />
                      <button
                        type="button"
                        className="auth-password-toggle"
                        onClick={() => setShowConfirmPassword((p) => !p)}
                        aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                        tabIndex={-1}
                      >
                        <i className={showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'}></i>
                      </button>
                    </div>
                    {errors.password_confirm && (
                      <div className="invalid-feedback d-block">{errors.password_confirm}</div>
                    )}
                  </Form.Group>
                </div>

                <button
                  type="submit"
                  className={`auth-submit-btn mt-3 ${loading ? 'auth-loading' : ''}`}
                  disabled={loading}
                >
                  {loading && <span className="auth-spinner me-2"></span>}
                  {loading ? 'Creating Account...' : 'Complete Registration'}
                </button>
              </Form>

              <div className="auth-link-text mt-4">
                Already have an account?{' '}
                <Link to={ROUTES.LOGIN} className="auth-link">
                  Log in here
                </Link>
              </div>
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

export default RegisterPage;
