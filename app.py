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

# --- HALAMAN 3: LANGKAH MANUAL (BARU) ---
with tab_manual:
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### ✍️ Urutan Perhitungan Manual Metode Simpleks (Sesuai Jurnal)")
    st.write("Bagaimana cara komputer atau manusia menemukan harga termurah di belakang layar? Berikut adalah langkah-langkah aljabarnya.")
    
    st.write("#### Langkah 1: Model Matematika (Sistem Persamaan Linier)")
    st.write("Menetapkan fungsi minimum dan fungsi kendala berdasarkan makanan yang dipilih.")
    st.latex(r"\text{Minimumkan: } Z = 1200x_1 + 2600x_2 + 1000x_3 + \dots")
    st.latex(r"\text{Kendala 1 (Kalori): } 130x_1 + 155x_2 + 193x_3 \ge 600")
    st.latex(r"\text{Kendala 2 (Protein): } 2.7x_1 + 13x_2 + 19x_3 \ge 25")
    
    st.write("#### Langkah 2: Bentuk Kanonik (Penambahan Slack/Surplus Variables)")
    st.write("Pertidaksamaan ($\ge$) tidak bisa dihitung dalam matriks. Maka ditambahkan variabel bayangan (S) untuk mengubahnya menjadi persamaan ($=$).")
    st.latex(r"130x_1 + 155x_2 + 193x_3 - S_1 = 600")
    st.latex(r"2.7x_1 + 13x_2 + 19x_3 - S_2 = 25")
    
    st.write("#### Langkah 3: Membangun Tabel Simpleks (Initial Tableau)")
    st.write("Memasukkan semua koefisien variabel ($x$ dan $S$) ke dalam format matriks M x N.")
    
    # Menampilkan contoh tabel simpleks menggunakan dataframe agar rapi
    df_tableau = pd.DataFrame({
        "Basis": ["S1", "S2", "Z"],
        "x1": ["130", "2.7", "-1200"],
        "x2": ["155", "13", "-2600"],
        "x3": ["193", "19", "-1000"],
        "S1": ["-1", "0", "0"],
        "S2": ["0", "-1", "0"],
        "Nilai Kanan (B)": ["600", "25", "0"]
    })
    st.table(df_tableau)
    
    st.write("#### Langkah 4: Iterasi Matriks (Operasi Baris Elementer)")
    st.write("1. **Menentukan Kolom Pivot:** Memilih kolom dengan nilai Z paling negatif.")
    st.write("2. **Menentukan Baris Pivot:** Membagi Nilai Kanan (B) dengan Kolom Pivot untuk mencari indeks terkecil (Variabel yang Keluar).")
    st.write("3. **Operasi Baris Elementer (OBE):** Mengubah elemen Pivot menjadi 1, dan elemen lain di kolom tersebut menjadi 0, persis seperti mencari Invers Matriks.")
    
    st.write("#### Langkah 5: Syarat Optimal")
    st.success("Iterasi OBE dilakukan berulang-ulang hingga **tidak ada lagi nilai negatif** pada baris $Z$. Saat itu terjadi, nilai di kolom paling kanan (B) pada baris Z adalah harga mutlak termurahnya!")
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