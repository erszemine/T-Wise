# backend/src/stok_yonetim_backend/config.py
import os
from dotenv import load_dotenv

load_dotenv() # .env dosyasındaki değişkenleri yükle

# MongoDB 
MONGO_URI = os.getenv("MONGO_URI") # Bu artık .env'den çekilecek
MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME", "stock_management_db") # .env'den çekilir, yoksa varsayılan

# JWT 
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Diğer uygulama ayarları buraya eklenebilir