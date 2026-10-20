"""MADDE 5 - 'Kalite görünümü.xlsx' ('Kontrol türü' sayfası bilgi sayfasıdır, kontrol edilmez)."""
from cekirdek.kayit import kural
from ._ortak import referansta_var_kontrol

DOSYA = "Kalite görünümü"


@kural("5.1", "B (malzeme numarası) dolu ise 'Kontrol planı' dosyasındaki 'Kontrol planı' sayfasının C kolonunda olmalı", dosya=DOSYA)
def madde_5_1(ctx):
    referansta_var_kontrol(ctx, "B", "Kontrol planı", "C", ref_sayfa="Kontrol planı")
