# Implementation Plan: E_Botar-Lite

> **Status**: ✅ **COMPLETED (v1.1.0)**  
> **Target**: University Blockchain-Backed Electronic Voting System (Lite Edition)  
> **Last Updated**: 2026-08-29

A streamlined, robust, and clean version of **E-Botar** focusing strictly on its core strengths: **Blockchain-backed voting ledger**, **voter receipt verification**, **real-time election results and statistics**, and **direct admin candidate management**.

---

## Executive Summary & Architectural Decisions

- [x] **Direct Candidate Management**: Administrators directly manage candidate rosters (create, edit, activate/deactivate, delete) via `/admin/candidates`, eliminating multi-tier application workflows.
- [x] **Append-Only Blockchain Ledger**: Preserved SHA-256 block hash chaining, genesis block initialization, tamper detection, and zero-knowledge voter receipt verification.
- [x] **Live Results & Statistical Analytics**: Preserved turnout calculation, candidate rankings, vote count bars, and winner highlights.
- [x] **Standardized Environment & Clean Git Hygiene**: Single root `.env.example`, Gunicorn `Procfile`, `.gitattributes` LF normalization, `.gitignore` ignoring `.env`, `venv/`, `node_modules/`, and dynamic databases.

> [!TIP]
> For the step-by-step commit, push, branch-leveling, and PythonAnywhere deployment instructions, see the [Git Versioning & Release Guide](guide.md).

---

## System Architecture

```text
E_Botar-Lite/
├── .gitattributes        # Standard LF line ending normalization
├── .gitignore            # Git exclusion rules for venv, .env, db.sqlite3, dist
├── .env.example          # Environment template for local & cloud deployments
├── Procfile              # Web process definition for Gunicorn hosting
├── package.json          # Root orchestration runner for frontend commands
├── pyrightconfig.json    # Project-wide Python type checking and venv config
├── CHANGELOG.md          # Release notes and semantic version history
├── README.md             # Developer setup and architectural documentation
│
├── backend/              # Django REST Framework Backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── backend/          # Core Django settings, URLs, WSGI
│   └── apps/
│       ├── accounts/     # User authentication, UserProfile, Department/Course programs
│       ├── elections/    # SchoolElection, SchoolPosition, ElectionPosition, Party
│       ├── candidates/   # Direct Candidate model & Admin CRUD ViewSet
│       ├── voting/       # Blockchain VoteBlock, Ballot, Receipts, Statistics, Verification
│       └── common/       # Security middleware, crypto utils, ActivityLog, simulators
│
└── frontend/             # React (Vite) Single Page Application
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── constants.js
        ├── assets/       # Design tokens, CSS architecture, university branding
        ├── components/   # Navbar, Footer, ProtectedRoute, Modals, Status Badges
        ├── contexts/     # AuthContext, BrandingContext
        ├── routes/       # AppRoutes.jsx
        ├── services/     # api.js, authService, candidateService, electionService, votingService
        └── modules/
            ├── auth/       # Login, Register
            ├── elections/  # Election List, Election Details
            ├── candidates/ # Public Candidate List & Manifestos
            ├── voting/     # Voting Ballot, My Votes, Receipt Verification
            ├── results/    # Results & Live Statistics View
            ├── profile/    # Student Dashboard & Profile
            └── admin/      # Admin Dashboard, Candidate Management, Election Management,
                            # Position, Party, Program, User Management, Voting Audit
```

---

## Phase Execution Checklist

### Phase 1: Environment & Repository Foundations
- [x] Create comprehensive root `.gitignore` and `frontend/.gitignore`.
- [x] Configure `backend/requirements.txt` with Django, DRF, SimpleJWT, Gunicorn, WhiteNoise, and Cloudinary.
- [x] Configure `frontend/package.json` with React, Lucide icons, React Router, Axios, and Vite.
- [x] Create root `package.json` proxy scripts (`dev`, `build`, `preview`).
- [x] Set up `.gitattributes`, root `Procfile`, and root `pyrightconfig.json`.

---

### Phase 2: Backend Core Services

#### 1. Accounts & Master Data (`apps/accounts`, `apps/elections`)
- [x] `UserProfile` model with Student ID, College Department, Course, Section, and status flags.
- [x] `Program` model with Department and Course hierarchy.
- [x] CSV bulk import/export for academic programs with preview validation and atomic transactions.
- [x] JWT Authentication endpoints (Login, Register, Token Refresh, Profile).
- [x] `SchoolElection`, `SchoolPosition`, `ElectionPosition`, and `Party` registries.

#### 2. Direct Candidate Management (`apps/candidates`)
- [x] Streamlined `Candidate` model linking User, Election, Position, Party, Manifesto, and Photo.
- [x] Admin `CandidateViewSet` supporting full CRUD and active/inactive status toggling.
- [x] Public read-only endpoints for candidate rosters and manifestos.

#### 3. Blockchain Ledger & Cryptographic Receipts (`apps/voting`)
- [x] `VoteBlock` append-only blockchain ledger with SHA-256 hash chaining (`previous_hash`, `current_hash`, `block_data`).
- [x] Automated genesis block creation upon election start.
- [x] `VoteReceipt` generation with formatted receipt codes (e.g. `ABCD-EFGH`) and SHA-256 verification hash.
- [x] Double-blind vote anonymization with `AnonVote` separation.
- [x] Continuous ledger integrity check endpoint (`GET /api/voting/results/ledger_integrity/`).
- [x] Public zero-knowledge receipt verification endpoint (`POST /api/voting/receipts/verify/`).
- [x] Real-time turnout calculation and position-by-position results aggregation.

#### 4. Simulation & Diagnostic Tooling (`apps/common`)
- [x] `simulate_election` Django management command for high-turnout test cohort generation.
- [x] `seed_data` management command for instant test environment bootstrapping.
- [x] `ActivityLog` security and event logging.

---

### Phase 3: Frontend Application

#### 1. UI Shell & Design System
- [x] Collapsible sidebar and topbar navigation with active route indicators.
- [x] Responsive layout with CSS design system tokens and glassmorphism styling.
- [x] Dark/light theme accents and mobile offcanvas menu.

#### 2. Voter & Student Experience
- [x] Two-column authentication flow (`/login`, `/register`).
- [x] Student Dashboard (`/dashboard`) with active elections and turnout cards.
- [x] Step-by-step Voting Ballot (`/vote/:id`) with ballot review modal.
- [x] Instant Receipt Modal with one-click copy and download functionality.
- [x] Independent Receipt Verification tool (`/verify-receipt`).
- [x] Personal Voting History (`/my-votes`).
- [x] Live Election Results & Analytics (`/results/:id`).

#### 3. Administrative Control Center
- [x] Admin KPI Overview (`/admin`) tracking elections, candidates, votes, and registered voters.
- [x] Candidate Management (`/admin/candidates`) modal-driven CRUD interface.
- [x] Election Management (`/admin/elections`) and Election Form (`/admin/elections/new`).
- [x] Master registries: Positions (`/admin/positions`), Parties (`/admin/parties`), Programs (`/admin/programs`), Users (`/admin/users`).
- [x] Blockchain Audit Trail (`/admin/receipt-audit`) with hash chain verification.

---

### Phase 4: Student Roster Synchronization, Google Auto-Link & Registration Lockdown (Target: v2.0.0)

#### Phase 4.0: Backend Modularization, Database Indexing & Token Resilience
- [ ] **Accounts Modularization & Google Auto-Link**: Extract Google OAuth authentication logic into `backend/apps/accounts/oauth.py` and Program CSV logic into `backend/apps/accounts/csv_services.py` to declutter `views.py`. Implement seamless auto-linking for pre-imported student emails logging in via verified Google OAuth.
- [x] **Database Indexing for Scale**: Add `db_index=True` on `UserProfile.year_level` and `UserProfile.is_verified`, and add compound index `models.Index(fields=['department', 'year_level'])` to accelerate high-volume student roster queries and permission checks.
- [x] **First-Login Schema Prep**: Add `must_change_password = models.BooleanField(default=False, db_index=True)` to `UserProfile` model and generate clean Django migration.
- [x] **Token Refresh Mutex**: In `frontend/src/services/api.js`, add a request queue for token refreshes to prevent concurrent 401 logout stampedes.

#### Phase 4.1: Core Student Excel/CSV Roster Parsing Engine
- [x] **Dual-Format Parser (`apps/accounts/services/roster_sync.py`)**: Support both `.xlsx` (via `openpyxl`) and `.csv` roster file uploads.
- [x] **Forgiving Data Normalization & Sanitization**:
  - Automatically strip leading/trailing whitespace from all fields.
  - Support case-insensitive department and course code lookups (`bscs` matches `BSCS`).
  - Parse year level flexibly (`4`, `4th`, `4th Year`, `Year 4`).
  - Tolerate and ignore trailing blank rows from spreadsheet exports.
- [x] **Clear, Actionable Error Reporting**: Return direct row-level error descriptions (e.g., `Row 14 [Email]: 'john@ssu' is not a valid email address`) for instant debugging.
- [x] **Roster Diff Classification**: Categorize rows into New Students, Existing (to be updated), and Unlisted (flagged for deactivation).

#### Phase 4.2: Roster Import API Endpoints & Transaction Atomicity
- [x] **Roster Preview Endpoint (`POST /api/auth/students/roster-preview/`)**: Parse and validate uploaded roster in memory without writing to database; return detailed statistics and error rows.
- [x] **Roster Sync Execution Endpoint (`POST /api/auth/students/roster-import/`)**: Execute atomic sync (`transaction.atomic()`) with chunked batch processing, create audit log entries (`ActivityLog`), and invalidate voting cache.
- [x] **Rate Limiting Guard**: Omitted from Lite version to keep dependencies minimal (uses default DRF throttling instead).

#### Phase 4.3: Frontend Administrative Roster Sync UI & Pre-Import Preview Modal
- [x] **Sync Roster Button & Dropzone**: Add "Sync Student Roster" trigger in `UserManagementPage.jsx` with file dropzone supporting `.xlsx` and `.csv`.
- [x] **Interactive Preview Modal**: Display detected row counts, new student count, updated student count, and an interactive validation error table before confirming execution.
- [x] **Sync Progress & Status Feedback**: Provide real-time loading feedback and confirmation summary toast.

#### Phase 4.4: Registration Lockdown, Roster-Restricted Login & First-Login Password Reset
- [x] **Lockdown Public Registration**: Disable public self-registration `/register` route and remove registration links from `LoginPage.jsx`.
- [x] **Roster-Restricted Google Login**: When registration is locked down, reject Google sign-in attempts for unlisted emails with a clear error prompt (*"Your email is not listed in the active student roster. Please contact the administrator or Office of Student Affairs."*).
- [x] **First-Login Password Reset Enforcement**: Check `must_change_password` flag on login response; render mandatory password update modal before granting full system access.

#### Phase 4.5: Automated Verification & Documentation Synchronization
- [ ] **Unit & Parser Tests**: Add tests covering valid and malformed Excel/CSV rosters, duplicate emails, and invalid student IDs.
- [ ] **Full Test Suite Execution**: Run `python backend/manage.py test` and verify zero failures.
- [ ] **Frontend Build Verification**: Run `npm run build` and ensure zero errors.
- [ ] **Documentation Sync**: Synchronize `CHANGELOG.md`, `README.md`, and project documentation.

---

### Phase 5: Architecture Simplification & Production Optimization (Target: v3.0.0)

Based on the v5.0.0 milestone from the main E-Botar repository, the Lite version will adopt key architectural simplifications and performance optimizations:

#### Phase 5.1: Canonical Versioned Gateway & API Minimization
- [ ] **`/api/v1/` Routing Prefix**: Standardize all backend domain endpoints under canonical versioned routes (`/api/v1/`) while maintaining backward compatibility via `/api/` aliases.
- [ ] **Framework-Native ViewSets**: Refactor bespoke API endpoints to rely on DRF's `ModelViewSet` and dynamic query parameters (e.g. `?status=active`, `?compact=true`).
- [ ] **Client Adapter Pattern**: Update frontend fetch calls to automatically target `/api/v1/` via a unified HTTP base configuration.

#### Phase 5.2: ACID Concurrency Guards & Domain Isolation
- [ ] **Ballot Submission Service (`BallotSubmissionService`)**: Decouple voting logic from views into a dedicated service layer.
- [ ] **Row-Level Locking**: Implement `select_for_update()` inside `transaction.atomic()` to guarantee safe concurrency and strictly prevent double-voting anomalies under load.
- [ ] **Constant-Time Cryptography**: Upgrade vote receipt and block chain validation logic to use `hmac.compare_digest` to mitigate side-channel timing attacks.

#### Phase 5.3: Data Streaming & Bounded Caching
- [ ] **Lazy Generator Streaming**: Replace large list-accumulated payloads on exports (e.g. Audit Logs, Results CSVs) with Django's `StreamingHttpResponse` to enforce constant server memory ($O(1)$) usage.
- [ ] **Sliding Window Pagination**: Implement headless bounding (`windowSize = 4`) for large list renders to eliminate DOM bloat on the frontend.
- [ ] **Direct SQL Aggregation**: Refactor in-memory analytics loops (e.g. election results) into optimized `.annotate(Count())` queries returning direct JSON responses.

#### Phase 5.4: Infrastructure Hardening & Application Stability
- [ ] **Active Unthrottled Health Probes**: Upgrade `/health/` endpoints to verify live PostgreSQL connectivity and Cache availability without throttling constraints.
- [ ] **Fail-Fast Secrets**: Enforce strict `ValueError` raising on application boot in production if an insecure default `SECRET_KEY` is detected.
- [ ] **React Error Boundary**: Wrap frontend `AppRoutes` in a global `ErrorBoundary` to prevent total unmount whiteout during rendering errors.
- [ ] **Unified Toast Notifications**: Consolidate alert feedbacks across the UI into a centralized, animated floating toast notification system.

---

### Phase 6: Algorithmic Hardening & Vulnerability Remediation (Target: v3.1.0)

Based on the algorithmic audit of the main E-Botar system, these optimizations will be applied to the Lite version to prevent Out-of-Memory (OOM) and CPU bottlenecks under high student volume:

#### Phase 6.1: Cryptographic Memory Optimization
- [ ] **Stream Blockchain Ledger Verification**: Refactor `verify_election_vote_chain` in `VoteBlock` to stream results using Django's `.iterator(chunk_size=2000)` instead of forcing a full memory materialization via `list()`. This prevents memory bloat during full campus audit trails.

#### Phase 6.2: Database-Level Aggregation
- [ ] **Push Aggregation to PostgreSQL Engine**: Remove any custom Python-based `AggregationAlgorithm` loops over `list(QuerySet)` within statistics/turnout generation. Use native PostgreSQL `COUNT()` aggregation via `.annotate(Count('id'))` directly on queries to eliminate CPU bottlenecks.

#### Phase 6.3: Payload Limits & Upload Hardening
- [ ] **OOM Protection via File Limiters**: Ensure `DATA_UPLOAD_MAX_MEMORY_SIZE` and `FILE_UPLOAD_MAX_MEMORY_SIZE` are strictly set in `settings.py`. When Phase 4 Roster CSV/Excel syncing is implemented, ensure it uses chunked streaming (`.chunks()`) rather than `.read()` into memory.

#### Phase 6.4: Code Defragmentation
- [ ] **Component & File Consolidation**: Merge fragmented, single-use React components and tiny utilities into cohesive, unified modules (e.g., standardizing status pills, modal wrappers, and data tables) to reduce module instantiation overhead.

---

## Verification & Status

- [x] **Automated Django Check**: `python backend/manage.py check` passes with 0 issues.
- [x] **Automated End-to-End Test Suite**: `test_e2e_core.py` passes all phases (setup, voting, block chaining, tampering detection, receipt verification).
- [x] **Frontend Production Build**: `npm run build` completes successfully.
