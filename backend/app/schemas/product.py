from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class OfferAmazonResponse(BaseModel):
    id: int
    marketplace: str
    price: Decimal
    shipping_cost: Decimal
    fba_fee: Optional[Decimal]
    referral_fee: Optional[Decimal]
    sellers_count: int
    buybox_stable: bool
    bsr: Optional[int]
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OfferRetailResponse(BaseModel):
    id: int
    store_name: str
    price: Decimal
    shipping_cost: Decimal
    availability: bool
    url: Optional[str]
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ScoreResponse(BaseModel):
    id: int
    marketplace: str
    landed_cost: Optional[Decimal]
    margin_eur: Optional[Decimal]
    roi_percent: Optional[float]
    calculated_at: datetime
    
    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    asin: str
    title: Optional[str]
    brand: Optional[str]
    category: Optional[str]
    image_url: Optional[str]
    description: Optional[str]
    amazon_offers: List[OfferAmazonResponse] = []
    retail_offers: List[OfferRetailResponse] = []
    scores: List[ScoreResponse] = []
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

