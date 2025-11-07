from pydantic import BaseModel
from typing import Dict, Any, Optional


class SettingsCreate(BaseModel):
    key: str
    value: Dict[str, Any]


class SettingsUpdate(BaseModel):
    value: Dict[str, Any]


class SettingsResponse(BaseModel):
    id: int
    key: str
    value: Dict[str, Any]
    
    class Config:
        from_attributes = True

