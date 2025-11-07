from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.offer import OfferAmazon, OfferRetail
from app.models.score import Score
from app.models.store import Store
from app.schemas.product import ProductResponse, OfferAmazonResponse, OfferRetailResponse, ScoreResponse

router = APIRouter(prefix="/api/product", tags=["product"])


@router.get("/{asin}", response_model=ProductResponse)
def get_product(
    asin: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.asin == asin).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    
    # Récupérer les offres Amazon
    amazon_offers = db.query(OfferAmazon).filter(OfferAmazon.product_id == product.id).all()
    amazon_offers_data = [
        OfferAmazonResponse(
            id=offer.id,
            marketplace=offer.marketplace,
            price=offer.price,
            shipping_cost=offer.shipping_cost,
            fba_fee=offer.fba_fee,
            referral_fee=offer.referral_fee,
            sellers_count=offer.sellers_count,
            buybox_stable=offer.buybox_stable,
            bsr=offer.bsr,
            updated_at=offer.updated_at
        )
        for offer in amazon_offers
    ]
    
    # Récupérer les offres retail
    retail_offers = db.query(OfferRetail).filter(OfferRetail.product_id == product.id).all()
    retail_offers_data = []
    for offer in retail_offers:
        store = db.query(Store).filter(Store.id == offer.store_id).first()
        retail_offers_data.append(OfferRetailResponse(
            id=offer.id,
            store_name=store.name if store else "Unknown",
            price=offer.price,
            shipping_cost=offer.shipping_cost,
            availability=offer.availability,
            url=offer.url,
            updated_at=offer.updated_at
        ))
    
    # Récupérer les scores
    scores = db.query(Score).filter(Score.product_id == product.id).all()
    scores_data = [
        ScoreResponse(
            id=score.id,
            marketplace=score.marketplace,
            landed_cost=score.landed_cost,
            margin_eur=score.margin_eur,
            roi_percent=float(score.roi_percent) if score.roi_percent else None,
            calculated_at=score.calculated_at
        )
        for score in scores
    ]
    
    return ProductResponse(
        id=product.id,
        asin=product.asin,
        title=product.title,
        brand=product.brand,
        category=product.category,
        image_url=product.image_url,
        description=product.description,
        amazon_offers=amazon_offers_data,
        retail_offers=retail_offers_data,
        scores=scores_data,
        created_at=product.created_at,
        updated_at=product.updated_at
    )

