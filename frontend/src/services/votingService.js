import api from './api';
import { API_ENDPOINTS } from '../constants';

export const votingService = {
  submitBallot: (ballotData) => api.post(API_ENDPOINTS.SUBMIT_BALLOT, ballotData),
  getMyBallot: (electionId) => api.get(API_ENDPOINTS.MY_BALLOT, { params: { election_id: electionId } }),
  getMyReceipts: () => api.get(API_ENDPOINTS.MY_RECEIPTS),
  verifyReceipt: (receiptCode) => api.post(API_ENDPOINTS.VERIFY_RECEIPT, { receipt_code: receiptCode }),
  getResults: (electionId) => api.get(API_ENDPOINTS.RESULTS, { params: { election_id: electionId } }),
  getElectionResults: (electionId) => api.get(API_ENDPOINTS.RESULTS, { params: { election_id: electionId } }),
  getVoteStatus: (electionId) => api.get(API_ENDPOINTS.VOTE_STATUS, { params: { election_id: electionId } }),
  getMyVoteStatus: (electionId) => api.get(API_ENDPOINTS.VOTE_STATUS, { params: { election_id: electionId } }),
  getStatistics: (electionId) => api.get(API_ENDPOINTS.STATISTICS, { params: { election_id: electionId } }),
  getLedgerIntegrity: (electionId) => api.get(API_ENDPOINTS.LEDGER_INTEGRITY, { params: { election_id: electionId } }),
  getVotingStatusList: (params = {}) => api.get(API_ENDPOINTS.VOTING_STATUS, { params }),
  getVotingStatus: (params = {}) => api.get(API_ENDPOINTS.VOTING_STATUS, { params }),
  getAuditReceipts: (params = {}) => api.get(`${API_ENDPOINTS.RECEIPTS}audit/`, { params }),
  getReceiptAudit: (params = {}) => api.get(`${API_ENDPOINTS.RECEIPTS}audit/`, { params }),
};

export default votingService;
