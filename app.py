import streamlit as st
import numpy as np
import pandas as pd

# Konfigurasi Halaman Web
st.set_page_config(page_title="Optimasi Pupuk - SDG 2", page_icon="🌱", layout="centered")

# Header Aplikasi
st.title("🌱 Aplikasi Optimasi Pupuk Organik")
st.subheader("Penerapan Aljabar Linier (SPL) untuk Mendukung SDG 2: Zero Hunger")

st.markdown("""
Aplikasi ini membantu kelompok tani memformulasikan takaran campuran 3 jenis kompos cair untuk mendapatkan nutrisi tanah yang presisi. 
Perhitungan ini menggunakan metode **Sistem Persamaan Linear (SPL)** yang dimodelkan ke dalam matriks.
""")

st.divider()

# Membagi layout menjadi 2 kolom untuk Input
col1, col2 = st.columns(2)

with col1:
    st.write("### Kandungan Nutrisi per Liter")
    st.caption("Matriks Koefisien (A)")
    
    # Matriks N, P, K untuk Kompos A, B, C
    matriks_A = np.array([
        [1, 2, 1], 
        [2, 1, 1], 
        [1, 1, 2]
    ])
    
    # Menampilkan matriks ke dalam tabel agar lebih rapi
    df_A = pd.DataFrame(
        matriks_A, 
        columns=["Kompos A", "Kompos B", "Kompos C"], 
        index=["Nitrogen (N)", "Fosfor (P)", "Kalium (K)"]
    )
    st.dataframe(df_A, use_container_width=True)

with col2:
    st.write("### Target Nutrisi Lahan")
    st.caption("Vektor Konstanta (B) - Silakan Ubah Nilai")
    
    # Input interaktif untuk Vektor B
    target_N = st.number_input("Kebutuhan Nitrogen (N)", value=14, step=1)
    target_P = st.number_input("Kebutuhan Fosfor (P)", value=13, step=1)
    target_K = st.number_input("Kebutuhan Kalium (K)", value=17, step=1)
    
    vektor_B = np.array([target_N, target_P, target_K])

st.divider()

# Menampilkan representasi matematis
st.write("### Representasi Matematis ($AX = B$)")
st.latex(rf"""
\begin{bmatrix} 1 & 2 & 1 \\ 2 & 1 & 1 \\ 1 & 1 & 2 \end{bmatrix}
\begin{bmatrix} x \\ y \\ z \end{bmatrix} =
\begin{bmatrix} {target_N} \\ {target_P} \\ {target_K} \end{bmatrix}
""")

# Tombol Eksekusi
if st.button("Hitung Solusi Optimasi 🚀", type="primary", use_container_width=True):
    try:
        # Proses perhitungan invers matriks dan SPL menggunakan NumPy
        solusi = np.linalg.solve(matriks_A, vektor_B)
        
        st.success("✅ Perhitungan Aljabar Linier Berhasil! Berikut adalah takaran pupuk yang dibutuhkan:")
        
        # Menampilkan hasil (Nilai X, Y, Z) dengan kartu metrik yang estetik
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric(label="Kompos A ($x$)", value=f"{solusi[0]:.1f} Liter")
        res_col2.metric(label="Kompos B ($y$)", value=f"{solusi[1]:.1f} Liter")
        res_col3.metric(label="Kompos C ($z$)", value=f"{solusi[2]:.1f} Liter")
        
    except np.linalg.LinAlgError:
        # Menangani error jika matriks singular (determinan = 0)
        st.error("Gagal: Sistem persamaan tidak memiliki solusi unik (Matriks Singular).")