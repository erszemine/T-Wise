
# src_backend/models_entity/Stock.py
from datetime import datetime
from typing import Optional, List
from beanie import Document, Link
from pydantic import Field
from .Product import Product # Product modelini import edin

class Stock(Document):
    product: Link[Product] = Field(description="Hangi ürüne/parçaya ait stok bilgisi")
    location: str = Field(description="Depodaki fiziksel konum")
    current_quantity: int = Field(default=0, description="Depoda şu anki mevcut miktar")
    reserved_quantity: int = Field(default=0, description="Üretim için rezerve edilmiş miktar")
    incoming_quantity: int = Field(default=0, description="Sipariş edilmiş, henüz gelmemiş miktar")
    min_level: int = Field(default=0, description="Minimum stok seviyesi")
    max_level: int = Field(default=99999, description="Maksimum stok seviyesi")

    last_in_date: Optional[datetime] = Field(None, description="Son girişin tarihi ve saati")
    last_out_date: Optional[datetime] = Field(None, description="Son çıkışın tarihi ve saati")
    serial_numbers: Optional[List[str]] = Field([], description="Seri numarası ile takip edilenler için listesi")

    class Settings:
        name = "stocks"
        indexes = [
            #"product", # Tekil alan indeksi
            #(
                #[("location", 1), ("product", 1)],  # Bileşik indeks anahtarları: (alan adı, sıralama yönü)
                #{"unique": True} # Bileşik indeks için seçenekler (benzersizlik)
            #),
        ]

    # model_config'i ekleyin
    model_config = {
        "from_attributes": True
    }