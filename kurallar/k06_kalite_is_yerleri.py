"""MADDE 6 - 'Kalite iş yerleri.xlsx'."""
from cekirdek.kayit import kural
from ._ortak import eslesiz_kontrol, uzunluk_kontrol

DOSYA = "Kalite iş yerleri"


# 6.1: ilk satır başlık -> ayarlar.py

@kural("6.2", "B ve C kolonu birlikte eşsiz olmalı", dosya=DOSYA)
def madde_6_2(ctx):
    eslesiz_kontrol(ctx, ["B", "C"])


@kural("6.3", "Maksimum karakter sınırları (C=8, D=40)", dosya=DOSYA)
def madde_6_3(ctx):
    uzunluk_kontrol(ctx, {"C": 8, "D": 40})
