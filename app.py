import streamlit as st
import numpy as np
import pandas as pd

# --- 1. KONFIGURASI WEB & CSS ---
st.set_page_config(page_title="Sistem Ekologi SDG 15", layout="wide")

# CSS untuk menyembunyikan bawaan Streamlit agar terlihat seperti website utuh
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem;}
    /* Modifikasi ukuran font Tab agar persis seperti menu Kompas */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. HEADER WEBSITE ---
st.markdown("<h1 style='color: #2E86C1; margin-bottom: 0px;'>Sistem Prediksi Ekologi (SDG 15)</h1>", unsafe_allow_html=True)
st.write("Platform Simulasi Demografi Satwa Berbasis Aljabar Linier")
st.write("---")

# --- 3. MENU NAVIGASI (ALA KOMPAS) ---
# Menggunakan st.tabs agar menunya ada di atas, berjejer horizontal, dan bisa dipencet
menu1, menu2, menu3 = st.tabs([
    "Berita Utama (Beranda)", 
    "Simulasi & Parameter", 
    "Spesifikasi Matriks (Teori)"
])

# --- 4. STATE MANAGEMENT ---
if 'nama_hewan' not in st.session_state:
    st.session_state.nama_hewan = "Harimau Sumatera"
if 'populasi_awal' not in st.session_state:
    st.session_state.populasi_awal = [50, 30, 20] # Bayi, Remaja, Dewasa
if 'parameter_matriks' not in st.session_state:
    st.session_state.parameter_matriks = [0.2, 0.5, 0.8, 0.9] # Fekunditas, S1, S2, S3

# ==========================================
# HALAMAN 1: BERANDA
# ==========================================
with menu1:
    st.write("### Identifikasi Spesies")
    st.write("Ketik nama hewan yang ingin dianalisis. Sistem akan menyesuaikan seluruh laporan prediksi secara otomatis.")
    
    # INPUT NAMA HEWAN (FITUR DINAMIS)
    input_hewan = st.text_input("Nama Spesies Satwa:", st.session_state.nama_hewan)
    st.session_state.nama_hewan = input_hewan
    
    st.success(f"**Target Analisis:** Populasi {st.session_state.nama_hewan} di Ekosistem Darat (SDG 15).")
    
    col1, col2 = st.columns(2)
    col1.metric("Total Populasi Saat Ini", sum(st.session_state.populasi_awal), "Individu")
    col2.metric("Target SDG 15", "Menghentikan Kepunahan Keanekaragaman Hayati")

# ==========================================
# HALAMAN 2: SIMULASI & PARAMETER
# ==========================================
with menu2:
    st.write(f"### Parameter Demografi: {st.session_state.nama_hewan}")
    
    col_input, col_grafik = st.columns([1, 2])
    
    with col_input:
        st.markdown("**1. Vektor Populasi (Individu)**")
        bayi = st.number_input("Fase Bayi", min_value=0, value=st.session_state.populasi_awal[0])
        remaja = st.number_input("Fase Remaja", min_value=0, value=st.session_state.populasi_awal[1])
        dewasa = st.number_input("Fase Dewasa", min_value=0, value=st.session_state.populasi_awal[2])
        st.session_state.populasi_awal = [bayi, remaja, dewasa]
        
        st.markdown("**2. Matriks Peluang Hidup**")
        f_dewasa = st.slider("Laju Reproduksi Dewasa", 0.0, 5.0, st.session_state.parameter_matriks[0], 0.1)
        s_bayi = st.slider("Peluang Hidup Bayi", 0.0, 1.0, st.session_state.parameter_matriks[1], 0.05)
        s_remaja = st.slider("Peluang Hidup Remaja", 0.0, 1.0, st.session_state.parameter_matriks[2], 0.05)
        s_dewasa = st.slider("Peluang Hidup Dewasa", 0.0, 1.0, st.session_state.parameter_matriks[3], 0.05)
        st.session_state.parameter_matriks = [f_dewasa, s_bayi, s_remaja, s_dewasa]

    with col_grafik:
        st.markdown(f"**Grafik Proyeksi {st.session_state.nama_hewan} (20 Tahun Kedepan)**")
        
        matriks_leslie = np.array([
            [0, 0, f_dewasa],
            [s_bayi, 0, 0],
            [0, s_remaja, s_dewasa]
        ])
        
        vektor_populasi = np.array(st.session_state.populasi_awal)
        riwayat = [vektor_populasi]
        
        for _ in range(20):
            vektor_populasi = np.dot(matriks_leslie, vektor_populasi)
            riwayat.append(vektor_populasi)
            
        df_proyeksi = pd.DataFrame(riwayat, columns=["Bayi", "Remaja", "Dewasa"])
        st.line_chart(df_proyeksi)
        st.info(f"Total {st.session_state.nama_hewan} di akhir proyeksi: **{int(np.sum(riwayat[-1]))} Individu**")

# ==========================================
# HALAMAN 3: SPESIFIKASI MATRIKS
# ==========================================
with menu3:
    st.write("### Evaluasi Aljabar Linier (Nilai Eigen)")
    st.write(f"Untuk mengetahui status kepunahan {st.session_state.nama_hewan}, sistem menghitung **Nilai Eigen Utama** dari matriks yang terbentuk.")
    
    matriks_leslie = np.array([
        [0, 0, st.session_state.parameter_matriks[0]],
        [st.session_state.parameter_matriks[1], 0, 0],
        [0, st.session_state.parameter_matriks[2], st.session_state.parameter_matriks[3]]
    ])
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**Matriks Pertumbuhan (A)**")
        st.dataframe(pd.DataFrame(matriks_leslie).style.format("{:.2f}"))
    with col_b:
        st.write("**Vektor Awal (x)**")
        st.dataframe(pd.DataFrame(st.session_state.populasi_awal, index=["Bayi", "Remaja", "Dewasa"], columns=["Populasi"]))
        
    st.markdown("---")
    
    # Perhitungan Nilai Eigen
    nilai_eigen, vektor_eigen = np.linalg.eig(matriks_leslie)
    eigen_dominan = max(np.real(nilai_eigen))
    
    st.markdown(f"#### Hasil Ekstraksi Nilai Eigen ($\lambda$) = {eigen_dominan:.4f}")
    
    if eigen_dominan > 1:
        st.success(f"**Kesimpulan:** $\lambda > 1$. Populasi {st.session_state.nama_hewan} dalam keadaan LESTARI dan bertambah.")
    elif eigen_dominan == 1:
        st.warning(f"**Kesimpulan:** $\lambda = 1$. Populasi {st.session_state.nama_hewan} STABIL.")
    else:
        st.error(f"**Kesimpulan:** $\lambda < 1$. Perhatian! {st.session_state.nama_hewan} TERANCAM PUNAH.")