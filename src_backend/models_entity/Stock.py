from datetime import datetime
from typing import Optional
from beanie import Document, Link # Beanie kütüphanesinden Document ve Link sınıflarını import ediyoruz.
                                 # Document: MongoDB koleksiyonundaki bir belgeyi temsil eden temel sınıf.
                                 # Link: Diğer Beanie Document'larına referans vermek için kullanılır, SQL'deki FK'lere benzer.
from pydantic import Field # Pydantic kütüphanesinden Field sınıfını import ediyoruz.
                          # Alanlara varsayılan değerler, kısıtlamalar (örn. minimum/maksimum değer) ve indeksleme özellikleri eklemek için kullanılır.

# Bu modelin referans verdiği diğer Beanie Document'ları import ediyoruz.
# Beanie Link'leri, başka bir koleksiyondaki belgeye referans verdiğinde,
# bu referans verilen Document'ın da tanımlanmış ve import edilmiş olması gerekir.
from .product import Product
from .warehouse import Warehouse

class Stock(Document):
    """
    Bu sınıf, bir ürünün belirli bir depodaki mevcut stok seviyesini temsil eder.
    MongoDB'deki 'stocks' koleksiyonundaki her bir belgeye karşılık gelir.
    """
    # product: Link[Product] -> 'Product' Document'ına bir referans (link) tanımlar.
    # Bu, aslında MongoDB'de Product koleksiyonundaki ilgili belgenin _id'sini saklar.
    # Beanie, bu _id üzerinden Product Document'ına kolayca erişim sağlar.
    product: Link[Product] 
    
    # warehouse: Link[Warehouse] -> 'Warehouse' Document'ına bir referans (link) tanımlar.
    warehouse: Link[Warehouse] 
    
    # quantity: int = Field(default=0, ge=0) -> Stoktaki ürün miktarı.
    # default=0: Eğer değer verilmezse varsayılan olarak 0 olur.
    # ge=0: Değerin 0'a eşit veya daha büyük (greater than or equal) olması gerektiğini belirtir, yani negatif stok olmaz.
    quantity: int = Field(default=0, ge=0) 
    
    # critical_stock_level: int = Field(default=0, ge=0) -> Bu ürün için kritik stok seviyesi.
    # Stok bu seviyenin altına düştüğünde uyarı verilebilir.
    critical_stock_level: int = Field(default=0, ge=0) 
    
    # last_updated: datetime = Field(default_factory=datetime.now) -> Stok kaydının son güncellenme tarihi ve saati.
    # default_factory=datetime.now: Her yeni belge oluşturulduğunda veya güncellendiğinde
    # bu alana mevcut tarih ve saat otomatik olarak atanır.
    last_updated: datetime = Field(default_factory=datetime.now) 

    class Settings:
        """
        Beanie Document'ın MongoDB ile nasıl eşleşeceğini ve davranacağını belirleyen ayarlar.
        """
        name = "stocks" # Bu Document'ın MongoDB'deki koleksiyon adı 'stocks' olacaktır.
                       # Eğer bu koleksiyon yoksa, Beanie ilk bağlantıda otomatik olarak oluşturur.
        
        # indexes: Birleşik benzersiz indeks tanımlar.
        # Bu, aynı ürünün aynı depoda birden fazla stok kaydının olmasını engeller.
        # Örneğin, bir depo ve bir ürün kombinasyonu için sadece bir stok belgesi olabilir.
        # ([("product", 1), ("warehouse", 1)], {"unique": True}):
        # - ("product", 1): 'product' alanına göre artan (1) sırada indeksleme yapar.
        # - ("warehouse", 1): 'warehouse' alanına göre artan (1) sırada indeksleme yapar.
        # - {"unique": True}: Bu iki alanın kombinasyonunun benzersiz olması gerektiğini belirtir.
        # Beanie, Link'lerin arkasındaki gerçek _id'leri kullanarak bu indeksi oluşturur.
        indexes = [
            ([("product", 1), ("warehouse", 1)], {"unique": True})
        ]

    def __repr__(self):
        """
        Geliştiriciler için bu objenin string temsilini döndürür.
        Debugger veya loglarda objeyi daha anlaşılır görmek için faydalıdır.
        """
        return f"<Stock(product_id={self.product.id}, warehouse_id={self.warehouse.id}, quantity={self.quantity})>"

    def __str__(self):
        """
        Son kullanıcıya gösterilebilecek veya okunabilir bir string temsilini döndürür.
        """
        return f"Stock of {self.product.name} in {self.warehouse.name}: {self.quantity}"