"""QM Ana Veri Kontrol Programı - Streamlit arayüzü.
Çalıştırma:  streamlit run app.py
"""
import io
import zipfile
from pathlib import Path

import pandas as pd
import streamlit as st

from cekirdek.motor import calistir, kurallari_yukle
from cekirdek.rapor import rapor_olustur

st.set_page_config(page_title="QM Ana Veri Kontrolü", page_icon="✅", layout="wide")
st.title("QM Ana Veri Kontrol Programı")
st.caption("Müşteriden gelen Excel şablonları, QM Master Data Rules kurallarına göre kontrol edilir.")

# ---------------- Şablonları indir ----------------
SABLON_KLASORU = Path(__file__).parent / "sablonlar"
sablonlar = sorted(SABLON_KLASORU.glob("*.xlsx")) if SABLON_KLASORU.exists() else []


@st.cache_data
def sablon_zip_olustur(yollar: tuple) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for y in yollar:
            z.write(y, arcname=Path(y).name)
    return buf.getvalue()


if sablonlar:
    st.download_button("📥 Şablonları indir (tümü, .zip)", sablon_zip_olustur(tuple(map(str, sablonlar))),
                       file_name="QM_Ana_Veri_Sablonlari.zip", mime="application/zip")
    with st.expander("Şablonları tek tek indir"):
        for y in sablonlar:
            st.download_button(y.name, y.read_bytes(), file_name=y.name, key=f"sablon_{y.name}",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("Şablon klasörü (sablonlar/) bulunamadı.")

# ---------------- Kural seçimi ----------------
kurallar = kurallari_yukle()
if "sec_surum" not in st.session_state:
    st.session_state["sec_surum"] = 0
if "sec_durum" not in st.session_state:                 # madde no -> seçili mi (varsayılan: hepsi seçili)
    st.session_state["sec_durum"] = {k.id: k.aktif for k in kurallar}


def hepsini_ayarla(deger: bool):
    st.session_state["sec_durum"] = {k.id: (deger and k.aktif) for k in kurallar}
    st.session_state["sec_surum"] += 1


def tik_degisti():
    """Tablodaki tik değişikliklerini kaydeder; tablo yeniden çizilince 'Durum' kolonu da güncellenir."""
    degisimler = st.session_state[f"kural_secimi_{st.session_state['sec_surum']}"]["edited_rows"]
    for satir_no, degisim in degisimler.items():
        if "Kontrol et" in degisim:
            k = kurallar[int(satir_no)]
            st.session_state["sec_durum"][k.id] = bool(degisim["Kontrol et"]) and k.aktif


def durum_metni(k) -> str:
    if not k.aktif:
        return "Pasif (kodda kapalı)"
    return "Aktif" if st.session_state["sec_durum"].get(k.id, True) else "Deaktif"


with st.expander("Kontrol edilecek kurallar (tiklenebilir)", expanded=False):
    b1, b2, _ = st.columns([1, 1, 6])
    b1.button("Tümünü seç", on_click=hepsini_ayarla, args=(True,))
    b2.button("Hiçbirini seçme", on_click=hepsini_ayarla, args=(False,))
    kural_df = pd.DataFrame([{
        "Kontrol et": st.session_state["sec_durum"].get(k.id, k.aktif),
        "Madde": k.id, "Kapsam": k.kapsam, "Dosya": k.dosya or "Tümü", "Sayfa": k.sayfa or "Tümü",
        "Kural": k.baslik, "Durum": durum_metni(k)} for k in kurallar])
    st.data_editor(
        kural_df, hide_index=True, width="stretch", height=450,
        key=f"kural_secimi_{st.session_state['sec_surum']}", on_change=tik_degisti,
        disabled=["Madde", "Kapsam", "Dosya", "Sayfa", "Kural", "Durum"],
        column_config={"Kontrol et": st.column_config.CheckboxColumn("Kontrol et", default=True)})
    secili_kurallar = {kid for kid, secili in st.session_state["sec_durum"].items() if secili}
    st.caption(f"Seçili kural sayısı: {len(secili_kurallar)} / {len(kurallar)}")

dosyalar = st.file_uploader("Excel dosyalarını yükleyin (tümünü birlikte seçebilirsiniz)",
                            type=["xlsx"], accept_multiple_files=True)

if dosyalar and not secili_kurallar:
    st.warning("Hiç kural seçilmedi. Kontrol için en az bir kural seçin.")

if st.button("Kontrolü çalıştır", type="primary", disabled=not dosyalar or not secili_kurallar):
    with st.spinner("Kontrol ediliyor..."):
        sonuc = calistir([(f.name, f.getvalue()) for f in dosyalar], secili_kurallar)
        st.session_state["sonuc"] = sonuc
        st.session_state["rapor"] = rapor_olustur(sonuc)

sonuc = st.session_state.get("sonuc")
if sonuc:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kontrol edilen dosya", len(sonuc.yuklenen_dosyalar))
    c2.metric("Çalışan kural", len(sonuc.calisan_kurallar))
    c3.metric("Toplam bulgu", len(sonuc.bulgular))
    c4.metric("Kontrol edilemeyen kural", len(sonuc.atlananlar))

    st.download_button("📄 Word raporunu indir", st.session_state["rapor"],
                       file_name=f"QM_Kontrol_Raporu_{sonuc.tarih:%Y%m%d_%H%M}.docx",
                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    for ad, neden in sonuc.taninmayan_dosyalar:
        st.warning(f"'{ad}' kontrol edilmedi: {neden}")
    if sonuc.yuklenmeyen_dosyalar:
        st.info("Yüklenmeyen dosyalar: " + ", ".join(sonuc.yuklenmeyen_dosyalar))
    if sonuc.atlananlar:
        with st.expander("Kontrol edilemeyen kurallar"):
            for kid, neden in sonuc.atlananlar:
                st.write(f"**Madde {kid}** – {neden}")

    if sonuc.bulgular:
        df = pd.DataFrame([{"Dosya": b.dosya, "Sayfa": b.sayfa, "Satır": b.satir, "Hücre": b.kolon,
                            "Değer": b.deger, "Madde": b.kural_id, "Açıklama": b.mesaj}
                           for b in sonuc.bulgular])
        f1, f2 = st.columns(2)
        sec_d = f1.multiselect("Dosya filtresi", sorted(df["Dosya"].unique()))
        sec_m = f2.multiselect("Madde filtresi", sorted(df["Madde"].unique()))
        if sec_d:
            df = df[df["Dosya"].isin(sec_d)]
        if sec_m:
            df = df[df["Madde"].isin(sec_m)]
        st.dataframe(df, width="stretch", hide_index=True)
    else:
        st.success("Hata bulunamadı.")
