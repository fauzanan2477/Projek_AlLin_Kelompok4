import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. KONFIGURASI WEB & CSS ---
st.set_page_config(page_title="Sistem Konservasi SDG 15", layout="wide", initial_sidebar_state="expanded")

# CSS untuk menyembunyikan elemen bawaan Streamlit agar terlihat seperti website mandiri
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    h1, h2, h3 {font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #2E4053;}
    </style>
""", unsafe_allow_html=True)

# --- 2. STATE MANAGEMENT (PENYIMPANAN DATA SEMENTARA) ---
if 'populasi_awal' not in st.session_state:
    st.session_state.populasi_awal = [150, 100, 250] # Bayi, Remaja, Dewasa

if 'parameter_matriks' not in st.session_state:
    # [Fekunditas Dewasa, Survival Bayi->Remaja, Survival Remaja->Dewasa, Survival Dewasa]
    st.session_state.parameter_matriks = [0.15, 0.60, 0.85, 0.90] 

# --- 3. MENU NAVIGASI (SIDEBAR) ---
with st.sidebar:
    st.title("Sistem Ekologi (SDG 15)")
    st.write("Pemodelan Populasi Spesies Rentan")
    st.markdown("---")
    menu_pilihan = st.radio(
        "Navigasi Halaman:",
        ["Beranda", "Manajemen Parameter", "Simulasi Proyeksi", "Spesifikasi Aljabar Linier"]
    )
    st.markdown("---")
    st.caption("Berbasis Matriks Leslie & Nilai Eigen")

# --- 4. KONTEN HALAMAN ---

if menu_pilihan == "Beranda":
    st.title("Ringkasan Konservasi Orangutan Kalimantan")
    st.write("Selamat datang di Sistem Proyeksi Ekologi. Sistem ini menggunakan **Matriks Leslie** untuk memprediksi pertumbuhan populasi Orangutan Kalimantan (*Pongo pygmaeus*) dalam beberapa dekade mendatang guna mendukung tujuan pembangunan berkelanjutan (SDG 15).")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Populasi Saat Ini", sum(st.session_state.populasi_awal), "Individu")
    col2.metric("Tingkat Kelahiran (Fekunditas)", f"{st.session_state.parameter_matriks[0]}", "Per Individu Dewasa")
    col3.metric("Status Konservasi", "Kritis (Critically Endangered)", delta_color="inverse")
    
    st.image("https://images.unsplash.com/photo-1549472614-6101c5cb5aeb?q=80&w=1200&auto=format&fit=crop", caption="Orangutan Kalimantan (Ilustrasi)", use_column_width=True)


elif menu_pilihan == "Manajemen Parameter":
    st.title("Manajemen Parameter Populasi")
    st.write("Sesuaikan vektor populasi awal dan matriks probabilitas kelangsungan hidup (Berdasarkan data observasi lapangan).")
    
    col_kiri, col_kanan = st.columns(2)
    
    with col_kiri:
        st.subheader("1. Vektor Populasi Awal")
        bayi = st.number_input("Jumlah Bayi (0-5 Tahun)", min_value=0, value=st.session_state.populasi_awal[0])
        remaja = st.number_input("Jumlah Remaja (6-15 Tahun)", min_value=0, value=st.session_state.populasi_awal[1])
        dewasa = st.number_input("Jumlah Dewasa (>15 Tahun)", min_value=0, value=st.session_state.populasi_awal[2])
        st.session_state.populasi_awal = [bayi, remaja, dewasa]
        
    with col_kanan:
        st.subheader("2. Matriks Kelangsungan Hidup")
        f_dewasa = st.slider("Laju Reproduksi Dewasa", 0.0, 1.0, st.session_state.parameter_matriks[0], 0.01)
        s_bayi = st.slider("Peluang Hidup (Bayi → Remaja)", 0.0, 1.0, st.session_state.parameter_matriks[1], 0.01)
        s_remaja = st.slider("Peluang Hidup (Remaja → Dewasa)", 0.0, 1.0, st.session_state.parameter_matriks[2], 0.01)
        s_dewasa = st.slider("Peluang Bertahan Hidup Dewasa", 0.0, 1.0, st.session_state.parameter_matriks[3], 0.01)
        st.session_state.parameter_matriks = [f_dewasa, s_bayi, s_remaja, s_dewasa]
        
    st.success("Data berhasil disimpan ke dalam memori sesi (Session State). Silakan buka menu 'Simulasi Proyeksi'.")


elif menu_pilihan == "Simulasi Proyeksi":
    st.title("Simulasi Proyeksi Masa Depan")
    
    rentang_tahun = st.slider("Rentang Proyeksi (Tahun ke depan)", 1, 50, 20)
    
    # Membangun Matriks Leslie (Ordo 3x3)
    f_dewasa, s_bayi, s_remaja, s_dewasa = st.session_state.parameter_matriks
    matriks_leslie = np.array([
        [0, 0, f_dewasa],
        [s_bayi, 0, 0],
        [0, s_remaja, s_dewasa]
    ])
    
    # Vektor Populasi (Ordo 3x1)
    vektor_populasi = np.array(st.session_state.populasi_awal)
    
    # Proses Iterasi Perkalian Matriks (N_t+1 = L * N_t)
    riwayat_populasi = [vektor_populasi]
    for _ in range(rentang_tahun):
        vektor_populasi = np.dot(matriks_leslie, vektor_populasi)
        riwayat_populasi.append(vektor_populasi)
        
    # Visualisasi
    df_proyeksi = pd.DataFrame(riwayat_populasi, columns=["Fase Bayi", "Fase Remaja", "Fase Dewasa"])
    df_proyeksi.index.name = "Tahun Ke-"
    
    st.line_chart(df_proyeksi)
    
    total_akhir = np.sum(riwayat_populasi[-1])
    st.metric("Estimasi Total Populasi di Akhir Proyeksi", f"{int(total_akhir)} Individu")


elif menu_pilihan == "Spesifikasi Aljabar Linier":
    st.title("Spesifikasi Model Aljabar Linier")
    st.write("Bagian ini memaparkan justifikasi matematis di balik simulasi populasi menggunakan matriks.")
    
    f_dewasa, s_bayi, s_remaja, s_dewasa = st.session_state.parameter_matriks
    matriks_leslie = np.array([
        [0, 0, f_dewasa],
        [s_bayi, 0, 0],
        [0, s_remaja, s_dewasa]
    ])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 1. Matriks Leslie ($L$)")
        st.write("Menyimpan tingkat reproduksi (baris pertama) dan kelangsungan hidup (diagonal bawah).")
        st.dataframe(pd.DataFrame(matriks_leslie).style.format("{:.2f}"))
        
    with col2:
        st.markdown("#### 2. Vektor Status Awal ($N_0$)")
        st.write("Jumlah populasi saat ini yang bertindak sebagai vektor awal.")
        st.dataframe(pd.DataFrame(st.session_state.populasi_awal, index=["Bayi", "Remaja", "Dewasa"], columns=["Jumlah"]))

    st.markdown("---")
    st.markdown("#### 3. Analisis Ekologi melalui Nilai Eigen ($\lambda$)")
    st.write("Untuk mengetahui apakah spesies ini akan punah atau lestari tanpa perlu melihat grafik, sistem menghitung **Nilai Eigen Dominan** dari Matriks $L$.")
    
    # Perhitungan Nilai Eigen
    nilai_eigen, vektor_eigen = np.linalg.eig(matriks_leslie)
    eigen_dominan = max(np.real(nilai_eigen))
    
    st.info(f"Ditemukan Nilai Eigen Maksimum (Laju Pertumbuhan Populasi) = **{eigen_dominan:.4f}**")
    
    if eigen_dominan > 1:
        st.success("**Status:** Spesies Lestari ($\lambda > 1$). Populasi akan terus bertambah.")
    elif eigen_dominan == 1:
        st.warning("**Status:** Stabil ($\lambda = 1$). Populasi tidak bertambah dan tidak berkurang.")
    else:
        st.error("**Status:** Terancam Punah ($\lambda < 1$). Intervensi konservasi sangat diperlukan.")