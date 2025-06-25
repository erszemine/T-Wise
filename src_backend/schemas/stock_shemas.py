# src_backend/schemas/stock_schemas.py

from pydantic import BaseModel, Field, BeforeValidator # BeforeValidator'ı import ediyoruz
from beanie import PydanticObjectId # Sadece PydanticObjectId import ediyoruz
from datetime import datetime
from typing import Optional, List, Annotated # Annotated'ı import ediyoruz

# ProductResponse şemamızı import ediyoruz
from schemas.product_schemas import ProductResponse # BU SATIR ÇOK ÖNEMLİ!
# Beanie Product modelini de import etmeliyiz, çünkü BeforeValidator onu işleyecek.
from models_entity.Product import Product # BU SATIR DA ÇOK ÖNEMLİ!


# Yardımcı bir dönüştürme fonksiyonu
# Bu fonksiyon, bir Product Beanie Document'ı (veya benzer bir objeyi) alır ve
# ProductResponse Pydantic modeline dönüştürür.
# Pydantic'in `from_attributes=True` ile otomatik yapamadığı durumda devreye girer.
def convert_product_to_response(v: any) -> ProductResponse:
    if isinstance(v, Product):
        return ProductResponse.model_validate(v)
    # Eğer gelen değer zaten uygun bir dict veya ProductResponse örneği ise, Pydantic kendi başına işleyebilir.
    # Ancak burada asıl amacımız Beanie Product objesini yakalamak ve dönüştürmek.
    # Eğer buraya farklı bir tip gelirse ve ProductResponse'a dönüşemezse, Pydantic hata verir.
    # Dolayısıyla, buraya genellikle bir Beanie Product objesi gelecektir.
    return v # Diğer durumlar için Pydantic'in kendi validasyonuna bırakırız.


# Stock oluşturmak için kullanılacak istek şeması (Aynı kalır)
class StockCreate(BaseModel):
    product_id: PydanticObjectId = Field(..., description="Stok kaydının ait olduğu ürünün ID'si")
    location: str = Field(..., description="Depodaki fiziksel konum")
    current_quantity: int = Field(default=0, description="Depoda şu anki mevcut miktar")
    reserved_quantity: int = Field(default=0, description="Üretim için rezerve edilmiş miktar")
    incoming_quantity: int = Field(default=0, description="Sipariş edilmiş, henüz gelmemiş miktar")
    min_level: int = Field(default=0, description="Minimum stok seviyesi")
    max_level: int = Field(default=99999, description="Maksimum stok seviyesi")
    serial_numbers: Optional[List[str]] = Field([], description="Seri numarası ile takip edilenler için listesi")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": "60c72b2f9f1b2c3d4e5f6a7e",
                    "location": "A-Raf-1",
                    "current_quantity": 150,
                    "reserved_quantity": 10,
                    "incoming_quantity": 50,
                    "min_level": 20,
                    "max_level": 500,
                    "serial_numbers": ["SN001", "SN002"]
                }
            ]
        }
    }

# Stock güncellemek için kullanılacak istek şeması (Aynı kalır)
class StockUpdate(BaseModel):
    product_id: Optional[PydanticObjectId] = Field(None, description="Stok kaydının ait olduğu ürünün ID'si")
    location: Optional[str] = Field(None, description="Depodaki fiziksel konum")
    current_quantity: Optional[int] = Field(None, description="Depoda şu anki mevcut miktar")
    reserved_quantity: Optional[int] = Field(None, description="Üretim için rezerve edilmiş miktar")
    incoming_quantity: Optional[int] = Field(None, description="Sipariş edilmiş, henüz gelmemiş miktar")
    min_level: Optional[int] = Field(None, description="Minimum stok seviyesi")
    max_level: Optional[int] = Field(None, description="Maksimum stok seviyesi")
    serial_numbers: Optional[List[str]] = Field(None, description="Seri numarası ile takip edilenler için listesi")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "current_quantity": 160,
                    "reserved_quantity": 15
                }
            ]
        }
    }


# Stock yanıtı için kullanılacak şema
class StockResponse(BaseModel):
    id: PydanticObjectId = Field(..., alias="_id", description="Stok kaydının benzersiz MongoDB ID'si")

    # product alanına BeforeValidator ekliyoruz.
    # Bu, 'stock.product' (Beanie Product objesi) alındığında,
    # convert_product_to_response fonksiyonu ile ProductResponse'a dönüştürülmesini sağlayacaktır.
    product: Annotated[ProductResponse, BeforeValidator(convert_product_to_response)] = Field(
        ..., description="Stok kaydının ait olduğu ürünün detayları"
    )

    location: str
    current_quantity: int
    reserved_quantity: int
    incoming_quantity: int
    min_level: int
    max_level: int

    last_in_date: Optional[datetime] = None
    last_out_date: Optional[datetime] = None
    serial_numbers: Optional[List[str]] = []

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "from_attributes": True, # Bu, Beanie objesindeki alanların Pydantic modelindeki alanlara eşleşmesine yardımcı olur.
        "json_schema_extra": {
            "examples": [
                {
                    "id": "60c72b2f9f1b2c3d4e5f6a7d",
                    "product": { # ProductResponse örneği
                        "id": "60c72b2f9f1b2c3d4e5f6a7e",
                        "name": "Örnek Ürün Adı",
                        "description": "Örnek Ürün Açıklaması",
                        "sku": "SKU001",
                        "price": 99.99,
                        "created_at": "2023-01-01T10:00:00Z",
                        "updated_at": "2023-01-01T10:00:00Z"
                    },
                    "location": "A-Raf-1",
                    "current_quantity": 150,
                    "reserved_quantity": 10,
                    "incoming_quantity": 50,
                    "min_level": 20,
                    "max_level": 500,
                    "last_in_date": "2023-01-15T10:00:00Z",
                    "last_out_date": "2023-01-20T14:00:00Z",
                    "serial_numbers": ["SN001", "SN002"],
                    "created_at": "2023-01-01T10:00:00Z",
                    "updated_at": "2023-01-25T16:00:00Z"
                }
            ]
        }
    }