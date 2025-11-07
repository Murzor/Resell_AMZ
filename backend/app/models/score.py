from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Score(Base):
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    marketplace = Column(String, nullable=False, index=True)
    landed_cost = Column(Numeric(10, 2))
    margin_eur = Column(Numeric(10, 2))
    roi_percent = Column(Numeric(5, 2))
    best_retail_offer_id = Column(Integer, ForeignKey("offers_retail.id"))
    best_amazon_offer_id = Column(Integer, ForeignKey("offers_amz.id"))
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    product = relationship("Product", backref="scores")
    best_retail_offer = relationship("OfferRetail", foreign_keys=[best_retail_offer_id])
    best_amazon_offer = relationship("OfferAmazon", foreign_keys=[best_amazon_offer_id])

