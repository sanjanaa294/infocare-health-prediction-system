"""Unit tests for Pydantic input validation rules.

Tests date formats, calendar validity, future dates, email formatting,
numeric constraints, negative values, and exact assessment test cases.
"""

import pytest
from datetime import date
from pydantic import ValidationError
from app.schemas import PatientCreate


class TestPatientValidation:
    """Test suite for PatientCreate validation."""

    def test_valid_patient_creation_slash_format(self):
        """Test valid patient with DD/MM/YYYY date format."""
        data = {
            "full_name": "Robyn Pears",
            "date_of_birth": "28/01/1960",
            "email": "robyn@gmail.com",
            "glucose": 232.0,
            "haemoglobin": 13.5,
            "cholesterol": 180.0,
        }
        patient = PatientCreate(**data)
        assert patient.full_name == "Robyn Pears"
        assert patient.date_of_birth == date(1960, 1, 28)
        assert patient.email == "robyn@gmail.com"
        assert patient.glucose == 232.0
        assert patient.haemoglobin == 13.5
        assert patient.cholesterol == 180.0

    def test_valid_patient_creation_dot_format(self):
        """Test valid patient with DD.MM.YYYY date format."""
        data = {
            "full_name": "Robyn Pears",
            "date_of_birth": "28.01.1960",
            "email": "robyn@gmail.com",
            "glucose": 232,
            "haemoglobin": 13.5,
            "cholesterol": 180,
        }
        patient = PatientCreate(**data)
        assert patient.date_of_birth == date(1960, 1, 28)

    def test_full_name_whitespace_trimmed(self):
        """Test that extra whitespace around full_name is stripped."""
        data = {
            "full_name": "   Robyn Pears   ",
            "date_of_birth": "28.01.1960",
            "email": "robyn@gmail.com",
            "glucose": 100,
            "haemoglobin": 14,
            "cholesterol": 190,
        }
        patient = PatientCreate(**data)
        assert patient.full_name == "Robyn Pears"

    def test_full_name_empty_rejected(self):
        """Test that empty or whitespace-only full name is rejected."""
        data = {
            "full_name": "   ",
            "date_of_birth": "28.01.1960",
            "email": "robyn@gmail.com",
            "glucose": 100,
            "haemoglobin": 14,
            "cholesterol": 190,
        }
        with pytest.raises(ValidationError) as exc_info:
            PatientCreate(**data)
        assert "Full name cannot be empty" in str(exc_info.value)

    # ---------------- EMAIL VALIDATION ---------------- #

    def test_invalid_email_missing_domain_extension_assessment_test2(self):
        """Assessment Test 2: hunter@gmail is invalid because domain extension is missing."""
        data = {
            "full_name": "John Hunter",
            "date_of_birth": "10.12.1990",
            "email": "hunter@gmail",
            "glucose": 94,
            "haemoglobin": 15,
            "cholesterol": 200,
        }
        with pytest.raises(ValidationError) as exc_info:
            PatientCreate(**data)
        assert "Invalid email address format" in str(exc_info.value)

    def test_invalid_email_missing_at_symbol_assessment_test8(self):
        """Assessment Test 8: Kris.wu.gmail.com has no @ symbol."""
        data = {
            "full_name": "Kris Wu",
            "date_of_birth": "19.10.2000",  # Using valid date to isolate email
            "email": "Kris.wu.gmail.com",
            "glucose": 79,
            "haemoglobin": 16.5,
            "cholesterol": 197,
        }
        with pytest.raises(ValidationError) as exc_info:
            PatientCreate(**data)
        assert "Invalid email address format" in str(exc_info.value)

    def test_empty_email_rejected(self):
        """Test that empty email string is rejected."""
        data = {
            "full_name": "Test User",
            "date_of_birth": "10.10.1990",
            "email": "   ",
            "glucose": 100,
            "haemoglobin": 14,
            "cholesterol": 190,
        }
        with pytest.raises(ValidationError) as exc_info:
            PatientCreate(**data)
        assert "Email cannot be empty" in str(exc_info.value)

    # ---------------- DATE VALIDATION ---------------- #

    def test_invalid_calendar_date_assessment_test4(self):
        """Assessment Test 4: 31.11.2001 is invalid because November has 30 days."""
        data = {
            "full_name": "Peter Larry",
            "date_of_birth": "31.11.2001",
            "email": "Larry@hotmail.com",
            "glucose": 88,
            "haemoglobin": 11.5,
            "cholesterol": 165,
        }
        with pytest.raises(ValidationError) as exc_info:
            PatientCreate(**data)
        assert "Invalid calendar date or format" in str(exc_info.value)

    def test_future_date_rejected_assessment_test8(self):
        """Assessment Test 8: 19.10.2030 is in the future."""
        data = {
            "full_name": "Kris Wu",
            "date_of_birth": "19.10.2030",
            "email": "kris@gmail.com",  # Using valid email to isolate date
            "glucose": 79,
            "haemoglobin": 16.5,
            "cholesterol": 197,
        }
        with pytest.raises(ValidationError) as exc_info:
            PatientCreate(**data)
        assert "cannot be in the future" in str(exc_info.value)

    # ---------------- NUMERIC BLOOD TEST METRICS VALIDATION ---------------- #

    def test_negative_glucose_rejected(self):
        """Negative glucose must be rejected."""
        data = {
            "full_name": "Test Patient",
            "date_of_birth": "10.10.1990",
            "email": "test@example.com",
            "glucose": -50.0,
            "haemoglobin": 14.0,
            "cholesterol": 190.0,
        }
        with pytest.raises(ValidationError) as exc_info:
            PatientCreate(**data)
        assert "cannot be negative" in str(exc_info.value)

    def test_negative_haemoglobin_rejected(self):
        """Negative haemoglobin must be rejected."""
        data = {
            "full_name": "Test Patient",
            "date_of_birth": "10.10.1990",
            "email": "test@example.com",
            "glucose": 100.0,
            "haemoglobin": -12.0,
            "cholesterol": 190.0,
        }
        with pytest.raises(ValidationError) as exc_info:
            PatientCreate(**data)
        assert "cannot be negative" in str(exc_info.value)

    def test_negative_cholesterol_rejected(self):
        """Negative cholesterol must be rejected."""
        data = {
            "full_name": "Test Patient",
            "date_of_birth": "10.10.1990",
            "email": "test@example.com",
            "glucose": 100.0,
            "haemoglobin": 14.0,
            "cholesterol": -180.0,
        }
        with pytest.raises(ValidationError) as exc_info:
            PatientCreate(**data)
        assert "cannot be negative" in str(exc_info.value)

    def test_non_numeric_metric_rejected(self):
        """Non-numeric blood metric must be rejected."""
        data = {
            "full_name": "Test Patient",
            "date_of_birth": "10.10.1990",
            "email": "test@example.com",
            "glucose": "not_a_number",
            "haemoglobin": 14.0,
            "cholesterol": 180.0,
        }
        with pytest.raises(ValidationError) as exc_info:
            PatientCreate(**data)
        assert "must be a valid numeric value" in str(exc_info.value)

    def test_nan_blood_metric_rejected(self):
        """NaN blood metric value must be rejected."""
        data = {
            "full_name": "Test Patient",
            "date_of_birth": "10.10.1990",
            "email": "test@example.com",
            "glucose": float("nan"),
            "haemoglobin": 14.0,
            "cholesterol": 180.0,
        }
        with pytest.raises(ValidationError) as exc_info:
            PatientCreate(**data)
        assert "cannot be NaN or infinite" in str(exc_info.value)

    # ---------------- COMPLETE ASSESSMENT 10 TEST CASES VERIFICATION ---------------- #

    def test_assessment_10_cases_matrix(self):
        """Verify the exact expected outcome for each of the 10 assessment test records."""
        test_cases = [
            # Test 1: Valid
            (
                {"full_name": "Robyn Pears", "date_of_birth": "28.01.1960", "email": "robyn@gmail.com", "glucose": 232, "haemoglobin": 13.5, "cholesterol": 180},
                True,
                "Test 1: Robyn Pears should be valid"
            ),
            # Test 2: Invalid Email
            (
                {"full_name": "John Hunter", "date_of_birth": "10.12.1990", "email": "hunter@gmail", "glucose": 94, "haemoglobin": 15, "cholesterol": 200},
                False,
                "Test 2: John Hunter has invalid email hunter@gmail"
            ),
            # Test 3: Valid
            (
                {"full_name": "Darryl Tim", "date_of_birth": "12.11.1993", "email": "timd@smh.com.au", "glucose": 240, "haemoglobin": 18.6, "cholesterol": 326},
                True,
                "Test 3: Darryl Tim should be valid"
            ),
            # Test 4: Invalid Date (31.11.2001)
            (
                {"full_name": "Peter Larry", "date_of_birth": "31.11.2001", "email": "Larry@hotmail.com", "glucose": 88, "haemoglobin": 11.5, "cholesterol": 165},
                False,
                "Test 4: Peter Larry has invalid calendar date 31.11.2001"
            ),
            # Test 5: Valid
            (
                {"full_name": "Sam Kerr", "date_of_birth": "09.12.2006", "email": "sam@news.com.au", "glucose": 198, "haemoglobin": 8.9, "cholesterol": 192},
                True,
                "Test 5: Sam Kerr should be valid"
            ),
            # Test 6: Valid duplicate of Test 1
            (
                {"full_name": "Robyn Pears", "date_of_birth": "28.01.1960", "email": "robyn@gmail.com", "glucose": 232, "haemoglobin": 13.5, "cholesterol": 180},
                True,
                "Test 6: Robyn Pears duplicate should be valid"
            ),
            # Test 7: Valid
            (
                {"full_name": "Madison XI", "date_of_birth": "12.09.1998", "email": "madison@hotmail.com", "glucose": 85, "haemoglobin": 7.6, "cholesterol": 163},
                True,
                "Test 7: Madison XI should be valid"
            ),
            # Test 8: Future date and invalid email
            (
                {"full_name": "Kris Wu", "date_of_birth": "19.10.2030", "email": "Kris.wu.gmail.com", "glucose": 79, "haemoglobin": 16.5, "cholesterol": 197},
                False,
                "Test 8: Kris Wu has future date 2030 and invalid email"
            ),
            # Test 9: Valid
            (
                {"full_name": "Tenille Singh", "date_of_birth": "30.11.1991", "email": "Tenille@yahoo.com", "glucose": 101, "haemoglobin": 15, "cholesterol": 310},
                True,
                "Test 9: Tenille Singh should be valid"
            ),
            # Test 10: Valid
            (
                {"full_name": "Prem Kumar", "date_of_birth": "28.04.1990", "email": "prem@telstra.com", "glucose": 155, "haemoglobin": 12.5, "cholesterol": 265},
                True,
                "Test 10: Prem Kumar should be valid"
            ),
        ]

        valid_count = 0
        rejected_count = 0

        for payload, should_be_valid, description in test_cases:
            if should_be_valid:
                patient = PatientCreate(**payload)
                assert patient is not None, description
                valid_count += 1
            else:
                with pytest.raises(ValidationError):
                    PatientCreate(**payload)
                rejected_count += 1

        assert valid_count == 7, f"Expected 7 valid records, got {valid_count}"
        assert rejected_count == 3, f"Expected 3 rejected records, got {rejected_count}"

