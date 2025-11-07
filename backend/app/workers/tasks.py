import httpx
from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.database import SessionLocal
from app.models.store import Store
from app.models.product import Product
from app.models.offer import OfferRetail
from app.models.score import Score
from app.models.alert import Alert
from app.models.job import Job, JobStatus
from app.models.offer import OfferAmazon
from decimal import Decimal
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


def scrape_store(store_id: int, dry_run: bool = False) -> Dict[str, Any]:
    """
    Scrape une boutique retail pour récupérer les prix des produits.
    
    Args:
        store_id: ID de la boutique à scraper
        dry_run: Si True, ne fait que simuler le scraping (pour tests)
    
    Returns:
        Dict avec les résultats du scraping
    """
    db: Session = SessionLocal()
    job = None
    
    try:
        # Créer un job
        job = Job(
            job_type="scrape_store",
            status=JobStatus.RUNNING,
            parameters={"store_id": store_id, "dry_run": dry_run}
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise ValueError(f"Boutique {store_id} introuvable")
        
        if not store.is_active:
            raise ValueError(f"Boutique {store_id} inactive")
        
        if dry_run:
            # Mode dry-run : simuler le scraping
            logger.info(f"DRY-RUN: Scraping de {store.name} ({store.url})")
            result = {
                "store_id": store_id,
                "store_name": store.name,
                "products_scraped": 0,
                "offers_found": 0,
                "dry_run": True
            }
            job.status = JobStatus.COMPLETED
            job.result = result
            db.commit()
            return result
        
        # Charger les sélecteurs depuis JSON
        selectors = store.selectors if isinstance(store.selectors, dict) else json.loads(store.selectors)
        
        # Scraping avec Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(store.url, wait_until="networkidle")
            
            # Extraire les produits selon les sélecteurs
            products = []
            product_selector = selectors.get("product_selector", "")
            price_selector = selectors.get("price_selector", "")
            title_selector = selectors.get("title_selector", "")
            
            if product_selector:
                elements = page.query_selector_all(product_selector)
                for element in elements:
                    try:
                        price_text = element.query_selector(price_selector).inner_text() if price_selector else ""
                        title_text = element.query_selector(title_selector).inner_text() if title_selector else ""
                        
                        # Nettoyer le prix
                        price = clean_price(price_text)
                        
                        products.append({
                            "title": title_text.strip(),
                            "price": price
                        })
                    except Exception as e:
                        logger.warning(f"Erreur lors de l'extraction d'un produit: {e}")
                        continue
            
            browser.close()
        
        # Sauvegarder les offres dans la base
        offers_count = 0
        for product_data in products:
            # Chercher le produit par titre (approximatif) ou créer une offre générique
            # Pour l'instant, on sauvegarde juste les données brutes
            # Dans une vraie implémentation, on matcherait avec les produits existants
            if product_data.get("price"):
                # Créer une offre retail (nécessite un product_id, donc on skip pour l'instant)
                offers_count += 1
        
        result = {
            "store_id": store_id,
            "store_name": store.name,
            "products_scraped": len(products),
            "offers_found": offers_count
        }
        
        job.status = JobStatus.COMPLETED
        job.result = result
        db.commit()
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors du scraping: {e}", exc_info=True)
        if job:
            job.status = JobStatus.FAILED
            job.error = str(e)
            db.commit()
        raise
    finally:
        db.close()


def clean_price(price_text: str) -> Decimal:
    """Nettoie et convertit un texte de prix en Decimal"""
    # Enlever tout sauf les chiffres, points et virgules
    cleaned = "".join(c for c in price_text if c.isdigit() or c in ".,")
    # Remplacer la virgule par un point
    cleaned = cleaned.replace(",", ".")
    try:
        return Decimal(cleaned)
    except:
        return Decimal("0")


def refresh_scores(marketplace: str = None) -> Dict[str, Any]:
    """
    Recalcule les scores (landed_cost, marge, ROI) pour tous les produits.
    
    Args:
        marketplace: Marketplace spécifique (optionnel)
    
    Returns:
        Dict avec les résultats
    """
    db: Session = SessionLocal()
    job = None
    
    try:
        job = Job(
            job_type="refresh_scores",
            status=JobStatus.RUNNING,
            parameters={"marketplace": marketplace}
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Récupérer les paramètres de settings
        from app.models.settings import Settings as SettingsModel
        tva_setting = db.query(SettingsModel).filter(SettingsModel.key == "tva_rate").first()
        tva_rate = 0.20  # Par défaut
        if tva_setting and isinstance(tva_setting.value, dict):
            tva_rate = tva_setting.value.get("value", 0.20)
        
        fba_fees_setting = db.query(SettingsModel).filter(SettingsModel.key == "fba_fees").first()
        fba_fees = {}
        if fba_fees_setting and isinstance(fba_fees_setting.value, dict):
            fba_fees = fba_fees_setting.value
        
        prep_cost_setting = db.query(SettingsModel).filter(SettingsModel.key == "prep_cost").first()
        prep_cost = Decimal("0")
        if prep_cost_setting and isinstance(prep_cost_setting.value, dict):
            prep_cost = Decimal(str(prep_cost_setting.value.get("value", 0)))
        
        # Récupérer les produits avec leurs offres
        query = db.query(Product)
        if marketplace:
            # Filtrer par marketplace via les offres Amazon
            query = query.join(OfferAmazon).filter(OfferAmazon.marketplace == marketplace)
        
        products = query.all()
        scores_updated = 0
        
        for product in products:
            # Pour chaque marketplace, calculer le meilleur score
            amazon_offers = db.query(OfferAmazon).filter(OfferAmazon.product_id == product.id).all()
            
            for amazon_offer in amazon_offers:
                marketplace_code = amazon_offer.marketplace
                
                # Récupérer la meilleure offre retail
                retail_offers = db.query(OfferRetail).filter(
                    OfferRetail.product_id == product.id,
                    OfferRetail.availability == True
                ).order_by(OfferRetail.price).first()
                
                if not retail_offers:
                    continue
                
                # Calculer landed_cost
                retail_total = retail_offers.price + retail_offers.shipping_cost
                landed_cost = retail_total * (Decimal("1") + Decimal(str(tva_rate))) + prep_cost
                
                # Récupérer les fees pour ce marketplace
                marketplace_fees = fba_fees.get(marketplace_code, {})
                fba_fee = Decimal(str(marketplace_fees.get("fba_fee", 0)))
                referral_fee = Decimal(str(marketplace_fees.get("referral_fee", 0)))
                
                # Calculer marge et ROI
                total_fees = fba_fee + referral_fee
                margin_eur = amazon_offer.price - total_fees - landed_cost
                
                if landed_cost > 0:
                    roi_percent = float((margin_eur / landed_cost) * Decimal("100"))
                else:
                    roi_percent = 0.0
                
                # Mettre à jour ou créer le score
                score = db.query(Score).filter(
                    Score.product_id == product.id,
                    Score.marketplace == marketplace_code
                ).first()
                
                if score:
                    score.landed_cost = landed_cost
                    score.margin_eur = margin_eur
                    score.roi_percent = Decimal(str(roi_percent))
                    score.best_retail_offer_id = retail_offers.id
                    score.best_amazon_offer_id = amazon_offer.id
                else:
                    score = Score(
                        product_id=product.id,
                        marketplace=marketplace_code,
                        landed_cost=landed_cost,
                        margin_eur=margin_eur,
                        roi_percent=Decimal(str(roi_percent)),
                        best_retail_offer_id=retail_offers.id,
                        best_amazon_offer_id=amazon_offer.id
                    )
                    db.add(score)
                
                scores_updated += 1
        
        db.commit()
        
        result = {
            "scores_updated": scores_updated,
            "marketplace": marketplace
        }
        
        job.status = JobStatus.COMPLETED
        job.result = result
        db.commit()
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors du refresh des scores: {e}", exc_info=True)
        if job:
            job.status = JobStatus.FAILED
            job.error = str(e)
            db.commit()
        raise
    finally:
        db.close()


def run_alert_task(alert_id: int) -> Dict[str, Any]:
    """
    Exécute une alerte et retourne les produits correspondants.
    
    Args:
        alert_id: ID de l'alerte à exécuter
    
    Returns:
        Dict avec les produits correspondants
    """
    db: Session = SessionLocal()
    job = None
    
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise ValueError(f"Alerte {alert_id} introuvable")
        
        if not alert.is_active:
            raise ValueError(f"Alerte {alert_id} inactive")
        
        job = Job(
            job_type="run_alerts",
            status=JobStatus.RUNNING,
            parameters={"alert_id": alert_id}
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        filters = alert.filters
        
        # Construire la requête avec les filtres
        query = db.query(
            Product.id,
            Product.asin,
            Product.title,
            Score.marketplace,
            Score.roi_percent,
            Score.margin_eur,
            OfferAmazon.bsr,
            OfferAmazon.sellers_count,
            OfferAmazon.buybox_stable
        ).join(
            Score, Score.product_id == Product.id
        ).join(
            OfferAmazon, and_(
                OfferAmazon.product_id == Product.id,
                OfferAmazon.marketplace == Score.marketplace
            )
        )
        
        # Appliquer les filtres
        if filters.get("roi_min"):
            query = query.filter(Score.roi_percent >= Decimal(str(filters["roi_min"])))
        if filters.get("roi_max"):
            query = query.filter(Score.roi_percent <= Decimal(str(filters["roi_max"])))
        if filters.get("margin_min"):
            query = query.filter(Score.margin_eur >= Decimal(str(filters["margin_min"])))
        if filters.get("margin_max"):
            query = query.filter(Score.margin_eur <= Decimal(str(filters["margin_max"])))
        if filters.get("bsr_max"):
            query = query.filter(OfferAmazon.bsr <= filters["bsr_max"])
        if filters.get("sellers_count_max"):
            query = query.filter(OfferAmazon.sellers_count <= filters["sellers_count_max"])
        if filters.get("buybox_stable") is not None:
            query = query.filter(OfferAmazon.buybox_stable == filters["buybox_stable"])
        if filters.get("marketplace"):
            query = query.filter(Score.marketplace == filters["marketplace"])
        
        results = query.all()
        
        products = []
        for row in results:
            products.append({
                "asin": row.asin,
                "title": row.title,
                "marketplace": row.marketplace,
                "roi_percent": float(row.roi_percent) if row.roi_percent else None,
                "margin_eur": float(row.margin_eur) if row.margin_eur else None,
                "bsr": row.bsr,
                "sellers_count": row.sellers_count,
                "buybox_stable": row.buybox_stable
            })
        
        result = {
            "alert_id": alert_id,
            "alert_name": alert.name,
            "products_count": len(products),
            "products": products
        }
        
        job.status = JobStatus.COMPLETED
        job.result = result
        db.commit()
        
        # Mettre à jour last_run_at de l'alerte
        from datetime import datetime
        alert.last_run_at = datetime.utcnow()
        db.commit()
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'alerte: {e}", exc_info=True)
        if job:
            job.status = JobStatus.FAILED
            job.error = str(e)
            db.commit()
        raise
    finally:
        db.close()

