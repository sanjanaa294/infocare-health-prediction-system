# 🩺 InfoCare: AI-Powered Health Prediction & Patient Management System

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite3-HealthRecords-003B57.svg)](https://www.sqlite.org/)
[![OpenRouter API](https://img.shields.io/badge/OpenRouter-OpenAI--Compatible-6366F1.svg)](https://openrouter.ai/)
[![Tests](https://img.shields.io/badge/Tests-29%20Passed-success.svg)](https://pytest.org/)

A full-stack, clinical-grade patient management and automated health observation platform. The system ingests patient demographics and blood biomarker metrics (Fasting Glucose, Haemoglobin, Total Cholesterol), validates all inputs strictly via Pydantic on the backend, integrates with the **OpenRouter API** using the OpenAI-compatible Chat Completions format to synthesize structured preliminary health observations, and persists records in an ACID-compliant SQLite database via SQLAlchemy ORM.

---

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Technology Stack](#-technology-stack)
4. [Project Architecture](#-project-architecture)
5. [Database Design](#-database-design)
6. [Data Validation Rules](#-data-validation-rules)
7. [External AI API Integration (OpenRouter)](#-external-ai-api-integration-openrouter)
8. [API Endpoints Reference](#-api-endpoints-reference)
9. [Technical Assessment 10 Test Cases](#-technical-assessment-10-test-cases)
10. [Installation & Setup](#-installation--setup)
11. [Running the Application](#-running-the-application)
12. [Running Automated Tests](#-running-automated-tests)
13. [Demonstration Video Recording Guide](#-demonstration-video-recording-guide)

---

## 🌟 Project Overview
This application was engineered to fulfill the technical assessment criteria for an **AI Growth & Automation Associate**. It showcases senior-level software engineering principles:
- **Clean Architecture & Separation of Concerns**: Strict boundaries between presentation (Jinja2 + Bootstrap 5), routing (FastAPI Routers), data modeling (SQLAlchemy ORM), business logic/validation (Pydantic), and external services (OpenRouter AI Service).
- **Production-Ready Medical Safety Guardrails**: AI-generated remarks adhere to strict medical disclaimers, explaining that interpretations depend on lab-specific reference ranges and clinical history without prescribing medication or claiming definitive disease diagnosis.
- **Fail-Safe Asynchronous Resilience**: External AI API timeouts or failures do not crash the app or block patient creation; records are persisted with a `FAILED` status and provide users with a 1-click retry mechanism.
- **Duplicate Support**: Support for identical patient data submissions stored as distinct database entries without restrictive unique constraints.

---

## 🚀 Key Features
- **Interactive Clinical Dashboard**: High-level summary metrics (Total Patients, AI Processed, Pending/Attention, System Status) with real-time patient tables.
- **Comprehensive CRUD Operations**:
  - **Create**: Add new patients with blood panel values, automatically triggering AI observation generation.
  - **Read**: Browse all patient records with real-time client/server search filtering by Name, Email, or Patient ID.
  - **Update**: Edit patient demographics or blood biomarkers. Modifying biomarker values automatically triggers fresh AI observations.
  - **Delete**: Soft/hard removal with an interactive safety confirmation modal.
- **Interactive Assessment Benchmark Suite**: A built-in quick-fill panel on the Add Patient form allows evaluators to load any of the 10 benchmark records with one click and observe live backend validation in action.
- **Interactive Swagger Documentation**: Full OpenAPI schema available out of the box at `/docs`.

---

## 💻 Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons, Vanilla JS | Responsive, modern clinical dashboard and forms |
| **Backend Framework** | Python 3.13+, FastAPI, Starlette, Uvicorn | High-performance asynchronous REST API |
| **Data Validation** | Pydantic v2 | Strict backend data schema validation |
| **Database** | SQLite3 (`health_records.db`) | Relational transactional persistence |
| **ORM** | SQLAlchemy 2.0+ | Object-relational mapping & schema definitions |
| **External AI API** | OpenRouter Chat Completions (`openai` SDK / `httpx`) | OpenAI-compatible endpoint (`https://openrouter.ai/api/v1`) |
| **Testing** | Pytest 9+, HTTPX | Comprehensive automated unit and integration tests |

---

## 🏗 Project Architecture

```
health_prediction_app/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app factory, lifespan, routing & template mounting
│   ├── database.py              # SQLAlchemy engine, session maker & dependency injection
│   ├── models.py                # Database models (Patient ORM table)
│   ├── schemas.py               # Pydantic validation schemas (PatientCreate, PatientUpdate, etc.)
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── patients.py          # CRUD REST endpoints (/api/patients)
│   │   └── health_ai.py         # AI status, preview, and dashboard stats (/api/ai)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── ai_service.py        # OpenRouter API client, medical safety prompt & retry logic
│   │
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html            # Common layout, navbar, modals & toasts
│   │   ├── dashboard.html       # Analytics overview & recent records
│   │   ├── patients.html        # Directory with search & full CRUD table
│   │   ├── add_patient.html     # Registration form with Assessment Test Case Loader
│   │   └── edit_patient.html    # Patient edit form with dynamic AI refresh
│   │
│   └── static/
│       ├── css/
│       │   └── style.css        # Professional medical theme styling
│       └── js/
│           └── app.js           # AJAX handlers, UI updates, modals & test loaders
│
├── tests/
│   ├── __init__.py
│   ├── test_patients.py         # End-to-end CRUD, duplicates, delete, AI failures
│   └── test_validation.py       # Date, email, numeric, and negative constraint tests
│
├── .env.example                 # Template for environment variables
├── .gitignore                   # Excludes virtual env, databases, keys, and caches
├── requirements.txt             # Verified pinned dependencies
├── test_openrouter_live.py      # Live OpenRouter integration and CRUD verification script
├── verify_assessment.py         # Automated CLI benchmark runner for the 10 test cases
├── README.md                    # Project documentation
└── run.py                       # Server startup script
```

---

## 🗄 Database Design

The application uses SQLite (`health_records.db`) managed through SQLAlchemy.

### `patients` Table Schema

| Column Name | SQL Type | Modifiers | Description |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY, AUTOINCREMENT` | Unique numeric identifier |
| `full_name` | `VARCHAR(255)` | `NOT NULL` | Patient's legal name |
| `date_of_birth` | `DATE` | `NOT NULL` | Normalized date of birth (`YYYY-MM-DD`) |
| `email` | `VARCHAR(255)` | `NOT NULL, INDEX` | Email address (Non-unique to allow duplicates) |
| `glucose` | `FLOAT` | `NOT NULL` | Fasting blood glucose in mg/dL |
| `haemoglobin` | `FLOAT` | `NOT NULL` | Blood haemoglobin in g/dL |
| `cholesterol` | `FLOAT` | `NOT NULL` | Serum total cholesterol in mg/dL |
| `remarks` | `TEXT` | `NULLABLE` | OpenRouter AI-generated clinical observation |
| `ai_status` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'PENDING'` | Status: `COMPLETED`, `PENDING`, or `FAILED` |
| `created_at` | `DATETIME` | `NOT NULL` | UTC creation timestamp |
| `updated_at` | `DATETIME` | `NOT NULL` | UTC last updated timestamp |

> **Design Choice**: The `email` column deliberately omits a unique constraint. Per assessment guidelines, duplicate entries (e.g. Assessment Test 1 and Test 6) must both be stored as separate records.

---

## 🛡 Data Validation Rules

All validation occurs strictly on the **Python backend** using Pydantic:

1. **Full Name**:
   - Required, minimum 2 characters.
   - Trims extraneous leading/trailing spaces.
   - Rejects empty strings or whitespace-only inputs.
2. **Date of Birth**:
   - Accepts both `DD/MM/YYYY` and `DD.MM.YYYY` (as well as standard ISO `YYYY-MM-DD`).
   - Rejects invalid calendar dates (e.g., `31.11.2001` — November has only 30 days).
   - Rejects future dates (e.g., `19.10.2030`).
   - Rejects dates prior to 1890.
3. **Email Address**:
   - Required, normalized to lowercase.
   - Validates proper RFC structure (`username@domain.tld`).
   - Rejects malformed addresses such as `hunter@gmail` (no domain extension) and `Kris.wu.gmail.com` (no `@` symbol).
4. **Blood Test Metrics (Glucose, Haemoglobin, Cholesterol)**:
   - Must be valid numeric values (integers or floats).
   - Rejects empty values, non-numeric strings, `NaN`, and `Infinity`.
   - Rejects negative values (`< 0`).

---

## 🤖 External AI API Integration (OpenRouter)

AI integration is isolated inside [`app/services/ai_service.py`](file:///app/services/ai_service.py) using the OpenAI-compatible Chat Completions API with OpenRouter.

### Configuration
- **Base URL**: `https://openrouter.ai/api/v1`
- **Environment Variables**:
  - `OPENROUTER_API_KEY`: OpenRouter bearer authentication key.
  - `OPENROUTER_MODEL`: Model slug (default: `openai/gpt-4o-mini`).

### Prompt Architecture & Medical Guardrails
```python
def build_health_prompt(glucose: float, haemoglobin: float, cholesterol: float) -> str:
    return f"""...
    Please generate a concise health observation report (3 to 5 sentences) addressing:
    1. General Interpretation
    2. Potential Health Risk Indicators
    3. Clinical Summary
    4. Professional Recommendation
    MANDATORY MEDICAL SAFETY GUIDELINES:
    - Clearly label this as AI-generated informational guidance.
    - Do NOT provide a definitive medical diagnosis.
    - Do NOT prescribe medication or treatments.
    - State clearly that clinical interpretation depends on laboratory-specific reference ranges.
    """
```

### Error Handling & Resilience
- **API Key Missing/Invalid**: Catches missing or invalid key, records `ai_status = "FAILED"`, and returns a clear descriptive message without crashing.
- **Timeouts & Rate Limits**: Explicitly catches `RateLimitError` (HTTP 429) and `APITimeoutError` gracefully. The patient record is safely preserved in SQLite.
- **Key Protection**: Exception messages are sanitized to guarantee API keys are never exposed in user responses or server logs.

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `GET` | `/api/patients` | Retrieve all patient records (supports `?search=` query) | `200 OK` |
| `GET` | `/api/patients/{id}` | Retrieve single patient record by ID | `200 OK` / `404 Not Found` |
| `POST` | `/api/patients` | Create patient, validate, call OpenRouter AI, persist record | `201 Created` / `422 Unprocessable` |
| `PUT` | `/api/patients/{id}` | Update patient details (regenerates AI if biomarkers change) | `200 OK` / `404 Not Found` |
| `DELETE` | `/api/patients/{id}` | Delete patient record from SQLite database | `200 OK` / `404 Not Found` |
| `POST` | `/api/patients/{id}/generate-remarks` | Manually retry or regenerate AI remarks | `200 OK` / `404 Not Found` |
| `GET` | `/api/ai/status` | Check OpenRouter API configuration and active model | `200 OK` |
| `GET` | `/api/ai/dashboard-stats` | Retrieve aggregate counts and biomarker averages | `200 OK` |

---

## 🧪 Technical Assessment 10 Test Cases

The application was tested against the 10 benchmark test records from the assessment document:

| # | Name | DOB | Email | Glu | Hb | Chol | Expected Action | Actual Result |
|---|---|---|---|---|---|---|---|---|
| **1** | Robyn Pears | 28.01.1960 | gokul@infocare.com | 232 | 13.5 | 180 | **Save (Valid)** | ✅ **Saved (ID #1)** |
| **2** | John Hunter | 10.12.1990 | hunter@gmail | 94 | 15.0 | 200 | **Reject (Invalid Email)** | ❌ **Rejected: missing domain extension** |
| **3** | Darryl Tim | 12.11.1993 | timd@smh.com.au | 240 | 18.6 | 326 | **Save (Valid)** | ✅ **Saved (ID #2)** |
| **4** | Peter Larry | 31.11.2001 | Larry@hotmail.com | 88 | 11.5 | 165 | **Reject (Invalid Date)** | ❌ **Rejected: Nov has 30 days** |
| **5** | Sam Kerr | 09.12.2006 | sam@news.com.au | 198 | 8.9 | 192 | **Save (Valid)** | ✅ **Saved (ID #3)** |
| **6** | Robyn Pears | 28.01.1960 | robyn@gmail.com | 232 | 13.5 | 180 | **Save (Duplicate)** | ✅ **Saved as distinct ID (#4)** |
| **7** | Madison XI | 12.09.1998 | madison@hotmail.com | 85 | 7.6 | 163 | **Save (Valid)** | ✅ **Saved (ID #5)** |
| **8** | Kris Wu | 19.10.2030 | Kris.wu.gmail.com | 79 | 16.5 | 197 | **Reject (Future Date & Email)** | ❌ **Rejected: Future date + no @** |
| **9** | Tenille Singh | 30.11.1991 | Tenille@yahoo.com | 101 | 15.0 | 310 | **Save (Valid)** | ✅ **Saved (ID #6)** |
| **10** | Prem Kumar | 28.04.1990 | prem@telstra.com | 155 | 12.5 | 265 | **Save (Valid)** | ✅ **Saved & later deleted per demo** |

**Assessment Summary Result:**
- **7 Successfully Validated Records**
- **3 Correctly Rejected Records** with transparent, actionable validation error feedback.

---

## ⚙ Installation & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Git

### 1. Clone or Open the Repository
```bash
git clone <your-repository-url>
cd infocare
```

### 2. Create and Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and configure your OpenRouter credentials:
```ini
OPENROUTER_API_KEY=sk-or-v1-...your_actual_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
DATABASE_URL=sqlite:///./health_records.db
HOST=127.0.0.1
PORT=8000
```
> **Note**: An API key can be obtained from [OpenRouter](https://openrouter.ai/keys). If run without an API key, the application functions fully for all CRUD and validation operations, with the AI status cleanly displaying "API Key Not Configured" and preserving records.

---

## ▶ Running the Application

Start the web application using the launcher:
```bash
python run.py
```
Or directly via Uvicorn:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Access the application in your browser:
- **Clinical Dashboard**: [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)
- **Patient Directory**: [http://127.0.0.1:8000/patients](http://127.0.0.1:8000/patients)
- **Add Patient Form**: [http://127.0.0.1:8000/patients/add](http://127.0.0.1:8000/patients/add)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Running Automated Tests

Run the full automated test suite (29 tests) using Pytest:
```bash
pytest -v
```

Run the OpenRouter live integration test:
```bash
python test_openrouter_live.py
```

Run the assessment benchmark verification script:
```bash
python verify_assessment.py
```

All 29 tests cover:
- Valid patient creation and date formats (`DD/MM/YYYY`, `DD.MM.YYYY`, ISO)
- Rejection of invalid calendar dates (`31.11.2001`)
- Rejection of future dates (`19.10.2030`)
- Rejection of malformed emails (`hunter@gmail`, `Kris.wu.gmail.com`)
- Numeric validations (non-numeric, negative values, NaN, Infinity)
- Duplicate entry handling
- Single patient and list retrieval
- Patient update and automatic AI remarks regeneration
- Patient deletion
- External AI API failure tolerance and recovery

---

## 🔒 Security & Data Privacy Notice
- No API keys or credentials are hardcoded or tracked in Git.
- The `.gitignore` file strictly excludes `.env`, `*.db`, `.venv`, and cache files.
