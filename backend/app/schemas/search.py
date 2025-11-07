from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from decimal import Decimal


class SearchFilters(BaseModel):
    roi_min: Optional[float] = None
    roi_max: Optional[float] = None
    margin_min: Optional[Decimal] = None
    margin_max: Optional[Decimal] = None
    bsr_max: Optional[int] = None
    sellers_count_max: Optional[int] = None
    buybox_stable: Optional[bool] = None
    marketplace: Optional[str] = None


class SearchItem(BaseModel):
    asin: str
    title: Optional[str]
    marketplace: str
    amazon_price: Optional[Decimal]
    retail_price: Optional[Decimal]
    landed_cost: Optional[Decimal]
    margin_eur: Optional[Decimal]
    roi_percent: Optional[float]
    bsr: Optional[int]
    sellers_count: Optional[int]
    buybox_stable: Optional[bool]
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    items: List[SearchItem]
    total: int
    page: int
    page_size: int
    total_pages: int

