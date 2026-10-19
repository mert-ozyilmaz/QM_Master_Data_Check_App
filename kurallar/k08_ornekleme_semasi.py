"""MADDE 8 - 'Örnekleme şeması.xlsx'."""
from cekirdek.kayit import kural
from ._ortak import uzunluk_kontrol

DOSYA = "Örnekleme şeması"


# 8.1: ilk satır başlık -> ayarlar.py

@kural("8.2", "Maksimum karakter sınırları (A=3, B=40)", dosya=DOSYA)
def madde_8_2(ctx):
    uzunluk_kontrol(ctx, {"A": 3, "B": 40})


@kural("8.3", "A, B ve C dolu ise D ve E kolonları da dolu olmalı", dosya=DOSYA)
def madde_8_3(ctx):
    for s in ctx.satirlar:
        if s.dolu("A") and s.dolu("B") and s.dolu("C"):
            bos = [k for k in ("D", "E") if not s.dolu(k)]
            if bos:
                ctx.hata(s, ", ".join(bos), f"A, B ve C dolu olduğu halde {', '.join(bos)} kolonu boş.")
