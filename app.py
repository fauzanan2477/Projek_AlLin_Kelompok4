import streamlit as st
import numpy as np
import pandas as pd

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="NutriMatrix | SDG 2", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    #MainMenu, header, footer {visibility: hidden;}
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    .stTabs [data-baseweb="tab-list"] { background-color: #1a1a1a; padding: 10px 20px; border-bottom: 1px solid #333; }
    .stTabs [data-baseweb="tab-list"] button { color: #B3B3B3; font-size: 1.05rem; font-weight: 600; text-transform: uppercase; border: none; }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] { color: #FFFFFF; border-bottom: 3px solid #E74C3C; }
    div[data-testid="metric-container"] { background-color: #242424; border: 1px solid #333; padding: 20px; border-radius: 8px; border-left: 4px solid #E74C3C; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HEADER ---
st.markdown("<h1 style='margin-bottom: -15px;'>Nutri<span style='color:#E74C3C;'>Matrix</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#B3B3B3; font-style: italic;'>Integrasi Makalah ITB (Matriks) & Modul STIKes (Gizi Medis)</p>", unsafe_allow_html=True)

# --- 3. DATABASE MAKANAN DINAMIS ---
if 'db_makanan' not in st.session_state:
    st.session_state.db_makanan = pd.DataFrame({
        "Nama Makanan (Per Porsi)": ["Dada Ayam Bakar", "Nasi Putih", "Alpukat", "Telur Rebus", "Tempe Goreng"],
        "Protein (g)": [25.0, 3.0, 1.0, 6.0, 10.0],
        "Karbohidrat (g)": [0.0, 40.0, 4.0, 1.0, 9.0],
        "Lemak (g)": [3.0, 0.0, 10.0, 5.0, 7.0]
    })

# --- 4. NAVIGASI TAB ---
tab_profil, tab_kalkulator, tab_db, tab_teori = st.tabs([
    "1. Profil Gizi (STIKes)", 
    "2. Matriks Porsi (ITB)", 
    "3. Database Makanan", 
    "4. Penjelasan Rumus"
])

# ==========================================
# TAB 1: PROFIL TUBUH (MENGHITUNG TARGET OTOMATIS)
# ==========================================
with tab_profil:
    st.write("### Identifikasi Kondisi Tubuh & Metabolisme")
    st.write("Sistem menghitung Total Kalori Harian (TDEE) Anda, kemudian membaginya menjadi target makronutrisi harian berdasarkan **Modul Tuntunan Gizi STIKes Persada Nabire** (Protein 15%, Karbohidrat 60%, Lemak 25%).")
    
    col1, col2, col3, col4 = st.columns(4)
    gender = col1.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
    umur = col2.number_input("Umur (Tahun)", value=20, min_value=10)
    berat = col3.number_input("Berat Badan (kg)", value=60.0, min_value=30.0)
    tinggi = col4.number_input("Tinggi Badan (cm)", value=165.0, min_value=100.0)
    
    aktivitas = st.selectbox("Tingkat Aktivitas Fisik", [
        "Sangat Jarang Olahraga (x1.2)", 
        "Jarang Olahraga (x1.375)", 
        "Cukup Sering Olahraga (x1.55)"
    ])
    
    # Logic BMR Harris-Benedict
    if gender == "Pria":
        bmr = 88.362 + (13.397 * berat) + (4.799 * tinggi) - (5.677 * umur)
    else:
        bmr = 447.593 + (9.247 * berat) + (3.098 * tinggi) - (4.330 * umur)
        
    # Logic TDEE
    if "Sangat Jarang" in aktivitas: multiplier = 1.2
    elif "Cukup Sering" in aktivitas: multiplier = 1.55
    else: multiplier = 1.375
    tdee = bmr * multiplier
    
    # Makro Nutrisi (Konversi berdasar Rujukan STIKes)
    st.session_state.target_p = (0.15 * tdee) / 4  # 1g protein = 4 kalori
    st.session_state.target_k = (0.60 * tdee) / 4  # 1g karbo = 4 kalori
    st.session_state.target_l = (0.25 * tdee) / 9  # 1g lemak = 9 kalori
    
    st.markdown("---")
    st.info(f"Target Energi Harian Anda: **{int(tdee)} Kalori/hari**. Berikut adalah konversi target ke dalam Vektor Gram:")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Target Protein Harian", f"{st.session_state.target_p:.0f} Gram")
    m2.metric("Target Karbo Harian", f"{st.session_state.target_k:.0f} Gram")
    m3.metric("Target Lemak Harian", f"{st.session_state.target_l:.0f} Gram")

# ==========================================
# TAB 2: OPTIMASI MATRIKS (ALJABAR LINIER)
# ==========================================
with tab_kalkulator:
    st.write("### Kalkulasi Porsi Menggunakan Invers Matriks")
    st.write("Sesuai dengan rujukan **Makalah IF2123 ITB**, permasalahan porsi makanan diselesaikan dengan metode SPL (Sistem Persamaan Linier). Pilih **3 jenis makanan** untuk membentuk matriks persegi.")
    
    daftar_menu = st.session_state.db_makanan["Nama Makanan (Per Porsi)"].tolist()
    pilihan = st.multiselect("Pilih Tepat 3 Menu Makanan:", daftar_menu, default=["Dada Ayam Bakar", "Nasi Putih", "Telur Rebus"], max_selections=3)
    
    if len(pilihan) == 3:
        df_pilih = st.session_state.db_makanan[st.session_state.db_makanan["Nama Makanan (Per Porsi)"].isin(pilihan)]
        
        matriks_A = np.array([
            df_pilih["Protein (g)"].values,
            df_pilih["Karbohidrat (g)"].values,
            df_pilih["Lemak (g)"].values
        ])
        
        vektor_B = np.array([st.session_state.target_p, st.session_state.target_k, st.session_state.target_l])
        
        try:
            invers_A = np.linalg.inv(matriks_A)
            vektor_X = np.dot(invers_A, vektor_B)
            
            st.markdown("<h4 style='color:#2ECC71;'>Hasil Porsi (Solusi SPL):</h4>", unsafe_allow_html=True)
            h1, h2, h3 = st.columns(3)
            h1.metric(df_pilih["Nama Makanan (Per Porsi)"].iloc[0], f"{vektor_X[0]:.1f} Porsi")
            h2.metric(df_pilih["Nama Makanan (Per Porsi)"].iloc[1], f"{vektor_X[1]:.1f} Porsi")
            h3.metric(df_pilih["Nama Makanan (Per Porsi)"].iloc[2], f"{vektor_X[2]:.1f} Porsi")
            
            # Memperbaiki error porsi negatif dari Jurnal ITB
            if any(p < 0 for p in vektor_X):
                st.warning("⚠️ Mengingat temuan dari Jurnal ITB, terdapat angka porsi negatif. Secara matematika benar, tapi tidak logis dimakan. Silakan ganti kombinasi makanan yang lain!")
        except np.linalg.LinAlgError:
            st.error("Matriks Singular! Gagal mencari invers.")
    else:
        st.write("Silakan pilih 3 makanan!")

# ==========================================
# TAB 3: DATABASE MAKANAN
# ==========================================
with tab_db:
    st.write("### Database Kandungan Bahan Pangan")
    st.write("Tambah baris makanan baru sesuka hati untuk melihat kecerdasan perhitungan matriks.")
    tabel_baru = st.data_editor(st.session_state.db_makanan, num_rows="dynamic", use_container_width=True, hide_index=True)
    st.session_state.db_makanan = tabel_baru

# ==========================================
# TAB 4: TEORI DOSEN
# ==========================================
with tab_teori:
    st.write("### Alur Logika Pemrograman (Bukti Matematis)")
    
    st.markdown("**1. Pembangkitan Vektor Target (B) via Rujukan STIKes**")
    st.write("Vektor B didapat secara dinamis dari rumus Kalori dikalikan rasio makronutrisi modul Gizi STIKes Persada Nabire (Karbo 60%, Protein 15%, Lemak 25%).")
    
    if len(pilihan) == 3:
        st.markdown("**2. Penyusunan SPL berdasarkan Makalah ITB**")
        st.latex(f"({matriks_A[0,0]})X_1 + ({matriks_A[0,1]})X_2 + ({matriks_A[0,2]})X_3 = {vektor_B[0]:.1f} \\text{{ (Protein)}}")
        st.latex(f"({matriks_A[1,0]})X_1 + ({matriks_A[1,1]})X_2 + ({matriks_A[1,2]})X_3 = {vektor_B[1]:.1f} \\text{{ (Karbohidrat)}}")
        st.latex(f"({matriks_A[2,0]})X_1 + ({matriks_A[2,1]})X_2 + ({matriks_A[2,2]})X_3 = {vektor_B[2]:.1f} \\text{{ (Lemak)}}")
        
        st.markdown("**3. Pemecahan Matriks $(X = A^{-1} \cdot B)$**")
        st.write("Komputer mencari Invers Matriks Kandungan Makanan $(A^{-1})$:")
        st.dataframe(pd.DataFrame(invers_A).style.format("{:.3f}"))
        st.success("Matriks Invers di atas kemudian dikalikan dengan Vektor B untuk mendapatkan rekomendasi porsi (X) secara instan!")