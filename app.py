import streamlit as st
import numpy as np
from PIL import Image

st.set_page_config(page_title="Forest-Vision | SDG 15", layout="wide", page_icon="🌲")

st.title("🌲 Forest-Vision: Pengolahan Citra Satelit Hutan")
st.write("**Mendukung SDG 15 (Life on Land) via Aljabar Linier (SVD & Penskalaan Matriks)**")

uploaded_file = st.file_uploader("Unggah Citra Satelit/Drone Hutan (JPG/PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # 1. Konversi ke Grayscale untuk memudahkan dekomposisi matriks 2D
    image_asli = Image.open(uploaded_file).convert('L')
    
    # --- FITUR 1: UBAH UKURAN (RESIZE MATRIKS) ---
    st.sidebar.header("⚙️ 1. Penskalaan Resolusi Matriks")
    scale_percent = st.sidebar.slider("Skala Gambar Asli (%)", 10, 100, 50)
    
    # Proses Matematika: Mengurangi Ordo Matriks
    width = int(image_asli.width * scale_percent / 100)
    height = int(image_asli.height * scale_percent / 100)
    image_resized = image_asli.resize((width, height))
    A = np.array(image_resized) # Mengubah gambar menjadi Matriks A
    
    # --- FITUR 2: KOMPRESI SVD ---
    st.sidebar.header("🗜️ 2. Kompresi SVD")
    st.sidebar.write("Matriks didekomposisi menjadi U, Σ, V^T")
    U, S, Vt = np.linalg.svd(A, full_matrices=False)
    
    max_k = len(S)
    k = st.sidebar.slider("Jumlah Nilai Singular (k) yang dipakai:", 1, max_k, max_k // 5)
    
    # Proses Matematika: Rekonstruksi Matriks Ak
    Ak = np.dot(U[:, :k], np.dot(np.diag(S[:k]), Vt[:k, :]))
    Ak = np.clip(Ak, 0, 255).astype(np.uint8)
    image_compressed = Image.fromarray(Ak)
    
    # --- TAMPILAN ANTARMUKA ---
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"### 🖼️ Citra Pra-Proses (Ordo Matriks: {width}x{height})")
        st.image(image_resized, use_column_width=True)
        st.info("Gambar ini sudah diskalakan resolusinya melalui Interpolasi piksel.")
        
    with col2:
        st.write(f"### 🗜️ Citra Hasil SVD (Nilai k = {k})")
        st.image(image_compressed, use_column_width=True)
        energy = (np.sum(S[:k]**2) / np.sum(S**2)) * 100
        st.success(f"Dekomposisi berhasil! Energi visual yang dipertahankan: **{energy:.2f}%**")