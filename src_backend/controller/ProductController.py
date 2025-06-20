# src_backend/controller/ProductController.py

from typing import List, Optional
from beanie import PydanticObjectId
from repository.ProductRepository import ProductRepository
from models_entity.Product import Product # Product modelini import ediyoruz

# DTO (Data Transfer Object) olarak kullanılacak Pydantic modelleri
# API katmanından gelen verinin doğruluğunu kontrol etmek için kullanacağız.
# Henüz oluşturmadıysak, geçici olarak Product modelini kullanabiliriz
# veya ayrı bir dosya (örneğin schema/product_schema.py) oluşturabiliriz.
# Şimdilik Product modelini doğrudan kullanalım, daha sonra DTO'lara ayırabiliriz.

class ProductController:
    def __init__(self, product_repository: ProductRepository = None):
        # Eğer dışarıdan bir repository objesi verilmezse, yeni bir tane oluştururuz.
        # Bu, bağımlılık enjeksiyonu (dependency injection) için esneklik sağlar.
        self.product_repository = product_repository if product_repository else ProductRepository()

    async def create_new_product(self, product_data: Product) -> Optional[Product]:
        """
        Yeni bir ürün oluşturma iş mantığını içerir.
        Gelen product_data, Product modeline uygun olmalıdır.
        """
        # Burada ekstra iş mantığı veya validasyon eklenebilir
        # Örneğin: product_data.code zaten var mı kontrolü (repository'de de yapabiliriz)
        existing_product = await self.product_repository.get_product_by_code(product_data.code)
        if existing_product:
            # Hata döndürmek için bir mekanizma eklemeliyiz (örn: HTTPException)
            # Şimdilik None döndürelim, API katmanı bunu yakalar.
            print(f"Hata: {product_data.code} kodlu ürün zaten mevcut.")
            return None # Frontend'e veya API katmanına bir hata mesajı ile dönülecek

        new_product = await self.product_repository.create_product(product_data)
        return new_product

    async def get_all_products(self) -> List[Product]:
        """
        Tüm ürünleri listeler.
        """
        products = await self.product_repository.get_all_products()
        return products

    async def get_product_details_by_id(self, product_id: PydanticObjectId) -> Optional[Product]:
        """
        Belirli bir ID'ye sahip ürünün detaylarını çeker.
        """
        product = await self.product_repository.get_product_by_id(product_id)
        return product

    async def get_product_details_by_code(self, code: str) -> Optional[Product]:
        """
        Belirli bir koda sahip ürünün detaylarını çeker.
        """
        product = await self.product_repository.get_product_by_code(code)
        return product

    async def update_existing_product(self, product_id: PydanticObjectId, update_data: dict) -> Optional[Product]:
        """
        Mevcut bir ürünü günceller.
        """
        # Burada update_data'nın geçerliliği veya iş mantığı kontrolleri yapılabilir.
        updated_product = await self.product_repository.update_product(product_id, update_data)
        return updated_product

    async def delete_existing_product(self, product_id: PydanticObjectId) -> bool:
        """
        Belirli bir ürünü siler.
        """
        # Silme öncesi bağımlılık kontrolleri gibi iş mantığı eklenebilir.
        result = await self.product_repository.delete_product(product_id)
        return result
    