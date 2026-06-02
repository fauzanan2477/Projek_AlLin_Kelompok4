import streamlit as st
import numpy as np
import pandas as pd

# --- 1. KONFIGURASI HALAMAN (Wajib di baris paling atas) ---
st.set_page_config(page_title="CarbonWatch | SDG 13", layout="wide", page_icon="🌍")

# --- 2. MENU NAVIGASI ATAS (TOP MENU) ---
st.markdown('<h2 style="color:#22d3ee; text-align:center;">🌍 CARBONWATCH: Analisis Emisi CO₂ (SDG 13)</h2>', unsafe_allow_html=True)
st.write("---")

# Membuat menu pilihan berbentuk horizontal di atas
menu_pilihan = st.radio(
    "PILIH HALAMAN:",
    ["🏠 1. Dashboard Utama (Data & Tren)", "🎛️ 2. Kompresi Matriks (SVD)", "▦ 3. Analisis Nilai Eigen (PCA)"],
    horizontal=True
)
st.write("---")

# --- 3. DATABASE (BISA DI-EDIT) ---
# Kita taruh data di luar agar bisa diakses oleh semua halaman
kota = ["Jakarta", "Surabaya", "Bandung", "Medan", "Makassar"]
bulan = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun"]

# Jika belum ada data tersimpan, buat data default
if 'data_emisi' not in st.session_state:
    st.session_state.data_emisi = pd.DataFrame(
        [
            [8.2, 7.9, 8.5, 9.1, 9.4, 8.8],
            [5.1, 4.8, 5.3, 5.7, 6.0, 5.5],
            [3.4, 3.2, 3.6, 3.9, 4.1, 3.7],
            [4.6, 4.3, 4.8, 5.2, 5.5, 5.0],
            [2.8, 2.6, 2.9, 3.2, 3.4, 3.0],
        ], 
        index=kota, columns=bulan
    )

# Mengambil data dari memory (Session State)
df = st.session_state.data_emisi

# --- 4. LOGIKA PERPINDAHAN HALAMAN ---

# ==========================================
# HALAMAN 1: DASHBOARD UTAMA
# ==========================================
if menu_pilihan == "🏠 1. Dashboard Utama (Data & Tren)":
    st.subheader("📝 Tabel Data Emisi Karbon (Mt CO₂)")
    st.info("💡 **Interaktif:** Silakan klik dua kali pada angka di tabel untuk mengubah nilainya. Grafik dan perhitungan Aljabar Linier di halaman lain akan otomatis menyesuaikan!")
    
    # Tabel interaktif yang bisa diedit user
    df_diedit = st.data_editor(df, use_container_width=True)
    
    # Simpan perubahan ke memory
    st.session_state.data_emisi = df_diedit
    
    st.subheader("📈 Grafik Tren Emisi Bulanan")
    st.write("Arahkan mouse ke garis grafik untuk melihat detail angka secara interaktif.")
    # Streamlit line_chart butuh data di mana kolom adalah garis (kota) dan baris adalah sumbu X (bulan)
    # Jadi kita perlu men-transpose matriksnya (T)
    st.line_chart(df_diedit.T)


# ==========================================
# HALAMAN 2: KOMPRESI MATRIKS (SVD)
# ==========================================
elif menu_pilihan == "🎛️ 2. Kompresi Matriks (SVD)":
    st.subheader("🎛️ Dekomposisi Nilai Singular (Singular Value Decomposition)")
    st.write("Metode SVD ($A = U \cdot \Sigma \cdot V^T$) digunakan untuk membuang *noise* pada data cuaca/emisi.")
    
    A = df.values # Mengambil matriks angka
    
    # Slider interaktif
    k = st.slider("Tentukan jumlah rank (k) untuk merekonstruksi matriks:", min_value=1, max_value=5, value=2)
    
    # Perhitungan SVD
    U, S, Vt = np.linalg.svd(A, full_matrices=False)
    
    # Rekonstruksi matriks baru (Ak) berdasarkan rank k
    Ak = np.dot(U[:, :k], np.dot(np.diag(S[:k]), Vt[:k, :]))
    
    col1, col2 = st.columns(2)
    with col1:
        st.success("**Matriks Asli (A)**")
        st.dataframe(df)
        st.write("**Nilai Singular ($\Sigma$) yang ditemukan:**")
        st.write(S.round(3))
        
    with col2:
        st.warning(f"**Matriks Rekonstruksi Rank-{k} ($\hat{{A}}$)**")
        # Mengubah hasil numpy kembali ke wujud tabel Pandas
        df_Ak = pd.DataFrame(Ak, index=kota, columns=bulan)
        st.dataframe(df_Ak.style.format("{:.2f}"))
        
        # Menghitung Error / Kehilangan Data
        error = np.linalg.norm(A - Ak, 'fro')
        st.info(f"Tingkat Kehilangan Data (Error Frobenius): **{error:.3f}**")


# ==========================================
# HALAMAN 3: NILAI EIGEN (PCA)
# ==========================================
elif menu_pilihan == "▦ 3. Analisis Nilai Eigen (PCA)":
    st.subheader("▦ Analisis Nilai Eigen & Vektor Eigen")
    st.write("Dalam pemodelan iklim (*Principal Component Analysis*), matriks data akan dikalikan dengan transposenya untuk mencari **Matriks Kovarians**, lalu dihitung Nilai Eigennya untuk menemukan komponen utama (penyumbang emisi terbesar).")
    
    A = df.values
    # Perkalian Matriks (A dikali A Transpose)
    C = np.dot(A, A.T)
    
    # Mencari Nilai Eigen
    nilai_eigen, vektor_eigen = np.linalg.eigh(C)
    
    # Mengurutkan dari yang paling besar ke kecil
    nilai_eigen = nilai_eigen[::-1]
    
    # Tampilan hasil
    st.write("**Nilai Eigen yang Diperoleh ($\lambda$):**")
    df_eigen = pd.DataFrame({
        "Komponen": [f"λ {i+1}" for i in range(len(nilai_eigen))],
        "Besaran Variansi": nilai_eigen
    })
    st.dataframe(df_eigen.style.format({"Besaran Variansi": "{:.2f}"}), use_container_width=True)
    
    st.subheader("📊 Grafik Distribusi Nilai Eigen")
    # Bar chart interaktif bawaan Streamlit
    st.bar_chart(df_eigen.set_index("Komponen"))
    st.info("💡 **Analisis Ekologi (SDG 13):** Nilai Eigen pertama ($\lambda 1$) yang sangat tinggi menunjukkan bahwa pola tren emisi secara keseluruhan sangat didominasi oleh satu faktor utama (kemungkinan besar aktivitas industri di Jakarta & Surabaya).")