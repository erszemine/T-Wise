# src_backend/api/product_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from beanie import PydanticObjectId
from typing import List, Optional
from datetime import datetime

from ..models_entity.Product import Product  # veritabanı modeli
from ..schemas.product_schemas import ProductCreate, ProductResponse, ProductUpdate, ProductListResponse # Yeni şemalarımızı import ettik
# from security import get_current_user # Eğer kimlik doğrulama eklemek isterseniz bu satırı yorumdan çıkarın

router = APIRouter(prefix="/api/products", tags=["Products"]) # API rotaları için ortak prefix ve tag tanımlandı

@router.get("/", response_model=ProductListResponse, summary="Tüm ürünleri/parçaları listele")
async def get_all_products():
    """
    Sistemdeki tüm ürünleri/parçaları listeler.
    Ürünler bulunamazsa boş bir liste ve toplam sayı 0 döndürür.
    """
    products = await Product.find_all().to_list()
    
    # ProductListResponse şemasına uygun hale getiriyoruz
    product_responses = [ProductResponse.model_validate(p.model_dump(by_alias=True)) for p in products]
    return ProductListResponse(products=product_responses, total_count=len(products))

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, summary="Yeni bir ürün/parça oluştur")
async def create_product(product_data: ProductCreate):
    """
    Sisteme yeni bir ürün veya parça ekler.
    Gerekli alanlar: name, code, unit, category, purchase_price, sale_price,
    current_stock, minimum_stock, reorder_point.
    """
    # Mevcut bir ürün koduyla çakışma olup olmadığını kontrol et
    existing_product = await Product.find_one(Product.code == product_data.code)
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # 409 Conflict çakışma durumları için uygundur
            detail=f"'{product_data.code}' kodlu ürün zaten mevcut."
        )

    # Veritabanı modelini oluştururken sadece ProductCreate şemasından gelen verileri kullanıyoruz
    product = Product(**product_data.model_dump())
    
    # Zaman damgalarını otomatik olarak ekleyelim (created_at ve updated_at)
    now = datetime.utcnow()
    product.created_at = now
    product.updated_at = now
    
    await product.insert() # Ürünü veritabanına kaydet
    return ProductResponse.model_validate(product) # Yanıtı ProductResponse şemasıyla döndürüyoruz

@router.get("/{product_id}", response_model=ProductResponse, summary="Belirli bir ürünü/parçayı ID ile getir")
async def get_product_by_id(product_id: PydanticObjectId):
    """
    Belirtilen ID'ye sahip ürünü/parçayı getirir.
    Ürün bulunamazsa 404 Not Found hatası döndürür.
    """
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    return ProductResponse.model_validate(product)

@router.put("/{product_id}", response_model=ProductResponse, summary="Belirli bir ürünü/parçayı güncelle")
async def update_product(product_id: PydanticObjectId, product_data: ProductUpdate):
    """
    Belirtilen ID'ye sahip ürünü/parçayı günceller.
    Yalnızca sağlanan alanları günceller.
    Ürün bulunamazsa 404 Not Found hatası döndürür.
    """
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    # ProductUpdate şemasından sadece ayarlanmış (gelen) alanları al
    update_data = product_data.model_dump(exclude_unset=True) 
    
    # Eğer kod güncelleniyorsa ve başka bir ürünle çakışıyorsa kontrol et
    if "code" in update_data and update_data["code"] != product.code:
        existing_product = await Product.find_one(Product.code == update_data["code"])
        if existing_product and existing_product.id != product_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"'{update_data['code']}' kodlu başka bir ürün zaten mevcut."
            )

    # Güncellenen alanları ürüne uygula
    for key, value in update_data.items():
        setattr(product, key, value)
    
    product.updated_at = datetime.utcnow() # Güncelleme zamanını güncelleyin

    await product.save() # Ürünü veritabanında kaydet
    return ProductResponse.model_validate(product)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Belirli bir ürünü/parçayı sil")
async def delete_product(product_id: PydanticObjectId):
    """
    Belirtilen ID'ye sahip ürünü/parçayı siler.
    Başarılı olursa 204 No Content yanıtı döner.
    Ürün bulunamazsa 404 Not Found hatası döndürür.
    """
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    await product.delete()
    return # 204 No Content yanıtı için return değeri yok