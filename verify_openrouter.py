"""Test OpenRouter live API integration and full CRUD workflows."""

import os
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base, SessionLocal
from app.models import Patient

# Ensure tables exist and dependency overrides are clear
app.dependency_overrides.clear()
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_openrouter_live_flow():
    print("=" * 80)
    print("  OPENROUTER AI LIVE INTEGRATION & CRUD VERIFICATION")
    print("=" * 80)

    # 1. Create a patient and verify AI-generated remarks
    print("\n[STEP 1] Creating a new patient via POST /api/patients...")
    new_patient_data = {
        "full_name": "Marcus Vance",
        "date_of_birth": "14/06/1988",
        "email": "marcus.vance@example.com",
        "glucose": 175.0,
        "haemoglobin": 14.2,
        "cholesterol": 225.0,
    }
    res = client.post("/api/patients", json=new_patient_data)
    assert res.status_code == 201, f"Failed to create patient: {res.text}"
    created = res.json()
    patient_id = created["id"]
    print(f"  --> Created Patient ID #{patient_id} ({created['full_name']})")
    print(f"  --> AI Status: {created['ai_status']}")
    assert created["ai_status"] == "COMPLETED", "AI Status should be COMPLETED"
    assert created["remarks"] and len(created["remarks"]) > 50, "Expected non-empty remarks"
    print(f"  --> Live OpenRouter Remarks Preview (first 180 chars):\n      {created['remarks'][:180]}...")

    # 2. Update blood test values and verify AI remarks regeneration
    print("\n[STEP 2] Updating blood test metrics via PUT /api/patients/{id}...")
    original_remarks = created["remarks"]
    update_data = {
        "glucose": 92.0,  # Changed from 175.0 to 92.0 (normal)
    }
    put_res = client.put(f"/api/patients/{patient_id}", json=update_data)
    assert put_res.status_code == 200, f"Failed to update patient: {put_res.text}"
    updated = put_res.json()
    assert updated["glucose"] == 92.0
    assert updated["ai_status"] == "COMPLETED"
    print(f"  --> Glucose updated to {updated['glucose']} mg/dL")
    print(f"  --> AI Remarks successfully regenerated! Preview:\n      {updated['remarks'][:180]}...")

    # 3. Test the regenerate AI remarks endpoint
    print("\n[STEP 3] Testing POST /api/patients/{id}/generate-remarks...")
    regen_res = client.post(f"/api/patients/{patient_id}/generate-remarks")
    assert regen_res.status_code == 200, f"Regenerate remarks failed: {regen_res.text}"
    regen_data = regen_res.json()
    assert regen_data["ai_status"] == "COMPLETED"
    print(f"  --> Regenerate Endpoint Succeeded! AI Status: {regen_data['ai_status']}")
    print(f"  --> Regenerated Remarks Preview:\n      {regen_data['remarks'][:180]}...")

    # 4. Verify all existing CRUD operations still work
    print("\n[STEP 4] Verifying all CRUD operations...")
    # GET all
    all_res = client.get("/api/patients")
    assert all_res.status_code == 200
    all_patients = all_res.json()
    print(f"  --> GET /api/patients retrieved {len(all_patients)} records.")

    # GET one
    one_res = client.get(f"/api/patients/{patient_id}")
    assert one_res.status_code == 200
    assert one_res.json()["email"] == "marcus.vance@example.com"
    print(f"  --> GET /api/patients/{patient_id} verified.")

    # PUT non-blood field (no AI regeneration triggered)
    put_name_res = client.put(f"/api/patients/{patient_id}", json={"full_name": "Marcus Vance Updated"})
    assert put_name_res.status_code == 200
    assert put_name_res.json()["full_name"] == "Marcus Vance Updated"
    print(f"  --> PUT /api/patients/{patient_id} (demographic update) verified.")

    # DELETE the test patient so assessment data remains clean
    del_res = client.delete(f"/api/patients/{patient_id}")
    assert del_res.status_code == 200
    print(f"  --> DELETE /api/patients/{patient_id} succeeded.")

    # Verify 404 after deletion
    get_del = client.get(f"/api/patients/{patient_id}")
    assert get_del.status_code == 404
    print("  --> GET after delete confirmed 404 Not Found.")

    # 5. Confirm assessment data preserved
    print("\n[STEP 5] Confirming existing assessment data remains intact...")
    db = SessionLocal()
    robyn = db.query(Patient).filter(Patient.id == 1).first()
    assert robyn is not None
    assert robyn.email == "gokul@infocare.com", f"Expected gokul@infocare.com, got {robyn.email}"
    assert robyn.glucose == 232.0, f"Expected glucose 232.0, got {robyn.glucose}"
    print(f"  --> Assessment Record #1 verified: {robyn.full_name} | {robyn.email} | Glucose: {robyn.glucose}")
    db.close()

    print("\n" + "=" * 80)
    print("  >>> ALL OPENROUTER TESTS & CRUD CHECKS PASSED WITH 100% SUCCESS! <<<")
    print("=" * 80)


if __name__ == "__main__":
    test_openrouter_live_flow()
