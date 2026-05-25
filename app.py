import streamlit as st
import numpy as np
from PIL import Image
import io

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Forest Data-Lite | SVD", layout="wide", page_icon="🌲")

# --- MENU INTERAKTIF SIDEBAR ---
st.sidebar.title("🌲 Menu Navigasi")
menu = st.sidebar.radio("Pilih Halaman:", ["💻 Simulasi SVD", "📖 Dasar Teori Alin"])

if menu == "💻 Simulasi SVD":
    st.title("Aplikasi Kompresi Citra (SVD)")
    st.write("Mendukung SDG 15: Efisiensi Transmisi Data Pemantauan Hutan")
    
    # Menu Pilihan Mode
    st.sidebar.header("Pengaturan Matriks")
    mode_warna = st.sidebar.selectbox("Pilih Mode Dimensi Matriks:", ["2D (Hitam Putih / Grayscale)", "3D (Berwarna / RGB)"])
    
    uploaded_file = st.sidebar.file_uploader("Unggah Citra (JPG/PNG)", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        # Buka gambar sesuai mode yang dipilih
        if mode_warna == "2D (Hitam Putih / Grayscale)":
            image = Image.open(uploaded_file).convert('L')
            A = np.array(image)
            
            # SVD Proses
            U, S, Vt = np.linalg.svd(A, full_matrices=False)
            max_k = len(S)
            
            k = st.slider("Geser Nilai Singular (k):", 1, max_k, max_k // 5)
            
            # Rekonstruksi Matriks
            Ak = np.dot(U[:, :k], np.dot(np.diag(S[:k]), Vt[:k, :]))
            Ak = np.clip(Ak, 0, 255).astype(np.uint8)
            img_compressed = Image.fromarray(Ak)
            
            # Hitung Energi untuk metrik
            energy = (np.sum(S[:k]**2) / np.sum(S**2)) * 100

        else:
            # MODE RGB (Lebih Canggih)
            image = Image.open(uploaded_file).convert('RGB')
            A = np.array(image)
            
            # Memecah matriks 3D menjadi 3 matriks 2D (Red, Green, Blue)
            R, G, B = A[:,:,0], A[:,:,1], A[:,:,2]
            
            # SVD untuk masing-masing channel
            UR, SR, VtR = np.linalg.svd(R, full_matrices=False)
            UG, SG, VtG = np.linalg.svd(G, full_matrices=False)
            UB, SB, VtB = np.linalg.svd(B, full_matrices=False)
            
            max_k = len(SR)
            k = st.slider("Geser Nilai Singular (k) untuk Matriks RGB:", 1, max_k, max_k // 5)
            
            # Rekonstruksi per channel
            Rk = np.dot(UR[:, :k], np.dot(np.diag(SR[:k]), VtR[:k, :]))
            Gk = np.dot(UG[:, :k], np.dot(np.diag(SG[:k]), VtG[:k, :]))
            Bk = np.dot(UB[:, :k], np.dot(np.diag(SB[:k]), VtB[:k, :]))
            
            # Menggabungkan kembali (Stacking Matriks)
            Ak = np.stack((Rk, Gk, Bk), axis=2)
            Ak = np.clip(Ak, 0, 255).astype(np.uint8)
            img_compressed = Image.fromarray(Ak)
            
            # Rata-rata energi untuk RGB
            energy = (np.sum(SR[:k]**2) / np.sum(SR**2)) * 100

        # --- TAMPILAN GAMBAR ---
        col1, col2 = st.columns(2)
        with col1:
            st.write("### 🖼️ Citra Matriks Asli")
            st.image(image, use_column_width=True)
            st.caption(f"Dimensi Matriks: {A.shape}")
            
        with col2:
            st.write(f"### 🗜️ Citra Rekonstruksi (k = {k})")
            st.image(img_compressed, use_column_width=True)
            
            # Metrik Interaktif
            st.metric(label="Informasi Visual yang Dipertahankan", value=f"{energy:.2f} %")
            
            # --- TOMBOL DOWNLOAD ---
            buf = io.BytesIO()
            img_compressed.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="📥 Unduh Gambar Hasil Kompresi",
                data=byte_im,
                file_name=f"svd_kompresi_k{k}.png",
                mime="image/png",
                use_container_width=True
            )

        # --- TABEL MATRIKS ---
        st.divider()
        st.write("### 🧮 Detail Inspeksi Matriks ($15 \\times 15$ Piksel Pertama)")
        if mode_warna == "2D (Hitam Putih / Grayscale)":
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Matriks A", "Matriks U", "Matriks Σ", "Matriks V^T", "Matriks Ak"])
            with tab1: st.dataframe(A[:15, :15])
            with tab2: st.dataframe(U[:15, :15])
            with tab3: st.dataframe(np.diag(S[:15]))
            with tab4: st.dataframe(Vt[:15, :15])
            with tab5: st.dataframe(Ak[:15, :15])
        else:
            st.info("Inspeksi matriks tabel hanya tersedia untuk mode 2D (Grayscale) karena bentuk data RGB merupakan tensor 3 Dimensi.")
            
    else:
        st.info("👈 Silakan unggah gambar di menu samping untuk memulai simulasi.")

elif menu == "📖 Dasar Teori Alin":
    st.title("📖 Dasar Teori Singular Value Decomposition (SVD)")
    st.write("Metode **SVD** memfaktorkan matriks citra $A$ berukuran $m \\times n$ menjadi perkalian tiga matriks:")
    st.latex(r"A = U \cdot \Sigma \cdot V^T")
    st.write("""
    - $U$ adalah matriks ortogonal berukuran $m \\times m$ yang berisi **Vektor Eigen** dari $AA^T$.
    - $\Sigma$ adalah matriks diagonal berisi **Nilai Singular** (Akar dari Nilai Eigen).
    - $V^T$ adalah matriks ortogonal berukuran $n \\times n$ yang berisi **Vektor Eigen** dari $A^TA$.
    """)
    st.success("Dengan memotong (truncation) Nilai Singular pada parameter $k$, kita dapat merekonstruksi matriks gambar baru dengan ukuran penyimpanan yang jauh lebih kecil tanpa kehilangan fitur esensialnya (SVD Truncation).")