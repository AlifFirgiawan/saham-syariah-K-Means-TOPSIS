import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from logic import (
    CRITERIA, ARAH_KRITERIA,
    load_semua_data, normalisasi_min_max,
    hitung_wcss_silhouette, kmeans_clustering,
    entropy_weighting, topsis,
)

# =================================================================================
# KONFIGURASI HALAMAN
# =================================================================================
st.set_page_config(
    page_title="Dashboard Saham Syariah JII",
    page_icon="📈",
    layout="wide",
)

DATA_PATH = "Dataset.xlsx"


@st.cache_data
def get_data():
    return load_semua_data(DATA_PATH)


data = get_data()
X_norm = normalisasi_min_max(data)

# =================================================================================
# SIDEBAR NAVIGASI
# =================================================================================

halaman = option_menu(
    menu_title=None,
    options=["Beranda", "Elbow & Clustering", "Entropy & TOPSIS"],
    icons=['house','graph-up','table'],
    default_index=0,
    orientation="horizontal",
)

# =================================================================================
# HALAMAN: BERANDA
# =================================================================================
if halaman == "Beranda":
    st.title("Data Rasio Fundamental Saham JII")
    st.caption("Rata-rata rasio fundamental periode 2023 - awal 2026")

    # st.subheader("🔍 Filter & Pencarian Emiten")
    c1, c2 = st.columns([1, 2])
    with c1:
        cari_kode = st.text_input("Cari kode saham", placeholder="contoh: ADRO")
    with c2:
        kriteria_filter = st.multiselect(
            "Pilih kriteria yang ingin difilter",
            CRITERIA,
            default=[],
            help="Pilih satu atau lebih rasio untuk mengatur rentang nilainya",
        )

    data_filtered = data.copy()

    if cari_kode:
        data_filtered = data_filtered[
            data_filtered["KODE"].str.contains(cari_kode.upper(), na=False)
        ]

    if kriteria_filter:
        cols_slider = st.columns(len(kriteria_filter))
        for i, crit in enumerate(kriteria_filter):
            with cols_slider[i]:
                nilai_min = float(data[crit].min())
                nilai_max = float(data[crit].max())
                rentang = st.slider(
                    f"{crit}",
                    min_value=round(nilai_min, 2),
                    max_value=round(nilai_max, 2),
                    value=(round(nilai_min, 2), round(nilai_max, 2)),
                    key=f"filter_{crit}",
                )
                data_filtered = data_filtered[
                    (data_filtered[crit] >= rentang[0]) & (data_filtered[crit] <= rentang[1])
                ]

    st.caption(f"Menampilkan **{len(data_filtered)}** dari {len(data)} saham")
    st.dataframe(
        data_filtered.style.format({c: "{:.2f}" for c in CRITERIA}),
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Unduh data terfilter (CSV)",
        data_filtered.to_csv(index=False).encode("utf-8"),
        file_name="data_saham_terfilter.csv",
        mime="text/csv",
    )

    st.divider()
    st.subheader("Distribusi Tiap Kriteria")
    crit_pilihan = st.selectbox("Pilih kriteria untuk dilihat distribusinya", CRITERIA)
    fig = px.bar(
        data_filtered.sort_values(crit_pilihan, ascending=False),
        x="KODE", y=crit_pilihan, color=crit_pilihan,
        color_continuous_scale="Blues",
    )
    st.plotly_chart(fig, use_container_width=True)


# =================================================================================
# HALAMAN: ELBOW & CLUSTERING (+ Interaktivitas Parameter Klaster)
# =================================================================================
elif halaman == "Elbow & Clustering":
    st.title("Metode Elbow & K-Means Clustering")

    K_range, wcss, silhouette = hitung_wcss_silhouette(X_norm, k_max=10)

    st.subheader("Metode Elbow")
    fig_elbow = go.Figure()
    fig_elbow.add_trace(go.Scatter(
        x=K_range, y=wcss, mode="lines+markers",
        line=dict(color="#1F4E78", width=3), marker=dict(size=8),
        name="WCSS",
    ))
    fig_elbow.update_layout(
        xaxis_title="Jumlah Cluster (k)",
        yaxis_title="WCSS (Within-Cluster Sum of Squares)",
        xaxis=dict(tickmode="linear"),
        height=400,
    )
    st.plotly_chart(fig_elbow, use_container_width=True)

    st.divider()
    st.subheader("Interaktivitas Parameter Cluster")
    st.markdown(
        "Geser slider di bawah untuk mengubah jumlah cluster (k) dan lihat "
        "perubahan hasil pengelompokan saham secara langsung."
    )

    c1, c2 = st.columns([1, 3])
    with c1:
        k_pilihan = st.slider("Jumlah Cluster (k)", min_value=2, max_value=8, value=3)
        if k_pilihan in silhouette:
            st.metric("Silhouette Score", f"{silhouette[k_pilihan]:.4f}")
        st.metric("WCSS", f"{wcss[k_pilihan - 1]:.4f}")

        eksis_x = st.selectbox("Sumbu X", CRITERIA, index=0, key="sumbu_x")
        eksis_y = st.selectbox("Sumbu Y", CRITERIA, index=2, key="sumbu_y")

    labels = kmeans_clustering(X_norm, k_pilihan)
    data_cluster = data.copy()
    data_cluster["Cluster"] = labels.astype(str)

    with c2:
        fig_scatter = px.scatter(
            data_cluster, x=eksis_x, y=eksis_y, color="Cluster",
            text="KODE", hover_data=CRITERIA,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_scatter.update_traces(textposition="top center", marker=dict(size=12))
        fig_scatter.update_layout(height=480)
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader(f"Profil Tiap Cluster (k={k_pilihan})")
    profil = data_cluster.groupby("Cluster")[CRITERIA].mean().round(2)
    profil["Jumlah Anggota"] = data_cluster.groupby("Cluster").size()
    st.dataframe(profil, use_container_width=True)

    for c in sorted(data_cluster["Cluster"].unique(), key=int):
        anggota = data_cluster.loc[data_cluster["Cluster"] == c, "KODE"].tolist()
        st.markdown(f"**Cluster {c}** ({len(anggota)} saham): {', '.join(anggota)}")

    st.session_state["data_cluster"] = data_cluster
    st.session_state["k_pilihan"] = k_pilihan


# =================================================================================
# HALAMAN: ENTROPY & TOPSIS 
# =================================================================================
elif halaman == "Entropy & TOPSIS":
    st.title("Simulasi Bobot Kriteria: Entropy vs Kustom")

    data_cluster = st.session_state.get("data_cluster")
    if data_cluster is None:
        st.warning(
            "Silakan buka halaman **Elbow & Clustering** terlebih dahulu untuk "
            "menentukan jumlah cluster sebelum melakukan perankingan TOPSIS."
        )
        st.stop()

    k_pilihan = st.session_state["k_pilihan"]
    daftar_cluster = sorted(data_cluster["Cluster"].unique(), key=int)
    cluster_topsis = st.selectbox(
        "Pilih cluster yang akan diranking dengan TOPSIS",
        daftar_cluster,
        help="Sebaiknya pilih cluster beranggota lebih dari 1 saham",
    )
    data_input = data_cluster[data_cluster["Cluster"] == cluster_topsis].reset_index(drop=True)

    if len(data_input) < 2:
        st.warning(
            f"Cluster {cluster_topsis} hanya berisi 1 saham, TOPSIS membutuhkan "
            "minimal 2 alternatif untuk dibandingkan. Pilih cluster lain."
        )
        st.stop()

    bobot_entropy = entropy_weighting(data_input)

    st.subheader("Atur Bobot Kustom")
    st.caption("Geser slider di bawah, bobot akan otomatis dinormalisasi agar totalnya 100%")

    cols = st.columns(len(CRITERIA))
    bobot_mentah = {}
    for i, crit in enumerate(CRITERIA):
        with cols[i]:
            bobot_mentah[crit] = st.slider(
                crit, min_value=0.0, max_value=1.0,
                value=float(bobot_entropy[crit]), step=0.01,
                key=f"bobot_{crit}",
            )

    total_bobot = sum(bobot_mentah.values())
    if total_bobot == 0:
        st.error("Total bobot tidak boleh 0. Geser minimal satu slider.")
        st.stop()
    bobot_kustom = pd.Series(
        {c: v / total_bobot for c, v in bobot_mentah.items()}
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Bobot Entropy (otomatis)**")
        st.dataframe(
            bobot_entropy.to_frame("Bobot").style.format("{:.2%}"),
            use_container_width=True,
        )
    with c2:
        st.markdown("**Bobot Kustom (ternormalisasi)**")
        st.dataframe(
            bobot_kustom.to_frame("Bobot").style.format("{:.2%}"),
            use_container_width=True,
        )

    fig_bobot = go.Figure()
    fig_bobot.add_trace(go.Bar(x=CRITERIA, y=bobot_entropy.values, name="Entropy"))
    fig_bobot.add_trace(go.Bar(x=CRITERIA, y=bobot_kustom.values, name="Kustom"))
    fig_bobot.update_layout(barmode="group", height=320, yaxis_title="Bobot")
    st.plotly_chart(fig_bobot, use_container_width=True)

    st.divider()
    st.subheader(f"Perbandingan Ranking TOPSIS — Cluster {cluster_topsis}")

    hasil_entropy = topsis(data_input, bobot_entropy)[["KODE", "Skor_TOPSIS", "Ranking"]]
    hasil_entropy.columns = ["KODE", "Skor_Entropy", "Ranking_Entropy"]

    hasil_kustom = topsis(data_input, bobot_kustom)[["KODE", "Skor_TOPSIS", "Ranking"]]
    hasil_kustom.columns = ["KODE", "Skor_Kustom", "Ranking_Kustom"]

    perbandingan = hasil_entropy.merge(hasil_kustom, on="KODE")
    perbandingan["Perubahan Ranking"] = (
        perbandingan["Ranking_Entropy"] - perbandingan["Ranking_Kustom"]
    )
    perbandingan = perbandingan.sort_values("Ranking_Entropy")

    def beri_warna(val):
        if val > 0:
            return "color: green"
        elif val < 0:
            return "color: red"
        return "color: gray"

    st.dataframe(
        perbandingan.style
        .format({"Skor_Entropy": "{:.4f}", "Skor_Kustom": "{:.4f}"})
        .map(beri_warna, subset=["Perubahan Ranking"]),
        use_container_width=True,
        hide_index=True,
    )