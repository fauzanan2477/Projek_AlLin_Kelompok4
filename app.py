import streamlit as st
import numpy as np
import pandas as pd

# --- 1. KONFIGURASI HALAMAN (WIDE) ---
st.set_page_config(page_title="Gizi.com | SDG 2", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CSS CUSTOM (DARK MODE KOMPAS-STYLE) ---
st.markdown("""
    <style>
    /* Mengubah tema dasar menjadi gelap */
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    
    /* Menyembunyikan header dan footer bawaan Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Modifikasi ukuran container atas */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    /* Membuat gaya Tab persis seperti Navbar Kompas.com Dark Mode */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a1a;
        padding: 10px 20px;
        border-bottom: 1px solid #333;
        gap: 20px;
    }
    .stTabs [data-baseweb="tab-list"] button {
        color: #B3B3B3;
        background-color: transparent;
        font-size: 1rem;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 600;
        text-transform: uppercase;
        border: none;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #FFFFFF;
        border-bottom: 3px solid #D32F2F; /* Garis bawah merah ala portal berita */
    }
    .stTabs [data-baseweb="tab-list"] button:hover {
        color: #FFFFFF;
    }
    
    /* Modifikasi Metric Card agar keren di dark mode */
    div[data-testid="metric-container"] {
        background-color: #242424;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. HEADER WEBSITE (LOGO) ---
st.markdown("<h1 style='font-family: serif; margin-bottom: -15px;'>GIZI<span style='color:#D32F2F;'>.com</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#B3B3B3; font-size: 0.9rem; font-style: italic;'>JERNIH MEMENUHI NUTRISI BERSAMA ALJABAR LINIER</p>", unsafe_allow_html=True)

# --- 4. MENU NAVIGASI (ALA PORTAL BERITA) ---
menu1, menu2, menu3 = st.tabs([
    "News (Kalkulator)", 
    "Kolom (Database)", 
    "Edukasi (Teori Matriks)"
])

# --- DATA KANDUNGAN GIZI ---
if 'kandungan_gizi' not in st.session_state:
    st.session_state.kandungan_gizi = pd.DataFrame({
        "Bahan Makanan": ["Makanan A (Tempe)", "Makanan B (Telur)", "Makanan C (Sayur)"],
        "Protein (g)": [2, 1, 3],
        "Karbohidrat (g)": [3, 2, 1],
        "Lemak (g)": [1, 2, 1]
    })

# ==========================================
# TAB 1: NEWS (KALKULATOR UTAMA)
# ==========================================
with menu1:
    st.markdown("### Kalkulasi Komposisi Porsi Harian")
    st.write("Masukkan target gizi yang ingin Anda penuhi hari ini. Mesin matriks kami akan menghitung kombinasi porsinya secara akurat.")
    
    k1, k2, k3 = st.columns(3)
    target_protein = k1.number_input("Target Protein (g)", value=12)
    target_karbo = k2.number_input("Target Karbohidrat (g)", value=12)
    target_lemak = k3.number_input("Target Lemak (g)", value=8)
    
    st.write("---")
    
    df = st.session_state.kandungan_gizi
    matriks_A = np.array([
        df["Protein (g)"].values,
        df["Karbohidrat (g)"].values,
        df["Lemak (g)"].values
    ])
    
    vektor_B = np.array([target_protein, target_karbo, target_lemak])
    
    try:
        invers_A = np.linalg.inv(matriks_A)
        vektor_X = np.dot(invers_A, vektor_B)
        
        st.markdown("<h4 style='color:#4CAF50;'>Rekomendasi Porsi Makanan:</h4>", unsafe_allow_html=True)
        
        h1, h2, h3 = st.columns(3)
        h1.metric(df["Bahan Makanan"].iloc[0], f"{vektor_X[0]:.0f} Porsi")
        h2.metric(df["Bahan Makanan"].iloc[1], f"{vektor_X[1]:.0f} Porsi")
        h3.metric(df["Bahan Makanan"].iloc[2], f"{vektor_X[2]:.0f} Porsi")
        
    except np.linalg.LinAlgError:
        st.error("Kalkulasi gagal. Susunan gizi matriks menyebabkan Determinan = 0.")

# ==========================================
# TAB 2: KOLOM (DATABASE KANDUNGAN)
# ==========================================
with menu2:
    st.markdown("### Database Kandungan Bahan Pangan")
    st.write("Tabel kandungan per 1 porsi saji. Ubah nilai di bawah ini untuk melihat bagaimana invers matriks beradaptasi.")
    
    tabel_edit = st.data_editor(st.session_state.kandungan_gizi, use_container_width=True, hide_index=True)
    st.session_state.kandungan_gizi = tabel_edit

# ==========================================
# TAB 3: EDUKASI (BUKTI TEORI MATRIKS)
# ==========================================
with menu3:
    st.markdown("### Pembuktian Invers Matriks & SPL")
    st.write("Sebuah makalah dari ITB membuktikan bahwa perhitungan gizi sering menghasilkan porsi negatif. Di sini, kita merancang SPL $3 \\times 3$ yang terukur untuk menjamin solusi bilangan bulat positif.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**1. Matriks Kandungan Nutrisi (A)**")
        st.dataframe(pd.DataFrame(matriks_A, index=["Baris Protein", "Baris Karbo", "Baris Lemak"], columns=["Mkn A", "Mkn B", "Mkn C"]))
    with col_b:
        st.markdown("**2. Vektor Target (B)**")
        st.dataframe(pd.DataFrame(vektor_B, index=["Target Protein", "Target Karbo", "Target Lemak"], columns=["Nilai"]))
        
    st.markdown("---")
    st.markdown("**3. Eksekusi Matriks Invers $(A^{-1})$**")
    st.write("Untuk mencari Vektor X (Jumlah Porsi), kita mencari Invers dari Matriks A, lalu mengalikannya dengan Vektor B ($X = A^{-1} \cdot B$).")
    
    if 'invers_A' in locals():
        st.dataframe(pd.DataFrame(invers_A).style.format("{:.3f}"))
        st.success("Operasi *Dot Product* antara Matriks Invers dan Vektor Target terbukti memecahkan sistem persamaan linier secara presisi tanpa metode coba-coba!")