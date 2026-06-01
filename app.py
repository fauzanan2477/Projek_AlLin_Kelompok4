import streamlit as st
import numpy as np
import pandas as pd

# --- KONFIGURASI WEB ---
st.set_page_config(page_title="AI Fire-Predictor | SDG 15", layout="wide", page_icon="🔥")

st.markdown('<h1 style="color:#d35400; text-align:center;">🔥 AI Fire-Predictor (Machine Learning)</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#e67e22; font-size:1.2rem;">Prediksi Kebakaran Hutan (SDG 15) Menggunakan SPL & Invers Matriks</p>', unsafe_allow_html=True)

# --- 1. DATA HISTORIS DINAMIS ---
st.write("### ⚙️ 1. Matriks Data Historis Cuaca & Karhutla")
st.info("💡 **Tabel Interaktif:** Kamu bisa mengetik langsung di dalam tabel ini, menambah baris baru, atau menghapus data. Rumus Aljabar Linier akan menghitung ulang secara otomatis!")

# Data Default (Bisa diubah-ubah di web)
data_awal = pd.DataFrame({
    "Suhu Udara (°C)": [32.0, 33.5, 34.0, 35.5, 36.0, 37.0],
    "Curah Hujan (mm)": [200, 150, 100, 50, 20, 5],
    "Luas Terbakar (Hektar)": [10, 50, 120, 450, 800, 1500]
})

# Menampilkan tabel yang bisa di-edit (Dynamic Rows)
df_edit = st.data_editor(data_awal, num_rows="dynamic", use_container_width=True)

# --- 2. LOGIKA MATEMATIKA (ALJABAR LINIER) ---
try:
    # Membentuk Vektor Target Y (Luas Terbakar)
    Y = df_edit["Luas Terbakar (Hektar)"].values

    # Membentuk Matriks Fitur X (Kolom 1 adalah Konstanta angka 1)
    # Ordo Matriks X menyesuaikan jumlah baris yang ada di tabel
    X = np.column_stack((np.ones(len(df_edit)), df_edit["Suhu Udara (°C)"], df_edit["Curah Hujan (mm)"]))

    # RUMUS PERSAMAAN NORMAL (Normal Equation): Beta = (X^T * X)^-1 * X^T * Y
    X_T = X.T                                   # 1. Transpose Matriks X
    X_T_X = np.dot(X_T, X)                      # 2. Perkalian Matriks
    X_T_X_inv = np.linalg.inv(X_T_X)            # 3. MENCARI INVERS MATRIKS (ALIN INTI)
    X_T_Y = np.dot(X_T, Y)                      # 4. Perkalian Vektor
    Beta = np.dot(X_T_X_inv, X_T_Y)             # 5. Hasil Vektor Koefisien SPL (Beta)

    sukses_hitung = True
except np.linalg.LinAlgError:
    st.error("🚨 Gagal memproses! Determinan matriks bernilai 0 (Matriks Singular). Pastikan data di tabel bervariasi.")
    sukses_hitung = False

if sukses_hitung:
    # --- 3. BUKTI KOMPUTASI UNTUK DOSEN ---
    st.divider()
    st.write("### 🧮 2. Bukti Operasi Aljabar Linier")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Matriks Invers $(X^T X)^{-1}$**")
        st.dataframe(pd.DataFrame(X_T_X_inv).style.format("{:.4f}"))
        
    with col2:
        st.write("**Vektor Solusi SPL ($\beta$)**")
        df_beta = pd.DataFrame(Beta, index=["Konstanta (b0)", "Bobot Suhu (b1)", "Bobot Hujan (b2)"], columns=["Nilai"])
        st.dataframe(df_beta.style.format("{:.2f}"))
        
    with col3:
        st.write("**Rumus AI yang Terbentuk:**")
        st.latex(r"Y = \beta_0 + \beta_1 X_1 + \beta_2 X_2")
        st.info("Invers matriks berhasil memecahkan Sistem Persamaan Linier yang kompleks menjadi sebuah rumus prediksi mutakhir!")

    # --- 4. DASHBOARD PREDIKSI INTERAKTIF ---
    st.divider()
    st.write("### 🔮 3. Simulator Prediksi Kebakaran Hutan")
    
    col_input1, col_input2, col_hasil = st.columns(3)
    with col_input1:
        input_suhu = st.number_input("Prediksi Suhu Ekstrem (°C):", value=38.0, step=0.5)
    with col_input2:
        input_hujan = st.number_input("Prediksi Curah Hujan (mm):", value=0.0, step=10.0)

    with col_hasil:
        # Menghitung prediksi menggunakan perkalian Vektor (Dot Product)
        vektor_input = np.array([1, input_suhu, input_hujan])
        prediksi_y = np.dot(vektor_input, Beta)
        
        st.warning("🚨 **Estimasi Luas Hutan Terbakar:**")
        st.header(f"{max(0, prediksi_y):,.0f} Hektar")
        if prediksi_y > 1000:
            st.error("🔥 STATUS: SIAGA 1 (Darurat SDG 15!)")
        else:
            st.success("🌱 STATUS: Aman Terkendali")