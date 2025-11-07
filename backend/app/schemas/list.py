from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ListItemCreate(BaseModel):
    product_id: int
    notes: Optional[str] = None


class ListItemResponse(BaseModel):
    id: int
    product_id: int
    asin: str
    title: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ListCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ListResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    items: List[ListItemResponse] = []
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

