import streamlit as st
import numpy as np
import pandas as pd
import time

# --- 1. KONFIGURASI & TEMA DASHBOARD ---
st.set_page_config(page_title="Prediksi Karhutla", layout="wide", page_icon="🌲")

st.markdown("""
    <style>
    .main-title { font-size: 3rem; font-weight: 900; color: #d35400; text-align: center; margin-bottom: 0; }
    .sub-title { font-size: 1.2rem; color: #e67e22; text-align: center; margin-bottom: 30px; }
    .metric-card { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border-left: 5px solid #d35400; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🌲 Sistem Prediksi Karhutla</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Simulasi Mitigasi Bencana (SDG 15) Berbasis Aljabar Linier & SPL</p>', unsafe_allow_html=True)

# --- 2. DATA HISTORIS (BISA DI-EDIT AUDIENS) ---
st.write("### 📅 1. Perekaman Data Historis (Interaktif)")
st.info("Ketik langsung pada tabel untuk mengubah data historis. Algoritma matriks akan beradaptasi secara otomatis!")

data_awal = pd.DataFrame({
    "Bulan": ["Januari", "Februari", "Maret", "April", "Mei", "Juni"],
    "Suhu Udara (°C)": [31.0, 31.5, 32.5, 33.5, 34.5, 35.5],
    "Curah Hujan (mm)": [250, 200, 150, 80, 40, 10],
    "Luas Terbakar (Ha)": [20, 50, 150, 500, 1200, 3500]
})

df_edit = st.data_editor(data_awal, num_rows="dynamic", use_container_width=True)

# --- 3. KOMPUTASI ALJABAR LINIER (CORE ENGINE) ---
try:
    Y = df_edit["Luas Terbakar (Ha)"].values
    X = np.column_stack((np.ones(len(df_edit)), df_edit["Suhu Udara (°C)"], df_edit["Curah Hujan (mm)"]))

    # SPL & Invers Matriks: Beta = (X^T * X)^-1 * X^T * Y
    X_T = X.T
    X_T_X_inv = np.linalg.inv(np.dot(X_T, X))
    Beta = np.dot(X_T_X_inv, np.dot(X_T, Y))
    sukses = True
except np.linalg.LinAlgError:
    st.error("🚨 Matriks Singular! Determinan bernilai 0. Pastikan data suhu/hujan bervariasi.")
    sukses = False

if sukses:
    # --- 4. PANEL SIMULASI INTERAKTIF ---
    st.divider()
    st.write("### 🎮 2. Simulasi Prediksi Masa Depan")
    st.write("Pilih skenario cuaca untuk bulan depan, atau atur sendiri angkanya secara kustom untuk melihat respon sistem!")
    
    # Fitur Interaktif: Pilihan Skenario
    skenario = st.radio("Pilih Skenario Cuaca BMKG:", 
                        ["⛅ Normal (Kemarau Biasa)", "🔥 El Nino Ekstrem (Kering & Panas)", "🌧️ La Nina (Basah)", "🎛️ Kustom (Geser Sendiri)"], 
                        horizontal=True)
    
    col_kiri, col_kanan = st.columns([1, 2])
    
    with col_kiri:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        # Logika Skenario
        if skenario == "⛅ Normal (Kemarau Biasa)":
            suhu = st.slider("Suhu (°C)", 30.0, 42.0, 34.0, disabled=True)
            hujan = st.slider("Hujan (mm)", 0.0, 300.0, 100.0, disabled=True)
        elif skenario == "🔥 El Nino Ekstrem (Kering & Panas)":
            suhu = st.slider("Suhu (°C)", 30.0, 42.0, 38.5, disabled=True)
            hujan = st.slider("Hujan (mm)", 0.0, 300.0, 0.0, disabled=True)
        elif skenario == "🌧️ La Nina (Basah)":
            suhu = st.slider("Suhu (°C)", 30.0, 42.0, 31.0, disabled=True)
            hujan = st.slider("Hujan (mm)", 0.0, 300.0, 250.0, disabled=True)
        else:
            suhu = st.slider("Suhu (°C)", 30.0, 42.0, 35.0, 0.5)
            hujan = st.slider("Hujan (mm)", 0.0, 300.0, 50.0, 10.0)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_kanan:
        # Menghitung Prediksi (Dot Product Matrix)
        prediksi_y = np.dot(np.array([1, suhu, hujan]), Beta)
        hasil_prediksi = max(0, prediksi_y)
        
        # UI Metrik Interaktif
        m1, m2, m3 = st.columns(3)
        m1.metric(label="Suhu Terpantau", value=f"{suhu}°C")
        m2.metric(label="Hujan Terpantau", value=f"{hujan} mm")
        m3.metric(label="Prediksi Lahan Terbakar", value=f"{hasil_prediksi:,.0f} Ha", delta=f"{hasil_prediksi - df_edit['Luas Terbakar (Ha)'].iloc[-1]:,.0f} dari bulan lalu", delta_color="inverse")
        
        # Progress Bar Bahaya (Maksimal 5000 Hektar untuk visualisasi)
        persentase_bahaya = min(hasil_prediksi / 5000.0, 1.0)
        st.write("**Tingkat Kerusakan Ekosistem (SDG 15):**")
        progress_bar = st.progress(0)
        
        # Animasi Progress Bar
        for percent_complete in range(int(persentase_bahaya * 100)):
            time.sleep(0.01)
            progress_bar.progress(percent_complete + 1)
        
        # Indikator Status
        if hasil_prediksi > 2500:
            st.error("🚨 **STATUS: BENCANA NASIONAL (EL NINO)** - Evakuasi satwa liar dan kerahkan water-bombing!")
        elif hasil_prediksi > 800:
            st.warning("⚠️ **STATUS: SIAGA** - Tingkatkan patroli polisi hutan di titik rawan.")
        else:
            st.success("🌱 **STATUS: AMAN** - Ekosistem darat terkendali.")

    # --- 5. BUKTI MATEMATIKA UNTUK DOSEN ---
    with st.expander("Klik di sini untuk melihat Bukti Komputasi Aljabar Linier (Untuk Dosen)"):
        st.write("Sistem menemukan bobot fitur secara dinamis menggunakan rumus: $\\beta = (X^T X)^{-1} X^T Y$")
        c1, c2 = st.columns(2)
        c1.write("**1. Matriks Invers $(X^T X)^{-1}$**")
        c1.dataframe(pd.DataFrame(X_T_X_inv).style.format("{:.5f}"))
        c2.write("**2. Vektor Bobot Regresi (Beta)**")
        df_beta = pd.DataFrame(Beta, index=["Konstanta", "Bobot Suhu", "Bobot Hujan"], columns=["Nilai"])
        c2.dataframe(df_beta.style.format("{:.2f}"))