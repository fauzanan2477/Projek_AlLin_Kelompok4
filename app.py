import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Pakar Gizi & SPL", layout="wide", initial_sidebar_state="collapsed")

# CSS Disederhanakan (Hanya untuk Header dan Tab, agar Tabel tetap aman dan bisa diedit/dihapus)
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; max-width: 95%; }
    .header-box { border-bottom: 4px solid #27AE60; padding-bottom: 15px; margin-bottom: 25px; }
    .header-box h1 { font-weight: 800; font-size: 2.2rem; color: #27AE60; margin: 0; }
    .header-box p { font-size: 1rem; color: #7F8C8D; margin-top: 5px; }
    .target-box { background-color: #F9FBFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 20px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HEADER ---
st.markdown("""
<div class="header-box">
    <h1>🥗 Sistem Pakar Perhitungan Gizi & Aljabar Linier</h1>
    <p>SDGs 3: Kehidupan Sehat dan Sejahtera | Basis: Buku Gizi Klinis & Matriks Aljabar Linier</p>
</div>
""", unsafe_allow_html=True)

# --- 3. DATA SEMENTARA (Data Real per 100 gram) ---
if 'target_nutrisi' not in st.session_state:
    st.session_state['target_nutrisi'] = {"energi": 2000, "protein": 75, "lemak": 65, "karbo": 275, "serat": 25}

if 'db_gizi' not in st.session_state:
    st.session_state['db_gizi'] = pd.DataFrame({
        "Bahan Makanan": ["Nasi Putih", "Dada Ayam", "Telur Ayam", "Susu Sapi", "Kangkung"],
        "Energi (kkal)": [130.0, 165.0, 155.0, 61.0, 23.0],
        "Protein (g)": [2.7, 31.0, 13.0, 3.2, 2.9],
        "Lemak (g)": [0.3, 3.6, 11.0, 3.3, 0.4],
        "Karbohidrat (g)": [28.0, 0.0, 1.1, 4.8, 3.6],
        "Serat (g)": [0.4, 0.0, 0.0, 0.0, 2.2]
    })

# --- 4. TABS NAVBAR ---
tab1, tab2, tab3 = st.tabs(["👤 1. Kalkulator Kebutuhan Personal", "🧮 2. Matriks SPL Porsi Makanan", "📚 3. Dasar Teori"])

# ==========================================
# TAB 1: KALKULATOR PERSONAL 
# ==========================================
with tab1:
    st.write("### Masukkan Data Fisik Anda")
    st.caption("Sistem akan menghitung Total Kebutuhan Energi (Target Vektor B) menggunakan formula medis BMR (Mifflin-St Jeor).")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    with col2: umur = st.number_input("Umur (Tahun)", min_value=10, max_value=100, value=20)
    with col3: bb = st.number_input("Berat Badan (kg)", min_value=30.0, value=65.0)
    with col4: tb = st.number_input("Tinggi Badan (cm)", min_value=120.0, value=170.0)
    
    col_act, col_goal = st.columns(2)
    with col_act:
        aktivitas = st.selectbox("Tingkat Aktivitas Fisik", [
            "Jarang olahraga", 
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
        # 1. Hitung BMR 
        if jk == "Laki-laki":
            bmr = (10 * bb) + (6.25 * tb) - (5 * umur) + 5
        else:
            bmr = (10 * bb) + (6.25 * tb) - (5 * umur) - 161
            
        # 2. Kalikan dengan Faktor Aktivitas
        if "Jarang" in aktivitas: tdee = bmr * 1.2
        elif "ringan" in aktivitas: tdee = bmr * 1.375
        elif "sedang" in aktivitas: tdee = bmr * 1.55
        else: tdee = bmr * 1.725
        
        # 3. Penyesuaian Tujuan
        if "Menurunkan" in tujuan: tdee -= 500
        elif "Menaikkan" in tujuan: tdee += 500
        
        # 4. Hitung Makronutrien
        karbo = (tdee * 0.50) / 4
        protein = (tdee * 0.20) / 4
        lemak = (tdee * 0.30) / 9
        serat = 25 
        
        st.session_state['target_nutrisi'] = {
            "energi": round(tdee, 1), "protein": round(protein, 1), 
            "lemak": round(lemak, 1), "karbo": round(karbo, 1), "serat": serat
        }
        st.success("Target Vektor B berhasil dihitung dan disimpan! Silakan lanjut ke Tab 2.")

    # Tampilan Box Target
    st.markdown('<div class="target-box">', unsafe_allow_html=True)
    st.write("#### 🎯 Target Nutrisi Harian Anda (Vektor B)")
    t_col1, t_col2, t_col3, t_col4, t_col5 = st.columns(5)
    t = st.session_state['target_nutrisi']
    t_col1.metric("⚡ Energi", f"{t['energi']} kkal")
    t_col2.metric("🥩 Protein", f"{t['protein']} g")
    t_col3.metric("🥑 Lemak", f"{t['lemak']} g")
    t_col4.metric("🍚 Karbohidrat", f"{t['karbo']} g")
    t_col5.metric("🥬 Serat", f"{t['serat']} g")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 2: MATRIKS SPL (INTERAKTIF & NYATA)
# ==========================================
with tab2:
    st.write("### 📝 Tabel Kandungan Gizi per 100 Gram (Matriks A)")
    st.info("💡 **Cara Interaksi:** Klik 2x pada angka untuk mengedit. Klik ujung bawah tabel untuk menambah baris. **Untuk menghapus:** Centang kotak di sebelah kiri nomor baris, lalu tekan tombol 'Delete' atau 'Backspace' di keyboard Anda.")
    
    # Tabel murni tanpa CSS yang mengganggu
    tabel_diedit = st.data_editor(
        st.session_state['db_gizi'], 
        num_rows="dynamic", 
        use_container_width=True
    )
    st.session_state['db_gizi'] = tabel_diedit
    
    st.write("---")
    if st.button("🚀 Kalkulasi Takaran Makanan (Eliminasi Gauss-Jordan)", type="primary", use_container_width=True):
        st.write("### 📊 Hasil Komputasi Takaran (Vektor X)")
        
        A_raw = tabel_diedit[["Energi (kkal)", "Protein (g)", "Lemak (g)", "Karbohidrat (g)", "Serat (g)"]].values.T
        
        t = st.session_state['target_nutrisi']
        B = np.array([t['energi'], t['protein'], t['lemak'], t['karbo'], t['serat']])
        
        nama_makanan = tabel_diedit["Bahan Makanan"].tolist()
        jumlah_variabel = len(nama_makanan)
        
        if jumlah_variabel == 5:
            try:
                # Menghitung nilai X (Multiplier per 100 gram)
                X = np.linalg.solve(A_raw, B)
                
                kolom_hasil = st.columns(5)
                for i in range(5):
                    # Mengubah output X yang awalnya "Porsi" menjadi satuan Gram nyata
                    jumlah_gram = X[i] * 100 
                    kolom_hasil[i].metric(label=f"{nama_makanan[i]}", value=f"{jumlah_gram:.0f} Gram")
                    
                st.write("")
                if any(porsi < 0 for porsi in X):
                    st.error("⚠️ **EVALUASI:** Sistem mendeteksi adanya takaran bernilai **NEGATIF (Minus Gram)**. Ini membuktikan kelemahan fatal SPL murni di dunia nyata (tidak ada batas ≥ 0). Logika aljabar benar menyilangkan garis persamaan, namun hasilnya tidak valid secara dunia nyata.")
                else:
                    st.success("✅ Matriks diselesaikan dan kombinasi takaran bernilai positif (logis).")
            except np.linalg.LinAlgError:
                st.error("🚨 Matriks Singular! Sistem tidak menemukan solusi persilangan garis (Determinannya Nol).")
        else:
            st.warning(f"Sistem menggunakan pendekatan **Least Squares** karena matriks tidak berbentuk persegi (5 x {jumlah_variabel}).")
            try:
                X, _, _, _ = np.linalg.lstsq(A_raw, B, rcond=None)
                kolom_hasil = st.columns(jumlah_variabel)
                for i in range(jumlah_variabel):
                    jumlah_gram = X[i] * 100
                    kolom_hasil[i].metric(label=f"{nama_makanan[i]}", value=f"{jumlah_gram:.0f} Gram")
            except Exception as e:
                st.error(f"Error perhitungan matriks dinamis: {e}")

# ==========================================
# TAB 3: DASAR TEORI
# ==========================================
with tab3:
    st.write("### Landasan Matematika dan Teori Gizi")
    st.write("""
    1. **Tahap 1 (Buku Tuntunan Gizi):** Sistem meminta data biofisik pengguna untuk mencari target kalori menggunakan rumus BMR. Target ini kemudian didistribusikan ke makronutrisi dan dijadikan **Vektor Hasil (B)**.
    2. **Tahap 2 (Makalah ITB):** Sistem mengubah database makanan (per 100 gram) menjadi matriks koefisien (A). Sistem persamaan linear **AX = B** kemudian dipecahkan. Vektor (X) yang dihasilkan dikalikan 100 untuk mendapatkan takaran riil dalam satuan gram. 
    3. **Tujuan Utama:** Proyek ini membuktikan bahwa Aljabar Linier adalah fondasi komputasi medis, namun sekaligus mendemonstrasikan kelemahannya jika tidak diberi batasan realitas fisik (batasan tidak boleh di bawah nol).
    """)