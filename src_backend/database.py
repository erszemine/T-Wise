# src_backend/database.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, Document
from dotenv import load_dotenv
from typing import List, Type

# src_backend paketinin içindeki models_entity altından
from .models_entity.Product import Product
from .models_entity.Stock import Stock
from .models_entity.StockMovement import StockMovement
from .models_entity.User import User

# src_backend paketinin içindeki config modülünden
from .config import MONGO_URI, MONGO_DATABASE_NAME # NOT: config.py'de DATABASE_URL yerine MONGO_URI kullanıldığını varsayıyorum

# from models_entity.UretimTalebi import UretimTalebi # Üretim talebi kullanılmayacağı için yorum satırı yapıldı veya silindi

load_dotenv() # .env dosyasını yükle

# Tüm Beanie Document modellerini listeleyin (UretimTalebi hariç)
document_models: List[Type[Document]] = [
    Product,
    Stock,
    StockMovement,
    User,
]

async def connect_db():
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI ortam değişkeni ayarlanmamış.")

    try:
        client = AsyncIOMotorClient(mongo_uri)
        # URI'den veritabanı adını çek
        database_name = mongo_uri.split('/')[-1].split('?')[0]
        db = client[database_name]

        await init_beanie(database=db, document_models=document_models)
        print(f"MongoDB'ye başarıyla bağlandı! Veritabanı: {database_name}")
    except Exception as e:
        print(f"MongoDB bağlantı hatası: {e}")
        raise e