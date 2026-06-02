import streamlit as st
import pandas as pd
import numpy as np

# 1. KONFIGURASI HALAMAN UTAMA (Harus di baris pertama)
st.set_page_config(page_title="NutriCalc Pro - SPL", layout="wide", initial_sidebar_state="collapsed")

# 2. INJEKSI CUSTOM HTML & CSS (Menghilangkan ciri khas Streamlit)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Mengubah font keseluruhan dan background */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f4f7f6;
    }
    
    /* Menyembunyikan elemen bawaan Streamlit (Header, Menu, Footer) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Desain Navbar (Header Atas) */
    .web-navbar {
        background: linear-gradient(135deg, #0b486b 0%, #f56217 100%);
        padding: 20px 30px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
    }
    .web-navbar h1 { margin: 0; font-size: 28px; font-weight: 700; color: white; }
    .web-navbar span { font-size: 14px; opacity: 0.9; }

    /* Desain Kartu (Kontainer Putih) */
    .web-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #eaeaea;
        margin-bottom: 20px;
    }
    
    /* Desain Judul Bagian */
    .section-title {
        color: #2c3e50;
        font-weight: 700;
        font-size: 18px;
        border-bottom: 3px solid #f56217;
        padding-bottom: 8px;
        margin-bottom: 20px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# 3. NAVigasi & HEADER HTML
st.markdown("""
<div class="web-navbar">
    <div>
        <h1>NutriCalc Pro 🥗</h1>
        <span>Sistem Pakar Gizi Berbasis Aljabar Linier (SDGs 3)</span>
    </div>
    <div style="text-align: right;">
        <span>Referensi: Makalah ITB 2024</span><br>
        <strong>Metode: Sistem Persamaan Linier</strong>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. INISIALISASI DATABASE SEMENTARA (Sesuai Angka Asli Jurnal)
if 'db_makanan' not in st.session_state:
    st.session_state['db_makanan'] = pd.DataFrame({
        "Bahan Makanan": ["Nasi Putih", "Ayam Broiler", "Telur Ayam", "Susu", "Kangkung"],
        "Energi": [1.30, 2.39, 1.43, 0.42, 0.18],
        "Protein": [0.027, 0.27, 0.13, 0.034, 0.026],
        "Lemak": [0.003, 0.13, 0.10, 0.01, 0.002],
        "Karbohidrat": [0.28, 0.0, 0.007, 0.05, 0.031],
        "Serat": [0.004, 0.0, 0.0, 0.0, 0.021]
    })

# 5. LAYOUT HALAMAN (Grid Kiri dan Kanan)
col_kiri, col_kanan = st.columns([7, 3])

with col_kiri:
    st.markdown('<div class="web-card"><div class="section-title">Database Nutrisi Makanan</div>', unsafe_allow_html=True)
    st.caption("✨ **Interaktif:** Anda dapat mengganti angka langsung di dalam tabel, klik tombol **[+]** di bagian paling bawah tabel untuk menambah makanan baru, atau menekan *Delete* di keyboard untuk menghapus baris makanan.")
    
    # Tabel interaktif (Bisa ditambah, diedit, dihapus)
    tabel_diedit = st.data_editor(
        st.session_state['db_makanan'],
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True
    )
    st.session_state['db_makanan'] = tabel_diedit
    st.markdown('</div>', unsafe_allow_html=True)

with col_kanan:
    st.markdown('<div class="web-card"><div class="section-title">Target Gizi (B)</div>', unsafe_allow_html=True)
    st.caption("Skenario: Anak 7-9 Tahun (Skala 1:100)")
    
    t_energi = st.number_input("Energi (kkal)", value=16.50, step=1.0)
    t_protein = st.number_input("Protein (g)", value=0.40, step=0.1)
    t_lemak = st.number_input("Lemak (g)", value=0.55, step=0.1)
    t_karbo = st.number_input("Karbohidrat (g)", value=2.50, step=0.1)
    t_serat = st.number_input("Serat (g)", value=0.23, step=0.1)
    st.markdown('</div>', unsafe_allow_html=True)

# 6. BAGIAN KALKULASI ALJABAR
st.markdown('<div class="web-card"><div class="section-title">Hasil Analisis Pemrograman Linier</div>', unsafe_allow_html=True)

if st.button("🚀 Hitung Porsi Makanan (Proses Matriks)", type="primary", use_container_width=True):
    # Mengekstrak Matriks A dari tabel (Di-transpose agar Makanan = Variabel x)
    A_raw = tabel_diedit[["Energi", "Protein", "Lemak", "Karbohidrat", "Serat"]].values.T
    B = np.array([t_energi, t_protein, t_lemak, t_karbo, t_serat])
    nama_makanan = tabel_diedit["Bahan Makanan"].tolist()
    
    jumlah_persamaan = 5
    jumlah_variabel = len(nama_makanan)
    
    st.write("---")
    
    if jumlah_variabel == 5:
        # Jika matriks 5x5 (Syarat SPL murni terpenuhi)
        try:
            X = np.linalg.solve(A_raw, B)
            st.success("✅ Matriks Persegi 5x5 berhasil dihitung menggunakan Eliminasi Gauss-Jordan.")
            
            # Menampilkan hasil
            kolom_hasil = st.columns(5)
            for i in range(5):
                kolom_hasil[i].metric(label=f"Porsi {nama_makanan[i]}", value=f"{X[i]:.3f}")
                
            # Validasi Negatif (Sesuai jurnal)
            if any(porsi < 0 for porsi in X):
                st.error("⚠️ **Analisis Evaluasi Jurnal:** Perhatikan bahwa terdapat porsi bernilai negatif. Hal ini membuktikan kesimpulan Makalah ITB, bahwa SPL murni tidak memiliki *constraint* realitas fisik (batas nol), sehingga tidak bisa langsung diterapkan di lapangan.")
                
        except np.linalg.LinAlgError:
            st.error("🚨 Matriks Singular! Sistem tidak memiliki invers (solusi).")
            
    else:
        # Jika makanan diubah (Misal ditambah jadi 6, atau dihapus jadi 4)
        st.warning(f"⚠️ Sistem mendeteksi **{jumlah_variabel} variabel makanan** untuk **5 persamaan**. Matriks bukan lagi matriks persegi ($5 \\times 5$). Sistem secara cerdas beralih ke metode **Kuadrat Terkecil (Least Squares)**.")
        try:
            X, residuals, rank, s = np.linalg.lstsq(A_raw, B, rcond=None)
            
            # Menampilkan hasil secara dinamis sesuai jumlah makanan
            kolom_hasil = st.columns(jumlah_variabel)
            for i in range(jumlah_variabel):
                kolom_hasil[i].metric(label=f"Porsi {nama_makanan[i]}", value=f"{X[i]:.3f}")
                
        except Exception as e:
            st.error(f"Gagal menghitung matriks non-persegi: {e}")

st.markdown('</div>', unsafe_allow_html=True)