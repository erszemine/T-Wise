from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class StockMovement(Base):
    __tablename__ = "StockMovements" # Veritabanındaki tablo adı

    id = Column(Integer, primary_key=True, index=True)
    
    product_id = Column(Integer, ForeignKey("Products.id", ondelete="CASCADE"), nullable=False) # urunID -> product_id (Foreign Key)
    movement_type = Column(String(20), nullable=False) # hareketTipi (e.g., 'ENTRY', 'EXIT', 'TRANSFER')
    amount = Column(Integer, nullable=False) # miktar
    movement_date = Column(DateTime, default=func.now()) # tarih
    
    user_id = Column(Integer, ForeignKey("Users.id", ondelete="SET NULL"), nullable=True) # kullanici -> user_id (Foreign Key)
    explanation = Column(Text, nullable=True) # Açıklama
    

    # İlişki tanımları:
    # 'product' ilişkisi, StockMovement objesinden ilgili Product objesine erişmeyi sağlar.
    # 'back_populates' ile Product modelindeki 'stock_movements' ilişkisini belirtiriz.
    product = relationship("Product", back_populates="stock_movements")
    
    # 'user' ilişkisi, StockMovement objesinden ilgili User objesine erişmeyi sağlar.
    # 'back_populates' ile User modelindeki (eğer User'da tanımlanmışsa) 'stock_movements' ilişkisini belirtiriz.
    user = relationship("User", back_populates="stock_movements")

    def __repr__(self):
        return f"<StockMovement(id={self.id}, product_id={self.product_id}, movement_type='{self.movement_type}', amount={self.amount})>"