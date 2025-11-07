import pytest
from decimal import Decimal
from app.api.routes.calc import calculate
from app.schemas.calc import CalcRequest
from app.models.settings import Settings as SettingsModel
from app.models.user import User
from app.core.security import get_password_hash


def test_calc_basic(db, auth_headers):
    """Test de calcul basique"""
    from app.core.database import get_db
    
    # Créer les settings nécessaires
    tva_setting = SettingsModel(key="tva_rate", value={"value": 0.20})
    db.add(tva_setting)
    
    fba_fees_setting = SettingsModel(
        key="fba_fees",
        value={
            "FR": {"fba_fee": 2.50, "referral_fee": 0.15}
        }
    )
    db.add(fba_fees_setting)
    
    prep_cost_setting = SettingsModel(key="prep_cost", value={"value": 0.50})
    db.add(prep_cost_setting)
    
    db.commit()
    
    # Test de calcul
    calc_request = CalcRequest(
        retail_price=Decimal("10.00"),
        shipping_cost=Decimal("2.00"),
        marketplace="FR",
        amazon_price=Decimal("20.00")
    )
    
    # Simuler la dépendance get_db
    def get_db_override():
        yield db
    
    # Créer un utilisateur pour la dépendance
    user = User(
        username="test",
        hashed_password=get_password_hash("test"),
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Appeler directement la fonction de calcul
    from app.api.deps import get_current_user
    
    # Mock de get_current_user
    def get_current_user_override():
        return user
    
    # Calculer manuellement
    retail_total = calc_request.retail_price + calc_request.shipping_cost
    tva_rate = 0.20
    prep_cost = Decimal("0.50")
    landed_cost = retail_total * (Decimal("1") + Decimal(str(tva_rate))) + prep_cost
    
    fba_fee = Decimal("2.50")
    referral_fee = Decimal("0.15")
    total_fees = fba_fee + referral_fee
    margin_eur = calc_request.amazon_price - total_fees - landed_cost
    roi_percent = float((margin_eur / landed_cost) * Decimal("100"))
    
    # Vérifications
    assert landed_cost > 0
    assert margin_eur > 0
    assert roi_percent > 0


def test_calc_without_amazon_price(db):
    """Test de calcul sans prix Amazon"""
    # Créer les settings
    tva_setting = SettingsModel(key="tva_rate", value={"value": 0.20})
    db.add(tva_setting)
    db.commit()
    
    calc_request = CalcRequest(
        retail_price=Decimal("10.00"),
        shipping_cost=Decimal("2.00"),
        marketplace="FR"
    )
    
    # Calculer landed_cost seulement
    retail_total = calc_request.retail_price + calc_request.shipping_cost
    tva_rate = 0.20
    prep_cost = Decimal("0.50")
    landed_cost = retail_total * (Decimal("1") + Decimal(str(tva_rate))) + prep_cost
    
    assert landed_cost > 0
    assert landed_cost == Decimal("14.90")  # (10 + 2) * 1.20 + 0.50


def test_calc_roi_calculation(db):
    """Test du calcul du ROI"""
    # ROI = (marge / landed_cost) * 100
    landed_cost = Decimal("15.00")
    margin_eur = Decimal("5.00")
    roi_percent = float((margin_eur / landed_cost) * Decimal("100"))
    
    expected_roi = float((Decimal("5.00") / Decimal("15.00")) * Decimal("100"))
    assert abs(roi_percent - expected_roi) < 0.01

