# QM Ana Veri Kontrol Programı

Müşteriden gelen Excel şablonlarını `QM Master Data Rules` kurallarına göre kontrol eder ve Word raporu üretir.

## Çalıştırma
```
pip install -r requirements.txt
streamlit run app.py
```
GitHub + Streamlit Community Cloud: repoyu yükleyin, ana dosya olarak `app.py` seçin.

## Yapı
- `app.py` – Streamlit arayüzü
- `cekirdek/ayarlar.py` – dosya adları, başlık satırı sayıları, bilgi sayfaları
- `cekirdek/motor.py` – kuralları dosya/sayfalara uygular
- `cekirdek/rapor.py` – Word raporu
- `kurallar/` – **her madde için ayrı fonksiyon** (`k01_genel.py`, `k02_...`, …)

## Kural ekleme / değiştirme
Her kural `@kural(...)` ile işaretli ayrı bir fonksiyondur; değişiklik sadece o fonksiyonda yapılır.

```python
@kural("9.11", "Açıklama", dosya="Örnekleme yöntemi", sayfa="Sayfa1")
def madde_9_11(ctx):
    for s in ctx.satirlar:                       # başlıklar hariç, dolu satırlar
        if s.dolu("A") and ...:
            ctx.hata(s, "A", "Hata mesajı", s.metin("A"))
```
Kapsam parametrelerden belirlenir: `dosya`/`sayfa` yok → **Genel**; sadece `dosya` → **Dosya**; ikisi de → **Sayfa**.
Kuralı devre dışı bırakmak için `aktif=False`; yorum/varsayım notu için `varsayim="..."` (raporda görünür).
Yeni `kurallar/*.py` dosyaları otomatik yüklenir.

Fonksiyon içinde: `s["B"]` ham değer, `s.metin("B")`, `s.dolu("B")`, `s.x("B")`, `s.sayi("B")`, `s.n` (Excel satır no),
`ctx.referans_degerleri("Dosya adı", "A", sayfa=None)` başka dosyadan değer kümesi getirir.
