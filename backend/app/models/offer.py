from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class OfferAmazon(Base):
    __tablename__ = "offers_amz"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    marketplace = Column(String, nullable=False, index=True)  # FR, DE, IT, ES, etc.
    price = Column(Numeric(10, 2), nullable=False)
    shipping_cost = Column(Numeric(10, 2), default=0)
    fba_fee = Column(Numeric(10, 2))
    referral_fee = Column(Numeric(10, 2))
    sellers_count = Column(Integer, default=0)
    buybox_stable = Column(Boolean, default=False)
    bsr = Column(Integer)  # Best Seller Rank
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    product = relationship("Product", backref="amazon_offers")


class OfferRetail(Base):
    __tablename__ = "offers_retail"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    shipping_cost = Column(Numeric(10, 2), default=0)
    availability = Column(Boolean, default=True)
    url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    product = relationship("Product", backref="retail_offers")
    store = relationship("Store", backref="offers")

