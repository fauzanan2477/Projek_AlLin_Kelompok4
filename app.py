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
    /* Latar belakang putih bersih dan ukuran kontainer menengah agar elegan */
    .block-container { padding-top: 1rem; max-width: 950px; }
    
    /* Mengubah desain Tabs menjadi Menu Navbar Besar */
    .stTabs [data-baseweb="tab-list"] { 
        justify-content: center; 
        gap: 40px; 
        border-bottom: 2px solid #f0f0f0; 
        padding-bottom: 10px;
    }
    .stTabs [data-baseweb="tab"] { 
        font-weight: 800; 
        font-size: 1.3rem; /* Teks Menu Besar */
        color: #888; 
        background-color: transparent; 
        border: none; 
    }
    .stTabs [aria-selected="true"] { 
        color: #0056ff; 
        border-bottom: 4px solid #0056ff; 
    }
    
    /* Desain Teks Utama (Hero Section) */
    .hero-section { text-align: center; padding: 40px 0px 20px 0px; }
    .hero-title { font-size: 3.5rem; font-weight: 900; color: #111; line-height: 1.2; margin-bottom: 15px;}
    .hero-title span { color: #0056ff; }
    .hero-subtitle { font-size: 1.2rem; color: #555; font-weight: 500; margin-bottom: 30px;}
    
    /* Desain Kotak Hasil (Card) */
    .result-card { 
        background-color: #f4f8ff; 
        border-radius: 15px; 
        padding: 30px; 
        text-align: center; 
        border: 1px solid #d0e3ff; 
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .result-card h2 { color: #0056ff; font-size: 3.5rem; margin: 0; font-weight: 900;}
    .result-card p { color: #333; font-size: 1.2rem; margin: 0; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HERO SECTION (TAMPILAN MIRIP WEBSITE)
# ==========================================
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">Sistem Optimasi Aljabar<br><span>Makan Bergizi Gratis</span></h1>
    <p class="hero-subtitle">Mendukung SDG 2 & 3 | Engine: Matriks & Metode Simpleks</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATABASE MAKANAN (DENGAN FITUR CEKLIS)
# ==========================================
if 'db_bahan' not in st.session_state:
    st.session_state['db_bahan'] = pd.DataFrame({
        "Gunakan": [True, True, True, True, False, False], # Fitur Checkbox untuk memilih
        "Bahan Makanan": ["Nasi Putih", "Telur Rebus", "Tempe Goreng", "Sayur Bayam", "Susu UHT", "Daging Sapi"],
        "Harga (Rp)": [1200, 2600, 1000, 800, 3000, 12000], 
        "Kalori (Kkal)": [130.0, 155.0, 193.0, 23.0, 60.0, 250.0],
        "Protein (g)": [2.7, 13.0, 19.0, 3.0, 3.2, 26.0],
        "Lemak (g)": [0.3, 11.0, 11.0, 0.4, 3.3, 15.0]
    })

# ==========================================
# 4. MENU UTAMA (NAVBAR)
# ==========================================
tab_app, tab_docs = st.tabs(["Beranda Kalkulator", "Dokumentasi & Teori"])

# --- HALAMAN 1: KALKULATOR ---
with tab_app:
    st.write("### ⚙️ 1. Target Gizi (Vektor Kendala)")
    col1, col2, col3 = st.columns(3)
    with col1: min_kalori = st.number_input("Target Kalori Minimal", value=700.0)
    with col2: min_protein = st.number_input("Target Protein Minimal", value=25.0)
    with col3: min_lemak = st.number_input("Target Lemak Minimal", value=15.0)
    
    st.write("---")
    st.write("### 🛒 2. Matriks Bahan Makanan (Pilih Menu Hari Ini)")
    st.caption("Beri centang pada kolom **'Gunakan'** untuk memasukkan bahan tersebut ke dalam perhitungan aljabar.")
    
    # Tabel interaktif
    df_interaktif = st.data_editor(
        st.session_state['db_bahan'], 
        num_rows="dynamic", 
        use_container_width=True,
        hide_index=True
    )
    st.session_state['db_bahan'] = df_interaktif
    
    st.write("<br>", unsafe_allow_html=True)
    
    # Tombol Eksekusi
    if st.button("🚀 Hitung Vektor Biaya Termurah (Jalankan Simpleks)", type="primary", use_container_width=True):
        
        # FITUR CERDAS: Hanya mengambil makanan yang dicentang "True"
        df_dipilih = df_interaktif[df_interaktif["Gunakan"] == True].copy()
        
        if len(df_dipilih) < 2:
            st.error("⚠️ Silakan centang minimal 2 bahan makanan untuk membandingkan harganya.")
        else:
            # Memastikan tipe data adalah angka untuk mencegah Error
            harga = pd.to_numeric(df_dipilih["Harga (Rp)"], errors='coerce').fillna(0).values
            gizi = df_dipilih[["Kalori (Kkal)", "Protein (g)", "Lemak (g)"]].apply(pd.to_numeric, errors='coerce').fillna(0)
            
            # --- PROSES MATEMATIKA (SPL) ---
            # Dikali -1 karena scipy membaca <= , sedangkan batas gizi kita adalah >=
            A_ub = -1 * gizi.values.T
            b_ub = -1 * np.array([min_kalori, min_protein, min_lemak])
            batas = [(0, None) for _ in range(len(harga))]
            
            try:
                hasil = linprog(harga, A_ub=A_ub, b_ub=b_ub, bounds=batas, method='highs')
                
                if hasil.success:
                    st.markdown(f"""
                    <div class="result-card">
                        <p>Titik Potong SPL Ditemukan! Total Biaya Termurah:</p>
                        <h2>Rp {hasil.fun:,.0f}</h2>
                        <p style="color:#555; font-size:1rem; margin-top:5px;">Per Porsi Anak</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("### ⚖️ Vektor Rekomendasi Takaran (Matriks Solusi)")
                    
                    # Ekstrak takaran gram dari matriks hasil
                    hasil_gram = hasil.x * 100 
                    df_hasil = pd.DataFrame({
                        "Bahan Makanan": df_dipilih["Bahan Makanan"].values,
                        "Rekomendasi Takaran": [f"{g:,.0f} Gram" for g in hasil_gram],
                        "Alokasi Harga": [f"Rp {(g/100)*h:,.0f}" for g, h in zip(hasil_gram, harga)]
                    })
                    
                    # Hanya tampilkan yang takarannya lebih dari 0 gram
                    st.table(df_hasil[hasil.x > 0.01].reset_index(drop=True))
                    
                    st.success("Tabel di atas adalah kombinasi bahan termurah secara mutlak yang menjamin target Kalori, Protein, dan Lemak tetap terpenuhi.")
                else:
                    st.error("🚨 Matriks Infeasible: Garis kendala tidak menemukan titik temu. Target nutrisi terlalu tinggi untuk kombinasi makanan yang Anda centang.")
                    
            except Exception as e:
                st.error(f"Terjadi kesalahan komputasi matriks: {e}")

# --- HALAMAN 2: DOKUMENTASI & RUMUS ---
with tab_docs:
    st.write("### 📖 Penerapan Aljabar Linier pada Sistem")
    st.write("Sistem Persamaan Linier di dalam aplikasi ini dimodelkan dengan fungsi:")
    st.latex(r"\text{Fungsi Objektif (Minimasi Harga): } Z = \mathbf{C}^T \mathbf{X}")
    st.latex(r"\text{Sistem Matriks Kendala (Gizi): } \mathbf{A}\mathbf{X} \ge \mathbf{B}")
    
    st.write("Penjelasan Variabel:")
    st.markdown("""
    - $C$ : Vektor harga pasar dari makanan yang dipilih.
    - $X$ : Vektor penyelesaian (takaran makanan dalam ratusan gram) yang dicari.
    - $A$ : Matriks kandungan gizi (Kalori, Protein, Lemak).
    - $B$ : Vektor konstanta (Target minimal nutrisi pemerintah).
    """)
    st.info("Algoritma ini menggunakan **Metode Simpleks** untuk melakukan Operasi Baris Elementer (OBE) dan pertukaran *Basis Vektor* guna mencari titik di mana nilai harga ($Z$) adalah yang paling rendah.")