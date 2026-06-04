import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS KONTRAS TINGGI
# ==========================================
st.set_page_config(page_title="Sistem Pakar MBG", layout="wide")

st.markdown("""
    <style>
    /* Mengatur Background Utama menjadi Abu-abu sangat terang agar kontras dengan Box Putih */
    .stApp { background-color: #f4f6f9; color: #111111; }
    .block-container { padding-top: 2rem; max-width: 1100px; }
    
    /* Box Teks & Elemen UI berwarna Putih Bersih dengan Shadow */
    .white-box { background-color: #ffffff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #e1e4e8; color: #333333;}
    
    /* Navbar Custom */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 30px; border-bottom: 2px solid #dcdde1; background-color: #ffffff; padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { font-weight: 800; font-size: 1.15rem; color: #555555; background-color: transparent; border: none; }
    .stTabs [aria-selected="true"] { color: #1e3799; border-bottom: 4px solid #1e3799; }
    
    /* Typography */
    h1, h2, h3, h4, p, li { color: #111111 !important; }
    .hero-title { font-size: 3.2rem; font-weight: 900; color: #000000 !important; line-height: 1.2; margin-bottom: 15px; text-align: center; }
    .hero-title span { color: #1e3799 !important; }
    .hero-subtitle { font-size: 1.2rem; color: #444444 !important; font-weight: 500; text-align: center; margin-bottom: 30px;}
    
    /* Card Hasil Termurah */
    .result-card { background: linear-gradient(135deg, #1e3799, #0984e3); color: white !important; border-radius: 12px; padding: 30px; text-align: center; margin: 20px 0px; box-shadow: 0 5px 15px rgba(0,0,0,0.2);}
    .result-card h2 { color: #ffffff !important; font-size: 3.5rem; margin: 0; font-weight: 900;}
    .result-card p { color: #dff9fb !important; font-size: 1.1rem; margin: 0; font-weight: bold; letter-spacing: 1px;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HERO SECTION
# ==========================================
st.markdown("""
<div class="hero-title">Sistem Optimasi Logistik<br><span>Makan Bergizi Gratis (MBG)</span></div>
<div class="hero-subtitle">Integrasi Ilmu Gizi Biometrik dan Aljabar Linier (Metode Simpleks Dua Fase)</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATABASE (SESSION STATE)
# ==========================================
if 'db_bahan' not in st.session_state:
    st.session_state['db_bahan'] = pd.DataFrame({
        "Gunakan": [True, True, True, True, False, True], 
        "Bahan Makanan": ["Nasi Putih", "Telur Ayam", "Tempe Murni", "Sayur Bayam", "Susu Sapi", "Daging Ayam"],
        "Harga (Rp)": [1200, 2600, 1000, 800, 3000, 4500], 
        "Kalori (Kkal)": [130.0, 155.0, 193.0, 23.0, 60.0, 165.0],
        "Protein (g)": [2.7, 13.0, 19.0, 3.0, 3.2, 31.0],
        "Lemak (g)": [0.3, 11.0, 11.0, 0.4, 3.3, 3.6],
        "Karbohidrat (g)": [28.6, 1.1, 9.4, 3.6, 4.8, 0.0], # DATA BARU: Karbohidrat
        "Porsi (g)": [200.0, 100.0, 100.0, 150.0, 200.0, 150.0] 
    })

if 'target_kalori' not in st.session_state:
    st.session_state.update({
        'target_kalori': 600.0, 
        'target_protein': 22.5, 
        'target_lemak': 20.0, 
        'target_karbo': 82.5,
        'aktivitas_val': 1.55,
        'bmr_val': 1161.0
    })

# ==========================================
# 4. MENU NAVBAR (TABS)
# ==========================================
tab_gizi, tab_aljabar, tab_manual, tab_docs = st.tabs([
    "1. Kalkulator Gizi", 
    "2. Eksekusi Optimasi", 
    "3. Langkah Manual (Sangat Detail)", 
    "4. Dokumentasi Rumus"
])

# --- HALAMAN 1: KALKULATOR GIZI ---
with tab_gizi:
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### 👦 Penentuan Vektor Konstanta Gizi (B)")
    st.write("Sistem menghitung target Makronutrien anak berdasarkan persamaan Harris-Benedict dan tingkat aktivitas fisik (Merujuk pada Jurnal Brawijaya).")
    
    col_bio1, col_bio2 = st.columns(2)
    with col_bio1:
        umur = st.number_input("Umur Anak (Tahun)", min_value=5, max_value=18, value=10)
        jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        
        aktivitas = st.selectbox("Tingkat Aktivitas Fisik (Olahraga)", [
            "Sangat Jarang (Pasif / Tidak olahraga)",
            "Jarang (Olahraga ringan 1-3 hari/minggu)",
            "Cukup (Olahraga sedang 3-5 hari/minggu)",
            "Sering (Olahraga berat 6-7 hari/minggu)",
            "Sangat Sering (Atlet / Fisik ekstra)"
        ], index=2)
        
    with col_bio2:
        bb = st.number_input("Berat Badan (kg)", min_value=15.0, value=30.0)
        tb = st.number_input("Tinggi Badan (cm)", min_value=100.0, value=135.0)
    
    if st.button("Hitung Target & Simpan", type="primary"):
        if aktivitas == "Sangat Jarang (Pasif / Tidak olahraga)": multiplier = 1.2
        elif aktivitas == "Jarang (Olahraga ringan 1-3 hari/minggu)": multiplier = 1.375
        elif aktivitas == "Cukup (Olahraga sedang 3-5 hari/minggu)": multiplier = 1.55
        elif aktivitas == "Sering (Olahraga berat 6-7 hari/minggu)": multiplier = 1.725
        else: multiplier = 1.9

        # Rumus BMR Harris Benedict
        if jk == "Laki-laki":
            bmr = 66.5 + (13.7 * bb) + (5 * tb) - (6.8 * umur)
        else:
            bmr = 655 + (9.6 * bb) + (1.8 * tb) - (4.7 * umur)
        
        # Eksekusi Pembagian 1 Porsi Makan Siang (1/3 dari Total Harian)
        porsi_kalori = (bmr * multiplier) / 3 
        porsi_protein = (porsi_kalori * 0.15) / 4   # 15% dari kalori, 1g protein = 4 kkal
        porsi_lemak = (porsi_kalori * 0.30) / 9     # 30% dari kalori, 1g lemak = 9 kkal
        porsi_karbo = (porsi_kalori * 0.55) / 4     # 55% dari kalori, 1g karbo = 4 kkal
        
        st.session_state['bmr_val'] = round(bmr, 1)
        st.session_state['aktivitas_val'] = multiplier
        st.session_state['target_kalori'] = round(porsi_kalori, 1)
        st.session_state['target_protein'] = round(porsi_protein, 1)
        st.session_state['target_lemak'] = round(porsi_lemak, 1)
        st.session_state['target_karbo'] = round(porsi_karbo, 1)
        st.success(f"Target Vektor Gizi Makronutrien diperbarui! Lanjut ke Tab 2.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- HALAMAN 2: EKSEKUSI OPTIMASI ---
with tab_aljabar:
    st.markdown('<div class="white-box" style="border-left: 5px solid #e1b12c;">', unsafe_allow_html=True)
    st.write("#### 🎯 Target Gizi Saat Ini (Syarat Matriks):")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kalori Minimal", f"{st.session_state['target_kalori']} Kkal")
    c2.metric("Protein Minimal", f"{st.session_state['target_protein']} Gram")
    c3.metric("Lemak Minimal", f"{st.session_state['target_lemak']} Gram")
    c4.metric("Karbo Minimal", f"{st.session_state['target_karbo']} Gram")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### 🛒 Database Bahan Makanan (Pilih Lauk)")
    df_interaktif = st.data_editor(st.session_state['db_bahan'], num_rows="dynamic", use_container_width=True, hide_index=True)
    st.session_state['db_bahan'] = df_interaktif
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🚀 Kalkulasi Biaya Termurah", type="primary", use_container_width=True):
        df_dipilih = df_interaktif[df_interaktif["Gunakan"] == True].copy()
        
        if len(df_dipilih) < 2:
            st.error("⚠️ Centang minimal 2 bahan makanan untuk komputasi.")
        else:
            harga = pd.to_numeric(df_dipilih["Harga (Rp)"], errors='coerce').fillna(0).values
            gizi = df_dipilih[["Kalori (Kkal)", "Protein (g)", "Lemak (g)", "Karbohidrat (g)"]].apply(pd.to_numeric, errors='coerce').fillna(0)
            porsi_makan = pd.to_numeric(df_dipilih["Porsi (g)"], errors='coerce').fillna(1000).values / 100.0
            
            A_ub = -1 * gizi.values.T
            b_ub = -1 * np.array([st.session_state['target_kalori'], st.session_state['target_protein'], st.session_state['target_lemak'], st.session_state['target_karbo']])
            porsi = [(0, maks) for maks in porsi_makan]
            
            try:
                hasil = linprog(harga, A_ub=A_ub, b_ub=b_ub, bounds=porsi, method='highs')
                
                if hasil.success:
                    st.markdown(f"""
                    <div class="result-card">
                        <p>Total Biaya Paling Minimum (Titik Optimal)</p>
                        <h2>Rp {hasil.fun:,.0f}</h2>
                        <p>Per Anak / Sekali Makan</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('<div class="white-box">', unsafe_allow_html=True)
                    st.write("### ⚖️ Vektor Rekomendasi Takaran")
                    hasil_gram = hasil.x * 100 
                    df_hasil = pd.DataFrame({
                        "Bahan Makanan": df_dipilih["Bahan Makanan"].values,
                        "Takaran Disarankan": [f"{g:,.0f} Gram" for g in hasil_gram],
                        "Biaya Realisasi": [f"Rp {(g/100)*h:,.0f}" for g, h in zip(hasil_gram, harga)]
                    })
                    st.table(df_hasil[hasil.x > 0.01].reset_index(drop=True))
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("🚨 SPL Infeasible: Sistem tidak bisa memenuhi ke-4 target makronutrien dengan lauk yang dipilih. Coba tambah variasi makanan atau besarkan porsi maksimal.")
            except Exception as e:
                st.error(f"Error komputasi: {e}")

# --- HALAMAN 3: LANGKAH MANUAL (SANGAT DETAIL) ---
with tab_manual:
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### ✍️ Simulasi Pemodelan: Dari Biometrik ke Matriks")
    st.write("Di balik layar, sistem ini bekerja melalui dua tahap besar: (1) Penentuan Kebutuhan Gizi Makronutrien dan (2) Optimasi Matriks Simpleks Dua Fase.")
    
    st.write("---")
    st.write("#### TAHAP 1: Perhitungan Konstanta Gizi (Vektor B)")
    st.write("Berikut adalah langkah-langkah bagaimana sistem menentukan target gizi minimal anak berdasarkan data yang Anda input di Tab 1:")
    
    st.markdown(f"""
    1. **Menghitung BMR (Basal Metabolic Rate):** Sistem menggunakan rumus Harris-Benedict berdasarkan Umur, Berat Badan, dan Tinggi Badan anak.  
       👉 *Hasil BMR anak ini:* **{st.session_state.get('bmr_val', 0)} Kkal**
    2. **Menghitung TEE (Total Energy Expenditure):** BMR dikalikan dengan Faktor Aktivitas Fisik (Olahraga). Pengali yang dipilih adalah **{st.session_state.get('aktivitas_val', 1)}**.  
       👉 *Total Kalori Harian:* {st.session_state.get('bmr_val', 0)} × {st.session_state.get('aktivitas_val', 1)} = **{round(st.session_state.get('bmr_val', 0) * st.session_state.get('aktivitas_val', 1), 1)} Kkal**
    3. **Membagi Porsi Makan Siang (MBG):** Target harian dibagi 3 (untuk 1x makan siang).  
       👉 *Target Kalori (K):* **{st.session_state['target_kalori']} Kkal**
    4. **Memecah Makronutrien:** - **Protein (P):** 15% dari Kalori dibagi 4 (karena 1g protein = 4 kkal) = **{st.session_state['target_protein']} g**
       - **Lemak (L):** 30% dari Kalori dibagi 9 (karena 1g lemak = 9 kkal) = **{st.session_state['target_lemak']} g**
       - **Karbohidrat (C):** 55% dari Kalori dibagi 4 (karena 1g karbo = 4 kkal) = **{st.session_state['target_karbo']} g**
    """)
    
    df_aktif = st.session_state['db_bahan'][st.session_state['db_bahan']["Gunakan"] == True].reset_index(drop=True)
    
    if len(df_aktif) < 2:
        st.warning("⚠️ Silakan centang minimal 2 bahan makanan di Tab 2 untuk melihat simulasi matriksnya.")
    else:
        st.write("---")
        st.write("#### TAHAP 2: Model Matematika (Fungsi Asli)")
        st.write("Keempat nilai makronutrien di atas kini dijadikan batas minimal ($\ge$) yang harus dipenuhi oleh kombinasi makanan.")
        
        z_terms = [f"{int(row['Harga (Rp)'])}x_{i+1}" for i, row in df_aktif.iterrows()]
        st.latex(r"\text{Fungsi Tujuan (Minimasi Biaya): } Z = " + " + ".join(z_terms))
        
        k_terms = [f"{row['Kalori (Kkal)']}x_{i+1}" for i, row in df_aktif.iterrows()]
        p_terms = [f"{row['Protein (g)']}x_{i+1}" for i, row in df_aktif.iterrows()]
        l_terms = [f"{row['Lemak (g)']}x_{i+1}" for i, row in df_aktif.iterrows()]
        c_terms = [f"{row['Karbohidrat (g)']}x_{i+1}" for i, row in df_aktif.iterrows()]
        
        st.latex(r"\text{Kendala 1 (Kalori): } " + " + ".join(k_terms) + f" \ge {st.session_state['target_kalori']}")
        st.latex(r"\text{Kendala 2 (Protein): } " + " + ".join(p_terms) + f" \ge {st.session_state['target_protein']}")
        st.latex(r"\text{Kendala 3 (Lemak): } " + " + ".join(l_terms) + f" \ge {st.session_state['target_lemak']}")
        st.latex(r"\text{Kendala 4 (Karbo): } " + " + ".join(c_terms) + f" \ge {st.session_state['target_karbo']}")
        
        st.write("---")
        st.write("#### TAHAP 3: Bentuk Kanonik (Surplus & Artificial Variables)")
        st.write("Sistem Simpleks tidak bisa membaca tanda $\ge$. Maka dikurangkan variabel Surplus ($S$) agar menjadi persaman ($=$). Karena hal itu menyebabkan identitas negatif, ditambahkan **Variabel Semu / Artificial ($R$)** agar komputer punya titik awal matriks.")
        st.latex(" + ".join(k_terms) + f" - S_1 + R_1 = {st.session_state['target_kalori']}")
        st.latex(" + ".join(p_terms) + f" - S_2 + R_2 = {st.session_state['target_protein']}")
        st.latex(" + ".join(l_terms) + f" - S_3 + R_3 = {st.session_state['target_lemak']}")
        st.latex(" + ".join(c_terms) + f" - S_4 + R_4 = {st.session_state['target_karbo']}")
        
        st.write("---")
        st.write("#### TAHAP 4: FASE 1 (Mencari Solusi Awal Fisibel) ")
        st.write("Pada Fase 1, nilai uang (Z) diabaikan sementara. Tujuan algoritma diubah menjadi **meminimalkan total Variabel Semu ($W = R_1 + R_2 + R_3 + R_4$)**. Jika $W$ berhasil menyentuh $0$, berarti kombinasi porsi makanan yang logis (tidak minus) telah ditemukan.")
        st.latex(r"\text{Fungsi Tujuan Fase 1: Minimasi } W = R_1 + R_2 + R_3 + R_4")
        
        # Matriks Dinamis Fase 1 (Diperluas untuk 4 Kendala)
        kolom_x = [f"x{i+1}" for i in range(len(df_aktif))]
        kolom_lengkap = ["Basis"] + kolom_x + ["S1", "S2", "S3", "S4", "R1", "R2", "R3", "R4", "NK (B)"]
        
        baris_r1 = ["R1"] + list(df_aktif["Kalori (Kkal)"]) + [-1, 0, 0, 0,  1, 0, 0, 0, st.session_state['target_kalori']]
        baris_r2 = ["R2"] + list(df_aktif["Protein (g)"]) + [0, -1, 0, 0,  0, 1, 0, 0, st.session_state['target_protein']]
        baris_r3 = ["R3"] + list(df_aktif["Lemak (g)"]) + [0, 0, -1, 0,  0, 0, 1, 0, st.session_state['target_lemak']]
        baris_r4 = ["R4"] + list(df_aktif["Karbohidrat (g)"]) + [0, 0, 0, -1,  0, 0, 0, 1, st.session_state['target_karbo']]
        baris_w  = ["W (Z-Fase 1)"] + [0]*len(df_aktif) + [0, 0, 0, 0,  -1, -1, -1, -1, 0] 
        
        df_matriks = pd.DataFrame([baris_r1, baris_r2, baris_r3, baris_r4, baris_w], columns=kolom_lengkap)
        st.dataframe(df_matriks.style.format(precision=1), use_container_width=True, hide_index=True)
        st.caption("📌 *Ini adalah Tableau Initial Fase 1. Operasi Baris Elementer (OBE) akan mereduksi matriks ini hingga nilai pada baris W tidak ada lagi yang negatif.*")
        
        st.write("---")
        st.write("#### TAHAP 5: FASE 2 (Optimasi Biaya Termurah)")
        st.write("Setelah Fase 1 berhasil menyingkirkan elemen fiktif, kolom $R$ dibuang. Algoritma mengembalikan fungsi biaya asli ($Z$) ke dalam matriks dan melakukan iterasi penutupan untuk mencari titik temu antara **Gizi Terpenuhi** dan **Harga Termurah**. Hasil akhirnya adalah apa yang Anda lihat di layar utama Tab 2.")
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- HALAMAN 4: DOKUMENTASI (RUMUS) ---
with tab_docs:
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### 📖 Integrasi Matriks Aljabar")
    st.write("Sistem Persamaan Linier dimodelkan dengan notasi matriks abstrak:")
    st.latex(r"\text{Fungsi Minimum: } Z = \mathbf{C}^T \mathbf{X}")
    st.latex(r"\text{Batasan Mutlak (Matriks): } \mathbf{A}\mathbf{X} \ge \mathbf{B}")
    
    st.write("Penjelasan Variabel Ruang Vektor:")
    st.markdown("""
    - $C$ : Vektor harga makanan.
    - $X$ : Vektor penyelesaian (takaran/porsi makanan).
    - $A$ : Matriks kandungan gizi.
    - $B$ : Vektor target minimal nutrisi anak.
    """)
    st.markdown('</div>', unsafe_allow_html=True)