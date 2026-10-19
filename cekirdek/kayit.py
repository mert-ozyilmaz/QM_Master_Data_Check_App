"""Kural kayıt sistemi.

Her kural, @kural(...) ile işaretlenmiş AYRI bir fonksiyondur. Kapsam, parametrelerden otomatik belirlenir:
  - dosya ve sayfa verilmedi  -> GENEL kural  (her dosya ve her sayfa)
  - sadece dosya verildi      -> DOSYA kuralı (o dosyanın tüm sayfaları)
  - dosya + sayfa verildi     -> SAYFA kuralı (sadece o sayfa)
"""
from dataclasses import dataclass
from typing import Callable, Optional

from .yardimcilar import madde_sirasi, norm_ad


class ReferansYok(Exception):
    """Kural, yüklenmemiş bir dosya/sayfaya başvuruyor."""


@dataclass
class Kural:
    id: str
    baslik: str
    fonksiyon: Callable
    dosya: Optional[str] = None
    sayfa: Optional[str] = None
    aktif: bool = True
    varsayim: str = ""      # belirsiz noktalar / yorum notu (raporda gösterilir)

    @property
    def kapsam(self) -> str:
        if self.dosya and self.sayfa:
            return "Sayfa"
        return "Dosya" if self.dosya else "Genel"

    def dosya_uyar_mi(self, dosya_adi: str) -> bool:
        return self.dosya is None or norm_ad(self.dosya) == norm_ad(dosya_adi)

    def sayfa_uyar_mi(self, sayfa_adi: str) -> bool:
        return self.sayfa is None or norm_ad(self.sayfa) == norm_ad(sayfa_adi)


KURALLAR: list[Kural] = []


def kural(id: str, baslik: str, *, dosya: str = None, sayfa: str = None,
          aktif: bool = True, varsayim: str = ""):
    if sayfa and not dosya:
        raise ValueError(f"Madde {id}: sayfa belirtmek için dosya da belirtilmeli.")

    def kaydet(fn):
        if any(k.id == id for k in KURALLAR):
            raise ValueError(f"Madde {id} birden fazla kez tanımlanmış.")
        KURALLAR.append(Kural(id, baslik, fn, dosya, sayfa, aktif, varsayim))
        KURALLAR.sort(key=lambda k: madde_sirasi(k.id))
        return fn
    return kaydet
