"""MADDE 5 - 'Kalite görünümü.xlsx'."""
from cekirdek.kayit import kural

DOSYA = "Kalite görünümü"


@kural("5.1", "B (malzeme numarası) dolu ise 'Kontrol planı' dosyasında 'Kontrol planı' sayfası C kolonunda "
              "veya 'Çoklu malzeme tayini' sayfası C kolonunda bulunmalı", dosya=DOSYA)
def madde_5_1(ctx):
    plan_c = ctx.referans_degerleri("Kontrol planı", "C", "Kontrol planı")
    coklu_c = ctx.referans_degerleri("Kontrol planı", "C", "Çoklu malzeme tayini")
    for s in ctx.satirlar:
        m = s.metin("B")
        if m and m not in plan_c and m not in coklu_c:
            ctx.hata(s, "B", "B kolonundaki malzeme 'Kontrol planı' dosyasında hem 'Kontrol planı' sayfasının C "
                             "kolonunda hem de 'Çoklu malzeme tayini' sayfasının C kolonunda yok.", m)
