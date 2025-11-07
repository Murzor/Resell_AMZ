from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.settings import Settings as SettingsModel
from app.schemas.calc import CalcRequest, CalcResponse
from decimal import Decimal
from typing import Optional

router = APIRouter(prefix="/api/calc", tags=["calc"])


def get_setting_value(db: Session, key: str, default_value):
    """Récupère une valeur de settings ou retourne la valeur par défaut"""
    setting = db.query(SettingsModel).filter(SettingsModel.key == key).first()
    if setting and isinstance(setting.value, dict):
        return setting.value.get("value", default_value)
    return default_value


@router.post("", response_model=CalcResponse)
def calculate(
    calc_data: CalcRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Récupérer les paramètres depuis settings
    tva_rate = calc_data.tva_rate or get_setting_value(db, "tva_rate", 0.20)  # 20% par défaut
    
    # Récupérer les fees FBA par marketplace
    fba_fees_setting = get_setting_value(db, "fba_fees", {})
    fba_fee = calc_data.fba_fee
    if fba_fee is None:
        marketplace_fees = fba_fees_setting.get(calc_data.marketplace, {})
        fba_fee = Decimal(str(marketplace_fees.get("fba_fee", 0)))
    
    referral_fee = calc_data.referral_fee
    if referral_fee is None:
        marketplace_fees = fba_fees_setting.get(calc_data.marketplace, {})
        referral_fee = Decimal(str(marketplace_fees.get("referral_fee", 0)))
    
    prep_cost = calc_data.prep_cost or get_setting_value(db, "prep_cost", Decimal("0"))
    
    # Calcul du landed_cost
    # landed_cost = (retail_price + shipping_cost) * (1 + tva_rate) + prep_cost
    retail_total = calc_data.retail_price + calc_data.shipping_cost
    landed_cost = retail_total * (Decimal("1") + Decimal(str(tva_rate))) + prep_cost
    
    # Si amazon_price n'est pas fourni, on ne peut pas calculer la marge
    if calc_data.amazon_price is None:
        return CalcResponse(
            landed_cost=landed_cost,
            margin_eur=Decimal("0"),
            roi_percent=0.0
        )
    
    # Calcul de la marge
    # marge = amazon_price - fba_fee - referral_fee - landed_cost
    total_fees = fba_fee + referral_fee
    margin_eur = calc_data.amazon_price - total_fees - landed_cost
    
    # Calcul du ROI
    # ROI = (marge / landed_cost) * 100
    if landed_cost > 0:
        roi_percent = float((margin_eur / landed_cost) * Decimal("100"))
    else:
        roi_percent = 0.0
    
    return CalcResponse(
        landed_cost=landed_cost,
        margin_eur=margin_eur,
        roi_percent=roi_percent
    )

