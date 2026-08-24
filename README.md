# E-Botar Lite - Streamlined Blockchain Electronic Voting System

**Version 1.0.0** | High-performance, simplified electronic voting platform with an append-only cryptographic blockchain ledger and direct administrative candidate management.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16-red.svg)](https://www.django-rest-framework.org/)
[![React](https://img.shields.io/badge/React-19.2-cyan.svg)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-7.3-purple.svg)](https://vitejs.dev/)
[![License](https://img.shields.io/badge/License-Proprietary-yellow.svg)](#)

---

## 📖 Table of Contents

- [Overview & The Lite Philosophy](#-overview--the-lite-philosophy)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Quick Start Guide](#-quick-start-guide)
- [Default Seed Accounts](#-default-seed-accounts)
- [API Reference](#-api-reference)
- [Testing & Integrity Verification](#-testing--integrity-verification)
- [Project Structure](#-project-structure)

---

## 💡 Overview & The Lite Philosophy

**E-Botar Lite** is a streamlined edition of the E-Botar university voting platform. It strips away extraneous multi-step application workflows, heavy export processors, and bloat to focus entirely on **performance, security, and core democratic functionality**:

1. **Direct Administrative Candidate Management**: Staff and administrators assign student leaders directly to positions with instant modal CRUD—eliminating multi-stage candidate application queues and reviews.
2. **True Cryptographic Ledger (`VoteBlock`)**: Every ballot cast appends an immutable block linked by SHA-256 cryptographic digests to previous blocks. The chain can be audited and verified for tampering in real time.
3. **Cryptographic Vote Receipts**: Voters receive instant formatted receipt codes (e.g. `ABCD-EFGH`) backed by salted SHA-256 digests for public zero-knowledge ballot verification on `/verify-receipt`.
4. **Clean Monolithic Architecture**: Fast, lightweight Django REST API backend coupled with an optimized React + Vite frontend.

---

## 🌟 Key Features

### 🗳️ Student Voter Experience
- **Interactive Ballot**: Clean position-by-position voting interface with candidate photos, political party tags, and manifestos.
- **Vote Anonymization (`AnonVote`)**: Decouples voter identity from vote choices while logging immutable append-only ledger blocks.
- **Instant Digital Receipts (`VoteReceipt`)**: Generates verifiable receipt codes immediately upon ballot submission.
- **Public Receipt Verification**: Any voter can verify whether their ballot was securely included in the blockchain ledger without revealing their specific vote choices.
- **Personal Voting History (`/my-votes`)**: Track elections participated in and retrieve past receipts.
- **Live & Post-Election Statistics**: Turnout percentages, vote tallies, and winner highlights on `/results/:id`.

### 🛡️ Administrative & Election Management
- **Direct Candidate Management (`/admin/candidates`)**: Direct student user assignment to election positions with photo uploads, party affiliations, and active toggles.
- **Election Scheduling (`/admin/elections`)**: Configure USC (University-wide) and Department-level elections with start/end timestamps and position requirements.
- **Blockchain Ledger & Receipt Audit (`/admin/receipt-audit`)**: Real-time hash-chain integrity verification and tamper detection.
- **Master Data Registries**: Full control over Academic Positions (`/admin/positions`), Political Parties (`/admin/parties`), and Degree Programs (`/admin/programs`).
- **Student Voter Status (`/admin/voting-status`)**: Track which registered students have cast their ballots per election.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12, Django 6.1, Django REST Framework, SimpleJWT (JWT Authentication), SQLite / PostgreSQL.
- **Frontend**: React 19, Vite 7.3, Bootstrap 5, Bootstrap Icons, Axios, React Router 7.
- **Security & Algorithms**: SHA-256 Hash Chaining, Constant-Time Hash Digest Verification, In-Memory Quicksort, Aggregation Pipelines.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.12+**
- **Node.js 18+ & npm**

### 1. Backend Setup

```powershell
# Navigate to project root
cd "d:\System Projects\E_Botar-Lite"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt

# Run migrations
python backend/manage.py migrate

# Seed initial database with programs, positions, parties, active election & demo users
python backend/manage.py seed_data

# Start backend development server (Port 8000)
python backend/manage.py runserver 8000
```

### 2. Frontend Setup

```powershell
# In a new terminal, navigate to frontend
cd "d:\System Projects\E_Botar-Lite\frontend"

# Install dependencies
npm install

# Start Vite dev server (Port 5173)
npm run dev
```

### 3. Unified Root Scripts
You can also run frontend scripts directly from the workspace root:

```powershell
npm run dev      # Starts Vite dev server
npm run build    # Compiles production bundle
```

---

## 🔑 Default Seed Accounts

The `seed_data` command creates ready-to-test accounts:

| Role | Username | Password | Access / Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin12345` | Full system access, Direct Candidate CRUD, Elections, Audit, Master Registries |
| **Student Voter 1** | `juan.delacruz` | `student12345` | Student voting, Receipt verification, Profile |
| **Student Voter 2** | `maria.santos` | `student12345` | Student voting, Receipt verification, Profile |
| **Student Voter 3** | `pedro.penduko` | `student12345` | Student voting, Receipt verification, Profile |
| **Student Voter 4** | `ana.reyes` | `student12345` | Student voting, Candidate assignment |

---

## 📡 API Reference

### Authentication & Accounts (`/api/auth/`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/token/` | Obtain JWT access and refresh token pair | Public |
| `POST` | `/api/auth/register/` | Register new student voter account | Public |
| `GET` | `/api/auth/me/` | Current authenticated user profile | Authenticated |
| `GET` | `/api/auth/users/` | List and search users | Staff / Admin |
| `GET` | `/api/auth/programs/` | List departments and courses | Public |

### Elections (`/api/elections/`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/elections/` | List all elections with status filters | Public |
| `POST` | `/api/elections/` | Create a new election | Staff / Admin |
| `GET` | `/api/elections/active/` | Get currently ongoing elections | Public |
| `GET` | `/api/elections/positions/` | Master list of election positions | Public |
| `GET` | `/api/elections/parties/` | Master list of political parties | Public |

### Candidates (`/api/candidates/`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/candidates/` | List candidates (filterable by election/position) | Public |
| `POST` | `/api/candidates/` | **Directly create/assign candidate** | Staff / Admin |
| `PUT` | `/api/candidates/:id/` | Update candidate details / manifesto | Staff / Admin |
| `DELETE` | `/api/candidates/:id/` | Remove candidate | Staff / Admin |
| `POST` | `/api/candidates/:id/toggle_active/` | Toggle candidate active status | Staff / Admin |

### Voting & Blockchain Ledger (`/api/voting/`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/voting/ballots/` | Submit ballot & append to blockchain ledger | Authenticated Voter |
| `GET` | `/api/voting/ballots/my_ballot/` | Retrieve user's submitted ballot | Authenticated Voter |
| `POST` | `/api/voting/receipts/verify/` | Verify vote receipt on blockchain | Public |
| `GET` | `/api/voting/receipts/my_receipts/` | Voter's personal receipt list | Authenticated Voter |
| `GET` | `/api/voting/results/election_results/` | Vote tallies, rankings & winners | Public / Authenticated |
| `GET` | `/api/voting/results/statistics/` | Voter turnout metrics & participation | Public / Authenticated |
| `GET` | `/api/voting/results/ledger_integrity/` | **Verify cryptographic hash chain integrity** | Staff / Admin |

---

## 🧪 Testing & Integrity Verification

### Run Automated Unit Tests
```powershell
& ".\venv\Scripts\python.exe" backend\manage.py test apps.voting
```

### Run End-to-End Core Verification
```powershell
& ".\venv\Scripts\python.exe" test_e2e_core.py
```
*Validates: Admin user setup, Direct Candidate creation, Ballot submission, SHA-256 hash chaining, Sequential ledger tamper detection, Receipt code verification, and Results aggregation.*

### Verify Frontend Production Build
```powershell
cd frontend
npm run build
```

---

## 📁 Project Structure

```
E_Botar-Lite/
├── .gitignore
├── package.json                   # Root convenience scripts
├── README.md                      # Project documentation
├── test_e2e_core.py               # E2E test verification runner
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── backend/                   # Settings, WSGI, URLs
│   └── apps/
│       ├── common/                # Cryptography, Algorithms, Logging, SystemSettings
│       ├── accounts/              # UserProfile, Programs (Departments & Courses), Auth
│       ├── elections/             # SchoolElection, SchoolPosition, Party
│       ├── candidates/            # Direct Candidate CRUD (No applications)
│       └── voting/                # VoteBlock Ledger, VoteReceipt, Ballot, Results
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── assets/                # Styles, design tokens, logo
        ├── components/            # Layout (Topbar, Sidebar), Common UI
        ├── contexts/              # AuthContext, BrandingContext
        ├── hooks/                 # useAuth, useBranding
        ├── modules/
        │   ├── admin/             # Dashboard, Direct Candidates, Elections, Registries
        │   ├── auth/              # Login, Register
        │   ├── candidates/        # Candidate directory & profiles
        │   ├── elections/         # Election browser & details
        │   ├── profile/           # User dashboard & account
        │   ├── results/           # Statistics & vote counts
        │   └── voting/            # Ballot submission & Receipt verification
        ├── routes/                # Route definitions & protected routes
        └── services/              # API clients & service barrel
```

---

## 📄 License
Proprietary — Developed for Student Government and Institutional Online Voting.