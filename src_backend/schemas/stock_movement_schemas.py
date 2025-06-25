# src_backend/schemas/stock_movement_schemas.py
from pydantic import BaseModel, Field, BeforeValidator #, ValidationInfo # ValidationInfo kullanılmıyorsa silebilirsiniz
from beanie import PydanticObjectId, Link
from datetime import datetime
from typing import Optional, List, Annotated
import enum # <-- Bu satırı ekleyin

# Gerekli şemaları import ediyoruz
from schemas.product_schemas import ProductResponse
from schemas.user_schemas import UserResponse

# Gerekli Beanie modellerini import ediyoruz
from models_entity.Product import Product
from models_entity.User import User


# --- Dönüştürme Yardımcı Fonksiyonları ---
def convert_product_for_movement_response(v: any) -> ProductResponse:
    if isinstance(v, Link):
        if v.ref:
            return ProductResponse.model_validate(v.ref)
        raise ValueError(f"Product Link does not contain a fetched document: {v}")
    elif isinstance(v, Product):
        return ProductResponse.model_validate(v)
    return v

def convert_user_for_movement_response(v: any) -> UserResponse:
    if isinstance(v, Link):
        if v.ref:
            return UserResponse.model_validate(v.ref)
        raise ValueError(f"User Link does not contain a fetched document: {v}")
    elif isinstance(v, User):
        return UserResponse.model_validate(v)
    return v


# --- StockMovement Şemaları ---
# HATA BURADAYDI: StrEnum (Python 3.11+) veya Enum + str mixin kullanın
class MovementType(str, enum.Enum):
    IN = "Giriş"
    OUT = "Çıkış"
    TRANSFER = "Transfer"
    ADJUSTMENT = "Düzeltme"

class StockMovementCreate(BaseModel):
    product_id: PydanticObjectId
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    quantity: int = Field(gt=0, description="Hareket eden miktar")
    movement_type: MovementType = Field(description="Hareket tipi (in, out, transfer, adjustment)")
    reference_document: Optional[str] = Field(None, description="İlgili belge numarası (örn: sipariş no, irsaliye no)")
    remarks: Optional[str] = Field(None, description="Ek notlar")
    performed_by: UserResponse

    model_config = {
        "json_schema_extra": {
            "example": {
                "product_id": "60c72b2f9f1b2c3d4e5f6a7e",
                "from_location": "Depo A",
                "to_location": "Depo B",
                "quantity": 10,
                "movement_type": "transfer",
                "reference_document": "TRF-2023-001",
                "remarks": "Depo içi transfer",
                "performed_by_id": "60c72b2f9f1b2c3d4e5f6a7d"
            }
        }
    }

class StockMovementResponse(BaseModel):
    id: PydanticObjectId = Field(..., alias="_id", description="Hareket kaydının benzersiz MongoDB ID'si")

    product: Annotated[ProductResponse, BeforeValidator(convert_product_for_movement_response)] = Field(
        ..., description="Harekete konu olan ürünün detayları"
    )

    from_location: Optional[str] = Field(None, description="Stokun geldiği konum")
    to_location: Optional[str] = Field(None, description="Stokun gittiği konum")
    quantity: int = Field(description="Hareket eden miktar")
    movement_type: MovementType = Field(description="Hareket tipi (in, out, transfer, adjustment)")
    # 'movement_date' modeldeki alan adı, 'timestamp' ise yanıt şemasında görmek istediğiniz isim olabilir.
    # Eğer modelde 'movement_date' ise, burayı da 'movement_date' yapın veya 'alias' kullanın.
    timestamp: datetime = Field(..., alias="movement_date", description="Hareketin gerçekleştiği zaman")
    reference_document: Optional[str] = Field(None, description="İlgili belge numarası")
    remarks: Optional[str] = Field(None, description="Ek notlar")

    performed_by: Annotated[UserResponse, BeforeValidator(convert_user_for_movement_response)] = Field(
        ..., description="Hareketi gerçekleştiren kullanıcının detayları"
    )

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
        "json_encoders": {
            PydanticObjectId: str,
            datetime: lambda v: v.isoformat() + "Z"
        },
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "60c72b2f9f1b2c3d4e5f6a7f",
                    "product": {
                        "id": "60c72b2f9f1b2c3d4e5f6a7e",
                        "name": "Örnek Ürün Adı",
                        "code": "CODE001",
                        "description": "Açıklama",
                        "unit": "Adet",
                        "category": "Kategori",
                        "purchase_price": 10.0,
                        "sale_price": 15.0,
                        "current_stock": 100,
                        "minimum_stock": 10,
                        "reorder_point": 20,
                        "is_active": True,
                        "components": [],
                        "created_at": "2023-01-01T10:00:00Z",
                        "updated_at": "2023-01-01T10:00:00Z"
                    },
                    "from_location": "Depo A",
                    "to_location": "Depo B",
                    "quantity": 10,
                    "movement_type": "transfer",
                    "timestamp": "2023-01-26T12:00:00Z",
                    "reference_document": "TRF-2023-001",
                    "remarks": "Depo içi transfer",
                    "performed_by": {
                        "id": "60c72b2f9f1b2c3d4e5f6a7d",
                        "username": "testuser",
                        "first_name": "Test",
                        "last_name": "User",
                        "email": "test@example.com",
                        "position": "Admin",
                        "is_active": True,
                        "created_at": "2023-01-01T09:00:00Z"
                    }
                }
            ]
        }
    }