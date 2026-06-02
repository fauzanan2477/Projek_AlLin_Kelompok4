import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Pakar Gizi SPL Dinamis", layout="wide", initial_sidebar_state="collapsed")

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
    <h1>🥗 Sistem Pakar Gizi & Aljabar Linier (Dinamis)</h1>
    <p>Simulasi Matriks 3x3 dan 5x5 | Ref: Makalah ITB & Buku Gizi Klinis</p>
</div>
""", unsafe_allow_html=True)

# --- 3. TABS NAVBAR ---
tab1, tab2, tab3 = st.tabs(["👤 1. Kalkulator Target Gizi Personal", "🧮 2. Pemecahan Matriks SPL (Takaran)", "📚 3. Dasar Teori Matriks"])

# ==========================================
# TAB 1: KALKULATOR PERSONAL 
# ==========================================
with tab1:
    st.write("### Masukkan Data Biofisik")
    st.caption("Sistem akan menghitung BMR dan menentukan Vektor B (Target Nutrisi) Anda.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    with col2: umur = st.number_input("Umur (Tahun)", min_value=10, max_value=100, value=20)
    with col3: bb = st.number_input("Berat Badan (kg)", min_value=30.0, value=65.0)
    with col4: tb = st.number_input("Tinggi Badan (cm)", min_value=120.0, value=170.0)
    
    col_act, col_goal = st.columns(2)
    with col_act: aktivitas = st.selectbox("Tingkat Aktivitas", ["Jarang olahraga", "Olahraga ringan", "Olahraga sedang", "Olahraga berat"])
    with col_goal: tujuan = st.selectbox("Program", ["Mempertahankan Berat Badan", "Menurunkan Berat Badan", "Menaikkan Berat Badan"])
    
    # State untuk menyimpan target
    if 'target_nutrisi' not in st.session_state:
        st.session_state['target_nutrisi'] = {"energi": 2000, "protein": 75, "lemak": 65, "karbo": 275, "serat": 25}

    if st.button("Hitung & Simpan Target Nutrisi", type="primary"):
        bmr = (10 * bb) + (6.25 * tb) - (5 * umur) + (5 if jk == "Laki-laki" else -161)
        
        if "Jarang" in aktivitas: tdee = bmr * 1.2
        elif "ringan" in aktivitas: tdee = bmr * 1.375
        elif "sedang" in aktivitas: tdee = bmr * 1.55
        else: tdee = bmr * 1.725
        
        if "Menurunkan" in tujuan: tdee -= 500
        elif "Menaikkan" in tujuan: tdee += 500
        
        karbo = (tdee * 0.50) / 4
        protein = (tdee * 0.20) / 4
        lemak = (tdee * 0.30) / 9
        
        st.session_state['target_nutrisi'] = {
            "energi": round(tdee, 1),
            "protein": round(protein, 1), 
            "lemak": round(lemak, 1), 
            "karbo": round(karbo, 1),
            "serat": 25.0
        }
        st.success("Target Vektor B berhasil diperbarui!")

    st.markdown('<div class="target-box">', unsafe_allow_html=True)
    st.write("#### 🎯 Target Vektor B (Disesuaikan otomatis dengan mode matriks yang dipilih)")
    t = st.session_state['target_nutrisi']
    t_c1, t_c2, t_c3, t_c4, t_c5 = st.columns(5)
    t_c1.metric("⚡ Energi", f"{t['energi']} kkal")
    t_c2.metric("🥩 Protein", f"{t['protein']} g")
    t_c3.metric("🥑 Lemak", f"{t['lemak']} g")
    t_c4.metric("🍚 Karbo", f"{t['karbo']} g")
    t_c5.metric("🥬 Serat", f"{t['serat']} g")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 2: MATRIKS SPL DINAMIS
# ==========================================
with tab2:
    st.write("### 🎛️ Pengaturan Ordo Matriks")
    
    # FITUR PILIHAN MODE MATRIKS (Ide Brilian User)
    mode_matriks = st.radio(
        "Pilih Dimensi Matriks yang ingin disimulasikan:",
        ["Mode 3x3 (Fokus Zat Gizi Makro)", "Mode 5x5 (Lengkap: Energi, Makro, dan Mikro/Serat)"],
        horizontal=True
    )
    
    # Inisialisasi Database sesuai mode
    if "3x3" in mode_matriks:
        kolom_nutrisi = ["Protein (g)", "Lemak (g)", "Karbohidrat (g)"]
        if 'db_gizi_3x3' not in st.session_state:
            st.session_state['db_gizi_3x3'] = pd.DataFrame({
                "Bahan Makanan": ["Nasi Putih", "Dada Ayam", "Tempe Murni"],
                "Protein (g)": [2.7, 31.0, 19.0],
                "Lemak (g)": [0.3, 3.6, 11.0],
                "Karbohidrat (g)": [28.0, 0.0, 9.0]
            })
        db_aktif = 'db_gizi_3x3'
        jumlah_ideal = 3
    else:
        kolom_nutrisi = ["Energi (kkal)", "Protein (g)", "Lemak (g)", "Karbohidrat (g)", "Serat (g)"]
        if 'db_gizi_5x5' not in st.session_state:
            st.session_state['db_gizi_5x5'] = pd.DataFrame({
                "Bahan Makanan": ["Nasi Putih", "Dada Ayam", "Tempe Murni", "Susu Sapi", "Kangkung"],
                "Energi (kkal)": [130.0, 165.0, 193.0, 61.0, 23.0],
                "Protein (g)": [2.7, 31.0, 19.0, 3.2, 2.9],
                "Lemak (g)": [0.3, 3.6, 11.0, 3.3, 0.4],
                "Karbohidrat (g)": [28.0, 0.0, 9.0, 4.8, 3.6],
                "Serat (g)": [0.4, 0.0, 0.0, 0.0, 2.2]
            })
        db_aktif = 'db_gizi_5x5'
        jumlah_ideal = 5

    st.write("---")
    st.write(f"### 📝 Tabel Gizi per 100 Gram (Matriks A: Kunci ke {jumlah_ideal}x{jumlah_ideal})")
    
    # Tabel interaktif (Diberi key dinamis agar tidak kereset saat ganti mode)
    tabel_diedit = st.data_editor(
        st.session_state[db_aktif], 
        num_rows="dynamic", 
        use_container_width=True,
        key=f"tabel_gizi_{jumlah_ideal}" 
    )
    st.session_state[db_aktif] = tabel_diedit
    
    st.write("---")
    if st.button("🚀 Jalankan Komputasi Matriks", type="primary", use_container_width=True):
        
        if tabel_diedit.empty:
            st.error("⚠️ Tabel makanan kosong!")
        else:
            st.write("### 📊 Rekomendasi Takaran (Vektor X dalam Gram):")
            
            # Matriks A diekstrak sesuai kolom yang aktif
            A_raw = tabel_diedit[kolom_nutrisi].values.T
            
            # Vektor B disusun sesuai mode
            t = st.session_state['target_nutrisi']
            if "3x3" in mode_matriks:
                B = np.array([t['protein'], t['lemak'], t['karbo']])
            else:
                B = np.array([t['energi'], t['protein'], t['lemak'], t['karbo'], t['serat']])
            
            nama_makanan = tabel_diedit["Bahan Makanan"].tolist()
            jumlah_makanan = len(nama_makanan)
            
            # Pengecekan Syarat Persegi (n x n)
            if jumlah_makanan == jumlah_ideal:
                st.info(f"✅ **Sistem Mendeteksi Matriks Persegi {jumlah_ideal}x{jumlah_ideal}.** Eliminasi Gauss-Jordan dijalankan.")
                try:
                    X = np.linalg.solve(A_raw, B)
                    kolom_hasil = st.columns(jumlah_ideal)
                    for i in range(jumlah_ideal):
                        jumlah_gram = X[i] * 100 
                        kolom_hasil[i].metric(label=f"{nama_makanan[i]}", value=f"{jumlah_gram:.0f} Gram")
                        
                    st.write("")
                    if any(porsi < 0 for porsi in X):
                        st.error("⚠️ **EVALUASI:** Ditemukan takaran **NEGATIF (Minus Gram)**. Ini membuktikan kelemahan matriks SPL murni di dunia nyata.")
                except np.linalg.LinAlgError:
                    st.error("🚨 Matriks Singular! Gizi makanan tidak memiliki titik persilangan.")
            
            else:
                st.warning(f"⚠️ **Matriks Tidak Persegi!** Ada {jumlah_ideal} Target Nutrisi tapi {jumlah_makanan} Makanan. Sistem otomatis menggunakan metode *Least Squares*.")
                try:
                    X, _, _, _ = np.linalg.lstsq(A_raw, B, rcond=None)
                    kolom_hasil = st.columns(jumlah_makanan)
                    for i in range(jumlah_makanan):
                        jumlah_gram = X[i] * 100
                        kolom_hasil[i].metric(label=f"{nama_makanan[i]}", value=f"{jumlah_gram:.0f} Gram")
                except Exception as e:
                    st.error(f"Gagal memproses matriks: {e}")

# ==========================================
# TAB 3: DASAR TEORI MATRIKS
# ==========================================
with tab3:
    st.write("### Landasan Logika Matematika")
    st.write("""
    - **Sifat Dinamis Aplikasi:** Sesuai jurnal ITB, matriks awal berukuran 5x5. Namun, kelompok kami memodifikasi algoritmanya agar pengguna dapat menyederhanakannya menjadi matriks 3x3 (Fokus pada Zat Gizi Makro saja).
    - **Syarat Mutlak Aljabar Linier:** Agar memiliki solusi tunggal, SPL memerlukan jumlah kolom dan baris yang sama. Mode 3x3 meminta Anda memasukkan 3 bahan makanan, sedangkan Mode 5x5 membutuhkan 5 bahan makanan.
    """)