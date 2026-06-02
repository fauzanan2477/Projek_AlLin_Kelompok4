import streamlit as st
import pandas as pd
import numpy as np

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Sistem Perencanaan Energi", layout="wide")

# 2. INJEKSI CSS UNTUK TAMPILAN HTML KLASIK
st.markdown("""
    <style>
    /* Mengatur kontainer agar mirip halaman web biasa */
    .block-container { 
        padding-top: 1.5rem; 
        max-width: 1000px; /* Lebar dibatasi agar rapi seperti container HTML */
    }
    
    /* Format Judul */
    .app-header {
        border-bottom: 2px solid #333;
        padding-bottom: 10px;
        margin-bottom: 20px;
        font-family: Arial, sans-serif;
    }
    .app-header h1 {
        font-size: 26px;
        color: #222;
        margin: 0;
    }
    .app-header p {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
    }
    
    /* Mengubah desain Tab menjadi Navbar Sederhana */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        border-bottom: 1px solid #ccc;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        padding: 8px 16px;
        font-family: Arial, sans-serif;
        font-weight: 600;
        color: #444;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #0056b3;
        color: #0056b3;
    }
    </style>
""", unsafe_allow_html=True)

# 3. HEADER WEBSITE
st.markdown("""
<div class="app-header">
    <h1>Sistem Perencanaan Pembangkit Energi (Matriks SPL)</h1>
    <p>Aplikasi implementasi Aljabar Linier untuk tata kota berkelanjutan (SDG 7).</p>
</div>
""", unsafe_allow_html=True)

# 4. INISIALISASI DATA MATRIKS
if 'db_energi' not in st.session_state:
    st.session_state['db_energi'] = pd.DataFrame({
        "Jenis Pembangkit (Variabel)": ["PLTS (Surya - x1)", "PLTB (Angin - x2)", "PLTA (Air - x3)"],
        "Koefisien Energi (MW)": [1.0, 1.0, 1.0],
        "Biaya Pembangunan (Miliar)": [10.0, 15.0, 20.0],
        "Reduksi Emisi (Ton)": [5.0, 8.0, 12.0]
    })

# 5. NAVBAR MENU (Pindah Halaman)
halaman1, halaman2, halaman3 = st.tabs(["Beranda Target", "Kalkulator Matriks", "Dokumentasi"])

# --- HALAMAN 1: BERANDA / TARGET ---
with halaman1:
    st.write("### Penentuan Konstanta (Vektor B)")
    st.write("Silakan tentukan target yang harus dicapai oleh sistem komputasi:")
    
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1: target_energi = st.number_input("Target Total Energi (MW)", value=100.0)
    with col_t2: target_biaya = st.number_input("Batas Anggaran (Miliar Rupiah)", value=1400.0)
    with col_t3: target_karbon = st.number_input("Target Pengurangan Karbon (Ton)", value=760.0)
    
    st.info("Nilai di atas akan digunakan sebagai Vektor Konstanta (B) dalam operasi Aljabar Linier.")

# --- HALAMAN 2: KALKULATOR MATRIKS ---
with halaman2:
    st.write("### Tabel Parameter Pembangkit (Matriks A)")
    st.write("Sistem mendeteksi 3 jenis infrastruktur. Nilai koefisien dapat diedit langsung pada tabel di bawah ini.")
    
    # Tabel interaktif dengan key agar stabil
    tabel_matriks = st.data_editor(
        st.session_state['db_energi'], 
        use_container_width=True,
        hide_index=True,
        key="tabel_parameter"
    )
    st.session_state['db_energi'] = tabel_matriks
    
    st.write("---")
    
    if st.button("Proses Operasi Eliminasi Gauss-Jordan", type="primary"):
        # Menyusun array Matriks
        A_raw = tabel_matriks[["Koefisien Energi (MW)", "Biaya Pembangunan (Miliar)", "Reduksi Emisi (Ton)"]].values.T
        B = np.array([target_energi, target_biaya, target_karbon])
        nama_pembangkit = tabel_matriks["Jenis Pembangkit (Variabel)"].tolist()
        
        jumlah_variabel = len(nama_pembangkit)
        
        # Validasi Komputasi
        st.write("#### Output Resolusi Sistem (Vektor X)")
        if jumlah_variabel == 3:
            try:
                X = np.linalg.solve(A_raw, B)
                
                res_c1, res_c2, res_c3 = st.columns(3)
                res_c1.metric(label=f"{nama_pembangkit[0]}", value=f"{X[0]:.1f} MW")
                res_c2.metric(label=f"{nama_pembangkit[1]}", value=f"{X[1]:.1f} MW")
                res_c3.metric(label=f"{nama_pembangkit[2]}", value=f"{X[2]:.1f} MW")
                
                st.success("Komputasi Selesai. Hasil matriks tunggal (solusi eksak) berhasil ditemukan.")
            except np.linalg.LinAlgError:
                st.error("Sistem Gagal: Matriks bersifat singular. Tidak ada titik potong yang valid untuk parameter tersebut.")
        else:
            st.error("Kesalahan Dimensi: Operasi eliminasi murni membutuhkan bentuk matriks persegi (3x3). Silakan kembalikan baris tabel menjadi 3 jenis pembangkit.")

# --- HALAMAN 3: DOKUMENTASI ---
with halaman3:
    st.write("### Dokumentasi Logika Sistem")
    st.write("""
    **Arsitektur Komputasi:**
    - Perangkat lunak ini mengubah data input tabel (Frontend) menjadi struktur Array dua dimensi (Backend) menggunakan pustaka `NumPy`.
    - Persamaan yang terbentuk:
      1. Persamaan Kapasitas: $x_1 + x_2 + x_3 = Target\_Energi$
      2. Persamaan Finansial: $c_1x_1 + c_2x_2 + c_3x_3 = Batas\_Anggaran$
      3. Persamaan Lingkungan: $e_1x_1 + e_2x_2 + e_3x_3 = Target\_Karbon$
    - Sistem akan mengeksekusi fungsi `numpy.linalg.solve` untuk mengembalikan matriks Invers yang memecahkan Vektor $X$ (kapasitas pembangkit).
    """)