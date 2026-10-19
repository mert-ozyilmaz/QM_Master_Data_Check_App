"""Genel yardımcı fonksiyonlar (metin/sayı normalizasyonu, kolon harfi çevirme vb.)."""
import re
import unicodedata
from datetime import date, datetime
from functools import lru_cache

from openpyxl.utils import column_index_from_string, get_column_letter

_TR_HARITA = str.maketrans({
    "İ": "i", "I": "i", "ı": "i", "Ş": "s", "ş": "s", "Ğ": "g", "ğ": "g",
    "Ü": "u", "ü": "u", "Ö": "o", "ö": "o", "Ç": "c", "ç": "c",
})


def norm_ad(ad: str) -> str:
    """Dosya/sayfa adlarını karşılaştırmak için sadeleştirir.
    'Hata_kodları_ve_seçim_kümeleri' == 'Hata kodları ve seçim kümeleri'
    'NİCEL ' == 'Nicel'
    """
    s = unicodedata.normalize("NFC", str(ad)).strip()
    s = s.translate(_TR_HARITA).lower()
    return re.sub(r"[^a-z0-9]", "", s)


def norm_dosya_adi(ad: str) -> str:
    ad = re.sub(r"\.xls[xm]?$", "", str(ad).strip(), flags=re.I)
    return norm_ad(ad)


def metin(v) -> str:
    """Hücre değerini karşılaştırılabilir metne çevirir (boş -> '')."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    if isinstance(v, (datetime, date)):
        return v.strftime("%d.%m.%Y")
    return str(v).replace("\xa0", " ").strip()


def dolu(v) -> bool:
    return metin(v) != ""


def sayi(v):
    """Değeri float'a çevirir. '13,52' ve 13.52 desteklenir. Çevrilemezse None."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = metin(v).replace(" ", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def x_mi(v) -> bool:
    """Hücre büyük harf 'X' ile işaretli mi? (küçük 'x' işaretli sayılmaz)"""
    return metin(v) == "X"


@lru_cache(maxsize=None)
def kolon_no(harf: str) -> int:
    """'A' -> 0, 'B' -> 1, 'AA' -> 26 ..."""
    return column_index_from_string(harf) - 1


@lru_cache(maxsize=None)
def kolon_harfi(no: int) -> str:
    return get_column_letter(no + 1)


def madde_sirasi(madde_no: str):
    """'2.1.10' -> (2,1,10) : doğal sıralama için."""
    return tuple(int(p) if p.isdigit() else 0 for p in madde_no.split("."))
