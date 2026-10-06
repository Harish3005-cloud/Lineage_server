# LINEAGE Server — FastAPI Backend

> *"Every contribution has a lineage. Every reward has evidence."*

FastAPI REST backend for **LINEAGE**, providing secure authentication, access-controlled project management, versioned charter governance, AI Gateway logging, TF-IDF integrity verification, cryptographic SHA-256 ledger chaining, and escrow payouts.

---

## 🚀 Technology Stack

* **Framework**: Python FastAPI
* **ORM & Database**: SQLAlchemy + PostgreSQL (with SQLite fallback for local development)
* **Validation**: Pydantic v2 schemas
* **Authentication**: JWT Bearer Tokens with Passlib/Bcrypt password hashing

---

## 📁 Repository Structure

```
app/
├── api/
│   ├── api.py                  # Main API router registry (/api)
│   ├── deps.py                 # JWT dependency & DB session injectors
│   └── routes/
│       ├── auth.py             # Login, register, current user endpoints
│       ├── users.py            # User management endpoints
│       └── project_members.py  # Project member management endpoints
├── core/
│   ├── config.py               # Environment configuration
│   └── security.py             # JWT token creation & password hashing
├── db/
│   ├── database.py             # Database engine & SessionLocal
│   └── models/                 # SQLAlchemy database models
│       ├── user.py
│       ├── project.py
│       ├── project_member.py
│       ├── charter.py
│       ├── milestone.py
│       ├── contribution.py
│       ├── review.py
│       ├── ledger_entry.py
│       ├── escrow.py
│       ├── payout.py
│       └── dispute.py
└── schemas/                    # Pydantic validation schemas
```

---

## 🛠️ Quick Start

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

* **Interactive API Documentation (Swagger)**: `http://localhost:8000/docs`
* **Alternative API Documentation (ReDoc)**: `http://localhost:8000/redoc`
* **Health Check**: `http://localhost:8000/health`

---

## 🔒 Security & Access Control

* **Confidential Brief Security**: Confidential research details are restricted at the database/API endpoint level and only returned to authorized project members after charter sign-off.
* **Admin Identification**: Ledger entries automatically derive `admin_id` directly from the authenticated JWT token.
* **Under-18 Minor Safeguards**: Automatically identifies minor users (`age < 18`) and tracks `guardian_consent` status (`pending`, `approved`, `not_required`).
