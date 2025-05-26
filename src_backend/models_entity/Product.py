from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship # İlişkileri tanımlamak için
from ..database import Base

class Product(Base):
    __tablename__ = "Products" # Veritabanındaki tablo adı

    id = Column(Integer, primary_key=True, index=True) # urunID -> id
    product_name = Column(String(255), nullable=False) 
    code = Column(String(50), unique=True, index=True, nullable=False) 
    product_information = Column(Text, nullable=True) 
    barcode = Column(String(50), unique=True, nullable=True) 

    # İlişki tanımı: Bir ürünün birden fazla stok hareketi olabilir.
    # Bu, 'StokHareketleri' tablosundaki 'product_id' sütununa otomatik olarak bağlanacaktır.
    stock_movements = relationship("StockMovement", back_populates="product", cascade="all, delete-orphan")
    
    # Stok ile birebir ilişki: Bir ürünün bir stok kaydı olabilir.
    stock_record = relationship("Stock", back_populates="product", uselist=False, cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Product(id={self.id}, product_name='{self.product_name}', code='{self.code}')>"