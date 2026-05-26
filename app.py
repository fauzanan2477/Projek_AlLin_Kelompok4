"""
app.py
======
File utama aplikasi Streamlit ForestVision.
Hanya berisi logika UI dan alur data —
detail SVD ada di backend.py, tampilan di styles.py.

Jalankan dengan: streamlit run app.py
"""

import io
import time

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

# Import modul lokal
import backend as svd
import styles as ui

# ─────────────────────────────────────────────────────────
# KONFIGURASI HALAMAN
# ─────────────────────────────────────────────────────────

st.set_page_config(
    page_title="ForestVision | SVD Compression",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="expanded"
)

# Terapkan CSS tema SDG 15
ui.terapkan_css()

# ─────────────────────────────────────────────────────────
# HEADER — Hero banner & statistik konteks
# ─────────────────────────────────────────────────────────

ui.render_hero_banner()

# Baris 4 kartu statistik konteks SDG 15
kolom_stat = st.columns(4)
data_statistik = [
    ("🌳", "31%",   "Tutupan Hutan Dunia"),
    ("⚠️", "10M ha", "Hutan Hilang / Tahun"),
    ("🦎", "80%",   "Biodiversitas Terestrial"),
    ("📡", "SVD",   "Metode Kompresi"),
]
for kolom, (ikon, angka, label) in zip(kolom_stat, data_statistik):
    with kolom:
        ui.render_kartu_statistik(ikon, angka, label)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# SIDEBAR — Kontrol input pengguna
# ─────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:20px 0 10px;'>
        <div style='font-size:2.5rem;'>🌿</div>
        <div style='font-family:Playfair Display; font-size:1.2rem;
                    color:#6dbf6e; font-weight:700;'>ForestVision</div>
        <div style='font-size:0.7rem; color:rgba(245,240,232,0.45);
                    letter-spacing:2px; text-transform:uppercase;'>SVD Engine v2.0</div>
    </div>
    <hr style='border-color:rgba(109,191,110,0.15);'>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Konfigurasi")

    # Pilihan mode komputasi
    pilihan_mode = st.selectbox(
        "Mode Komputasi Matriks",
        ["🔲 Grayscale (Matriks 2D)", "🎨 Berwarna (Tensor 3D RGB)"],
        help="Grayscale: 1 matriks | RGB: 3 matriks terpisah (R, G, B)"
    )
    adalah_grayscale = "Grayscale" in pilihan_mode

    # Upload gambar
    file_gambar = st.file_uploader(
        "Unggah Citra Hutan",
        type=["jpg", "png", "jpeg"],
        help="Disarankan foto ekosistem hutan untuk konteks SDG 15."
    )

    st.markdown("""
    <hr style='border-color:rgba(109,191,110,0.15);'>
    <div style='font-size:0.75rem; color:rgba(245,240,232,0.4); line-height:1.8;'>
        <b style='color:#6dbf6e;'>Tentang SDG 15</b><br>
        Melindungi & memulihkan ekosistem darat secara berkelanjutan.
        Kompresi citra mendukung pemantauan perubahan hutan secara efisien.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# TAB UTAMA
# ─────────────────────────────────────────────────────────

tab_workspace, tab_analisis, tab_teori = st.tabs([
    "🚀  Workspace Kompresi",
    "📈  Analisis & Visualisasi",
    "📚  Dasar Teori SVD",
])

# ══════════════════════════════════════════════════════════
# TAB 1 — WORKSPACE KOMPRESI
# ══════════════════════════════════════════════════════════

with tab_workspace:

    # Tampilkan placeholder jika belum ada gambar
    if file_gambar is None:
        st.markdown("""
        <div style='text-align:center; padding:60px 20px;
                    border:2px dashed rgba(109,191,110,0.2);
                    border-radius:20px; background:rgba(13,43,15,0.3);'>
            <div style='font-size:4rem; margin-bottom:16px;'>🌲</div>
            <div style='font-family:Playfair Display; font-size:1.6rem;
                        color:#6dbf6e; margin-bottom:8px;'>Unggah Citra Hutan</div>
            <div style='color:rgba(245,240,232,0.45); font-size:0.9rem;'>
                Gunakan panel sidebar kiri · Format JPG atau PNG
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # ── Proses SVD ──────────────────────────────────────
        with st.spinner('🌿 Menghitung Dekomposisi SVD...'):
            time.sleep(0.6)

            if adalah_grayscale:
                matriks_asli = svd.muat_gambar_grayscale(file_gambar)
                gambar_asli  = Image.fromarray(matriks_asli.astype(np.uint8))
                hasil_svd    = svd.hitung_svd_grayscale(matriks_asli)
                vektor_sigma = hasil_svd["vektor_sigma"]
            else:
                tensor_asli  = svd.muat_gambar_rgb(file_gambar)
                gambar_asli  = Image.fromarray(tensor_asli.astype(np.uint8))
                hasil_svd    = svd.hitung_svd_rgb(tensor_asli)
                vektor_sigma = hasil_svd["sigma_merah"]  # referensi energi dari channel merah
                matriks_asli = tensor_asli

        jumlah_maks_k = hasil_svd["jumlah_maks_k"]

        # ── Slider kontrol k ────────────────────────────────
        ui.render_kepala_seksi("🎚️ Kendali Komponen Singular")
        k_dipilih = st.slider(
            "Jumlah komponen singular (k) yang dipertahankan:",
            min_value=1,
            max_value=jumlah_maks_k,
            value=max(1, jumlah_maks_k // 6),
            step=1,
            help="Lebih besar k → gambar lebih detail, ukuran lebih besar."
        )

        # ── Rekonstruksi gambar terkompresi ─────────────────
        if adalah_grayscale:
            piksel_terkompresi = svd.rekonstruksi_grayscale(hasil_svd, k_dipilih)
            gambar_terkompresi = Image.fromarray(piksel_terkompresi)
        else:
            piksel_terkompresi = svd.rekonstruksi_rgb(hasil_svd, k_dipilih)
            gambar_terkompresi = Image.fromarray(piksel_terkompresi)

        # ── Hitung metrik ────────────────────────────────────
        persen_energi  = svd.hitung_energi_visual(vektor_sigma, k_dipilih)
        rasio_kompresi = svd.hitung_rasio_kompresi(
            ukuran_asli   = matriks_asli.size,
            jumlah_baris  = matriks_asli.shape[0],
            jumlah_kolom  = matriks_asli.shape[1],
            k             = k_dipilih,
            adalah_rgb    = not adalah_grayscale
        )

        # ── Tampilkan 4 kotak metrik ─────────────────────────
        kolom_metrik = st.columns(4)
        data_metrik = [
            (f"{persen_energi:.1f}%", "Info Visual Tersisa"),
            (str(k_dipilih),          "Komponen k Aktif"),
            (str(jumlah_maks_k),      "Total Komponen"),
            (f"{rasio_kompresi:.1f}x","Rasio Kompresi"),
        ]
        for kolom, (nilai, label) in zip(kolom_metrik, data_metrik):
            with kolom:
                ui.render_kotak_metrik(nilai, label)

        # Progress bar energi
        st.markdown("<br>", unsafe_allow_html=True)
        st.progress(int(persen_energi))
        st.markdown(
            f"<div style='text-align:right; font-size:0.78rem; "
            f"color:rgba(245,240,232,0.4);'>Energi visual: {persen_energi:.2f}%</div>",
            unsafe_allow_html=True
        )

        # ── Tampilkan gambar asli vs hasil ──────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        kolom_kiri, kolom_kanan = st.columns(2, gap="large")

        with kolom_kiri:
            ui.render_kepala_seksi("🖼️ Citra Original")
            st.image(gambar_asli, use_column_width=True)
            ui.render_keterangan_gambar(
                f"Dimensi: {matriks_asli.shape[0]} × {matriks_asli.shape[1]}"
            )

        with kolom_kanan:
            ui.render_kepala_seksi(f"🗜️ Hasil SVD — k = {k_dipilih}")
            st.image(gambar_terkompresi, use_column_width=True)
            ui.render_keterangan_gambar(
                f"Energi: {persen_energi:.2f}% | k = {k_dipilih} / {jumlah_maks_k}"
            )

        # ── Tombol unduh ─────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        buffer_unduh = io.BytesIO()
        gambar_terkompresi.save(buffer_unduh, format="PNG")
        st.download_button(
            label="📥 Unduh Citra Terkompresi (PNG)",
            data=buffer_unduh.getvalue(),
            file_name=f"forestvision_k{k_dipilih}.png",
            mime="image/png",
            use_container_width=True,
            type="primary"
        )

        # ── Inspeksi nilai matriks ───────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔬 Inspeksi Nilai Matriks (15×15 piksel pertama)"):
            if adalah_grayscale:
                tab_A, tab_U, tab_S, tab_Vt, tab_Ak = st.tabs(
                    ["A (Asli)", "U", "Σ", "Vᵀ", "Aₖ (Hasil)"]
                )
                with tab_A:
                    st.dataframe(matriks_asli[:15, :15], use_container_width=True)
                with tab_U:
                    st.dataframe(hasil_svd["matriks_U"][:15, :15], use_container_width=True)
                with tab_S:
                    st.dataframe(np.diag(vektor_sigma[:15]), use_container_width=True)
                with tab_Vt:
                    st.dataframe(hasil_svd["matriks_Vt"][:15, :15], use_container_width=True)
                with tab_Ak:
                    st.dataframe(piksel_terkompresi[:15, :15].astype(float), use_container_width=True)
            else:
                st.info("Inspeksi nilai matriks tersedia pada mode Grayscale (2D).")


# ══════════════════════════════════════════════════════════
# TAB 2 — ANALISIS INTERAKTIF
# ══════════════════════════════════════════════════════════

with tab_analisis:

    if file_gambar is None:
        st.info("🌿 Unggah gambar terlebih dahulu untuk melihat analisis interaktif.")

    else:
        ui.render_kepala_seksi("📊 Analisis Nilai Singular")
        kolom_grafik_kiri, kolom_grafik_kanan = st.columns(2, gap="large")

        # Pengaturan warna grafik (konsisten dengan tema)
        WARNA_GARIS_UTAMA = '#6dbf6e'
        WARNA_AREA        = 'rgba(109,191,110,0.08)'
        WARNA_PENANDA_K   = '#d4a843'
        WARNA_PLOT_BG     = 'rgba(13,43,15,0.4)'
        WARNA_GRID        = 'rgba(109,191,110,0.1)'
        WARNA_TEKS        = '#f5f0e8'

        # ── Grafik 1: Distribusi nilai singular ─────────────
        batas_grafik = min(80, len(vektor_sigma))
        with kolom_grafik_kiri:
            fig_sigma = go.Figure()
            fig_sigma.add_trace(go.Scatter(
                x    = list(range(1, batas_grafik + 1)),
                y    = vektor_sigma[:batas_grafik],
                mode = 'lines+markers',
                line = dict(color=WARNA_GARIS_UTAMA, width=2.5),
                marker = dict(size=4, color='#a8d96c'),
                fill      = 'tozeroy',
                fillcolor = WARNA_AREA,
            ))
            fig_sigma.add_vline(
                x=k_dipilih, line_dash="dash",
                line_color=WARNA_PENANDA_K,
                annotation_text=f"k={k_dipilih}",
                annotation_font_color=WARNA_PENANDA_K
            )
            fig_sigma.update_layout(
                title        = "Distribusi Nilai Singular (σ)",
                paper_bgcolor= 'rgba(0,0,0,0)',
                plot_bgcolor = WARNA_PLOT_BG,
                font         = dict(color=WARNA_TEKS),
                xaxis        = dict(title="Indeks Komponen", gridcolor=WARNA_GRID),
                yaxis        = dict(title="Nilai σ",         gridcolor=WARNA_GRID),
                margin       = dict(l=20, r=20, t=50, b=20),
                showlegend   = False,
                height       = 300,
            )
            st.plotly_chart(fig_sigma, use_container_width=True)

        # ── Grafik 2: Energi kumulatif ───────────────────────
        data_energi_kumulatif = svd.hitung_energi_kumulatif(vektor_sigma, batas=100)
        with kolom_grafik_kanan:
            fig_energi = go.Figure()
            fig_energi.add_trace(go.Scatter(
                x    = list(range(1, len(data_energi_kumulatif) + 1)),
                y    = data_energi_kumulatif,
                mode = 'lines',
                line = dict(color='#a8d96c', width=3),
                fill      = 'tozeroy',
                fillcolor = 'rgba(168,217,108,0.1)',
            ))
            # Garis ambang 90% dan 99%
            for target, opasitas in [(90, 0.6), (99, 0.4)]:
                fig_energi.add_hline(
                    y=target,
                    line_dash="dot",
                    line_color=f"rgba(212,168,67,{opasitas})",
                    annotation_text=f"{target}%",
                    annotation_font_color=WARNA_PENANDA_K
                )
            fig_energi.add_vline(
                x=k_dipilih, line_dash="dash",
                line_color=WARNA_PENANDA_K,
                annotation_text=f"k={k_dipilih}",
                annotation_font_color=WARNA_PENANDA_K
            )
            fig_energi.update_layout(
                title        = "Energi Kumulatif (%)",
                paper_bgcolor= 'rgba(0,0,0,0)',
                plot_bgcolor = WARNA_PLOT_BG,
                font         = dict(color=WARNA_TEKS),
                xaxis        = dict(title="Komponen k", gridcolor=WARNA_GRID),
                yaxis        = dict(title="Energi (%)", gridcolor=WARNA_GRID, range=[0, 101]),
                margin       = dict(l=20, r=20, t=50, b=20),
                showlegend   = False,
                height       = 300,
            )
            st.plotly_chart(fig_energi, use_container_width=True)

        # ── Grafik 3: Perbandingan energi multi-k ───────────
        ui.render_kepala_seksi("🔄 Perbandingan Multi-k")

        kandidat_k    = [1, 5, 10, 20, 50, k_dipilih, jumlah_maks_k]
        daftar_k_valid = sorted(set(kv for kv in kandidat_k if 1 <= kv <= jumlah_maks_k))
        daftar_energi  = svd.hitung_energi_multi_k(vektor_sigma, daftar_k_valid)

        fig_multik = go.Figure(go.Bar(
            x    = [f"k={kv}" for kv in daftar_k_valid],
            y    = daftar_energi,
            marker_color      = [WARNA_PENANDA_K if kv == k_dipilih else '#4a9e50'
                                 for kv in daftar_k_valid],
            marker_line_color = 'rgba(109,191,110,0.4)',
            marker_line_width = 1,
            text          = [f"{e:.1f}%" for e in daftar_energi],
            textposition  = 'outside',
            textfont      = dict(color=WARNA_TEKS, size=11),
        ))
        fig_multik.update_layout(
            title        = "Energi Visual pada Berbagai Nilai k",
            paper_bgcolor= 'rgba(0,0,0,0)',
            plot_bgcolor = WARNA_PLOT_BG,
            font         = dict(color=WARNA_TEKS),
            xaxis        = dict(gridcolor=WARNA_GRID),
            yaxis        = dict(title="Energi (%)", gridcolor=WARNA_GRID, range=[0, 115]),
            margin       = dict(l=20, r=20, t=50, b=20),
            height       = 320,
        )
        st.plotly_chart(fig_multik, use_container_width=True)

        # ── Kotak insight ────────────────────────────────────
        k_untuk_90_persen = svd.cari_k_untuk_target_energi(vektor_sigma, 90)
        k_untuk_99_persen = svd.cari_k_untuk_target_energi(vektor_sigma, 99)
        ui.render_kotak_insight(
            k_untuk_90     = k_untuk_90_persen,
            k_untuk_99     = k_untuk_99_persen,
            total_k        = jumlah_maks_k,
            energi_saat_ini= persen_energi,
            k_aktif        = k_dipilih
        )


# ══════════════════════════════════════════════════════════
# TAB 3 — DASAR TEORI
# ══════════════════════════════════════════════════════════

with tab_teori:
    ui.render_kepala_seksi("📖 Landasan Matematika ForestVision")
    st.markdown("""
    <div style='background:rgba(45,106,48,0.12); border-left:4px solid #6dbf6e;
                border-radius:0 12px 12px 0; padding:16px 20px; margin-bottom:24px;'>
        Aplikasi ini mengintegrasikan <b style='color:#a8d96c;'>5 pilar Aljabar Linier</b>
        untuk mendukung <b style='color:#a8d96c;'>SDG Goal 15: Life on Land</b>.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("1. 🖼️ Matriks sebagai Representasi Citra Digital", expanded=True):
        st.markdown("""
Setiap gambar digital adalah **matriks angka**:
- **Grayscale**: matriks 2D *m × n*, nilai piksel 0–255
- **RGB**: tensor 3D *m × n × 3*, tiga lapisan warna

Dengan merepresentasikan citra hutan sebagai matriks, kita
bisa menerapkan operasi matematis untuk kompresi dan analisis.
        """)

    with st.expander("2. 🔀 Singular Value Decomposition (SVD)"):
        st.markdown(r"""
SVD memfaktorkan matriks **A** menjadi:
$$A = U \cdot \Sigma \cdot V^T$$

| Matriks | Dimensi | Makna |
|---------|---------|-------|
| **U** | *m × m* | Vektor singular kiri — pola baris |
| **Σ** | *m × n* | Matriks diagonal — nilai singular |
| **Vᵀ** | *n × n* | Vektor singular kanan — pola kolom |

Kompresi: simpan hanya k komponen → $A_k = U_k \cdot \Sigma_k \cdot V^T_k$
        """)

    with st.expander("3. 🎯 Nilai Eigen & Vektor Eigen"):
        st.markdown(r"""
SVD diturunkan dari eigendecomposition:
- Kolom **U** = vektor eigen dari $AA^T$
- Kolom **V** = vektor eigen dari $A^TA$
- Nilai singular: $\sigma_i = \sqrt{\lambda_i}$

Nilai singular terbesar = fitur visual paling dominan.
        """)

    with st.expander("4. 🔲 Diagonalisasi & Matriks Diagonal"):
        st.markdown(r"""
Matriks **Σ** adalah matriks diagonal:
$$\Sigma = \begin{pmatrix} \sigma_1 & 0 & \cdots \\ 0 & \sigma_2 & \cdots \\ \vdots & & \ddots \end{pmatrix}$$

Memotong k < rank(A) = membuang nilai kecil → hemat penyimpanan.
        """)

    with st.expander("5. ✖️ Perkalian Matriks & Energi"):
        st.markdown(r"""
Rekonstruksi: $A_k = U_{[:,1:k]} \cdot \Sigma_{[1:k,1:k]} \cdot V^T_{[1:k,:]}$

Energi visual:
$$\text{Energi} = \frac{\sum_{i=1}^{k} \sigma_i^2}{\sum_{i=1}^{n} \sigma_i^2} \times 100\%$$
        """)

    st.markdown("""
    <div style='background:linear-gradient(135deg,rgba(13,43,15,0.9),rgba(22,46,14,0.7));
                border:1px solid rgba(212,168,67,0.3); border-radius:16px;
                padding:28px; margin-top:24px;'>
        <div style='font-family:Playfair Display; font-size:1.3rem;
                    color:#d4a843; margin-bottom:16px;'>
            🌍 Relevansi dengan SDG 15 — Life on Land
        </div>
        <div style='color:rgba(245,240,232,0.75); line-height:1.9; font-size:0.9rem;'>
            🌲 <b>Penyimpanan efisien</b> data citra hutan tanpa kehilangan info krusial<br>
            📡 <b>Transmisi cepat</b> data pemantauan ke pusat analisis lingkungan<br>
            🔬 <b>Ekstraksi fitur</b> untuk deteksi deforestasi berbasis machine learning<br>
            💾 <b>Arsip jangka panjang</b> perubahan tutupan hutan dengan biaya rendah
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────

ui.render_footer()