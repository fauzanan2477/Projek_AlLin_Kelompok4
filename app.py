import streamlit as st
import numpy as np
import pandas as pd

# --- 1. PENGATURAN HALAMAN (RAPI DI TENGAH) ---
st.set_page_config(page_title="Simulasi Ekologi SDG 15", layout="centered")

# CSS minimalis agar tab di atas mirip Kompas dan font lebih natural
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    /* Membuat tulisan tab menu lebih besar */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.15rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. JUDUL HALAMAN ---
st.markdown("<h2 style='text-align: center; color: #2E86C1;'>Simulasi Ekologi Satwa (SDG 15)</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Pemodelan Matriks Berdasarkan Data Kelahiran & Kematian</p>", unsafe_allow_html=True)
st.write("---")

# --- 3. MENU NAVIGASI (DI ATAS) ---
menu1, menu2, menu3 = st.tabs([
    "Berita Utama", 
    "Simulasi & Input Data", 
    "Hitungan Matriks (Teori)"
])

# --- 4. PENYIMPANAN DATA SEMENTARA ---
if 'nama_hewan' not in st.session_state:
    st.session_state.nama_hewan = "Harimau Sumatera"
if 'populasi_awal' not in st.session_state:
    st.session_state.populasi_awal = [50, 30, 20] # Bayi, Remaja, Dewasa

# ==========================================
# HALAMAN 1: BERANDA
# ==========================================
with menu1:
    st.write("### Pilih Hewan yang Dianalisis")
    st.write("Ketik nama hewan di bawah ini. Seluruh laporan dan hitungan akan otomatis menyesuaikan dengan hewan yang kamu pilih.")
    
    input_hewan = st.text_input("Nama Hewan:", st.session_state.nama_hewan)
    st.session_state.nama_hewan = input_hewan
    
    st.success(f"Sistem sekarang dikonfigurasi untuk menganalisis populasi **{st.session_state.nama_hewan}**.")

# ==========================================
# HALAMAN 2: SIMULASI & INPUT DATA MANUAL
# ==========================================
with menu2:
    st.write(f"### Masukkan Data Historis {st.session_state.nama_hewan}")
    st.write("Masukkan jumlah hewan secara nyata (ekor). Sistem akan otomatis menghitung nilai peluangnya (desimal) untuk dimasukkan ke dalam matriks.")
    
    # Membagi layar jadi 2 kolom di tengah
    kolom_kiri, kolom_kanan = st.columns(2)
    
    with kolom_kiri:
        st.info("**1. Populasi Saat Ini**")
        bayi_skrg = st.number_input("Jumlah Bayi Saat Ini", min_value=0, value=st.session_state.populasi_awal[0])
        remaja_skrg = st.number_input("Jumlah Remaja Saat Ini", min_value=0, value=st.session_state.populasi_awal[1])
        dewasa_skrg = st.number_input("Jumlah Dewasa Saat Ini", min_value=0, value=st.session_state.populasi_awal[2])
        st.session_state.populasi_awal = [bayi_skrg, remaja_skrg, dewasa_skrg]
        
    with kolom_kanan:
        st.info("**2. Data Kelahiran & Kematian (Tahun Lalu)**")
        # Input manual angka aslinya
        induk_dewasa = st.number_input("Total Dewasa Tahun Lalu", min_value=1, value=20)
        bayi_lahir = st.number_input("Bayi yang Lahir dari mereka", min_value=0, value=5)
        
        bayi_awal = st.number_input("Total Bayi Tahun Lalu", min_value=1, value=50)
        bayi_hidup = st.number_input("Bayi yang hidup jadi Remaja", min_value=0, value=25)
        
        remaja_awal = st.number_input("Total Remaja Tahun Lalu", min_value=1, value=30)
        remaja_hidup = st.number_input("Remaja yang hidup jadi Dewasa", min_value=0, value=24)
        
        dewasa_awal = st.number_input("Total Dewasa (Selain yang mati tua)", min_value=1, value=20)
        dewasa_hidup = st.number_input("Dewasa yang bertahan hidup", min_value=0, value=18)

    # Menghitung probabilitas (Desimal) dari angka manual di atas
    f_dewasa = bayi_lahir / induk_dewasa
    s_bayi = bayi_hidup / bayi_awal
    s_remaja = remaja_hidup / remaja_awal
    s_dewasa = dewasa_hidup / dewasa_awal

    st.write("---")
    st.write("### Grafik Proyeksi 20 Tahun ke Depan")
    
    # Membentuk Matriks Leslie dari hasil hitungan manual tadi
    matriks_leslie = np.array([
        [0, 0, f_dewasa],
        [s_bayi, 0, 0],
        [0, s_remaja, s_dewasa]
    ])
    
    vektor_populasi = np.array(st.session_state.populasi_awal)
    riwayat = [vektor_populasi]
    
    # Looping perkalian matriks untuk 20 tahun
    for _ in range(20):
        vektor_populasi = np.dot(matriks_leslie, vektor_populasi)
        riwayat.append(vektor_populasi)
        
    df_proyeksi = pd.DataFrame(riwayat, columns=["Bayi", "Remaja", "Dewasa"])
    st.line_chart(df_proyeksi)
    
    total_akhir = int(np.sum(riwayat[-1]))
    st.write(f"Estimasi jumlah {st.session_state.nama_hewan} 20 tahun lagi: **{total_akhir} ekor**.")

# ==========================================
# HALAMAN 3: TEORI UNTUK DOSEN
# ==========================================
with menu3:
    st.write(f"### Pembuktian Aljabar Linier")
    st.write("Ini adalah halaman untuk menjelaskan kepada dosen dari mana asal usul nilai desimal pada matriks dan bagaimana cara membuktikan hewan tersebut punah atau tidak menggunakan **Nilai Eigen**.")
    
    st.markdown("**1. Konversi Data Manual menjadi Nilai Peluang (Desimal)**")
    st.write(f"- **Tingkat Kelahiran:** {bayi_lahir} bayi lahir dibagi {induk_dewasa} induk = **{f_dewasa:.2f}**")
    st.write(f"- **Peluang Hidup Bayi:** {bayi_hidup} hidup dibagi {bayi_awal} total bayi = **{s_bayi:.2f}**")
    st.write(f"- **Peluang Hidup Remaja:** {remaja_hidup} hidup dibagi {remaja_awal} total remaja = **{s_remaja:.2f}**")
    st.write(f"- **Peluang Hidup Dewasa:** {dewasa_hidup} hidup dibagi {dewasa_awal} total dewasa = **{s_dewasa:.2f}**")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**2. Matriks Pertumbuhan yang Terbentuk**")
        st.dataframe(pd.DataFrame(matriks_leslie).style.format("{:.2f}"))
    with col_b:
        st.markdown("**3. Vektor Populasi Awal**")
        st.dataframe(pd.DataFrame(st.session_state.populasi_awal, index=["Bayi", "Remaja", "Dewasa"], columns=["Ekor"]))
        
    st.markdown("---")
    st.markdown("**4. Mencari Nilai Eigen**")
    st.write("Untuk menyimpulkan status SDG 15 tanpa melihat grafik, kita mencari Nilai Eigen ($\lambda$) terbesar dari Matriks di atas dengan persamaan $Ax = \lambda x$.")
    
    # Eksekusi Nilai Eigen sesuai permintaan dosen di PDF
    nilai_eigen, vektor_eigen = np.linalg.eig(matriks_leslie)
    eigen_dominan = max(np.real(nilai_eigen))
    
    st.markdown(f"#### Hasil Nilai Eigen Terbesar ($\lambda$) = {eigen_dominan:.4f}")
    
    if eigen_dominan > 1:
        st.success(f"**Kesimpulan:** Karena $\lambda > 1$, laju pertumbuhan positif. Populasi {st.session_state.nama_hewan} **LESTARI**.")
    elif eigen_dominan == 1:
        st.warning(f"**Kesimpulan:** Karena $\lambda = 1$, populasi {st.session_state.nama_hewan} **STABIL** (tidak bertambah/berkurang).")
    else:
        st.error(f"**Kesimpulan:** Karena $\lambda < 1$, tingkat kematian lebih tinggi. {st.session_state.nama_hewan} **TERANCAM PUNAH**.")