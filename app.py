import streamlit as st
import numpy as np
import pandas as pd

# --- 1. KONFIGURASI TAMPILAN WEB ---
st.set_page_config(page_title="Eco-Rank | SDG 15", layout="wide", page_icon="🐆")

st.markdown("""
    <style>
    .judul { font-size: 2.8rem; font-weight: 900; color: #1E4620; text-align: center; margin-bottom: 0px; }
    .subjudul { font-size: 1.2rem; color: #4A7C59; text-align: center; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="judul">🐆 Eco-Rank: Deteksi Spesies Kunci</p>', unsafe_allow_html=True)
st.markdown('<p class="subjudul">Analisis Sentralitas Ekosistem Hutan (SDG 15) Menggunakan Matriks & Vektor Eigen</p>', unsafe_allow_html=True)

# --- 2. PANEL INPUT (SIDEBAR) ---
st.sidebar.header("⚙️ Kekuatan Interaksi Matriks")
st.sidebar.write("Atur seberapa besar ketergantungan (aliran energi) antar spesies di ekosistem ini.")

st.sidebar.subheader("Tingkat Konsumsi Herbivora:")
w_pohon_monyet = st.sidebar.slider("Ketergantungan Monyet pada Pohon", 0.0, 5.0, 3.0)
w_pohon_rangkong = st.sidebar.slider("Ketergantungan Rangkong pada Pohon", 0.0, 5.0, 2.0)

st.sidebar.subheader("Tingkat Konsumsi Karnivora:")
w_monyet_macan = st.sidebar.slider("Macan Dahan memangsa Monyet", 0.0, 5.0, 4.0)
w_rangkong_macan = st.sidebar.slider("Macan Dahan memangsa Rangkong", 0.0, 5.0, 1.5)
w_macan_harimau = st.sidebar.slider("Harimau memangsa Macan Dahan", 0.0, 5.0, 5.0)

# --- 3. LOGIKA MATEMATIKA (ALJABAR LINIER) ---
spesies = ["Pohon Ara", "Monyet", "Burung Rangkong", "Macan Dahan", "Harimau Sumatera"]

# Membentuk Matriks Ketetanggaan Berbobot (Adjacency Matrix) 5x5
# Baris: Dimakan oleh, Kolom: Yang memakan
A = np.array([
    [0.0, w_pohon_monyet, w_pohon_rangkong, 0.0, 0.0],
    [0.0, 0.0, 0.0, w_monyet_macan, 0.0],
    [0.0, 0.0, 0.0, w_rangkong_macan, 0.0],
    [0.0, 0.0, 0.0, 0.0, w_macan_harimau],
    [0.0, 0.0, 0.0, 0.0, 0.0]
])

# Agar Vektor Eigen bekerja sempurna layaknya PageRank, matriks harus distabilkan (Damping Factor / Ekosistem Terbuka)
# Kita tambahkan nilai kecil agar tidak ada baris/kolom yang benar-benar 0
A = A + 0.1 

# --- 4. TAMPILAN HASIL (DASHBOARD) ---
tab_grafik, tab_teori = st.tabs(["📊 DASHBOARD PERINGKAT", "🧮 BUKTI MATRIKS & VEKTOR EIGEN"])

with tab_grafik:
    col_chart, col_data = st.columns([2, 1])
    
    # EKSEKUSI PENCARIAN NILAI & VEKTOR EIGEN
    nilai_eigen, vektor_eigen = np.linalg.eig(A)
    
    # Ambil Vektor Eigen yang bersesuaian dengan Nilai Eigen Terbesar
    idx_max = np.argmax(np.abs(nilai_eigen))
    vektor_sentralitas = np.abs(np.real(vektor_eigen[:, idx_max]))
    
    # Normalisasi skor menjadi persentase (Total 100%)
    skor_akhir = (vektor_sentralitas / np.sum(vektor_sentralitas)) * 100
    
    df_ranking = pd.DataFrame({
        "Spesies": spesies,
        "Skor Kepentingan (%)": skor_akhir
    }).sort_values(by="Skor Kepentingan (%)", ascending=False).reset_index(drop=True)

    with col_chart:
        st.write("### 🏆 Peringkat Spesies Kunci Ekosistem")
        st.bar_chart(df_ranking.set_index("Spesies"))
        st.info("💡 **Analisis SDG 15:** Geser kekuatan rantai makanan di panel kiri. Spesies dengan persentase tertinggi adalah **Spesies Kunci**. Jika pemerintah membiarkan spesies tersebut punah, seluruh jaring-jaring kehidupan di hutan ini akan runtuh berantakan!")
        
    with col_data:
        st.write("### 📋 Tabel Vektor Sentralitas")
        st.dataframe(df_ranking.style.format({"Skor Kepentingan (%)": "{:.2f}%"}), use_container_width=True)
        spesies_kunci = df_ranking.iloc[0]["Spesies"]
        st.error(f"🚨 **PRIORITAS KONSERVASI: {spesies_kunci}**")

with tab_teori:
    st.write("### Landasan Teori: Vektor Eigen Utama (Principal Eigenvector)")
    
    st.write("#### 1. Pembentukan Matriks Ekosistem ($A$)")
    st.write("Nilai-nilai dari input *slider* disusun menjadi **Matriks Ketetanggaan** berordo $5 \\times 5$:")
    df_A = pd.DataFrame(A, index=spesies, columns=spesies)
    st.dataframe(df_A.style.format("{:.1f}"))
    
    st.write("#### 2. Persamaan Karakteristik & Vektor Eigen ($Ax = \lambda x$)")
    st.write("Menghitung tingkat kepentingan hewan tidak bisa hanya dengan menjumlahkan siapa memakan siapa (skalar). Hewan yang jarang dimakan, namun dimakan oleh *predator yang sangat penting*, akan mendapatkan skor yang tinggi. Hal ini dipecahkan menggunakan komputasi matriks Vektor Eigen.")
    
    st.success(f"Sistem menemukan Nilai Eigen Utama ($\lambda$) = **{np.real(nilai_eigen[idx_max]):.4f}**")
    st.write("Vektor Eigen yang bersesuaian dengan Nilai Eigen tersebut kemudian diekstrak, dan itulah yang menjadi **Skor Kepentingan** pada grafik di halaman depan.")