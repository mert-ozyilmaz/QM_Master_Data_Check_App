"""MADDE 3 - 'Hata kodları ve seçim kümeleri.xlsx' (ilk satır başlık; tüm sayfalar)."""
from cekirdek.kayit import kural
from ._ortak import turkce_harf_kontrol, uzunluk_kontrol

DOSYA = "Hata kodları ve seçim kümeleri"


# 3.1: ilk satır başlık -> ayarlar.py

@kural("3.2", "Maksimum karakter sınırları (D=8, E=40, F=8, G=40, H=4, I=40)", dosya=DOSYA)
def madde_3_2(ctx):
    uzunluk_kontrol(ctx, {"D": 8, "E": 40, "F": 8, "G": 40, "H": 4, "I": 40})


@kural("3.3", "D ve F kolonlarında Türkçe karakter (Ğ,Ü,Ş,İ,Ö,Ç) olamaz", dosya=DOSYA)
def madde_3_3(ctx):
    turkce_harf_kontrol(ctx, ["D", "F"])


@kural("3.4", "D ve F kolonlarında '*' veya ',' işareti olamaz", dosya=DOSYA)
def madde_3_4(ctx):
    yasak = ["*", ","]
    for s in ctx.satirlar:
        for kolon in ("D", "F"):
            m = s.metin(kolon)
            bulunan = [c for c in yasak if c in m]
            if bulunan:
                ctx.hata(s, kolon, f"{kolon} kolonunda yasak özel işaret var: {' '.join(bulunan)}", m)


@kural("3.5", "J kolonu 'R' ise K kolonu (hata sınıfı) dolu olmalı", dosya=DOSYA)
def madde_3_5(ctx):
    for s in ctx.satirlar:
        if s.metin("J").upper() == "R" and not s.dolu("K"):
            ctx.hata(s, "J / K", "Kod değerlemesi 'R' (ret) olduğu halde K kolonu (Hata Sınıfı) boş.", s.metin("J"))
