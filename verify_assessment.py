"""Technical Assessment Benchmark Verification Script.

Tests each of the 10 provided assessment records through the application's
Pydantic validation and records the exact outcome.
Demonstrates 7 successful records and 3 correctly rejected records.
"""

from pydantic import ValidationError
from app.schemas import PatientCreate

ASSESSMENT_TEST_DATA = [
    {
        "test_id": 1,
        "name": "Robyn Pears",
        "dob": "28.01.1960",
        "email": "robyn@gmail.com",
        "glucose": 232,
        "haemoglobin": 13.5,
        "cholesterol": 180,
        "expected_action": "VALID (Save)",
    },
    {
        "test_id": 2,
        "name": "John Hunter",
        "dob": "10.12.1990",
        "email": "hunter@gmail",
        "glucose": 94,
        "haemoglobin": 15,
        "cholesterol": 200,
        "expected_action": "REJECT (Invalid email: hunter@gmail)",
    },
    {
        "test_id": 3,
        "name": "Darryl Tim",
        "dob": "12.11.1993",
        "email": "timd@smh.com.au",
        "glucose": 240,
        "haemoglobin": 18.6,
        "cholesterol": 326,
        "expected_action": "VALID (Save)",
    },
    {
        "test_id": 4,
        "name": "Peter Larry",
        "dob": "31.11.2001",
        "email": "Larry@hotmail.com",
        "glucose": 88,
        "haemoglobin": 11.5,
        "cholesterol": 165,
        "expected_action": "REJECT (Invalid date: 31.11.2001)",
    },
    {
        "test_id": 5,
        "name": "Sam Kerr",
        "dob": "09.12.2006",
        "email": "sam@news.com.au",
        "glucose": 198,
        "haemoglobin": 8.9,
        "cholesterol": 192,
        "expected_action": "VALID (Save)",
    },
    {
        "test_id": 6,
        "name": "Robyn Pears",
        "dob": "28.01.1960",
        "email": "robyn@gmail.com",
        "glucose": 232,
        "haemoglobin": 13.5,
        "cholesterol": 180,
        "expected_action": "VALID (Save duplicate as separate record)",
    },
    {
        "test_id": 7,
        "name": "Madison XI",
        "dob": "12.09.1998",
        "email": "madison@hotmail.com",
        "glucose": 85,
        "haemoglobin": 7.6,
        "cholesterol": 163,
        "expected_action": "VALID (Save)",
    },
    {
        "test_id": 8,
        "name": "Kris Wu",
        "dob": "19.10.2030",
        "email": "Kris.wu.gmail.com",
        "glucose": 79,
        "haemoglobin": 16.5,
        "cholesterol": 197,
        "expected_action": "REJECT (Future date 2030 & invalid email)",
    },
    {
        "test_id": 9,
        "name": "Tenille Singh",
        "dob": "30.11.1991",
        "email": "Tenille@yahoo.com",
        "glucose": 101,
        "haemoglobin": 15,
        "cholesterol": 310,
        "expected_action": "VALID (Save)",
    },
    {
        "test_id": 10,
        "name": "Prem Kumar",
        "dob": "28.04.1990",
        "email": "prem@telstra.com",
        "glucose": 155,
        "haemoglobin": 12.5,
        "cholesterol": 265,
        "expected_action": "VALID (Save)",
    },
]


def run_benchmark():
    print("=" * 80)
    print("  TECHNICAL ASSESSMENT: 10 PATIENT RECORDS VALIDATION BENCHMARK")
    print("=" * 80)

    saved_count = 0
    rejected_count = 0

    for item in ASSESSMENT_TEST_DATA:
        tid = item["test_id"]
        name = item["name"]
        dob = item["dob"]
        email = item["email"]
        glu = item["glucose"]
        hb = item["haemoglobin"]
        chol = item["cholesterol"]

        print(f"\n[TEST {tid}] Patient: {name} | DOB: {dob} | Email: {email}")
        print(f"         Biomarkers: Glucose={glu}, Haemoglobin={hb}, Cholesterol={chol}")

        payload = {
            "full_name": name,
            "date_of_birth": dob,
            "email": email,
            "glucose": glu,
            "haemoglobin": hb,
            "cholesterol": chol,
        }

        try:
            patient = PatientCreate(**payload)
            saved_count += 1
            print(f"  --> RESULT: ACCEPTED / VALID")
            print(f"      Parsed DOB: {patient.date_of_birth} | Normalized Email: {patient.email}")
            print(f"      Status: Ready for Gemini AI Remark Generation and Database Persistence.")
        except ValidationError as e:
            rejected_count += 1
            print(f"  --> RESULT: REJECTED (Validation Error)")
            for err in e.errors():
                loc = ".".join(str(l) for l in err["loc"])
                msg = err["msg"].replace("Value error, ", "")
                print(f"      Validation Issue in [{loc}]: {msg}")

    print("\n" + "=" * 80)
    print(f"  BENCHMARK SUMMARY:")
    print(f"  Total Tested Records:     {len(ASSESSMENT_TEST_DATA)}")
    print(f"  Successfully Validated:   {saved_count}  (Expected: 7)")
    print(f"  Correctly Rejected:       {rejected_count}  (Expected: 3)")
    print("=" * 80)

    assert saved_count == 7, "Error: Expected exactly 7 saved records"
    assert rejected_count == 3, "Error: Expected exactly 3 rejected records"
    print("  >>> ALL ASSESSMENT CRITERIA PERFECTLY MET! <<<\n")


if __name__ == "__main__":
    run_benchmark()

