import streamlit as st
import numpy as np
from PIL import Image

# Konfigurasi Halaman
st.set_page_config(page_title="Forest Data-Lite | SVD Compressor", layout="centered", page_icon="🌲")

# --- HEADER ---
st.title("🌲 Forest Data-Lite")
st.subheader("Implementasi SVD Kompresi Citra Hutan (SDG 15)")
st.write("Singular Value Decomposition memecah matriks citra ($A$) menjadi $U \Sigma V^T$.")

# --- SIDEBAR (INPUT) ---
st.sidebar.header("Konfigurasi Projek")
uploaded_file = st.sidebar.file_uploader("Unggah Citra Hutan (JPG/PNG)", type=["jpg", "png", "jpeg"])

# --- LOGIKA ALJABAR LINIER ---
if uploaded_file is not None:
    # 1. Konversi ke Grayscale (Matriks 2D)
    image = Image.open(uploaded_file).convert('L')
    A = np.array(image)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Citra Asli**")
        st.image(image, use_column_width=True)
        st.caption(f"Resolusi: {A.shape[0]} x {A.shape[1]} piksel")
    
    # 2. Proses SVD
    U, S, Vt = np.linalg.svd(A, full_matrices=False)
    
    # 3. Slider untuk menentukan Nilai k
    max_k = len(S)
    st.write("---")
    k = st.slider("Atur Nilai Komponen Singular (k):", min_value=1, max_value=max_k, value=50)
    
    # 4. Rekonstruksi Matriks
    Ak = np.dot(U[:, :k], np.dot(np.diag(S[:k]), Vt[:k, :]))
    Ak = np.clip(Ak, 0, 255).astype(np.uint8)
    img_compressed = Image.fromarray(Ak)
    
    with col2:
        st.write(f"**Citra Kompresi (k={k})**")
        st.image(img_compressed, use_column_width=True)
        # Menghitung energi yang dipertahankan (seperti punya temanmu)
        energy_retained = (np.sum(S[:k]**2) / np.sum(S**2)) * 100
        st.caption(f"Informasi Visual Bertahan: {energy_retained:.2f}%")
    
    # --- FITUR PAMER MATRIKS (SEPERTI PUNYA TEMANMU) ---
    st.divider()
    st.write("### 🧮 Detail Komputasi Matriks (Aljabar Linier)")
    st.write("Berikut adalah cuplikan elemen matriks (15x15 piksel pojok kiri atas) yang diproses di belakang layar:")
    
    # Membuat Tab
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Matriks Citra (A)", "Matriks U", "Nilai Singular (Σ)", "Matriks V^T", "Matriks Hasil (Ak)"])
    
    with tab1:
        st.write("Matriks Intensitas Piksel Asli ($A$)")
        st.dataframe(A[:15, :15])
        
    with tab2:
        st.write("Matriks Ortogonal Kiri ($U$) - *Vektor Eigen dari* $AA^T$")
        st.dataframe(U[:15, :15])
        
    with tab3:
        st.write("Matriks Diagonal ($\Sigma$) - *Akar Nilai Eigen*")
        st.dataframe(np.diag(S[:15]))
        
    with tab4:
        st.write("Matriks Ortogonal Kanan ($V^T$) - *Vektor Eigen dari* $A^TA$")
        st.dataframe(Vt[:15, :15])
        
    with tab5:
        st.write("Matriks Hasil Rekonstruksi Kompresi ($A_k$)")
        st.dataframe(Ak[:15, :15])

else:
    st.info("Silakan unggah gambar di bilah sisi (sidebar kiri) untuk memulai simulasi SVD.")