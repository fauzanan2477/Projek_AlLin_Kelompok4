import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Sistem Pakar MBG", layout="wide")

st.markdown("""
    <style>
    /* Desain Background Putih & Kontainer Modern */
    .stApp { background-color: #ffffff; }
    .block-container { padding-top: 2rem; max-width: 1050px; }
    
    /* Navbar Custom (Lebar dan Jelas) */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 50px; border-bottom: 2px solid #eaeaea; }
    .stTabs [data-baseweb="tab"] { font-weight: 800; font-size: 1.25rem; color: #7f8c8d; background-color: transparent; border: none; padding-bottom: 10px;}
    .stTabs [aria-selected="true"] { color: #2980b9; border-bottom: 4px solid #2980b9; }
    
    /* Hero Section */
    .hero-section { text-align: center; padding: 20px 0px 40px 0px; }
    .hero-title { font-size: 3.5rem; font-weight: 900; color: #2c3e50; line-height: 1.1; margin-bottom: 15px; letter-spacing: -1px;}
    .hero-title span { color: #2980b9; }
    .hero-subtitle { font-size: 1.2rem; color: #7f8c8d; font-weight: 500;}
    
    /* Card Hasil */
    .result-card { background-color: #f4f9ff; border-radius: 12px; padding: 30px; text-align: center; border: 1px solid #dcebfa; margin: 20px 0px;}
    .result-card h2 { color: #2980b9; font-size: 3.5rem; margin: 0; font-weight: 900;}
    .result-card p { color: #34495e; font-size: 1rem; margin: 0; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HERO SECTION
# ==========================================
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">Sistem Optimasi Logistik<br><span>Makan Bergizi Gratis (MBG)</span></h1>
    <p class="hero-subtitle">Integrasi Ilmu Gizi (Harris-Benedict) dan Aljabar Linier (Metode Simpleks)</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATABASE MATRIKS (SESSION STATE)
# ==========================================
if 'db_bahan' not in st.session_state:
    st.session_state['db_bahan'] = pd.DataFrame({
        "Gunakan": [True, True, True, True, False, True], # Checkbox
        "Bahan Makanan": ["Nasi Putih", "Telur Ayam", "Tempe Murni", "Sayur Bayam", "Susu Sapi UHT", "Daging Ayam"],
        "Harga (Rp)": [1200, 2600, 1000, 800, 3000, 4500], 
        "Kalori (Kkal)": [130.0, 155.0, 193.0, 23.0, 60.0, 165.0],
        "Protein (g)": [2.7, 13.0, 19.0, 3.0, 3.2, 31.0],
        "Lemak (g)": [0.3, 11.0, 11.0, 0.4, 3.3, 3.6],
        "Batas Maks (g)": [200.0, 100.0, 100.0, 150.0, 200.0, 150.0] # Batas agar porsi realistis
    })

if 'target_kalori' not in st.session_state:
    st.session_state.update({'target_kalori': 600.0, 'target_protein': 22.0, 'target_lemak': 15.0})

# ==========================================
# 4. MENU NAVBAR (TABS)
# ==========================================
tab_gizi, tab_aljabar, tab_docs = st.tabs(["1. Kalkulator Gizi Anak", "2. Mesin Optimasi Aljabar", "3. Dokumentasi & Teori"])

# --- HALAMAN 1: KALKULATOR GIZI ---
with tab_gizi:
    st.write("### 👦 Kalkulator Biometrik (Vektor Konstanta)")
    st.write("Sistem menggunakan rumus BMR untuk menghitung kebutuhan 1 porsi makan siang anak (1/3 dari total harian). Angka ini akan menjadi matriks pembatas bagi algoritma aljabar.")
    
    col_bio1, col_bio2 = st.columns(2)
    with col_bio1:
        umur = st.number_input("Umur Anak (Tahun)", min_value=5, max_value=18, value=10)
        jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    with col_bio2:
        bb = st.number_input("Berat Badan (kg)", min_value=15.0, value=30.0)
        tb = st.number_input("Tinggi Badan (cm)", min_value=100.0, value=135.0)
    
    if st.button("Hitung Vektor Target Gizi", type="primary"):
        # Rumus Harris Benedict
        if jk == "Laki-laki":
            bmr = 66.5 + (13.7 * bb) + (5 * tb) - (6.8 * umur)
        else:
            bmr = 655 + (9.6 * bb) + (1.8 * tb) - (4.7 * umur)
        
        tdee = bmr * 1.55 # Faktor aktivitas anak sekolah aktif
        
        # Target 1 porsi makan siang (MBG) = 1/3 Harian
        porsi_kalori = tdee / 3 
        porsi_protein = (porsi_kalori * 0.15) / 4 # 15% dari kalori
        porsi_lemak = (porsi_kalori * 0.30) / 9 # 30% dari kalori
        
        # Simpan ke memori sesi
        st.session_state['target_kalori'] = round(porsi_kalori, 1)
        st.session_state['target_protein'] = round(porsi_protein, 1)
        st.session_state['target_lemak'] = round(porsi_lemak, 1)
        st.success("Target berhasil diperbarui! Silakan buka Tab 2 untuk optimasi.")

    col_t1, col_t2, col_t3 = st.columns(3)
    col_t1.metric("Target Kalori Minimal", f"{st.session_state['target_kalori']} Kkal")
    col_t2.metric("Target Protein Minimal", f"{st.session_state['target_protein']} g")
    col_t3.metric("Target Lemak Minimal", f"{st.session_state['target_lemak']} g")

# --- HALAMAN 2: MESIN OPTIMASI ALJABAR (SIMPLEKS) ---
with tab_aljabar:
    st.write("### 🛒 Database Bahan Makanan (Matriks Input)")
    st.caption("Centang kolom **'Gunakan'** untuk memilih makanan hari ini. Sesuaikan **'Batas Maks'** agar aplikasi memvariasikan porsi lauk.")
    
    # Tabel Data
    df_interaktif = st.data_editor(st.session_state['db_bahan'], num_rows="dynamic", use_container_width=True, hide_index=True)
    st.session_state['db_bahan'] = df_interaktif
    
    st.write("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Jalankan Operasi Matriks (Cari Biaya Termurah)", type="primary", use_container_width=True):
        df_dipilih = df_interaktif[df_interaktif["Gunakan"] == True].copy()
        
        if len(df_dipilih) < 2:
            st.error("⚠️ Centang minimal 2 bahan makanan untuk komputasi matriks.")
        else:
            # 1. Pastikan semua data adalah angka
            harga = pd.to_numeric(df_dipilih["Harga (Rp)"], errors='coerce').fillna(0).values
            gizi = df_dipilih[["Kalori (Kkal)", "Protein (g)", "Lemak (g)"]].apply(pd.to_numeric, errors='coerce').fillna(0)
            
            # Batas Maksimal (Diubah ke satuan pengali per 100 gram)
            batas_gram = pd.to_numeric(df_dipilih["Batas Maks (g)"], errors='coerce').fillna(1000).values
            batas_multiplier = batas_gram / 100.0
            
            # 2. Setup Persamaan SPL (Dikali -1 untuk mengubah <= menjadi >=)
            A_ub = -1 * gizi.values.T
            b_ub = -1 * np.array([st.session_state['target_kalori'], st.session_state['target_protein'], st.session_state['target_lemak']])
            
            # Batas Bawah dan Batas Atas Makanan (0 sampai Batas Maksimal)
            batas = [(0, maks) for maks in batas_multiplier]
            
            # 3. Eksekusi Simpleks
            try:
                hasil = linprog(harga, A_ub=A_ub, b_ub=b_ub, bounds=batas, method='highs')
                
                if hasil.success:
                    st.markdown(f"""
                    <div class="result-card">
                        <p>Titik Potong SPL Ditemukan! Total Biaya Termurah</p>
                        <h2>Rp {hasil.fun:,.0f}</h2>
                        <p style="color:#666; font-size:1rem; font-weight:normal; margin-top:5px;">Per Porsi / Anak</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("### ⚖️ Vektor Penyelesaian (Kombinasi Porsi yang Realistis)")
                    hasil_gram = hasil.x * 100 
                    df_hasil = pd.DataFrame({
                        "Bahan Makanan": df_dipilih["Bahan Makanan"].values,
                        "Takaran Disarankan": [f"{g:,.0f} Gram" for g in hasil_gram],
                        "Alokasi Harga": [f"Rp {(g/100)*h:,.0f}" for g, h in zip(hasil_gram, harga)]
                    })
                    # Tampilkan yang porsinya nyata (> 0)
                    st.table(df_hasil[hasil.x > 0.01].reset_index(drop=True))
                    
                else:
                    st.error("🚨 Matriks Infeasible: Sistem tidak bisa memenuhi target gizi dengan kombinasi makanan yang dicentang. Coba naikkan 'Batas Maks' makanan, atau tambah variasi lauk di tabel.")
            except Exception as e:
                st.error(f"Terjadi kesalahan komputasi: {e}")

# --- HALAMAN 3: DOKUMENTASI (RUMUS) ---
with tab_docs:
    st.write("### 📖 Integrasi Rumus Biometrik dan Aljabar Linier")
    st.write("**1. Penentuan Vektor Konstanta (Target Gizi)**")
    st.write("Target gizi minimal tidak ditebak, melainkan dihitung berdasarkan modifikasi persamaan Harris-Benedict (AKG Kemenkes) untuk Anak Sekolah:")
    st.latex(r"BMR_{Laki} = 66.5 + (13.7 \times BB) + (5 \times TB) - (6.8 \times Umur)")
    st.write("Angka $BMR$ dikalikan faktor aktivitas, lalu dibagi tiga (untuk 1 porsi makan siang) yang bertindak sebagai Vektor Target $B$.")
    
    st.write("---")
    st.write("**2. Sistem Persamaan Linier (Metode Simpleks)**")
    st.write("Masalah optimasi ini dipetakan ke dalam ruang vektor. Komputer diperintahkan untuk mencari titik paling minimum dari Fungsi Objektif (Biaya):")
    st.latex(r"Z = \mathbf{C}^T \mathbf{X}")
    st.write("Dengan batasan matriks (Gizi harus terpenuhi, namun porsi makanan memiliki batas atas agar realistis):")
    st.latex(r"\mathbf{A}\mathbf{X} \ge \mathbf{B} \quad \text{dan} \quad 0 \le \mathbf{X} \le \mathbf{U_{maks}}")
    st.info("Dengan adanya Vektor $\mathbf{U_{maks}}$ (Batas Maksimal), aljabar Linier dipaksa mengkombinasikan berbagai lauk, mencegah mesin menyarankan anak memakan 1 porsi ekstrem (seperti 1 Kg tempe saja).")