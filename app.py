import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Optimasi MBG", layout="wide")

st.markdown("""
    <style>
    /* Desain CSS meniru gaya website modern yang bersih */
    .block-container { padding-top: 1rem; max-width: 900px; }
    
    /* Navbar Custom */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; border-bottom: none; gap: 20px; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; font-size: 16px; color: #555; background-color: transparent; border: none; }
    .stTabs [aria-selected="true"] { color: #0056ff; border-bottom: 3px solid #0056ff; }
    
    /* Hero Section */
    .hero-section { text-align: center; padding: 40px 0px 30px 0px; }
    .hero-title { font-size: 3.5rem; font-weight: 900; color: #111; line-height: 1.2; margin-bottom: 15px;}
    .hero-title span { color: #0056ff; }
    .hero-subtitle { font-size: 1.2rem; color: #666; font-weight: 500; margin-bottom: 30px;}
    
    /* Card Hasil */
    .result-card { background-color: #f0f7ff; border-radius: 15px; padding: 30px; text-align: center; border: 1px solid #d0e3ff; margin-top:20px;}
    .result-card h2 { color: #0056ff; font-size: 3rem; margin: 0; font-weight: 800;}
    .result-card p { color: #333; font-size: 1.1rem; margin: 0; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HERO SECTION (TAMPILAN MIRIP WEBSITE)
# ==========================================
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">Sistem Optimasi<br><span>Makan Bergizi Gratis</span></h1>
    <p class="hero-subtitle">Explore how Linear Equations and the Simplex Method optimize<br>national meal budgets while ensuring nutritional standards.</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATABASE MAKANAN (DEFAULT)
# ==========================================
if 'db_bahan' not in st.session_state:
    st.session_state['db_bahan'] = pd.DataFrame({
        "Bahan Makanan": ["Nasi Putih", "Telur Rebus", "Tempe Goreng", "Sayur Bayam", "Susu UHT"],
        "Harga (Rp)": [1200, 2600, 1000, 800, 3000], 
        "Kalori (Kkal)": [130, 155, 193, 23, 60],
        "Protein (g)": [2.7, 13.0, 19.0, 3.0, 3.2],
        "Lemak (g)": [0.3, 11.0, 11.0, 0.4, 3.3]
    })

# ==========================================
# 4. NAVBAR & HALAMAN
# ==========================================
tab_home, tab_app, tab_docs = st.tabs(["Home", "Try App", "Docs"])

# --- HALAMAN 1: HOME (PENJELASAN SINGKAT) ---
with tab_home:
    st.info("👋 **Selamat Datang!** Aplikasi ini adalah implementasi dari Tugas Projek Aljabar Linier. Kami menggunakan algoritma *Scipy Optimize* untuk mensimulasikan pencarian harga termurah dari program MBG (SDG 2 & 3). Silakan buka menu **Try App** untuk menjalankan simulasi.")
    
# --- HALAMAN 2: APLIKASI UTAMA (KALKULATOR SIMPLEKS) ---
with tab_app:
    st.write("### ⚙️ Konfigurasi Target Gizi (Vektor Kendala)")
    col1, col2, col3 = st.columns(3)
    with col1: min_kalori = st.number_input("Target Kalori", value=700.0)
    with col2: min_protein = st.number_input("Target Protein", value=25.0)
    with col3: min_lemak = st.number_input("Target Lemak", value=15.0)
    
    st.write("---")
    st.write("### 📝 Tabel Harga Pasar & Gizi (Matriks Input)")
    df_interaktif = st.data_editor(st.session_state['db_bahan'], num_rows="dynamic", use_container_width=True)
    st.session_state['db_bahan'] = df_interaktif
    
    st.write("")
    
    # Tombol Eksekusi
    if st.button("🚀 Jalankan Optimasi Aljabar (Run Simplex)", type="primary", use_container_width=True):
        df = st.session_state['db_bahan']
        
        # PERBAIKAN BUG TYPE-ERROR: Memaksa kolom menjadi angka (float)
        harga = pd.to_numeric(df["Harga (Rp)"], errors='coerce').fillna(0).values
        gizi = df[["Kalori (Kkal)", "Protein (g)", "Lemak (g)"]].apply(pd.to_numeric, errors='coerce').fillna(0)
        
        # PROSES MATEMATIKA (SPL)
        # Dikali -1 karena scipy membaca <= , sedangkan batas gizi kita adalah >=
        A_ub = -1 * gizi.values.T
        b_ub = -1 * np.array([min_kalori, min_protein, min_lemak])
        batas = [(0, None) for _ in range(len(harga))]
        
        try:
            hasil = linprog(harga, A_ub=A_ub, b_ub=b_ub, bounds=batas, method='highs')
            
            if hasil.success:
                st.markdown(f"""
                <div class="result-card">
                    <p>Total Biaya Termurah Secara Matematis</p>
                    <h2>Rp {hasil.fun:,.0f}</h2>
                    <p style="color:#666; font-size:0.9rem; margin-top:5px;">Per Porsi / Anak</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("### ⚖️ Vektor Rekomendasi Takaran")
                hasil_gram = hasil.x * 100 
                df_hasil = pd.DataFrame({
                    "Bahan Makanan": df["Bahan Makanan"],
                    "Rekomendasi Takaran": [f"{g:,.0f} Gram" for g in hasil_gram]
                })
                # Tampilkan makanan yang takarannya > 0
                st.table(df_hasil[hasil.x > 0.01].reset_index(drop=True))
            else:
                st.error("🚨 Matriks Infeasible: Garis kendala tidak menemukan titik temu. Target nutrisi terlalu tinggi untuk kombinasi makanan yang ada.")
                
        except Exception as e:
            st.error(f"Terjadi kesalahan kalkulasi: {e}")

# --- HALAMAN 3: DOCS (RUMUS MATEMATIKA) ---
with tab_docs:
    st.write("### 📖 Dokumentasi Aljabar Linier")
    st.write("Sistem Persamaan Linier di atas dimodelkan dengan fungsi:")
    st.latex(r"\text{Fungsi Objektif (Minimasi): } Z = \mathbf{C}^T \mathbf{X}")
    st.latex(r"\text{Sistem Kendala Matriks: } \mathbf{A}\mathbf{X} \ge \mathbf{B}")
    st.write("Metode Simpleks akan menghitung Vektor $X$ (Takaran Makanan) yang menghasilkan nilai $Z$ paling minimum.")