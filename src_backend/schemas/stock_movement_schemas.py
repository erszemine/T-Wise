# src/stok_yonetim_backend/schemas/stock_movement_schemas.py
from pydantic import BaseModel, Field
from beanie import PydanticObjectId
from datetime import datetime
from typing import Optional

class StockMovementResponse(BaseModel):
    id: PydanticObjectId = Field(..., alias="_id", description="Stok hareketinin MongoDB ID'si")
    product_id: PydanticObjectId = Field(description="Hareketi yapılan ürünün ID'si")
    user_id: Optional[PydanticObjectId] = Field(None, description="Hareketi yapan kullanıcının ID'si (isteğe bağlı)")
    
    quantity: int = Field(description="Hareket eden stok miktarı")
    movement_type: str = Field(pattern="^(IN|OUT|ADJUSTMENT)$", description="Stok hareketi tipi (IN, OUT, ADJUSTMENT)") # TRANSFER kaldırıldı
    timestamp: datetime = Field(description="Stok hareketinin gerçekleştiği tarih ve saat")
    notes: Optional[str] = Field(None, description="Stok hareketiyle ilgili notlar")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "60c72b2f9f1b2c3d4e5f6a7d",
                    "product_id": "60c72b2f9f1b2c3d4e5f6a7b",
                    "user_id": "60c72b2f9f1b2c3d4e5f6a7c",
                    "quantity": 50,
                    "movement_type": "IN",
                    "timestamp": "2023-01-06T10:00:00.000Z",
                    "notes": "Tedarikçiden yeni ürün girişi."
                }
            ]
        }
    }