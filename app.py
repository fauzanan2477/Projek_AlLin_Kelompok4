import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. KONFIGURASI DASHBOARD
# ==========================================
st.set_page_config(page_title="Sistem Optimasi MBG (Aljabar Linier)", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; max-width: 95%; }
    .header-box { border-bottom: 4px solid #27ae60; padding-bottom: 10px; margin-bottom: 20px; }
    .header-box h1 { font-size: 2.2rem; color: #27ae60; margin: 0; font-weight: 800; }
    .header-box p { font-size: 1.1rem; color: #555; margin-top: 5px; }
    .cost-card { background: linear-gradient(135deg, #f39c12, #d35400); color: white; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATABASE MAKANAN (DEFAULT MATRIKS)
# ==========================================
if 'db_bahan' not in st.session_state:
    st.session_state['db_bahan'] = pd.DataFrame({
        "Bahan Makanan": ["Nasi Putih", "Telur Rebus", "Dada Ayam", "Tempe Goreng", "Sayur Bayam", "Susu UHT", "Pisang"],
        "Harga (Rp)": [1200, 2600, 4500, 1000, 800, 3000, 1500], # per 100 gram
        "Kalori (Kkal)": [130, 155, 165, 193, 23, 60, 89],
        "Protein (g)": [2.7, 13.0, 31.0, 19.0, 3.0, 3.2, 1.1],
        "Lemak (g)": [0.3, 11.0, 3.6, 11.0, 0.4, 3.3, 0.3]
    })

# ==========================================
# 3. SIDEBAR (KONTROL VEKTOR TARGET)
# ==========================================
with st.sidebar:
    st.header("⚙️ Vektor Target Gizi")
    st.caption("Batasan Sistem Persamaan Linier (SPL)")
    min_kalori = st.number_input("Minimal Kalori (Kkal)", value=700.0, step=50.0)
    min_protein = st.number_input("Minimal Protein (g)", value=25.0, step=5.0)
    min_lemak = st.number_input("Minimal Lemak (g)", value=15.0, step=5.0)
    
    st.write("---")
    st.info("💡 **Logika Aljabar:** Nilai ini adalah Vektor B. Algoritma matriks akan mencari penyelesaian termurah tanpa melanggar batas gizi minimal ini.")

# ==========================================
# 4. HEADER UTAMA
# ==========================================
st.markdown("""
<div class="header-box">
    <h1>🍲 Sistem Cerdas Optimasi Makan Bergizi Gratis (MBG)</h1>
    <p>Engine: Aljabar Linier (SPL & Matriks Simpleks) | SDG 2 (Zero Hunger) & SDG 3 (Good Health)</p>
</div>
""", unsafe_allow_html=True)

# TABS NAVBAR
tab1, tab2, tab3 = st.tabs(["📊 Dasbor Komputasi Matriks", "📝 Editor Harga Pasar", "🧮 Bedah Rumus Aljabar (SPL)"])

# ==========================================
# TAB 2: DATABASE INTERAKTIF
# ==========================================
with tab2:
    st.write("### 🛒 Editor Data Harga & Gizi (per 100 gram)")
    st.write("Ubah harga bahan sesuai inflasi pasar. Anda juga bisa menambah baris makanan baru. Matriks Aljabar akan otomatis beradaptasi.")
    
    tabel_diedit = st.data_editor(
        st.session_state['db_bahan'], 
        num_rows="dynamic", 
        use_container_width=True,
        key="tabel_bahan_mbg"
    )
    st.session_state['db_bahan'] = tabel_diedit

# ==========================================
# TAB 1: DASBOR OPTIMASI & VISUALISASI
# ==========================================
with tab1:
    col_btn, col_blank = st.columns([1, 2])
    with col_btn:
        jalankan = st.button("🚀 Eksekusi Operasi Matriks (Cari Biaya Minimum)", type="primary", use_container_width=True)

    st.write("---")
    
    if jalankan:
        df = st.session_state['db_bahan']
        
        # --- PROSES MATEMATIKA (SPL) ---
        c = df["Harga (Rp)"].values # Fungsi Objektif
        
        # Matriks Kendala (A) dan Vektor Target (B)
        # Dikali -1 karena scipy membaca <= , sedangkan batas gizi adalah >=
        A_ub = -1 * df[["Kalori (Kkal)", "Protein (g)", "Lemak (g)"]].values.T
        b_ub = -1 * np.array([min_kalori, min_protein, min_lemak])
        batas = [(0, None) for _ in range(len(c))]
        
        # Eksekusi Solver (Simplex / Highs)
        hasil = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=batas, method='highs')
        
        if hasil.success:
            st.toast("Titik Penyelesaian SPL Berhasil Ditemukan!", icon="✅")
            
            # TAMPILAN BIAYA (HERO METRIC)
            st.markdown(f"""
                <div class="cost-card">
                    <h4 style="margin:0; color:white;">Total Biaya Termurah (Titik Optimal)</h4>
                    <h1 style="margin:0; color:white; font-size:3rem;">Rp {hasil.fun:,.0f} <span style="font-size:1.5rem">/ Porsi</span></h1>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("<br>", unsafe_allow_html=True)
            
            # Proses Hasil Takaran (Vektor X)
            hasil_gram = hasil.x * 100 
            df_hasil = pd.DataFrame({
                "Bahan Makanan": df["Bahan Makanan"],
                "Gramasi": hasil_gram,
                "Biaya": (hasil_gram/100) * c,
                "Kalori Didapat": (hasil_gram/100) * df["Kalori (Kkal)"],
                "Protein Didapat": (hasil_gram/100) * df["Protein (g)"],
            })
            
            # Filter hanya makanan yang masuk rekomendasi
            df_final = df_hasil[df_hasil["Gramasi"] > 0.01].reset_index(drop=True)
            
            # LAYOUT DUA KOLOM UNTUK TABEL & GRAFIK
            col_tabel, col_grafik = st.columns([1.2, 1])
            
            with col_tabel:
                st.write("### ⚖️ Vektor Penyelesaian (Takaran Gram)")
                # Format tabel agar rapi
                df_tampil = df_final.copy()
                df_tampil["Gramasi"] = df_tampil["Gramasi"].map("{:,.0f} g".format)
                df_tampil["Biaya"] = df_tampil["Biaya"].map("Rp {:,.0f}".format)
                df_tampil["Kalori Didapat"] = df_tampil["Kalori Didapat"].map("{:,.0f} Kkal".format)
                df_tampil["Protein Didapat"] = df_tampil["Protein Didapat"].map("{:,.1f} g".format)
                st.dataframe(df_tampil, use_container_width=True, hide_index=True)
            
            with col_grafik:
                st.write("### 🥧 Proporsi Alokasi Dana")
                # Visualisasi Pie Chart
                fig_pie = px.pie(df_final, values='Biaya', names='Bahan Makanan', hole=0.4, 
                                 color_discrete_sequence=px.colors.sequential.YlOrRd)
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
                st.plotly_chart(fig_pie, use_container_width=True)

            # BAR CHART PEMENUHAN GIZI
            st.write("### 📊 Validasi Pemenuhan Gizi (Batas Minimal vs Realisasi)")
            real_kalori = df_final["Kalori Didapat"].sum()
            real_protein = df_final["Protein Didapat"].sum()
            
            fig_bar = go.Figure(data=[
                go.Bar(name='Target Minimal', x=['Kalori', 'Protein'], y=[min_kalori, min_protein], marker_color='#95a5a6'),
                go.Bar(name='Realisasi (Hasil Optimasi)', x=['Kalori', 'Protein'], y=[real_kalori, real_protein], marker_color='#27ae60')
            ])
            fig_bar.update_layout(barmode='group', height=350, margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_bar, use_container_width=True)
            
        else:
            st.error("🚨 **Sistem Infeasible:** Matriks tidak memiliki ruang penyelesaian (garis kendala tidak berpotongan). Target gizi terlalu tinggi dan tidak bisa dipenuhi oleh bahan makanan yang ada di database.")

# ==========================================
# TAB 3: DOKUMENTASI MATEMATIKA (LATEX)
# ==========================================
with tab3:
    st.write("### 📑 Pemodelan Sistem Persamaan Linier (SPL)")
    st.write("Di balik layar, aplikasi ini menerjemahkan database makanan ke dalam bahasa matriks aljabar:")
    
    st.write("**1. Fungsi Objektif (Minimasi Z):** Vektor harga dikalikan dengan vektor variabel takaran makanan ($X$).")
    st.latex(r"\text{Minimalkan } Z = \mathbf{C}^T \mathbf{X}")
    st.latex(r"Z = c_1x_1 + c_2x_2 + \dots + c_nx_n")
    
    st.write("**2. Sistem Kendala Nutrisi (Pertidaksamaan Matriks):** Matriks kandungan gizi ($A$) dikalikan vektor takaran ($X$), hasilnya wajib melebihi vektor target gizi ($B$).")
    st.latex(r"\mathbf{A}\mathbf{X} \ge \mathbf{B}")
    
    st.write("Bentuk Matriks yang dihitung oleh komputer:")
    st.latex(r"""
    \begin{bmatrix}
    \text{Kalori}_1 & \text{Kalori}_2 & \dots & \text{Kalori}_n \\
    \text{Protein}_1 & \text{Protein}_2 & \dots & \text{Protein}_n \\
    \text{Lemak}_1 & \text{Lemak}_2 & \dots & \text{Lemak}_n
    \end{bmatrix}
    \begin{bmatrix}
    x_1 \\ x_2 \\ \dots \\ x_n
    \end{bmatrix}
    \ge
    \begin{bmatrix}
    \text{Target Kalori} \\
    \text{Target Protein} \\
    \text{Target Lemak}
    \end{bmatrix}
    """)
    
    st.info("Algoritma kemudian melakukan serangkaian iterasi Operasi Baris Elementer (OBE) pada matriks *tableau* hingga menemukan titik penyelesaian di mana nilai $Z$ (harga) adalah yang paling kecil/murah.")