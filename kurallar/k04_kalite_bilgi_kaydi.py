"""MADDE 4 - 'Kalite bilgi kaydı.xlsx'  (Dokümanda henüz kural tanımlı değil.)

Yeni kural eklemek için örnek:

    from cekirdek.kayit import kural
    DOSYA = "Kalite bilgi kaydı"

    @kural("4.1", "Kural açıklaması", dosya=DOSYA)          # tüm sayfalar
    @kural("4.1", "Kural açıklaması", dosya=DOSYA, sayfa="AB FOOD")   # sadece bir sayfa
    def madde_4_1(ctx):
        for s in ctx.satirlar:
            if ...:
                ctx.hata(s, "A", "Hata mesajı", s.metin("A"))
"""
