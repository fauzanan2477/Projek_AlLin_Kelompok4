import streamlit as st
import pandas as pd
import numpy as np

# 1. KONFIGURASI HALAMAN (Mode WIDE agar full menyesuaikan layar)
st.set_page_config(page_title="Dashboard Gizi & SPL", layout="wide", initial_sidebar_state="collapsed")

# 2. INJEKSI CSS CUSTOM (Memaksa Latar Belakang Putih & Bersih)
st.markdown("""
    <style>
    /* Memaksa background seluruh aplikasi menjadi putih bersih */
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    /* Mengatur padding dan lebar kontainer utama */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important; /* Membuatnya responsif memenuhi layar */
    }
    
    /* Tipografi yang bersih dan elegan (Hitam/Abu-abu gelap) */
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #1E1E1E !important;
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }
    
    /* Header Custom */
    .header-box {
        border-bottom: 3px solid #2E86C1;
        padding-bottom: 15px;
        margin-bottom: 25px;
    }
    .header-box h1 {
        font-weight: 800;
        font-size: 2.2rem;
        margin: 0;
        color: #2E86C1 !important;
    }
    .header-box p {
        font-size: 1rem;
        color: #555555 !important;
        margin-top: 5px;
    }
    
    /* Kustomisasi Tab agar menyatu dengan background putih */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #E0E0E0;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #2E86C1;
        color: #2E86C1 !important;
    }
    
    /* Kustomisasi Data Editor/Tabel */
    [data-testid="stDataFrame"] {
        background-color: #FAFAFA;
        border: 1px solid #EEEEEE;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. HEADER
st.markdown("""
<div class="header-box">
    <h1>🥗 Sistem Komputasi Gizi Seimbang (Aljabar Linier)</h1>
    <p>Mendukung SDGs 3: Kesehatan yang Baik dan Kesejahteraan | Ref: Makalah ITB (2024) & Jurnal Univ. Aisyah (2022)</p>
</div>
""", unsafe_allow_html=True)

# 4. DATABASE SEMENTARA (Matriks 5x5 sesuai Jurnal Utama)
if 'db_gizi' not in st.session_state:
    st.session_state['db_gizi'] = pd.DataFrame({
        "Bahan Makanan": ["Nasi Putih", "Ayam Broiler", "Telur Ayam", "Susu", "Kangkung"],
        "Energi": [1.30, 2.39, 1.43, 0.42, 0.18],
        "Protein": [0.027, 0.27, 0.13, 0.034, 0.026],
        "Lemak": [0.003, 0.13, 0.10, 0.01, 0.002],
        "Karbohidrat": [0.28, 0.0, 0.007, 0.05, 0.031],
        "Serat": [0.004, 0.0, 0.0, 0.0, 0.021]
    })

# 5. TAB NAVBAR
tab1, tab2 = st.tabs(["🧮 Kalkulator Matriks SPL (Interaktif)", "📚 Resume & Metodologi"])

# --- ISI TAB 1: KALKULATOR ---
with tab1:
    # Membagi layout responsif menggunakan column (Kiri untuk Tabel, Kanan untuk Target)
    col_tabel, col_target = st.columns([6, 2])
    
    with col_tabel:
        st.write("### 📝 Tabel Matriks Kandungan Gizi (A)")
        st.caption("Data interaktif: Anda bebas mengubah angka, menambah baris makanan baru, atau menghapus baris.")
        
        tabel_diedit = st.data_editor(
            st.session_state['db_gizi'],
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True
        )
        st.session_state['db_gizi'] = tabel_diedit
        
    with col_target:
        st.write("### 🎯 Target AKE Harian (B)")
        st.caption("Skenario: Anak 7-9 Tahun (Skala 1:100)")
        t_energi = st.number_input("Energi", value=16.50, step=1.0)
        t_protein = st.number_input("Protein", value=0.40, step=0.1)
        t_lemak = st.number_input("Lemak", value=0.55, step=0.1)
        t_karbo = st.number_input("Karbo", value=2.50, step=0.1)
        t_serat = st.number_input("Serat", value=0.23, step=0.1)

    st.write("---")
    
    # EKSEKUSI PERHITUNGAN
    if st.button("🚀 Kalkulasi Eliminasi Gauss-Jordan", type="primary", use_container_width=True):
        st.write("### 📊 Hasil Komputasi Vektor Porsi (X)")
        
        A_raw = tabel_diedit[["Energi", "Protein", "Lemak", "Karbohidrat", "Serat"]].values.T
        B = np.array([t_energi, t_protein, t_lemak, t_karbo, t_serat])
        nama_makanan = tabel_diedit["Bahan Makanan"].tolist()
        jumlah_variabel = len(nama_makanan)
        
        if jumlah_variabel == 5:
            try:
                X = np.linalg.solve(A_raw, B)
                
                # Menampilkan hasil berdampingan secara responsif
                kolom_hasil = st.columns(5)
                for i in range(5):
                    kolom_hasil[i].metric(label=f"{nama_makanan[i]}", value=f"{X[i]:.3f} Porsi")
                    
                # Validasi Kelemahan Jurnal
                st.write("")
                if any(porsi < 0 for porsi in X):
                    st.error("""
                    **⚠️ PERINGATAN VALIDASI (Sesuai Kesimpulan Makalah ITB):** Sistem mendeteksi adanya porsi makanan bernilai **NEGATIF**. Hal ini menunjukkan kelemahan fatal SPL murni jika diterapkan di dunia nyata, di mana porsi makanan fisik tidak mungkin berada di bawah nol. SPL membutuhkan penambahan *constraint logic* (Program Linier).
                    """)
                else:
                    st.success("✅ Matriks diselesaikan dan porsi bernilai logis.")
            except np.linalg.LinAlgError:
                st.error("🚨 Matriks Singular! Sistem persamaan ini tidak memiliki solusi pasti.")
        else:
            st.warning(f"Sistem beralih ke metode **Kuadrat Terkecil (Least Squares)** karena matriks tidak berbentuk persegi ($5 \\times {jumlah_variabel}$).")
            try:
                X, _, _, _ = np.linalg.lstsq(A_raw, B, rcond=None)
                kolom_hasil = st.columns(jumlah_variabel)
                for i in range(jumlah_variabel):
                    kolom_hasil[i].metric(label=f"{nama_makanan[i]}", value=f"{X[i]:.3f} Porsi")
            except Exception as e:
                st.error(f"Error perhitungan matriks dinamis: {e}")

# --- ISI TAB 2: METODOLOGI ---
with tab2:
    st.write("### Landasan Matematika dan Teori Gizi")
    st.write("""
    - **Teori Gizi:** Berdasarkan Jurnal *ABDI KE UNGU* (2022), IMT yang sehat memerlukan asupan kalori dan nutrisi makro yang sangat presisi sesuai pilar Gizi Seimbang.
    - **Model SPL:** Berdasarkan Makalah ITB (2024), penghitungan gizi direpresentasikan sebagai $AX = B$.
    - **Pembuktian Evaluasi:** Aplikasi ini membuktikan secara *real-time* bahwa perkalian invers matriks pada $AX = B$ kerap kali memberikan *output* angka negatif pada vektor $X$ yang melanggar hukum realitas alam.
    """)