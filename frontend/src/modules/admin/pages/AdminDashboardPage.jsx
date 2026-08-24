import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Container } from '../../../components/layout';
import { LoadingSpinner } from '../../../components/common';
import { electionService, candidateService, authService } from '../../../services';
import { ROUTES } from '../../../constants';
import '../admin.css';
import '../admin-dashboard.css';

const AdminDashboardPage = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalElections: 0,
    activeElections: 0,
    totalCandidates: 0,
    totalVotes: 0,
    totalUsers: 0,
    totalStudents: 0,
  });
  const [recentElections, setRecentElections] = useState([]);
  const [recentCandidates, setRecentCandidates] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [electionsRes, activeRes, candidatesRes, userCountRes] = await Promise.all([
        electionService.getAll(),
        electionService.getActive(),
        candidateService.getAll(),
        authService.getUserCount(),
      ]);

      const elections = electionsRes?.data?.results || electionsRes?.data || [];
      const active = activeRes?.data?.results || activeRes?.data || [];
      const candidates = candidatesRes?.data?.results || candidatesRes?.data || [];
      const userCounts = userCountRes?.data || userCountRes || {};

      const totalVotes = elections.reduce((sum, e) => sum + (e.total_votes || 0), 0);

      setStats({
        totalElections: elections.length,
        activeElections: active.length,
        totalCandidates: candidates.length,
        totalVotes: totalVotes,
        totalUsers: userCounts.total_users || 0,
        totalStudents: userCounts.total_students || 0,
      });

      setRecentElections(elections.slice(0, 5));
      setRecentCandidates(candidates.slice(0, 5));
    } catch (error) {
      console.error('Error fetching admin dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner fullScreen text="Loading dashboard statistics..." />;
  }

  return (
    <Container>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h3 fw-bold mb-1">
            <i className="bi bi-speedometer2 me-2 text-primary"></i> Administrative Dashboard
          </h1>
          <p className="text-muted mb-0">System performance, voting metrics, and election management.</p>
        </div>
        <div className="d-flex gap-2">
          <Link to={ROUTES.ADMIN_CANDIDATES} className="btn btn-outline-primary btn-sm px-3 rounded-3">
            <i className="bi bi-person-badge me-1"></i> Manage Candidates
          </Link>
          <Link to="/admin/elections/new" className="btn btn-primary btn-sm px-3 rounded-3">
            Create Election
          </Link>
        </div>
      </div>

      {/* KPI Stats Cards */}
      <div className="row g-3 mb-4">
        <div className="col-sm-6 col-lg-3">
          <div className="card border-0 shadow-sm rounded-4 p-3 bg-white h-100">
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <span className="text-muted small fw-semibold">Active Elections</span>
                <h3 className="fw-bold my-1 text-primary">{stats.activeElections}</h3>
                <span className="small text-muted">{stats.totalElections} total elections</span>
              </div>
              <div className="rounded-circle bg-primary-subtle text-primary p-3 d-flex align-items-center justify-content-center" style={{ width: '52px', height: '52px' }}>
                <i className="bi bi-calendar-check fs-4"></i>
              </div>
            </div>
          </div>
        </div>

        <div className="col-sm-6 col-lg-3">
          <div className="card border-0 shadow-sm rounded-4 p-3 bg-white h-100">
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <span className="text-muted small fw-semibold">Direct Candidates</span>
                <h3 className="fw-bold my-1 text-success">{stats.totalCandidates}</h3>
                <span className="small text-muted">Running across positions</span>
              </div>
              <div className="rounded-circle bg-success-subtle text-success p-3 d-flex align-items-center justify-content-center" style={{ width: '52px', height: '52px' }}>
                <i className="bi bi-people-fill fs-4"></i>
              </div>
            </div>
          </div>
        </div>

        <div className="col-sm-6 col-lg-3">
          <div className="card border-0 shadow-sm rounded-4 p-3 bg-white h-100">
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <span className="text-muted small fw-semibold">Blockchain Ballots Cast</span>
                <h3 className="fw-bold my-1 text-warning">{stats.totalVotes}</h3>
                <span className="small text-muted">Cryptographically verified</span>
              </div>
              <div className="rounded-circle bg-warning-subtle text-warning p-3 d-flex align-items-center justify-content-center" style={{ width: '52px', height: '52px' }}>
                <i className="bi bi-shield-check fs-4"></i>
              </div>
            </div>
          </div>
        </div>

        <div className="col-sm-6 col-lg-3">
          <div className="card border-0 shadow-sm rounded-4 p-3 bg-white h-100">
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <span className="text-muted small fw-semibold">Registered Students</span>
                <h3 className="fw-bold my-1 text-info">{stats.totalStudents}</h3>
                <span className="small text-muted">{stats.totalUsers} total accounts</span>
              </div>
              <div className="rounded-circle bg-info-subtle text-info p-3 d-flex align-items-center justify-content-center" style={{ width: '52px', height: '52px' }}>
                <i className="bi bi-person-lines-fill fs-4"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Access Actions */}
      <div className="card shadow-sm border-0 rounded-4 mb-4">
        <div className="card-header bg-white py-3 border-0">
          <h5 className="fw-bold mb-0">Management Quick Actions</h5>
        </div>
        <div className="card-body pt-0">
          <div className="row g-3">
            <div className="col-6 col-md-3">
              <Link to={ROUTES.ADMIN_ELECTIONS} className="btn btn-light w-100 text-start p-3 border rounded-3 text-decoration-none shadow-sm">
                <i className="bi bi-calendar3 fs-4 text-primary d-block mb-1"></i>
                <div className="fw-bold text-dark">Elections</div>
                <div className="text-muted fs-xs">Schedule & configure</div>
              </Link>
            </div>
            <div className="col-6 col-md-3">
              <Link to={ROUTES.ADMIN_CANDIDATES} className="btn btn-light w-100 text-start p-3 border rounded-3 text-decoration-none shadow-sm">
                <i className="bi bi-person-badge fs-4 text-success d-block mb-1"></i>
                <div className="fw-bold text-dark">Candidates</div>
                <div className="text-muted fs-xs">Direct assign & edit</div>
              </Link>
            </div>
            <div className="col-6 col-md-3">
              <Link to={ROUTES.ADMIN_RECEIPT_AUDIT} className="btn btn-light w-100 text-start p-3 border rounded-3 text-decoration-none shadow-sm">
                <i className="bi bi-diagram-3 fs-4 text-warning d-block mb-1"></i>
                <div className="fw-bold text-dark">Blockchain Ledger</div>
                <div className="text-muted fs-xs">Integrity check & audit</div>
              </Link>
            </div>
            <div className="col-6 col-md-3">
              <Link to={ROUTES.ADMIN_USERS} className="btn btn-light w-100 text-start p-3 border rounded-3 text-decoration-none shadow-sm">
                <i className="bi bi-people fs-4 text-info d-block mb-1"></i>
                <div className="fw-bold text-dark">User Accounts</div>
                <div className="text-muted fs-xs">Voters & staff access</div>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity / Tables */}
      <div className="row g-4">
        {/* Recent Elections */}
        <div className="col-lg-7">
          <div className="card shadow-sm border-0 rounded-4 h-100">
            <div className="card-header bg-white py-3 border-0 d-flex justify-content-between align-items-center">
              <h5 className="fw-bold mb-0">Recent Elections</h5>
              <Link to={ROUTES.ADMIN_ELECTIONS} className="small text-primary text-decoration-none fw-semibold">
                View All
              </Link>
            </div>
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light">
                    <tr>
                      <th className="ps-3">Title</th>
                      <th>Type</th>
                      <th>Status</th>
                      <th className="text-end pe-3">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentElections.length === 0 ? (
                      <tr>
                        <td colSpan="4" className="text-center py-4 text-muted">No elections created yet.</td>
                      </tr>
                    ) : (
                      recentElections.map((el) => (
                        <tr key={el.id}>
                          <td className="ps-3">
                            <div className="fw-semibold text-dark">{el.title}</div>
                            <div className="fs-xs text-muted">Positions: {el.total_positions || 0}</div>
                          </td>
                          <td>
                            <span className="badge bg-primary-subtle text-primary border border-primary-subtle px-2 py-1 rounded-pill">
                              {el.election_type === 'university' ? 'USC' : 'Dept'}
                            </span>
                          </td>
                          <td>
                            <span className={`badge px-2 py-1 rounded-pill text-capitalize ${el.status === 'ongoing' ? 'bg-success' : el.status === 'upcoming' ? 'bg-warning text-dark' : 'bg-secondary'}`}>
                              {el.status}
                            </span>
                          </td>
                          <td className="text-end pe-3">
                            <Link to={`/results/${el.id}`} className="btn btn-sm btn-outline-primary px-3 rounded-pill">
                              Results
                            </Link>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Direct Candidates */}
        <div className="col-lg-5">
          <div className="card shadow-sm border-0 rounded-4 h-100">
            <div className="card-header bg-white py-3 border-0 d-flex justify-content-between align-items-center">
              <h5 className="fw-bold mb-0">Active Candidates</h5>
              <Link to={ROUTES.ADMIN_CANDIDATES} className="small text-primary text-decoration-none fw-semibold">
                Manage
              </Link>
            </div>
            <div className="card-body p-0">
              <div className="list-group list-group-flush">
                {recentCandidates.length === 0 ? (
                  <div className="text-center py-4 text-muted">No candidates assigned yet.</div>
                ) : (
                  recentCandidates.map((cand) => (
                    <div key={cand.id} className="list-group-item d-flex align-items-center justify-content-between py-3 px-3">
                      <div className="d-flex align-items-center gap-3">
                        {cand.photo_url ? (
                          <img src={cand.photo_url} alt="Photo" className="rounded-circle object-fit-cover shadow-sm border" width="38" height="38" />
                        ) : (
                          <div className="rounded-circle bg-primary text-white fw-bold d-flex align-items-center justify-content-center shadow-sm" style={{ width: '38px', height: '38px', fontSize: '0.95rem' }}>
                            {(cand.user?.first_name?.[0] || 'C').toUpperCase()}
                          </div>
                        )}
                        <div>
                          <div className="fw-semibold text-dark">{cand.user?.full_name}</div>
                          <div className="fs-xs text-muted">{cand.position?.name} • {cand.party?.name || 'Independent'}</div>
                        </div>
                      </div>
                      <span className={`badge px-2 py-1 rounded-pill ${cand.is_active ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-light text-muted border'}`}>
                        {cand.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Container>
  );
};

export default AdminDashboardPage;
