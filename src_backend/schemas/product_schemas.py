# src_backend/schemas/product_schemas.py
from beanie import PydanticObjectId
from pydantic import BaseModel, Field
from typing import Optional, List # components için Dict gerekebilir, import edin
from datetime import datetime

# components için Dict import edildiğinden emin olun
from typing import Dict # Bunu da ProductBase'e eklemişsiniz ama tekrar emin olalım

# --- YENİ BİR TEMEL ŞEMA: ProductCreateUpdateBase ---
# Bu şema, hem oluşturma hem de güncelleme için ortak alanları içerir.
# Otomatik atanan alanları (id, created_at, updated_at) içermez.
class ProductCreateUpdateBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Ürünün veya parçanın adı.")
    code: str = Field(..., min_length=2, max_length=50, description="Ürünün veya parçanın benzersiz kodu.")
    description: Optional[str] = Field(None, max_length=500, description="Ürünün kısa açıklaması.")
    unit: str = Field(..., description="Ürünün birimi (örn: Adet, Koli, Litre).")
    category: str = Field(..., description="Ürünün ait olduğu kategori (örn: Motor Parçaları, Fren Sistemi).")
    purchase_price: float = Field(..., gt=0, description="Ürünün alış fiyatı.")
    sale_price: float = Field(..., gt=0, description="Ürünün satış fiyatı.")
    current_stock: int = Field(..., ge=0, description="Mevcut stok miktarı.")
    minimum_stock: int = Field(..., ge=0, description="Asgari stok seviyesi, altına düşüldüğünde uyarı verilir.")
    reorder_point: int = Field(..., ge=0, description="Yeniden sipariş noktası.")
    is_active: bool = Field(True, description="Ürünün aktif olup olmadığı.")
    components: Optional[List[Dict]] = Field([], description="Ürünün üretim için gerekli alt parçaları (BOM)") # Burası Product modelinizle uyumlu olmalı

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ön Fren Balatası",
                "code": "FREN-BALATA-001",
                "description": "Yüksek performanslı seramik ön fren balatası.",
                "unit": "Takım",
                "category": "Fren Sistemi",
                "purchase_price": 300.00,
                "sale_price": 450.00,
                "current_stock": 50,
                "minimum_stock": 10,
                "reorder_point": 15,
                "is_active": True,
                "components": []
            }
        }

# Product creation schema - Yeni ürün oluşturulurken kullanılır
class ProductCreate(ProductCreateUpdateBase):
    # Oluşturma sırasında tüm alanlar zorunlu olmalıdır (Base'den gelir)
    pass

# Product update schema - Ürün güncellenirken kullanılır
class ProductUpdate(ProductCreateUpdateBase):
    # Güncellemede tüm alanlar opsiyonel olabilir
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    purchase_price: Optional[float] = None
    sale_price: Optional[float] = None
    current_stock: Optional[int] = None
    minimum_stock: Optional[int] = None
    reorder_point: Optional[int] = None
    is_active: Optional[bool] = None
    components: Optional[List[Dict]] = None # Güncelleme sırasında da opsiyonel olabilir


# --- API Yanıt Şeması: ProductResponse ---
# Bu şema, API'den dönecek verilerin yapısını tanımlar.
# MongoDB'deki _id ve otomatik zaman damgalarını içerir.
class ProductResponse(BaseModel):
    id: PydanticObjectId = Field(alias="_id", description="Ürünün veritabanı kimliği.") # PydanticObjectId olmalı
    name: str
    code: str
    description: Optional[str] = None
    unit: str
    category: Optional[str] = None
    purchase_price: float
    sale_price: float
    current_stock: int
    minimum_stock: int
    reorder_point: int
    is_active: bool
    components: Optional[List[Dict]] = None # Product modelinizle uyumlu olmalı

    created_at: datetime = Field(description="Ürünün oluşturulma tarihi ve saati.")
    updated_at: datetime = Field(description="Ürünün son güncellenme tarihi ve saati.")

    class Config:
        populate_by_name = True # _id alanını id olarak kullanmamızı sağlar
        json_encoders = {
            PydanticObjectId: str, # ObjectId'yi string'e çevirir
            datetime: lambda v: v.isoformat() + "Z" # datetime objesini ISO formatına çevirir ve Z (UTC) ekler
        }
        arbitrary_types_allowed = True # PydanticObjectId için gerekli


# API response for a list of products
class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total_count: int

    class Config:
        pass # Config: pass bırakılabilir veya ek ayarlamalar yapılabilir