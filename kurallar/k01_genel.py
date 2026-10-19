"""MADDE 1 - GENEL KURALLAR (her dosya ve her sayfa için geçerli).
Madde 1.1 (başlıklar kontrol edilmez) motor tarafından uygulanır: cekirdek/ayarlar.py ve cekirdek/veri.py.
"""
from cekirdek.kayit import kural
from cekirdek.yardimcilar import metin


@kural("1.2", "Küçük harf 'x' ile işaretlenmiş hücre olamaz (yalnızca büyük 'X' geçerli)")
def madde_1_2(ctx):
    for s in ctx.satirlar:
        for kolon, deger in s.hucreler():
            if metin(deger) == "x":
                ctx.hata(s, kolon, "Hücre küçük harf 'x' ile işaretlenmiş; büyük 'X' olmalı.", "x")
