import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from database.connection import init_db, check_db_connection
from services.scoring import ScoringService
from services.finding_fusion import FindingFusionService
from schemas.finding import RawFinding, FindingSchema, SuggestionSchema

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    init_db()

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data

def test_auth_workflow():
    import uuid
    rand_email = f"student_{uuid.uuid4().hex[:8]}@example.com"
    
    # 1. Register
    reg_payload = {
        "name": "Jane Developer",
        "email": rand_email,
        "password": "SecurePassword123!"
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    user_data = reg_res.json()
    assert user_data["email"] == rand_email
    assert "user_id" in user_data

    # 2. Duplicate registration fails
    dup_res = client.post("/api/auth/register", json=reg_payload)
    assert dup_res.status_code == 400

    # 3. Valid Login
    login_res = client.post("/api/auth/login", json={
        "email": rand_email,
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    token = token_data["access_token"]
    assert token

    # 4. Invalid Login fails
    bad_login = client.post("/api/auth/login", json={
        "email": rand_email,
        "password": "WrongPassword999"
    })
    assert bad_login.status_code == 401

    # 5. Protected profile endpoint with JWT
    headers = {"Authorization": f"Bearer {token}"}
    prof_res = client.get("/api/auth/profile", headers=headers)
    assert prof_res.status_code == 200
    assert prof_res.json()["email"] == rand_email

def test_empty_code_rejected():
    res = client.post("/api/review/analyze", json={"code": "   ", "language": "python"})
    assert res.status_code == 400

def test_analyze_bad_python():
    sample_path = os.path.join(os.path.dirname(__file__), "..", "sample_code", "bad_python.py")
    with open(sample_path, "r", encoding="utf-8") as f:
        code = f.read()

    res = client.post("/api/review/analyze", json={"code": code, "language": "python", "filename": "bad_python.py"})
    assert res.status_code == 200
    data = res.json()
    assert data["language"] == "python"
    assert data["overall_score"] < 95.0
    assert len(data["issues"]) > 0

    # Verify standard finding format
    first_issue = data["issues"][0]
    assert "line" in first_issue
    assert "severity" in first_issue
    assert "issue_type" in first_issue
    assert "explanation" in first_issue
    assert "evidence" in first_issue
    assert "confidence" in first_issue
    assert "sources" in first_issue
    assert "suggestion" in first_issue

def test_analyze_good_python():
    sample_path = os.path.join(os.path.dirname(__file__), "..", "sample_code", "good_python.py")
    with open(sample_path, "r", encoding="utf-8") as f:
        code = f.read()

    res = client.post("/api/review/analyze", json={"code": code, "language": "python", "filename": "good_python.py"})
    assert res.status_code == 200
    data = res.json()
    assert data["summary"]["critical"] == 0
    assert data["summary"]["high"] == 0
    assert data["overall_score"] >= 95.0

def test_file_upload_analysis():
    sample_path = os.path.join(os.path.dirname(__file__), "..", "sample_code", "bad_javascript.js")
    with open(sample_path, "rb") as f:
        files = {"file": ("test_script.js", f, "application/javascript")}
        res = client.post("/api/review/upload", files=files)
    
    assert res.status_code == 200
    data = res.json()
    assert data["language"] == "javascript"
    assert len(data["issues"]) > 0

def test_review_history_and_details():
    # Fetch history
    res = client.get("/api/review/history")
    assert res.status_code == 200
    history = res.json()
    assert isinstance(history, list)
    assert len(history) > 0

    rev_id = history[0]["review_id"]
    detail_res = client.get(f"/api/review/{rev_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["review_id"] == rev_id
    assert "scores" in detail
    assert "issues" in detail

def test_fix_generation_endpoint():
    finding = {
        "line": 5,
        "issue_type": "security",
        "severity": "HIGH",
        "title": "Hard-coded API Token",
        "evidence": "api_key = 'sk_test_12345'",
        "sources": ["static"]
    }
    payload = {
        "original_code": "def init():\n    api_key = 'sk_test_12345'\n    return api_key",
        "finding": finding,
        "language": "python"
    }
    res = client.post("/api/fix/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "corrected_code" in data
    assert "recommendation" in data
    assert "diff_unified" in data

def test_dashboard_statistics():
    res = client.get("/api/dashboard/statistics")
    assert res.status_code == 200
    stats = res.json()
    assert "total_reviews" in stats
    assert "average_score" in stats
    assert "severity_counts" in stats
    assert stats["total_reviews"] > 0

def test_finding_fusion_logic():
    f1 = RawFinding(
        line=10,
        issue_type="security",
        severity="HIGH",
        title="Hard-coded password",
        message="Plaintext secret found",
        evidence="pwd = 'abc'",
        source="bandit"
    )
    f2 = RawFinding(
        line=10,
        issue_type="security",
        severity="HIGH",
        title="Hard-coded credential",
        message="Sensitive token exposed",
        evidence="pwd = 'abc'",
        source="llm"
    )
    fused = FindingFusionService.fuse_findings([f1, f2])
    assert len(fused) == 1
    assert "static" in fused[0].sources
    assert "llm" in fused[0].sources

def test_scoring_formula():
    findings = [
        FindingSchema(
            line=1,
            issue_type="security",
            severity="CRITICAL",
            title="SQL Injection",
            sources=["static"]
        )
    ]
    scores, summary = ScoringService.calculate_scores_and_summary(findings, {"complexity": 1})
    assert summary.critical == 1
    assert scores.security == 70.0 # 100 - 30
    assert scores.overall < 100.0
