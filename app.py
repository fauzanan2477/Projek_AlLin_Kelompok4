import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS
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
    .white-box h1, .white-box h2, .white-box h3, .white-box h4, .white-box p, .white-box li { color: #111111; }
    .hero-title { font-size: 3.2rem; font-weight: 900; color: #000000 !important; line-height: 1.2; margin-bottom: 15px; text-align: center; }
    .hero-title span { color: #1e3799 !important; }
    .hero-subtitle { font-size: 1.2rem; color: #444444 !important; font-weight: 500; text-align: center; margin-bottom: 30px;}
    .result-card { background: linear-gradient(135deg, #1e3799, #0984e3); color: white !important; border-radius: 12px; padding: 30px; text-align: center; margin: 20px 0px; box-shadow: 0 5px 15px rgba(0,0,0,0.2);}
    div[data-baseweb="select"] > div { background-color: transparent; }
    </style>
    <div class="hero-title">Sistem Optimasi Logistik<br><span>Makan Bergizi Gratis (MBG)</span></div>
    <div class="hero-subtitle">Integrasi Ilmu Gizi Biometrik dan Aljabar Linier (Metode Simpleks Dua Fase)</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. INISIALISASI DATABASE (SESSION STATE)
# ==========================================
if 'db_bahan' not in st.session_state:
    st.session_state['db_bahan'] = pd.DataFrame({
        "Gunakan": [True]*4 + [False, True], 
        "Bahan Makanan": ["Nasi Putih", "Telur Ayam", "Tempe Murni", "Sayur Bayam", "Susu Sapi", "Daging Ayam"],
        "Harga (Rp)": [1200, 2600, 1000, 800, 3000, 4500], 
        "Kalori (Kkal)": [130.0, 155.0, 193.0, 23.0, 60.0, 165.0],
        "Protein (g)": [2.7, 13.0, 19.0, 3.0, 3.2, 31.0],
        "Lemak (g)": [0.3, 11.0, 11.0, 0.4, 3.3, 3.6],
        "Karbohidrat (g)": [28.6, 1.1, 9.4, 3.6, 4.8, 0.0],
        "Porsi (g)": [200.0, 100.0, 100.0, 150.0, 200.0, 150.0] 
    })

st.session_state.setdefault('gizi', {'kalori': 1800.0, 'protein': 45.0, 'lemak': 40.0, 'karbo': 202.5, 'bmr': 1161.0, 'pal': 1.55, 'bagi': 1, 'r_t': "", 'r_a': ""})

# ==========================================
# 3. TABS UI
# ==========================================
tab_gizi, tab_aljabar, tab_manual, tab_docs = st.tabs(["1. Kalkulator Gizi", "2. Eksekusi Optimasi", "3. Langkah Manual", "4. Dokumentasi Rumus"])

# --- TAB 1: KALKULATOR GIZI ---
with tab_gizi:
    st.markdown('<div class="white-box"><h3>👦 Penentuan Vektor Konstanta Gizi (B)</h3>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    umur = c1.number_input("Umur (Tahun)", 1, 18, 10)
    jk = c1.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    act_idx = c1.selectbox("Tingkat Aktivitas", ["Sangat Jarang", "Jarang", "Cukup", "Sering", "Sangat Sering"], index=2)
    bb = c2.number_input("Berat Badan (kg)", 5.0, value=30.0)
    tb_m = c2.number_input("Tinggi Badan (cm)", 50.0, value=135.0) / 100.0
    waktu = c2.selectbox("Target Pemenuhan", ["1 Hari Penuh (Persis Jurnal UB)", "1x Makan Siang (Dibagi 3)"])
    
    if st.button("Hitung Target & Simpan", type="primary"):
        pal = [1.2, 1.375, 1.55, 1.725, 1.9][["Sangat Jarang", "Jarang", "Cukup", "Sering", "Sangat Sering"].index(act_idx)]
        
        # Logika BMR Disempurnakan (Ternary / Padat)
        if jk == "Laki-laki":
            bmr = (0.167*bb + 1517.4*tb_m - 617.6) if umur <= 3 else (19.6*bb + 130.3*tb_m + 414.9) if umur <= 10 else (16.25*bb + 137.2*tb_m + 515.5)
            r_t = r"\text{AMB (L)} = " + ("0.167 Wt + 1517.4 Ht - 617.6" if umur <= 3 else "19.6 Wt + 130.3 Ht + 414.9" if umur <= 10 else "16.25 Wt + 137.2 Ht + 515.5")
            r_a = f"\\text{{AMB (L)}} = " + (f"(0.167 \\times {bb}) + (1517.4 \\times {tb_m}) - 617.6" if umur <= 3 else f"(19.6 \\times {bb}) + (130.3 \\times {tb_m}) + 414.9" if umur <= 10 else f"(16.25 \\times {bb}) + (137.2 \\times {tb_m}) + 515.5")
        else:
            bmr = (16.25*bb + 1023.2*tb_m - 413.5) if umur <= 3 else (16.97*bb + 161.8*tb_m + 371.2) if umur <= 10 else (8.365*bb + 465.0*tb_m + 200.0)
            r_t = r"\text{AMB (P)} = " + ("16.25 Wt + 1023.2 Ht - 413.5" if umur <= 3 else "16.97 Wt + 161.8 Ht + 371.2" if umur <= 10 else "8.365 Wt + 465 Ht + 200")
            r_a = f"\\text{{AMB (P)}} = " + (f"(16.25 \\times {bb}) + (1023.2 \\times {tb_m}) - 413.5" if umur <= 3 else f"(16.97 \\times {bb}) + (161.8 \\times {tb_m}) + 371.2" if umur <= 10 else f"(8.365 \\times {bb}) + (465.0 \\times {tb_m}) + 200.0")

        bagi = 1 if "1 Hari" in waktu else 3
        k = (bmr * pal) / bagi
        
        # PERBAIKAN BATAS BAWAH SESUAI JURNAL: 10% Protein, 20% Lemak, 45% Karbo
        st.session_state['gizi'] = {'kalori': k, 'protein': (k * 0.1) / 4, 'lemak': (k * 0.2) / 9, 'karbo': (k * 0.45) / 4, 'bmr': bmr, 'pal': pal, 'bagi': bagi, 'r_t': r_t, 'r_a': r_a}
        st.success("Target Gizi Minimum diperbarui! Lanjut ke Tab 2.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: EKSEKUSI OPTIMASI ---
with tab_aljabar:
    gz = st.session_state['gizi']
    st.markdown('<div class="white-box" style="border-left: 5px solid #e1b12c;"><h4>🎯 Target Gizi Saat Ini (Syarat Matriks Batas Bawah):</h4>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kalori", f"{gz['kalori']:.1f} Kkal")
    c2.metric("Protein (10%)", f"{gz['protein']:.1f} Gram")
    c3.metric("Lemak (20%)", f"{gz['lemak']:.1f} Gram")
    c4.metric("Karbo (45%)", f"{gz['karbo']:.1f} Gram")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="white-box"><h3>🛒 Database Bahan Makanan (Pilih Lauk)</h3>', unsafe_allow_html=True)
    df = st.session_state['db_bahan'] = st.data_editor(st.session_state['db_bahan'], num_rows="dynamic", use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🚀 Kalkulasi Biaya Termurah", type="primary", use_container_width=True):
        d_pilih = df[df["Gunakan"]].copy()
        if len(d_pilih) < 2: st.error("⚠️ Centang minimal 2 bahan makanan.")
        else:
            H = pd.to_numeric(d_pilih["Harga (Rp)"], errors='coerce').fillna(0).values
            Nut = d_pilih[["Kalori (Kkal)", "Protein (g)", "Lemak (g)", "Karbohidrat (g)"]].apply(pd.to_numeric).fillna(0).values
            Bounds = [(0, p/100.0) for p in pd.to_numeric(d_pilih["Porsi (g)"], errors='coerce').fillna(1000).values]
            
            # Simpleks mencari Minimum, batas >= diubah ke <= dengan dikali -1
            res = linprog(H, A_ub=-Nut.T, b_ub=-np.array([gz['kalori'], gz['protein'], gz['lemak'], gz['karbo']]), bounds=Bounds, method='highs')
            
            if res.success:
                st.markdown(f'<div class="result-card"><p>Total Biaya Optimal</p><h2>Rp {res.fun:,.0f}</h2></div>', unsafe_allow_html=True)
                st.markdown('<div class="white-box"><h3>⚖️ Rekomendasi Takaran</h3>', unsafe_allow_html=True)
                st.table(pd.DataFrame({"Bahan Makanan": d_pilih["Bahan Makanan"].values, "Takaran": [f"{g*100:,.0f} Gram" for g in res.x], "Biaya": [f"Rp {g*h:,.0f}" for g, h in zip(res.x, H)]})[res.x > 0.01].reset_index(drop=True))
                st.markdown('</div>', unsafe_allow_html=True)
            else: st.error("🚨 SPL Infeasible: Matriks gagal dipenuhi.")

# --- TAB 3: LANGKAH MANUAL ---
with tab_manual:
    gz = st.session_state['gizi']
    d_aktif = st.session_state['db_bahan'][st.session_state['db_bahan']["Gunakan"]].reset_index(drop=True)
    
    st.markdown('<div class="white-box"><h3>✍️ Simulasi Pemodelan Aljabar</h3><hr><h4>TAHAP 1: Konstanta Gizi (Asal Vektor B)</h4>', unsafe_allow_html=True)
    st.markdown("**1. Angka Metabolisme Basal (AMB)**")
    st.latex(gz['r_t']); st.latex(f"{gz['r_a']} = {gz['bmr']:.1f} \\text{{ Kkal}}")
    st.markdown("**2. Total Energy Expenditure (TEE) & Target Kalori (K)**")
    st.latex(f"K = \\frac{{TEE}}{{{gz['bagi']}}} = \\frac{{{gz['bmr']:.1f} \\times {gz['pal']}}}{{{gz['bagi']}}} = {gz['kalori']:.1f} \\text{{ Kkal}}")
    st.markdown("**3. Distribusi Batas Bawah (Minimum) Sesuai Jurnal**")
    st.latex(r"\text{Protein} = \frac{10\% \times K}{4} \Rightarrow \frac{0.1 \times " + f"{gz['kalori']:.1f}" + r"}{4} = " + f"{gz['protein']:.1f} \\text{{ g}}")
    st.latex(r"\text{Lemak} = \frac{20\% \times K}{9} \Rightarrow \frac{0.2 \times " + f"{gz['kalori']:.1f}" + r"}{9} = " + f"{gz['lemak']:.1f} \\text{{ g}}")
    st.latex(r"\text{Karbo} = \frac{45\% \times K}{4} \Rightarrow \frac{0.45 \times " + f"{gz['kalori']:.1f}" + r"}{4} = " + f"{gz['karbo']:.1f} \\text{{ g}}")
    
    if len(d_aktif) >= 2:
        st.write("<hr><h4>TAHAP 2 & 3: Model Matematika & Bentuk Kanonik</h4>", unsafe_allow_html=True)
        st.latex(r"\text{Min } Z = " + " + ".join([f"{int(r['Harga (Rp)'])}x_{i+1}" for i, r in d_aktif.iterrows()]))
        
        # Compact equation rendering
        nut_cols = ["Kalori (Kkal)", "Protein (g)", "Lemak (g)", "Karbohidrat (g)"]
        b_vals = [gz['kalori'], gz['protein'], gz['lemak'], gz['karbo']]
        for j, (col, b) in enumerate(zip(nut_cols, b_vals)):
            st.latex(" + ".join([f"{r[col]}x_{i+1}" for i, r in d_aktif.iterrows()]) + f" - S_{j+1} + R_{j+1} = {b:.1f}")

        st.write("<hr><h4>TAHAP 4: Tableau Initial Fase 1 (Setelah Substitusi R)</h4>", unsafe_allow_html=True)
        st.latex(r"\text{Minimasi } W = R_1 + R_2 + R_3 + R_4")
        
        # Simplified Matrix Building
        cols = ["Basis"] + [f"x{i+1}" for i in range(len(d_aktif))] + ["S1","S2","S3","S4", "R1","R2","R3","R4", "NK (B)"]
        mat = []
        for i, col in enumerate(nut_cols):
            mat.append([f"R{i+1}"] + list(d_aktif[col]) + [0]*i + [-1] + [0]*(3-i) + [0]*i + [1] + [0]*(3-i) + [b_vals[i]])
        
        # Substitusi W (Sum of X coefficients)
        mat.append(["W (Fase 1)"] + [d_aktif.loc[i, nut_cols].sum() for i in range(len(d_aktif))] + [-1,-1,-1,-1, 0,0,0,0, sum(b_vals)])
        st.dataframe(pd.DataFrame(mat, columns=cols).style.format(precision=1), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 4: DOKUMENTASI ---
with tab_docs:
    st.markdown('<div class="white-box"><h3>📖 Integrasi Matriks Aljabar</h3>', unsafe_allow_html=True)
    st.latex(r"\text{Fungsi Minimum: } Z = \mathbf{C}^T \mathbf{X} \quad | \quad \text{Kendala: } \mathbf{A}\mathbf{X} \ge \mathbf{B}")
    st.markdown("- **$C$**: Vektor harga, **$X$**: Vektor porsi, **$A$**: Matriks gizi, **$B$**: Vektor target gizi.")
    st.markdown('</div>', unsafe_allow_html=True)