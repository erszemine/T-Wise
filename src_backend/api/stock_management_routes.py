# src_backend/api/stock_management_routes.py
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Optional
from bson.objectid import ObjectId
from datetime import datetime
from pydantic import BaseModel, Field

from models_entity.Stock import Stock
from models_entity.Product import Product
from models_entity.StockMovement import StockMovement
# from models_entity.UretimTalebi import UretimTalebi # Üretim talebi kullanılmayacağı için yorum satırı yapıldı veya silindi
from models_entity.User import User
from security import role_required, get_current_user

router = APIRouter()

class StockMovementRequest(BaseModel):
    product_id: str
    movement_type: str # Örn: "Giriş", "Çıkış", "İade", "Düzeltme"
    quantity: int # Giriş için pozitif, çıkış için negatif
    reference_document: Optional[str] = None # Fatura no, sipariş no vb.
    location: Optional[str] = "UNKNOWN" # Hangi konumdan/konuma hareket yapıldığı (şimdilik opsiyonel)

class StockMovementResponse(StockMovement):
    id: str = Field(alias="_id")
    product: str # Sadece ID
    performed_by: str # Sadece ID
    product_details: Optional[Product] = None # İlişkili ürün detayları
    performed_by_details: Optional[User] = None # İlişkili kullanıcı detayları
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True

class PlanIncomingPartsRequest(BaseModel):
    needed_parts: List[Dict[str, int]] # [{'product_id': '...', 'quantity': ...}]
    supplier_info: Optional[str] = None # Tedarikçi ID'si veya adı
    delivery_date: Optional[datetime] = None # Tahmini teslim tarihi

@router.post("/record-movement", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED, summary="Yeni bir stok hareketi kaydet ve stok miktarını güncelle")
async def record_stock_movement(movement_data: StockMovementRequest, current_user: User = Depends(role_required(["Yönetici", "Depo Sorumlusu"]))):
    try:
        product = await Product.get(ObjectId(movement_data.product_id))
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="İlgili ürün bulunamadı")

        # Stok kaydını bul veya oluştur
        # Basit versiyonda, her ürün için tek bir genel stok kaydı olduğunu varsayalım veya konum bazında kontrol edelim
        stock = await Stock.find_one(Stock.product.id == product.id, Stock.location == movement_data.location)
        if not stock:
            # Yeni konumda veya ürün için ilk stok kaydı ise oluştur
            stock = Stock(product=product, location=movement_data.location, current_quantity=0)
            await stock.insert()

        # Stok miktarını güncelle
        new_quantity = stock.current_quantity + movement_data.quantity
        if new_quantity < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stok miktarı sıfırın altına düşemez.")

        stock.current_quantity = new_quantity

        if movement_data.quantity > 0:
            stock.last_in_date = datetime.now()
        else:
            stock.last_out_date = datetime.now()

        await stock.save()

        new_movement = StockMovement(
            product=product,
            movement_type=movement_data.movement_type,
            quantity=movement_data.quantity,
            reference_document=movement_data.reference_document,
            performed_by=current_user
        )
        await new_movement.insert()

        return StockMovementResponse(
            **new_movement.dict(),
            id=str(new_movement.id),
            product=str(new_movement.product.id),
            performed_by=str(new_movement.performed_by.id),
            product_details=product,
            performed_by_details=current_user
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Stok hareketi kaydedilemedi: {e}")

@router.get("/movements", response_model=List[StockMovementResponse], summary="Tüm stok hareketlerini listele")
async def get_all_stock_movements(current_user: User = Depends(get_current_user)):
    movements = await StockMovement.find_all().to_list()
    response_list = []
    for movement in movements:
        await movement.fetch_link(StockMovement.product)
        await movement.fetch_link(StockMovement.performed_by)
        response_list.append(StockMovementResponse(
            **movement.dict(),
            id=str(movement.id),
            product=str(movement.product.id),
            performed_by=str(movement.performed_by.id),
            product_details=movement.product,
            performed_by_details=movement.performed_by
        ))
    return response_list

@router.post("/plan-incoming-parts", status_code=status.HTTP_200_OK, summary="Gelecek parçaları planla (sipariş oluşturma)")
async def plan_incoming_parts(request_body: PlanIncomingPartsRequest, current_user: User = Depends(role_required(["Yönetici", "Depo Sorumlusu"]))):
    movements_created = []
    for item in request_body.needed_parts:
        product_id = ObjectId(item['product_id'])
        quantity = item['quantity']

        product = await Product.get(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ürün bulunamadı: {item['product_id']}")

        # Varsayılan konumu "UNKNOWN" olarak alalım veya request_body'den alalım
        location = "UNKNOWN" # Burayı dinamik yapabilirsiniz

        stock_record = await Stock.find_one(Stock.product.id == product_id, Stock.location == location)
        if stock_record:
            stock_record.incoming_quantity += quantity
            await stock_record.save()
        else:
            new_stock = Stock(product=product, location=location, incoming_quantity=quantity, current_quantity=0)
            await new_stock.insert()

        movement = StockMovement(
            product=product,
            movement_type="Giriş (Sipariş Edildi)",
            quantity=quantity,
            reference_document=f"Tedarikçi Siparişi: {request_body.supplier_info or 'N/A'}",
            performed_by=current_user
        )
        await movement.insert()
        movements_created.append(StockMovementResponse(
            **movement.dict(),
            id=str(movement.id),
            product=str(movement.product.id),
            performed_by=str(movement.performed_by.id),
            product_details=product,
            performed_by_details=current_user
        ))

    return {"message": "Gelecek parçalar başarıyla planlandı.", "movements": movements_created}