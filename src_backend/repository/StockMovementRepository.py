# src/stok_yonetim_backend/repositories/stock_movement_repository.py
from beanie import PydanticObjectId
from typing import List, Optional
from datetime import datetime

from models_entity.StockMovement import StockMovement
from models_entity.Product import Product # Product modelini import edin
from models_entity.User import User # User modelini import edin

class StockMovementRepository:
    async def create_movement(self, product_id: PydanticObjectId, 
                              user_id: PydanticObjectId,
                              quantity: int, movement_type: str, 
                              notes: Optional[str] = None) -> StockMovement:
        """
        Yeni bir stok hareketi kaydı oluşturur.
        product_id, user_id: Beanie'nin Link'ini otomatik çözmesi için PydanticObjectId olarak geçilebilir.
        """
        movement_data = {
            "product": product_id,
            "user": user_id,
            "quantity": quantity,
            "movement_type": movement_type,
            "notes": notes,
            "movement_date": datetime.utcnow()
        }
        
        movement = StockMovement(**movement_data)
        await movement.insert()
        return movement

    async def get_all_movements(self, skip: int = 0, limit: int = 100) -> List[StockMovement]:
        return await StockMovement.find_all().skip(skip).limit(limit).to_list()

    async def get_movements_by_product(self, product_id: PydanticObjectId, skip: int = 0, limit: int = 100) -> List[StockMovement]:
        return await StockMovement.find(StockMovement.product.id == product_id).skip(skip).limit(limit).to_list()

    async def get_movements_by_user(self, user_id: PydanticObjectId, skip: int = 0, limit: int = 100) -> List[StockMovement]:
        return await StockMovement.find(StockMovement.user.id == user_id).skip(skip).limit(limit).to_list()

    async def get_movement_by_id(self, movement_id: PydanticObjectId) -> Optional[StockMovement]:
        return await StockMovement.get(movement_id)