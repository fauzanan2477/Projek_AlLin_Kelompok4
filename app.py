import streamlit as st
import numpy as np
import pandas as pd

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Gizi.com | SDG 2", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CSS CUSTOM (TEMA DARK MODE PORTAL BERITA) ---
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #FFFFFF; }
    #MainMenu, header, footer {visibility: hidden;}
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    
    /* Gaya Tab Navigasi ala Portal Berita */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a1a; padding: 10px 20px; border-bottom: 1px solid #333; gap: 20px;
    }
    .stTabs [data-baseweb="tab-list"] button {
        color: #B3B3B3; background-color: transparent; font-size: 1.05rem; 
        font-family: 'Segoe UI', Arial, sans-serif; font-weight: 600; text-transform: uppercase; border: none;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #FFFFFF; border-bottom: 3px solid #D32F2F; /* Garis bawah merah */
    }
    /* Modifikasi Metric Card */
    div[data-testid="metric-container"] {
        background-color: #242424; border: 1px solid #333; padding: 20px; border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. HEADER WEBSITE ---
st.markdown("<h1 style='font-family: serif; margin-bottom: -15px;'>GIZI<span style='color:#D32F2F;'>.com</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#B3B3B3; font-size: 0.9rem; font-style: italic;'>JERNIH MEMENUHI NUTRISI BERSAMA ALJABAR LINIER</p>", unsafe_allow_html=True)

# --- 4. PENYIMPANAN DATABASE DINAMIS ---
# Data awal, pengguna bisa menambah baris baru di menu Kolom (Database)
if 'database_makanan' not in st.session_state:
    st.session_state.database_makanan = pd.DataFrame({
        "Nama Menu": ["Tempe Goreng", "Telur Rebus", "Sayur Bayam", "Dada Ayam", "Nasi Putih", "Tahu Kukus"],
        "Protein (g)": [2, 1, 3, 5, 1, 2],
        "Karbohidrat (g)": [3, 2, 1, 0, 8, 2],
        "Lemak (g)": [1, 2, 1, 1, 0, 1]
    })

# --- 5. MENU NAVIGASI ---
tab_kalkulator, tab_database, tab_edukasi = st.tabs([
    "Kalkulator Gizi", 
    "Kolom (Database Makanan)", 
    "Edukasi (Teori Matriks)"
])

# ==========================================
# TAB 1: KALKULATOR GIZI (INTERAKTIF)
# ==========================================
with tab_kalkulator:
    st.markdown("### Optimasi Porsi Makanan Harian")
    st.write("Tentukan target gizi harian Anda, lalu pilih **tepat 3 jenis menu** dari database. Sistem akan menghitung porsi ideal menggunakan Invers Matriks.")
    
    # Input Target Gizi
    kolom_target1, kolom_target2, kolom_target3 = st.columns(3)
    target_protein = kolom_target1.number_input("Target Protein (g)", value=12, min_value=1)
    target_karbo = kolom_target2.number_input("Target Karbohidrat (g)", value=12, min_value=1)
    target_lemak = kolom_target3.number_input("Target Lemak (g)", value=8, min_value=1)
    
    st.markdown("---")
    
    # Pilihan Menu Dinamis dari Database
    daftar_menu_tersedia = st.session_state.database_makanan["Nama Menu"].tolist()
    
    pilihan_menu = st.multiselect(
        "Pilih Komposisi Makanan (Wajib 3 Menu):", 
        options=daftar_menu_tersedia, 
        default=daftar_menu_tersedia[:3], # Default pilih 3 teratas
        max_selections=3
    )
    
    if len(pilihan_menu) == 3:
        # Mengambil data dari menu yang dipilih
        df_dipilih = st.session_state.database_makanan[st.session_state.database_makanan["Nama Menu"].isin(pilihan_menu)]
        
        # 1. Membentuk Matriks Kandungan (3x3)
        matriks_kandungan_gizi = np.array([
            df_dipilih["Protein (g)"].values,
            df_dipilih["Karbohidrat (g)"].values,
            df_dipilih["Lemak (g)"].values
        ])
        
        # 2. Membentuk Vektor Target
        vektor_target_gizi = np.array([target_protein, target_karbo, target_lemak])
        
        # 3. Eksekusi Invers Matriks
        try:
            invers_matriks_kandungan = np.linalg.inv(matriks_kandungan_gizi)
            vektor_hasil_porsi = np.dot(invers_matriks_kandungan, vektor_target_gizi)
            
            st.markdown("<h4 style='color:#4CAF50;'>Rekomendasi Porsi Konsumsi:</h4>", unsafe_allow_html=True)
            
            hasil1, hasil2, hasil3 = st.columns(3)
            hasil1.metric(df_dipilih["Nama Menu"].iloc[0], f"{vektor_hasil_porsi[0]:.1f} Porsi")
            hasil2.metric(df_dipilih["Nama Menu"].iloc[1], f"{vektor_hasil_porsi[1]:.1f} Porsi")
            hasil3.metric(df_dipilih["Nama Menu"].iloc[2], f"{vektor_hasil_porsi[2]:.1f} Porsi")
            
            # Peringatan Logika Porsi Negatif (Kaitan dengan Makalah ITB)
            if any(p < 0 for p in vektor_hasil_porsi):
                st.warning("⚠️ **Perhatian:** Terdapat angka porsi negatif. Secara matematis benar, namun tidak logis untuk dimakan. Silakan ganti kombinasi menu lain!")
                
        except np.linalg.LinAlgError:
            st.error("🚨 Kalkulasi gagal. Matriks dari kombinasi makanan ini bernilai Singular (Determinan = 0). Tidak bisa di-invers.")
    else:
        st.info("Silakan pilih tepat 3 menu agar sistem dapat membentuk Matriks Persegi 3x3.")

# ==========================================
# TAB 2: DATABASE MAKANAN (BISA DITAMBAH)
# ==========================================
with tab_database:
    st.markdown("### Database Kandungan Bahan Pangan")
    st.info("💡 **Fitur Dinamis:** Anda bisa mengetik langsung di tabel ini, mengubah angka, atau menekan tombol **(+) di bawah tabel** untuk menambahkan makanan baru sesuka hati!")
    
    # num_rows="dynamic" memungkinkan user menambah/menghapus baris
    tabel_interaktif = st.data_editor(
        st.session_state.database_makanan, 
        use_container_width=True, 
        hide_index=True,
        num_rows="dynamic" 
    )
    st.session_state.database_makanan = tabel_interaktif

# ==========================================
# TAB 3: EDUKASI TEORI MATRIKS
# ==========================================
with tab_edukasi:
    st.markdown("### Spesifikasi Komputasi Aljabar Linier")
    st.write("Visualisasi pembentukan Sistem Persamaan Linier (SPL) dari kombinasi menu yang dipilih di halaman Kalkulator.")
    
    if len(pilihan_menu) == 3:
        col_matriks, col_vektor = st.columns(2)
        with col_matriks:
            st.markdown("**1. Matriks Kandungan Nutrisi (A)**")
            st.dataframe(pd.DataFrame(
                matriks_kandungan_gizi, 
                index=["Baris Protein", "Baris Karbo", "Baris Lemak"], 
                columns=pilihan_menu
            ))
        with col_vektor:
            st.markdown("**2. Vektor Target Gizi (B)**")
            st.dataframe(pd.DataFrame(vektor_target_gizi, index=["Target Protein", "Target Karbo", "Target Lemak"], columns=["Nilai Target"]))
            
        st.markdown("---")
        st.markdown("**3. Eksekusi Matriks Invers $(A^{-1})$**")
        st.write("Pencarian nilai variabel Porsi (X) diselesaikan dengan rumus matriks: $X = A^{-1} \cdot B$. Berikut adalah hasil perhitungan invers matriks:")
        
        if 'invers_matriks_kandungan' in locals():
            st.dataframe(pd.DataFrame(invers_matriks_kandungan).style.format("{:.3f}"))
            st.success("Telah dieksekusi operasi Perkalian Vektor (Dot Product) antara Matriks Invers dan Vektor Target Gizi untuk menghasilkan porsi yang akurat.")
    else:
        st.write("Silakan pilih 3 menu di halaman kalkulator untuk melihat perhitungan matriksnya.")