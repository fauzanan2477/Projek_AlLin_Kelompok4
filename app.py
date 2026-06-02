import streamlit as st
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.express as px

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Sistem Analisis Nutrisi PCA", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; max-width: 1100px; }
    .header-box { border-bottom: 4px solid #8e44ad; padding-bottom: 15px; margin-bottom: 25px; }
    .header-box h1 { font-size: 2.2rem; color: #8e44ad; margin: 0; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-box"><h1>🛒 Analisis Nutrisi PCA (Jurnal ALGORITMA 2026)</h1></div>', unsafe_allow_html=True)

# 2. DATABASE (Session State agar tidak reset)
if 'db_nutrisi' not in st.session_state:
    st.session_state['db_nutrisi'] = pd.DataFrame({
        "Nama Produk": ["Mie Instan", "Soda Cola", "Snack Kentang", "Susu UHT", "Yogurt"],
        "Kategori": ["Makanan Berat", "Minuman", "Cemilan", "Minuman", "Susu/Dairy"],
        "Kalori": [380, 140, 480, 150, 80],
        "Lemak": [14.0, 0.0, 28.0, 4.5, 1.5],
        "Karbo": [54.0, 39.0, 50.0, 22.0, 12.0],
        "Gula": [8.0, 39.0, 2.0, 18.0, 4.0],
        "Natrium": [1070, 45, 650, 90, 60]
    })

# 3. NAVIGASI
tab1, tab2, tab3 = st.tabs(["📊 Visualisasi PCA", "🗄️ Database", "📚 Teori"])

with tab1:
    st.write("### Pemetaan Karakteristik Nutrisi")
    
    if st.button("🚀 Jalankan PCA", type="primary"):
        df = st.session_state['db_nutrisi']
        
        # --- VALIDASI ALJABAR ---
        if len(df) < 2:
            st.error("⚠️ **Peringatan:** PCA membutuhkan minimal 2 jenis produk untuk dapat membandingkan data. Silakan tambah data di tab 'Database'.")
        else:
            fitur = df.select_dtypes(include=[np.number])
            
            # Standardisasi (Z-Score) agar perhitungan vektor eigen tidak bias
            matriks_skala = StandardScaler().fit_transform(fitur)
            
            # Eksekusi PCA (Reduksi ke 2 Dimensi)
            pca = PCA(n_components=2)
            pca_res = pca.fit_transform(matriks_skala)
            
            df_hasil = pd.DataFrame(pca_res, columns=["Vektor_X", "Vektor_Y"])
            df_hasil["Produk"] = df["Nama Produk"]
            
            st.success("✅ Matriks berhasil direduksi ke 2D menggunakan Vektor Eigen.")
            
            # Visualisasi
            fig = px.scatter(df_hasil, x="Vektor_X", y="Vektor_Y", text="Produk", size_max=15)
            fig.update_traces(textposition='top center', marker=dict(size=12, color='#8e44ad'))
            st.plotly_chart(fig, use_column_width=True)

with tab2:
    st.write("### Edit Data Nutrisi")
    tabel = st.data_editor(st.session_state['db_nutrisi'], num_rows="dynamic", use_container_width=True, key="tabel_nutrisi")
    st.session_state['db_nutrisi'] = tabel

with tab3:
    st.write("### Teori PCA & Vektor Eigen")
    st.write("Algoritma ini menggunakan **Vektor Eigen** dari matriks kovarian untuk memproyeksikan data nutrisi (Kalori, Lemak, Karbo, Gula, Natrium) ke ruang 2 dimensi.")
    st.latex(r"A \mathbf{v} = \lambda \mathbf{v}")
    st.write("Dimana $\lambda$ adalah Nilai Eigen dan $\mathbf{v}$ adalah Vektor Eigen.")