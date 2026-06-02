import streamlit as st
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.express as px

# 1. KONFIGURASI HALAMAN DASHBOARD
st.set_page_config(page_title="Sistem Analisis Nutrisi PCA", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; max-width: 1100px; }
    .header-box { border-bottom: 4px solid #8e44ad; padding-bottom: 15px; margin-bottom: 25px; }
    .header-box h1 { font-size: 2.2rem; color: #8e44ad; margin: 0; font-weight: 800; }
    .header-box p { font-size: 1.1rem; color: #555; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# 2. HEADER
st.markdown("""
<div class="header-box">
    <h1>🛒 Pemetaan Data Nutrisi Makanan Kemasan (PCA)</h1>
    <p>Reduksi Dimensi Aljabar Linier (Nilai & Vektor Eigen) | Ref: Jurnal ALGORITMA (2026)</p>
</div>
""", unsafe_allow_html=True)

# 3. DATABASE DUMMY MAKANAN KEMASAN (MATRIKS MULTIDIMENSI)
if 'db_nutrisi' not in st.session_state:
    st.session_state['db_nutrisi'] = pd.DataFrame({
        "Nama Produk": ["Mie Goreng Instan", "Minuman Soda Cola", "Snack Keripik Kentang", "Susu Cokelat UHT", "Yogurt Plain", "Teh Manis Kemasan", "Kacang Panggang"],
        "Kategori": ["Makanan Berat", "Minuman", "Cemilan", "Minuman", "Susu/Dairy", "Minuman", "Cemilan"],
        "Kalori (kkal)": [380, 140, 480, 150, 80, 120, 520],
        "Lemak (g)": [14.0, 0.0, 28.0, 4.5, 1.5, 0.0, 42.0],
        "Karbohidrat (g)": [54.0, 39.0, 50.0, 22.0, 12.0, 31.0, 18.0],
        "Gula (g)": [8.0, 39.0, 2.0, 18.0, 4.0, 31.0, 3.0],
        "Natrium/Garam (mg)": [1070, 45, 650, 90, 60, 20, 200]
    })

# 4. TABS NAVIGASI
tab1, tab2, tab3 = st.tabs(["📊 Visualisasi PCA (Pemetaan Produk)", "🗄️ Database Matriks (Data Mentah)", "📚 Teori Vektor Eigen"])

# ==========================================
# TAB 1: VISUALISASI PCA (OUTPUT VISUAL UTAMA)
# ==========================================
with tab1:
    st.write("### 🧮 Analisis Reduksi Dimensi")
    st.write("Data nutrisi memiliki 5 variabel (Kalori, Lemak, Karbo, Gula, Natrium). Manusia tidak bisa menggambar grafik 5 Dimensi. Tekan tombol di bawah untuk menggunakan **Vektor Eigen (PCA)** demi memampatkan data tersebut menjadi 2 Dimensi (Sumbu X dan Y).")
    
    if st.button("🚀 Eksekusi Aljabar Linier (Jalankan PCA)", type="primary"):
        df = st.session_state['db_nutrisi']
        
        # 1. Memisahkan Label dan Matriks Numerik
        fitur_nutrisi = df[["Kalori (kkal)", "Lemak (g)", "Karbohidrat (g)", "Gula (g)", "Natrium/Garam (mg)"]]
        
        # 2. Standardisasi Matriks (Agar skala Garam(mg) dan Lemak(g) setara di mata Aljabar)
        scaler = StandardScaler()
        matriks_skala = scaler.fit_transform(fitur_nutrisi)
        
        # 3. PROSES INTI: Ekstraksi Vektor Eigen (PCA)
        pca = PCA(n_components=2)
        matriks_pca = pca.fit_transform(matriks_skala)
        varians_tersimpan = pca.explained_variance_ratio_.sum() * 100
        
        # 4. Memasukkan hasil ke DataFrame untuk divisualisasikan
        df_hasil = pd.DataFrame(matriks_pca, columns=["Komponen Utama 1 (Vektor X)", "Komponen Utama 2 (Vektor Y)"])
        df_hasil["Nama Produk"] = df["Nama Produk"]
        df_hasil["Kategori"] = df["Kategori"]
        
        st.write("---")
        st.success(f"✅ Matriks berhasil direduksi! Meskipun dimensi dikompresi dari 5D ke 2D, kita masih mempertahankan **{varians_tersimpan:.2f}%** karakteristik asli data makanan.")
        
        # 5. OUTPUT VISUAL: Scatter Plot Interaktif menggunakan Plotly
        st.write("### 🗺️ Peta Kedekatan Karakteristik Makanan")
        st.caption("Titik yang saling berdekatan menunjukkan bahwa makanan tersebut memiliki profil gizi yang serupa secara aljabar.")
        
        fig = px.scatter(
            df_hasil, 
            x="Komponen Utama 1 (Vektor X)", 
            y="Komponen Utama 2 (Vektor Y)", 
            color="Kategori", 
            text="Nama Produk",
            size_max=15
        )
        fig.update_traces(textposition='top center', marker=dict(size=12))
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 2: DATABASE DATA MENTAH
# ==========================================
with tab2:
    st.write("### 📋 Matriks Data Nutrisi Multidimensi")
    st.info("Ini adalah wujud matriks asli sebelum direduksi. Anda dapat menambahkan produk baru di baris terbawah untuk melihat posisinya di grafik PCA.")
    
    tabel_diedit = st.data_editor(
        st.session_state['db_nutrisi'], 
        num_rows="dynamic", 
        use_container_width=True
    )
    st.session_state['db_nutrisi'] = tabel_diedit

# ==========================================
# TAB 3: DOKUMENTASI MATEMATIKA
# ==========================================
with tab3:
    st.write("### 📑 Mengapa PCA Membutuhkan Nilai Eigen & Vektor Eigen?")
    st.write("""
    Sesuai dengan jurnal **ALGORITMA (2026)**, Principal Component Analysis (PCA) tidak mungkin bisa bekerja tanpa ilmu Aljabar Linier tingkat lanjut.
    
    1. **Matriks Kovarian:** Komputer pertama-tama mengubah data nutrisi menjadi Matriks Kovarian (mengukur bagaimana Lemak bergerak bersama Kalori, dsb).
    2. **Pencarian Arah Utama (Vektor Eigen):** Sistem mencari **Vektor Eigen** dari matriks kovarian tersebut. Vektor Eigen bertindak sebagai "Sumbu/Garis Kemiringan" yang menangkap pergerakan data paling ekstrem.
    3. **Pembobotan (Nilai Eigen):** **Nilai Eigen** menunjukkan seberapa besar informasi (varians) yang dikandung oleh masing-masing Vektor Eigen.
    4. **Proyeksi SVD:** Data nutrisi awal kemudian dikalikan (dot product) dengan Vektor Eigen terkuat untuk membentuk titik-titik baru (Komponen Utama) yang bisa Anda lihat pada grafik di Tab 1.
    """)