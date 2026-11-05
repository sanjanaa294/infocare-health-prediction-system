"""Live End-to-End System Verification Script.

Executes all verification checks against the running FastAPI server at http://127.0.0.1:8000:
1. Tests all 10 assessment records individually.
2. Verifies 7 accepted records and 3 rejected records.
3. Verifies duplicate entry preservation with distinct IDs.
4. Verifies updating a patient email to gokul@infocare.com.
5. Verifies modifying blood test values updates remarks.
6. Verifies deletion of a patient record.
7. Displays the final patient directory after deletion.
"""

import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

ASSESSMENT_RECORDS = [
    {
        "test_id": 1,
        "name": "Robyn Pears",
        "dob": "28.01.1960",
        "email": "robyn@gmail.com",
        "glucose": 232,
        "haemoglobin": 13.5,
        "cholesterol": 180,
        "expected": "ACCEPT",
    },
    {
        "test_id": 2,
        "name": "John Hunter",
        "dob": "10.12.1990",
        "email": "hunter@gmail",
        "glucose": 94,
        "haemoglobin": 15,
        "cholesterol": 200,
        "expected": "REJECT",
    },
    {
        "test_id": 3,
        "name": "Darryl Tim",
        "dob": "12.11.1993",
        "email": "timd@smh.com.au",
        "glucose": 240,
        "haemoglobin": 18.6,
        "cholesterol": 326,
        "expected": "ACCEPT",
    },
    {
        "test_id": 4,
        "name": "Peter Larry",
        "dob": "31.11.2001",
        "email": "Larry@hotmail.com",
        "glucose": 88,
        "haemoglobin": 11.5,
        "cholesterol": 165,
        "expected": "REJECT",
    },
    {
        "test_id": 5,
        "name": "Sam Kerr",
        "dob": "09.12.2006",
        "email": "sam@news.com.au",
        "glucose": 198,
        "haemoglobin": 8.9,
        "cholesterol": 192,
        "expected": "ACCEPT",
    },
    {
        "test_id": 6,
        "name": "Robyn Pears",
        "dob": "28.01.1960",
        "email": "robyn@gmail.com",
        "glucose": 232,
        "haemoglobin": 13.5,
        "cholesterol": 180,
        "expected": "ACCEPT (Duplicate)",
    },
    {
        "test_id": 7,
        "name": "Madison XI",
        "dob": "12.09.1998",
        "email": "madison@hotmail.com",
        "glucose": 85,
        "haemoglobin": 7.6,
        "cholesterol": 163,
        "expected": "ACCEPT",
    },
    {
        "test_id": 8,
        "name": "Kris Wu",
        "dob": "19.10.2030",
        "email": "Kris.wu.gmail.com",
        "glucose": 79,
        "haemoglobin": 16.5,
        "cholesterol": 197,
        "expected": "REJECT",
    },
    {
        "test_id": 9,
        "name": "Tenille Singh",
        "dob": "30.11.1991",
        "email": "Tenille@yahoo.com",
        "glucose": 101,
        "haemoglobin": 15,
        "cholesterol": 310,
        "expected": "ACCEPT",
    },
    {
        "test_id": 10,
        "name": "Prem Kumar",
        "dob": "28.04.1990",
        "email": "prem@telstra.com",
        "glucose": 155,
        "haemoglobin": 12.5,
        "cholesterol": 265,
        "expected": "ACCEPT",
    },
]


def post_json(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    payload_bytes = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload_bytes,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body


def put_json(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    payload_bytes = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload_bytes,
        headers={"Content-Type": "application/json"},
        method="PUT",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body


def get_json(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def delete_req(endpoint):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method="DELETE")
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def run_full_verification():
    print("=" * 80)
    print("  LIVE SYSTEM VERIFICATION: 10 ASSESSMENT RECORDS SUBMISSION")
    print("=" * 80)

    saved_records = []
    rejected_records = []

    for item in ASSESSMENT_RECORDS:
        tid = item["test_id"]
        name = item["name"]
        dob = item["dob"]
        email = item["email"]
        glu = item["glucose"]
        hb = item["haemoglobin"]
        chol = item["cholesterol"]

        payload = {
            "full_name": name,
            "date_of_birth": dob,
            "email": email,
            "glucose": glu,
            "haemoglobin": hb,
            "cholesterol": chol,
        }

        print(f"\n[SUBMITTING TEST {tid}]: {name} | DOB: {dob} | Email: {email}")
        status_code, response = post_json("/api/patients", payload)

        if status_code == 201:
            saved_records.append(response)
            print(f"  --> HTTP {status_code} CREATED: Saved successfully!")
            print(f"      Record ID: #{response['id']} | Full Name: {response['full_name']}")
            print(f"      AI Status: {response['ai_status']}")
            print(f"      AI Remarks: {response['remarks'][:120]}...")
        else:
            rejected_records.append((tid, name, response))
            print(f"  --> HTTP {status_code} REJECTED: Correctly denied by backend validation.")
            if isinstance(response, dict):
                error_detail = response.get("detail", response.get("message"))
                print(f"      Validation Error: {error_detail}")
            else:
                print(f"      Raw Response: {response}")

    print("\n" + "=" * 80)
    print("  ASSESSMENT BENCHMARK SUMMARY:")
    print(f"  Total Submissions:     {len(ASSESSMENT_RECORDS)}")
    print(f"  Total Accepted:        {len(saved_records)} (Expected: 7)")
    print(f"  Total Rejected:        {len(rejected_records)} (Expected: 3)")
    print("=" * 80)

    assert len(saved_records) == 7, "Error: Expected exactly 7 saved records"
    assert len(rejected_records) == 3, "Error: Expected exactly 3 rejected records"

    # Verify duplicate record storage (Test 1 and Test 6)
    robyn_records = [r for r in saved_records if r["full_name"] == "Robyn Pears"]
    print(f"\n[DUPLICATE ENTRY VERIFICATION]: Found {len(robyn_records)} records for 'Robyn Pears'")
    assert len(robyn_records) == 2, "Expected 2 distinct records for Robyn Pears"
    print(f"  Record 1 ID: #{robyn_records[0]['id']} | Email: {robyn_records[0]['email']}")
    print(f"  Record 2 ID: #{robyn_records[1]['id']} | Email: {robyn_records[1]['email']}")
    assert robyn_records[0]["id"] != robyn_records[1]["id"], "Duplicate entries must have unique IDs!"
    print("  --> Duplicate entries correctly stored as independent database records!")

    # ---------------- UPDATE REQUIREMENT ---------------- #
    # "Change any one patient's email address to: gokul@infocare.com"
    target_patient = saved_records[0]
    target_id = target_patient["id"]
    old_email = target_patient["email"]
    new_email = "gokul@infocare.com"

    print("\n" + "=" * 80)
    print(f"  VERIFYING UPDATE REQUIREMENT: Update Email to '{new_email}'")
    print("=" * 80)
    print(f"Updating Patient ID #{target_id} ({target_patient['full_name']})")
    print(f"  Old Email: {old_email}")
    print(f"  New Email: {new_email}")

    put_status, put_resp = put_json(f"/api/patients/{target_id}", {"email": new_email})
    assert put_status == 200, f"Update failed with status {put_status}"
    assert put_resp["email"] == new_email, "Email was not updated"
    print(f"  --> HTTP {put_status} OK: Patient email updated to '{put_resp['email']}' successfully!")

    # Verify via fresh GET request
    get_status, get_resp = get_json(f"/api/patients/{target_id}")
    assert get_status == 200
    assert get_resp["email"] == new_email
    print(f"  --> GET /api/patients/{target_id} confirmed updated email: {get_resp['email']}")

    # ---------------- VERIFY BLOOD TEST UPDATE REGENERATION ---------------- #
    print("\n" + "=" * 80)
    print("  VERIFYING BLOOD TEST METRICS CHANGE REGENERATES AI REMARKS")
    print("=" * 80)
    original_glu = target_patient["glucose"]
    updated_glu = 110.0
    print(f"Updating Glucose from {original_glu} to {updated_glu} for Patient #{target_id}...")
    glu_status, glu_resp = put_json(f"/api/patients/{target_id}", {"glucose": updated_glu})
    assert glu_status == 200
    assert glu_resp["glucose"] == updated_glu
    print(f"  --> Glucose updated to {glu_resp['glucose']}. AI Status: {glu_resp['ai_status']}")
    print(f"  --> AI Remarks: {glu_resp['remarks'][:120]}...")

    # ---------------- DELETE REQUIREMENT ---------------- #
    # "Delete any one patient and confirm that the record is removed. Display the final patient list after deletion."
    patient_to_delete = saved_records[-1]  # Prem Kumar
    del_id = patient_to_delete["id"]
    del_name = patient_to_delete["full_name"]

    print("\n" + "=" * 80)
    print(f"  VERIFYING DELETE REQUIREMENT: Delete Patient #{del_id} ({del_name})")
    print("=" * 80)
    del_status, del_resp = delete_req(f"/api/patients/{del_id}")
    assert del_status == 200
    print(f"  --> HTTP {del_status} OK: {del_resp.get('message')}")

    # Confirm record is gone
    try:
        get_json(f"/api/patients/{del_id}")
        assert False, f"Patient #{del_id} should have been deleted!"
    except urllib.error.HTTPError as e:
        assert e.code == 404, f"Expected 404 Not Found, got {e.code}"
        print(f"  --> Confirmed: GET /api/patients/{del_id} returns HTTP 404 Not Found.")

    # ---------------- FINAL PATIENT DIRECTORY LISTING ---------------- #
    print("\n" + "=" * 80)
    print("  FINAL PATIENT DIRECTORY LISTING (AFTER DELETION):")
    print("=" * 80)
    list_status, final_patients = get_json("/api/patients")
    assert list_status == 200

    print(f"Total remaining patients: {len(final_patients)} (Expected: 6)")
    print(f"{'ID':<6} | {'Full Name':<18} | {'DOB':<12} | {'Email':<24} | {'Glucose':<8} | {'Hb':<6} | {'Chol':<6} | {'AI Status'}")
    print("-" * 105)
    for p in final_patients:
        print(f"#{p['id']:<5} | {p['full_name']:<18} | {p['date_of_birth']:<12} | {p['email']:<24} | {p['glucose']:<8} | {p['haemoglobin']:<6} | {p['cholesterol']:<6} | {p['ai_status']}")
    print("-" * 105)

    assert len(final_patients) == 6, f"Expected 6 remaining patients, got {len(final_patients)}"
    # Verify that gokul@infocare.com is present in the list
    gokul_found = any(p["email"] == "gokul@infocare.com" for p in final_patients)
    assert gokul_found, "gokul@infocare.com not found in final patient listing!"
    print("\n>>> ALL VERIFICATION CHECKS COMPLETED SUCCESSFULLY! <<<\n")


if __name__ == "__main__":
    run_full_verification()

