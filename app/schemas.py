"""Pydantic schemas and validation rules for patient records and AI analysis."""

from datetime import date, datetime
import math
import re
from typing import Optional, Union, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$")


class PatientBase(BaseModel):
    """Base schema holding common fields and validation logic."""

    full_name: str = Field(..., description="Full legal name of the patient")
    date_of_birth: Union[date, str] = Field(..., description="Date of birth in DD/MM/YYYY, DD.MM.YYYY, or YYYY-MM-DD format")
    email: str = Field(..., description="Patient email address")
    glucose: float = Field(..., description="Blood glucose level (mg/dL)")
    haemoglobin: float = Field(..., description="Blood haemoglobin level (g/dL)")
    cholesterol: float = Field(..., description="Blood cholesterol level (mg/dL)")

    @field_validator("full_name", mode="before")
    @classmethod
    def validate_full_name(cls, v: Any) -> str:
        if v is None:
            raise ValueError("Full name is required.")
        if not isinstance(v, str):
            v = str(v)
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Full name cannot be empty.")
        if len(cleaned) < 2:
            raise ValueError("Full name must be at least 2 characters long.")
        return cleaned

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def validate_date_of_birth(cls, v: Any) -> date:
        if v is None or (isinstance(v, str) and not v.strip()):
            raise ValueError("Date of birth is required.")

        if isinstance(v, date) and not isinstance(v, datetime):
            parsed_date = v
        elif isinstance(v, datetime):
            parsed_date = v.date()
        elif isinstance(v, str):
            v_str = v.strip()
            # Try supported formats
            formats = ["%d/%m/%Y", "%d.%m.%Y", "%Y-%m-%d", "%d-%m-%Y"]
            parsed_date = None
            last_err = None

            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(v_str, fmt).date()
                    break
                except ValueError as e:
                    last_err = e

            if parsed_date is None:
                raise ValueError(
                    f"Invalid calendar date or format: '{v_str}'. "
                    "Accepted formats are DD/MM/YYYY or DD.MM.YYYY."
                )
        else:
            raise ValueError("Invalid type for date of birth.")

        # Reject future dates
        today = date.today()
        if parsed_date > today:
            raise ValueError(
                f"Date of birth ({parsed_date.strftime('%d/%m/%Y')}) cannot be in the future. "
                f"Today is {today.strftime('%d/%m/%Y')}."
            )

        # Reject unreasonable past dates (e.g., older than 130 years)
        if parsed_date.year < 1890:
            raise ValueError("Date of birth must be after year 1890.")

        return parsed_date

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: Any) -> str:
        if v is None:
            raise ValueError("Email is required.")
        if not isinstance(v, str):
            v = str(v)
        email_str = v.strip()
        if not email_str:
            raise ValueError("Email cannot be empty.")

        if not EMAIL_REGEX.match(email_str):
            raise ValueError(f"Invalid email address format: '{email_str}'.")

        return email_str.lower()

    @field_validator("glucose", "haemoglobin", "cholesterol", mode="before")
    @classmethod
    def validate_numeric_metric(cls, v: Any, info) -> float:
        field_name = info.field_name.replace("_", " ").title()
        if v is None or (isinstance(v, str) and not v.strip()):
            raise ValueError(f"{field_name} is required.")

        try:
            val = float(v)
        except (ValueError, TypeError):
            raise ValueError(f"{field_name} must be a valid numeric value.")

        if math.isnan(val) or math.isinf(val):
            raise ValueError(f"{field_name} cannot be NaN or infinite.")

        if val < 0:
            raise ValueError(f"{field_name} cannot be negative.")

        return round(val, 2)


class PatientCreate(PatientBase):
    """Schema for creating a patient record."""
    pass


class PatientUpdate(BaseModel):
    """Schema for updating an existing patient record (all fields optional)."""

    full_name: Optional[str] = None
    date_of_birth: Optional[Union[date, str]] = None
    email: Optional[str] = None
    glucose: Optional[float] = None
    haemoglobin: Optional[float] = None
    cholesterol: Optional[float] = None

    @field_validator("full_name", mode="before")
    @classmethod
    def validate_full_name(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        cleaned = str(v).strip()
        if not cleaned:
            raise ValueError("Full name cannot be empty.")
        if len(cleaned) < 2:
            raise ValueError("Full name must be at least 2 characters long.")
        return cleaned

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def validate_date_of_birth(cls, v: Any) -> Optional[date]:
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        return PatientBase.validate_date_of_birth(v)

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: Any) -> Optional[str]:
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        return PatientBase.validate_email(v)

    @field_validator("glucose", "haemoglobin", "cholesterol", mode="before")
    @classmethod
    def validate_numeric_metric(cls, v: Any, info) -> Optional[float]:
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        return PatientBase.validate_numeric_metric(v, info)


class PatientResponse(BaseModel):
    """Schema for serialized patient response."""

    id: int
    full_name: str
    date_of_birth: date
    email: str
    glucose: float
    haemoglobin: float
    cholesterol: float
    remarks: Optional[str] = None
    ai_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatientListResponse(BaseModel):
    """Schema for listing patient records."""

    total: int
    patients: list[PatientResponse]


class RemarksGenerateResponse(BaseModel):
    """Schema for the response when generating AI remarks."""

    patient_id: int
    ai_status: str
    remarks: Optional[str] = None
    error: Optional[str] = None

