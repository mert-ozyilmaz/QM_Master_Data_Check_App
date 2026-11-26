"""MADDE 12 - 'Kontrol planı.xlsx' (sayfalar: Kontrol planı, Çoklu malzeme tayini)."""
import re

from cekirdek.kayit import kural
from ._ortak import (ayni_anahtar_ayni_deger_kontrol, diger_satirlar_metni, referansta_var_kontrol,
                     turkce_harf_kontrol, uzunluk_kontrol)

DOSYA = "Kontrol planı"
PLAN = "Kontrol planı"          # dosyadaki ana plan sayfasının adı
ANA_KRKT = "Ana kontrol karakteristikleri"


# ============================ PLAN SAYFASI (12.1.x) ============================
# 12.1.1: ilk satır başlık -> ayarlar.py

@kural("12.1.4", "Plan: Aynı D (plan grubu) satırlarında F (kullanım) tek değer olmalı", dosya=DOSYA, sayfa=PLAN)
def madde_12_1_4(ctx):
    ayni_anahtar_ayni_deger_kontrol(ctx, ["D"], ["F"])


@kural("12.1.5", "Plan: G kolonu en fazla 40 karakter olabilir", dosya=DOSYA, sayfa=PLAN)
def madde_12_1_5(ctx):
    uzunluk_kontrol(ctx, {"G": 40})


@kural("12.1.6", "Plan: K (işyeri) dolu ise 'Kalite iş yerleri' dosyasının C kolonunda olmalı", dosya=DOSYA, sayfa=PLAN)
def madde_12_1_6(ctx):
    referansta_var_kontrol(ctx, "K", "Kalite iş yerleri", "C")


@kural("12.1.7", "Plan: H dolu ise C (malzeme) + H (plan ölçü birimi) çifti 'Malzeme ölçü birimleri' dosyasında A + B olarak bulunmalı",
       dosya=DOSYA, sayfa=PLAN)
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


@kural("12.1.8", "Plan: Aynı D (plan grubu) satırlarında G (plan tanımı) tek değer olmalı", dosya=DOSYA, sayfa=PLAN)
def madde_12_1_8(ctx):
    ayni_anahtar_ayni_deger_kontrol(ctx, ["D"], ["G"])


@kural("12.1.9", "Plan: Aynı D + J satırlarında K, L, M kolonları tek değer olmalı", dosya=DOSYA, sayfa=PLAN)
def madde_12_1_9(ctx):
    ayni_anahtar_ayni_deger_kontrol(ctx, ["D", "J"], ["K", "L", "M"])


@kural("12.1.10", "Plan: O (karakteristik) dolu ise Ana kontrol karakteristikleri Nicel/Nitel B kolonunda olmalı",
       dosya=DOSYA, sayfa=PLAN)
def madde_12_1_10(ctx):
    gecerli = set()
    for sayfa in ("Nicel", "Nitel"):
        gecerli |= ctx.referans_degerleri(ANA_KRKT, "B", sayfa)
    for s in ctx.satirlar:
        m = s.metin("O")
        if m and m not in gecerli:
            ctx.hata(s, "O", "O kolonundaki karakteristik 'Ana kontrol karakteristikleri' dosyasının "
                             "Nicel/Nitel sayfalarındaki B kolonunda yok.", m)


@kural("12.1.11", "Plan: Aynı D + J satırlarında N (karakteristik sırası) tekrar etmemeli", dosya=DOSYA, sayfa=PLAN)
def madde_12_1_11(ctx):
    gruplar = {}
    for s in ctx.satirlar:
        if s.dolu("D") and s.dolu("J") and s.dolu("N"):
            gruplar.setdefault((s.metin("D"), s.metin("J"), s.metin("N")), []).append(s)
    for (d, j, n), satirlar in gruplar.items():
        if len(satirlar) > 1:
            for s in satirlar:
                digerleri = diger_satirlar_metni(satirlar, s)
                ctx.hata(s, "N", f"Aynı D ({d}) ve J ({j}) için N={n} birden fazla satırda var (satır {digerleri}).", n)


@kural("12.1.12", "Plan: R (kontrol yöntemi) dolu ise 'Kontrol yöntemi' dosyasının B kolonunda olmalı",
       dosya=DOSYA, sayfa=PLAN)
def madde_12_1_12(ctx):
    referansta_var_kontrol(ctx, "R", "Kontrol yöntemi", "B")


@kural("12.1.13", "Plan: T (örnekleme yöntemi) dolu ise 'Örnekleme yöntemi' dosyasının A kolonunda olmalı",
       dosya=DOSYA, sayfa=PLAN)
def madde_12_1_13(ctx):
    referansta_var_kontrol(ctx, "T", "Örnekleme yöntemi", "A")


@kural("12.1.14", "Plan: V (ölçü birimi) dolu ise 'Ölçü birimleri' dosyasının A kolonunda olmalı", dosya=DOSYA, sayfa=PLAN)
def madde_12_1_14(ctx):
    referansta_var_kontrol(ctx, "V", "Ölçü birimleri", "A")


@kural("12.1.15", "Plan: W, X, Y değerleri U (ondalık basamak) kadar ondalık içermeli (ör. U=2 -> 13,52)",
       dosya=DOSYA, sayfa=PLAN)
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
       dosya=DOSYA, sayfa=PLAN)
def madde_12_1_16(ctx):
    _tolerans_isareti_kontrol(ctx, "W", "G", "alt limit")


@kural("12.1.17", "Plan: X (üst limit) dolu ise Nicel sayfasındaki eşleşen karakteristiğin H kolonu 'X' olmalı",
       dosya=DOSYA, sayfa=PLAN)
def madde_12_1_17(ctx):
    _tolerans_isareti_kontrol(ctx, "X", "H", "üst limit")


@kural("12.1.18", "Plan: Y (hedef değer) dolu ise Nicel sayfasındaki eşleşen karakteristiğin I kolonu 'X' olmalı",
       dosya=DOSYA, sayfa=PLAN)
def madde_12_1_18(ctx):
    _tolerans_isareti_kontrol(ctx, "Y", "I", "hedef değer")


@kural("12.1.19", "Plan: Z (seçim kümesi) dolu ise 'Hata kodları ve seçim kümeleri' dosyasının D kolonunda olmalı",
       dosya=DOSYA, sayfa=PLAN)
def madde_12_1_19(ctx):
    referansta_var_kontrol(ctx, "Z", "Hata kodları ve seçim kümeleri", "D")


@kural("12.1.20", "Plan: D (plan grubu) aynı değerleri alt alta olmalı; değer değişince tekrar kullanılmamalı",
       dosya=DOSYA, sayfa=PLAN)
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

@kural("12.2.1", "Çoklu malzeme tayini: A kolonundaki değerlerin hepsi Kontrol planı sayfası C kolonunda olmalı",
       dosya=DOSYA, sayfa="Çoklu malzeme tayini")
def madde_12_2_1(ctx):
    plan_c = ctx.referans_sayfa(DOSYA, PLAN).kolon_degerleri("C")
    for s in ctx.satirlar:
        a = s.metin("A")
        if a and a not in plan_c:
            ctx.hata(s, "A", "A kolonundaki değer 'Kontrol planı' sayfasının C kolonunda yok.", a)


@kural("12.2.2", "Çoklu malzeme tayini: A ve E kolonu çifti, Kontrol planı sayfasındaki C ve D kolonu çifti olarak bulunmalı",
       dosya=DOSYA, sayfa="Çoklu malzeme tayini",
       varsayim="A ve E'nin ikisi de boş olan satırlar atlanır; biri boşsa çift bulunamamış sayılır.")
def madde_12_2_2(ctx):
    plan_ciftleri = {(p.metin("C"), p.metin("D")) for p in ctx.referans_sayfa(DOSYA, PLAN).satirlar}
    for s in ctx.satirlar:
        a, e = s.metin("A"), s.metin("E")
        if (a or e) and (a, e) not in plan_ciftleri:
            ctx.hata(s, "A / E", "A (malzeme) ve E (plan grubu) çifti 'Kontrol planı' sayfasının C ve D "
                                 "kolonlarında birlikte bulunamadı.", f"{a} | {e}")


@kural("12.1.21", "Plan: D kolonunda Türkçe karakter (Ğ,Ü,Ş,İ,Ö,Ç) olamaz", dosya=DOSYA, sayfa=PLAN)
def madde_12_1_21(ctx):
    turkce_harf_kontrol(ctx, ["D"])


@kural("12.1.22", "Plan: C (malzeme) + F (kullanım) -> 'Plan kullanımı' sayfasındaki kontrol türü -> 'Kalite görünümü' dosyasında B (malzeme) + C (kontrol türü) eşleşmeli",
       dosya=DOSYA, sayfa=PLAN,
       varsayim="Satırdaki F değeri, 'Plan kullanımı' sayfasının C kolonunda aranır; eşleşen satır(lar)ın A kolonu (kontrol türü) alınır. "
                "Bir plan kullanımı birden fazla kontrol türüne karşılık gelebilir; herhangi biri Kalite görünümü'nde "
                "C (malzeme) = B ve kontrol türü = C olarak bulunursa doğru sayılır. C veya F boşsa satır atlanır.")
def madde_12_1_22(ctx):
    kullanim = ctx.referans_sayfa(DOSYA, "Plan kullanımı")
    kontrol_turleri = {}                      # plan kullanımı (C) -> {kontrol türü (A), ...}
    for r in kullanim.satirlar:
        if r.dolu("C") and r.dolu("A"):
            kontrol_turleri.setdefault(r.metin("C"), set()).add(r.metin("A"))
    gorunum = set()                           # (malzeme, kontrol türü) çiftleri
    for sayfa in ctx.referans_sayfalar("Kalite görünümü"):
        for r in sayfa.satirlar:
            gorunum.add((r.metin("B"), r.metin("C")))

    for s in ctx.satirlar:
        c, f = s.metin("C"), s.metin("F")
        if not c or not f:
            continue
        turler = kontrol_turleri.get(f)
        if not turler:
            ctx.hata(s, "F", f"F değeri ('{f}') 'Plan kullanımı' sayfasının C kolonunda bulunamadı.", f)
        elif not any((c, t) in gorunum for t in turler):
            ctx.hata(s, "C / F", f"Malzeme '{c}' ve kontrol türü ({', '.join(sorted(turler))}) çifti "
                                 f"'Kalite görünümü' dosyasında (B + C kolonları) bulunamadı.", f"{c} | {f}")


@kural("12.1.23", "Plan: J (operasyon) 10'un katı olmalı; D ve M önceki satırla aynı ise J aynı, D önceki satırdan farklı ise J = 10 olmalı",
       dosya=DOSYA, sayfa=PLAN,
       varsayim="D aynı ama M farklı ise J için ek bir şart aranmaz (yalnızca 10'un katı olmalı). İlk dolu satır için yalnızca "
                "10'un katı olma şartı aranır; boş J hücreleri atlanır.")
def madde_12_1_23(ctx):
    onceki = None                                   # önceki dolu J satırı
    for s in ctx.satirlar:
        if not s.dolu("J"):
            continue
        j = s.sayi("J")
        if j is None or j < 10 or j % 10 != 0:
            ctx.hata(s, "J", "J kolonundaki değer 10'un katı (10, 20, 30 ...) olmalı.", s.metin("J"))
        elif onceki is not None:
            if s.metin("D") != onceki.metin("D"):
                if j != 10:
                    ctx.hata(s, "J", f"D değeri önceki satırdan (satır {onceki.n}) farklı; yeni plan grubunun J değeri "
                                     f"10 olmalı.", s.metin("J"))
            elif s.metin("M") == onceki.metin("M"):
                if s.metin("J") != onceki.metin("J") and j != onceki.sayi("J"):
                    ctx.hata(s, "J", f"D ve M değerleri önceki satırla (satır {onceki.n}) aynı; J değeri de aynı "
                                     f"({onceki.metin('J')}) olmalı.", s.metin("J"))
        onceki = s


@kural("12.1.24", "Plan: N (karakteristik sırası) 10'un katı olmalı; J aynı ise bir sonraki satır +10, J farklı ise 10 olmalı",
       dosya=DOSYA, sayfa=PLAN,
       varsayim="Plan grubu (D) değişirse J aynı görünse bile yeni plan başladığı kabul edilir ve N'nin 10 olması beklenir "
                "(D_DEGISINCE_SIFIRLA = False yapılırsa yalnızca J'ye bakılır). İlk dolu satır için yalnızca 10'un katı "
                "olma şartı aranır; boş N hücreleri atlanır.")
def madde_12_1_24(ctx):
    D_DEGISINCE_SIFIRLA = True
    onceki = None                                   # önceki dolu N satırı
    for s in ctx.satirlar:
        if not s.dolu("N"):
            continue
        n = s.sayi("N")
        if n is None or n < 10 or n % 10 != 0:
            ctx.hata(s, "N", "N kolonundaki değer 10'un katı (10, 20, 30 ...) olmalı.", s.metin("N"))
        elif onceki is not None:
            onceki_n = onceki.sayi("N")
            if onceki_n is not None:
                ayni_j = s.metin("J") == onceki.metin("J")
                if D_DEGISINCE_SIFIRLA and s.metin("D") != onceki.metin("D"):
                    ayni_j = False
                if ayni_j:
                    if n != onceki_n + 10:
                        ctx.hata(s, "N", f"J değeri önceki satırla (satır {onceki.n}) aynı ve önceki N = {int(onceki_n)}; "
                                         f"bu satırdaki N {int(onceki_n) + 10} olmalı.", s.metin("N"))
                elif n != 10:
                    ctx.hata(s, "N", f"J değeri önceki satırdan (satır {onceki.n}) farklı; N değeri 10 olmalı.",
                             s.metin("N"))
        onceki = s


@kural("12.1.25", "Plan: Aynı D ve F kolonu için C kolonunda birden fazla farklı değer olamaz", dosya=DOSYA, sayfa=PLAN,
       varsayim="D ve F dolu olan satırlar gruplanır; C boş olan satırlar yok sayılır. Çakışan grubun tüm satırları raporlanır.")
def madde_12_1_25(ctx):
    gruplar = {}
    for s in ctx.satirlar:
        if s.dolu("D") and s.dolu("F") and s.dolu("C"):
            gruplar.setdefault((s.metin("D"), s.metin("F")), []).append(s)
    for (d, f), satirlar in gruplar.items():
        degerler = sorted({s.metin("C") for s in satirlar})
        if len(degerler) > 1:
            gosterilen = ", ".join(degerler[:5]) + (f" ... (+{len(degerler) - 5} değer daha)" if len(degerler) > 5 else "")
            for s in satirlar:
                ctx.hata(s, "C", f"Aynı D ({d}) ve F ({f}) için C kolonunda birden fazla farklı değer var: "
                                 f"{gosterilen}.", s.metin("C"))


@kural("12.1.26", "Plan: T'nin Örnekleme yöntemi dosyasındaki C değeri 3 ise I dolu, 1 ise I boş olmalı", dosya=DOSYA, sayfa=PLAN,
       varsayim="T değeri 'Örnekleme yöntemi' dosyasının A kolonunda bulunamazsa bu kuralda atlanır (12.1.13 raporlar). "
                "Aynı değer birden fazla sayfada geçerse her eşleşen C değeri ayrı ayrı değerlendirilir.")
def madde_12_1_26(ctx):
    c_degerleri = {}                                # örnekleme yöntemi (A) -> {C değerleri}
    for sayfa in ctx.referans_sayfalar("Örnekleme yöntemi"):
        for r in sayfa.satirlar:
            if r.dolu("A"):
                c_degerleri.setdefault(r.metin("A"), set()).add(r.metin("C"))
    for s in ctx.satirlar:
        t = s.metin("T")
        if not t or t not in c_degerleri:
            continue
        c = c_degerleri[t]
        if "3" in c and not s.dolu("I"):
            ctx.hata(s, "T / I", f"T ('{t}') örnekleme yönteminde C = 3 olduğu halde I kolonu boş.", t)
        if "1" in c and s.dolu("I"):
            ctx.hata(s, "T / I", f"T ('{t}') örnekleme yönteminde C = 1 olduğu halde I kolonu dolu.", s.metin("I"))
