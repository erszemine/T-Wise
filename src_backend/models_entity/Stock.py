from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Stock(Base):
    __tablename__ = "Stock" # Veritabanındaki tablo adı

    id = Column(Integer, primary_key=True, index=True)
    
    product_id = Column(Integer, ForeignKey("Products.id", ondelete="CASCADE"), unique=True, nullable=False) 
    # product_id benzersiz olmalı, her ürün için sadece bir stok kaydı olabilir
    
    amount = Column(Integer, nullable=False, default=0) # Miktar
    critical_stock_level = Column(Integer, nullable=False, default=0) # Kritik stok seviyesi
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now()) # Son güncelleme tarihi

    # İlişki tanımı: Bir stok kaydı bir ürüne aittir.
    # 'back_populates' ile Product modelindeki 'stock_record' ilişkisini belirtiriz.
    product = relationship("Product", back_populates="stock_record")

    def __repr__(self):
        return f"<Stock(id={self.id}, product_id={self.product_id}, amount={self.amount})>"