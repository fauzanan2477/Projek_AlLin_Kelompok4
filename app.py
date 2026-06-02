import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURASI HALAMAN (WIDE & WHITE BACKGROUND) ---
st.set_page_config(page_title="Sistem Pakar Gizi & SPL", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 95% !important; }
    h1, h2, h3, h4, p, span, div, label { color: #2C3E50 !important; font-family: 'Inter', sans-serif !important; }
    
    .header-box { border-bottom: 4px solid #27AE60; padding-bottom: 15px; margin-bottom: 25px; }
    .header-box h1 { font-weight: 800; font-size: 2.2rem; color: #27AE60 !important; margin: 0; }
    .header-box p { font-size: 1rem; color: #7F8C8D !important; margin-top: 5px; }
    
    .stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #ECF0F1; }
    .stTabs [data-baseweb="tab"] { background-color: #FFFFFF; font-weight: 700; font-size: 1.1rem; }
    .stTabs [aria-selected="true"] { border-bottom: 4px solid #27AE60; color: #27AE60 !important; }
    
    /* Box untuk hasil target */
    .target-box { background-color: #F9FBFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 20px; text-align: center; }
    .target-box h2 { color: #27AE60 !important; font-size: 2rem; margin:0; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HEADER ---
st.markdown("""
<div class="header-box">
    <h1>🥗 Sistem Pakar Perhitungan Gizi & Aljabar Linier</h1>
    <p>SDGs 3: Kehidupan Sehat dan Sejahtera | Basis: Buku Gizi (Dr. Betty Yosephin) & SPL Matriks (ITB)</p>
</div>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE (Penyimpanan Data Sementara) ---
if 'target_nutrisi' not in st.session_state:
    st.session_state['target_nutrisi'] = {"energi": 2000, "protein": 75, "lemak": 65, "karbo": 275, "serat": 25}

if 'db_gizi' not in st.session_state:
    st.session_state['db_gizi'] = pd.DataFrame({
        "Bahan Makanan": ["Nasi Putih", "Ayam Broiler", "Telur Ayam", "Susu", "Kangkung"],
        "Energi": [1.30, 2.39, 1.43, 0.42, 0.18],
        "Protein": [0.027, 0.27, 0.13, 0.034, 0.026],
        "Lemak": [0.003, 0.13, 0.10, 0.01, 0.002],
        "Karbohidrat": [0.28, 0.0, 0.007, 0.05, 0.031],
        "Serat": [0.004, 0.0, 0.0, 0.0, 0.021]
    })

# --- 4. TABS NAVBAR ---
tab1, tab2, tab3 = st.tabs(["👤 1. Kalkulator Kebutuhan Personal", "🧮 2. Matriks SPL Porsi Makanan", "📚 3. Dasar Teori"])

# ==========================================
# TAB 1: KALKULATOR PERSONAL (Berdasarkan Buku)
# ==========================================
with tab1:
    st.write("### Masukkan Data Fisik Anda")
    st.caption("Sistem akan menghitung Total Kebutuhan Energi (Target Vektor B) menggunakan formula medis standar.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    with col2: umur = st.number_input("Umur (Tahun)", min_value=10, max_value=100, value=20)
    with col3: bb = st.number_input("Berat Badan (kg)", min_value=30.0, value=65.0)
    with col4: tb = st.number_input("Tinggi Badan (cm)", min_value=120.0, value=170.0)
    
    col_act, col_goal = st.columns(2)
    with col_act:
        aktivitas = st.selectbox("Tingkat Aktivitas Fisik", [
            "Jarang olahraga (Sedentary)", 
            "Olahraga ringan (1-3 hari/minggu)", 
            "Olahraga sedang (3-5 hari/minggu)", 
            "Olahraga berat (6-7 hari/minggu)"
        ])
    with col_goal:
        tujuan = st.selectbox("Tujuan Berat Badan", [
            "Mempertahankan Berat Badan (Maintain)",
            "Menurunkan Berat Badan (Defisit Kalori)",
            "Menaikkan Berat Badan (Surplus Kalori)"
        ])
    
    if st.button("Hitung Target Gizi Pribadi", type="primary"):
        # 1. Hitung BMR (Mifflin-St Jeor Equation - Standar Medis)
        if jk == "Laki-laki":
            bmr = (10 * bb) + (6.25 * tb) - (5 * umur) + 5
        else:
            bmr = (10 * bb) + (6.25 * tb) - (5 * umur) - 161
            
        # 2. Kalikan dengan Faktor Aktivitas
        if "Jarang" in aktivitas: tdee = bmr * 1.2
        elif "ringan" in aktivitas: tdee = bmr * 1.375
        elif "sedang" in aktivitas: tdee = bmr * 1.55
        else: tdee = bmr * 1.725
        
        # 3. Penyesuaian Tujuan Berat Badan
        if "Menurunkan" in tujuan: tdee -= 500
        elif "Menaikkan" in tujuan: tdee += 500
        
        # 4. Hitung Makronutrien (Karbo 50%, Protein 20%, Lemak 30%)
        karbo = (tdee * 0.50) / 4
        protein = (tdee * 0.20) / 4
        lemak = (tdee * 0.30) / 9
        serat = 25 # Kebutuhan serat rata-rata harian
        
        # Simpan ke Session State untuk digunakan di Matriks SPL
        st.session_state['target_nutrisi'] = {
            "energi": round(tdee, 1), "protein": round(protein, 1), 
            "lemak": round(lemak, 1), "karbo": round(karbo, 1), "serat": serat
        }
        
        st.success("Target Vektor $B$ berhasil dihitung dan disimpan! Silakan lanjut ke Tab 2.")

    # Menampilkan Target Saat Ini
    st.markdown('<div class="target-box">', unsafe_allow_html=True)
    st.write("#### 🎯 Target Nutrisi Harian Anda (Vektor $B$)")
    t_col1, t_col2, t_col3, t_col4, t_col5 = st.columns(5)
    t = st.session_state['target_nutrisi']
    t_col1.metric("⚡ Energi", f"{t['energi']} kkal")
    t_col2.metric("🥩 Protein", f"{t['protein']} g")
    t_col3.metric("🥑 Lemak", f"{t['lemak']} g")
    t_col4.metric("🍚 Karbohidrat", f"{t['karbo']} g")
    t_col5.metric("🥬 Serat", f"{t['serat']} g")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 2: MATRIKS SPL (Berdasarkan Jurnal)
# ==========================================
with tab2:
    st.write("### 📝 Tabel Matriks Kandungan Gizi Makanan (Matriks $A$)")
    st.caption("Data interaktif: Anda bebas mengubah angka, menambah baris makanan baru, atau menghapus baris.")
    
    tabel_diedit = st.data_editor(st.session_state['db_gizi'], num_rows="dynamic", use_container_width=True, hide_index=True)
    st.session_state['db_gizi'] = tabel_diedit
    
    st.write("---")
    if st.button("🚀 Kalkulasi Porsi Makanan (Eliminasi Gauss-Jordan)", type="primary", use_container_width=True):
        st.write("### 📊 Hasil Komputasi Vektor Porsi ($X$)")
        
        # Mengambil Matriks A dari Tabel (Ditranspose)
        A_raw = tabel_diedit[["Energi", "Protein", "Lemak", "Karbohidrat", "Serat"]].values.T
        
        # Mengambil Target Vektor B dari Tab 1
        # Skala dibagi 100 menyesuaikan koefisien matriks pada jurnal
        t = st.session_state['target_nutrisi']
        B = np.array([t['energi']/100, t['protein']/100, t['lemak']/100, t['karbo']/100, t['serat']/100])
        
        nama_makanan = tabel_diedit["Bahan Makanan"].tolist()
        jumlah_variabel = len(nama_makanan)
        
        if jumlah_variabel == 5:
            try:
                # Penyelesaian SPL Murni
                X = np.linalg.solve(A_raw, B)
                
                kolom_hasil = st.columns(5)
                for i in range(5):
                    kolom_hasil[i].metric(label=f"{nama_makanan[i]}", value=f"{X[i]:.2f} Porsi")
                    
                st.write("")
                if any(porsi < 0 for porsi in X):
                    st.error("⚠️ **EVALUASI JURNAL:** Sistem mendeteksi adanya porsi bernilai **NEGATIF**. Ini membuktikan kelemahan fatal SPL murni di dunia nyata (tidak ada batas $\ge 0$). Logika aljabar benar, namun tidak valid secara biologis manusia.")
                else:
                    st.success("✅ Matriks diselesaikan dan kombinasi porsi bernilai positif (logis).")
            except np.linalg.LinAlgError:
                st.error("🚨 Matriks Singular! Sistem tidak menemukan solusi persilangan garis (Determinannya Nol).")
        else:
            st.warning(f"Sistem menggunakan pendekatan **Least Squares** karena matriks tidak berbentuk persegi ($5 \\times {jumlah_variabel}$).")
            try:
                X, _, _, _ = np.linalg.lstsq(A_raw, B, rcond=None)
                kolom_hasil = st.columns(jumlah_variabel)
                for i in range(jumlah_variabel):
                    kolom_hasil[i].metric(label=f"{nama_makanan[i]}", value=f"{X[i]:.2f} Porsi")
            except Exception as e:
                st.error(f"Error perhitungan matriks dinamis: {e}")

# ==========================================
# TAB 3: DASAR TEORI
# ==========================================
with tab3:
    st.write("### Landasan Matematika dan Teori Gizi")
    st.write("""
    1. **Tahap 1 (Buku Tuntunan Gizi):** Sistem meminta data biofisik pengguna untuk mencari target kalori menggunakan rumus BMR. Target ini kemudian didistribusikan ke makronutrisi dan dijadikan **Vektor Hasil ($B$)**.
    2. **Tahap 2 (Makalah ITB):** Sistem mengubah makanan menjadi matriks sistem persamaan linear $AX = B$. Vektor porsi $X$ dicari menggunakan kalkulasi matriks balikan (invers). 
    3. **Tujuan Utama:** Proyek ini menyimulasikan algoritma di balik aplikasi kesehatan dan membuktikan kelemahan SPL jika tidak diberi *constraint* dunia nyata.
    """)