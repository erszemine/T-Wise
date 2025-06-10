# src_backend/api/product_routes.py

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from beanie import PydanticObjectId # Değişiklik: ObjectId yerine PydanticObjectId
from datetime import datetime
from pydantic import BaseModel, Field

# Controller'ı import ediyoruz
from controller.ProductController import ProductController
# Modelimizi import ediyoruz (Response modelleri için hala gerekli)
from models_entity.Product import Product

# Kullanıcı ve yetkilendirme (henüz geliştirilmedi ama yapıya uygun)
from models_entity.User import User # Kullanıcı modeliniz için
from security import role_required, get_current_user # security.py'deki fonksiyonlarınız için

router = APIRouter()

# Controller örneğini oluşturuyoruz.
# FastAPI'nin Dependency Injection sistemini kullanarak da enjekte edebiliriz,
# ancak şimdilik basit tutalım ve burada bir örnek oluşturalım.
product_controller = ProductController()

# Pydantic Request/Response Modelleri (Product modeli ile uyumlu)
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=50, description="Benzersiz ürün kodu")
    description: Optional[str] = Field(None, max_length=500)
    unit: str = Field("Adet", min_length=1, max_length=20)
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    purchase_price: Optional[float] = Field(None, gt=0, description="Satın alma maliyeti (pozitif olmalı)")
    # components: Optional[List[Dict]] = Field([], description="Ürünün üretim için gerekli alt parçaları (BOM)")
    # Not: components karmaşık bir yapıda olduğu için Product modelinde olduğu gibi bırakalım
    # ProductCreate'de de bu alanı dahil etmek isterseniz, Product modelindeki tanımına benzer şekilde eklemelisiniz.

class ProductUpdate(BaseModel): # Güncelleme için ayrı bir model, tüm alanlar opsiyonel
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=50, description="Benzersiz ürün kodu")
    description: Optional[str] = Field(None, max_length=500)
    unit: Optional[str] = Field(None, min_length=1, max_length=20)
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    purchase_price: Optional[float] = Field(None, gt=0, description="Satın alma maliyeti (pozitif olmalı)")

class ProductResponse(BaseModel): # Product modelindeki tüm alanları yansıtmak için
    # Product modelinden direkt miras almak yerine, alanlarını tanımlayabiliriz
    # veya Product modelini Pydantic model olarak doğrudan kullanabiliriz
    # ama _id dönüşümünü sağlamak için bu yapıyı koruyalım.
    id: PydanticObjectId = Field(alias="_id") # MongoDB'deki _id'yi id olarak gösterir
    name: str
    code: str
    description: Optional[str] = None
    unit: str
    category: Optional[str] = None
    purchase_price: Optional[float] = None
    components: Optional[List[dict]] = None # Product modelinizdeki gibi Dict veya List[Dict] olmalı
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True # alias'ı kullanmak için
        json_encoders = {
            PydanticObjectId: str, # PydanticObjectId'i string'e çevirir
            datetime: lambda dt: dt.isoformat() # Tarihleri ISO formatına çevirir
        }


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, summary="Yeni bir ürün/parça oluştur")
async def create_product_route(
    product_data: ProductCreate,
    current_user: User = Depends(role_required(["Yönetici", "Depo Sorumlusu"])) # Yetkilendirme şimdilik kalsın
):
    # Gelen ProductCreate modelini Product modeline dönüştürüyoruz
    product_model = Product(**product_data.dict())
    
    new_product = await product_controller.create_new_product(product_model)
    
    if new_product is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ürün oluşturulamadı. Kod '{product_data.code}' zaten mevcut olabilir.")
    
    return ProductResponse.parse_obj(new_product.dict()) # Beanie'nin döndürdüğü Product nesnesini parse_obj ile dönüştürüyoruz


@router.get("/", response_model=List[ProductResponse], summary="Tüm ürünleri/parçaları listele")
async def get_all_products_route(current_user: User = Depends(get_current_user)):
    products = await product_controller.get_all_products()
    return [ProductResponse.parse_obj(p.dict()) for p in products]

@router.get("/{product_id}", response_model=ProductResponse, summary="Belirli bir ürünü/parçayı ID ile getir")
async def get_product_by_id_route(product_id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    # PydanticObjectId otomatik dönüşüm yapar, elle ObjectId(product_id) yapmaya gerek kalmaz.
    product = await product_controller.get_product_details_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ürün bulunamadı")
    return ProductResponse.parse_obj(product.dict())

@router.put("/{product_id}", response_model=ProductResponse, summary="Bir ürünü/parçayı ID ile güncelle")
async def update_product_route(
    product_id: PydanticObjectId, # PydanticObjectId kullanıyoruz
    product_update: ProductUpdate, # ProductUpdate modelini kullanıyoruz
    current_user: User = Depends(role_required(["Yönetici", "Depo Sorumlusu"]))
):
    update_data = product_update.dict(exclude_unset=True) # Sadece gelen alanları al
    
    # Güncelleme sırasında updated_at'ı otomatik ayarlamak için controller'a bırakabiliriz
    # veya burada update_data'ya ekleyebiliriz:
    # update_data["updated_at"] = datetime.now() 
    
    updated_product = await product_controller.update_existing_product(product_id, update_data)
    
    if not updated_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Güncellenecek ürün bulunamadı.")
    
    return ProductResponse.parse_obj(updated_product.dict())

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Bir ürünü/parçayı ID ile sil")
async def delete_product_route(
    product_id: PydanticObjectId, # PydanticObjectId kullanıyoruz
    current_user: User = Depends(role_required(["Yönetici"]))
):
    result = await product_controller.delete_existing_product(product_id)
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Silinecek ürün bulunamadı veya silinemedi.")
    
    return # 204 No Content yanıtı için boş döner