"""Kurallarda ortak kullanılan GENEL yardımcılar (kural mantığı değil, tekrar eden mekanik işler).
Kuralın kendine özgü parametreleri (kolonlar, sınırlar, değerler) her zaman kuralın kendi fonksiyonundadır."""
from collections import Counter, defaultdict

# Madde 2.1.4 / 2.2.4 / 3.3 : yasak Türkçe karakterler.
# Dokümandaki büyük harfler + küçük karşılıkları (ğ ü ş ö ç ı). 'i' ASCII olduğu için küçük 'İ' ayrıca aranmaz.
TURKCE_HARFLER = set("ĞÜŞİÖÇ" + "ğüşöçı")


def uzunluk_kontrol(ctx, sinirlar: dict):
    """sinirlar: {'B': 8, 'D': 40}"""
    for s in ctx.satirlar:
        for kolon, maks in sinirlar.items():
            m = s.metin(kolon)
            if len(m) > maks:
                ctx.hata(s, kolon, f"{kolon} kolonu en fazla {maks} karakter olabilir; "
                                   f"değer {len(m)} karakter.", m)


def turkce_harf_kontrol(ctx, kolonlar):
    for s in ctx.satirlar:
        for kolon in kolonlar:
            m = s.metin(kolon)
            bulunan = sorted({c for c in m if c in TURKCE_HARFLER})
            if bulunan:
                ctx.hata(s, kolon, f"{kolon} kolonunda Türkçe karakter var: {', '.join(bulunan)}", m)


def tek_x_kontrol(ctx, kolonlar):
    """Verilen kolonlardan TAM OLARAK biri 'X' olmalı."""
    for s in ctx.satirlar:
        isaretli = [k for k in kolonlar if s.x(k)]
        liste = ", ".join(kolonlar)
        if len(isaretli) == 0:
            ctx.hata(s, liste, f"{liste} kolonlarından hiçbiri 'X' ile işaretlenmemiş; biri işaretlenmeli.")
        elif len(isaretli) > 1:
            ctx.hata(s, ", ".join(isaretli),
                     f"{liste} kolonlarından birden fazlası 'X' ile işaretlenmiş "
                     f"({', '.join(isaretli)}); yalnızca biri işaretlenmeli.")


def eslesiz_kontrol(ctx, kolonlar):
    """Verilen kolonların birleşimi sayfada tek olmalı (tekrar eden satırların hepsi raporlanır)."""
    gruplar = defaultdict(list)
    for s in ctx.satirlar:
        anahtar = tuple(s.metin(k) for k in kolonlar)
        if any(anahtar):
            gruplar[anahtar].append(s)
    liste = " + ".join(kolonlar)
    for anahtar, satirlar in gruplar.items():
        if len(satirlar) > 1:
            for s in satirlar:
                digerleri = ", ".join(str(x.n) for x in satirlar if x is not s)
                ctx.hata(s, ", ".join(kolonlar),
                         f"{liste} birlikte eşsiz olmalı; aynı değer diğer satırlarda da var (satır {digerleri}).",
                         " | ".join(anahtar))


def referansta_var_kontrol(ctx, kolon, ref_dosya, ref_kolon, ref_sayfa=None):
    """kolon doluysa değeri, ref dosyadaki ref_kolon değerleri arasında olmalı."""
    gecerli = ctx.referans_degerleri(ref_dosya, ref_kolon, ref_sayfa)
    yer = f"'{ref_dosya}'" + (f" / '{ref_sayfa}'" if ref_sayfa else "")
    for s in ctx.satirlar:
        m = s.metin(kolon)
        if m and m not in gecerli:
            ctx.hata(s, kolon, f"{kolon} kolonundaki değer {yer} dosyasının {ref_kolon} kolonunda yok.", m)


def ayni_anahtar_ayni_deger_kontrol(ctx, anahtar_kolonlar, deger_kolonlar):
    """Aynı anahtar kolonlarına sahip satırlarda, deger_kolonlarının her biri tek bir değer olmalı."""
    gruplar = defaultdict(list)
    for s in ctx.satirlar:
        anahtar = tuple(s.metin(k) for k in anahtar_kolonlar)
        if all(anahtar):
            gruplar[anahtar].append(s)
    akl = " + ".join(anahtar_kolonlar)
    for anahtar, satirlar in gruplar.items():
        for dk in deger_kolonlar:
            sayac = Counter(s.metin(dk) for s in satirlar)
            if len(sayac) <= 1:
                continue
            referans = sayac.most_common(1)[0][0]        # en sık geçen değer 'doğru' kabul edilir
            ozet = "; ".join(f"'{v or 'boş'}' (satır {', '.join(str(s.n) for s in satirlar if s.metin(dk) == v)})"
                             for v in sayac)
            for s in satirlar:
                if s.metin(dk) != referans:
                    ctx.hata(s, dk, f"Aynı {akl} ({' | '.join(anahtar)}) için {dk} kolonunda farklı değerler var: "
                                    f"{ozet}.", s.metin(dk))
