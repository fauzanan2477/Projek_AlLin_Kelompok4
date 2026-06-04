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
    .block-container { padding-top: 2rem; max-width: 1050px; }
    
    /* Box Teks & Elemen UI berwarna Putih Bersih dengan Shadow */
    .white-box { background-color: #ffffff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #e1e4e8; color: #333333;}
    
    /* Navbar Custom */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 30px; border-bottom: 2px solid #dcdde1; background-color: #ffffff; padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { font-weight: 800; font-size: 1.15rem; color: #555555; background-color: transparent; border: none; }
    .stTabs [aria-selected="true"] { color: #1e3799; border-bottom: 4px solid #1e3799; }
    
    /* Typography */
    h1, h2, h3, h4, p { color: #111111 !important; }
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
<div class="hero-subtitle">Integrasi Ilmu Gizi Biometrik dan Aljabar Linier (Metode Matriks Simpleks)</div>
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
        "Porsi (g)": [200.0, 100.0, 100.0, 150.0, 200.0, 150.0] 
    })

if 'target_kalori' not in st.session_state:
    st.session_state.update({'target_kalori': 600.0, 'target_protein': 22.0, 'target_lemak': 15.0})

# ==========================================
# 4. MENU NAVBAR (TABS)
# ==========================================
tab_gizi, tab_aljabar, tab_manual, tab_docs = st.tabs([
    "1. Kalkulator Gizi", 
    "2. Eksekusi Optimasi", 
    "3. Langkah Manual (Jurnal)", 
    "4. Dokumentasi Rumus"
])

# --- HALAMAN 1: KALKULATOR GIZI ---
with tab_gizi:
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### 👦 Penentuan Vektor Konstanta Gizi (B)")
    st.write("Sistem menghitung target gizi anak (AKG) berdasarkan persamaan biometrik untuk digunakan sebagai batas matriks di halaman berikutnya.")
    
    col_bio1, col_bio2 = st.columns(2)
    with col_bio1:
        umur = st.number_input("Umur Anak (Tahun)", min_value=5, max_value=18, value=10)
        jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    with col_bio2:
        bb = st.number_input("Berat Badan (kg)", min_value=15.0, value=30.0)
        tb = st.number_input("Tinggi Badan (cm)", min_value=100.0, value=135.0)
    
    if st.button("Hitung Target & Simpan", type="primary"):
        # Harris Benedict Formula
        if jk == "Laki-laki":
            bmr = 66.5 + (13.7 * bb) + (5 * tb) - (6.8 * umur)
        else:
            bmr = 655 + (9.6 * bb) + (1.8 * tb) - (4.7 * umur)
        
        porsi_kalori = (bmr * 1.55) / 3 
        porsi_protein = (porsi_kalori * 0.15) / 4 
        porsi_lemak = (porsi_kalori * 0.30) / 9 
        
        st.session_state['target_kalori'] = round(porsi_kalori, 1)
        st.session_state['target_protein'] = round(porsi_protein, 1)
        st.session_state['target_lemak'] = round(porsi_lemak, 1)
        st.success("Target Vektor Gizi berhasil diperbarui! Lanjut ke Tab 2.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- HALAMAN 2: EKSEKUSI OPTIMASI (ALJABAR) ---
with tab_aljabar:
    # MENAMPILKAN TARGET GIZI SEBAGAI PENGINGAT
    st.markdown('<div class="white-box" style="border-left: 5px solid #e1b12c;">', unsafe_allow_html=True)
    st.write("#### 🎯 Target Gizi Saat Ini (Syarat Matriks):")
    c1, c2, c3 = st.columns(3)
    c1.metric("Kalori Minimal", f"{st.session_state['target_kalori']} Kkal")
    c2.metric("Protein Minimal", f"{st.session_state['target_protein']} Gram")
    c3.metric("Lemak Minimal", f"{st.session_state['target_lemak']} Gram")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### 🛒 Database Bahan Makanan (Pilih Lauk)")
    st.caption("Centang kolom **'Gunakan'** untuk mengikutkan makanan. Sesuaikan **'Porsi'** agar gizi anak anak terpenuhi.")
    st.caption("**'Keterangan'**: Harga dan Kandungan Gizi(Karbohidrat, Protein, dan Lemak) ditulis dalam nilai **'per 100 gram'**.")

    df_interaktif = st.data_editor(st.session_state['db_bahan'], num_rows="dynamic", use_container_width=True, hide_index=True)
    st.session_state['db_bahan'] = df_interaktif
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🚀 Kalkulasi Biaya Termurah (Metode Simpleks)", type="primary", use_container_width=True):
        df_dipilih = df_interaktif[df_interaktif["Gunakan"] == True].copy()
        
        if len(df_dipilih) < 2:
            st.error("⚠️ Centang minimal 2 bahan makanan untuk komputasi.")
        else:
            harga = pd.to_numeric(df_dipilih["Harga (Rp)"], errors='coerce').fillna(0).values
            gizi = df_dipilih[["Kalori (Kkal)", "Protein (g)", "Lemak (g)"]].apply(pd.to_numeric, errors='coerce').fillna(0)
            porsi_makan = pd.to_numeric(df_dipilih["Porsi (g)"], errors='coerce').fillna(1000).values / 100.0
            
            A_ub = -1 * gizi.values.T
            b_ub = -1 * np.array([st.session_state['target_kalori'], st.session_state['target_protein'], st.session_state['target_lemak']])
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
                    st.error("🚨 SPL Infeasible: Sistem tidak bisa memenuhi target gizi dengan lauk yang dipilih. Coba tambah 'Porsi' makanan.")
            except Exception as e:
                st.error(f"Error komputasi: {e}")

# --- HALAMAN 3: LANGKAH MANUAL (DINAMIS & REAL-TIME) ---
with tab_manual:
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### ✍️ Urutan Perhitungan Manual Metode Simpleks (Otomatis)")
    st.write("Berikut adalah langkah-langkah pemodelan aljabar linear yang di-*generate* langsung berdasarkan data bahan makanan yang Anda centang di Tab 2.")
    
    # Ambil data yang aktif (dicentang) dari Tab 2
    df_aktif = st.session_state['db_bahan'][st.session_state['db_bahan']["Gunakan"] == True].reset_index(drop=True)
    
    if len(df_aktif) < 2:
        st.warning("⚠️ Silakan centang minimal 2 bahan makanan di Tab 2 untuk melihat simulasi matriks manualnya.")
    else:
        # --- LANGKAH 1 ---
        st.write("#### Langkah 1: Model Matematika (Sistem Persamaan Linier)")
        st.write("Menetapkan fungsi minimum dan fungsi kendala berdasarkan makanan yang dipilih.")
        
        # Build Fungsi Tujuan dinamis
        z_terms = [f"{int(row['Harga (Rp)'])}x_{i+1}" for i, row in df_aktif.iterrows()]
        st.latex(r"\text{Minimumkan: } Z = " + " + ".join(z_terms))
        
        # Build Fungsi Kendala dinamis
        k_terms = [f"{row['Kalori (Kkal)']}x_{i+1}" for i, row in df_aktif.iterrows()]
        p_terms = [f"{row['Protein (g)']}x_{i+1}" for i, row in df_aktif.iterrows()]
        l_terms = [f"{row['Lemak (g)']}x_{i+1}" for i, row in df_aktif.iterrows()]
        
        st.latex(r"\text{Kendala 1 (Kalori): } " + " + ".join(k_terms) + f" \ge {st.session_state['target_kalori']}")
        st.latex(r"\text{Kendala 2 (Protein): } " + " + ".join(p_terms) + f" \ge {st.session_state['target_protein']}")
        st.latex(r"\text{Kendala 3 (Lemak): } " + " + ".join(l_terms) + f" \ge {st.session_state['target_lemak']}")
        
        # --- LANGKAH 2 ---
        st.write("#### Langkah 2: Bentuk Kanonik (Penambahan Surplus Variables)")
        st.write("Pertidaksamaan ($\ge$) diubah menjadi persamaan ($=$) dengan mengurangkan variabel surplus ($S$) agar dapat diolah ke dalam matriks.")
        st.latex(" + ".join(k_terms) + f" - S_1 = {st.session_state['target_kalori']}")
        st.latex(" + ".join(p_terms) + f" - S_2 = {st.session_state['target_protein']}")
        st.latex(" + ".join(l_terms) + f" - S_3 = {st.session_state['target_lemak']}")
        
        # --- LANGKAH 3 ---
        st.write("#### Langkah 3: Membangun Tabel Simpleks (Initial Tableau Matriks)")
        st.write("Menyusun seluruh koefisien persamaan di atas ke dalam bentuk matriks.")
        
        # Membuat header tabel (Kolom x1, x2, ..., S1, S2, S3, NK)
        var_cols = [f"x{i+1}" for i in range(len(df_aktif))]
        cols = ["Basis"] + var_cols + ["S1", "S2", "S3", "Nilai Kanan (NK)"]
        
        # Mengisi baris matriks secara dinamis
        row_s1 = ["S1"] + list(df_aktif["Kalori (Kkal)"]) + [-1, 0, 0, st.session_state['target_kalori']]
        row_s2 = ["S2"] + list(df_aktif["Protein (g)"]) + [0, -1, 0, st.session_state['target_protein']]
        row_s3 = ["S3"] + list(df_aktif["Lemak (g)"]) + [0, 0, -1, st.session_state['target_lemak']]
        # Baris fungsi Z (Nilai harga diubah menjadi negatif untuk iterasi minimum)
        row_z = ["Z"] + [-int(x) for x in df_aktif["Harga (Rp)"]] + [0, 0, 0, 0]
        
        df_tableau = pd.DataFrame([row_s1, row_s2, row_s3, row_z], columns=cols)
        
        # Tampilkan matriks menggunakan DataFrame dengan presisi angka yang rapi
        st.dataframe(df_tableau.style.format(precision=1), use_container_width=True, hide_index=True)
        st.caption("*(Keterangan: Matriks di atas akan terus berubah menyesuaikan bahan dan harga yang Anda edit di Tab 2)*")
        
        # --- LANGKAH 4 & 5 ---
        st.write("#### Langkah 4: Iterasi Matriks (Operasi Baris Elementer)")
        st.markdown("""
        Untuk menemukan titik optimal termurah, komputer melakukan tahapan berikut:
        1. **Menentukan Kolom Pivot:** Memilih kolom dengan nilai paling negatif pada baris Z terbawah.
        2. **Menentukan Baris Pivot:** Membagi Nilai Kanan (NK) dengan elemen pada Kolom Pivot (mencari rasio positif terkecil).
        3. **Operasi Baris Elementer (OBE):** Menggunakan perkalian dan penjumlahan antar baris untuk mengubah elemen Pivot menjadi **1**, dan elemen lain di kolom tersebut menjadi **0**. Proses ini sama dengan mencari *Invers Matriks*.
        """)
        
        st.write("#### Langkah 5: Kondisi Optimal (Hasil Akhir)")
        st.success("Iterasi OBE tersebut dilakukan berulang-ulang oleh sistem hingga **tidak ada lagi nilai negatif** pada baris $Z$. Saat iterasi berhenti, nilai pada kolom 'Nilai Kanan (NK)' di baris Z adalah Harga Mutlak Termurah yang muncul di layar kalkulator utama!")
        
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