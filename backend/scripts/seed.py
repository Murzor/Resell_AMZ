"""
Script de seed pour initialiser la base de données avec des données de test.
"""
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import *
from app.core.security import get_password_hash
from app.core.config import settings
from decimal import Decimal

def seed():
    db: Session = SessionLocal()
    
    try:
        # Créer l'utilisateur admin
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            user = User(
                username="admin",
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                is_active=True
            )
            db.add(user)
            db.commit()
            print("✓ Utilisateur admin créé")
        else:
            print("✓ Utilisateur admin existe déjà")
        
        # Créer les settings par défaut
        settings_data = [
            {
                "key": "tva_rate",
                "value": {"value": 0.20}  # 20% TVA
            },
            {
                "key": "prep_cost",
                "value": {"value": 0.50}  # 0.50€ de préparation
            },
            {
                "key": "fba_fees",
                "value": {
                    "FR": {"fba_fee": 2.50, "referral_fee": 0.15},
                    "DE": {"fba_fee": 2.50, "referral_fee": 0.15},
                    "IT": {"fba_fee": 2.50, "referral_fee": 0.15},
                    "ES": {"fba_fee": 2.50, "referral_fee": 0.15}
                }
            }
        ]
        
        for setting_data in settings_data:
            existing = db.query(Settings).filter(Settings.key == setting_data["key"]).first()
            if not existing:
                setting = Settings(key=setting_data["key"], value=setting_data["value"])
                db.add(setting)
                print(f"✓ Setting {setting_data['key']} créé")
            else:
                print(f"✓ Setting {setting_data['key']} existe déjà")
        
        db.commit()
        
        # Créer une boutique de test
        store = db.query(Store).filter(Store.name == "Boutique Test").first()
        if not store:
            store = Store(
                name="Boutique Test",
                url="https://example.com",
                selectors={
                    "product_selector": ".product",
                    "price_selector": ".price",
                    "title_selector": ".title"
                },
                is_active=True
            )
            db.add(store)
            db.commit()
            print("✓ Boutique de test créée")
        else:
            print("✓ Boutique de test existe déjà")
        
        print("\n✓ Seed terminé avec succès!")
        
    except Exception as e:
        print(f"✗ Erreur lors du seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()

