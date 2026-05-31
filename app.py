import streamlit as st
import numpy as np
import pandas as pd

# --- KONFIGURASI WEB ---
st.set_page_config(page_title="Eco-Rank | SDG 15", layout="wide", page_icon="🐆")

st.markdown('<h1 style="color:#1E4620; text-align:center;">🐆 Eco-Rank: Spesies Kunci (Dinamis)</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#4A7C59;">Analisis Jaring Makanan Hutan via Matriks & Vektor Eigen</p>', unsafe_allow_html=True)

# --- 1. INPUT SPESIES DINAMIS (BEBAS CUSTOM) ---
st.write("### ⚙️ 1. Tentukan Ekosistem (Dinamis)")
st.info("Ketik nama-nama spesies yang ada di ekosistem hutanmu, pisahkan dengan tanda koma (,). Kamu bebas menambah/mengurangi spesies!")

# Input dinamis
input_spesies = st.text_input("Daftar Spesies Ekosistem:", "Pohon Buah, Serangga, Burung Kecil, Ular, Harimau")

# Membersihkan dan memisahkan teks menjadi List (Array)
spesies_list = [s.strip() for s in input_spesies.split(",") if s.strip() != ""]

# --- 2. EDITOR MATRIKS INTERAKTIF (SEPERTI EXCEL) ---
st.write("---")
st.write("### 🕸️ 2. Matriks Porsi Makan (0% - 100%)")
st.write("Isi tabel di bawah. **Baris** adalah Predator, **Kolom** adalah Mangsanya. Misalnya: Jika Harimau (Baris) memakan 100% Rusa (Kolom), isi dengan angka 100.")

# Membuat DataFrame kosong berukuran dinamis N x N
df_awal = pd.DataFrame(0.0, index=spesies_list, columns=spesies_list)

# Menampilkan Editor Tabel Excel di dalam Streamlit
df_matriks = st.data_editor(df_awal, use_container_width=True)

if st.button("Mulai Komputasi Nilai Eigen", type="primary"):
    
    # --- 3. LOGIKA MATEMATIKA (ALJABAR LINIER) ---
    # Mengambil nilai angka dari tabel
    A = df_matriks.values
    
    # Normalisasi (Membagi persentase dengan 100) dan Transpose Matriks
    # Transpose diperlukan karena energi mengalir dari Mangsa KE Predator
    A_transpose = (A / 100.0).T 
    
    # Mencegah matriks kosong (mengurangi error ekosistem tertutup)
    A_stabil = A_transpose + 0.01 
    
    # EKSEKUSI PENCARIAN NILAI & VEKTOR EIGEN
    nilai_eigen, vektor_eigen = np.linalg.eig(A_stabil)
    
    # Ambil Vektor Eigen yang bersesuaian dengan Nilai Eigen Terbesar
    idx_max = np.argmax(np.abs(nilai_eigen))
    eigen_terbesar = np.real(nilai_eigen[idx_max])
    vektor_sentralitas = np.abs(np.real(vektor_eigen[:, idx_max]))
    
    # Mengubah Vektor menjadi persentase skor (Total 100%)
    skor_akhir = (vektor_sentralitas / np.sum(vektor_sentralitas)) * 100
    
    # Memasukkan hasil ke dalam tabel baru
    df_ranking = pd.DataFrame({
        "Spesies": spesies_list,
        "Skor Kepentingan (%)": skor_akhir
    }).sort_values(by="Skor Kepentingan (%)", ascending=False).reset_index(drop=True)

    # --- 4. TAMPILAN DASHBOARD HASIL ---
    st.divider()
    tab_grafik, tab_teori = st.tabs(["📊 DASHBOARD PERINGKAT", "🧮 BUKTI MATRIKS & VEKTOR EIGEN"])
    
    with tab_grafik:
        col_chart, col_data = st.columns([2, 1])
        with col_chart:
            st.write("### 🏆 Peringkat Prioritas Konservasi")
            st.bar_chart(df_ranking.set_index("Spesies"))
            
        with col_data:
            spesies_kunci = df_ranking.iloc[0]["Spesies"]
            st.error(f"🚨 **SPESIES KUNCI: {spesies_kunci.upper()}**")
            st.write("Jika spesies di atas punah, keseimbangan matriks akan runtuh dan menghancurkan ekosistem hutan.")
            st.dataframe(df_ranking.style.format({"Skor Kepentingan (%)": "{:.2f}%"}), use_container_width=True)
            
    with tab_teori:
        st.write("### Landasan Teori (Aljabar Linier)")
        st.write("Aplikasi ini tidak merangking secara asal. Program mencari **Nilai Eigen Terbesar (Principal Eigenvalue)** dari matriks persentase makanan yang kamu isi.")
        
        st.success(f"Ditemukan Nilai Eigen Utama ($\lambda$) = **{eigen_terbesar:.4f}**")
        st.write("Vektor Eigen yang bersesuaian dengan $\lambda$ tersebut kemudian diekstrak. Nilai pada vektor itulah yang menjadi **Skor Kepentingan** pada grafik di halaman depan.")
        st.latex(r"A \mathbf{x} = \lambda \mathbf{x}")