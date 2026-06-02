import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1. KONFIGURASI WEB
st.set_page_config(page_title="SDG 13 - Emisi CO2", layout="wide")
st.title("🌍 Monitoring Emisi CO₂ & Analisis Matriks")
st.write("Silakan **edit angka pada tabel di bawah ini**. Grafik, SVD, dan Nilai Eigen akan dihitung ulang secara otomatis!")

# 2. DATA DEFAULT (Bisa diubah oleh pengguna di Web)
cities = ["Jakarta", "Surabaya", "Bandung", "Medan", "Makassar"]
months = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun"]
default_data = np.array([
    [8.2, 7.9, 8.5, 9.1, 9.4, 8.8],
    [5.1, 4.8, 5.3, 5.7, 6.0, 5.5],
    [3.4, 3.2, 3.6, 3.9, 4.1, 3.7],
    [4.6, 4.3, 4.8, 5.2, 5.5, 5.0],
    [2.8, 2.6, 2.9, 3.2, 3.4, 3.0],
])

df = pd.DataFrame(default_data, index=cities, columns=months)

# FITUR UTAMA: Tabel yang bisa diedit layaknya Excel
st.subheader("📝 Tabel Data Emisi (Bisa Diedit)")
edited_df = st.data_editor(df, use_container_width=True)

# Ambil matriks angka yang sudah diedit
A = edited_df.values

# 3. DASHBOARD VISUALISASI (Dibagi menjadi 3 Tab)
tab1, tab2, tab3 = st.tabs(["📈 Tren Emisi", "🎛️ Dekomposisi SVD", "▦ Nilai Eigen (PCA)"])

with tab1:
    st.subheader("Tren Emisi CO₂ (Berdasarkan Tabel Saat Ini)")
    fig, ax = plt.subplots(figsize=(10, 4))
    for i, city in enumerate(cities):
        ax.plot(months, A[i], marker='o', lw=2, label=city)
    ax.set_ylabel("Mt CO₂")
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax.grid(alpha=0.3)
    st.pyplot(fig)

with tab2:
    st.subheader("Singular Value Decomposition (A = U Σ Vᵀ)")
    k = st.slider("Pilih Rank-k untuk Kompresi Matriks (Rekonstruksi):", min_value=1, max_value=5, value=2)
    
    # Rumus Aljabar Linear: SVD
    U, S, Vt = np.linalg.svd(A, full_matrices=False)
    Ak = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("1. Matriks Asli (A):")
        st.dataframe(pd.DataFrame(A, index=cities, columns=months))
        st.write("Nilai Singular (Σ):", S.round(2))
    with col2:
        st.write(f"2. Rekonstruksi Matriks Rank-{k} (Â):")
        st.dataframe(pd.DataFrame(Ak.round(2), index=cities, columns=months))

with tab3:
    st.subheader("Nilai Eigen dari Matriks Kovarians (C = A·Aᵀ)")
    st.write("Basis utama untuk algoritma *Principal Component Analysis (PCA)* di dalam jurnal iklim.")
    
    # Rumus Aljabar Linear: Nilai Eigen
    A_At = A @ A.T
    eigenvalues, _ = np.linalg.eigh(A_At)
    eigenvalues = eigenvalues[::-1] # Urutkan dari yang terbesar
    
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    ax2.bar([f"λ{i+1}" for i in range(len(eigenvalues))], eigenvalues, color='teal')
    ax2.set_ylabel("Besaran Variansi (Eigen)")
    st.pyplot(fig2)