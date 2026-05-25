import streamlit as st
import numpy as np
from PIL import Image
import io
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Forest-Vision | SVD Compressor", layout="wide", page_icon="🌍")

# --- CUSTOM CSS (Biar lebih mirip website modern) ---
st.markdown("""
    <style>
    .main-header { font-size: 3rem; font-weight: bold; color: #1E4620; margin-bottom: 0px; }
    .sub-header { font-size: 1.2rem; color: #4A7C59; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- MENU NAVIGASI SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2855/2855562.png", width=80)
    st.title("🌍 Navigasi Web")
    menu = st.radio("Pergi ke halaman:", ["🚀 Workspace Kompresi", "📚 Baca Teori SVD"])
    st.divider()
    st.caption("Dibuat untuk memenuhi Projek Aljabar Linier & SDG 15.")

# ==========================================
# HALAMAN 1: WORKSPACE KOMPRESI (INTERAKTIF)
# ==========================================
if menu == "🚀 Workspace Kompresi":
    # Hero Section
    st.markdown('<p class="main-header">SVD Image Compressor</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Mendukung SDG 15: Optimasi Transmisi Data Pemantauan Hutan via Aljabar Linier</p>', unsafe_allow_html=True)
    
    st.info("💡 **Petunjuk:** Unggah gambar pada kotak di bawah, lalu atur *slider* untuk melihat proses dekomposisi matriks secara *real-time*.")

    # Container Utama (Kotak Unggah)
    with st.container(border=True):
        col_input1, col_input2 = st.columns([1, 2])
        
        with col_input1:
            st.write("### ⚙️ Pengaturan")
            mode_warna = st.selectbox("Mode Dimensi Matriks:", ["Grayscale (Matriks 2D)", "Berwarna (Tensor 3D RGB)"])
            uploaded_file = st.file_uploader("Unggah Citra (JPG/PNG)", type=["jpg", "png", "jpeg"])
        
        with col_input2:
            if uploaded_file is None:
                st.write("<br><br><br>", unsafe_allow_html=True)
                st.warning("Menunggu unggahan citra satelit/hutan...")
    
    # --- LOGIKA SVD & TAMPILAN HASIL ---
    if uploaded_file is not None:
        st.divider()
        
        # Animasi Loading Interaktif
        with st.spinner('Mengekstrak Nilai Eigen dan memproses Singular Value Decomposition...'):
            time.sleep(1) # Efek delay buatan agar terasa seperti memproses data berat
            
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

        st.toast('Proses Dekomposisi Matriks Selesai! 🎉', icon='✅')

        # --- SLIDER INTERAKTIF (FULL WIDTH) ---
        st.write("### 🎚️ Panel Kendali Matriks")
        k = st.slider("Atur Jumlah Komponen Singular (k) yang dipertahankan:", min_value=1, max_value=max_k, value=max_k//5, step=1)
        
        # Rekonstruksi & Kalkulasi Berdasarkan Nilai Slider
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

        # --- TAMPILAN PERBANDINGAN GAMBAR (KIRI - KANAN) ---
        col_img1, col_img2 = st.columns(2)
        
        with col_img1:
            st.write(f"#### 🖼️ Citra Asli (k = {max_k})")
            st.image(image, use_column_width=True)
            st.caption(f"Dimensi Awal: {A.shape} piksel")
            
        with col_img2:
            st.write(f"#### 🗜️ Hasil Rekonstruksi (k = {k})")
            st.image(img_compressed, use_column_width=True)
            
            # Progress bar untuk energi
            st.write(f"**Informasi Visual Dipertahankan: {energy:.2f}%**")
            st.progress(int(energy))

            # Tombol Download
            buf = io.BytesIO()
            img_compressed.save(buf, format="PNG")
            st.download_button(
                label="📥 Unduh Citra Terkompresi",
                data=buf.getvalue(),
                file_name=f"svd_result_k{k}.png",
                mime="image/png",
                use_container_width=True,
                type="primary"
            )

        # --- MENU AKORDION: TABEL MATRIKS (BISA DI-SCROLL) ---
        st.write("---")
        with st.expander("🔍 Klik untuk Inspeksi Detail Angka Matriks (Aljabar Linier)"):
            if mode_warna == "Grayscale (Matriks 2D)":
                st.write("Menampilkan cuplikan $15 \\times 15$ piksel kiri atas dari operasi dekomposisi matriks.")
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["Matriks A (Asli)", "Matriks U", "Matriks Σ", "Matriks V^T", "Matriks Ak (Hasil)"])
                
                # Menggunakan st.dataframe agar tabelnya interaktif dan bisa di-scroll mandiri
                with tab1: st.dataframe(A[:15, :15], use_container_width=True)
                with tab2: st.dataframe(U[:15, :15], use_container_width=True)
                with tab3: st.dataframe(np.diag(S[:15]), use_container_width=True)
                with tab4: st.dataframe(Vt[:15, :15], use_container_width=True)
                with tab5: st.dataframe(Ak[:15, :15], use_container_width=True)
            else:
                st.warning("Tabel matriks dinonaktifkan untuk mode RGB karena data berbentuk Tensor 3 Dimensi.")

# ==========================================
# HALAMAN 2: DASAR TEORI
# ==========================================
elif menu == "📚 Baca Teori SVD":
    st.markdown('<p class="main-header">Dasar Teori Aljabar Linier</p>', unsafe_allow_html=True)
    st.write("Pelajari matematika di balik layar aplikasi ini.")
    
    with st.container(border=True):
        st.write("### 1. Singular Value Decomposition (SVD)")
        st.write("Metode SVD memfaktorkan matriks citra $A$ berukuran $m \\times n$ menjadi perkalian tiga matriks:")
        st.latex(r"A = U \cdot \Sigma \cdot V^T")
        
        st.write("""
        - **Matriks U:** Berisi Vektor Eigen dari hasil perkalian matriks $A A^T$.
        - **Matriks $\Sigma$ (Sigma):** Matriks diagonal yang berisi Nilai Singular (Akar kuadrat dari Nilai Eigen).
        - **Matriks $V^T$:** Berisi Vektor Eigen dari hasil perkalian matriks $A^T A$.
        """)
        
    with st.container(border=True):
        st.write("### 2. Bagaimana Kompresi Terjadi?")
        st.write("""
        Alih-alih menggunakan seluruh nilai singular di matriks $\Sigma$, kita hanya mengambil sejumlah **$k$ nilai terbesar** (Truncated SVD). 
        Nilai singular terbesar menyimpan pola informasi paling penting dari gambar, sedangkan nilai terkecil biasanya hanya merepresentasikan *noise* (bintik/detail tidak penting).
        Dengan membuang nilai singular yang kecil, kita menghemat memori (*storage*) secara drastis!
        """)