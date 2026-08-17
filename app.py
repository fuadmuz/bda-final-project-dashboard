# -*- coding: utf-8 -*-
"""
Dashboard Analitik Kecelakaan Lalu Lintas AS (2016-2023)
Final Project - Big Data Analytics (COMP8035041)
Fuad Maulana Muzaddiq - 2602687343 - MTI 2422
"""
import json
import os

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

AKAR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(AKAR, "data")

BERKAS_WAJIB = [
    "fp_ringkasan.json", "fp_model_meta.json", "fp_model.joblib",
    "fp_agg_tahun.csv", "fp_agg_bulan.csv", "fp_agg_jam.csv", "fp_agg_hari.csv",
    "fp_agg_cuaca.csv", "fp_agg_state.csv", "fp_agg_severity.csv", "fp_agg_jam_state.csv",
    "fp_hotspot.csv", "fp_kota_lookup.csv", "fp_graph_nodes.csv", "fp_graph_edges.csv",
    "fp_graph_komunitas.csv", "fp_model_roc.csv", "fp_model_threshold.csv",
]

BIRU, TEAL, ORANYE, MERAH, ABU = "#065A82", "#1C7293", "#F98D3C", "#C62828", "#5A6B75"
SKALA = [[0.0, "#DCE9F2"], [0.35, "#7FB3D5"], [0.7, "#1C7293"], [1.0, "#0B3C55"]]

st.set_page_config(page_title="Analitik Kecelakaan Lalu Lintas AS",
                   page_icon="🚦", layout="wide")

st.markdown("""
<style>
  .block-container {padding-top: 2rem; padding-bottom: 2rem;}
  div[data-testid="stMetricValue"] {font-size: 1.9rem;}
  /* Warna teks ditetapkan eksplisit agar tetap terbaca pada tema gelap maupun terang */
  .insight {background:#EAF2F8 !important; border-left:5px solid #065A82;
            padding:0.9rem 1.1rem; border-radius:6px; margin:0.6rem 0 1.2rem 0;
            color:#1A2A33 !important; font-size:0.95rem; line-height:1.6;}
  .insight b, .insight i {color:#065A82 !important;}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Pemuatan data
# --------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def muat_csv(nama):
    return pd.read_csv(os.path.join(DATA, nama))


@st.cache_data(show_spinner=False)
def muat_json(nama):
    with open(os.path.join(DATA, nama), "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_resource(show_spinner=False)
def muat_model():
    return joblib.load(os.path.join(DATA, "fp_model.joblib"))


def periksa_data():
    """Memberi pesan yang jelas bila berkas data belum lengkap di repo."""
    ada_folder = os.path.isdir(DATA)
    isi = sorted(os.listdir(DATA)) if ada_folder else []
    kurang = [f for f in BERKAS_WAJIB if f not in isi]
    if ada_folder and not kurang:
        return

    st.error("### Berkas data belum lengkap")
    if not ada_folder:
        st.markdown(
            f"Folder **`data/`** tidak ditemukan di samping `app.py`.\n\n"
            f"Isi folder aplikasi saat ini: `{sorted(os.listdir(AKAR))}`")
    else:
        st.markdown(f"Folder `data/` ada, tetapi **{len(kurang)} berkas** belum terunggah:")
        st.code("\n".join(kurang))
        st.caption(f"Yang sudah ada ({len(isi)}): {', '.join(isi) if isi else '(kosong)'}")

    st.markdown(
        "**Cara memperbaiki di GitHub:**\n"
        "1. Buka repo → **Add file** → **Upload files**\n"
        "2. Seret **folder `data`** dari komputer (folder utuh, bukan berkasnya satu per satu)\n"
        "3. Klik **Commit changes**, lalu tunggu aplikasi ini memuat ulang sendiri\n\n"
        "Struktur yang benar di akar repo: `app.py`, `requirements.txt`, `README.md`, "
        "dan folder `data/` berisi 18 berkas.")
    st.stop()


periksa_data()
RINGKAS = muat_json("fp_ringkasan.json")
META = muat_json("fp_model_meta.json")

HARI = {1: "Minggu", 2: "Senin", 3: "Selasa", 4: "Rabu", 5: "Kamis", 6: "Jumat", 7: "Sabtu"}
BULAN = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
         7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"}
CUACA_ID = {"Clear": "Cerah", "Cloudy": "Berawan", "Rain": "Hujan", "Snow_Ice": "Salju / Es",
            "Fog_Haze": "Kabut / Asap", "Storm": "Badai", "Other": "Lainnya"}


def ribu(n):
    return f"{int(n):,}".replace(",", ".")


def persen(x, d=1):
    return f"{x*100:.{d}f}%".replace(".", ",")


def kotak_insight(judul, isi):
    st.markdown(f'<div class="insight"><b>{judul}</b><br>{isi}</div>', unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🚦 Analitik Kecelakaan Lalu Lintas AS")
    st.caption("Final Project — Big Data Analytics")
    halaman = st.radio(
        "Halaman",
        ["Ringkasan", "Kapan & Di Mana", "Model Risiko", "Jaringan Koridor"],
        label_visibility="collapsed")
    st.divider()
    st.caption(
        f"**Fuad Maulana Muzaddiq**  \n2602687343 — MTI 2422  \n"
        f"COMP8035041 Big Data Analytics  \n\n"
        f"Data: {ribu(RINGKAS['total_kejadian'])} kejadian, "
        f"{RINGKAS['jumlah_negara_bagian']} negara bagian  \n"
        f"Periode: {RINGKAS['periode']}")
    st.caption(
        "Sumber: [US Accidents (Kaggle)]"
        "(https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents) — "
        "Moosavi et al. (2019), lisensi CC BY-NC-SA 4.0.")


# ==========================================================================
# 1. RINGKASAN
# ==========================================================================
if halaman == "Ringkasan":
    st.title("Ringkasan Eksekutif")
    st.caption("Tiga temuan utama dari 7,7 juta catatan kecelakaan di Amerika Serikat, "
               "diolah dengan Apache Spark, machine learning, dan graph analytics.")

    m = RINGKAS["model"]
    g = RINGKAS["graph"]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total kejadian", ribu(RINGKAS["total_kejadian"]),
              help="Setelah pembersihan data pada Assignment I")
    k2.metric("Berdampak besar", persen(RINGKAS["proporsi_parah"]),
              help="Severity 3-4: gangguan lalu lintas berat")
    k3.metric("AUC model prediksi", str(m["auc_roc"]).replace(".", ","),
              help="Kemampuan model membedakan kejadian parah dan tidak parah")
    k4.metric("Ruas jalan kritis", ribu(g["jumlah_node"]),
              help=f"Node graph di {g['negara_bagian']} dengan minimal 20 kejadian")

    st.divider()

    kiri, kanan = st.columns([3, 2])
    with kiri:
        st.subheader("Tren kejadian per tahun")
        t = muat_csv("fp_agg_tahun.csv")
        t["ringan"] = t["jumlah"] - t["parah"]
        fig = go.Figure()
        fig.add_bar(x=t["tahun"], y=t["ringan"], name="Dampak ringan-sedang", marker_color=TEAL)
        fig.add_bar(x=t["tahun"], y=t["parah"], name="Dampak besar (Severity 3-4)",
                    marker_color=ORANYE)
        fig.update_layout(barmode="stack", height=360, margin=dict(t=10, b=10, l=10, r=10),
                          legend=dict(orientation="h", y=1.12), xaxis_title="Tahun",
                          yaxis_title="Jumlah kejadian")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Data 2023 hanya mencakup Januari–Maret sehingga tampak turun.")

    with kanan:
        st.subheader("Komposisi tingkat keparahan")
        s = muat_csv("fp_agg_severity.csv")
        s["label"] = "Severity " + s["Severity"].astype(str)
        fig = px.pie(s, values="jumlah", names="label", hole=0.45,
                     color_discrete_sequence=["#C7E9C0", "#7FB3D5", ORANYE, MERAH])
        fig.update_traces(textposition="inside", textinfo="percent")
        fig.update_layout(height=360, margin=dict(t=10, b=10, l=10, r=10),
                          legend=dict(orientation="h", y=-0.05))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Tiga insight utama")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("##### 1. Waktu dan lokasi")
        st.markdown(
            "Kejadian memuncak pada jam komuter pagi dan sore, dan terkonsentrasi di sedikit "
            "wilayah. **California** menyumbang "
            f"**{ribu(RINGKAS['negara_bagian_teratas_jumlah'])}** kejadian sendirian.")
        st.caption("→ Dasar penjadwalan patroli dan kesiagaan unit gawat darurat.")
    with c2:
        st.markdown("##### 2. Prediksi risiko")
        st.markdown(
            f"Model memisahkan kejadian parah dengan AUC **{str(m['auc_roc']).replace('.', ',')}** "
            f"dan ketepatan **{str(m['lift']).replace('.', ',')}×** lebih baik daripada tebakan acak.")
        st.caption("→ Memungkinkan triase otomatis saat laporan pertama masuk.")
    with c3:
        st.markdown("##### 3. Koridor kritis")
        st.markdown(
            f"Hanya **{g['lima_komunitas_terbesar_ruas']} ruas jalan** "
            f"(**{persen(g['lima_komunitas_terbesar_ruas']/g['jumlah_node'])}** dari jaringan) "
            f"menyumbang **{ribu(g['lima_komunitas_terbesar_kejadian'])}** kejadian.")
        st.caption("→ Prioritas investasi perbaikan infrastruktur.")

    st.info("Gunakan menu di sebelah kiri untuk menelusuri setiap insight secara interaktif.")


# ==========================================================================
# 2. KAPAN & DI MANA
# ==========================================================================
elif halaman == "Kapan & Di Mana":
    st.title("Kapan dan Di Mana Kecelakaan Terjadi")
    st.caption("Insight 1 — pola waktu dan sebaran geografis untuk perencanaan operasional.")

    hot = muat_csv("fp_hotspot.csv")
    negara = muat_csv("fp_agg_state.csv")

    f1, f2 = st.columns([2, 3])
    with f1:
        pilihan = ["Seluruh Amerika Serikat"] + negara["negara_bagian"].tolist()
        wilayah = st.selectbox("Wilayah", pilihan)
    with f2:
        min_kej = st.slider("Tampilkan sel peta dengan minimal sekian kejadian",
                            30, 2000, 100, step=10)

    h = hot if wilayah == "Seluruh Amerika Serikat" else hot[hot["negara_bagian"] == wilayah]
    h = h[h["jumlah"] >= min_kej]

    k1, k2, k3 = st.columns(3)
    k1.metric("Kejadian tercakup", ribu(h["jumlah"].sum()))
    k2.metric("Titik rawan ditampilkan", ribu(len(h)))
    k3.metric("Porsi berdampak besar",
              persen(h["parah"].sum() / max(h["jumlah"].sum(), 1)))

    st.subheader("Peta titik rawan")
    if len(h) == 0:
        st.warning("Tidak ada sel yang memenuhi filter. Turunkan ambang minimal kejadian.")
    else:
        fig = px.scatter_mapbox(
            h, lat="lat", lon="lng", size="jumlah", color="share_parah",
            color_continuous_scale="OrRd", size_max=28, zoom=3 if wilayah ==
            "Seluruh Amerika Serikat" else 5,
            hover_name="negara_bagian",
            hover_data={"jumlah": ":,", "share_parah": ":.1%", "rata_severity": True,
                        "lat": False, "lng": False},
            labels={"share_parah": "Porsi parah"})
        fig.update_layout(mapbox_style="open-street-map", height=520,
                          margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Ukuran lingkaran = jumlah kejadian. Warna makin merah = porsi kejadian "
                   "berdampak besar makin tinggi. Sel berukuran sekitar 11 km.")

    st.divider()
    kiri, kanan = st.columns(2)

    with kiri:
        st.subheader("Pola per jam")
        js = muat_csv("fp_agg_jam_state.csv")
        if wilayah != "Seluruh Amerika Serikat" and wilayah in set(js["negara_bagian"]):
            j = js[js["negara_bagian"] == wilayah][["jam", "jumlah", "parah"]]
            ket = wilayah
        else:
            j = muat_csv("fp_agg_jam.csv")
            ket = "seluruh AS"
        fig = go.Figure()
        fig.add_scatter(x=j["jam"], y=j["jumlah"], mode="lines+markers",
                        line=dict(color=BIRU, width=3), fill="tozeroy", name="Total")
        for jam in (7, 16):
            fig.add_vline(x=jam, line_dash="dash", line_color=ABU, opacity=0.6)
        fig.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10),
                          xaxis_title=f"Jam ({ket})", yaxis_title="Jumlah kejadian",
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with kanan:
        st.subheader("Pola per hari")
        d = muat_csv("fp_agg_hari.csv")
        d["hari"] = d["hari_idx"].map(HARI)
        fig = px.bar(d, x="hari", y="jumlah", color_discrete_sequence=[BIRU])
        fig.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10),
                          xaxis_title="", yaxis_title="Jumlah kejadian")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Kondisi cuaca saat kejadian")
    c = muat_csv("fp_agg_cuaca.csv")
    c["cuaca_id"] = c["cuaca"].map(CUACA_ID).fillna(c["cuaca"])
    c["porsi_parah"] = c["parah"] / c["jumlah"]
    kiri2, kanan2 = st.columns(2)
    with kiri2:
        fig = px.bar(c.sort_values("jumlah"), x="jumlah", y="cuaca_id", orientation="h",
                     color_discrete_sequence=[TEAL])
        fig.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10),
                          xaxis_title="Jumlah kejadian", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Jumlah kejadian menurut cuaca")
    with kanan2:
        fig = px.bar(c.sort_values("porsi_parah"), x="porsi_parah", y="cuaca_id",
                     orientation="h", color_discrete_sequence=[ORANYE])
        fig.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10),
                          xaxis_title="Porsi kejadian berdampak besar", yaxis_title="")
        fig.update_xaxes(tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Porsi kejadian berdampak besar menurut cuaca")

    puncak = muat_csv("fp_agg_jam.csv").sort_values("jumlah", ascending=False).head(2)["jam"].tolist()
    kotak_insight(
        "Insight 1 — paparan lebih menentukan daripada kondisi ekstrem",
        "Kejadian memuncak pada jam komuter (sekitar pukul "
        f"{min(puncak):02d}.00 dan {max(puncak):02d}.00) dan menurun tajam pada akhir pekan. "
        "Mayoritas kecelakaan justru terjadi saat cuaca cerah, karena volume lalu lintas jauh "
        "lebih besar — meskipun secara proporsi, cuaca buruk menghasilkan porsi kejadian berat "
        "yang lebih tinggi.<br><br>"
        "<i>Implikasi bisnis:</i> penempatan patroli dan kesiagaan unit gawat darurat sebaiknya "
        "dijadwalkan berdasarkan jam sibuk dan titik rawan pada peta, bukan berdasarkan prakiraan "
        "cuaca semata.")


# ==========================================================================
# 3. MODEL RISIKO
# ==========================================================================
elif halaman == "Model Risiko":
    st.title("Model Prediksi Risiko")
    st.caption("Insight 2 — hasil pemodelan machine learning dari Assignment II, "
               "dilengkapi simulator untuk menguji model secara langsung.")

    m = META["metrics"]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("AUC-ROC", str(m["auc_roc"]).replace(".", ","))
    k2.metric("AUC-PR", str(m["auc_pr"]).replace(".", ","),
              help="Dibandingkan proporsi kelas parah "
                   f"{str(m['prevalensi']).replace('.', ',')}")
    k3.metric("Peningkatan vs acak", f"{str(m['lift']).replace('.', ',')}×")
    k4.metric("Data latih", ribu(m["n_train"]))

    tab1, tab2 = st.tabs(["🎛️ Simulator prediksi", "📈 Performa model"])

    # ---------------- Simulator ----------------
    with tab1:
        st.markdown("Atur kondisi sebuah kejadian, lalu lihat perkiraan peluangnya "
                    "berdampak besar terhadap lalu lintas.")
        kota = muat_csv("fp_kota_lookup.csv")

        c1, c2, c3 = st.columns(3)
        with c1:
            nama_kota = st.selectbox(
                "Kota", kota["kota"] + " — " + kota["negara_bagian"], index=0)
            baris_kota = kota.iloc[list(kota["kota"] + " — " + kota["negara_bagian"]).index(nama_kota)]
            jam = st.slider("Jam kejadian", 0, 23, 8)
            hari_nama = st.selectbox("Hari", [HARI[i] for i in range(1, 8)], index=1)
        with c2:
            bulan_nama = st.selectbox("Bulan", [BULAN[i] for i in range(1, 13)], index=6)
            cuaca_opsi = META["cat_categories"]["f_weather"]
            cuaca = st.selectbox("Kondisi cuaca",
                                 cuaca_opsi,
                                 format_func=lambda x: CUACA_ID.get(x, x),
                                 index=cuaca_opsi.index("Clear") if "Clear" in cuaca_opsi else 0)
            malam = st.checkbox("Kondisi malam hari", value=(jam >= 19 or jam <= 5))
        with c3:
            suhu = st.slider("Suhu (°F)", -20, 120, int(META["default_num"]["Temperature(F)"]))
            jarak_pandang = st.slider("Jarak pandang (mil)", 0.0, 20.0,
                                      float(META["default_num"]["Visibility(mi)"]), step=0.5)
            angin = st.slider("Kecepatan angin (mph)", 0, 60,
                              int(META["default_num"]["Wind_Speed(mph)"]))

        st.markdown("**Karakteristik jalan di titik kejadian**")
        p1, p2, p3, p4 = st.columns(4)
        poi = {
            "f_junction": p1.checkbox("Persimpangan", value=False),
            "f_traffic_signal": p2.checkbox("Lampu lalu lintas", value=False),
            "f_crossing": p3.checkbox("Penyeberangan", value=False),
            "f_stop": p4.checkbox("Rambu berhenti", value=False),
        }

        # --- menyusun vektor fitur persis seperti saat pelatihan ---
        nilai = dict(META["default_num"])
        hari_idx = [k for k, v in HARI.items() if v == hari_nama][0]
        bulan_idx = [k for k, v in BULAN.items() if v == bulan_nama][0]
        nilai.update({
            "f_hour": jam, "f_dow": hari_idx, "f_month": bulan_idx,
            "f_weekend": 1 if hari_idx in (1, 7) else 0,
            "f_rush": 1 if (6 <= jam <= 9 or 15 <= jam <= 18) else 0,
            "f_night": 1 if malam else 0,
            "Start_Lat": float(baris_kota["lat"]), "Start_Lng": float(baris_kota["lng"]),
            "Temperature(F)": float(suhu), "Visibility(mi)": float(jarak_pandang),
            "Wind_Speed(mph)": float(angin),
        })
        for k, v in poi.items():
            if k in nilai:
                nilai[k] = int(v)
        nilai["f_poi_count"] = sum(int(nilai.get(c, 0)) for c in META["poi_features"])

        kategori_nilai = {
            "State": str(baris_kota["negara_bagian"]),
            "f_weather": cuaca,
            "Timezone": str(baris_kota["timezone"]),
        }

        vektor = []
        for f in META["features"]:
            if f in META["cat_features"]:
                daftar = META["cat_categories"][f]
                v = kategori_nilai.get(f)
                vektor.append(daftar.index(v) if v in daftar else -1)
            else:
                vektor.append(float(nilai.get(f, 0.0)))
        X = np.array([vektor], dtype=float)

        try:
            model = muat_model()
            prob = float(model.predict_proba(X)[0, 1])
        except Exception as e:
            st.error(f"Model gagal dimuat: {e}")
            st.stop()

        st.divider()
        amb = st.slider("Ambang penandaan (threshold)", 0.10, 0.90, 0.50, step=0.05,
                        help="Nilai peluang minimal agar kejadian ditandai berpotensi berdampak besar")

        h1, h2 = st.columns([2, 3])
        with h1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number={"suffix": "%", "font": {"size": 44}},
                gauge={"axis": {"range": [0, 100]},
                       "bar": {"color": BIRU},
                       "steps": [{"range": [0, 25], "color": "#E8F4EA"},
                                 {"range": [25, 50], "color": "#FDF0DC"},
                                 {"range": [50, 100], "color": "#FADBD8"}],
                       "threshold": {"line": {"color": MERAH, "width": 4},
                                     "value": amb * 100}}))
            fig.update_layout(height=280, margin=dict(t=30, b=10, l=20, r=20))
            st.plotly_chart(fig, use_container_width=True)
        with h2:
            st.markdown("#### Rekomendasi tindakan")
            if prob >= amb:
                st.error(f"**DITANDAI BERISIKO** — peluang {persen(prob)} melampaui ambang "
                         f"{persen(amb, 0)}.")
                st.markdown(
                    "- Kirim unit gawat darurat tanpa menunggu konfirmasi lapangan\n"
                    "- Aktifkan pengalihan rute pada aplikasi navigasi\n"
                    "- Siagakan rumah sakit terdekat")
            else:
                st.success(f"**PENANGANAN STANDAR** — peluang {persen(prob)} di bawah ambang "
                           f"{persen(amb, 0)}.")
                st.markdown(
                    "- Tangani mengikuti antrean prioritas biasa\n"
                    "- Pantau perkembangan laporan susulan")
            dasar = RINGKAS["proporsi_parah"]
            selisih = f"{prob / dasar:.1f}".replace(".", ",") if dasar else "-"
            st.caption(f"Sebagai pembanding, rata-rata kejadian di seluruh dataset berpeluang "
                       f"{persen(dasar)} berdampak besar. Kondisi yang Anda pilih berpeluang "
                       f"**{selisih}×** dari rata-rata tersebut.")

        kotak_insight(
            "Insight 2 — model mengubah laporan mentah menjadi keputusan prioritas",
            "Model dilatih hanya dengan informasi yang tersedia <i>pada saat kejadian dilaporkan</i> — "
            "waktu, cuaca, lokasi, dan karakteristik jalan. Kolom seperti durasi gangguan sengaja "
            "dibuang karena baru diketahui setelah kejadian selesai, sehingga model tetap dapat "
            "dipakai secara nyata.<br><br>"
            "<i>Implikasi bisnis:</i> operator pusat kendali dapat melakukan triase otomatis pada "
            "menit-menit pertama, sementara ambang penandaan diatur sesuai kapasitas sumber daya "
            "yang tersedia.")

    # ---------------- Performa ----------------
    with tab2:
        kiri, kanan = st.columns(2)
        with kiri:
            st.subheader("Kurva ROC")
            roc = muat_csv("fp_model_roc.csv")
            fig = go.Figure()
            fig.add_scatter(x=roc["fpr"], y=roc["tpr"], mode="lines",
                            line=dict(color=BIRU, width=3),
                            name=f"Model (AUC = {m['auc_roc']})")
            fig.add_scatter(x=[0, 1], y=[0, 1], mode="lines",
                            line=dict(color=ABU, dash="dash"), name="Tebakan acak")
            fig.update_layout(height=380, margin=dict(t=10, b=10, l=10, r=10),
                              xaxis_title="False Positive Rate", yaxis_title="True Positive Rate",
                              legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig, use_container_width=True)
        with kanan:
            st.subheader("Pengaruh ambang penandaan")
            thr = muat_csv("fp_model_threshold.csv")
            fig = go.Figure()
            fig.add_scatter(x=thr["threshold"], y=thr["recall"], mode="lines+markers",
                            line=dict(color=BIRU, width=3),
                            name="Recall — kejadian parah tertangkap")
            fig.add_scatter(x=thr["threshold"], y=thr["precision"], mode="lines+markers",
                            line=dict(color=ORANYE, width=3),
                            name="Precision — peringatan yang benar")
            fig.update_layout(height=380, margin=dict(t=10, b=10, l=10, r=10),
                              xaxis_title="Ambang penandaan", yaxis_title="Nilai",
                              yaxis_range=[0, 1], legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Konsekuensi operasional tiap ambang")
        t = thr.copy()
        t.columns = ["Ambang", "% kejadian ditandai", "Recall", "Precision", "F1"]
        st.dataframe(
            t, use_container_width=True, hide_index=True,
            column_config={
                "Ambang": st.column_config.NumberColumn(format="%.2f"),
                "% kejadian ditandai": st.column_config.NumberColumn(format="%.2f%%"),
                "Recall": st.column_config.ProgressColumn(
                    "Recall", help="Porsi kejadian parah yang berhasil ditandai",
                    format="%.3f", min_value=0.0, max_value=1.0),
                "Precision": st.column_config.ProgressColumn(
                    "Precision", help="Porsi peringatan yang benar",
                    format="%.3f", min_value=0.0, max_value=1.0),
                "F1": st.column_config.NumberColumn(format="%.4f"),
            })

        st.markdown(
            f"**Catatan teknis.** Model pada dashboard ini adalah "
            f"`{META['algoritma']}` yang dilatih ulang atas fitur dan target yang sama dengan "
            f"Assignment II ({META['target']}). Pelatihan berskala penuh tetap dilakukan dengan "
            "Apache Spark MLlib; versi ringan ini dipakai agar inferensi dapat berjalan seketika "
            "di dashboard tanpa memerlukan klaster Spark — pola *train big, serve small* yang "
            "lazim pada lapisan penyajian.")


# ==========================================================================
# 4. JARINGAN KORIDOR
# ==========================================================================
elif halaman == "Jaringan Koridor":
    g = RINGKAS["graph"]
    st.title("Jaringan Koridor Rawan Kecelakaan")
    st.caption(f"Insight 3 — hasil graph analytics dari Assignment II, wilayah "
               f"{g['negara_bagian']}.")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Node (ruas jalan)", ribu(g["jumlah_node"]))
    k2.metric("Edge (keterhubungan)", ribu(g["jumlah_edge"]))
    k3.metric("Komunitas / koridor", ribu(g["jumlah_komunitas"]))
    k4.metric("Komponen terpisah", ribu(g["jumlah_komponen"]))

    nodes = muat_csv("fp_graph_nodes.csv")
    edges = muat_csv("fp_graph_edges.csv")
    komunitas = muat_csv("fp_graph_komunitas.csv")

    st.subheader("Peringkat ruas jalan paling sentral (PageRank)")
    n_tampil = st.slider("Jumlah ruas ditampilkan", 5, 30, 12)
    top = nodes.head(n_tampil).iloc[::-1]
    label = top["jalan"].astype(str) + " (" + top["kota"].astype(str) + ")"
    fig = go.Figure(go.Bar(
        x=top["pagerank"], y=label, orientation="h", marker_color=BIRU,
        hovertemplate="<b>%{y}</b><br>PageRank: %{x:.3f}<br>"
                      "Kecelakaan: %{customdata[0]:,}<br>"
                      "Rata-rata severity: %{customdata[1]}<extra></extra>",
        customdata=top[["jumlah_kecelakaan", "rata_severity"]].values))
    fig.update_layout(height=max(320, 26 * n_tampil), margin=dict(t=10, b=10, l=10, r=10),
                      xaxis_title="Skor PageRank", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    kiri, kanan = st.columns([3, 2])

    with kiri:
        st.subheader("Peta jaringan ruas kritis")
        pos = nodes.set_index("id")[["lat", "lng"]]
        lat_garis, lon_garis = [], []
        for s_, d_ in zip(edges["src"], edges["dst"]):
            if s_ in pos.index and d_ in pos.index:
                lat_garis += [pos.at[s_, "lat"], pos.at[d_, "lat"], None]
                lon_garis += [pos.at[s_, "lng"], pos.at[d_, "lng"], None]

        pr = nodes["pagerank"].astype(float)
        ukuran = 7 + 18 * (pr - pr.min()) / max(pr.max() - pr.min(), 1e-9)

        fig = go.Figure()
        fig.add_trace(go.Scattermapbox(
            lat=lat_garis, lon=lon_garis, mode="lines",
            line=dict(width=1, color="rgba(28,114,147,0.45)"),
            hoverinfo="skip", name="Keterhubungan"))
        fig.add_trace(go.Scattermapbox(
            lat=nodes["lat"], lon=nodes["lng"], mode="markers",
            marker=dict(size=ukuran, color=pr, colorscale="Blues", cmin=float(pr.min()),
                        cmax=float(pr.max()), showscale=True,
                        colorbar=dict(title="PageRank", thickness=12)),
            text=[f"<b>{r.jalan}</b><br>{r.kota}<br>"
                  f"Kecelakaan: {ribu(r.jumlah_kecelakaan)}<br>"
                  f"PageRank: {r.pagerank:.3f}<br>Keterhubungan: {int(r.degree)}"
                  for r in nodes.itertuples()],
            hoverinfo="text", name="Ruas jalan"))
        fig.update_layout(
            mapbox=dict(style="open-street-map", zoom=4.6,
                        center=dict(lat=float(nodes["lat"].mean()),
                                    lon=float(nodes["lng"].mean()))),
            height=460, margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"200 ruas jalan dengan PageRank tertinggi beserta "
                   f"{ribu(len(edges))} keterhubungan di antaranya. "
                   "Garis menandakan dua ruas yang kecelakaannya terjadi di sel geografis sama.")

    with kanan:
        st.subheader("Koridor terbesar")
        kk = komunitas.head(8).copy()
        kk["Koridor"] = ["Koridor " + str(i + 1) for i in range(len(kk))]
        fig = px.bar(kk.iloc[::-1], x="total_kecelakaan", y="Koridor", orientation="h",
                     color_discrete_sequence=[ORANYE],
                     hover_data={"jumlah_ruas": True, "rata_severity": True})
        fig.update_layout(height=460, margin=dict(t=10, b=10, l=10, r=10),
                          xaxis_title="Total kecelakaan", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Sepuluh ruas jalan paling kritis")
    tabel = nodes.head(10)[["jalan", "kota", "jumlah_kecelakaan", "rata_severity",
                            "pagerank", "degree"]].copy()
    tabel.columns = ["Ruas jalan", "Kota", "Jumlah kecelakaan", "Rata-rata severity",
                     "PageRank", "Keterhubungan"]
    st.dataframe(tabel, use_container_width=True, hide_index=True)

    nd_rank = nodes.reset_index(drop=True)
    pr1 = nd_rank.iloc[0]
    idx_banyak = int(nd_rank["jumlah_kecelakaan"].idxmax())
    banyak = nd_rank.iloc[idx_banyak]
    kotak_insight(
        "Insight 3 — ruas tersibuk belum tentu ruas terpenting",
        f"Algoritma PageRank menempatkan <b>{pr1['jalan']} ({pr1['kota']})</b> di peringkat "
        f"teratas dengan {ribu(pr1['jumlah_kecelakaan'])} kejadian. Sementara itu, ruas dengan "
        f"kecelakaan <i>terbanyak</i> — <b>{banyak['jalan']} ({banyak['kota']})</b>, "
        f"{ribu(banyak['jumlah_kecelakaan'])} kejadian — hanya menempati peringkat "
        f"<b>ke-{idx_banyak + 1}</b> dalam sentralitas jaringan. PageRank memperhitungkan "
        "keterhubungan dengan ruas rawan lain, bukan sekadar jumlah kejadian. Sembilan dari "
        "sepuluh ruas teratas merupakan bagian dari jalan tol utama Interstate 5, CA-99, dan "
        "Interstate 80.<br><br>"
        f"<i>Implikasi bisnis:</i> hanya {g['lima_komunitas_terbesar_ruas']} ruas jalan "
        f"({persen(g['lima_komunitas_terbesar_ruas']/g['jumlah_node'])} dari jaringan) menyumbang "
        f"{ribu(g['lima_komunitas_terbesar_kejadian'])} kejadian. Anggaran perbaikan infrastruktur "
        "sebaiknya diarahkan pada sedikit koridor ini, bukan disebar merata — dan karena jaringan "
        f"terpecah menjadi {ribu(g['jumlah_komponen'])} komponen terpisah, tiap koridor dapat "
        "ditangani sebagai program mandiri.")
