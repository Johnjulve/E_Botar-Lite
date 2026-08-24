/**
 * Application Constants for E-Botar Lite
 */

export const APP_VERSION = '1.0.0';

export const API_BASE_URL = import.meta.env.DEV ? '/api' : (import.meta.env.VITE_API_BASE_URL || '/api');

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user',
  THEME: 'theme'
};

export const ELECTION_STATUS = {
  UPCOMING: 'upcoming',
  ACTIVE: 'active',
  FINISHED: 'finished'
};

export const USER_ROLES = {
  ADMIN: 'admin',
  STAFF: 'staff',
  STUDENT: 'student'
};

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  ELECTIONS: '/elections',
  ELECTION_DETAILS: '/elections/:id',
  CANDIDATES: '/candidates',
  CANDIDATE_PROFILE: '/candidates/:id',
  VOTE: '/vote/:id',
  MY_VOTES: '/my-votes',
  VERIFY_RECEIPT: '/verify-receipt',
  RESULTS: '/results/:id',
  PROFILE: '/profile',
  EDIT_PROFILE: '/profile/edit',
  ADMIN: '/admin',
  ADMIN_ELECTIONS: '/admin/elections',
  ADMIN_CANDIDATES: '/admin/candidates',
  ADMIN_POSITIONS: '/admin/positions',
  ADMIN_PARTIES: '/admin/parties',
  ADMIN_PROGRAMS: '/admin/programs',
  ADMIN_USERS: '/admin/users',
  ADMIN_VOTING_STATUS: '/admin/voting-status',
  ADMIN_RECEIPT_AUDIT: '/admin/receipt-audit',
  ADMIN_LOGS: '/admin/logs'
};

export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/token/',
  REGISTER: '/auth/register/',
  REFRESH_TOKEN: '/auth/token/refresh/',
  ME: '/auth/me/',
  DEPARTMENTS: '/auth/departments/',
  COURSES: '/auth/courses/',
  PROFILES: '/auth/profiles/',
  USERS: '/auth/users/',
  PROGRAMS: '/auth/programs/',
  USER_COUNTS: '/auth/user-counts/',

  // Elections
  ELECTIONS: '/elections/elections/',
  ACTIVE_ELECTIONS: '/elections/elections/active/',
  UPCOMING_ELECTIONS: '/elections/elections/upcoming/',
  FINISHED_ELECTIONS: '/elections/elections/finished/',
  POSITIONS: '/elections/positions/',
  PARTIES: '/elections/parties/',

  // Candidates
  CANDIDATES: '/candidates/candidates/',
  CANDIDATES_BY_ELECTION: '/candidates/candidates/by_election/',

  // Voting
  BALLOTS: '/voting/ballots/',
  SUBMIT_BALLOT: '/voting/ballots/submit/',
  MY_BALLOT: '/voting/ballots/my_ballot/',
  RECEIPTS: '/voting/receipts/',
  MY_RECEIPTS: '/voting/receipts/my_receipts/',
  VERIFY_RECEIPT: '/voting/receipts/verify/',
  RESULTS: '/voting/results/election_results/',
  VOTE_STATUS: '/voting/results/my_vote_status/',
  STATISTICS: '/voting/results/statistics/',
  LEDGER_INTEGRITY: '/voting/results/ledger_integrity/',
  VOTING_STATUS: '/voting/voting-status/',

  // Common
  HEALTH: '/common/health/',
  VERSION: '/common/version/',
  BRANDING: '/common/branding/',
  SYSTEM_LOGS: '/common/system-logs/',
};

export default {
  APP_VERSION,
  API_BASE_URL,
  STORAGE_KEYS,
  ELECTION_STATUS,
  USER_ROLES,
  ROUTES,
  API_ENDPOINTS,
};
