"""Word (.docx) rapor üretimi."""
from io import BytesIO

from docx import Document
from openpyxl import Workbook
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from . import ayarlar



def _golge(hucre, renk):
    tc_pr = hucre._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), renk)
    tc_pr.append(shd)


def _baslik_tekrarla(satir):
    tr_pr = satir._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    tr_pr.append(el)


def _tablo(doc, basliklar, satirlar, genislikler_cm):
    t = doc.add_table(rows=1, cols=len(basliklar))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, b in enumerate(basliklar):
        h = t.rows[0].cells[i]
        h.text = ""
        r = h.paragraphs[0].add_run(b)
        r.bold, r.font.size, r.font.color.rgb = True, Pt(9), RGBColor(255, 255, 255)
        _golge(h, "1F3864")
    _baslik_tekrarla(t.rows[0])
    for satir in satirlar:
        cells = t.add_row().cells
        for i, v in enumerate(satir):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v))
            r.font.size = Pt(8.5)
    for row in t.rows:
        for i, w in enumerate(genislikler_cm):
            row.cells[i].width = Cm(w)
    # Word/LibreOffice'in genişlikleri uygulaması için tablo ızgarasını da ayarla
    for gc, w in zip(t._tbl.tblGrid.findall(qn("w:gridCol")), genislikler_cm):
        gc.set(qn("w:w"), str(int(Cm(w).twips)))
    return t


def _kirpma_notu(sonuc) -> str:
    kirpilan = sonuc.kirpilan_kurallar
    if not kirpilan:
        return ""
    liste = ", ".join(f"{k} ({v:,} bulgu)".replace(",", ".") for k, v in kirpilan.items())
    return (f"Bazı kurallarda çok fazla bulgu çıktığı için her kural için yalnızca ilk {ayarlar.MAKS_BULGU_KURAL:,} bulgu "
            f"kaydedilmiştir: {liste}.").replace(",", ".")


def rapor_olustur(sonuc) -> bytes:
    """Sade rapor: tek tablo (Dosya | Sayfa | Satır | Hücre | Değer | Madde | Açıklama).
    Çok fazla bulgu varsa Word'e ilk MAKS_WORD_SATIR satır yazılır; tamamı Excel raporundadır."""
    doc = Document()
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
    for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, m, Cm(1.5))
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(10)

    doc.add_heading("QM Ana Veri Kontrol Raporu", 1)
    doc.add_paragraph(f"Tarih: {sonuc.tarih:%d.%m.%Y %H:%M}    |    Toplam bulgu: {sonuc.toplam_bulgu:,}".replace(",", "."))
    if sonuc.toplam_kural and len(sonuc.calisan_kurallar) < sonuc.toplam_kural:
        doc.add_paragraph(f"Kontrol edilen kural sayısı: {len(sonuc.calisan_kurallar)} / {sonuc.toplam_kural} "
                          f"(seçilmeyen kurallar kontrol edilmedi).")
    not_ = _kirpma_notu(sonuc)
    if not_:
        doc.add_paragraph(not_)

    gosterilen = sonuc.bulgular[:ayarlar.MAKS_WORD_SATIR]
    if len(sonuc.bulgular) > len(gosterilen):
        doc.add_paragraph(f"Word raporunda ilk {len(gosterilen):,} bulgu gösterilmektedir; "
                          f"kaydedilen {len(sonuc.bulgular):,} bulgunun tamamı Excel raporundadır.".replace(",", "."))

    if not sonuc.bulgular:
        doc.add_paragraph("Hata bulunamadı.")
    else:
        _tablo(doc, ["Dosya", "Sayfa", "Satır", "Hücre", "Değer", "Madde", "Açıklama"],
               [(b.dosya, b.sayfa, b.satir, b.kolon,
                 (b.deger[:60] + "…") if len(b.deger) > 60 else b.deger,
                 b.kural_id, b.mesaj) for b in gosterilen],
               [5, 3.2, 1.4, 2.2, 3.5, 1.6, 9.8])

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()


def excel_rapor_olustur(sonuc) -> bytes:
    """Tüm kaydedilen bulguları içeren Excel raporu (akış modunda yazılır; büyük listelerde hızlı ve hafif)."""
    wb = Workbook(write_only=True)
    ozet = wb.create_sheet("Özet")
    ozet.append(["Tarih", f"{sonuc.tarih:%d.%m.%Y %H:%M}"])
    ozet.append(["Toplam bulgu", sonuc.toplam_bulgu])
    ozet.append(["Kaydedilen bulgu", len(sonuc.bulgular)])
    ozet.append([])
    ozet.append(["Madde", "Kural", "Bulgu sayısı", "Not"])
    for k in sonuc.calisan_kurallar:
        n = sonuc.bulgu_sayaclari.get(k.id, 0)
        ozet.append([k.id, k.baslik, n, f"İlk {ayarlar.MAKS_BULGU_KURAL} bulgu kaydedildi" if n > ayarlar.MAKS_BULGU_KURAL else ""])
    ws = wb.create_sheet("Bulgular")
    ws.append(["Dosya", "Sayfa", "Satır", "Hücre", "Değer", "Madde", "Açıklama"])
    for b in sonuc.bulgular:
        ws.append([b.dosya, b.sayfa, b.satir, b.kolon, b.deger, b.kural_id, b.mesaj])
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
