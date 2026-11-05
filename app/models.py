"""SQLAlchemy models for the Health Prediction Application."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime
from app.database import Base


def utcnow():
    """Return current UTC timestamp without timezone offset for clean database storage."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Patient(Base):
    """Patient table storing personal details, blood test metrics, and AI health observations."""

    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    # Email is NOT unique as assessment data contains duplicate patient entries that must be stored separately
    email = Column(String(255), nullable=False, index=True)
    glucose = Column(Float, nullable=False)
    haemoglobin = Column(Float, nullable=False)
    cholesterol = Column(Float, nullable=False)
    remarks = Column(Text, nullable=True)
    ai_status = Column(String(50), nullable=False, default="PENDING")
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    def to_dict(self):
        """Serialize patient model to a dictionary representation."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "date_of_birth": self.date_of_birth.strftime("%d/%m/%Y") if self.date_of_birth else None,
            "date_of_birth_iso": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "email": self.email,
            "glucose": self.glucose,
            "haemoglobin": self.haemoglobin,
            "cholesterol": self.cholesterol,
            "remarks": self.remarks,
            "ai_status": self.ai_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

