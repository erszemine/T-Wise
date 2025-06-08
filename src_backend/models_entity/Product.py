'''from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field

class Product(Document):
    name: str # Ürün adı
    code: str = Field(unique=True, index=True) # Ürün kodu benzersiz ve indeksli olsun
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "products" # MongoDB koleksiyon adı '''

# src_backend/models_entity/Product.py
from datetime import datetime
from typing import Optional, List, Dict # List ve Dict eklendi
from beanie import Document
from pydantic import Field

class Product(Document):
    name: str = Field(description="Ürün/Parça adı")
    code: str = Field(unique=True, index=True, description="Ürün/Parça kodu (benzersiz)")
    description: Optional[str] = Field(None, description="Detaylı açıklama")
    unit: str = Field("Adet", description="Stokta takip edildiği birim (Adet, Metre vb.)")
    category: Optional[str] = Field(None, description="Ürünün ait olduğu kategori")
    purchase_price: Optional[float] = Field(None, description="Birim satın alma maliyeti")
    # Aşağıdaki satırda List ve Dict kullanıldığı için import etmeniz gerekiyor
    components: Optional[List[Dict]] = Field([], description="Ürünün üretim için gerekli alt parçaları (BOM)")


    created_at: datetime = Field(default_factory=datetime.now, description="Oluşturulma tarihi")
    updated_at: datetime = Field(default_factory=datetime.now, description="Son güncelleme tarihi")

    class Settings:
        name = "products"