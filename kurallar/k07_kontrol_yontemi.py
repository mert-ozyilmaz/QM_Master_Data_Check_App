"""MADDE 7 - 'Kontrol yöntemi.xlsx'."""
from cekirdek.kayit import kural
from ._ortak import eslesiz_kontrol, uzunluk_kontrol

DOSYA = "Kontrol yöntemi"


# 7.1: ilk satır başlık -> ayarlar.py

@kural("7.2", "A ve B kolonu birlikte eşsiz olmalı", dosya=DOSYA)
def madde_7_2(ctx):
    eslesiz_kontrol(ctx, ["A", "B"])


@kural("7.3", "Maksimum karakter sınırları (B=8, D=40, E=40, F=40)", dosya=DOSYA)
def madde_7_3(ctx):
    uzunluk_kontrol(ctx, {"B": 8, "D": 40, "E": 40, "F": 40})
