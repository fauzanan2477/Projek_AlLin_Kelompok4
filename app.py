import streamlit as st
import numpy as np
from PIL import Image
import io
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Forest-Vision | SVD", layout="wide", page_icon="🌍")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main-header { font-size: 3rem; font-weight: 900; color: #1E4620; text-align: center; margin-bottom: 0; }
    .sub-header { font-size: 1.2rem; color: #4A7C59; text-align: center; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER UTAMA ---
st.markdown('<p class="main-header">🌍 Forest Data-Lite</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Sistem Kompresi Citra via Dekomposisi Matriks (SDG 15)</p>', unsafe_allow_html=True)

# ==========================================
# MENU TAB ATAS
# ==========================================
tab_app, tab_teori = st.tabs(["🚀 WORKSPACE KOMPRESI", "📚 DASAR TEORI ALJABAR LINIER"])

# --- ISI TAB 1: APLIKASI UTAMA ---
with tab_app:
    with st.container(border=True):
        st.write("### ⚙️ Panel Input Data")
        col_input1, col_input2 = st.columns(2)
        
        with col_input1:
            mode_warna = st.selectbox("Pilih Mode Komputasi Matriks:", ["Grayscale (Matriks 2D)", "Berwarna (Tensor 3D RGB)"])
        with col_input2:
            uploaded_file = st.file_uploader("Unggah Citra Hutan (JPG/PNG)", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        st.write("---")
        with st.spinner('Mengekstrak Vektor Eigen & Menghitung SVD...'):
            time.sleep(1) 
            
            if mode_warna == "Grayscale (Matriks 2D)":
                image = Image.open(uploaded_file).convert('L')
                A = np.array(image)
                U, S, Vt = np.linalg.svd(A, full_matrices=False)
                max_k = len(S)
            else:
                image = Image.open(uploaded_file).convert('RGB')
                A = np.array(image)
                R, G, B = A[:,:,0], A[:,:,1], A[:,:,2]
                UR, SR, VtR = np.linalg.svd(R, full_matrices=False)
                UG, SG, VtG = np.linalg.svd(G, full_matrices=False)
                UB, SB, VtB = np.linalg.svd(B, full_matrices=False)
                max_k = len(SR)

        st.write("### 🎚️ Panel Kendali Matriks (Atur Resolusi)")
        k = st.slider("Jumlah Komponen Singular (k) yang dipertahankan:", min_value=1, max_value=max_k, value=max_k//5, step=1)
        
        if mode_warna == "Grayscale (Matriks 2D)":
            Ak = np.dot(U[:, :k], np.dot(np.diag(S[:k]), Vt[:k, :]))
            Ak = np.clip(Ak, 0, 255).astype(np.uint8)
            img_compressed = Image.fromarray(Ak)
            energy = (np.sum(S[:k]**2) / np.sum(S**2)) * 100
        else:
            Rk = np.dot(UR[:, :k], np.dot(np.diag(SR[:k]), VtR[:k, :]))
            Gk = np.dot(UG[:, :k], np.dot(np.diag(SG[:k]), VtG[:k, :]))
            Bk = np.dot(UB[:, :k], np.dot(np.diag(SB[:k]), VtB[:k, :]))
            Ak = np.stack((Rk, Gk, Bk), axis=2)
            Ak = np.clip(Ak, 0, 255).astype(np.uint8)
            img_compressed = Image.fromarray(Ak)
            energy = (np.sum(SR[:k]**2) / np.sum(SR**2)) * 100

        col_img1, col_img2 = st.columns(2)
        with col_img1:
            st.write(f"#### 🖼️ Citra Asli (Dimensi: {A.shape})")
            st.image(image, use_column_width=True)
            
        with col_img2:
            st.write(f"#### 🗜️ Hasil SVD (k = {k})")
            st.image(img_compressed, use_column_width=True)
            st.write(f"**Informasi Visual Dipertahankan: {energy:.2f}%**")
            st.progress(int(energy))

            buf = io.BytesIO()
            img_compressed.save(buf, format="PNG")
            st.download_button("📥 Unduh Citra Terkompresi", buf.getvalue(), f"svd_result_k{k}.png", "image/png", use_container_width=True, type="primary")

        st.write("---")
        with st.expander("🔍 Buka Inspeksi Detail Angka Matriks ($15 \\times 15$ Piksel Pertama)"):
            if mode_warna == "Grayscale (Matriks 2D)":
                tab_m1, tab_m2, tab_m3, tab_m4, tab_m5 = st.tabs(["Matriks A (Asli)", "Matriks U", "Matriks Σ", "Matriks V^T", "Matriks Ak (Hasil)"])
                with tab_m1: st.dataframe(A[:15, :15], use_container_width=True)
                with tab_m2: st.dataframe(U[:15, :15], use_container_width=True)
                with tab_m3: st.dataframe(np.diag(S[:15]), use_container_width=True)
                with tab_m4: st.dataframe(Vt[:15, :15], use_container_width=True)
                with tab_m5: st.dataframe(Ak[:15, :15], use_container_width=True)
            else:
                st.warning("Inspeksi angka hanya didukung pada mode Matriks 2D (Grayscale).")
    else:
        st.info("👈 Silakan unggah gambar pada panel di atas untuk memulai simulasi.")

# ==========================================
# ISI TAB 2: DASAR TEORI (FULL ALJABAR LINIER)
# ==========================================
with tab_teori:
    st.write("### 📖 Landasan Matematika di Balik Aplikasi")
    st.write("Aplikasi ini dibangun menggunakan integrasi dari **5 pilar utama** materi Aljabar Linier:")
    
    with st.expander("1. Matriks (Representasi Digital)", expanded=True):
        st.write("Dalam ilmu komputer, citra/gambar tidak disimpan sebagai foto, melainkan direpresentasikan sebagai **Matriks 2 Dimensi** (untuk Grayscale) atau **Tensor 3 Dimensi** (untuk RGB). Setiap elemen matriks berisi angka intensitas piksel (0 - 255).")
        
    with st.expander("2. Dekomposisi SVD (Singular Value Decomposition)"):
        st.write("SVD adalah algoritma yang memecah (memfaktorkan) matriks citra $A$ berukuran $m \\times n$ menjadi perkalian tiga matriks terpisah:")
        st.latex(r"A = U \cdot \Sigma \cdot V^T")
        
    with st.expander("3. Nilai Eigen & Vektor Eigen (Akar dari SVD)"):
        st.write("Meskipun yang dipanggil adalah fungsi SVD, metode ini secara matematis diturunkan murni dari konsep Eigen:")
        st.markdown("""
        - Matriks $U$ berisi **Vektor Eigen** dari hasil perkalian $AA^T$.
        - Matriks $V^T$ berisi **Vektor Eigen** dari hasil perkalian $A^TA$.
        - Nilai-nilai di dalam matriks $\Sigma$ pada dasarnya adalah akar kuadrat dari **Nilai Eigen** tersebut.
        """)
        
    with st.expander("4. Diagonalisasi & Matriks Diagonal"):
        st.write("Matriks $\Sigma$ (Sigma) hasil dari SVD adalah sebuah **Matriks Diagonal**. Semua elemen pada matriks tersebut bernilai nol, *kecuali* pada garis diagonal utamanya yang berisikan Nilai Singular. Pada aplikasi ini, kita memotong dimensi matriks diagonal ini (menggunakan *slider*) untuk membuang nilai yang kecil.")
        
    with st.expander("5. Operasi Perkalian Matriks (Dot Product)"):
        st.write("Untuk menampilkan gambar yang sudah dikompresi ke layar, program mengeksekusi operasi **Perkalian Matriks** ($U_k \cdot \Sigma_k \cdot V^T_k$). Proses ini merekonstruksi kembali matriks-matriks yang sudah dipotong menjadi satu matriks gambar $A_k$ yang utuh dengan ukuran file yang jauh lebih efisien.")