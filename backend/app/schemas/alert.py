from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class AlertCreate(BaseModel):
    name: str
    description: Optional[str] = None
    filters: Dict[str, Any]


class AlertUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AlertResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    filters: Dict[str, Any]
    is_active: bool
    last_run_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

