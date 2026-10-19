"""MADDE 2 - 'Ana kontrol karakteristikleri.xlsx' (sayfalar: Nicel, Nitel)."""
from cekirdek.kayit import kural
from cekirdek.yardimcilar import sayi
from ._ortak import (eslesiz_kontrol, referansta_var_kontrol, tek_x_kontrol,
                     turkce_harf_kontrol, uzunluk_kontrol)

DOSYA = "Ana kontrol karakteristikleri"


# ============================ NİCEL SAYFASI (2.1.x) ============================
# 2.1.1: ilk satır başlık -> ayarlar.py (varsayılan 1)

@kural("2.1.2", "Nicel: A ve B kolonu birlikte eşsiz olmalı", dosya=DOSYA, sayfa="Nicel")
def madde_2_1_2(ctx):
    eslesiz_kontrol(ctx, ["A", "B"])


@kural("2.1.3", "Nicel: Maksimum karakter sınırları (B=8, D=40, E=40, F=40)", dosya=DOSYA, sayfa="Nicel")
def madde_2_1_3(ctx):
    uzunluk_kontrol(ctx, {"B": 8, "D": 40, "E": 40, "F": 40})


@kural("2.1.4", "Nicel: B kolonunda Türkçe karakter (Ğ,Ü,Ş,İ,Ö,Ç) olamaz", dosya=DOSYA, sayfa="Nicel",
       varsayim="Dokümandaki büyük harflere ek olarak küçük karşılıkları (ğ,ü,ş,ö,ç,ı) da yanlış sayılır.")
def madde_2_1_4(ctx):
    turkce_harf_kontrol(ctx, ["B"])


@kural("2.1.5", "Nicel: K ve L kolonlarından yalnızca biri 'X' olmalı", dosya=DOSYA, sayfa="Nicel")
def madde_2_1_5(ctx):
    tek_x_kontrol(ctx, ["K", "L"])


@kural("2.1.6", "Nicel: M ve N kolonlarından yalnızca biri 'X' olmalı", dosya=DOSYA, sayfa="Nicel")
def madde_2_1_6(ctx):
    tek_x_kontrol(ctx, ["M", "N"])


@kural("2.1.7", "Nicel: O, P, Q ve R kolonlarından yalnızca biri 'X' olmalı", dosya=DOSYA, sayfa="Nicel")
def madde_2_1_7(ctx):
    tek_x_kontrol(ctx, ["O", "P", "Q", "R"])


@kural("2.1.8", "Nicel: S, T ve U kolonlarından yalnızca biri 'X' olmalı", dosya=DOSYA, sayfa="Nicel")
def madde_2_1_8(ctx):
    tek_x_kontrol(ctx, ["S", "T", "U"])


@kural("2.1.9", "Nicel: W ve X kolonlarından yalnızca biri 'X' olmalı", dosya=DOSYA, sayfa="Nicel")
def madde_2_1_9(ctx):
    tek_x_kontrol(ctx, ["W", "X"])


@kural("2.1.10", "Nicel: Z (ölçü birimi) 'Ölçü birimleri' dosyasının A kolonunda olmalı", dosya=DOSYA, sayfa="Nicel")
def madde_2_1_10(ctx):
    referansta_var_kontrol(ctx, "Z", "Ölçü birimleri", "A")


@kural("2.1.11", "Nicel: AA (alt tolerans değeri) girildiyse G kolonu 'X' olmalı", dosya=DOSYA, sayfa="Nicel")
def madde_2_1_11(ctx):
    for s in ctx.satirlar:
        if s.dolu("AA") and not s.x("G"):
            ctx.hata(s, "AA / G", "AA kolonunda alt tolerans değeri girilmiş ancak G kolonu 'X' değil.", s.metin("AA"))


@kural("2.1.12", "Nicel: AB (üst sınır değer) girildiyse H kolonu 'X' olmalı", dosya=DOSYA, sayfa="Nicel")
def madde_2_1_12(ctx):
    for s in ctx.satirlar:
        if s.dolu("AB") and not s.x("H"):
            ctx.hata(s, "AB / H", "AB kolonunda üst sınır değer girilmiş ancak H kolonu 'X' değil.", s.metin("AB"))


@kural("2.1.13", "Nicel: AC (hedef değer) girildiyse I kolonu 'X' olmalı", dosya=DOSYA, sayfa="Nicel",
       varsayim="Dokümanda AC için de 'Üst sınır değer' yazıyor; başlıkta 'Hedef değer' olduğu için hedef değer kabul edildi.")
def madde_2_1_13(ctx):
    for s in ctx.satirlar:
        if s.dolu("AC") and not s.x("I"):
            ctx.hata(s, "AC / I", "AC kolonunda hedef değer girilmiş ancak I kolonu 'X' değil.", s.metin("AC"))


@kural("2.1.14", "Nicel: Girilen değerlerde AB (üst) > AC (hedef) > AA (alt) olmalı", dosya=DOSYA, sayfa="Nicel",
       varsayim="Yalnızca dolu olan değerler karşılaştırılır; eşitlik de yanlış sayılır (kesin büyük olmalı).")
def madde_2_1_14(ctx):
    for s in ctx.satirlar:
        dolu_kolonlar = [k for k in ("AA", "AB", "AC") if s.dolu(k)]
        if not dolu_kolonlar:
            continue
        sayilar = {k: s.sayi(k) for k in dolu_kolonlar}
        sayisal_degil = [k for k, v in sayilar.items() if v is None]
        if sayisal_degil:
            ctx.hata(s, ", ".join(sayisal_degil), "Tolerans kolonlarında sayısal olmayan değer var.",
                     " | ".join(s.metin(k) for k in sayisal_degil))
            continue
        ozet = f"AA={s.metin('AA') or '-'}, AB={s.metin('AB') or '-'}, AC={s.metin('AC') or '-'}"
        for buyuk, kucuk in (("AB", "AC"), ("AC", "AA"), ("AB", "AA")):
            if buyuk in sayilar and kucuk in sayilar and not sayilar[buyuk] > sayilar[kucuk]:
                ctx.hata(s, f"{buyuk} / {kucuk}", f"{buyuk} değeri {kucuk} değerinden büyük olmalı.", ozet)


@kural("2.1.15", "Nicel: B kolonundaki karakteristik 'Nitel' sayfasının B kolonunda da bulunmamalı",
       dosya=DOSYA, sayfa="Nicel")
def madde_2_1_15(ctx):
    nitel = ctx.referans_sayfa(DOSYA, "Nitel")
    nitel_satirlari = {}
    for n in nitel.satirlar:
        if n.dolu("B"):
            nitel_satirlari.setdefault(n.metin("B"), []).append(n.n)
    for s in ctx.satirlar:
        m = s.metin("B")
        if m in nitel_satirlari:
            satirlar = ", ".join(map(str, nitel_satirlari[m]))
            ctx.hata(s, "B", f"Aynı ana kontrol karakteristiği 'Nitel' sayfasında da var (Nitel satır {satirlar}).", m)


# ============================ NİTEL SAYFASI (2.2.x) ============================
# 2.2.1: ilk satır başlık -> ayarlar.py (varsayılan 1)

@kural("2.2.2", "Nitel: A ve B kolonu birlikte eşsiz olmalı", dosya=DOSYA, sayfa="Nitel")
def madde_2_2_2(ctx):
    eslesiz_kontrol(ctx, ["A", "B"])


@kural("2.2.3", "Nitel: Maksimum karakter sınırları (B=8, D=40, E=40, F=40)", dosya=DOSYA, sayfa="Nitel")
def madde_2_2_3(ctx):
    uzunluk_kontrol(ctx, {"B": 8, "D": 40, "E": 40, "F": 40})


@kural("2.2.4", "Nitel: B kolonunda Türkçe karakter (Ğ,Ü,Ş,İ,Ö,Ç) olamaz", dosya=DOSYA, sayfa="Nitel",
       varsayim="Dokümandaki büyük harflere ek olarak küçük karşılıkları (ğ,ü,ş,ö,ç,ı) da yanlış sayılır.")
def madde_2_2_4(ctx):
    turkce_harf_kontrol(ctx, ["B"])


@kural("2.2.5", "Nitel: H ve I kolonlarından yalnızca biri 'X' olmalı", dosya=DOSYA, sayfa="Nitel")
def madde_2_2_5(ctx):
    tek_x_kontrol(ctx, ["H", "I"])


@kural("2.2.6", "Nitel: J ve K kolonlarından yalnızca biri 'X' olmalı", dosya=DOSYA, sayfa="Nitel")
def madde_2_2_6(ctx):
    tek_x_kontrol(ctx, ["J", "K"])


@kural("2.2.7", "Nitel: L, M, N ve O kolonlarından yalnızca biri 'X' olmalı", dosya=DOSYA, sayfa="Nitel")
def madde_2_2_7(ctx):
    tek_x_kontrol(ctx, ["L", "M", "N", "O"])


@kural("2.2.8", "Nitel: P, Q ve R kolonlarından yalnızca biri 'X' olmalı", dosya=DOSYA, sayfa="Nitel")
def madde_2_2_8(ctx):
    tek_x_kontrol(ctx, ["P", "Q", "R"])


@kural("2.2.9", "Nitel: T (seçim kümesi), 'Hata kodları ve seçim kümeleri' D kolonunda (A=1 satırlar) olmalı",
       dosya=DOSYA, sayfa="Nitel",
       varsayim="T boşsa kontrol edilmez. Hata kodları dosyasının tüm sayfaları taranır.")
def madde_2_2_9(ctx):
    gecerli = set()
    for sayfa in ctx.referans_sayfalar("Hata kodları ve seçim kümeleri"):
        for r in sayfa.satirlar:
            if r.metin("A") == "1" and r.dolu("D"):
                gecerli.add(r.metin("D"))
    for s in ctx.satirlar:
        m = s.metin("T")
        if m and m not in gecerli:
            ctx.hata(s, "T", "T kolonundaki seçim kümesi 'Hata kodları ve seçim kümeleri' dosyasında "
                             "(A=1 olan satırların D kolonunda) yok.", m)
