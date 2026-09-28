import io
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_admin_login_api():
    payload = {
        "email": "admin@analyzer.ai",
        "password": "admin123"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "admin@analyzer.ai"

def test_user_registration_api():
    unique_email = f"user_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "username": "Test User",
        "email": unique_email,
        "password": "my_secure_password_123456",
        "role": "user"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == unique_email

def test_analyze_text_api():
    payload = {
        "title": "Unit Test Document",
        "text": "The project deadline is approaching and we encountered multiple unexpected errors during deployment. We require technical guidance and assistance to resolve these issues quickly.",
        "doc_type": "Technical Report"
    }
    response = client.post("/api/documents/analyze-text", json=payload)
    assert response.status_code == 200
    report = response.json()
    assert "report_id" in report
    assert "emotion_analysis" in report
    assert "intent_analysis" in report
    assert "summary_insight" in report

def test_upload_document_api():
    sample_doc_content = b"""
    Dear Customer Support,
    I purchased this product last month. It failed to work repeatedly.
    I spent hours on troubleshooting with no fix.
    I want to return the product and receive a full refund immediately.
    """
    files = {
        "file": ("complaint_document.txt", io.BytesIO(sample_doc_content), "text/plain")
    }
    data = {
        "doc_type": "Complaint Letter"
    }
    response = client.post("/api/documents/upload", files=files, data=data)
    assert response.status_code == 200
    report = response.json()
    assert report["report_id"].startswith("REP-")
    assert report["metadata"]["document_name"] == "complaint_document.txt"
    assert "Product Return" in report["intent_analysis"]["primary_intent"] or "Refund" in report["intent_analysis"]["primary_intent"]

def test_analytics_dashboard_api():
    response = client.get("/api/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "emotion_distribution" in data
