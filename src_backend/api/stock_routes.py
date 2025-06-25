# src_backend/api/stock_routes.py

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from beanie import PydanticObjectId, Link # PydanticObjectId ve Link'i import ediyoruz
from datetime import datetime

from models_entity.Stock import Stock
from models_entity.Product import Product # Product modelini import ediyoruz
from models_entity.User import User # Kullanıcı yetkilendirme için

from security import role_required, get_current_user
from enums import UserPosition # UserPosition enum'ını import ediyoruz

# Şemaları doğru yoldan import ediyoruz
from schemas.stock_shemas import StockResponse, StockCreate, StockUpdate


router = APIRouter(prefix="/api/stock", tags=["Stock"])

# ÖNEMLİ: stock_schemas.py dosyasında tanımlanan StockCreate ve StockResponse sınıflarını kullanıyoruz.
# BURADA AYNI İSİMDE YENİDEN TANIMLAMA YAPMAYIN!

@router.post("/", response_model=StockResponse, status_code=status.HTTP_201_CREATED, summary="Yeni bir stok kaydı oluştur")
async def create_stock(stock_data: StockCreate, current_user: User = Depends(role_required([UserPosition.ADMIN, UserPosition.DEPO_YONETICISI]))):
    try:
        # Product ID'sine göre ürünü bul
        product = await Product.get(stock_data.product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="İlgili ürün bulunamadı")

        # Bu ürün için zaten bir stok kaydı olup olmadığını kontrol et (Eğer her ürün için tek bir stok kaydı isteniyorsa)
        # Genellikle stok 'product' ve 'location' çiftine göre benzersiz olur.
        # Eğer böyle bir unique indexiniz varsa, ona göre kontrol etmelisiniz.
        # Mevcut modelinizde sadece 'product' linki var, 'location' ayrı bir alan.
        # Burada sadece 'product' bazında kontrol ediyoruz.
        existing_stock = await Stock.find_one(Stock.product.id == stock_data.product_id)
        if existing_stock:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu ürün için zaten bir stok kaydı mevcut. Mevcut kaydı güncelleyin.")

        # Yeni stok objesini oluştur
        # stock_data.model_dump() kullanarak Pydantic modelini dictionary'ye çeviriyoruz.
        # product_id'yi dışarıda bırakıyoruz çünkü Link olarak atayacağız.
        stock_dict = stock_data.model_dump(exclude={'product_id'})
        new_stock = Stock(**stock_dict)
        new_stock.product = product # Product Link objesini ata

        await new_stock.insert()
        
        # İlişkili ürün detaylarını da yanıtla döndürmek için fetch_link kullanıyoruz
        await new_stock.fetch_link(Stock.product)

        # model_validate() kullanarak Beanie objesini doğrudan Pydantic Response şemasına dönüştürüyoruz
        return StockResponse.model_validate(new_stock)

    except HTTPException as e: # Custom hataları yakala
        raise e
    except Exception as e: # Diğer genel hataları yakala
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Stok kaydı oluşturulamadı: {e}")

@router.get("/", response_model=List[StockResponse], summary="Tüm stok kayıtlarını listele")
async def get_stocks(current_user: User = Depends(get_current_user)):
    # fetch_links=True kullanarak tüm ilişkili ürün bilgilerini de tek seferde çekiyoruz
    stocks = await Stock.find_all(fetch_links=True).to_list()
    
    # Her bir stok objesini StockResponse şemasına dönüştürerek listeyi döndürüyoruz
    return [StockResponse.model_validate(stock) for stock in stocks]


@router.get("/by-product/{product_id}", response_model=Optional[StockResponse], summary="Ürün ID'sine göre stok kaydını getir")
async def get_stock_by_product_id(product_id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    try:
        # find_one içinde fetch_links=True kullanarak ilişkili ürünü de çek
        stock = await Stock.find_one(Stock.product.id == product_id, fetch_links=True)
        if not stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bu ürüne ait stok kaydı bulunamadı")
        
        # model_validate() kullanarak doğru Pydantic objesi oluşturma
        return StockResponse.model_validate(stock)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Geçersiz ID veya hata: {e}")


@router.put("/{stock_id}", response_model=StockResponse, summary="Bir stok kaydını ID ile güncelle")
async def update_stock(stock_id: PydanticObjectId, stock_update: StockUpdate, current_user: User = Depends(role_required([UserPosition.ADMIN, UserPosition.DEPO_YONETICISI]))):
    try:
        stock = await Stock.get(stock_id) # Doğrudan PydanticObjectId kullanın
        if not stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Güncellenecek stok kaydı bulunamadı")

        update_data = stock_update.model_dump(exclude_unset=True) # Yalnızca set edilen alanları alır

        # Eğer product_id güncelleniyorsa, yeni Product Link'i oluştur
        if 'product_id' in update_data and update_data['product_id']:
            new_product = await Product.get(update_data['product_id'])
            if not new_product:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Yeni ilgili ürün bulunamadı")
            stock.product = new_product
            del update_data['product_id'] # Güncelleme döngüsüne girmemesi için sil

        # Geri kalan alanları güncelle
        for key, value in update_data.items():
            setattr(stock, key, value)

        await stock.save()
        await stock.fetch_link(Stock.product) # Güncellenmiş stok kaydını döndürmeden önce product linkini tekrar fetch et
        
        # model_validate() kullanarak doğru Pydantic objesi oluşturma
        return StockResponse.model_validate(stock)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Güncelleme hatası: {e}")


@router.delete("/{stock_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Bir stok kaydını ID ile sil")
async def delete_stock(stock_id: PydanticObjectId, current_user: User = Depends(role_required([UserPosition.ADMIN]))):
    try:
        stock = await Stock.get(stock_id) # Doğrudan PydanticObjectId kullanın
        if not stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Silinecek stok kaydı bulunamadı")

        await stock.delete()
        return
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Silme hatası: {e}")