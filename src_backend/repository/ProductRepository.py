# src_backend/repository/ProductRepository.py

from typing import List, Optional
from beanie import PydanticObjectId # ID tipi için
from models_entity.Product import Product # Product modelimizi import ediyoruz

class ProductRepository:
    def __init__(self):
        # Repository'nin başlangıçta özel bir şeye ihtiyacı yok,
        # metodlar doğrudan Product.find(), Product.insert() gibi Beanie metodlarını kullanacak.
        pass

    async def create_product(self, product: Product) -> Product:
        """
        Yeni bir ürünü veritabanına kaydeder.
        """
        await product.insert()
        return product

    async def get_all_products(self) -> List[Product]:
        """
        Veritabanındaki tüm ürünleri döner.
        """
        return await Product.find_all().to_list()

    async def get_product_by_id(self, product_id: PydanticObjectId) -> Optional[Product]:
        """
        Belirli bir ID'ye sahip ürünü veritabanından çeker.
        """
        return await Product.get(product_id)

    async def get_product_by_code(self, code: str) -> Optional[Product]:
        """
        Belirli bir koda sahip ürünü veritabanından çeker.
        Code alanı benzersiz olduğu için tek bir sonuç beklenir.
        """
        return await Product.find_one(Product.code == code)

    async def update_product(self, product_id: PydanticObjectId, update_data: dict) -> Optional[Product]:
        """
        Belirli bir ID'ye sahip ürünü günceller.
        update_data: Güncellenecek alanları ve değerlerini içeren bir dictionary.
        """
        product = await Product.get(product_id)
        if product:
            # Pydantic modelin update metodunu kullanarak veriyi günceller
            # exclude_unset=True ile sadece belirtilen alanları güncelleriz
            # update_data'nın Pydantic modeline uygun olması gerekir.
            # Örneğin, update_data = {"name": "Yeni Ad", "price": 100.0}
            for key, value in update_data.items():
                setattr(product, key, value)
            await product.save() # Veritabanına kaydet
            return product
        return None

    async def delete_product(self, product_id: PydanticObjectId) -> bool:
        """
        Belirli bir ID'ye sahip ürünü veritabanından siler.
        """
        product = await Product.get(product_id)
        if product:
            await product.delete()
            return True
        return False