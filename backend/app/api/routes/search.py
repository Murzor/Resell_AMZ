from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.offer import OfferAmazon, OfferRetail
from app.models.score import Score
from app.models.store import Store
from app.schemas.search import SearchResponse, SearchItem
from decimal import Decimal

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    roi_min: Optional[float] = Query(None),
    roi_max: Optional[float] = Query(None),
    margin_min: Optional[Decimal] = Query(None),
    margin_max: Optional[Decimal] = Query(None),
    bsr_max: Optional[int] = Query(None),
    sellers_count_max: Optional[int] = Query(None),
    buybox_stable: Optional[bool] = Query(None),
    marketplace: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Requête de base avec jointures
    query = db.query(
        Product.asin,
        Product.title,
        Score.marketplace,
        OfferAmazon.price.label("amazon_price"),
        OfferRetail.price.label("retail_price"),
        Score.landed_cost,
        Score.margin_eur,
        Score.roi_percent,
        OfferAmazon.bsr,
        OfferAmazon.sellers_count,
        OfferAmazon.buybox_stable
    ).join(
        Score, Score.product_id == Product.id
    ).outerjoin(
        OfferAmazon, and_(
            OfferAmazon.product_id == Product.id,
            OfferAmazon.marketplace == Score.marketplace
        )
    ).outerjoin(
        OfferRetail, OfferRetail.product_id == Product.id
    ).group_by(
        Product.id, Product.asin, Product.title,
        Score.id, Score.marketplace, Score.landed_cost,
        Score.margin_eur, Score.roi_percent,
        OfferAmazon.id, OfferAmazon.price, OfferAmazon.bsr,
        OfferAmazon.sellers_count, OfferAmazon.buybox_stable,
        OfferRetail.id, OfferRetail.price
    )
    
    # Appliquer les filtres
    if roi_min is not None:
        query = query.filter(Score.roi_percent >= roi_min)
    if roi_max is not None:
        query = query.filter(Score.roi_percent <= roi_max)
    if margin_min is not None:
        query = query.filter(Score.margin_eur >= margin_min)
    if margin_max is not None:
        query = query.filter(Score.margin_eur <= margin_max)
    if bsr_max is not None:
        query = query.filter(OfferAmazon.bsr <= bsr_max)
    if sellers_count_max is not None:
        query = query.filter(OfferAmazon.sellers_count <= sellers_count_max)
    if buybox_stable is not None:
        query = query.filter(OfferAmazon.buybox_stable == buybox_stable)
    if marketplace:
        query = query.filter(Score.marketplace == marketplace)
    
    # Compter le total
    total = query.count()
    
    # Pagination
    offset = (page - 1) * page_size
    results = query.offset(offset).limit(page_size).all()
    
    # Formater les résultats
    items = []
    for row in results:
        items.append(SearchItem(
            asin=row.asin,
            title=row.title,
            marketplace=row.marketplace,
            amazon_price=row.amazon_price,
            retail_price=row.retail_price,
            landed_cost=row.landed_cost,
            margin_eur=row.margin_eur,
            roi_percent=float(row.roi_percent) if row.roi_percent else None,
            bsr=row.bsr,
            sellers_count=row.sellers_count,
            buybox_stable=row.buybox_stable
        ))
    
    total_pages = (total + page_size - 1) // page_size
    
    return SearchResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

