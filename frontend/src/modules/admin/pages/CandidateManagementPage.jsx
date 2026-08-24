import React, { useState, useEffect, useMemo } from 'react';
import { Container } from '../../../components/layout';
import { candidateService, electionService, authService } from '../../../services';
import LoadingSpinner from '../../../components/common/LoadingSpinner';
import Alert from '../../../components/common/Alert';
import '../admin.css';

const CandidateManagementPage = () => {
  const [candidates, setCandidates] = useState([]);
  const [elections, setElections] = useState([]);
  const [positions, setPositions] = useState([]);
  const [parties, setParties] = useState([]);
  const [students, setStudents] = useState([]);

  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState(null);

  // Filters
  const [selectedElection, setSelectedElection] = useState('');
  const [selectedPosition, setSelectedPosition] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  // Modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // Form states
  const [formData, setFormData] = useState({
    user_id: '',
    election_id: '',
    position_id: '',
    party_id: '',
    manifesto: '',
    photo: null,
    is_active: true,
  });

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    fetchCandidates();
  }, [selectedElection, selectedPosition]);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      const [electionsRes, positionsRes, partiesRes, studentsRes] = await Promise.all([
        electionService.getAll(),
        electionService.getPositions(),
        electionService.getParties(),
        authService.getUsers({ role: 'student', page_size: 100 }),
      ]);

      const electionsList = electionsRes.data.results || electionsRes.data || [];
      const positionsList = positionsRes.data.results || positionsRes.data || [];
      const partiesList = partiesRes.data.results || partiesRes.data || [];
      const studentsList = studentsRes.data.results || studentsRes.data || [];

      setElections(electionsList);
      setPositions(positionsList);
      setParties(partiesList);
      setStudents(studentsList);

      if (electionsList.length > 0 && !selectedElection) {
        setSelectedElection(electionsList[0].id);
      }
    } catch (error) {
      console.error('Error fetching candidate admin options:', error);
      setAlert({ type: 'danger', message: 'Failed to load options and candidate data.' });
    } finally {
      setLoading(false);
    }
  };

  const fetchCandidates = async () => {
    try {
      const params = {};
      if (selectedElection) params.election_id = selectedElection;
      if (selectedPosition) params.position_id = selectedPosition;

      const res = await candidateService.getAll(params);
      setCandidates(res.data.results || res.data || []);
    } catch (error) {
      console.error('Error fetching candidates:', error);
    }
  };

  const handleOpenAddModal = () => {
    setFormData({
      user_id: '',
      election_id: selectedElection || (elections[0]?.id || ''),
      position_id: positions[0]?.id || '',
      party_id: '',
      manifesto: '',
      photo: null,
      is_active: true,
    });
    setShowAddModal(true);
  };

  const handleOpenEditModal = (candidate) => {
    setSelectedCandidate(candidate);
    setFormData({
      user_id: candidate.user.id,
      election_id: candidate.election.id,
      position_id: candidate.position.id,
      party_id: candidate.party?.id || '',
      manifesto: candidate.manifesto || '',
      photo: null,
      is_active: candidate.is_active,
    });
    setShowEditModal(true);
  };

  const handleOpenDeleteModal = (candidate) => {
    setSelectedCandidate(candidate);
    setShowDeleteModal(true);
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFormData((prev) => ({
        ...prev,
        photo: e.target.files[0],
      }));
    }
  };

  const handleCreateCandidate = async (e) => {
    e.preventDefault();
    if (!formData.user_id || !formData.election_id || !formData.position_id) {
      setAlert({ type: 'warning', message: 'Please select a student, election, and position.' });
      return;
    }

    try {
      setSubmitting(true);
      const data = new FormData();
      data.append('user_id', formData.user_id);
      data.append('election_id', formData.election_id);
      data.append('position_id', formData.position_id);
      if (formData.party_id) data.append('party_id', formData.party_id);
      data.append('manifesto', formData.manifesto);
      data.append('is_active', formData.is_active ? 'true' : 'false');
      if (formData.photo) data.append('photo', formData.photo);

      await candidateService.create(data);
      setAlert({ type: 'success', message: 'Candidate added successfully!' });
      setShowAddModal(false);
      fetchCandidates();
    } catch (error) {
      console.error('Error creating candidate:', error);
      const detail = error.response?.data?.detail || JSON.stringify(error.response?.data) || 'Failed to add candidate.';
      setAlert({ type: 'danger', message: detail });
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdateCandidate = async (e) => {
    e.preventDefault();
    if (!selectedCandidate) return;

    try {
      setSubmitting(true);
      const data = new FormData();
      if (formData.position_id) data.append('position_id', formData.position_id);
      if (formData.party_id) {
        data.append('party_id', formData.party_id);
      } else {
        data.append('party_id', '');
      }
      data.append('manifesto', formData.manifesto);
      data.append('is_active', formData.is_active ? 'true' : 'false');
      if (formData.photo) data.append('photo', formData.photo);

      await candidateService.update(selectedCandidate.id, data);
      setAlert({ type: 'success', message: 'Candidate updated successfully!' });
      setShowEditModal(false);
      fetchCandidates();
    } catch (error) {
      console.error('Error updating candidate:', error);
      setAlert({ type: 'danger', message: 'Failed to update candidate.' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleActive = async (candidateId) => {
    try {
      await candidateService.toggleActive(candidateId);
      setCandidates((prev) =>
        prev.map((c) => (c.id === candidateId ? { ...c, is_active: !c.is_active } : c))
      );
      setAlert({ type: 'info', message: 'Candidate active status updated.' });
    } catch (error) {
      console.error('Error toggling candidate status:', error);
      setAlert({ type: 'danger', message: 'Failed to toggle status.' });
    }
  };

  const handleDeleteCandidate = async () => {
    if (!selectedCandidate) return;
    try {
      setSubmitting(true);
      await candidateService.delete(selectedCandidate.id);
      setAlert({ type: 'success', message: 'Candidate removed successfully.' });
      setShowDeleteModal(false);
      fetchCandidates();
    } catch (error) {
      console.error('Error deleting candidate:', error);
      setAlert({ type: 'danger', message: 'Failed to delete candidate.' });
    } finally {
      setSubmitting(false);
    }
  };

  const filteredCandidates = useMemo(() => {
    if (!searchQuery.trim()) return candidates;
    const q = searchQuery.toLowerCase();
    return candidates.filter((c) => {
      const name = c.user?.full_name?.toLowerCase() || '';
      const studentId = c.user?.student_id?.toLowerCase() || '';
      const position = c.position?.name?.toLowerCase() || '';
      const party = c.party?.name?.toLowerCase() || '';
      return name.includes(q) || studentId.includes(q) || position.includes(q) || party.includes(q);
    });
  }, [candidates, searchQuery]);

  if (loading) {
    return <LoadingSpinner fullScreen text="Loading candidates..." />;
  }

  return (
    <Container>
      <div className="admin-header d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
        <div>
          <h1>
            <i className="fas fa-users-cog text-primary"></i> Direct Candidate Management
          </h1>
          <p>Directly assign, configure, and manage official candidates for university student elections.</p>
        </div>
        <div className="admin-header-actions">
          <button className="btn btn-primary" onClick={handleOpenAddModal}>
            Add Candidate
          </button>
        </div>
      </div>

      {alert && (
        <Alert type={alert.type} message={alert.message} dismissible onDismiss={() => setAlert(null)} />
      )}

      {/* Filter Bar */}
      <div className="admin-filter-tabs mb-4">
        <div className="row g-3 w-100 align-items-end">
          <div className="col-md-4">
            <label className="form-label small fw-semibold text-muted">Filter by Election</label>
            <select
              className="form-select form-select-sm"
              value={selectedElection}
              onChange={(e) => setSelectedElection(e.target.value)}
            >
              <option value="">All Elections</option>
              {elections.map((el) => (
                <option key={el.id} value={el.id}>
                  {el.title} ({el.status})
                </option>
              ))}
            </select>
          </div>

          <div className="col-md-4">
            <label className="form-label small fw-semibold text-muted">Filter by Position</label>
            <select
              className="form-select form-select-sm"
              value={selectedPosition}
              onChange={(e) => setSelectedPosition(e.target.value)}
            >
              <option value="">All Positions</option>
              {positions.map((pos) => (
                <option key={pos.id} value={pos.id}>
                  {pos.name}
                </option>
              ))}
            </select>
          </div>

          <div className="col-md-4">
            <label className="form-label small fw-semibold text-muted">Search Candidates</label>
            <div className="input-group input-group-sm">
              <span className="input-group-text bg-white border-end-0">
                <i className="fas fa-search text-muted"></i>
              </span>
              <input
                type="text"
                className="form-control border-start-0"
                placeholder="Search name, student ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Table Container */}
      <div className="admin-table-container">
        {filteredCandidates.length === 0 ? (
          <div className="text-center py-5">
            <h5 className="text-muted">No candidates found</h5>
            <p className="text-muted small">Click "Add Candidate" to assign student leaders to election positions.</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="table admin-table align-middle mb-0">
              <thead>
                <tr>
                  <th style={{ width: '60px' }}>Photo</th>
                  <th>Candidate Name</th>
                  <th>Position</th>
                  <th>Election</th>
                  <th>Political Party</th>
                  <th>Status</th>
                  <th className="text-end pe-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredCandidates.map((candidate) => (
                  <tr key={candidate.id}>
                    <td>
                      {candidate.photo_url ? (
                        <img
                          src={candidate.photo_url}
                          alt="Candidate"
                          className="rounded-circle object-fit-cover border"
                          width="42"
                          height="42"
                        />
                      ) : (
                        <div
                          className="rounded-circle bg-light text-primary fw-bold d-flex align-items-center justify-content-center border"
                          style={{ width: '42px', height: '42px', fontSize: '0.9rem' }}
                        >
                          {(candidate.user?.first_name?.[0] || 'C').toUpperCase()}
                        </div>
                      )}
                    </td>
                    <td>
                      <div className="fw-semibold text-dark">{candidate.user?.full_name}</div>
                      <div className="fs-xs text-muted">
                        ID: {candidate.user?.student_id || 'N/A'} {candidate.user?.course_code ? `• ${candidate.user.course_code}` : ''}
                      </div>
                    </td>
                    <td>
                      <span className="badge bg-secondary-subtle text-dark border">
                        {candidate.position?.name}
                      </span>
                    </td>
                    <td>
                      <div className="small fw-semibold">{candidate.election?.title}</div>
                    </td>
                    <td>
                      {candidate.party ? (
                        <span
                          className="badge border"
                          style={{
                            backgroundColor: `${candidate.party.color || '#0b6e3b'}15`,
                            color: candidate.party.color || '#0b6e3b',
                            borderColor: candidate.party.color || '#0b6e3b',
                          }}
                        >
                          {candidate.party.name}
                        </span>
                      ) : (
                        <span className="badge bg-light text-muted border">Independent</span>
                      )}
                    </td>
                    <td>
                      <span
                        className={`badge rounded-pill ${candidate.is_active ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-light text-muted border'} px-3 py-1`}
                        style={{ cursor: 'pointer', fontSize: '0.85rem' }}
                        onClick={() => handleToggleActive(candidate.id)}
                        title="Click to toggle active status"
                      >
                        {candidate.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="text-end pe-4">
                      <div className="d-flex justify-content-end gap-1">
                        <button
                          type="button"
                          className="btn btn-sm btn-light border text-primary"
                          onClick={() => handleOpenEditModal(candidate)}
                          title="Edit Candidate"
                        >
                          <i className="bi bi-pencil"></i>
                        </button>
                        <button
                          type="button"
                          className="btn btn-sm btn-light border text-danger"
                          onClick={() => handleOpenDeleteModal(candidate)}
                          title="Delete Candidate"
                        >
                          <i className="bi bi-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="auth-link-modal-overlay" role="dialog" aria-modal="true">
          <div className="auth-link-modal-card" style={{ maxWidth: '650px', width: '90%' }}>
            <div className="d-flex justify-content-between align-items-center mb-4">
              <h3 className="h5 fw-bold mb-0">
                <i className="fas fa-user-check text-primary me-2"></i> Add Direct Candidate
              </h3>
              <button type="button" className="btn-close" onClick={() => setShowAddModal(false)}></button>
            </div>

            <form onSubmit={handleCreateCandidate}>
              <div className="row g-3">
                <div className="col-12">
                  <label className="form-label small fw-semibold">Select Student User *</label>
                  <select
                    name="user_id"
                    className="form-select"
                    value={formData.user_id}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">-- Choose Student --</option>
                    {students.map((s) => (
                      <option key={s.user_id || s.id} value={s.user_id || s.id}>
                        {s.full_name || `${s.first_name} ${s.last_name}`} ({s.student_id || s.username}) - {s.course_code || 'Student'}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="col-md-6">
                  <label className="form-label small fw-semibold">Election *</label>
                  <select
                    name="election_id"
                    className="form-select"
                    value={formData.election_id}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">-- Choose Election --</option>
                    {elections.map((el) => (
                      <option key={el.id} value={el.id}>
                        {el.title}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="col-md-6">
                  <label className="form-label small fw-semibold">Position *</label>
                  <select
                    name="position_id"
                    className="form-select"
                    value={formData.position_id}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">-- Choose Position --</option>
                    {positions.map((pos) => (
                      <option key={pos.id} value={pos.id}>
                        {pos.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="col-md-6">
                  <label className="form-label small fw-semibold">Political Party</label>
                  <select
                    name="party_id"
                    className="form-select"
                    value={formData.party_id}
                    onChange={handleInputChange}
                  >
                    <option value="">Independent (No Party)</option>
                    {parties.map((party) => (
                      <option key={party.id} value={party.id}>
                        {party.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="col-md-6">
                  <label className="form-label small fw-semibold">Candidate Photo</label>
                  <input type="file" className="form-control" accept="image/*" onChange={handleFileChange} />
                </div>

                <div className="col-12">
                  <label className="form-label small fw-semibold">Campaign Platform & Goals</label>
                  <textarea
                    name="manifesto"
                    className="form-control"
                    rows="3"
                    placeholder="Candidate advocacy, bio, or goals..."
                    value={formData.manifesto}
                    onChange={handleInputChange}
                  ></textarea>
                </div>

                <div className="col-12">
                  <div className="form-check form-switch">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      name="is_active"
                      id="addActiveSwitch"
                      checked={formData.is_active}
                      onChange={handleInputChange}
                    />
                    <label className="form-check-label small fw-semibold" htmlFor="addActiveSwitch">
                      Active on voting ballot
                    </label>
                  </div>
                </div>
              </div>

              <div className="auth-link-modal-actions mt-4">
                <button type="button" className="auth-link-modal-cancel" onClick={() => setShowAddModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="auth-link-modal-confirm" disabled={submitting}>
                  {submitting ? 'Saving...' : 'Add Candidate'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && selectedCandidate && (
        <div className="auth-link-modal-overlay" role="dialog" aria-modal="true">
          <div className="auth-link-modal-card" style={{ maxWidth: '650px', width: '90%' }}>
            <div className="d-flex justify-content-between align-items-center mb-4">
              <h3 className="h5 fw-bold mb-0">
                <i className="fas fa-pencil-alt text-primary me-2"></i> Edit Candidate: {selectedCandidate.user?.full_name}
              </h3>
              <button type="button" className="btn-close" onClick={() => setShowEditModal(false)}></button>
            </div>

            <form onSubmit={handleUpdateCandidate}>
              <div className="row g-3">
                <div className="col-md-6">
                  <label className="form-label small fw-semibold">Position</label>
                  <select
                    name="position_id"
                    className="form-select"
                    value={formData.position_id}
                    onChange={handleInputChange}
                    required
                  >
                    {positions.map((pos) => (
                      <option key={pos.id} value={pos.id}>
                        {pos.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="col-md-6">
                  <label className="form-label small fw-semibold">Political Party</label>
                  <select
                    name="party_id"
                    className="form-select"
                    value={formData.party_id}
                    onChange={handleInputChange}
                  >
                    <option value="">Independent (No Party)</option>
                    {parties.map((party) => (
                      <option key={party.id} value={party.id}>
                        {party.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="col-12">
                  <label className="form-label small fw-semibold">Replace Photo</label>
                  <input type="file" className="form-control" accept="image/*" onChange={handleFileChange} />
                </div>

                <div className="col-12">
                  <label className="form-label small fw-semibold">Campaign Platform & Goals</label>
                  <textarea
                    name="manifesto"
                    className="form-control"
                    rows="3"
                    value={formData.manifesto}
                    onChange={handleInputChange}
                  ></textarea>
                </div>

                <div className="col-12">
                  <div className="form-check form-switch">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      name="is_active"
                      id="editActiveSwitch"
                      checked={formData.is_active}
                      onChange={handleInputChange}
                    />
                    <label className="form-check-label small fw-semibold" htmlFor="editActiveSwitch">
                      Active on voting ballot
                    </label>
                  </div>
                </div>
              </div>

              <div className="auth-link-modal-actions mt-4">
                <button type="button" className="auth-link-modal-cancel" onClick={() => setShowEditModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="auth-link-modal-confirm" disabled={submitting}>
                  {submitting ? 'Updating...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Modal */}
      {showDeleteModal && selectedCandidate && (
        <div className="auth-link-modal-overlay" role="dialog" aria-modal="true">
          <div className="auth-link-modal-card">
            <h3 className="h5 fw-bold text-danger mb-3">
              <i className="fas fa-exclamation-triangle me-2"></i> Remove Candidate
            </h3>
            <p>
              Are you sure you want to remove candidate <strong>{selectedCandidate.user?.full_name}</strong> from position{' '}
              <strong>{selectedCandidate.position?.name}</strong>?
            </p>
            <div className="auth-link-modal-actions mt-4">
              <button type="button" className="auth-link-modal-cancel" onClick={() => setShowDeleteModal(false)}>
                Cancel
              </button>
              <button type="button" className="btn btn-danger" onClick={handleDeleteCandidate} disabled={submitting}>
                {submitting ? 'Removing...' : 'Delete Candidate'}
              </button>
            </div>
          </div>
        </div>
      )}
    </Container>
  );
};

export default CandidateManagementPage;
