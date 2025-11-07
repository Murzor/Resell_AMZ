from sqlalchemy import Column, Integer, String, Numeric, Boolean, JSON, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    filters = Column(JSON, nullable=False)  # Filtres: ROI%, marge€, BSR, etc.
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

