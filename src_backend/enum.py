# backend/src/stok_yonetim_backend/enums.py (veya constants.py)
from enum import Enum

class Permission(str, Enum): # String değerli Enum kullanıyoruz ki FastAPI path/query param olarak da kullanılabilir
    DEPO_DUZENI_YONET = "DEPO_DUZENI_YONET"
    URUN_KABUL_ET = "URUN_KABUL_ET"
    STOK_SEVIYESI_GUNCELLE = "STOK_SEVIYESI_GUNCELLE"
    PARCA_DURUMU_KONTROL_ET = "PARCA_DURUMU_KONTROL_ET"
    EKSİK_PARCA_TEDARİK_ET = "EKSİK_PARCA_TEDARIK_ET"
    LOJISTIK_PLANLAMA_YAP = "LOJISTIK_PLANLAMA_YAP"
    URETIME_PARCA_ILE_T = "URETIME_PARCA_ILET"
    RAPOR_OLUSTUR = "RAPOR_OLUSTUR"

# Not: İleride pozisyonlar ve yetkileri arasındaki eşleşmeyi
# veritabanında tutmak daha esnek olacaktır.
# Örneğin: Depo Yöneticisi -> DEPO_DUZENI_YONET, STOK_SEVIYESI_GUNCELLE vb.