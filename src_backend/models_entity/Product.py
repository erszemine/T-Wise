from datetime import datetime
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
        name = "products" # MongoDB koleksiyon adı