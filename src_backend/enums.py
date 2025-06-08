# src_backend/src_stok_yonetim_backend/app_enums.py (veya constants.py)
from enum import Enum # Python'ın standart Enum modülünü import ediyoruz

class Permission(str, Enum): # String değerli Enum kullanıyoruz ki FastAPI path/query param olarak da kullanılabilir
    DEPO_DUZENI_YONET = "DEPO_DUZENI_YONET"
    URUN_KABUL_ET = "URUN_KABUL_ET"
    STOK_SEVIYESI_GUNCELLE = "STOK_SEVIYESI_GUNCELLE"
    PARCA_DURUMU_KONTROL_ET = "PARCA_DURUMU_KONTROL_ET"
    EKSİK_PARCA_TEDARIK_ET = "EKSİK_PARCA_TEDARIK_ET"
    LOJİSTİK_PLANLAMA_YAP = "LOJİSTİK_PLANLAMA_YAP"
    URETME_PARCA_ILE_T = "URETME_PARCA_ILET"
    RAPOR_OLUSTUR = "RAPOR_OLUSTUR"

# Not: İleride pozisyonlar ve yetkileri arasındaki eşleşmeyi
# veritabanında tutmak daha esnek olacaktır.
# Örneğin: Depo Yöneticisi -> DEPO_DUZENI_YONET, STOK_SEVIYESI_GUNCELLE vb.