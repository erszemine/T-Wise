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

    # Zaman dilimi tutarlılığı için utcnow kullanın
    movement_date: datetime = Field(default_factory=datetime.utcnow, description="Hareketin gerçekleştiği tarih ve saat")

    class Settings:
        name = "stock_movements"
        # Index tanımlarını doğru formatta verin
        indexes = [
            #"product",
            #"movement_date",
            #"movement_type",
            #"performed_by",
        ]

    # model_config, Settings sınıfının dışında olmalıdır.
    model_config = {
        "from_attributes": True
    }