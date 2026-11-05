"""FastAPI router for AI service health check, preview, and dashboard metrics."""

import os
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Patient
from app.services.ai_service import (
    generate_health_remarks,
    get_openrouter_api_key,
    get_openrouter_model,
    OPENROUTER_BASE_URL,
)

router = APIRouter(prefix="/api/ai", tags=["AI & Analytics"])


class BloodTestInput(BaseModel):
    glucose: float = Field(..., ge=0, description="Glucose level (mg/dL)")
    haemoglobin: float = Field(..., ge=0, description="Haemoglobin level (g/dL)")
    cholesterol: float = Field(..., ge=0, description="Cholesterol level (mg/dL)")


@router.get("/status", status_code=status.HTTP_200_OK)
def get_ai_status():
    """Check AI integration configuration status."""
    api_key = get_openrouter_api_key()
    configured = bool(api_key and api_key not in ["your_api_key", "your_openrouter_api_key_here"])
    model = get_openrouter_model()

    return {
        "provider": "OpenRouter",
        "model": model,
        "base_url": OPENROUTER_BASE_URL,
        "is_configured": configured,
        "status": "Ready" if configured else "API Key Not Configured",
        "api_format": "OpenAI-compatible Chat Completions",
    }


@router.post("/preview", status_code=status.HTTP_200_OK)
def preview_remarks(payload: BloodTestInput):
    """Generate an on-demand AI health remarks preview without saving to database."""
    remarks, ai_status = generate_health_remarks(
        glucose=payload.glucose,
        haemoglobin=payload.haemoglobin,
        cholesterol=payload.cholesterol,
    )
    return {
        "glucose": payload.glucose,
        "haemoglobin": payload.haemoglobin,
        "cholesterol": payload.cholesterol,
        "remarks": remarks,
        "ai_status": ai_status,
    }


@router.get("/dashboard-stats", status_code=status.HTTP_200_OK)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Retrieve statistical summary for the dashboard cards."""
    total_patients = db.query(Patient).count()
    completed_ai = db.query(Patient).filter(Patient.ai_status == "COMPLETED").count()
    failed_ai = db.query(Patient).filter(Patient.ai_status == "FAILED").count()
    pending_ai = db.query(Patient).filter(Patient.ai_status == "PENDING").count()

    # Calculate blood test averages if records exist
    avg_glucose = db.query(func.avg(Patient.glucose)).scalar() or 0.0
    avg_haemoglobin = db.query(func.avg(Patient.haemoglobin)).scalar() or 0.0
    avg_cholesterol = db.query(func.avg(Patient.cholesterol)).scalar() or 0.0

    return {
        "total_patients": total_patients,
        "ai_processed": completed_ai,
        "pending_ai": pending_ai + failed_ai,
        "failed_ai": failed_ai,
        "averages": {
            "glucose": round(avg_glucose, 1),
            "haemoglobin": round(avg_haemoglobin, 1),
            "cholesterol": round(avg_cholesterol, 1),
        },
    }
