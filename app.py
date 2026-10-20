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

with st.expander("Tanımlı kurallar"):
    kurallar = kurallari_yukle()
    st.dataframe(pd.DataFrame([{
        "Madde": k.id, "Kapsam": k.kapsam, "Dosya": k.dosya or "Tümü", "Sayfa": k.sayfa or "Tümü",
        "Kural": k.baslik, "Durum": "Aktif" if k.aktif else "Pasif"} for k in kurallar]),
        width="stretch", hide_index=True)

dosyalar = st.file_uploader("Excel dosyalarını yükleyin (tümünü birlikte seçebilirsiniz)",
                            type=["xlsx"], accept_multiple_files=True)

if st.button("Kontrolü çalıştır", type="primary", disabled=not dosyalar):
    with st.spinner("Kontrol ediliyor..."):
        sonuc = calistir([(f.name, f.getvalue()) for f in dosyalar])
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
