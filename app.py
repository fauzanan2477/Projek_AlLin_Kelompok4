import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS
# ==========================================
st.set_page_config(page_title="Sistem Pakar MBG", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; color: #111111; }
    .block-container { padding-top: 2rem; max-width: 1100px; }
    .white-box { background-color: #ffffff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #e1e4e8; color: #333333;}
    
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 20px; border-bottom: 2px solid #dcdde1; background-color: #ffffff; padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { font-weight: 800; font-size: 1.1rem; color: #555555; background-color: transparent; border: none; }
    .stTabs [aria-selected="true"] { color: #1e3799; border-bottom: 4px solid #1e3799; }
    
    h1, h2, h3, h4, p { color: #111111 !important; }
    .hero-title { font-size: 3rem; font-weight: 900; color: #000000 !important; line-height: 1.2; margin-bottom: 10px; text-align: center; }
    .hero-title span { color: #1e3799 !important; }
    .hero-subtitle { font-size: 1.1rem; color: #444444 !important; font-weight: 500; text-align: center; margin-bottom: 30px;}
    
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
<div class="hero-subtitle">Mendukung SDG 2 & 3 | Engine: Ilmu Gizi Biometrik & Matriks Simpleks</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATABASE (SESSION STATE)
# ==========================================
if 'db_bahan' not in st.session_state:
    st.session_state['db_bahan'] = pd.DataFrame({
        "Gunakan": [True, True, True, True, False, False], 
        "Bahan Makanan": ["Nasi Putih", "Telur Ayam", "Tempe Murni", "Sayur Bayam", "Susu Sapi", "Daging Ayam"],
        "Harga (Rp)": [1200, 2600, 1000, 800, 3000, 4500], 
        "Kalori (Kkal)": [130.0, 155.0, 193.0, 23.0, 60.0, 165.0],
        "Protein (g)": [2.7, 13.0, 19.0, 3.0, 3.2, 31.0],
        "Lemak (g)": [0.3, 11.0, 11.0, 0.4, 3.3, 3.6],
        "Batas Maks (g)": [250.0, 100.0, 100.0, 150.0, 200.0, 150.0] 
    })

if 'target_kalori' not in st.session_state:
    st.session_state.update({'target_kalori': 600.0, 'target_protein': 22.0, 'target_lemak': 15.0})

# ==========================================
# 4. MENU NAVBAR (TABS)
# ==========================================
tab_gizi, tab_aljabar, tab_manual = st.tabs([
    "1. Kalkulator Gizi", 
    "2. Eksekusi Optimasi (SPL)", 
    "3. Langkah Manual (Backend Matriks)"
])

# --- HALAMAN 1: KALKULATOR GIZI ---
with tab_gizi:
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### 👦 Penentuan Vektor Target Gizi (Konstanta B)")
    st.write("Sistem menghitung target gizi anak berdasarkan persamaan biometrik Harris-Benedict untuk 1 porsi makan siang MBG.")
    
    col_bio1, col_bio2 = st.columns(2)
    with col_bio1:
        umur = st.number_input("Umur Anak (Tahun)", min_value=5, max_value=18, value=10)
        jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    with col_bio2:
        bb = st.number_input("Berat Badan (kg)", min_value=15.0, value=30.0)
        tb = st.number_input("Tinggi Badan (cm)", min_value=100.0, value=135.0)
    
    if st.button("Hitung Target & Simpan", type="primary"):
        if jk == "Laki-laki": bmr = 66.5 + (13.7 * bb) + (5 * tb) - (6.8 * umur)
        else: bmr = 655 + (9.6 * bb) + (1.8 * tb) - (4.7 * umur)
        
        porsi_kalori = (bmr * 1.55) / 3 
        
        st.session_state['target_kalori'] = round(porsi_kalori, 1)
        st.session_state['target_protein'] = round((porsi_kalori * 0.15) / 4, 1)
        st.session_state['target_lemak'] = round((porsi_kalori * 0.30) / 9, 1)
        st.success("Target Vektor Gizi berhasil diperbarui!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- HALAMAN 2: EKSEKUSI OPTIMASI (ALJABAR) ---
with tab_aljabar:
    st.markdown('<div class="white-box" style="border-left: 5px solid #1e3799; background-color:#f0f4f8;">', unsafe_allow_html=True)
    st.write("#### 🎯 Target Gizi Saat Ini (Syarat Matriks $\ge$ B):")
    c1, c2, c3 = st.columns(3)
    c1.metric("Kalori Minimal", f"{st.session_state['target_kalori']} Kkal")
    c2.metric("Protein Minimal", f"{st.session_state['target_protein']} Gram")
    c3.metric("Lemak Minimal", f"{st.session_state['target_lemak']} Gram")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### 🛒 Database Bahan Makanan (Pilih Lauk)")
    st.caption("Centang kolom **'Gunakan'** untuk menghitung makanan tersebut. Sesuaikan **'Batas Maks'** agar algoritma memberikan variasi menu, bukan hanya memilih 1 makanan paling murah.")
    
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
            batas_multiplier = pd.to_numeric(df_dipilih["Batas Maks (g)"], errors='coerce').fillna(1000).values / 100.0
            
            A_ub = -1 * gizi.values.T
            b_ub = -1 * np.array([st.session_state['target_kalori'], st.session_state['target_protein'], st.session_state['target_lemak']])
            batas = [(0, maks) for maks in batas_multiplier]
            
            try:
                hasil = linprog(harga, A_ub=A_ub, b_ub=b_ub, bounds=batas, method='highs')
                
                if hasil.success:
                    st.markdown(f"""
                    <div class="result-card">
                        <p>Total Biaya Paling Minimum (Titik Optimal Matriks)</p>
                        <h2>Rp {hasil.fun:,.0f}</h2>
                        <p>Satu Porsi Lengkap Sesuai Standar Gizi</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('<div class="white-box">', unsafe_allow_html=True)
                    st.write("### ⚖️ Vektor Penyelesaian (Kombinasi Takaran Makanan)")
                    hasil_gram = hasil.x * 100 
                    df_hasil = pd.DataFrame({
                        "Bahan Makanan": df_dipilih["Bahan Makanan"].values,
                        "Takaran Disarankan": [f"{g:,.0f} Gram" for g in hasil_gram],
                        "Biaya Realisasi": [f"Rp {(g/100)*h:,.0f}" for g, h in zip(hasil_gram, harga)]
                    })
                    st.table(df_hasil[hasil.x > 0.01].reset_index(drop=True))
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("🚨 SPL Infeasible: Matriks tidak menemukan titik temu. Makanan yang Anda pilih tidak bisa mencapai target gizi tanpa melanggar 'Batas Maks'. Coba naikkan batas maksimal tempe/telur, atau tambah variasi daging!")
            except Exception as e:
                st.error(f"Error komputasi: {e}")

# --- HALAMAN 3: LANGKAH MANUAL DINAMIS ---
with tab_manual:
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### ✍️ Backend Hitungan: Pemodelan Matriks Berjalan")
    st.write("Langkah-langkah di bawah ini di-*generate* secara dinamis berdasarkan data makanan yang Anda centang di Tab 2.")
    
    # Mengambil data yang sedang aktif dicentang
    df_aktif = st.session_state['db_bahan']
    df_aktif = df_aktif[df_aktif["Gunakan"] == True].reset_index(drop=True)
    
    if len(df_aktif) > 0:
        # 1. GENERATE FUNGSI Z (DINAMIS)
        st.write("#### 1. Fungsi Objektif (Minimasi Harga)")
        z_str = " + ".join([f"{int(harga)}x_{i+1}" for i, harga in enumerate(df_aktif['Harga (Rp)'])])
        st.latex(rf"\text{{Min }} Z = {z_str}")
        
        # 2. GENERATE FUNGSI KENDALA (DINAMIS)
        st.write("#### 2. Matriks Kendala Nutrisi (Pertidaksamaan)")
        kalori_str = " + ".join([f"{kal}x_{i+1}" for i, kal in enumerate(df_aktif['Kalori (Kkal)'])])
        protein_str = " + ".join([f"{pro}x_{i+1}" for i, pro in enumerate(df_aktif['Protein (g)'])])
        lemak_str = " + ".join([f"{lem}x_{i+1}" for i, lem in enumerate(df_aktif['Lemak (g)'])])
        
        st.latex(rf"\text{{Kalori: }} {kalori_str} \ge {st.session_state['target_kalori']}")
        st.latex(rf"\text{{Protein: }} {protein_str} \ge {st.session_state['target_protein']}")
        st.latex(rf"\text{{Lemak: }} {lemak_str} \ge {st.session_state['target_lemak']}")
        
        # 3. BATAS MAKSIMAL
        st.write("#### 3. Kendala Upper Bound (Batas Variasi)")
        bounds_str = ", ".join([f"x_{i+1} \le {maks/100}" for i, maks in enumerate(df_aktif['Batas Maks (g)'])])
        st.latex(rf"\text{{Batas Porsi: }} {bounds_str}")
        
        st.write("---")
        st.write("#### 4. Iterasi Operasi Baris Elementer (Metode Simpleks)")
        st.write("Komputer mengubah model di atas menjadi **Bentuk Kanonik** dengan menambahkan *Slack Variables* (S) dan *Surplus Variables*. Kemudian, algoritma menyusunnya ke dalam **Tabel Simpleks (Tableau)**.")
        st.info("Sistem melakukan **Operasi Baris Elementer (Pivot)** secara berulang-ulang untuk mengeliminasi kolom variabel hingga baris fungsi $Z$ tidak lagi memiliki nilai negatif. Saat itulah, kombinasi biaya termurah mutlak ditemukan.")
    else:
        st.warning("Pilih minimal 1 bahan makanan di Tab 2 untuk melihat langkah manualnya.")
    st.markdown('</div>', unsafe_allow_html=True)