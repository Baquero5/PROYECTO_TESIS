from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    unit = Column(String(50), default="unidades")
    
    # Stock levels
    stock = Column(Integer, default=0)
    min_stock = Column(Integer, default=0)
    reorder_point = Column(Integer, default=0)
    max_stock = Column(Integer, default=1000)
    
    # Pricing
    cost_price = Column(Float, default=0.0)
    sell_price = Column(Float, default=0.0)
    
    # Metadata
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
