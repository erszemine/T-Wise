# backend/src/stok_yonetim_backend/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import DATABASE_URL # config.py'den DB URL'yi al

# SQLAlchemy Engine: Veritabanı ile bağlantı kurar. echo=True SQL sorgularını terminale yazdırır.
engine = create_async_engine(DATABASE_URL, echo=True)

# AsyncSessionLocal: Veritabanı oturumları oluşturmak için kullanılır.
# autocommit=False: Her işlemden sonra otomatik commit yapmaz.
# autoflush=False: Nesneler sorgulanırken otomatik olarak veritabanına göndermez.
# bind=engine: Bu oturumları belirlenen engine'e bağlar.
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Base: Tüm SQLAlchemy ORM modellerimizin türetileceği temel sınıf.
# Bu obje, metadata'yı (tablo ve sütun tanımları) toplar.
Base = declarative_base()

# FastAPI bağımlılığı olarak veritabanı oturumu sağlama fonksiyonu
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session # İstek işlenirken oturumu sağlar
        await session.close() # İstek bittikten sonra oturumu kapatır

# Veritabanı tablolarını ORM modellerinden oluşturma fonksiyonu
async def create_db_and_tables():
    # Asenkron bağlantı ile tüm tabloları oluştur
    async with engine.begin() as conn:
        # Base.metadata'daki tüm tabloları (yani Base'den türetilen tüm modelleri) veritabanında oluşturur
        await conn.run_sync(Base.metadata.create_all)