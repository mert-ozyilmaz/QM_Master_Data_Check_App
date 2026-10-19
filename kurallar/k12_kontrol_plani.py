"""MADDE 12 - 'Kontrol planı.xlsx' (sayfalar: Plan, Çoklu malzeme tayini)."""
import re

from cekirdek.kayit import kural
from ._ortak import (ayni_anahtar_ayni_deger_kontrol, referansta_var_kontrol,
                     uzunluk_kontrol)

DOSYA = "Kontrol planı"
ANA_KRKT = "Ana kontrol karakteristikleri"


# ============================ PLAN SAYFASI (12.1.x) ============================
# 12.1.1: ilk beş satır başlık -> ayarlar.py

@kural("12.1.3", "Plan: Aynı C (malzeme) satırlarında D (plan grubu) tek değer olmalı", dosya=DOSYA, sayfa="Plan")
def madde_12_1_3(ctx):
    ayni_anahtar_ayni_deger_kontrol(ctx, ["C"], ["D"])


@kural("12.1.4", "Plan: Aynı D (plan grubu) satırlarında F (kullanım) tek değer olmalı", dosya=DOSYA, sayfa="Plan")
def madde_12_1_4(ctx):
    ayni_anahtar_ayni_deger_kontrol(ctx, ["D"], ["F"])


@kural("12.1.5", "Plan: G kolonu en fazla 40 karakter olabilir", dosya=DOSYA, sayfa="Plan")
def madde_12_1_5(ctx):
    uzunluk_kontrol(ctx, {"G": 40})


@kural("12.1.6", "Plan: K (işyeri) dolu ise 'Kalite iş yerleri' dosyasının C kolonunda olmalı", dosya=DOSYA, sayfa="Plan")
def madde_12_1_6(ctx):
    referansta_var_kontrol(ctx, "K", "Kalite iş yerleri", "C")


@kural("12.1.7", "Plan: H dolu ise C (malzeme) + H (plan ölçü birimi) çifti 'Malzeme ölçü birimleri' dosyasında A + B olarak bulunmalı",
       dosya=DOSYA, sayfa="Plan")
def madde_12_1_7(ctx):
    cift_listesi = set()
    for sayfa in ctx.referans_sayfalar("Malzeme ölçü birimleri"):
        for r in sayfa.satirlar:
            cift_listesi.add((r.metin("A"), r.metin("B")))
    for s in ctx.satirlar:
        if not s.dolu("H"):
            continue
        if (s.metin("C"), s.metin("H")) not in cift_listesi:
            ctx.hata(s, "C / H", "C (malzeme) ve H (ölçü birimi) çifti 'Malzeme ölçü birimleri' dosyasının "
                                 "A ve B kolonlarında birlikte bulunamadı.", f"{s.metin('C')} | {s.metin('H')}")


@kural("12.1.8", "Plan: Aynı D (plan grubu) satırlarında G (plan tanımı) tek değer olmalı", dosya=DOSYA, sayfa="Plan")
def madde_12_1_8(ctx):
    ayni_anahtar_ayni_deger_kontrol(ctx, ["D"], ["G"])


@kural("12.1.9", "Plan: Aynı D + J satırlarında K, L, M kolonları tek değer olmalı", dosya=DOSYA, sayfa="Plan")
def madde_12_1_9(ctx):
    ayni_anahtar_ayni_deger_kontrol(ctx, ["D", "J"], ["K", "L", "M"])


@kural("12.1.10", "Plan: O (karakteristik) dolu ise Ana kontrol karakteristikleri Nicel/Nitel B kolonunda olmalı",
       dosya=DOSYA, sayfa="Plan")
def madde_12_1_10(ctx):
    gecerli = set()
    for sayfa in ("Nicel", "Nitel"):
        gecerli |= ctx.referans_degerleri(ANA_KRKT, "B", sayfa)
    for s in ctx.satirlar:
        m = s.metin("O")
        if m and m not in gecerli:
            ctx.hata(s, "O", "O kolonundaki karakteristik 'Ana kontrol karakteristikleri' dosyasının "
                             "Nicel/Nitel sayfalarındaki B kolonunda yok.", m)


@kural("12.1.11", "Plan: Aynı D + J satırlarında N (karakteristik sırası) tekrar etmemeli", dosya=DOSYA, sayfa="Plan")
def madde_12_1_11(ctx):
    gruplar = {}
    for s in ctx.satirlar:
        if s.dolu("D") and s.dolu("J") and s.dolu("N"):
            gruplar.setdefault((s.metin("D"), s.metin("J"), s.metin("N")), []).append(s)
    for (d, j, n), satirlar in gruplar.items():
        if len(satirlar) > 1:
            for s in satirlar:
                digerleri = ", ".join(str(x.n) for x in satirlar if x is not s)
                ctx.hata(s, "N", f"Aynı D ({d}) ve J ({j}) için N={n} birden fazla satırda var (satır {digerleri}).", n)


@kural("12.1.12", "Plan: R (kontrol yöntemi) dolu ise 'Kontrol yöntemi' dosyasının B kolonunda olmalı",
       dosya=DOSYA, sayfa="Plan")
def madde_12_1_12(ctx):
    referansta_var_kontrol(ctx, "R", "Kontrol yöntemi", "B")


@kural("12.1.13", "Plan: T (örnekleme yöntemi) dolu ise 'Örnekleme yöntemi' dosyasının A kolonunda olmalı",
       dosya=DOSYA, sayfa="Plan")
def madde_12_1_13(ctx):
    referansta_var_kontrol(ctx, "T", "Örnekleme yöntemi", "A")


@kural("12.1.14", "Plan: V (ölçü birimi) dolu ise 'Ölçü birimleri' dosyasının A kolonunda olmalı", dosya=DOSYA, sayfa="Plan")
def madde_12_1_14(ctx):
    referansta_var_kontrol(ctx, "V", "Ölçü birimleri", "A")


@kural("12.1.15", "Plan: W, X, Y değerleri U (ondalık basamak) kadar ondalık içermeli (ör. U=2 -> 13,52)",
       dosya=DOSYA, sayfa="Plan")
def madde_12_1_15(ctx):
    def gorunen_ondalik(s, kolon):
        v = s[kolon]
        fmt = s.bicim(kolon)
        if "." in fmt and fmt.lower() != "general":
            return len(re.findall(r"[0#?]", fmt.split(".", 1)[1].split(";")[0]))
        return len(repr(float(v)).split(".")[1].rstrip("0")) if isinstance(v, float) else 0

    for s in ctx.satirlar:
        if not s.dolu("U"):
            continue
        u = s.sayi("U")
        if u is None or u < 0 or not float(u).is_integer():
            ctx.hata(s, "U", "U (ondalık basamak) negatif olmayan bir tam sayı olmalı.", s.metin("U"))
            continue
        u = int(u)
        beklenen = "tam sayı (ondalıksız)" if u == 0 else f"{u} basamaklı ondalık (ör. 13,{'5' * u})"
        for kolon in ("W", "X", "Y"):
            if not s.dolu(kolon):
                continue
            v = s[kolon]
            if isinstance(v, str):
                desen = r"-?\d+" if u == 0 else rf"-?\d+,\d{{{u}}}"
                uygun = re.fullmatch(desen, s.metin(kolon)) is not None
            else:
                uygun = isinstance(v, (int, float)) and gorunen_ondalik(s, kolon) == u
            if not uygun:
                ctx.hata(s, kolon, f"U={u} olduğu için {kolon} değeri {beklenen} olmalı.", s.metin(kolon))


def _tolerans_isareti_kontrol(ctx, kolon, nicel_kolon, ad):
    """12.1.16-18 için ortak mantık: kolon doluysa, O'daki karakteristiğin Nicel sayfasındaki karşılığında
    nicel_kolon 'X' olmalı."""
    nicel = ctx.referans_sayfa(ANA_KRKT, "Nicel")
    eslesen = {}
    for n in nicel.satirlar:
        eslesen.setdefault(n.metin("B"), []).append(n)
    for s in ctx.satirlar:
        if not s.dolu(kolon):
            continue
        krkt = s.metin("O")
        if not krkt:
            ctx.hata(s, f"{kolon} / O", f"{kolon} kolonunda {ad} girilmiş ancak O (karakteristik) boş.", s.metin(kolon))
        elif krkt not in eslesen:
            ctx.hata(s, f"{kolon} / O", f"{kolon} kolonunda {ad} girilmiş ancak '{krkt}' karakteristiği "
                                        f"'Nicel' sayfasında yok.", s.metin(kolon))
        elif not any(n.x(nicel_kolon) for n in eslesen[krkt]):
            satirlar = ", ".join(str(n.n) for n in eslesen[krkt])
            ctx.hata(s, f"{kolon} / O", f"{kolon} kolonunda {ad} girilmiş ancak '{krkt}' karakteristiğinin "
                                        f"Nicel sayfasındaki {nicel_kolon} kolonu (satır {satirlar}) 'X' değil.",
                     s.metin(kolon))


@kural("12.1.16", "Plan: W (alt limit) dolu ise Nicel sayfasındaki eşleşen karakteristiğin G kolonu 'X' olmalı",
       dosya=DOSYA, sayfa="Plan")
def madde_12_1_16(ctx):
    _tolerans_isareti_kontrol(ctx, "W", "G", "alt limit")


@kural("12.1.17", "Plan: X (üst limit) dolu ise Nicel sayfasındaki eşleşen karakteristiğin H kolonu 'X' olmalı",
       dosya=DOSYA, sayfa="Plan")
def madde_12_1_17(ctx):
    _tolerans_isareti_kontrol(ctx, "X", "H", "üst limit")


@kural("12.1.18", "Plan: Y (hedef değer) dolu ise Nicel sayfasındaki eşleşen karakteristiğin I kolonu 'X' olmalı",
       dosya=DOSYA, sayfa="Plan")
def madde_12_1_18(ctx):
    _tolerans_isareti_kontrol(ctx, "Y", "I", "hedef değer")


@kural("12.1.19", "Plan: Z (seçim kümesi) dolu ise 'Hata kodları ve seçim kümeleri' dosyasının D kolonunda olmalı",
       dosya=DOSYA, sayfa="Plan")
def madde_12_1_19(ctx):
    referansta_var_kontrol(ctx, "Z", "Hata kodları ve seçim kümeleri", "D")


@kural("12.1.20", "Plan: D (plan grubu) aynı değerleri alt alta olmalı; değer değişince tekrar kullanılmamalı",
       dosya=DOSYA, sayfa="Plan")
def madde_12_1_20(ctx):
    biten, onceki, ilk_satir = set(), None, {}
    for s in ctx.satirlar:
        d = s.metin("D")
        if not d:
            continue
        if d != onceki:
            if d in biten:
                ctx.hata(s, "D", f"D={d} değeri daha önce (satır {ilk_satir[d]}) kullanılıp değişmiş; "
                                 f"aynı değerler alt alta olmalı.", d)
            if onceki is not None:
                biten.add(onceki)
            ilk_satir.setdefault(d, s.n)
            onceki = d


# ====================== ÇOKLU MALZEME TAYİNİ SAYFASI (12.2.x) ======================

@kural("12.2.1", "Çoklu malzeme tayini: A kolonu ile Plan sayfasındaki C kolonu karşılıklı birebir aynı değerleri içermeli",
       dosya=DOSYA, sayfa="Çoklu malzeme tayini",
       varsayim="Hem 'Çoklu' sayfasında olup Plan'da olmayanlar hem de Plan'da olup 'Çoklu' sayfasında olmayanlar raporlanır.")
def madde_12_2_1(ctx):
    plan = ctx.referans_sayfa(DOSYA, "Plan")
    plan_c = plan.kolon_degerleri("C")
    coklu_a = ctx.sayfa.kolon_degerleri("A")
    for s in ctx.satirlar:
        a = s.metin("A")
        if a and a not in plan_c:
            ctx.hata(s, "A", "A kolonundaki malzeme 'Plan' sayfasının C kolonunda yok.", a)
    for p in plan.satirlar:
        c = p.metin("C")
        if c and c not in coklu_a:
            ctx.hata(p, "C", "Bu malzeme 'Çoklu malzeme tayini' sayfasının A kolonunda yok.", c, sayfa=plan)
