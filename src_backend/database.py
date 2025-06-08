'''
from motor.motor_asyncio import AsyncIOMotorClient # Motor, MongoDB için asenkron Python sürücüsüdür.
from beanie import init_beanie # Beanie ODM'yi başlatmak için kullanılan fonksiyon.
import logging # Uygulama logları için.

# Proje yapılandırma ayarlarını içeren config.py dosyasından gerekli değişkenleri import ediyoruz.
# Bu değişkenler (DATABASE_URL, MONGO_DATABASE_NAME) .env dosyasından okunur.
from .config import DATABASE_URL, MONGO_DATABASE_NAME

# Beanie'ye tanıtacağımız tüm Document (model) sınıflarını import ediyoruz.
# init_beanie fonksiyonu, bu Document'ları kullanarak MongoDB'de ilgili koleksiyonları oluşturacak
# ve tanımlanmış indeksleri ekleyecektir.
from .models_entitiy.product import Product
from .models_entitiy.stock import Stock
from .models_entitiy.stock_movement import StockMovement
from .models_entitiy.user import User


logger = logging.getLogger(__name__) # Bu modül için bir logger oluşturuluyor.

async def connect_to_mongodb():
    """
    MongoDB bağlantısını başlatır ve Beanie ODM'yi yapılandırır.
    Bu fonksiyon, FastAPI uygulamasının yaşam döngüsü başlangıcında (lifespan event) çağrılmalıdır.
    """
    if DATABASE_URL is None:
        logger.error("DATABASE_URL ortam değişkeni tanımlanmamış. MongoDB'ye bağlanılamıyor.")
        raise ValueError("DATABASE_URL ortam değişkeni tanımlı olmalıdır.")

    # AsyncIOMotorClient kullanarak MongoDB sunucusuna asenkron bir bağlantı oluşturulur.
    client = AsyncIOMotorClient(DATABASE_URL)
    
    # Beanie ODM'yi başlatma.
    # database: Bağlanılacak MongoDB veritabanı objesi. client[MONGO_DATABASE_NAME] ile belirlenir.
    # document_models: Beanie'nin yöneteceği ve MongoDB koleksiyonlarına eşleyeceği tüm Document sınıflarının listesi.
    #                  Beanie, bu modelleri kullanarak koleksiyonları ve indeksleri otomatik olarak oluşturur/günceller.
    await init_beanie(
        database=client[MONGO_DATABASE_NAME],
        document_models=[
            Product,
            Stock,
            StockMovement,
            User,
        ]
    )
    logger.info(f"MongoDB'ye '{MONGO_DATABASE_NAME}' veritabanı üzerinden başarıyla bağlanıldı.")

async def close_mongodb_connection():
    """
    MongoDB bağlantısını kapatır.
    Bu fonksiyon, FastAPI uygulamasının yaşam döngüsü sonunda (lifespan event) çağrılmalıdır.
    Motor istemcisi genellikle bağlantıları otomatik olarak yönetir, bu nedenle bu fonksiyon
    doğrudan bir 'kapatma' işlemi içermeyebilir, ancak yaşam döngüsü tutarlılığı için tutulur.
    """
    # Motor istemcisinin otomatik olarak bağlantıyı yöneteceğini varsayıyoruz.
    # Beanie'nin doğrudan bir 'close' metodu yoktur, ancak client nesnesini kullanarak yapılabilir.
    # Genellikle bu fonksiyon, doğrudan bir client.close() çağrısı gerektirmez,
    # ancak ileri düzey senaryolar için bir yer tutucudur.
    logger.info("MongoDB bağlantısı kapatıldı.") '''

# src_backend/database.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, Document
from dotenv import load_dotenv
from typing import List, Type

# Modelleri buraya import edin
from models_entity.Product import Product
from models_entity.Stock import Stock
from models_entity.StockMovement import StockMovement
from models_entity.User import User
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