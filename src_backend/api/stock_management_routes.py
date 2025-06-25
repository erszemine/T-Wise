# src_backend/api/stock_management_routes.py
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Optional
from bson.objectid import ObjectId
from datetime import datetime
from pydantic import BaseModel, Field

from src_backend.enums import UserPosition

from ..models_entity.Stock import Stock
from ..models_entity.Product import Product
from ..models_entity.StockMovement import StockMovement
# from models_entity.UretimTalebi import UretimTalebi # Üretim talebi kullanılmayacağı için yorum satırı yapıldı veya silindi
from ..models_entity.User import User
from ..security import role_required, get_current_user

from ..schemas.stock_movement_schemas import StockMovementResponse, StockMovementCreate
# Diğer şemaları da import ettiğinizden emin olun (ProductResponse, UserResponse)
from ..schemas.product_schemas import ProductResponse
from ..schemas.user_schemas import UserResponse


router = APIRouter(prefix="/api/stock-management", tags=["Stock Management"])

@router.post(
    "/record-movement",
    response_model=StockMovementResponse, # schemas'tan gelen StockMovementResponse kullanılacak
    status_code=status.HTTP_201_CREATED,
    summary="Yeni bir stok hareketi kaydet ve stok miktarını güncelle"
)
async def record_stock_movement(
    movement_data: StockMovementCreate, # schemas'tan gelen StockMovementCreate kullanılacak
    current_user: User = Depends(role_required([UserPosition.ADMIN, UserPosition.DEPO_YONETICISI]))
):
    try:
        # PydanticObjectId yerine ObjectId kullanıyorsanız, `product_id` alanını `str` olarak tanımlamanız
        # ve burada `ObjectId(movement_data.product_id)` ile dönüştürmeniz gerekir.
        # Eğer Product modelinde _id tipi PydanticObjectId ise, PydanticObjectId kullanmak daha tutarlıdır.
        product = await Product.get(movement_data.product_id) # Product.get(PydanticObjectId(movement_data.product_id)) daha doğru
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="İlgili ürün bulunamadı")

        # current_user zaten bir User Beanie dokümanı. Link olarak atayabilirsiniz.
        # Performansı artırmak için User.get ile çekmek yerine doğrudan current_user'ı atayabiliriz
        # ancak Type Hinting'in doğru çalıştığından emin olmak gerekir.
        # `current_user` doğrudan User objesi olduğu için Beanie onu otomatik olarak linkleyecektir.
        # Eğer current_user bir Link objesi ise, `current_user.ref` kullanmak gerekir.
        # Ancak Depends(get_current_user) bize direkt User objesini verir.
        performed_by_link = current_user # Veya eğer current_user bir link ise: current_user.ref

        # Stok kaydını bul veya oluştur
        stock = await Stock.find_one(
            Stock.product.id == product.id,
            Stock.location == movement_data.location # movement_data.location null olabilir, kontrol edin
        )
        if not stock:
            # Yeni konumda veya ürün için ilk stok kaydı ise oluştur
            stock = Stock(product=product, location=movement_data.location or "UNKNOWN", current_quantity=0)
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
            product=product, # product objesi otomatik olarak linklenecek
            movement_type=movement_data.movement_type,
            quantity=movement_data.quantity,
            reference_document=movement_data.reference_document,
            performed_by=performed_by_link, # User objesi otomatik olarak linklenecek
            # Diğer alanlar
            from_location=movement_data.from_location,
            to_location=movement_data.to_location,
            remarks=movement_data.remarks
        )
        await new_movement.insert()

        # Oluşturulan hareketin tam detaylarını (linkli belgelerle birlikte) döndür
        # Sadece Beanie dokümanını döndürüyoruz. schemas/stock_movement_schemas.py'deki
        # StockMovementResponse, Link'leri otomatik olarak dönüştürecektir.
        # Bu satırı kullanmak yerine, direkt new_movement objesini döndürmeniz daha temizdir:
        # created_movement_with_details = await StockMovement.get(new_movement.id, fetch_links=True)
        # return created_movement_with_details
        
        # Eğer Post operasyonunda tam olarak linkleri çekmek istiyorsanız:
        await new_movement.fetch_links() # Linkleri burada çekin
        return new_movement # Beanie dokümanını döndürün, şema otomatik dönüştürür

    except HTTPException as e:
        raise e
    except Exception as e:
        # Hatanın detayını loglamak ve hata mesajında vermek faydalıdır.
        print(f"Stok hareketi kaydedilemedi hatası: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Stok hareketi kaydedilemedi: {e}")


@router.get(
    "/movements",
    response_model=List[StockMovementResponse], # schemas'tan gelen StockMovementResponse kullanılacak
    summary="Tüm stok hareketlerini listele"
)
async def get_all_stock_movements(current_user: User = Depends(get_current_user)):
    # fetch_links=True kullanarak tüm linkli dokümanları çekin
    # Bu, her hareket için ayrı ayrı fetch_link çağırmaktan daha verimlidir.
    movements = await StockMovement.find_all(fetch_links=True).to_list()
    
    # Listeyi doğrudan döndürün. StockMovementResponse şeması dönüşümü yapacaktır.
    return movements


