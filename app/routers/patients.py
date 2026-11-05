"""FastAPI router for patient management CRUD operations and AI remarks regeneration."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.database import get_db
from app.models import Patient
from app.schemas import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse,
    RemarksGenerateResponse,
)
from app.services.ai_service import generate_health_remarks

logger = logging.getLogger("patients_router")

router = APIRouter(prefix="/api/patients", tags=["Patients"])


@router.get("", response_model=List[PatientResponse], status_code=status.HTTP_200_OK)
def get_all_patients(
    search: Optional[str] = Query(None, description="Search by patient name or email"),
    db: Session = Depends(get_db),
):
    """Retrieve all patient records with optional search filter."""
    query = db.query(Patient)
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Patient.full_name.ilike(term),
                Patient.email.ilike(term),
            )
        )
    patients = query.order_by(desc(Patient.id)).all()
    return patients


@router.get("/{patient_id}", response_model=PatientResponse, status_code=status.HTTP_200_OK)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a single patient by ID."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} was not found.",
        )
    return patient


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient record, validate input, call OpenRouter AI API for remarks,

    and persist the record in SQLite database.
    Duplicate patient records are allowed per assessment instructions.
    """
    logger.info(f"Creating patient record for: {payload.full_name} ({payload.email})")

    # Generate AI health remarks based on blood test results
    remarks, ai_status = generate_health_remarks(
        glucose=payload.glucose,
        haemoglobin=payload.haemoglobin,
        cholesterol=payload.cholesterol,
    )

    new_patient = Patient(
        full_name=payload.full_name,
        date_of_birth=payload.date_of_birth,
        email=payload.email,
        glucose=payload.glucose,
        haemoglobin=payload.haemoglobin,
        cholesterol=payload.cholesterol,
        remarks=remarks,
        ai_status=ai_status,
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    logger.info(f"Successfully created patient ID {new_patient.id} with AI status: {ai_status}")
    return new_patient


@router.put("/{patient_id}", response_model=PatientResponse, status_code=status.HTTP_200_OK)
def update_patient(
    patient_id: int,
    payload: PatientUpdate,
    db: Session = Depends(get_db),
):
    """Update patient information.

    If blood test values change, AI remarks are automatically regenerated.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} was not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return patient

    # Check if blood test metrics have changed to trigger AI regeneration
    metrics_changed = False
    new_glucose = update_data.get("glucose", patient.glucose)
    new_haemoglobin = update_data.get("haemoglobin", patient.haemoglobin)
    new_cholesterol = update_data.get("cholesterol", patient.cholesterol)

    if (
        (new_glucose is not None and new_glucose != patient.glucose)
        or (new_haemoglobin is not None and new_haemoglobin != patient.haemoglobin)
        or (new_cholesterol is not None and new_cholesterol != patient.cholesterol)
    ):
        metrics_changed = True

    # Update patient fields
    for field, value in update_data.items():
        setattr(patient, field, value)

    # Regenerate remarks if metrics changed
    if metrics_changed:
        logger.info(f"Blood test metrics modified for patient {patient_id}. Regenerating AI remarks...")
        remarks, ai_status = generate_health_remarks(
            glucose=patient.glucose,
            haemoglobin=patient.haemoglobin,
            cholesterol=patient.cholesterol,
        )
        patient.remarks = remarks
        patient.ai_status = ai_status

    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_200_OK)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """Delete a patient record from the database."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} was not found.",
        )

    db.delete(patient)
    db.commit()
    logger.info(f"Deleted patient ID {patient_id}")
    return {
        "success": True,
        "message": f"Patient '{patient.full_name}' (ID: {patient_id}) was successfully deleted.",
    }


@router.post(
    "/{patient_id}/generate-remarks",
    response_model=RemarksGenerateResponse,
    status_code=status.HTTP_200_OK,
)
def regenerate_remarks(patient_id: int, db: Session = Depends(get_db)):
    """Generate or retry generating AI remarks for an existing patient record."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} was not found.",
        )

    logger.info(f"Manual AI remark generation requested for patient ID {patient_id}")
    remarks, ai_status = generate_health_remarks(
        glucose=patient.glucose,
        haemoglobin=patient.haemoglobin,
        cholesterol=patient.cholesterol,
    )

    patient.remarks = remarks
    patient.ai_status = ai_status
    db.commit()
    db.refresh(patient)

    return RemarksGenerateResponse(
        patient_id=patient.id,
        ai_status=patient.ai_status,
        remarks=patient.remarks,
        error=None if ai_status == "COMPLETED" else patient.remarks,
    )

