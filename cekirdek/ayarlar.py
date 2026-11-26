"""Dosya/sayfa bazlı sabit ayarlar.

Kural dokümanındaki 'ilk N satır başlık satırıdır' bilgisi burada tutulur.
Başlık satırları hiçbir kuralda kontrol edilmez (Madde 1.1).
"""
import re

from .yardimcilar import norm_ad, norm_dosya_adi

# Kural dokümanındaki sıra + referans (başvuru) dosyaları
DOSYA_ADLARI = [
    "Ana kontrol karakteristikleri",
    "Hata kodları ve seçim kümeleri",
    "Kalite bilgi kaydı",
    "Kalite görünümü",
    "Kalite iş yerleri",
    "Kontrol yöntemi",
    "Örnekleme şeması",
    "Örnekleme yöntemi",
    "SD denetim verisi",
    "Tedarikte QM",
    "Kontrol planı",
    "Malzeme ölçü birimleri",
    "Ölçü birimleri",
]

VARSAYILAN_BASLIK_SATIRI = 1

# ---- Büyük dosya ayarları ----
# Bir kuralın raporlayacağı en fazla bulgu sayısı. Aşılırsa fazlası sayılır ama saklanmaz (bellek koruması).
MAKS_BULGU_KURAL = 5000
# Word raporuna yazılacak en fazla bulgu satırı (tamamı Excel raporunda bulunur).
MAKS_WORD_SATIR = 3000
# Veri bittikten sonra bu kadar ardışık boş satır görülürse sayfa okuması durdurulur
# (Excel'de biçimlendirilmiş ama boş milyonlarca satırı taramamak için).
ARDISIK_BOS_SATIR_LIMITI = 1000

# (dosya, sayfa) -> hücre sayı biçimine bakılması gereken kolonlar (Madde 12.1.15: W, X, Y).
_BICIM_KOLONLARI = {
    ("Kontrol planı", "Kontrol planı"): ["W", "X", "Y"],
}

# (dosya, sayfa) -> başlık satırı sayısı.  sayfa=None -> dosyadaki tüm sayfalar.
# Önce (dosya, sayfa), sonra (dosya, None) aranır; yoksa VARSAYILAN kullanılır.
_BASLIK_SATIRLARI = {
    ("Hata kodları ve seçim kümeleri", None): 1,     # Madde 3.1
    ("Örnekleme yöntemi", None): 2,                   # Madde 9.1
}

# Kural uygulanmayacak, sadece bilgi amaçlı sayfalar (dosya, sayfa).
# Güncel şablonlarda bilgi sayfası yok; gerekirse buraya ("Dosya adı", "Sayfa adı") eklenir.
_BILGI_SAYFALARI = []

_BASLIK = {(norm_ad(d), norm_ad(s) if s else None): n for (d, s), n in _BASLIK_SATIRLARI.items()}
_BILGI = {(norm_ad(d), norm_ad(s)) for d, s in _BILGI_SAYFALARI}
_BICIM = {(norm_ad(d), norm_ad(sh)): k for (d, sh), k in _BICIM_KOLONLARI.items()}
DOSYA_NORM = {norm_ad(d): d for d in DOSYA_ADLARI}


def standart_dosya_adi(yuklenen_ad: str):
    """Yüklenen dosya adından standart dosya adını bulur; bulunamazsa None.
    Önce birebir eşleşme, yoksa 'Kontrol_planı_5960d5.xlsx' gibi ek içeren adlar için
    en uzun ön ek eşleşmesi kullanılır."""
    ad = norm_dosya_adi(yuklenen_ad)
    if ad in DOSYA_NORM:
        return DOSYA_NORM[ad]
    ham = norm_ad(re.sub(r"\.xls[xm]?$", "", str(yuklenen_ad).strip(), flags=re.I))
    adaylar = [n for n in DOSYA_NORM if ham.startswith(n)]
    return DOSYA_NORM[max(adaylar, key=len)] if adaylar else None


def baslik_satiri_sayisi(dosya: str, sayfa: str) -> int:
    d, s = norm_ad(dosya), norm_ad(sayfa)
    return _BASLIK.get((d, s), _BASLIK.get((d, None), VARSAYILAN_BASLIK_SATIRI))


def bilgi_sayfasi_mi(dosya: str, sayfa: str) -> bool:
    return (norm_ad(dosya), norm_ad(sayfa)) in _BILGI


def bicim_kolonlari(dosya: str, sayfa: str) -> list:
    return _BICIM.get((norm_ad(dosya), norm_ad(sayfa)), [])
