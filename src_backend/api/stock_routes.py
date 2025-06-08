# src_backend/api/stock_routes.py
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime
from pydantic import BaseModel, Field

from models_entity.Stock import Stock
from models_entity.Product import Product
from models_entity.User import User
from security import role_required, get_current_user

router = APIRouter()

class StockCreate(BaseModel):
    product: str # Product ID'si string olarak
    location: str
    current_quantity: int = 0
    reserved_quantity: int = 0
    incoming_quantity: int = 0
    min_level: int = 0
    max_level: int = 99999
    serial_numbers: Optional[List[str]] = []

class StockResponse(Stock):
    id: str = Field(alias="_id")
    product: str # Yanıtta da Product ID'si string olarak
    product_details: Optional[Product] = None # İlişkili ürün detayları
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True

@router.post("/", response_model=StockResponse, status_code=status.HTTP_201_CREATED, summary="Yeni bir stok kaydı oluştur")
async def create_stock(stock_data: StockCreate, current_user: User = Depends(role_required(["Yönetici", "Depo Sorumlusu"]))):
    try:
        product = await Product.get(ObjectId(stock_data.product))
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="İlgili ürün bulunamadı")

        # Stok kaydını bul veya oluştur
        stock = await Stock.find_one(Stock.product.id == product.id)
        if stock: # Eğer zaten bu ürün ve konum için bir stok kaydı varsa hata döndür
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu ürün için zaten bir stok kaydı mevcut. Mevcut kaydı güncelleyin.")

        new_stock = Stock(**stock_data.dict(exclude={'product'}))
        new_stock.product = product

        await new_stock.insert()
        return StockResponse(
            **new_stock.dict(),
            id=str(new_stock.id),
            product=str(new_stock.product.id),
            product_details=product
        )
    except HTTPException as e: # Custom hataları yakala
        raise e
    except Exception as e: # Diğer genel hataları yakala
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Stok kaydı oluşturulamadı: {e}")

@router.get("/", response_model=List[StockResponse], summary="Tüm stok kayıtlarını listele")
async def get_stocks(current_user: User = Depends(get_current_user)):
    stocks = await Stock.find_all().to_list()
    response_list = []
    for stock in stocks:
        await stock.fetch_link(Stock.product)
        response_list.append(StockResponse(
            **stock.dict(),
            id=str(stock.id),
            product=str(stock.product.id),
            product_details=stock.product
        ))
    return response_list

@router.get("/by-product/{product_id}", response_model=Optional[StockResponse], summary="Ürün ID'sine göre stok kaydını getir")
async def get_stock_by_product_id(product_id: str, current_user: User = Depends(get_current_user)):
    try:
        stock = await Stock.find_one(Stock.product.id == ObjectId(product_id))
        if not stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bu ürüne ait stok kaydı bulunamadı")
        await stock.fetch_link(Stock.product)
        return StockResponse(
            **stock.dict(),
            id=str(stock.id),
            product=str(stock.product.id),
            product_details=stock.product
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Geçersiz ID veya hata: {e}")


@router.put("/{stock_id}", response_model=StockResponse, summary="Bir stok kaydını ID ile güncelle")
async def update_stock(stock_id: str, stock_update: StockCreate, current_user: User = Depends(role_required(["Yönetici", "Depo Sorumlusu"]))):
    try:
        stock = await Stock.get(ObjectId(stock_id))
        if not stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Güncellenecek stok kaydı bulunamadı")

        update_data = stock_update.dict(exclude_unset=True)
        if 'product' in update_data: # Ürün referansı değişiyorsa
            product = await Product.get(ObjectId(update_data['product']))
            if not product:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Yeni ilgili ürün bulunamadı")
            stock.product = product
            del update_data['product']

        for key, value in update_data.items():
            setattr(stock, key, value)

        await stock.save()
        await stock.fetch_link(Stock.product) # Güncellenmiş stok kaydını döndürmeden önce product linkini tekrar fetch et
        return StockResponse(
            **stock.dict(),
            id=str(stock.id),
            product=str(stock.product.id),
            product_details=stock.product
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Güncelleme hatası: {e}")

@router.delete("/{stock_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Bir stok kaydını ID ile sil")
async def delete_stock(stock_id: str, current_user: User = Depends(role_required(["Yönetici"]))):
    try:
        stock = await Stock.get(ObjectId(stock_id))
        if not stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Silinecek stok kaydı bulunamadı")

        await stock.delete()
        return
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Silme hatası: {e}")