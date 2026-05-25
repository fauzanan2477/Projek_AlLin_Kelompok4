import streamlit as st
import numpy as np
from PIL import Image

# Bagian Tampilan Web
st.set_page_config(page_title="SVD Image Compressor", page_icon="🗜️")
st.title("🗜️ SVD Image Compressor")
st.write("Aplikasi Kompresi Gambar berbasis Aljabar Linier (Singular Value Decomposition).")

# Fitur Upload Gambar
uploaded_file = st.file_uploader("Unggah Gambar Apa Saja (JPG/PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Membaca gambar sebagai Matriks Hitam Putih (Grayscale) agar proses SVD ringan
    image = Image.open(uploaded_file).convert('L')
    img_matrix = np.array(image)
    
    st.image(image, caption="Gambar Asli", use_column_width=True)
    
    # MATERI ALJABAR LINIER: Dekomposisi Matriks (SVD)
    # Matriks gambar dipecah menjadi U, Sigma (S), dan V Transpose
    U, S, V_T = np.linalg.svd(img_matrix, full_matrices=False)
    
    st.write("---")
    st.write("### Atur Tingkat Kompresi")
    st.write("Semakin kecil nilai *k*, gambar semakin buram tapi ukuran file semakin kecil.")
    
    # Slider untuk memilih jumlah nilai singular (k) yang mau dipakai
    max_k = min(img_matrix.shape)
    k = st.slider("Pilih Nilai k (Singular Values):", min_value=1, max_value=max_k, value=50)
    
    if st.button("Kompres Gambar!"):
        # PROSES MATEMATIKA: Rekonstruksi Matriks yang sudah dikompresi
        # Rumus: Matriks Baru = U_k * Sigma_k * V_T_k
        reconstructed_matrix = np.dot(U[:, :k], np.dot(np.diag(S[:k]), V_T[:k, :]))
        
        # Validasi batas matriks agar tetap berwujud piksel (0-255)
        reconstructed_matrix = np.clip(reconstructed_matrix, 0, 255).astype(np.uint8)
        
        # Ubah matriks kembali menjadi gambar
        hasil_image = Image.fromarray(reconstructed_matrix)
        
        st.success(f"Berhasil! Gambar direkonstruksi hanya dengan {k} nilai singular utama.")
        st.image(hasil_image, caption=f"Hasil Kompresi (k = {k})", use_column_width=True)