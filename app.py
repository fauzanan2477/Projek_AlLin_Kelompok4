import streamlit as st
import numpy as np
import pandas as pd

# --- 1. KONFIGURASI TAMPILAN WEB ---
st.set_page_config(page_title="Fauna-Matrix | SDG 15", layout="wide", page_icon="🐒")

st.markdown("""
    <style>
    .judul { font-size: 2.8rem; font-weight: 900; color: #1E4620; text-align: center; margin-bottom: 0px; }
    .subjudul { font-size: 1.2rem; color: #4A7C59; text-align: center; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="judul">🐒 Fauna-Matrix Predictor</p>', unsafe_allow_html=True)
st.markdown('<p class="subjudul">Pemodelan Populasi Satwa Langka (SDG 15) Menggunakan Matriks Leslie & Nilai Eigen</p>', unsafe_allow_html=True)

# --- 2. PANEL INPUT (SIDEBAR) ---
st.sidebar.header("⚙️ 1. Vektor Populasi Awal")
bayi = st.sidebar.number_input("Usia Bayi (0-1 Tahun):", value=100)
remaja = st.sidebar.number_input("Usia Remaja (1-3 Tahun):", value=50)
dewasa = st.sidebar.number_input("Usia Dewasa (>3 Tahun):", value=30)

st.sidebar.header("🧬 2. Parameter Matriks Leslie")
st.sidebar.write("Tingkat Kelahiran (Fekunditas):")
f1 = st.sidebar.slider("F1 (Bayi)", 0.0, 2.0, 0.0)
f2 = st.sidebar.slider("F2 (Remaja)", 0.0, 5.0, 1.2)
f3 = st.sidebar.slider("F3 (Dewasa)", 0.0, 5.0, 2.0)

st.sidebar.write("Tingkat Bertahan Hidup (Survival):")
s1 = st.sidebar.slider("S1 (Bayi ke Remaja)", 0.0, 1.0, 0.6)
s2 = st.sidebar.slider("S2 (Remaja ke Dewasa)", 0.0, 1.0, 0.8)

# --- 3. LOGIKA MATEMATIKA (ALJABAR LINIER) ---
# Membentuk Matriks Leslie (L) berordo 3x3
L = np.array([
    [f1, f2, f3],
    [s1, 0.0, 0.0],
    [0.0, s2, 0.0]
])

# Membentuk Vektor Populasi Awal (N0)
N0 = np.array([bayi, remaja, dewasa])

st.divider()
tahun_prediksi = st.slider("🎯 Proyeksi Pertumbuhan (Tahun ke depan):", 1, 50, 15)

# Perulangan Perkalian Matriks (Dot Product)
hasil = [N0]
N_curr = N0
for i in range(tahun_prediksi):
    # Rumus Alin: N_next = L * N_curr
    N_next = np.dot(L, N_curr) 
    hasil.append(N_next)
    N_curr = N_next

df = pd.DataFrame(hasil, columns=["Usia Bayi", "Usia Remaja", "Usia Dewasa"])
df.index.name = "Tahun"

# --- 4. TAMPILAN HASIL (DASHBOARD) ---
tab_grafik, tab_teori = st.tabs(["📊 DASHBOARD PROYEKSI", "🧮 BUKTI KOMPUTASI NILAI EIGEN"])

with tab_grafik:
    col_chart, col_data = st.columns([2, 1])
    
    with col_chart:
        st.write("### 📈 Grafik Laju Pertumbuhan Populasi")
        st.line_chart(df, color=["#FF4B4B", "#38ef7d", "#1E4620"])
        st.info("💡 **Analisis SDG 15:** Geser parameter di sebelah kiri. Jika tingkat bertahan hidup bayi sangat rendah, grafik akan menukik tajam menuju kepunahan.")
        
    with col_data:
        st.write("### 📋 Tabel Data (Ekor)")
        st.dataframe(df.astype(int), use_container_width=True)

with tab_teori:
    st.write("### Landasan Teori: Matriks dan Nilai Eigen")
    
    st.write("#### 1. Pembentukan Matriks Leslie ($L$)")
    st.write("Matriks dibentuk dari laju reproduksi (baris 1) dan laju kelangsungan hidup (sub-diagonal).")
    st.dataframe(pd.DataFrame(L).style.format("{:.2f}"))
    
    st.write("#### 2. Pencarian Nilai Eigen ($\lambda$)")
    st.write("Dalam Ilmu Lingkungan, kita tidak perlu mengalikan matriks ratusan kali untuk tahu apakah hewan akan punah. Kita cukup mencari **Nilai Eigen Terbesar** dari Matriks $L$.")
    
    # EKSEKUSI PENCARIAN NILAI EIGEN
    nilai_eigen, vektor_eigen = np.linalg.eig(L)
    eigen_dominan = max(np.real(nilai_eigen))
    
    st.success(f"Ditemukan Nilai Eigen Dominan ($\lambda$) = **{eigen_dominan:.4f}**")
    
    if eigen_dominan > 1:
        st.write("🟢 **Status:** $\lambda > 1$ (Populasi akan terus bertambah dan lestari).")
    elif eigen_dominan == 1:
        st.write("🟡 **Status:** $\lambda = 1$ (Populasi stagnan/stabil).")
    else:
        st.write("🔴 **Status:** $\lambda < 1$ (Spesies terancam punah! Perlu intervensi konservasi).")