# src_backend/api/product_routes.py
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime
from pydantic import BaseModel, Field

from models_entity.Product import Product
from models_entity.User import User
from security import role_required, get_current_user

router = APIRouter()

# Pydantic Request/Response Modelleri
class ProductCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    unit: str = "Adet"
    category: Optional[str] = None
    purchase_price: Optional[float] = None

class ProductResponse(Product):
    id: str = Field(alias="_id") # MongoDB'deki _id'yi id olarak gösterir
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, summary="Yeni bir ürün/parça oluştur")
async def create_product(product_data: ProductCreate, current_user: User = Depends(role_required(["Yönetici", "Depo Sorumlusu"]))):
    new_product = Product(**product_data.dict())
    try:
        await new_product.insert()
        return ProductResponse.parse_obj(new_product.dict())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ürün oluşturulamadı: {e}")

@router.get("/", response_model=List[ProductResponse], summary="Tüm ürünleri/parçaları listele")
async def get_products(current_user: User = Depends(get_current_user)):
    products = await Product.find_all().to_list()
    return [ProductResponse.parse_obj(p.dict()) for p in products]

@router.get("/{product_id}", response_model=ProductResponse, summary="Belirli bir ürünü/parçayı ID ile getir")
async def get_product_by_id(product_id: str, current_user: User = Depends(get_current_user)):
    try:
        product = await Product.get(ObjectId(product_id))
        if product:
            return ProductResponse.parse_obj(product.dict())
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ürün bulunamadı")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Geçersiz ID veya hata: {e}")

@router.put("/{product_id}", response_model=ProductResponse, summary="Bir ürünü/parçayı ID ile güncelle")
async def update_product(product_id: str, product_update: ProductCreate, current_user: User = Depends(role_required(["Yönetici", "Depo Sorumlusu"]))):
    try:
        product = await Product.get(ObjectId(product_id))
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Güncellenecek ürün bulunamadı")

        update_data = product_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        product.updated_at = datetime.now()
        await product.save()
        return ProductResponse.parse_obj(product.dict())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Güncelleme hatası: {e}")

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Bir ürünü/parçayı ID ile sil")
async def delete_product(product_id: str, current_user: User = Depends(role_required(["Yönetici"]))):
    try:
        product = await Product.get(ObjectId(product_id))
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Silinecek ürün bulunamadı")

        await product.delete()
        return # 204 No Content yanıtı için boş döner
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Silme hatası: {e}")