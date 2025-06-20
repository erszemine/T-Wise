# src_backend/models_entity/Product.py

from datetime import datetime
from typing import Optional, List, Dict
from beanie import Document, PydanticObjectId # PydanticObjectId eklendi
from pydantic import Field

class Product(Document):
    # MongoDB'deki _id alanı için
    # Beanie bunu otomatik olarak handle eder, ancak ProductResponse gibi yerlerde _id'ye erişmek için kullanılabilir.
    # Doğrudan buraya eklemeye gerek yok, Beanie handle edecektir.

    name: str = Field(description="Ürün/Parça adı")
    code: str = Field(unique=True, index=True, description="Ürün/Parça kodu (benzersiz)")
    description: Optional[str] = Field(None, description="Detaylı açıklama")
    unit: str = Field("Adet", description="Stokta takip edildiği birim (Adet, Metre vb.)")
    category: Optional[str] = Field(None, description="Ürünün ait olduğu kategori")
    
    purchase_price: float = Field(description="Birim satın alma maliyeti") # Optional kaldırıldı, float yapıldı
    # MongoDB belgenizde olan yeni alanlar eklendi:
    sale_price: float = Field(description="Birim satış maliyeti")
    current_stock: int = Field(description="Mevcut stok miktarı")
    minimum_stock: int = Field(description="Minimum stok seviyesi")
    reorder_point: int = Field(description="Yeniden sipariş noktası")
    is_active: bool = Field(description="Ürün aktif mi?") # boolean olarak ayarlandı

    components: Optional[List[Dict]] = Field([], description="Ürünün üretim için gerekli alt parçaları (BOM)")

    # created_at ve updated_at için datetime.utcnow kullanmak, zaman dilimi tutarlılığı sağlar.
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Oluşturulma tarihi")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Son güncelleme tarihi")

    class Settings:
        name = "products" # MongoDB koleksiyon adının "products" olduğundan emin olun
        keep_updated = True # Bu, Beanie'nin updated_at gibi alanları otomatik güncellemesine yardımcı olur
        # Beanie 1.x ve üzeri için varsayılan "_id" alanını otomatik olarak tanır.
        # Bu yüzden `id: PydanticObjectId` gibi bir tanıma gerek yoktur.
        # Ancak ProductResponse şemasında bunu "id" olarak aliaslamak gerekir.