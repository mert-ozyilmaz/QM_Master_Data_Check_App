"""Kontrol motoru: dosyaları yükler, kuralları ilgili dosya/sayfalara uygular."""
import importlib
import pkgutil
from dataclasses import dataclass, field
from datetime import datetime

import kurallar as kurallar_paketi
from . import ayarlar
from .kayit import KURALLAR, Kural, ReferansYok
from .veri import Calisma, Sayfa, dosya_yukle
from .yardimcilar import madde_sirasi, norm_ad


@dataclass
class Bulgu:
    kural_id: str
    kural_baslik: str
    kapsam: str
    dosya: str
    sayfa: str
    satir: int
    kolon: str
    deger: str
    mesaj: str


class Baglam:
    """Kural fonksiyonuna verilen nesne: sayfa verisi + bulgu ekleme + referans erişimi."""

    def __init__(self, calisma: Calisma, sayfa: Sayfa, kural: Kural, bulgular: list):
        self.calisma, self.sayfa, self.kural, self._bulgular = calisma, sayfa, kural, bulgular

    @property
    def satirlar(self):
        return self.sayfa.satirlar

    def hata(self, satir, kolon: str, mesaj: str, deger="", sayfa: Sayfa = None):
        """Bulgu ekler. Başka bir sayfadaki satır için sayfa= verilebilir."""
        hedef = sayfa or self.sayfa
        self._bulgular.append(Bulgu(
            self.kural.id, self.kural.baslik, self.kural.kapsam, hedef.dosya, hedef.ad,
            satir.n if hasattr(satir, "n") else int(satir), kolon, str(deger), mesaj))

    # ---- başka dosya/sayfalara erişim ----
    def referans_sayfalar(self, dosya: str, sayfa: str = None) -> list:
        d = self.calisma.dosya(dosya)
        if d is None:
            raise ReferansYok(f"'{dosya}' dosyası yüklenmemiş.")
        if sayfa:
            s = d.sayfa(sayfa)
            if s is None:
                raise ReferansYok(f"'{dosya}' dosyasında '{sayfa}' sayfası yok.")
            return [s]
        return [s for s in d.sayfalar if not s.bilgi]

    def referans_sayfa(self, dosya: str, sayfa: str) -> Sayfa:
        return self.referans_sayfalar(dosya, sayfa)[0]

    def referans_degerleri(self, dosya: str, kolon: str, sayfa: str = None) -> set:
        """Dosyadaki (veya verilen sayfadaki) kolonun dolu değerleri (metin olarak)."""
        degerler = set()
        for s in self.referans_sayfalar(dosya, sayfa):
            degerler |= s.kolon_degerleri(kolon)
        return degerler


@dataclass
class Sonuc:
    tarih: datetime = field(default_factory=datetime.now)
    bulgular: list = field(default_factory=list)
    kontrol_edilen: list = field(default_factory=list)   # (dosya, sayfa, satır sayısı)
    yuklenen_dosyalar: list = field(default_factory=list)   # (yüklenen ad, standart ad)
    taninmayan_dosyalar: list = field(default_factory=list)  # (yüklenen ad, neden)
    yuklenmeyen_dosyalar: list = field(default_factory=list)
    atlananlar: list = field(default_factory=list)       # (kural_id, neden)
    calisan_kurallar: list = field(default_factory=list)
    pasif_kurallar: list = field(default_factory=list)


def kurallari_yukle():
    """kurallar/ klasöründeki tüm modülleri içe aktarır (her modül kurallarını kendisi kaydeder)."""
    for m in pkgutil.iter_modules(kurallar_paketi.__path__):
        if not m.name.startswith("_"):
            importlib.import_module(f"{kurallar_paketi.__name__}.{m.name}")
    return KURALLAR


def calistir(yuklemeler) -> Sonuc:
    """yuklemeler: [(dosya_adi, bytes), ...]"""
    kurallari_yukle()
    sonuc, calisma = Sonuc(), Calisma()

    for ad, icerik in yuklemeler:
        dosya, hata = dosya_yukle(icerik, ad)
        if dosya is None:
            sonuc.taninmayan_dosyalar.append((ad, hata))
            continue
        calisma.dosyalar[norm_ad(dosya.ad)] = dosya
        sonuc.yuklenen_dosyalar.append((ad, dosya.ad))
        for s in dosya.sayfalar:
            if not s.bilgi:
                sonuc.kontrol_edilen.append((dosya.ad, s.ad, len(s.satirlar)))

    sonuc.yuklenmeyen_dosyalar = [d for d in ayarlar.DOSYA_ADLARI if calisma.dosya(d) is None]
    atlanan = {}

    for k in KURALLAR:
        if not k.aktif:
            sonuc.pasif_kurallar.append(k)
            continue
        sonuc.calisan_kurallar.append(k)
        hedefler = [d for d in calisma.dosyalar.values() if k.dosya_uyar_mi(d.ad)]
        if k.sayfa and any(d.sayfa(k.sayfa) is None for d in hedefler):
            atlanan[(k.id, "sayfa")] = f"'{k.dosya}' dosyasında '{k.sayfa}' sayfası bulunamadı."
        for d in hedefler:
            for s in d.sayfalar:
                if s.bilgi or not k.sayfa_uyar_mi(s.ad):
                    continue
                try:
                    k.fonksiyon(Baglam(calisma, s, k, sonuc.bulgular))
                except ReferansYok as e:
                    atlanan[(k.id, str(e))] = f"{d.ad} / {s.ad}: {e}"
                except Exception as e:   # tek bir kuralın hatası tüm kontrolü durdurmasın
                    atlanan[(k.id, repr(e))] = f"{d.ad} / {s.ad}: kural çalışırken hata oluştu ({e!r})"

    sonuc.atlananlar = sorted(((kid, neden) for (kid, _), neden in atlanan.items()),
                              key=lambda x: madde_sirasi(x[0]))
    sira = {norm_ad(d): i for i, d in enumerate(ayarlar.DOSYA_ADLARI)}
    sonuc.bulgular.sort(key=lambda b: (sira.get(norm_ad(b.dosya), 99), b.sayfa, b.satir,
                                       madde_sirasi(b.kural_id)))
    return sonuc
