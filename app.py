import streamlit as st
import numpy as np
from PIL import Image
import io

# --- 1. SETUP & CUSTOM CSS (UI MODERN) ---
st.set_page_config(page_title="Fauna-Clear | SVD Denoising", layout="wide", page_icon="🐾")

st.markdown("""
    <style>
    /* Tema Gelap Elegan */
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    
    /* Header Gradasi */
    .hero-box { 
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
        padding: 40px; 
        border-radius: 20px; 
        text-align: center; 
        box-shadow: 0px 10px 20px rgba(0,0,0,0.3);
        margin-bottom: 30px;
    }
    .hero-title { color: white; font-size: 3.5rem; font-weight: 900; margin-bottom: 0px; font-family: 'Arial Black', sans-serif; letter-spacing: 2px;}
    .hero-subtitle { color: #E8F5E9; font-size: 1.3rem; font-weight: 500; }
    
    /* Box Metrik */
    div[data-testid="metric-container"] {
        background-color: #1E2127; border: 1px solid #333; padding: 15px; border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. HEADER APLIKASI ---
st.markdown("""
<div class="hero-box">
    <p class="hero-title">🐾 Fauna-Clear SVD</p>
    <p class="hero-subtitle">Sistem Pembersihan Derau Citra Kamera Jebak Satwa Liar (SDG 15)</p>
</div>
""", unsafe_allow_html=True)

# --- 3. TAB NAVIGASI ---
tab1, tab2 = st.tabs(["🎛️ WORKSPACE DENOISING", "📖 LANDASAN ALJABAR LINIER"])

with tab1:
    st.info("💡 **Skenario Demo:** Unggah foto hewan. Sistem akan mensimulasikan foto tersebut sebagai hasil jepretan malam hari yang penuh bintik (Noise), lalu menggunakan SVD untuk membersihkannya.")
    
    # Kotak Upload di tengah
    col_up1, col_up2, col_up3 = st.columns([1, 2, 1])
    with col_up2:
        uploaded_file = st.file_uploader("📸 Unggah Foto Satwa Liar", type=["jpg", "png"])

    if uploaded_file is not None:
        # Buka Gambar dan Jadikan Grayscale
        image_asli = Image.open(uploaded_file).convert('L')
        A = np.array(image_asli)
        
        # --- SIMULASI NOISE KAMERA JEBAK ---
        # Membuat derau (bintik acak) menggunakan distribusi normal matriks
        noise = np.random.normal(0, 40, A.shape) 
        A_noisy = A + noise
        A_noisy = np.clip(A_noisy, 0, 255).astype(np.uint8) # Jaga di rentang piksel
        
        st.write("---")
        st.markdown("### 🎚️ Panel Kontrol Dekomposisi Matriks")
        
        # --- PROSES SVD ---
        U, S, Vt = np.linalg.svd(A_noisy, full_matrices=False)
        max_k = len(S)
        
        # Slider dengan desain yang lebih rapi
        k = st.slider("Tentukan Jumlah Nilai Singular (k) untuk merekonstruksi citra:", 1, max_k, max_k // 10)
        
        # Rekonstruksi Matriks Denoise
        Ak = np.dot(U[:, :k], np.dot(np.diag(S[:k]), Vt[:k, :]))
        Ak = np.clip(Ak, 0, 255).astype(np.uint8)
        
        # --- TAMPILAN DASHBOARD HASIL ---
        col_img1, col_img2 = st.columns(2)
        
        with col_img1:
            st.markdown("#### 🌙 Citra Kamera Jebak (Noisy)")
            st.image(A_noisy, use_column_width=True)
            st.caption("Gambar penuh bintik karena kurang cahaya / cuaca buruk.")
            
        with col_img2:
            st.markdown(f"#### 🐾 Hasil Pembersihan SVD (k={k})")
            st.image(Ak, use_column_width=True)
            st.caption("Gambar setelah dibersihkan menggunakan pemotongan matriks.")
            
        # Tampilan Metrik ala Dashboard
        st.markdown("### 📊 Analisis Komputasi")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Dimensi Matriks", f"{A.shape[0]} x {A.shape[1]}")
        col_m2.metric("Nilai Singular Terbuang", f"{max_k - k} Fitur")
        
        # Rumus sederhana: semakin kecil k, semakin banyak derau yang dibuang
        persentase_noise_hilang = (1 - (k / max_k)) * 100
        col_m3.metric("Estimasi Derau Dibuang", f"{persentase_noise_hilang:.1f} %")

        # Tombol Download
        buf = io.BytesIO()
        Image.fromarray(Ak).save(buf, format="PNG")
        st.download_button("📥 Simpan Bukti Pemantauan", buf.getvalue(), "satwa_terpantau.png", "image/png", use_container_width=True)

with tab2:
    st.markdown("### 🧮 Bagaimana SVD Membersihkan *Noise*?")
    st.write("""
    1. **Matriks Citra:** Foto *camera trap* malam hari (yang berbintik) dibaca sebagai matriks $A$.
    2. **Dekomposisi SVD ($A = U \cdot \Sigma \cdot V^T$):** Matriks tersebut dipecah. Matriks diagonal $\Sigma$ menyimpan 'Nilai Singular'.
    3. **Pemisahan Signal & Noise:** Dalam Aljabar Linier, nilai singular yang **besar** mewakili informasi visual utama (bentuk badan hewan, corak mata). Sedangkan nilai singular yang **sangat kecil** biasanya merupakan *noise* (bintik-bintik derau sensor kamera).
    4. **Pemotongan (Truncation):** Dengan memotong matriks dan hanya mengambil sejumlah $k$ nilai singular terbesar, kita membuang nilai-nilai kecil tersebut. Hasilnya saat matriks dikalikan kembali, bentuk hewan tetap ada, tetapi *noise*-nya hilang!
    """)