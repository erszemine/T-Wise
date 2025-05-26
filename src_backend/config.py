# backend/src/stok_yonetim_backend/config.py
import os
from dotenv import load_dotenv

load_dotenv() # .env dosyasındaki değişkenleri yükle

# Veritabanı ayarları
# Lütfen kendi PostgreSQL kullanıcı adınız, şifreniz ve veritabanı adınıza göre güncelleyin.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/stok_db")

# JWT (JSON Web Token) ayarları - Güvenli bir anahtar kullanın ve bunu .env'de tutun!
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-replace-me-in-production-please")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Diğer uygulama ayarları buraya eklenebilir