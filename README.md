# AI-Powered Code Review and Error Detection Platform Using Explainable AI

> **Final-Year B.Tech Project**  
> **Domain:** Artificial Intelligence + Machine Learning + Explainable AI + Software Engineering + Static Code Analysis + Bug Detection + Full Stack Development  
> **Target OS:** Windows 11 / Windows 10 with VS Code

---

## 1. Project Overview & Abstract

Modern software engineering demands high standards of code security, correctness, and maintainability. While traditional static analyzers (such as Pylint, Bandit, and ESLint) are deterministic and reliable at pattern-matching, they often produce isolated warning messages without contextual reasoning or actionable repairs. Conversely, modern Large Language Models (LLMs) excel at contextual understanding and code explanation but can occasionally hallucinate issues when ungrounded.

This platform implements a **Hybrid Analysis Pipeline** that marries the deterministic precision of static analysis with the contextual synthesis and explainability of AI reasoning:
1. **Source Code Ingestion:** Pasted code snippet or single-file upload with automatic language detection.
2. **Syntax & AST Parsing:** Language-aware parsing (Python `ast`, JavaScript/Java structural checks) extracting complexity metrics and catching syntax anomalies without executing untrusted code.
3. **Multi-Tool Static Analysis:** Orchestration of Pylint, Bandit, Semgrep, and ESLint normalized into a unified finding schema.
4. **AI Reasoning & Local Offline Fallback:** Context-grounded LLM review (Gemini / OpenAI API) combined with a deterministic offline rule engine so the platform remains 100% operational even without an active internet connection or API key.
5. **Finding Fusion & Deduplication:** Proximity and semantic similarity clustering that merges overlapping static and AI findings, tracking combined evidence sources (`["static", "llm"]`).
6. **5-Dimension Explainable AI (XAI):** Explicitly answers *What happened*, *Where did it happen*, *Why is it a problem*, *What is the evidence*, and *How can it be fixed*.
7. **Automated Fix Generation & Visual Code Diff:** Generates remediations with visual diffs and copy/apply options without overwriting source code automatically.
8. **Multi-Dimensional Quality Scoring:** Computes deterministic scores for Security (25%), Correctness (30%), Maintainability (20%), Style (10%), and Complexity (15%).
9. **Relational MySQL Persistence:** Stores users, reviews, findings, and suggestions with foreign keys and cascade rules.
10. **Interactive React Dashboard:** Real-time analytics, scorecards, review history, and interactive finding inspector.

---

## 2. System Architecture

```
User / Developer
      │
      ▼
React Dashboard (Vite + React.js + Monaco Editor)
      │  (REST API / JWT Bearer)
      ▼
FastAPI REST Backend
      │
      ├─► Input Validation & Language Detection
      ├─► Syntax Parsing & AST Complexity Metrics
      │
      ├─► Static Analysis (Pylint + Bandit + ESLint + Semgrep)
      │
      ├─► Context-Grounded LLM Analysis (Gemini / OpenAI)
      │   └─► Resilient Offline Fallback Rules ("Local Static Analysis")
      │
      ├─► Finding Fusion & Deduplication (Merges sources: ["static", "llm"])
      │
      ├─► 5-Dimension Explainability Engine (What, Where, Why, Evidence, Fix)
      │
      ├─► Quality Scoring Formula:
      │   Overall = (Security × 0.25) + (Correctness × 0.30) + 
      │             (Maintainability × 0.20) + (Style × 0.10) + (Complexity × 0.15)
      │
      ▼
MySQL Relational Database (code_review_db)
      │
      ▼
React Dashboard + History Table + Visual Diff
```

---

## 3. Technology Stack

| Layer | Technologies | Role / Description |
|---|---|---|
| **Frontend** | React 18, Vite, React Router v6, Axios, Lucide Icons, Monaco Editor, Diff | Reactive developer dashboard, code editor, visual diff, scorecards |
| **Backend** | Python 3.11+, FastAPI, Uvicorn, Pydantic v2 | High-performance asynchronous REST API and pipeline orchestration |
| **Database** | MySQL Server 8.0, SQLAlchemy ORM, PyMySQL | Relational persistence for accounts, review history, and findings |
| **Authentication** | JWT (JSON Web Tokens), bcrypt / passlib | Secure password hashing and stateless token authorization |
| **Static Analyzers**| Bandit, Pylint, ESLint, Semgrep | Rule-based security, style, and bug pattern identification |
| **AI / LLM** | Google Gemini API / OpenAI API (Optional) | Contextual issue analysis and remediation synthesis |
| **Testing** | Pytest, FastAPI TestClient | Automated unit and integration testing suite |

---

## 4. MySQL Relational Schema

Database Name: `code_review_db`

```sql
-- 1. Users Table
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Code Reviews Table
CREATE TABLE code_reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    filename VARCHAR(255),
    language VARCHAR(50) NOT NULL,
    source_code LONGTEXT NOT NULL,
    overall_score DECIMAL(5,2) NOT NULL,
    security_score DECIMAL(5,2),
    correctness_score DECIMAL(5,2),
    maintainability_score DECIMAL(5,2),
    style_score DECIMAL(5,2),
    complexity_score DECIMAL(5,2),
    metrics_summary JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 3. Findings Table
CREATE TABLE findings (
    finding_id INT PRIMARY KEY AUTO_INCREMENT,
    review_id INT NOT NULL,
    line_number INT,
    issue_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    explanation TEXT,
    evidence TEXT,
    confidence DECIMAL(5,2) NOT NULL,
    sources JSON,
    FOREIGN KEY (review_id) REFERENCES code_reviews(review_id) ON DELETE CASCADE
);

-- 4. Suggestions Table
CREATE TABLE suggestions (
    suggestion_id INT PRIMARY KEY AUTO_INCREMENT,
    finding_id INT NOT NULL UNIQUE,
    original_code TEXT,
    corrected_code TEXT,
    recommendation TEXT,
    FOREIGN KEY (finding_id) REFERENCES findings(finding_id) ON DELETE CASCADE
);
```

---

## 5. Prerequisites & Environment Setup (Windows 11)

1. **Python 3.11+** installed (check with `python --version`).
2. **Node.js v18+ & npm** installed (check with `node -v` and `npm -v`).
3. **MySQL Server 8.0** installed and running on port `3306` (or `3307`).

---

## 6. Installation Guide

### Step 1: Database Setup

Log into MySQL via Command Prompt / PowerShell:
```powershell
mysql -u root -p
```
Run the following SQL statement:
```sql
CREATE DATABASE IF NOT EXISTS code_review_db;
```

### Step 2: Backend Configuration & Dependencies

Open a PowerShell terminal in VS Code:
```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Create or configure `.env` inside `backend/`:
```ini
DATABASE_URL=mysql+pymysql://root:root123@localhost:3307/code_review_db
SECRET_KEY=b9c3f4e2a87d1904a6e54c82dbef4093817a02c849d1ef982c73d4a159e60742
LLM_API_KEY=
LLM_PROVIDER=gemini
APP_ENV=development
```
*(Note: If your local MySQL Server runs on standard port 3306, adjust `localhost:3307` to `localhost:3306` with your MySQL user/password).*

### Step 3: Frontend Installation

Open a second PowerShell terminal in VS Code:
```powershell
cd frontend
npm install
```

---

## 7. Running the Platform

### Start Backend Server:
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`
- Health Probe: `http://127.0.0.1:8000/health`

### Start Frontend Server:
```powershell
cd frontend
npm run dev
```
- Web Application URL: `http://localhost:5173`

---

## 8. Automated Testing

Run the comprehensive Pytest suite:
```powershell
cd backend
$env:PYTHONPATH="."
pytest ..\tests\backend\test_api.py -v
```

All 11 test modules will verify:
- Database connectivity and schema initialization
- User registration, duplicate checks, login, and JWT bearer token authorization
- Empty code and unsupported payload handling
- Defective Python analysis (Pylint, Bandit, Local rules, XAI, Diff generation)
- Clean Python analysis (0 critical/high findings, >= 95% quality score)
- File upload handling (`.js`, `.py`, `.java`)
- Finding deduplication and multi-source fusion
- Unified scoring calculation
- Review history persistence and query filters

---

## 9. API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Server and MySQL connectivity health check |
| `POST` | `/api/auth/register` | Register new developer account |
| `POST` | `/api/auth/login` | Authenticate and issue JWT Bearer token |
| `GET` | `/api/auth/profile` | Retrieve authenticated user profile *(Protected)* |
| `POST` | `/api/review/analyze` | Submit source code string for analysis |
| `POST` | `/api/review/upload` | Upload source file (`multipart/form-data`) |
| `GET` | `/api/review/history` | Retrieve past reviews for user |
| `GET` | `/api/review/{id}` | Retrieve complete review report and score breakdown |
| `GET` | `/api/review/{id}/findings` | Retrieve findings list for specific review |
| `POST` | `/api/fix/generate` | Generate remediation recommendation and unified diff |
| `GET` | `/api/dashboard/statistics`| Aggregated metrics, scores, and severity distributions |

---

## 10. Viva / Examination Preparation

### Q1: Why use a hybrid architecture combining static analysis and LLMs?
**Answer:** Traditional static analyzers (Pylint, Bandit) use deterministic pattern matching and AST inspection; they are fast, reliable, and produce zero hallucinations for known rules. However, they lack contextual understanding of broader application logic and cannot write conversational explanations. Large Language Models (LLMs) excel at contextual reasoning, synthesizing complex code explanations, and generating natural code repairs. Combining both via **Finding Fusion** allows static analyzers to provide hard evidence while the LLM or XAI engine enriches the finding with contextual impact and human-readable fixes.

### Q2: How does the platform achieve Explainable AI (XAI)?
**Answer:** The platform treats explainability as a first-class output. Rather than simply warning that a line has a bug, every finding explicitly answers five core questions:
1. **WHAT Happened?** (Concise title and message)
2. **WHERE did it happen?** (Exact source file line number and code construct)
3. **WHY is it a problem?** (Detailed explanation of root cause and runtime/security impact)
4. **WHAT is the evidence?** (Exact extracted source code snippet)
5. **HOW can it be fixed?** (Actionable recommendation, corrected replacement snippet, and visual diff)
Additionally, a system **confidence indicator** is calculated and displayed without falsely presenting confidence as absolute proof.

### Q3: Why is MySQL chosen over NoSQL (e.g., MongoDB)?
**Answer:** Code review data is strictly relational: a `User` has multiple `CodeReviews`, each `CodeReview` owns multiple `Findings`, and each `Finding` has a corresponding `Suggestion`. Relational foreign keys with `ON DELETE CASCADE` guarantee referential integrity and prevent orphaned findings when a user or review is deleted.

### Q4: How is untrusted uploaded code handled safely?
**Answer:** Untrusted user code is **NEVER executed**. All analysis is performed statically using AST parsing (`ast.parse`), rule-based inspection (`bandit`, `pylint`), and LLM reasoning. Code execution is completely isolated and avoided, eliminating remote code execution (RCE) risks on the host backend.

### Q5: How does the system operate offline or without an API key?
**Answer:** The architecture features a **Deterministic Local Static Analysis Engine** in `explanation_engine.py`. If no LLM API key is configured or network issues occur, the platform automatically engages local pattern-matching rules (for division-by-zero risks, hard-coded passwords, SQL injection patterns, dangerous eval usage, and unhandled errors) and explicitly labels them as `"Local Static Analysis"` to maintain academic and scientific integrity.

---

## 11. Project Directory Structure

```
ai-code-review-platform/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint & lifecycle
│   │   └── config.py                # Pydantic Settings & environment loader
│   ├── database/
│   │   └── connection.py            # MySQL SQLAlchemy engine & session dependency
│   ├── models/
│   │   ├── user.py                  # User ORM model
│   │   ├── review.py                # CodeReview ORM model
│   │   ├── finding.py               # Finding ORM model
│   │   └── suggestion.py            # Suggestion ORM model
│   ├── routes/
│   │   ├── auth.py                  # Registration, login, profile routes
│   │   ├── review.py                # Code analysis, file upload, history routes
│   │   ├── findings.py              # Individual finding inspection routes
│   │   ├── dashboard.py             # Dashboard statistics aggregation routes
│   │   └── fix.py                   # Fix generation and diff routes
│   ├── schemas/
│   │   ├── auth.py                  # Pydantic schemas for authentication
│   │   ├── review.py                # Pydantic schemas for reviews and scores
│   │   └── finding.py               # Pydantic schemas for standard findings
│   ├── services/
│   │   ├── parser.py                # AST parsing & structural complexity metrics
│   │   ├── language_detector.py     # File extension & syntax heuristics
│   │   ├── static_analyzer.py       # Pylint, Bandit, ESLint, Semgrep adapters
│   │   ├── llm_analyzer.py          # Gemini/OpenAI API integration
│   │   ├── explanation_engine.py    # 5-dimension XAI & offline fallback rules
│   │   ├── finding_fusion.py        # Finding deduplication & multi-source fusion
│   │   ├── fix_generator.py         # Remediation code & unified diff generator
│   │   └── scoring.py               # 5-dimension weighted quality scoring formula
│   ├── utils/
│   │   ├── security.py              # JWT token handling & bcrypt password hashing
│   │   └── validators.py            # Input size, filename, and extension validation
│   ├── requirements.txt             # Python backend dependencies
│   ├── .env                         # Active configuration
│   ├── .env.example                 # Environment template
│   └── Dockerfile                   # Backend Docker configuration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx           # Global navigation header with auth state
│   │   │   ├── ProtectedRoute.jsx   # Client-side route protection
│   │   │   ├── CodeEditor.jsx       # Monaco Editor wrapper with syntax highlighting
│   │   │   ├── LanguageSelector.jsx # Language dropdown selector
│   │   │   ├── UploadBox.jsx        # Drag-and-drop file upload zone
│   │   │   ├── AnalyzeButton.jsx    # Action trigger with loading spinner
│   │   │   ├── ScoreCard.jsx        # Gauge score & 5-dimension progress bars
│   │   │   ├── IssueList.jsx        # Filterable finding list cards
│   │   │   ├── IssueDetails.jsx     # 5-dimension Explainable AI inspector
│   │   │   ├── CodeDiff.jsx         # Visual code diff & copy fix controls
│   │   │   └── HistoryTable.jsx     # Review history data table
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx        # Main overview dashboard
│   │   │   ├── Review.jsx           # Interactive code review studio
│   │   │   ├── ReviewDetails.jsx    # Deep review report page
│   │   │   ├── History.jsx          # Audit trail of past reviews
│   │   │   ├── Login.jsx            # User login page
│   │   │   ├── Register.jsx         # User registration page
│   │   │   └── Profile.jsx          # Developer profile page
│   │   ├── services/
│   │   │   ├── api.js               # Axios instance with JWT interceptor
│   │   │   ├── authService.js       # Auth API client
│   │   │   └── reviewService.js     # Code review API client
│   │   ├── hooks/
│   │   │   └── useAuth.js           # Authentication hook
│   │   ├── App.jsx                  # Root router configuration
│   │   ├── main.jsx                 # React root mount
│   │   └── index.css                # Custom modern slate engineering theme
│   ├── package.json                 # Node.js dependencies
│   ├── vite.config.js               # Vite build configuration
│   └── Dockerfile                   # Frontend Docker configuration
├── tests/
│   ├── backend/
│   │   └── test_api.py              # Automated Pytest test suite (11 test modules)
│   └── sample_code/
│       ├── bad_python.py            # Sample Python with intentional defects
│       ├── good_python.py           # Clean validated Python sample
│       ├── bad_javascript.js        # Sample JS with vulnerabilities
│       ├── good_javascript.js       # Clean asynchronous JS sample
│       └── bad_java.java            # Sample Java code
├── docker-compose.yml               # Multi-container orchestration
└── README.md                        # Complete project manual & viva guide
```

---

## 12. License & Author Information

Developed as a Final-Year B.Tech Project in Computer Science and Engineering / Artificial Intelligence.
Designed for presentation, viva defense, academic review, and open-source GitHub publication.
