# Changelog

All notable changes to **E-Botar Lite** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.0.0] - 2026-10-06

Major architectural and infrastructure hardening release introducing unified API versioning, decoupled voting submission services, streaming export pipelines, sliding window pagination, database-level query aggregations, fail-fast configuration safety, and resilient frontend error boundaries and toast notifications.

### Added
- **API Versioning & Client Gateway Adapter (`/api/v1/`)**: Standardized all backend routing with `/api/v1/` prefixing and configured Axios interceptors with automated token renewal and standardized error envelope unboxing.
- **Lazy Streaming Pipelines (`EchoBuffer` & Generator Exports)**: Replaced full in-memory file buffers with generator-driven streaming CSV export pipelines, guaranteeing flat $O(1)$ memory footprints regardless of dataset size.
- **Sliding Window Pagination (`SlidingWindowPagination`)**: Implemented dynamic metadata pagination (`max_window_size=200`, `sliding_step=50`) preventing payload bloat on large tabular registries.
- **Global React Error Boundary (`ErrorBoundary.jsx`)**: Integrated application-level catch boundary with a recovery view and crash telemetry reporting, isolating rendering failures without white-screening.
- **Unified Notification System (`ToastProvider` & `useToast`)**: Replaced fragmented `alert()` dialogs with auto-dismissing, accessible floating toast alerts for actions, warnings, and error diagnostics.

### Changed & Performance
- **Decoupled Voting Submission Pipeline**: Refactored `BallotViewSet.submit()` into an isolated, atomic service with pre-validated candidate lookups, batch verification, and clean boundary separation.
- **Database-Level SQL Aggregation**: Optimized election results calculation by replacing Python-level iteration loops with direct Django ORM aggregation queries, slashing DB hits.
- **Fail-Fast Configuration Enforcement**: Implemented strict validation during Django startup to halt immediately if `SECRET_KEY` is missing or set to insecure defaults in non-debug environments.
- **Unthrottled Health Check Probes**: Whitelisted `/api/health/` and monitoring routes from API rate limiters to support continuous uptime monitoring.

---

## [2.0.0] - 2026-10-06

Major feature release introducing Administrative Student Roster Synchronization. This establishes a "Closed Registration" architectural posture where user accounts are strictly imported and managed by administrators via Excel/CSV, eliminating open public registration.

### Added
- **Centralized Administrative Roster Parser**: Added `StudentRosterParser` to support robust `.xlsx` and `.csv` parsing, format normalization (student IDs, year levels, course codes), and row-level validation.
- **Roster Diff & Execution Engine**: Implemented stateless pre-import execution pipeline `classify_roster_diff` to calculate New, Updated, Deactivated, and Erroneous records before committing to the database.
- **Google OAuth Integration**: Configured Google Social Login explicitly for University Google Workspace accounts, mapping verified emails directly to imported roster accounts, and auto-bypassing password requirements.
- **Frontend Sync UI & Interactive Preview**: Added bulk file dropzone and an interactive pre-import confirmation modal in the User Management dashboard.
- **Mandatory First-Login Password Reset**: Created `ChangePasswordPage.jsx` and `ProtectedRoute` interceptors enforcing imported students to update default passwords before accessing voting mechanisms.

### Changed
- **Locked Down Public Registration**: Removed the frontend registration view and explicitly disabled the `UserRegistrationView` endpoint to enforce the new closed-roster architecture.
- **User Profile Model Changes**: Added `must_change_password` flag and compound database indexes for optimized bulk querying.

---

## [1.1.0] - 2026-09-05

Minor feature release adding automated election simulation tooling, cryptographic blockchain receipt audit alignment, centralized unit testing, mobile responsiveness overhaul, global table sorting, and interactive user management.

### Added
- **Centralized Unit Testing Suite**:
  - Standardized backend unit tests under `backend/tests/`.
  - Isolated local testing scripts and benchmarks via `.gitignore` to maintain a clean repository.
- **Interactive User Management & Verified Column**:
  - Added the **Verified** sortable column to [`UserManagementPage.jsx`](frontend/src/modules/admin/pages/UserManagementPage.jsx).
  - Converted static status and verification badges in `UserManagementPage.jsx` and `UserDirectoryPage.jsx` into interactive buttons allowing instant click-to-toggle of active status and student verification.
- **Global Table Sorting Rollout**: Added [`SortableHeader`](frontend/src/components/common/SortableHeader.jsx) and [`useTableSort`](frontend/src/hooks/useTableSort.js) across all administration data tables.
- **Brand Identity & Favicon Elevation**:
  - Synchronized high-resolution, auto-trimmed default **E-Botar Banner Logo** (`logo.png`) across frontend assets and public roots.
  - Deployed dedicated circular **"E" + Checkmark** browser tab favicon (`favicon.png` & `favicon.ico`).
- **High-Turnout Election Simulator (`simulate_election`)**: Added Django management command `python backend/manage.py simulate_election` to generate realistic high-turnout voter cohorts (across colleges and courses) with automated ballot casting, blockchain block appending, and receipt issuance.
- **Enhanced Audit Trail Metadata (`VoteReceiptAuditSerializer`)**: Expanded receipt audit serializer with `block_hash`, `previous_hash`, `user_full_name`, `user_username`, `full_receipt_code`, and `vote_status` fields for comprehensive audit visibility.
- **Audit Service Alias (`votingService.getReceiptAudit`)**: Added client-side method alias ensuring reliable integration between receipt audit views and the backend audit endpoint.

### Fixed & Improved
- **System-Wide Mobile Responsiveness Overhaul**:
  - Replaced legacy vertical tab stacking with touch-friendly horizontal scrolling tabs (`.admin-filter-tabs`).
  - Implemented responsive mobile toolbar stacking (`.admin-registry-toolbar-row`): full-width search on top, horizontal scrollable filter pills below.
  - Modernized mobile Admin Dashboard Quick Actions into a balanced 2-column grid (`.admin-quick-actions-grid`).
  - Adjusted mobile action buttons into flexible rows instead of full-width blocks.
- **Voting Status Design System Elevation (`VotingStatusPage.jsx`)**:
  - Brought `/admin/voting-status` into full parity with `/admin/users` (User Management).
  - Integrated `.admin-users-toolbar-card` with magnifying search pill, 300ms debouncing, and one-click clear button.
  - Integrated collapsible Advanced Filters button with dynamic active filter badge counter (`(1)`).
  - Replaced raw text metric summaries with interactive 3-card stat grid (`.admin-users-stats-grid.three-cols`) with dynamic click-to-filter toggles.
- **Global Theme & Token Harmonization**:
  - Aligned primary action buttons, active tab indicators, and brand accents to SSCT Deep Forest Green (`#0b6e3b`).
  - Enforced strict preservation of Red (`#ef4444`) exclusively for destructive/delete/archive actions.
  - Harmonized toolbar search pills across Elections, Applications, and Voting Status.
  - Centralized responsive layout utility classes (`.admin-metrics-stats-grid`, `.admin-toolbar-card`, `.admin-search-pill`) in `admin.css`.
- **Blockchain Audit Hash Linkage Alignment (`VoteReceiptAuditSerializer`)**: Resolved multi-position election audit table alignment by implementing `_ballot_blocks` in `VoteReceiptAuditSerializer` and adding eager prefetching in `audit()` view. Each row now accurately reflects the ballot's entry `previous_hash` and terminal `current_hash`, ensuring consecutive row-to-row cryptographic continuity without N+1 query overhead.
- **Receipt Verification Display Robustness**: Fixed issue in [`VerifyReceiptPage.jsx`](frontend/src/modules/voting/pages/VerifyReceiptPage.jsx) to safely handle structured election metadata objects without rendering errors.
- **Receipt Audit Initial State**: Enhanced [`ReceiptAuditPage.jsx`](frontend/src/modules/admin/pages/ReceiptAuditPage.jsx) to automatically default to the primary election upon initial load.
- **Browser Tab Favicon Link Alignment**: Updated [`frontend/index.html`](frontend/index.html) to link `/favicon.png` and `/favicon.ico` instead of `/logo.png`, ensuring the browser tab correctly renders the new circular **"E" + Checkmark** favicon.
- **Git Ignore Hygiene**: Excluded thesis presentation assets (`THESIS_ASSETS.md`, `THESIS_*.md`) from version tracking.

---

## [1.0.0] - 2026-08-25

Initial release of **E-Botar Lite**, a streamlined, high-performance edition of the university electronic voting system featuring direct candidate management and an append-only cryptographic blockchain ledger.

### Added

#### 1. Cryptographic Blockchain Vote Ledger (`apps/voting`)
- **Append-Only Block Chaining (`VoteBlock`)**: Every ballot cast creates and appends an immutable block linked by SHA-256 cryptographic digests to previous blocks in the chain.
- **Genesis Block Initialization**: Automated genesis block creation upon election start to establish the tamper-evident cryptographic root.
- **Continuous Integrity Audit (`GET /api/voting/results/ledger_integrity/`)**: Real-time blockchain ledger audit endpoint that sequentially verifies hash linkage and immediately flags any database tampering.
- **Audit Dashboard (`/admin/receipt-audit`)**: Administrator interface for running one-click integrity checks across all election ledgers.

#### 2. Cryptographic Vote Receipts (`VoteReceipt`)
- **Instant Digital Receipts**: Generates clean, formatted receipt codes (e.g. `ABCD-EFGH`) immediately upon ballot submission.
- **Public Zero-Knowledge Verification (`/verify-receipt`)**: Voters can verify their ballot's inclusion in the blockchain ledger without exposing private voting choices.
- **Personal Voting History (`/my-votes`)**: Voter ledger interface displaying participated elections and past receipt tokens.

#### 3. Direct Administrative Candidate Management (`apps/candidates`)
- **Direct Candidate Assignment (`/admin/candidates`)**: Administrators assign registered student leaders directly to positions with photo uploads, political party affiliations, and manifestos.
- **Streamlined Workflow**: Eliminates multi-step candidate application queues, file upload reviews, and screening overhead.
- **Status Toggle**: Instant active/inactive candidate status switching with clean status badges.

#### 4. Master Data Registries & Administration
- **Degree Programs & Colleges (`/admin/programs`)**: Full management of departments and courses with CSV bulk import (featuring preview validation and atomic transactions) and CSV export.
- **Election Positions (`/admin/positions`)**: Position creation with maximum candidate limits and display ordering.
- **Political Parties (`/admin/parties`)**: Political party registry with customizable party color themes.
- **User Accounts & Directory (`/admin/users`)**: Searchable user management with role toggling (Admin, Staff, Student), password resets, and account status controls.
- **Voter Turnout Tracking (`/admin/voting-status`)**: Read-only per-election student participation roster.

#### 5. User Interface & Design System
- **Collapsible Sidebar & Navigation**: Responsive desktop collapsible sidebar with active route highlighting, topbar branding, and mobile offcanvas menu.
- **Auth & Profile Flow**: Modernized two-column login (`/login`) and student registration (`/register`) with department/course auto-selectors.
- **KPI Metrics Dashboard (`/admin`)**: Real-time administrative dashboard tracking active elections, total candidates, verified blockchain ballots, and registered student accounts.
- **Simplified Table UI**: Clean, lightweight status pills and compact icon action buttons matching the university design system.

#### 6. Core Algorithms & Security
- **Cryptographic Hashing**: SHA-256 hashing utility with constant-time digest comparison to prevent timing attacks.
- **Efficient Sorting & Aggregation**: In-memory Quicksort and aggregation pipelines for instant election results calculation.
- **JWT Authentication**: SimpleJWT token authentication with automatic refresh rotation and route protection.

#### 7. Developer Tooling & Verification
- **Automated End-to-End Suite (`test_e2e_core.py`)**: Standalone verification script that programmatically tests direct candidate setup, ballot casting, SHA-256 block linking, tamper detection, receipt verification, and results aggregation.
- **Comprehensive Database Seeder (`python backend/manage.py seed_data`)**: Single command to seed demo colleges, courses, positions, parties, active elections, and ready-to-test student/admin accounts.
- **Convenience Workspace Scripts (`package.json`)**: Root runner scripts (`npm run dev`, `npm run build`) delegating to the frontend Vite application.

---

### Removed & Streamlined (vs. Main System)

- **Candidate Application Pipeline**: Removed multi-tier application submission, document screening, and committee review stages in favor of direct candidate management.
- **Heavy PDF Report Engines**: Removed complex multi-thousand-line PDF generation pipelines to maintain a lightweight, fast codebase.
- **Extraneous Dependencies**: Stripped out unnecessary background queue handlers and bloated libraries for maximum speed and simplicity.
