import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Aljabar Energi (SDG 7)", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; max-width: 90%; }
    .header-box { border-bottom: 4px solid #F39C12; padding-bottom: 15px; margin-bottom: 25px; }
    .header-box h1 { font-weight: 800; font-size: 2.2rem; color: #F39C12; margin: 0; }
    .header-box p { font-size: 1.1rem; color: #555; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HEADER ---
st.markdown("""
<div class="header-box">
    <h1>☀️ Sistem Perencanaan Energi Bersih (Matriks Aljabar Linier)</h1>
    <p>Mendukung SDG 7 (Energi Bersih dan Terjangkau) | Penyelesaian SPL Matriks 3x3</p>
</div>
""", unsafe_allow_html=True)

# --- 3. DATABASE MATRIKS (Parameter Proyek) ---
if 'db_energi' not in st.session_state:
    st.session_state['db_energi'] = pd.DataFrame({
        "Jenis Pembangkit (Variabel)": ["PLTS (Surya - x1)", "PLTB (Angin - x2)", "PLTA (Air - x3)"],
        "Koefisien Energi": [1.0, 1.0, 1.0],
        "Biaya Pembangunan (Miliar/MW)": [10.0, 15.0, 20.0],
        "Penurunan Karbon (Ton/MW)": [5.0, 8.0, 12.0]
    })

# --- 4. LAYOUT APLIKASI ---
st.write("### 🎯 Langkah 1: Tentukan Target Pemerintah (Vektor B)")
col1, col2, col3 = st.columns(3)
with col1:
    target_energi = st.number_input("Target Total Energi (MW)", value=100)
with col2:
    target_biaya = st.number_input("Batas Anggaran (Miliar Rupiah)", value=1400)
with col3:
    target_karbon = st.number_input("Target Penurunan Emisi (Ton)", value=760)

st.write("---")
st.write("### 📝 Langkah 2: Parameter Pembangkit Listrik (Matriks A)")
st.caption("Anda dapat mengubah angka biaya dan karbon di tabel ini secara interaktif.")

tabel_diedit = st.data_editor(
    st.session_state['db_energi'], 
    use_container_width=True,
    hide_index=True
)

st.write("---")
if st.button("🚀 Hitung Kapasitas Pembangkit (Metode Eliminasi Matriks)", type="primary"):
    st.write("### 📊 Hasil Perhitungan Aljabar Linier (Vektor X)")
    
    # Membentuk Matriks A dari Tabel
    A = tabel_diedit[["Koefisien Energi", "Biaya Pembangunan (Miliar/MW)", "Penurunan Karbon (Ton/MW)"]].values.T
    
    # Membentuk Vektor B dari Input Target
    B = np.array([target_energi, target_biaya, target_karbon])
    
    try:
        # PEMECAHAN MATRIKS SPL
        X = np.linalg.solve(A, B)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Kapasitas PLTS (Surya)", f"{X[0]:.1f} Megawatt")
        c2.metric("Kapasitas PLTB (Angin)", f"{X[1]:.1f} Megawatt")
        c3.metric("Kapasitas PLTA (Air)", f"{X[2]:.1f} Megawatt")
        
        st.success("✅ Matriks 3x3 berhasil diselesaikan! Angka di atas adalah kapasitas pasti yang harus dibangun pemerintah agar sesuai dengan anggaran dan target emisi.")
        
    except np.linalg.LinAlgError:
        st.error("🚨 Matriks Singular! Parameter di tabel tidak dapat diselesaikan karena garis persamaannya sejajar (tidak berpotongan).")