from enum import Enum # Python'ın standart Enum modülünü import ediyoruz

class UserPosition(str, Enum):
    ADMIN = "admin"
    KALITE_KONTROL_UZMANI = "kalite kontrol uzmanı"
    TEDARIK_PLANLAMA_UZMANI = "tedarik planlama uzmanı"
    SATIN_ALMA_UZMANI = "satın alma uzmanı"
    STOK_KONTROL_UZMANI = "stok kontrol uzmanı"
    DEPO_YONETICISI = "depo yöneticisi"


# Not: İleride pozisyonlar ve yetkileri arasındaki eşleşmeyi
# veritabanında tutmak daha esnek olacaktır.
# Örneğin: Depo Yöneticisi -> DEPO_DUZENI_YONET, STOK_SEVIYESI_GUNCELLE vb.