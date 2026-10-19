"""MADDE 9 - 'Örnekleme yöntemi.xlsx' (ilk 2 satır başlık; tüm sayfalar)."""
from collections import defaultdict

from cekirdek.kayit import kural
from ._ortak import uzunluk_kontrol

DOSYA = "Örnekleme yöntemi"


# 9.1: ilk iki satır başlık -> ayarlar.py

@kural("9.2", "Maksimum karakter sınırları (A=8, B=40)", dosya=DOSYA)
def madde_9_2(ctx):
    uzunluk_kontrol(ctx, {"A": 8, "B": 40})


@kural("9.3", "C, D, E kolonları yalnızca izin verilen değerleri alabilir", dosya=DOSYA,
       varsayim="Boş hücre de geçersiz sayılır. İstenmezse BOS_HATA = False yapın.")
def madde_9_3(ctx):
    BOS_HATA = True
    izinli = {"C": ["1", "2", "3"],
              "D": ["100", "200", "300", "400"],
              "E": ["100", "400", "500", "700"]}
    for s in ctx.satirlar:
        for kolon, degerler in izinli.items():
            m = s.metin(kolon)
            if m == "" and not BOS_HATA:
                continue
            if m not in degerler:
                ctx.hata(s, kolon, f"{kolon} kolonu yalnızca {', '.join(degerler)} olabilir"
                                   + (" (boş bırakılamaz)." if m == "" else "."), m)


@kural("9.4", "D=100 ise F (örnekleme kapsamı) dolu olmalı", dosya=DOSYA)
def madde_9_4(ctx):
    for s in ctx.satirlar:
        if s.metin("D") == "100" and not s.dolu("F"):
            ctx.hata(s, "D / F", "Örnekleme türü 100 (sabit örnekleme) iken F kolonu boş.", s.metin("D"))


@kural("9.5", "D=400 ise I (örnek kapsamı %) dolu olmalı", dosya=DOSYA)
def madde_9_5(ctx):
    for s in ctx.satirlar:
        if s.metin("D") == "400" and not s.dolu("I"):
            ctx.hata(s, "D / I", "Örnekleme türü 400 (yüzde temelinde) iken I kolonu boş.", s.metin("D"))


@kural("9.6", "D=300 ise H dolu olmalı ve 'Örnekleme şeması' dosyasının A kolonunda bulunmalı", dosya=DOSYA)
def madde_9_6(ctx):
    sema_listesi = None
    for s in ctx.satirlar:
        if s.metin("D") != "300":
            continue
        if not s.dolu("H"):
            ctx.hata(s, "D / H", "Örnekleme türü 300 (örnekleme şeması) iken H kolonu boş.", s.metin("D"))
            continue
        if sema_listesi is None:                       # referans yoksa ReferansYok fırlatılır
            sema_listesi = ctx.referans_degerleri("Örnekleme şeması", "A")
        if s.metin("H") not in sema_listesi:
            ctx.hata(s, "H", "H kolonundaki örnekleme şeması 'Örnekleme şeması' dosyasının A kolonunda yok.",
                     s.metin("H"))


@kural("9.7", "D=200 ise F, H ve I kolonları boş olmalı", dosya=DOSYA)
def madde_9_7(ctx):
    for s in ctx.satirlar:
        if s.metin("D") == "200":
            dolu_olanlar = [k for k in ("F", "H", "I") if s.dolu(k)]
            if dolu_olanlar:
                ctx.hata(s, ", ".join(dolu_olanlar),
                         f"Örnekleme türü 200 (%100 kontrol) iken {', '.join(dolu_olanlar)} kolonu dolu; boş olmalı.",
                         " | ".join(s.metin(k) for k in dolu_olanlar))


@kural("9.8", "F ve G dolu ise F değeri G değerinden büyük olmalı", dosya=DOSYA,
       varsayim="Eşitlik de yanlış sayılır (F kesin büyük olmalı).")
def madde_9_8(ctx):
    for s in ctx.satirlar:
        if s.dolu("F") and s.dolu("G"):
            f, g = s.sayi("F"), s.sayi("G")
            if f is None or g is None:
                ctx.hata(s, "F / G", "F veya G sayısal bir değer değil.", f"F={s.metin('F')}, G={s.metin('G')}")
            elif not f > g:
                ctx.hata(s, "F / G", "F (örnekleme kapsamı) G (kabul sayısı) değerinden büyük olmalı.",
                         f"F={s.metin('F')}, G={s.metin('G')}")


@kural("9.9", "I ve J dolu ise I değeri J değerinden büyük olmalı", dosya=DOSYA,
       varsayim="Eşitlik de yanlış sayılır (I kesin büyük olmalı).")
def madde_9_9(ctx):
    for s in ctx.satirlar:
        if s.dolu("I") and s.dolu("J"):
            i, j = s.sayi("I"), s.sayi("J")
            if i is None or j is None:
                ctx.hata(s, "I / J", "I veya J sayısal bir değer değil.", f"I={s.metin('I')}, J={s.metin('J')}")
            elif not i > j:
                ctx.hata(s, "I / J", "I (örnek kapsamı %) J (kabul sayısı %) değerinden büyük olmalı.",
                         f"I={s.metin('I')}, J={s.metin('J')}")


@kural("9.10", "A kolonundaki değer sayfada tek olmalı (tekrar edemez)", dosya=DOSYA,
       varsayim="Eşsizlik her sayfa kendi içinde kontrol edilir.")
def madde_9_10(ctx):
    gruplar = defaultdict(list)
    for s in ctx.satirlar:
        if s.dolu("A"):
            gruplar[s.metin("A")].append(s)
    for deger, satirlar in gruplar.items():
        if len(satirlar) > 1:
            for s in satirlar:
                digerleri = ", ".join(str(x.n) for x in satirlar if x is not s)
                ctx.hata(s, "A", f"A kolonundaki değer birden fazla satırda geçiyor (satır {digerleri}).", deger)
