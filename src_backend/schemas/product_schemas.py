# src_backend/schemas/product_schemas.py
from beanie import PydanticObjectId 
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Base Product Schema - Diğer şemalar için temel sağlar
class ProductBase(BaseModel):
    id: str = Field(..., alias="_id", description="Ürünün veritabanı kimliği.")
    created_at: datetime = Field(..., description="Ürünün oluşturulma tarihi ve saati.")
    updated_at: datetime = Field(..., description="Ürünün son güncellenme tarihi ve saati.")
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

    class Config:
        populate_by_name = True
        json_encoders = {
            PydanticObjectId: str, # ObjectId'yi string'e çevirir
            datetime: lambda v: v.isoformat() + "Z" # datetime objesini ISO formatına çevirir ve Z (UTC) ekler
        }

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
                "is_active": True
            }
        }

# Product creation schema - Yeni ürün oluşturulurken kullanılır
class ProductCreate(ProductBase):
    pass # ProductBase'deki tüm alanlar yeterlidir

# Product update schema - Ürün güncellenirken kullanılır
class ProductUpdate(ProductBase):
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

# Product response schema - API yanıtlarında kullanılır (veritabanı kimliği ve zaman damgaları dahil)
class ProductResponse(ProductBase):
    id: str = Field(..., alias="_id", description="Ürünün veritabanı kimliği.")
    created_at: datetime = Field(..., description="Ürünün oluşturulma tarihi ve saati.")
    updated_at: datetime = Field(..., description="Ürünün son güncellenme tarihi ve saati.")

    class Config:
        populate_by_name = True # _id alanını id olarak kullanmamızı sağlar
        json_schema_extra = {
            "example": {
                "id": "60c72b2f9f1b2c3d4e5f6a7b", # Örnek ObjectId
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
                "created_at": "2023-01-15T10:30:00.000Z",
                "updated_at": "2023-01-15T10:30:00.000Z"
            }
        }

# API response for a list of products
class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "products": [
                    {
                        "id": "60c72b2f9f1b2c3d4e5f6a7b",
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
                        "created_at": "2023-01-15T10:30:00.000Z",
                        "updated_at": "2023-01-15T10:30:00.000Z"
                    }
                ],
                "total_count": 1
            }
        }