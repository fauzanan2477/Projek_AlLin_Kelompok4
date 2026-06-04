import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS KONTRAS TINGGI
# ==========================================
st.set_page_config(page_title="Sistem Pakar MBG", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; color: #111111; }
    .block-container { padding-top: 2rem; max-width: 1100px; }
    .white-box { background-color: #ffffff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #e1e4e8; color: #333333;}
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 30px; border-bottom: 2px solid #dcdde1; background-color: #ffffff; padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { font-weight: 800; font-size: 1.15rem; color: #555555; background-color: transparent; border: none; }
    .stTabs [aria-selected="true"] { color: #1e3799; border-bottom: 4px solid #1e3799; }
    
    /* REVISI CSS: Menghapus paksaan warna hitam pada list <li> global agar tidak merusak Dropdown Dark Mode */
    h1, h2, h3, h4, p { color: #111111 !important; }
    .white-box li { color: #333333; } 
    
    .hero-title { font-size: 3.2rem; font-weight: 900; color: #000000 !important; line-height: 1.2; margin-bottom: 15px; text-align: center; }
    .hero-title span { color: #1e3799 !important; }
    .hero-subtitle { font-size: 1.2rem; color: #444444 !important; font-weight: 500; text-align: center; margin-bottom: 30px;}
    .result-card { background: linear-gradient(135deg, #1e3799, #0984e3); color: white !important; border-radius: 12px; padding: 30px; text-align: center; margin: 20px 0px; box-shadow: 0 5px 15px rgba(0,0,0,0.2);}
    .result-card h2 { color: #ffffff !important; font-size: 3.5rem; margin: 0; font-weight: 900;}
    .result-card p { color: #dff9fb !important; font-size: 1.1rem; margin: 0; font-weight: bold; letter-spacing: 1px;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HERO SECTION
# ==========================================
st.markdown("""
<div class="hero-title">Sistem Optimasi Logistik<br><span>Makan Bergizi Gratis (MBG)</span></div>
<div class="hero-subtitle">Integrasi Ilmu Gizi Biometrik dan Aljabar Linier (Metode Simpleks Dua Fase)</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATABASE (SESSION STATE)
# ==========================================
if 'db_bahan' not in st.session_state:
    st.session_state['db_bahan'] = pd.DataFrame({
        "Gunakan": [True, True, True, True, False, True], 
        "Bahan Makanan": ["Nasi Putih", "Telur Ayam", "Tempe Murni", "Sayur Bayam", "Susu Sapi", "Daging Ayam"],
        "Harga (Rp)": [1200, 2600, 1000, 800, 3000, 4500], 
        "Kalori (Kkal)": [130.0, 155.0, 193.0, 23.0, 60.0, 165.0],
        "Protein (g)": [2.7, 13.0, 19.0, 3.0, 3.2, 31.0],
        "Lemak (g)": [0.3, 11.0, 11.0, 0.4, 3.3, 3.6],
        "Karbohidrat (g)": [28.6, 1.1, 9.4, 3.6, 4.8, 0.0],
        "Porsi (g)": [200.0, 100.0, 100.0, 150.0, 200.0, 150.0] 
    })

if 'target_kalori' not in st.session_state:
    st.session_state.update({
        'target_kalori': 1800.0, 'target_protein': 45.0, 'target_lemak': 40.0, 'target_karbo': 202.5,
        'aktivitas_val': 1.55, 'bmr_val': 1161.0, 'pembagi_val': 1,
        'rumus_amb_teks': r"\text{AMB (P)} = 16.969 Wt + 161.8 Ht + 371.2",
        'rumus_amb_angka': r"\text{AMB (P)} = (16.969 \times 30.0) + (161.8 \times 1.35) + 371.2"
    })

# ==========================================
# 4. MENU NAVBAR (TABS)
# ==========================================
tab_gizi, tab_aljabar, tab_manual, tab_docs = st.tabs(["1. Kalkulator Gizi", "2. Eksekusi Optimasi", "3. Langkah Manual (Sangat Detail)", "4. Dokumentasi Rumus"])

# --- HALAMAN 1: KALKULATOR GIZI ---
with tab_gizi:
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### 👦 Penentuan Vektor Konstanta Gizi (B)")
    st.write("Sistem menghitung target Makronutrien anak berdasarkan **Persamaan AMB Schofield** dan tingkat aktivitas fisik (Merujuk pada Jurnal Brawijaya).")
    
    col_bio1, col_bio2 = st.columns(2)
    with col_bio1:
        umur = st.number_input("Umur Anak (Tahun)", min_value=1, max_value=18, value=10)
        jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        aktivitas = st.selectbox("Tingkat Aktivitas Fisik", ["Sangat Jarang (Pasif / Tidak olahraga)", "Jarang (Olahraga ringan 1-3 hari/minggu)", "Cukup (Olahraga sedang 3-5 hari/minggu)", "Sering (Olahraga berat 6-7 hari/minggu)", "Sangat Sering (Atlet / Fisik ekstra)"], index=2)
        
    with col_bio2:
        bb = st.number_input("Berat Badan / Wt (kg)", min_value=5.0, value=30.0)
        tb = st.number_input("Tinggi Badan / Ht (cm)", min_value=50.0, value=135.0)
        target_waktu = st.selectbox("Target Pemenuhan Gizi (Skenario)", ["1 Hari Penuh (Persis Jurnal UB)", "1x Makan Siang (Program MBG - Dibagi 3)"])
    
    if st.button("Hitung Target & Simpan", type="primary"):
        # 1. Menentukan Multiplier Olahraga (Dictionary sederhana)
        act_map = {"Sangat Jarang (Pasif / Tidak olahraga)": 1.2, "Jarang (Olahraga ringan 1-3 hari/minggu)": 1.375, "Cukup (Olahraga sedang 3-5 hari/minggu)": 1.55, "Sering (Olahraga berat 6-7 hari/minggu)": 1.725, "Sangat Sering (Atlet / Fisik ekstra)": 1.9}
        multiplier = act_map[aktivitas]

        # 2. Rumus AMB Schofield (Disederhanakan logikanya)
        tb_m = tb / 100.0 
        if jk == "Laki-laki":
            c_w, c_h, c_c = (0.167, 1517.4, -617.6) if umur <= 3 else (19.59, 130.3, 414.9) if umur <= 10 else (16.25, 137.2, 515.5)
            lbl = "L"
        else:
            c_w, c_h, c_c = (16.25, 1023.2, -413.5) if umur <= 3 else (16.969, 161.8, 371.2) if umur <= 10 else (8.365, 465.0, 200.0)
            lbl = "P"
            
        bmr = (c_w * bb) + (c_h * tb_m) + c_c
        sign = "+" if c_c >= 0 else "-"
        
        # 3. Kebutuhan Makro (Batas Bawah Jurnal: 10% Pro, 20% Lemak, 45% Karbo)
        pembagi = 1 if "1 Hari" in target_waktu else 3
        porsi_kalori = (bmr * multiplier) / pembagi
        
        st.session_state.update({
            'bmr_val': round(bmr, 1), 'aktivitas_val': multiplier, 'pembagi_val': pembagi,
            'target_kalori': round(porsi_kalori, 1), 
            'target_protein': round((porsi_kalori * 0.10) / 4, 1),
            'target_lemak': round((porsi_kalori * 0.20) / 9, 1), 
            'target_karbo': round((porsi_kalori * 0.45) / 4, 1),
            'rumus_amb_teks': fr"\text{{AMB ({lbl})}} = {c_w} Wt + {c_h} Ht {sign} {abs(c_c)}", 
            'rumus_amb_angka': fr"\text{{AMB ({lbl})}} = ({c_w} \times {bb}) + ({c_h} \times {tb_m}) {sign} {abs(c_c)}"
        })
        st.success(f"Target Gizi diperbarui ({target_waktu})! Lanjut ke Tab 2.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- HALAMAN 2: EKSEKUSI OPTIMASI ---
with tab_aljabar:
    st.markdown('<div class="white-box" style="border-left: 5px solid #e1b12c;">', unsafe_allow_html=True)
    st.write("#### 🎯 Target Gizi Saat Ini (Syarat Matriks):")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kalori Minimal", f"{st.session_state['target_kalori']} Kkal")
    c2.metric("Protein (Min 10%)", f"{st.session_state['target_protein']} Gram")
    c3.metric("Lemak (Min 20%)", f"{st.session_state['target_lemak']} Gram")
    c4.metric("Karbo (Min 45%)", f"{st.session_state['target_karbo']} Gram")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### 🛒 Database Bahan Makanan (Pilih Lauk)")
    df_interaktif = st.data_editor(st.session_state['db_bahan'], num_rows="dynamic", use_container_width=True, hide_index=True)
    st.session_state['db_bahan'] = df_interaktif
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🚀 Kalkulasi Biaya Termurah", type="primary", use_container_width=True):
        df_dipilih = df_interaktif[df_interaktif["Gunakan"] == True].copy()
        
        if len(df_dipilih) < 2: st.error("⚠️ Centang minimal 2 bahan makanan untuk komputasi.")
        else:
            harga = pd.to_numeric(df_dipilih["Harga (Rp)"], errors='coerce').fillna(0).values
            gizi = df_dipilih[["Kalori (Kkal)", "Protein (g)", "Lemak (g)", "Karbohidrat (g)"]].apply(pd.to_numeric, errors='coerce').fillna(0)
            porsi = [(0, p/100.0) for p in pd.to_numeric(df_dipilih["Porsi (g)"], errors='coerce').fillna(1000).values]
            b_ub = -np.array([st.session_state['target_kalori'], st.session_state['target_protein'], st.session_state['target_lemak'], st.session_state['target_karbo']])
            
            try:
                hasil = linprog(harga, A_ub=-gizi.values.T, b_ub=b_ub, bounds=porsi, method='highs')
                if hasil.success:
                    st.markdown(f'<div class="result-card"><p>Total Biaya Paling Minimum (Titik Optimal)</p><h2>Rp {hasil.fun:,.0f}</h2><p>Solusi Makanan Termurah Sesuai Target Waktu</p></div>', unsafe_allow_html=True)
                    st.markdown('<div class="white-box">### ⚖️ Vektor Rekomendasi Takaran', unsafe_allow_html=True)
                    df_hasil = pd.DataFrame({"Bahan Makanan": df_dipilih["Bahan Makanan"].values, "Takaran Disarankan": [f"{g*100:,.0f} Gram" for g in hasil.x], "Biaya Realisasi": [f"Rp {g*h:,.0f}" for g, h in zip(hasil.x, harga)]})
                    st.table(df_hasil[hasil.x > 0.01].reset_index(drop=True))
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("🚨 SPL Infeasible: Matriks kendala gagal dipenuhi. Coba variasikan porsi makanan.")
            except Exception as e:
                st.error(f"Error komputasi: {e}")

# --- HALAMAN 3: LANGKAH MANUAL (SANGAT DETAIL) ---
with tab_manual:
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write("### ✍️ Simulasi Pemodelan: Dari Biometrik ke Matriks")
    st.write("Di balik layar, sistem ini bekerja melalui dua tahap besar: (1) Penentuan Kebutuhan Gizi Makronutrien dan (2) Optimasi Matriks Simpleks Dua Fase.")
    
    st.write("---")
    st.write("#### TAHAP 1: Perhitungan Konstanta Gizi (Asal Mula Vektor B)")
    st.markdown("**1. Angka Metabolisme Basal (AMB) - Persamaan Schofield**")
    st.latex(st.session_state['rumus_amb_teks'])
    st.latex(st.session_state['rumus_amb_angka'] + f" = {st.session_state['bmr_val']} \\text{{ Kkal}}")
    
    st.markdown("**2. Total Energy Expenditure (TEE) & Target Kalori Akhir (K)**")
    st.latex(f"TEE = {st.session_state['bmr_val']} \\times {st.session_state['aktivitas_val']} = {round(st.session_state['bmr_val'] * st.session_state['aktivitas_val'], 1)} \\text{{ Kkal}}")
    st.latex(r"K = \frac{TEE}{" + str(st.session_state.get('pembagi_val', 3)) + r"} = " + str(st.session_state['target_kalori']) + r" \text{ Kkal}")
    
    st.markdown("**3. Distribusi Batas Bawah Gizi Minimum (Jurnal)**")
    st.latex(r"\text{Protein (10\%)} = \frac{10\% \times K}{4} \Rightarrow " + str(st.session_state['target_protein']) + r" \text{ g}")
    st.latex(r"\text{Lemak (20\%)} = \frac{20\% \times K}{9} \Rightarrow " + str(st.session_state['target_lemak']) + r" \text{ g}")
    st.latex(r"\text{Karbo (45\%)} = \frac{45\% \times K}{4} \Rightarrow " + str(st.session_state['target_karbo']) + r" \text{ g}")
    
    df_aktif = st.session_state['db_bahan'][st.session_state['db_bahan']["Gunakan"] == True].reset_index(drop=True)
    if len(df_aktif) >= 2:
        nut_cols = ["Kalori (Kkal)", "Protein (g)", "Lemak (g)", "Karbohidrat (g)"]
        b_vals = [st.session_state['target_kalori'], st.session_state['target_protein'], st.session_state['target_lemak'], st.session_state['target_karbo']]
        
        st.write("---")
        st.write("#### TAHAP 2: Model Matematika (Fungsi Asli)")
        st.latex(r"\text{Fungsi Tujuan: } Z = " + " + ".join([f"{int(r['Harga (Rp)'])}x_{i+1}" for i, r in df_aktif.iterrows()]))
        for i, (col, b_val) in enumerate(zip(nut_cols, b_vals)):
            st.latex(f"\\text{{Kendala {i+1}: }} " + " + ".join([f"{r[col]}x_{j+1}" for j, r in df_aktif.iterrows()]) + f" \ge {b_val}")
        
        st.write("---")
        st.write("#### TAHAP 3: Bentuk Kanonik (Surplus & Artificial Variables)")
        for i, (col, b_val) in enumerate(zip(nut_cols, b_vals)):
            st.latex(" + ".join([f"{r[col]}x_{j+1}" for j, r in df_aktif.iterrows()]) + f" - S_{i+1} + R_{i+1} = {b_val}")
        
        st.write("---")
        st.write("#### TAHAP 4: FASE 1 (Mencari Solusi Awal Fisibel)")
        st.latex(r"\text{Fungsi Tujuan Fase 1: Minimasi } W = R_1 + R_2 + R_3 + R_4")
        
        # Pembangunan Matriks Dinamis (Disederhanakan menggunakan Loop)
        kolom_lengkap = ["Basis"] + [f"x{i+1}" for i in range(len(df_aktif))] + ["S1", "S2", "S3", "S4", "R1", "R2", "R3", "R4", "NK (B)"]
        matriks = []
        for i, (col, b_val) in enumerate(zip(nut_cols, b_vals)):
            S_cols, R_cols = [0]*4, [0]*4
            S_cols[i], R_cols[i] = -1, 1
            matriks.append([f"R{i+1}"] + list(df_aktif[col]) + S_cols + R_cols + [b_val])
            
        sum_x = df_aktif[nut_cols].sum(axis=1).tolist()
        matriks.append(["W (Fase 1)"] + sum_x + [-1,-1,-1,-1, 0,0,0,0, sum(b_vals)])
        
        st.dataframe(pd.DataFrame(matriks, columns=kolom_lengkap).style.format(precision=1), use_container_width=True, hide_index=True)
        st.caption("📌 *Ini adalah Tableau Initial Fase 1 yang sudah ter-substitusi. Operasi Baris Elementer (OBE) akan mereduksi matriks ini hingga nilai pada baris W mencapai 0.*")
        st.write("---")
        st.write("#### TAHAP 5: FASE 2 (Optimasi Biaya Termurah)")
        st.write("Setelah kolom $R$ dibuang, algoritma mengembalikan fungsi biaya asli ($Z$) ke dalam matriks untuk mencari titik temu harga termurah (Hasil akhir tampil di Tab 2).")
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- HALAMAN 4: DOKUMENTASI (RUMUS) ---
with tab_docs:
    st.markdown('<div class="white-box"><h3>📖 Integrasi Matriks Aljabar</h3>', unsafe_allow_html=True)
    st.latex(r"\text{Fungsi Minimum: } Z = \mathbf{C}^T \mathbf{X}")
    st.latex(r"\text{Batasan Mutlak (Matriks): } \mathbf{A}\mathbf{X} \ge \mathbf{B}")
    st.markdown("- $C$ : Vektor harga makanan.<br>- $X$ : Vektor porsi makanan.<br>- $A$ : Matriks kandungan gizi.<br>- $B$ : Vektor target minimal.", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)