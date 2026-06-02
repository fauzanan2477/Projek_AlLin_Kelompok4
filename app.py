import streamlit as st
import numpy as np
import pandas as pd

# --- 1. PENGATURAN HALAMAN ---
st.set_page_config(page_title="Simulasi Ekologi SDG 15", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.15rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. HEADER ---
st.markdown("<h2 style='text-align: center; color: #2E86C1;'>Simulasi Ekologi Satwa (SDG 15)</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Pemodelan Matriks Demografi & Nilai Eigen</p>", unsafe_allow_html=True)
st.write("---")

# --- 3. MENU NAVIGASI ---
menu1, menu2, menu3 = st.tabs([
    "Berita Utama", 
    "Simulasi & Input Data", 
    "Hitungan Matriks (Teori)"
])

# --- 4. PENYIMPANAN DATA SEMENTARA ---
if 'nama_hewan' not in st.session_state:
    st.session_state.nama_hewan = "Harimau Sumatera"
if 'populasi_awal' not in st.session_state:
    st.session_state.populasi_awal = [50, 30, 20] 

# ==========================================
# TAB 1: BERANDA
# ==========================================
with menu1:
    st.write("### Identifikasi Spesies")
    st.write("Masukkan nama spesies yang akan dianalisis. Seluruh data dan kalkulasi matriks akan menyesuaikan secara otomatis.")
    
    input_hewan = st.text_input("Nama Spesies:", st.session_state.nama_hewan)
    st.session_state.nama_hewan = input_hewan
    
    st.success(f"Target Analisis: **{st.session_state.nama_hewan}**")

# ==========================================
# TAB 2: SIMULASI & INPUT DATA
# ==========================================
with menu2:
    st.write(f"### Parameter Populasi {st.session_state.nama_hewan}")
    st.write("Masukkan populasi saat ini dan data historis tahun lalu. Sistem akan mengonversi data historis menjadi rasio probabilitas.")
    
    kolom_kiri, kolom_kanan = st.columns(2)
    
    with kolom_kiri:
        st.info("Populasi Saat Ini")
        bayi_skrg = st.number_input("Jumlah Bayi (Ekor)", min_value=0, value=st.session_state.populasi_awal[0])
        remaja_skrg = st.number_input("Jumlah Remaja (Ekor)", min_value=0, value=st.session_state.populasi_awal[1])
        dewasa_skrg = st.number_input("Jumlah Dewasa (Ekor)", min_value=0, value=st.session_state.populasi_awal[2])
        st.session_state.populasi_awal = [bayi_skrg, remaja_skrg, dewasa_skrg]
        
    with kolom_kanan:
        st.info("Data Kematian & Kelahiran (Tahun Lalu)")
        induk_dewasa = st.number_input("Total Dewasa Tahun Lalu", min_value=1, value=20)
        bayi_lahir = st.number_input("Bayi yang Lahir dari mereka", min_value=0, value=10)
        st.divider()
        bayi_awal = st.number_input("Total Bayi Tahun Lalu", min_value=1, value=50)
        bayi_hidup = st.number_input("Bayi yang hidup jadi Remaja", min_value=0, value=25)
        st.divider()
        remaja_awal = st.number_input("Total Remaja Tahun Lalu", min_value=1, value=30)
        remaja_hidup = st.number_input("Remaja yang hidup jadi Dewasa", min_value=0, value=24)
        st.divider()
        dewasa_awal = st.number_input("Total Dewasa (Selain yang mati tua)", min_value=1, value=20)
        dewasa_hidup = st.number_input("Dewasa yang bertahan hidup", min_value=0, value=18)

    # Kalkulasi Probabilitas
    f_dewasa = bayi_lahir / induk_dewasa
    s_bayi = bayi_hidup / bayi_awal
    s_remaja = remaja_hidup / remaja_awal
    s_dewasa = dewasa_hidup / dewasa_awal

    st.write("---")
    st.write("### Grafik Proyeksi (20 Tahun)")
    
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
    
    total_akhir = int(np.sum(riwayat[-1]))
    st.metric(f"Estimasi Populasi {st.session_state.nama_hewan} (Tahun ke-20)", f"{total_akhir} Ekor")

# ==========================================
# TAB 3: TEORI MATRIKS
# ==========================================
with menu3:
    st.write("### Penjelasan Matematis")
    st.write("Detail konversi data lapangan menjadi matriks probabilitas dan penentuan status kepunahan berbasis Nilai Eigen.")
    
    st.markdown("**1. Konversi Rasio Demografi**")
    st.write(f"- Laju Reproduksi: {bayi_lahir} / {induk_dewasa} = **{f_dewasa:.2f}**")
    st.write(f"- Probabilitas Hidup Bayi: {bayi_hidup} / {bayi_awal} = **{s_bayi:.2f}**")
    st.write(f"- Probabilitas Hidup Remaja: {remaja_hidup} / {remaja_awal} = **{s_remaja:.2f}**")
    st.write(f"- Probabilitas Hidup Dewasa: {dewasa_hidup} / {dewasa_awal} = **{s_dewasa:.2f}**")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**2. Matriks Pertumbuhan (Ordo 3x3)**")
        st.dataframe(pd.DataFrame(matriks_leslie).style.format("{:.2f}"))
    with col_b:
        st.markdown("**3. Vektor Populasi (Ordo 3x1)**")
        st.dataframe(pd.DataFrame(st.session_state.populasi_awal, index=["Bayi", "Remaja", "Dewasa"], columns=["Ekor"]))
        
    st.markdown("---")
    st.markdown("**4. Ekstraksi Nilai Eigen**")
    st.write("Berdasarkan persamaan $Ax = \lambda x$, status kelestarian spesies ditentukan oleh nilai eigen dominan ($\lambda$).")
    
    nilai_eigen, vektor_eigen = np.linalg.eig(matriks_leslie)
    eigen_dominan = max(np.real(nilai_eigen))
    
    st.markdown(f"**Nilai Eigen Dominan ($\lambda$) = {eigen_dominan:.4f}**")
    
    if eigen_dominan > 1:
        st.success(f"Status SDG 15: $\lambda > 1$ (Lestari). Populasi {st.session_state.nama_hewan} mengalami tren pertumbuhan.")
    elif eigen_dominan == 1:
        st.warning(f"Status SDG 15: $\lambda = 1$ (Stabil). Populasi {st.session_state.nama_hewan} stagnan.")
    else:
        st.error(f"Status SDG 15: $\lambda < 1$ (Kritis). Populasi {st.session_state.nama_hewan} terancam punah.")