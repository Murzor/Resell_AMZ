from sqlalchemy import Column, Integer, String, JSON, DateTime, Enum
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class JobStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String, nullable=False, index=True)  # scrape_store, refresh_scores, run_alerts
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, index=True)
    parameters = Column(JSON)  # Paramètres du job
    result = Column(JSON)  # Résultat du job
    error = Column(String)  # Message d'erreur si échec
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

