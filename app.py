import streamlit as st
import numpy as np
import pandas as pd

# --- KONFIGURASI WEB ---
st.set_page_config(page_title="Borneo Fire-Predictor | SDG 15", layout="wide", page_icon="🔥")

st.markdown('<h1 style="color:#d35400; text-align:center;">🔥 Borneo Fire-Predictor</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#e67e22; font-size:1.2rem;">Prediksi Kebakaran Hutan Kalimantan (SDG 15) via Invers Matriks & SPL</p>', unsafe_allow_html=True)

# --- 1. DATA HISTORIS (MATRIKS SUMBER) ---
st.sidebar.header("📊 Data Historis (Kalimantan 2023)")
st.sidebar.write("Data ini dibaca oleh sistem sebagai Matriks X (Suhu & Hujan) dan Vektor Y (Hektar Terbakar).")

data = {
    "Bulan": ["Maret", "April", "Mei", "Juni", "Juli", "Agustus"],
    "Suhu (°C)": [32.0, 32.5, 33.1, 34.0, 35.2, 36.5],
    "Curah Hujan (mm)": [200, 150, 100, 80, 40, 20],
    "Terbakar (Hektar)": [1500, 2100, 3500, 6200, 11000, 23697]
}
df = pd.DataFrame(data)
st.sidebar.dataframe(df.set_index("Bulan"))

# --- 2. ALGORITMA ALJABAR LINIER (REGRESI MATRIKS) ---
# Membentuk Vektor Target Y
Y = df["Terbakar (Hektar)"].values

# Membentuk Matriks X (Kolom 1 berisi angka 1 untuk konstanta)
X = np.column_stack((np.ones(len(df)), df["Suhu (°C)"], df["Curah Hujan (mm)"]))

# Rumus Persamaan Normal: Beta = (X^T * X)^-1 * X^T * Y
X_T = X.T                                   # 1. Transpose Matriks X
X_T_X = np.dot(X_T, X)                      # 2. Perkalian X^T dengan X
X_T_X_inv = np.linalg.inv(X_T_X)            # 3. MENCARI INVERS MATRIKS (MATERI ALIN INTI)
X_T_Y = np.dot(X_T, Y)                      # 4. Perkalian X^T dengan Vektor Y
Beta = np.dot(X_T_X_inv, X_T_Y)             # 5. Hasil Akhir (Koefisien SPL)

# --- 3. BUKTI KOMPUTASI UNTUK DOSEN ---
st.divider()
st.write("### 🧮 Bukti Komputasi Aljabar Linier (Persamaan Normal)")
col1, col2, col3 = st.columns(3)

with col1:
    st.info("1. Matriks Fitur (X)")
    st.write("Terdiri dari kolom: Konstanta (1), Suhu, dan Curah Hujan.")
    st.dataframe(pd.DataFrame(X, columns=["Konstanta", "Suhu", "Hujan"]))

with col2:
    st.info("2. Invers Matriks $(X^T X)^{-1}$")
    st.write("Algoritma mencari invers dari perkalian matriks menggunakan `np.linalg.inv()`.")
    st.dataframe(pd.DataFrame(X_T_X_inv))

with col3:
    st.info("3. Solusi Vektor SPL ($\beta$)")
    st.write("Bobot yang ditemukan dari perkalian Invers Matriks:")
    df_beta = pd.DataFrame(Beta, index=["Konstanta (b0)", "Bobot Suhu (b1)", "Bobot Hujan (b2)"], columns=["Nilai"])
    st.dataframe(df_beta)

# --- 4. KALKULATOR PREDIKSI MASA DEPAN ---
st.divider()
st.write("### 🔮 Simulator Prediksi Karhutla Kalimantan (Masa Depan)")
st.write("Berdasarkan Invers Matriks di atas, sistem telah menemukan Sistem Persamaan Linier baru: **$Y = b_0 + b_1(Suhu) + b_2(Hujan)$**")

col_input1, col_input2, col_hasil = st.columns(3)
with col_input1:
    input_suhu = st.number_input("Prediksi Suhu Ekstrem (°C):", value=37.0, step=0.5)
with col_input2:
    input_hujan = st.number_input("Prediksi Curah Hujan (mm):", value=10.0, step=10.0)

with col_hasil:
    # Memasukkan input baru ke dalam perkalian matriks
    vektor_input = np.array([1, input_suhu, input_hujan])
    prediksi_y = np.dot(vektor_input, Beta)
    
    st.warning("🚨 **Estimasi Hutan Terbakar:**")
    st.header(f"{max(0, prediksi_y):,.0f} Hektar")
    if prediksi_y > 10000:
        st.error("Status: BENCANA NASIONAL (SDG 15 Terancam Kritis!)")
    else:
        st.success("Status: Terkendali (Masih dalam batas mitigasi)")