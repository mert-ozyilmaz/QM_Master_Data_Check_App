"""Dosya/sayfa bazlı sabit ayarlar.

Kural dokümanındaki 'ilk N satır başlık satırıdır' bilgisi burada tutulur.
Başlık satırları hiçbir kuralda kontrol edilmez (Madde 1.1).
"""
from .yardimcilar import norm_ad

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

# (dosya, sayfa) -> başlık satırı sayısı.  sayfa=None -> dosyadaki tüm sayfalar.
# Önce (dosya, sayfa), sonra (dosya, None) aranır; yoksa VARSAYILAN kullanılır.
_BASLIK_SATIRLARI = {
    ("Hata kodları ve seçim kümeleri", None): 1,     # Madde 3.1
    ("Örnekleme yöntemi", None): 2,                   # Madde 9.1
    ("Kontrol planı", "Plan"): 5,                     # Madde 12.1.1
    ("Kontrol planı", "Çoklu malzeme tayini"): 2,     # Dokümanda yok; şablonda 2 satır başlık var
}

# Kural uygulanmayacak, sadece bilgi amaçlı sayfalar (dosya, sayfa).
# Güncel şablonlarda bilgi sayfası yok; gerekirse buraya ("Dosya adı", "Sayfa adı") eklenir.
_BILGI_SAYFALARI = []

_BASLIK = {(norm_ad(d), norm_ad(s) if s else None): n for (d, s), n in _BASLIK_SATIRLARI.items()}
_BILGI = {(norm_ad(d), norm_ad(s)) for d, s in _BILGI_SAYFALARI}
DOSYA_NORM = {norm_ad(d): d for d in DOSYA_ADLARI}


def baslik_satiri_sayisi(dosya: str, sayfa: str) -> int:
    d, s = norm_ad(dosya), norm_ad(sayfa)
    return _BASLIK.get((d, s), _BASLIK.get((d, None), VARSAYILAN_BASLIK_SATIRI))


def bilgi_sayfasi_mi(dosya: str, sayfa: str) -> bool:
    return (norm_ad(dosya), norm_ad(sayfa)) in _BILGI
