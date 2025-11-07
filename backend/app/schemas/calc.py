from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class CalcRequest(BaseModel):
    retail_price: Decimal
    shipping_cost: Decimal = Decimal("0")
    marketplace: str
    amazon_price: Optional[Decimal] = None
    tva_rate: Optional[float] = None
    fba_fee: Optional[Decimal] = None
    referral_fee: Optional[Decimal] = None
    prep_cost: Optional[Decimal] = None


class CalcResponse(BaseModel):
    landed_cost: Decimal
    margin_eur: Decimal
    roi_percent: float

