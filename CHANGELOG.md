# Changelog

All notable changes to **E-Botar Lite** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
