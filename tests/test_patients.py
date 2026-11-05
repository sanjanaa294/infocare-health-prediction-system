"""Integration and CRUD tests for FastAPI patient endpoints using a dedicated test database."""

import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Patient

# Dedicated test database URL
TEST_DB_FILE = "./test_health_records.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Dependency override providing test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    """Create test database tables before tests and clean up file afterward."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass


@pytest.fixture
def client():
    """Provide FastAPI test client."""
    return TestClient(app)


class TestPatientAPI:
    """Test suite for Patient CRUD and AI integration endpoints."""

    @patch("app.routers.patients.generate_health_remarks")
    def test_create_valid_patient(self, mock_ai, client):
        """Test POST /api/patients creates record and persists in database."""
        mock_ai.return_value = (
            "Observation: Glucose and cholesterol levels are slightly elevated. Consult a physician.",
            "COMPLETED",
        )

        payload = {
            "full_name": "Robyn Pears",
            "date_of_birth": "28.01.1960",
            "email": "robyn@gmail.com",
            "glucose": 232.0,
            "haemoglobin": 13.5,
            "cholesterol": 180.0,
        }

        response = client.post("/api/patients", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["full_name"] == "Robyn Pears"
        assert data["date_of_birth"] == "1960-01-28"
        assert data["email"] == "robyn@gmail.com"
        assert data["glucose"] == 232.0
        assert data["ai_status"] == "COMPLETED"
        assert "Observation" in data["remarks"]
        assert mock_ai.called

    def test_create_patient_invalid_email_rejected(self, client):
        """Test POST /api/patients rejects invalid email (Assessment Test 2: hunter@gmail)."""
        payload = {
            "full_name": "John Hunter",
            "date_of_birth": "10.12.1990",
            "email": "hunter@gmail",
            "glucose": 94,
            "haemoglobin": 15,
            "cholesterol": 200,
        }
        response = client.post("/api/patients", json=payload)
        assert response.status_code == 422
        body = response.json()
        assert "Validation failed" in body.get("message", "") or "email" in str(body)

    def test_create_patient_invalid_date_rejected(self, client):
        """Test POST /api/patients rejects invalid calendar date (Assessment Test 4: 31.11.2001)."""
        payload = {
            "full_name": "Peter Larry",
            "date_of_birth": "31.11.2001",
            "email": "Larry@hotmail.com",
            "glucose": 88,
            "haemoglobin": 11.5,
            "cholesterol": 165,
        }
        response = client.post("/api/patients", json=payload)
        assert response.status_code == 422
        body = response.json()
        assert "Invalid calendar date or format" in str(body)

    def test_create_patient_future_date_rejected(self, client):
        """Test POST /api/patients rejects future date (Assessment Test 8: 19.10.2030)."""
        payload = {
            "full_name": "Kris Wu",
            "date_of_birth": "19.10.2030",
            "email": "kris@gmail.com",
            "glucose": 79,
            "haemoglobin": 16.5,
            "cholesterol": 197,
        }
        response = client.post("/api/patients", json=payload)
        assert response.status_code == 422
        body = response.json()
        assert "cannot be in the future" in str(body)

    @patch("app.routers.patients.generate_health_remarks")
    def test_duplicate_patient_entries_allowed(self, mock_ai, client):
        """Test that duplicate patient entries (e.g. Assessment Test 6) are saved as separate records."""
        mock_ai.return_value = ("Duplicate observation note.", "COMPLETED")

        payload = {
            "full_name": "Robyn Pears",
            "date_of_birth": "28.01.1960",
            "email": "robyn@gmail.com",
            "glucose": 232,
            "haemoglobin": 13.5,
            "cholesterol": 180,
        }

        # First insert
        res1 = client.post("/api/patients", json=payload)
        assert res1.status_code == 201
        id1 = res1.json()["id"]

        # Second insert with identical details
        res2 = client.post("/api/patients", json=payload)
        assert res2.status_code == 201
        id2 = res2.json()["id"]

        # Must have distinct primary keys
        assert id1 != id2

    def test_get_all_patients(self, client):
        """Test GET /api/patients retrieves all patient records."""
        response = client.get("/api/patients")
        assert response.status_code == 200
        patients = response.json()
        assert isinstance(patients, list)
        assert len(patients) >= 2

    def test_get_patient_by_id(self, client):
        """Test GET /api/patients/{id} retrieves specific record."""
        # Retrieve all to get an existing ID
        all_patients = client.get("/api/patients").json()
        target_id = all_patients[0]["id"]

        response = client.get(f"/api/patients/{target_id}")
        assert response.status_code == 200
        assert response.json()["id"] == target_id

    def test_get_nonexistent_patient_returns_404(self, client):
        """Test GET /api/patients/99999 returns 404 Not Found."""
        response = client.get("/api/patients/99999")
        assert response.status_code == 404

    @patch("app.routers.patients.generate_health_remarks")
    def test_update_patient_without_blood_metric_change(self, mock_ai, client):
        """Test PUT /api/patients/{id} updates demographic field without regenerating AI remarks."""
        all_patients = client.get("/api/patients").json()
        target = all_patients[0]
        original_remarks = target["remarks"]

        payload = {"full_name": "Robyn Pears Updated"}
        response = client.put(f"/api/patients/{target['id']}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Robyn Pears Updated"
        # Remarks should not have been regenerated
        assert not mock_ai.called

    @patch("app.routers.patients.generate_health_remarks")
    def test_update_patient_with_blood_metric_change_regenerates_ai(self, mock_ai, client):
        """Test PUT /api/patients/{id} triggers AI regeneration when blood metrics change."""
        mock_ai.return_value = ("Updated AI Observation: Glucose has decreased.", "COMPLETED")

        all_patients = client.get("/api/patients").json()
        target = all_patients[0]

        payload = {"glucose": 95.0}  # Changed glucose
        response = client.put(f"/api/patients/{target['id']}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["glucose"] == 95.0
        assert mock_ai.called
        assert "Updated AI Observation" in data["remarks"]

    @patch("app.routers.patients.generate_health_remarks")
    def test_ai_api_failure_handling(self, mock_ai, client):
        """Test that if external AI API fails, the patient record is still saved gracefully with FAILED status."""
        mock_ai.return_value = (
            "AI Health Service Error: Connection timed out. Patient record preserved.",
            "FAILED",
        )

        payload = {
            "full_name": "Sam Kerr",
            "date_of_birth": "09.12.2006",
            "email": "sam@news.com.au",
            "glucose": 198,
            "haemoglobin": 8.9,
            "cholesterol": 192,
        }

        response = client.post("/api/patients", json=payload)
        # Should NOT crash with 500, but succeed with 201
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["ai_status"] == "FAILED"
        assert "AI Health Service Error" in data["remarks"]

    @patch("app.routers.patients.generate_health_remarks")
    def test_manual_regenerate_remarks_endpoint(self, mock_ai, client):
        """Test POST /api/patients/{id}/generate-remarks manually triggers remarks update."""
        mock_ai.return_value = ("Manually regenerated observation.", "COMPLETED")

        all_patients = client.get("/api/patients").json()
        target_id = all_patients[0]["id"]

        response = client.post(f"/api/patients/{target_id}/generate-remarks")
        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == target_id
        assert data["ai_status"] == "COMPLETED"
        assert data["remarks"] == "Manually regenerated observation."

    def test_delete_patient(self, client):
        """Test DELETE /api/patients/{id} removes the patient record."""
        # Create a record to delete
        with patch("app.routers.patients.generate_health_remarks") as mock_ai:
            mock_ai.return_value = ("To be deleted", "COMPLETED")
            created = client.post(
                "/api/patients",
                json={
                    "full_name": "Temporary Patient",
                    "date_of_birth": "01.01.2000",
                    "email": "temp@example.com",
                    "glucose": 100,
                    "haemoglobin": 14,
                    "cholesterol": 180,
                },
            ).json()

        patient_id = created["id"]

        # Delete it
        del_res = client.delete(f"/api/patients/{patient_id}")
        assert del_res.status_code == 200
        assert del_res.json()["success"] is True

        # Verify it no longer exists
        get_res = client.get(f"/api/patients/{patient_id}")
        assert get_res.status_code == 404

    def test_frontend_web_pages_render(self, client):
        """Test HTML rendering of dashboard, patient directory, and add patient views."""
        # Dashboard view
        res = client.get("/dashboard")
        assert res.status_code == 200
        assert "Clinical Health Analytics Dashboard" in res.text

        # Patients list view
        res = client.get("/patients")
        assert res.status_code == 200
        assert "Patient Clinical Directory" in res.text

        # Add patient view
        res = client.get("/patients/add")
        assert res.status_code == 200
        assert "Register New Patient" in res.text

        # Root redirect
        res = client.get("/", follow_redirects=False)
        assert res.status_code == 303
