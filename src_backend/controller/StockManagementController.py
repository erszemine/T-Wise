# src_backend/controller/StockManagementController.py

from typing import List, Dict, Optional
from beanie import PydanticObjectId
from datetime import datetime

# Repository importları
from repository.InventoryRepository import StockRepository
from repository.StockMovementRepository import StockMovementRepository
from repository.ProductRepository import ProductRepository # Stok hareketlerinde ürün detayları için

# Model importları
from models_entity.Stock import Stock
from models_entity.Product import Product
from models_entity.StockMovement import StockMovement
from models_entity.User import User # Hareketi yapan kullanıcı bilgisi için

# DTO'lar veya Request Modelleri (ProductController'da olduğu gibi, şimdilik modelleri kullanabiliriz)
# Eğer bu modelleri doğrudan API rotalarından alıyorsanız, burada tekrar tanımlamanıza gerek yok.
# Ancak, Controller'a özel bir input veya output formatı gerekiyorsa buraya ekleyin.

class StockManagementController:
    def __init__(self,
                 stock_repository: StockRepository = None,
                 stock_movement_repository: StockMovementRepository = None,
                 product_repository: ProductRepository = None):
        self.stock_repository = stock_repository if stock_repository else StockRepository()
        self.stock_movement_repository = stock_movement_repository if stock_movement_repository else StockMovementRepository()
        self.product_repository = product_repository if product_repository else ProductRepository()

    async def record_stock_movement(
        self,
        product_id: PydanticObjectId,
        movement_type: str,
        quantity: int,
        performed_by_user: User, # Token'dan gelen kullanıcı objesi
        reference_document: Optional[str] = None,
        location: Optional[str] = "UNKNOWN"
    ) -> Optional[StockMovement]:
        """
        Yeni bir stok hareketi kaydeder ve ilgili ürünün stok miktarını günceller.
        """
        product = await self.product_repository.get_product_by_id(product_id)
        if not product:
            # Controller'dan HTTPException fırlatmak yerine, None döndür ve API katmanında yakala
            print(f"Hata: Ürün bulunamadı: {product_id}")
            return None

        # Belirli konum ve ürün için stok kaydını bul veya oluştur
        stock = await self.stock_repository.get_stock_by_product_and_location(product_id, location)
        if not stock:
            # Yeni konumda veya ürün için ilk stok kaydı ise oluştur
            stock_data = Stock(product=product, location=location, current_quantity=0, incoming_quantity=0, outgoing_quantity=0)
            stock = await self.stock_repository.create_stock(stock_data)
            if not stock: # Oluşturma başarısız olursa
                print(f"Hata: Yeni stok kaydı oluşturulamadı.")
                return None


        # Stok miktarını güncelle
        new_quantity = stock.current_quantity + quantity
        if new_quantity < 0:
            print("Hata: Stok miktarı sıfırın altına düşemez.")
            return None # API katmanında 400 Bad Request olarak dönecek

        # Güncelleme için sadece gerekli alanları içeren bir dict oluştur
        update_fields = {"current_quantity": new_quantity}

        if quantity > 0:
            update_fields["last_in_date"] = datetime.utcnow()
            update_fields["incoming_quantity"] = stock.incoming_quantity + quantity # Gelen miktar takibi
        else:
            update_fields["last_out_date"] = datetime.utcnow()
            update_fields["outgoing_quantity"] = stock.outgoing_quantity + abs(quantity) # Çıkan miktar takibi

        updated_stock = await self.stock_repository.update_stock(stock.id, update_fields)
        if not updated_stock:
            print(f"Hata: Stok kaydı güncellenemedi: {stock.id}")
            return None

        # Stok hareketi kaydını oluştur
        movement_data = StockMovement(
            product=product,
            movement_type=movement_type,
            quantity=quantity,
            reference_document=reference_document,
            performed_by=performed_by_user,
            location=location # Hareketin yapıldığı konum da kaydedilebilir
        )
        new_movement = await self.stock_movement_repository.create_stock_movement(movement_data)
        if not new_movement:
            print(f"Hata: Stok hareketi kaydı oluşturulamadı.")
            # Burada stok güncellemesini geri alma mantığı eklenebilir
            return None

        return new_movement

    async def get_all_stock_movements(self) -> List[StockMovement]:
        """
        Tüm stok hareketlerini listeler.
        """
        movements = await self.stock_movement_repository.get_all_stock_movements()
        # İlişkili verileri çekme (eğer repository bunu yapmıyorsa)
        for movement in movements:
            await movement.fetch_link(StockMovement.product)
            await movement.fetch_link(StockMovement.performed_by)
        return movements

    async def get_stock_movement_by_id(self, movement_id: PydanticObjectId) -> Optional[StockMovement]:
        """
        Belirli bir ID'ye sahip stok hareketinin detaylarını çeker.
        """
        movement = await self.stock_movement_repository.get_stock_movement_by_id(movement_id)
        if movement:
            await movement.fetch_link(StockMovement.product)
            await movement.fetch_link(StockMovement.performed_by)
        return movement

    async def plan_incoming_parts(
        self,
        needed_parts: List[Dict[str, int]], # [{'product_id': '...', 'quantity': ...}]
        current_user: User, # Hareketi başlatan kullanıcı
        supplier_info: Optional[str] = None,
        delivery_date: Optional[datetime] = None
    ) -> List[StockMovement]:
        """
        Gelecek parçalar için planlama yapar ve ilgili stok kayıtlarının incoming_quantity'sini günceller.
        Her planlanan parça için bir stok hareketi kaydı oluşturur.
        """
        movements_created = []
        for item in needed_parts:
            product_id = PydanticObjectId(item['product_id'])
            quantity = item['quantity']

            product = await self.product_repository.get_product_by_id(product_id)
            if not product:
                print(f"Hata: Planlanan ürün bulunamadı: {item['product_id']}")
                continue # Bu ürünü atla ve diğerleriyle devam et

            # Varsayılan konum
            location = "UNKNOWN"

            # Stok kaydını bul veya oluştur
            stock_record = await self.stock_repository.get_stock_by_product_and_location(product_id, location)
            if stock_record:
                # Sadece incoming_quantity'yi artır
                update_fields = {"incoming_quantity": stock_record.incoming_quantity + quantity}
                await self.stock_repository.update_stock(stock_record.id, update_fields)
            else:
                # Yeni stok kaydı oluştur, sadece incoming_quantity ile
                new_stock_data = Stock(product=product, location=location, incoming_quantity=quantity, current_quantity=0, outgoing_quantity=0)
                await self.stock_repository.create_stock(new_stock_data)

            # Stok hareketi kaydını oluştur (Sipariş Edildi)
            movement_data = StockMovement(
                product=product,
                movement_type="Giriş (Sipariş Edildi)",
                quantity=quantity,
                reference_document=f"Tedarikçi Siparişi: {supplier_info or 'N/A'}",
                performed_by=current_user,
                location=location
            )
            new_movement = await self.stock_movement_repository.create_stock_movement(movement_data)
            if new_movement:
                await new_movement.fetch_link(StockMovement.product)
                await new_movement.fetch_link(StockMovement.performed_by)
                movements_created.append(new_movement)
            else:
                print(f"Hata: Sipariş hareket kaydı oluşturulamadı. Ürün: {product.name}")

        return movements_created

    async def get_current_stock_levels(self) -> List[Stock]:
        """
        Tüm ürünler için mevcut stok seviyelerini listeler.
        """
        stocks = await self.stock_repository.get_all_stocks()
        for stock in stocks:
            await stock.fetch_link(Stock.product) # Ürün detaylarını çek
        return stocks

    async def get_stock_by_product_id(self, product_id: PydanticObjectId) -> Optional[Stock]:
        """
        Belirli bir ürüne ait stok kaydını getirir.
        """
        stock = await self.stock_repository.get_stock_by_product_id(product_id)
        if stock:
            await stock.fetch_link(Stock.product)
        return stock

    async def get_stock_by_location(self, location: str) -> List[Stock]:
        """
        Belirli bir konuma ait tüm stok kayıtlarını getirir.
        """
        stocks = await self.stock_repository.get_stock_by_location(location)
        for stock in stocks:
            await stock.fetch_link(Stock.product)
        return stocks