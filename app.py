import streamlit as st
import numpy as np
import pandas as pd

# --- 1. KONFIGURASI TAMPILAN WEB ---
st.set_page_config(page_title="Platform Mitigasi Karhutla", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 600; }
    div[data-testid="metric-container"] {
        background-color: rgba(144, 153, 163, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #d9534f;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. MANAJEMEN BASIS DATA (SIKLUS 1 TAHUN) ---
if 'basis_data' not in st.session_state:
    st.session_state.basis_data = pd.DataFrame({
        "Bulan": ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Ags", "Sep", "Okt", "Nov", "Des"],
        "Suhu Udara (°C)": [31.0, 31.5, 32.0, 32.5, 33.5, 34.5, 35.5, 36.5, 36.0, 34.0, 32.5, 31.5],
        "Curah Hujan (mm)": [250, 220, 180, 150, 100, 60, 30, 10, 20, 80, 160, 230],
        "Luas Terbakar (Hektar)": [20, 35, 80, 150, 400, 900, 2100, 4500, 3800, 1200, 300, 50]
    })

tabel_historis = st.session_state.basis_data

# --- 3. MESIN KOMPUTASI ALJABAR LINIER ---
def hitung_regresi_matriks(tabel_data):
    try:
        # 1. Menyiapkan Vektor Target (Y) dan Matriks Fitur (X)
        vektor_luas_terbakar = tabel_data["Luas Terbakar (Hektar)"].values
        
        # Menambahkan angka 1 di kolom pertama matriks sebagai intersep/konstanta persamaan
        matriks_variabel_bebas = np.column_stack((
            np.ones(len(tabel_data)), 
            tabel_data["Suhu Udara (°C)"], 
            tabel_data["Curah Hujan (mm)"]
        ))
        
        # 2. Operasi Pemecahan Sistem Persamaan Linier (Normal Equation)
        matriks_transpose = matriks_variabel_bebas.T
        perkalian_matriks = np.dot(matriks_transpose, matriks_variabel_bebas)
        matriks_invers = np.linalg.inv(perkalian_matriks)
        
        perkalian_vektor = np.dot(matriks_transpose, vektor_luas_terbakar)
        
        # Hasil Akhir: Vektor Koefisien
        vektor_koefisien_regresi = np.dot(matriks_invers, perkalian_vektor)
        
        return vektor_koefisien_regresi, matriks_invers, True
    except Exception:
        return None, None, False

# Mengeksekusi fungsi matematika
koefisien_model, matriks_invers_model, status_kalkulasi = hitung_regresi_matriks(tabel_historis)

# --- 4. NAVIGASI SIDEBAR ---
with st.sidebar:
    st.title("Mitigasi SDG 15")
    st.write("Analisis Risiko Karhutla Tahunan")
    st.markdown("---")
    menu = st.radio(
        "Menu Navigasi",
        ["Ringkasan Eksekutif", "Manajemen Dataset (1 Tahun)", "Simulasi Prediktif", "Spesifikasi Pemodelan Matriks"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("Implementasi Aljabar Linier & SPL")

# --- 5. ANTARMUKA HALAMAN ---

if menu == "Ringkasan Eksekutif":
    st.title("Ringkasan Eksekutif Tahunan")
    st.write("Pemantauan siklus iklim selama 12 bulan terakhir dan dampaknya terhadap ekosistem hutan.")
    
    col1, col2, col3 = st.columns(3)
    suhu_puncak = tabel_historis["Suhu Udara (°C)"].max()
    total_lahan_rusak = tabel_historis["Luas Terbakar (Hektar)"].sum()
    bulan_terparah = tabel_historis.loc[tabel_historis["Luas Terbakar (Hektar)"].idxmax(), "Bulan"]
    
    col1.metric("Suhu Puncak Tahunan", f"{suhu_puncak:.1f} °C")
    col2.metric("Total Lahan Terdampak", f"{total_lahan_rusak:,.0f} Ha")
    col3.metric("Bulan Paling Kritis", f"{bulan_terparah}", delta="Kemarau Ekstrem", delta_color="inverse")
    
    st.markdown("### Kurva Luas Lahan Terbakar (Siklus 1 Tahun)")
    st.area_chart(tabel_historis.set_index("Bulan")["Luas Terbakar (Hektar)"], color="#d9534f")


elif menu == "Manajemen Dataset (1 Tahun)":
    st.title("Manajemen Dataset Pemantauan")
    st.write("Tabel di bawah ini memuat data pemantauan selama 12 bulan penuh. Perubahan pada angka di tabel akan langsung diproses ulang oleh sistem Aljabar Linier pada latar belakang (*backend*).")
    
    # Tinggi diatur agar muat 12 bulan tanpa memakan terlalu banyak ruang
    tabel_yang_diedit = st.data_editor(tabel_historis, height=450, use_container_width=True)
    st.session_state.basis_data = tabel_yang_diedit


elif menu == "Simulasi Prediktif":
    st.title("Simulasi Prediktif Kondisi Iklim")
    st.write("Masukkan estimasi suhu dan curah hujan untuk memprediksi potensi perluasan area terbakar.")
    
    if not status_kalkulasi:
        st.error("Kalkulasi dihentikan. Matriks Singular terdeteksi pada dataset historis.")
    else:
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.markdown("**Parameter Lingkungan:**")
            estimasi_suhu = st.number_input("Suhu Udara Harian (°C)", min_value=25.0, max_value=45.0, value=37.5, step=0.5)
            estimasi_hujan = st.number_input("Curah Hujan Bulanan (mm)", min_value=0.0, max_value=400.0, value=15.0, step=5.0)
            
        with c2:
            st.markdown("**Hasil Proyeksi Luas Lahan:**")
            
            # Perkalian Vektor (Input) dengan Vektor (Koefisien)
            vektor_kondisi_baru = np.array([1, estimasi_suhu, estimasi_hujan])
            perhitungan_prediksi = np.dot(vektor_kondisi_baru, koefisien_model)
            luas_lahan_final = max(0, perhitungan_prediksi)
            
            st.metric(label="Estimasi Kerusakan Ekosistem", value=f"{luas_lahan_final:,.0f} Hektar")
            
            st.write("Indeks Status Ekologi (SDG 15):")
            if luas_lahan_final > 3000:
                st.progress(1.0)
                st.error("Status: Kritis (Dibutuhkan Intervensi Pemadaman Udara Nasional)")
            elif luas_lahan_final > 1000:
                st.progress(0.5)
                st.warning("Status: Siaga (Peningkatan Patroli Hutan)")
            else:
                st.progress(0.1)
                st.success("Status: Terkendali (Kondisi Hutan Aman)")


elif menu == "Spesifikasi Pemodelan Matriks":
    st.title("Spesifikasi Operasi Aljabar Linier")
    st.write("Dokumentasi teknis pemecahan Sistem Persamaan Linier (SPL) yang bertugas sebagai *engine* prediksi pada aplikasi ini.")
    
    if not status_kalkulasi:
        st.warning("Data matriks gagal diproses (Determinan = 0).")
    else:
        st.markdown("#### 1. Persamaan Regresi yang Dihasilkan")
        st.latex(r"Y = \beta_0 + \beta_1 (\text{Suhu}) + \beta_2 (\text{Hujan})")
        
        st.markdown("#### 2. Matriks Invers $(X^T X)^{-1}$")
        st.write("Matriks invers ini adalah penentu utama keberhasilan sistem menyelesaikan persamaan kompleks dari data 12 bulan.")
        tabel_invers = pd.DataFrame(matriks_invers_model)
        st.dataframe(tabel_invers.style.format("{:.7f}"))
        
        st.markdown("#### 3. Vektor Koefisien ($\beta$)")
        tabel_koefisien = pd.DataFrame(
            koefisien_model, 
            index=["Intersep (Konstanta)", "Koefisien Suhu Udara", "Koefisien Curah Hujan"], 
            columns=["Nilai Bobot"]
        )
        st.dataframe(tabel_koefisien.style.format("{:.4f}"))