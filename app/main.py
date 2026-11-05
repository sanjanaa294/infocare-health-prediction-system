"""Main FastAPI application entry point.

Mounts routers, configures Jinja2 templates, static assets, and database tables.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.models import Patient
from app.routers import patients, health_ai


# Lifespan context manager for startup table creation
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create SQLite database tables on startup if they don't exist
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="HealthCare AI Prediction & Patient Management System",
    description="Full-stack AI-powered clinical observation and patient records management platform.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Custom validation error handler to return readable messages
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        # Strip internal Pydantic prefix "Value error, " if present
        if msg.startswith("Value error, "):
            msg = msg[len("Value error, "):]
        errors.append(f"{field}: {msg}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors, "message": "Validation failed: " + "; ".join(errors)},
    )


# Paths setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Mount static files and templates
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Include API Routers
app.include_router(patients.router)
app.include_router(health_ai.router)


# ---------------- Frontend Web Page Routes ---------------- #


@app.get("/", response_class=RedirectResponse)
def root_redirect():
    """Redirect root path to the Dashboard."""
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_view(request: Request, db: Session = Depends(get_db)):
    """Render main clinical dashboard with summary metrics and recent patient list."""
    total_patients = db.query(Patient).count()
    completed_ai = db.query(Patient).filter(Patient.ai_status == "COMPLETED").count()
    pending_ai = db.query(Patient).filter(Patient.ai_status.in_(["PENDING", "FAILED"])).count()
    recent_patients = db.query(Patient).order_by(Patient.id.desc()).limit(5).all()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "active_page": "dashboard",
            "total_patients": total_patients,
            "completed_ai": completed_ai,
            "pending_ai": pending_ai,
            "recent_patients": recent_patients,
        },
    )


@app.get("/patients", response_class=HTMLResponse)
def patients_list_view(request: Request, db: Session = Depends(get_db)):
    """Render full patients directory with search, filter, and action controls."""
    patients_list = db.query(Patient).order_by(Patient.id.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="patients.html",
        context={
            "active_page": "patients",
            "patients": patients_list,
        },
    )


@app.get("/patients/add", response_class=HTMLResponse)
def add_patient_view(request: Request):
    """Render Add Patient form."""
    return templates.TemplateResponse(
        request=request,
        name="add_patient.html",
        context={
            "active_page": "add_patient",
        },
    )


@app.get("/patients/edit/{patient_id}", response_class=HTMLResponse)
def edit_patient_view(patient_id: int, request: Request, db: Session = Depends(get_db)):
    """Render Edit Patient form for the specified patient ID."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return templates.TemplateResponse(
        request=request,
        name="edit_patient.html",
        context={
            "active_page": "patients",
            "patient": patient,
        },
    )
