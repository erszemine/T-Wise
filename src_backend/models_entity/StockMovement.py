'''
from datetime import datetime
from typing import Optional
from beanie import Document, Link # Beanie kütüphanesinden Document ve Link sınıflarını import ediyoruz.
from pydantic import Field # Pydantic kütüphanesinden Field sınıfını import ediyoruz.

# Bu modelin referans verdiği diğer Beanie Document'ları import ediyoruz.
from .product import Product
from .user import User
from .warehouse import Warehouse

class StockMovement(Document):
    """
    Bu sınıf, depodaki her bir stok hareketini (giriş, çıkış, transfer vb.) temsil eder.
    MongoDB'deki 'stock_movements' koleksiyonundaki her bir belgeye karşılık gelir.
    Bu, tüm stok hareketlerinin bir kaydını tutmamızı sağlar.
    """
    # product: Link[Product] -> Hareketi yapılan ürüne bir referans.
    product: Link[Product] 
    
    # movement_type: str = Field(pattern="^(ENTRY|EXIT|TRANSFER|INVENTORY_ADJUSTMENT)$") -> Hareketin türü.
    # pattern: Belirli bir regex desenine uyması gerektiğini belirtir.
    # Bu, 'movement_type' alanının sadece 'ENTRY', 'EXIT', 'TRANSFER' veya 'INVENTORY_ADJUSTMENT' değerlerinden birini almasını sağlar.
    movement_type: str = Field(pattern="^(ENTRY|EXIT|TRANSFER|INVENTORY_ADJUSTMENT)$") 
    
    # quantity: int = Field(gt=0) -> Hareket gören miktar.
    # gt=0: Değerin 0'dan büyük (greater than) olması gerektiğini belirtir, yani miktar pozitif olmalı.
    quantity: int = Field(gt=0) 
    
    # movement_date: datetime = Field(default_factory=datetime.now) -> Hareketin gerçekleştiği tarih ve saat.
    # default_factory=datetime.now: Yeni bir hareket kaydı oluşturulduğunda otomatik olarak mevcut tarih ve saat atanır.
    movement_date: datetime = Field(default_factory=datetime.now) 
    
    # user: Optional[Link[User]] = None -> Hareketi yapan kullanıcıya referans.
    # Optional[...]: Bu alanın null (None) olabileceğini belirtir.
    # None: Varsayılan değeri None'dur. Yani hareket yapan kullanıcı bilinmeyebilir veya sistem tarafından yapılmış olabilir.
    user: Optional[Link[User]] = None 

    # source_warehouse: Optional[Link[Warehouse]] = None -> Hareketin başladığı depo (örneğin transfer veya çıkış için).
    # Optional: Bu alan isteğe bağlıdır.
    source_warehouse: Optional[Link[Warehouse]] = None
    
    # destination_warehouse: Optional[Link[Warehouse]] = None -> Hareketin bittiği depo (örneğin transfer veya giriş için).
    # Optional: Bu alan isteğe bağlıdır.
    destination_warehouse: Optional[Link[Warehouse]] = None
    
    # description: Optional[str] = None -> Hareketle ilgili ek açıklama veya not.
    # Optional: Bu alan isteğe bağlıdır.
    description: Optional[str] = None 

    class Settings:
        """
        Beanie Document'ın MongoDB ile nasıl eşleşeceğini ve davranacağını belirleyen ayarlar.
        """
        name = "stock_movements" # Bu Document'ın MongoDB'deki koleksiyon adı 'stock_movements' olacaktır.

    def __repr__(self):
        """
        Geliştiriciler için bu objenin string temsilini döndürür.
        """
        return (
            f"<StockMovement(id={self.id}, product_id={self.product.id}, "
            f"type='{self.movement_type}', quantity={self.quantity})>"
        )

    def __str__(self):
        """
        Son kullanıcıya gösterilebilecek veya okunabilir bir string temsilini döndürür.
        """
        return (
            f"Movement of {self.quantity} units of {self.product.name} ({self.movement_type}) "
            f"on {self.movement_date.strftime('%Y-%m-%d %H:%M')}"
        )
    '''

# src_backend/models_entity/StockMovement.py
from datetime import datetime
from typing import Optional
from beanie import Document, Link
from pydantic import Field
from .Product import Product
from .User import User

class StockMovement(Document):
    product: Link[Product] = Field(description="Hareketi yapılan ürün/parça")
    movement_type: str = Field(description="Hareketin tipi (Giriş, Çıkış, İade, Düzeltme vb.)")
    quantity: int = Field(description="Hareketin miktarı (giriş için pozitif, çıkış için negatif)")
    reference_document: Optional[str] = Field(None, description="Hareketi tetikleyen belge/referans numarası")
    performed_by: Link[User] = Field(description="Hareketi gerçekleştiren kullanıcı")

    movement_date: datetime = Field(default_factory=datetime.now, description="Hareketin gerçekleştiği tarih ve saat")

    class Settings:
        name = "stock_movements"
        indexes = [
          '''  "product",
            "movement_date",
            "movement_type",
            "performed_by", '''
        ]