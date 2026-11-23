"""Kodda tanımlı kuralların güncel listesini Word dosyası olarak üretir.

Kullanım:   python kural_listesi.py
Çıktı:      QM_Kural_Listesi.docx
Liste doğrudan kural kayıt sisteminden (kurallar/ klasörü) üretildiği için her zaman güncel koddur.
"""
from datetime import datetime
from io import BytesIO

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.shared import Cm, Pt

from cekirdek import ayarlar
from cekirdek.motor import kurallari_yukle
from cekirdek.rapor import _tablo
from cekirdek.yardimcilar import madde_sirasi, norm_ad


def kural_listesi_olustur() -> bytes:
    kurallar = sorted(kurallari_yukle(), key=lambda k: madde_sirasi(k.id))
    doc = Document()
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
    for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, m, Cm(1.5))
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(10)

    doc.add_heading("QM Ana Veri Kontrol Programı - Güncel Kural Listesi", 0)
    aktif = [k for k in kurallar if k.aktif]
    doc.add_paragraph(f"Tarih: {datetime.now():%d.%m.%Y %H:%M}    |    Aktif kural sayısı: {len(aktif)}"
                      f"    |    Pasif kural sayısı: {len(kurallar) - len(aktif)}")
    doc.add_paragraph("Kapsam: Genel = her dosya ve sayfa; Dosya = ilgili dosyanın tüm sayfaları; "
                      "Sayfa = yalnızca belirtilen sayfa. Başlık satırları hiçbir kuralda kontrol edilmez.")

    genel = [k for k in kurallar if k.dosya is None]
    doc.add_heading("Genel kurallar", 1)
    _tablo(doc, ["Madde", "Kural", "Not"], [(k.id, k.baslik, k.varsayim) for k in genel], [2, 15, 9.7])

    for dosya in ayarlar.DOSYA_ADLARI:
        liste = [k for k in kurallar if k.dosya and norm_ad(k.dosya) == norm_ad(dosya)]
        doc.add_heading(f"{dosya}.xlsx", 1)
        doc.add_paragraph(f"Başlık satırı sayısı: {ayarlar.baslik_satiri_sayisi(dosya, '')}")
        if not liste:
            doc.add_paragraph("Bu dosya için tanımlı kural yok.")
            continue
        _tablo(doc, ["Madde", "Kapsam", "Sayfa", "Durum", "Kural", "Not"],
               [(k.id, k.kapsam, k.sayfa or "Tüm sayfalar", "Aktif" if k.aktif else "Pasif", k.baslik, k.varsayim)
                for k in liste],
               [1.7, 1.6, 2.8, 1.4, 11, 8.2])

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()


if __name__ == "__main__":
    with open("QM_Kural_Listesi.docx", "wb") as f:
        f.write(kural_listesi_olustur())
    print("QM_Kural_Listesi.docx oluşturuldu.")
