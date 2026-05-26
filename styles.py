"""
styles.py
=========
Semua CSS dan fungsi pembuat komponen HTML.
Tidak ada logika bisnis di sini — murni tampilan.
"""

import streamlit as st


# ─────────────────────────────────────────────────────────
# BAGIAN 1: CSS UTAMA
# ─────────────────────────────────────────────────────────

CSS_UTAMA = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --hijau-gelap:  #0d2b0f;
    --hijau-tengah: #2d6a30;
    --hijau-terang: #4a9e50;
    --hijau-daun:   #6dbf6e;
    --hijau-lime:   #a8d96c;
    --emas:         #d4a843;
    --krem:         #f5f0e8;
}

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(
        160deg,
        #0a1f0b 0%, #0d2b0f 40%,
        #112d13 70%, #0a1a0b 100%
    ) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--krem) !important;
}

[data-testid="stHeader"] { background: transparent !important; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071409 0%, #0f2410 100%) !important;
    border-right: 1px solid rgba(109,191,110,0.15) !important;
}
[data-testid="stSidebar"] * { color: var(--krem) !important; }

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(13,43,15,0.6) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(109,191,110,0.15) !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 10px !important;
    color: rgba(245,240,232,0.6) !important;
    font-weight: 500 !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: linear-gradient(
        135deg, var(--hijau-tengah), var(--hijau-gelap)
    ) !important;
    color: var(--hijau-daun) !important;
}

[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, var(--hijau-tengah), var(--hijau-lime)) !important;
    border-radius: 99px !important;
}
[data-testid="stProgress"] > div {
    background: rgba(255,255,255,0.07) !important;
    border-radius: 99px !important;
    height: 8px !important;
}

[data-testid="stButton"] button,
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, var(--hijau-tengah), #1f5222) !important;
    color: var(--krem) !important;
    border: 1px solid rgba(109,191,110,0.4) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.25s !important;
}
[data-testid="stButton"] button:hover,
[data-testid="stDownloadButton"] button:hover {
    background: linear-gradient(135deg, var(--hijau-terang), var(--hijau-tengah)) !important;
    box-shadow: 0 4px 20px rgba(45,106,48,0.5) !important;
}

[data-testid="stSelectbox"] > div > div {
    background: rgba(13,43,15,0.7) !important;
    border: 1px solid rgba(109,191,110,0.25) !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(109,191,110,0.3) !important;
    border-radius: 16px !important;
    background: rgba(13,43,15,0.4) !important;
}

[data-testid="stExpander"] {
    background: rgba(13,43,15,0.5) !important;
    border: 1px solid rgba(109,191,110,0.18) !important;
    border-radius: 14px !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(109,191,110,0.2) !important;
    border-radius: 12px !important;
    overflow: hidden;
}

.footer-bar {
    margin-top: 60px;
    padding: 30px;
    text-align: center;
    border-top: 1px solid rgba(109,191,110,0.12);
    color: rgba(245,240,232,0.35) !important;
    font-size: 0.8rem;
    letter-spacing: 0.5px;
}
</style>
"""


# ─────────────────────────────────────────────────────────
# BAGIAN 2: FUNGSI TERAPKAN CSS
# ─────────────────────────────────────────────────────────

def terapkan_css():
    """Inject seluruh CSS tema SDG 15 ke halaman Streamlit."""
    st.markdown(CSS_UTAMA, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# BAGIAN 3: HERO BANNER
# ─────────────────────────────────────────────────────────

def render_hero_banner():
    """Menampilkan banner judul utama dengan tema SDG 15."""
    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #071409 0%, #0f2d12 50%, #162e0e 100%);
        border: 1px solid rgba(109,191,110,0.2);
        border-radius: 20px;
        padding: 50px 40px 40px;
        text-align: center;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
    '>
        <div style='
            position:absolute; top:0; left:0; right:0; bottom:0;
            background:
                radial-gradient(ellipse at 30% 50%, rgba(45,106,48,0.25) 0%, transparent 60%),
                radial-gradient(ellipse at 70% 20%, rgba(168,217,108,0.08) 0%, transparent 50%);
            pointer-events:none;
        '></div>

        <div style='
            display:inline-block;
            background: linear-gradient(90deg, rgba(212,168,67,0.2), rgba(212,168,67,0.1));
            border: 1px solid rgba(212,168,67,0.4);
            border-radius: 50px;
            padding: 6px 18px;
            font-size: 0.75rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #d4a843;
            margin-bottom: 20px;
        '>🌿 SDG 15 · Life on Land · Forest Conservation</div>

        <div style='
            font-family: Playfair Display, serif;
            font-size: 3.2rem;
            font-weight: 900;
            color: #f5f0e8;
            line-height: 1.1;
            margin-bottom: 12px;
        '>Forest<span style='color:#6dbf6e;'>Vision</span></div>

        <div style='
            font-size: 1rem;
            color: rgba(245,240,232,0.6);
            font-weight: 300;
            max-width: 520px;
            margin: 0 auto 24px;
        '>
            Kompresi citra ekosistem hutan berbasis SVD —
            matematika linier untuk pemantauan lingkungan hidup.
        </div>

        <div style='display:flex; justify-content:center; gap:12px; flex-wrap:wrap;'>
            <span style='background:rgba(45,106,48,0.25); border:1px solid rgba(109,191,110,0.3);
                         border-radius:12px; padding:8px 16px; font-size:0.8rem; color:#6dbf6e;'>
                🌲 Dekomposisi Matriks
            </span>
            <span style='background:rgba(45,106,48,0.25); border:1px solid rgba(109,191,110,0.3);
                         border-radius:12px; padding:8px 16px; font-size:0.8rem; color:#6dbf6e;'>
                📊 Analisis Eigen
            </span>
            <span style='background:rgba(45,106,48,0.25); border:1px solid rgba(109,191,110,0.3);
                         border-radius:12px; padding:8px 16px; font-size:0.8rem; color:#6dbf6e;'>
                🗜️ Kompresi Adaptif
            </span>
            <span style='background:rgba(45,106,48,0.25); border:1px solid rgba(109,191,110,0.3);
                         border-radius:12px; padding:8px 16px; font-size:0.8rem; color:#6dbf6e;'>
                🌍 SDG Goal 15
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# BAGIAN 4: KOMPONEN KARTU & METRIK
# ─────────────────────────────────────────────────────────

def render_kartu_statistik(ikon: str, angka: str, label: str):
    """
    Menampilkan satu kartu statistik konteks SDG 15.

    Parameter:
        ikon  : emoji atau simbol
        angka : nilai utama yang ditampilkan besar
        label : deskripsi singkat di bawah angka
    """
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, rgba(13,43,15,0.8), rgba(22,46,14,0.6));
        border: 1px solid rgba(109,191,110,0.2);
        border-radius: 16px;
        padding: 24px 20px;
        text-align: center;
    '>
        <div style='font-size:2rem; margin-bottom:8px;'>{ikon}</div>
        <div style='
            font-family: Playfair Display, serif;
            font-size: 2.2rem;
            font-weight: 700;
            color: #a8d96c;
            line-height: 1;
            margin-bottom: 4px;
        '>{angka}</div>
        <div style='
            font-size: 0.78rem;
            color: rgba(245,240,232,0.55);
            text-transform: uppercase;
            letter-spacing: 1px;
        '>{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_kotak_metrik(nilai: str, label: str):
    """
    Menampilkan satu kotak metrik hasil kompresi
    (energi, k aktif, rasio kompresi, dll).
    """
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, rgba(13,43,15,0.9), rgba(11,35,13,0.8));
        border: 1px solid rgba(109,191,110,0.25);
        border-radius: 14px;
        padding: 20px;
        text-align: center;
    '>
        <div style='
            font-family: Playfair Display, serif;
            font-size: 2.4rem;
            font-weight: 700;
            color: #a8d96c;
        '>{nilai}</div>
        <div style='
            font-size: 0.78rem;
            color: rgba(245,240,232,0.5);
            text-transform: uppercase;
            letter-spacing: 1.5px;
        '>{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_kepala_seksi(teks: str):
    """Menampilkan judul seksi dengan garis dekorasi hijau."""
    st.markdown(f"""
    <p style='
        font-family: Playfair Display, serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #6dbf6e;
        margin-bottom: 4px;
    '>{teks}</p>
    <hr style='
        height: 2px;
        background: linear-gradient(90deg, #4a9e50, transparent);
        border: none;
        margin: 8px 0 20px;
    '>
    """, unsafe_allow_html=True)


def render_keterangan_gambar(teks: str):
    """Teks keterangan kecil di bawah gambar."""
    st.markdown(f"""
    <p style='
        font-size: 0.78rem;
        color: rgba(245,240,232,0.45);
        text-align: center;
        margin-top: 8px;
        letter-spacing: 0.5px;
    '>{teks}</p>
    """, unsafe_allow_html=True)


def render_kotak_insight(k_untuk_90: int, k_untuk_99: int,
                         total_k: int, energi_saat_ini: float, k_aktif: int):
    """Menampilkan kotak insight statistik SVD."""
    st.markdown(f"""
    <div style='
        background: rgba(13,43,15,0.6);
        border: 1px solid rgba(109,191,110,0.25);
        border-radius: 16px;
        padding: 24px;
        margin-top: 8px;
    '>
        <div style='
            font-family: Playfair Display, serif;
            font-size: 1.1rem;
            color: #6dbf6e;
            margin-bottom: 12px;
        '>💡 Insight Statistik</div>
        <div style='display:flex; gap:40px; flex-wrap:wrap;'>
            <div>
                <span style='color:#a8d96c; font-size:1.4rem; font-weight:700;'>{k_untuk_90}</span>
                <br><span style='color:rgba(245,240,232,0.5); font-size:0.8rem;'>k untuk 90% energi</span>
            </div>
            <div>
                <span style='color:#a8d96c; font-size:1.4rem; font-weight:700;'>{k_untuk_99}</span>
                <br><span style='color:rgba(245,240,232,0.5); font-size:0.8rem;'>k untuk 99% energi</span>
            </div>
            <div>
                <span style='color:#a8d96c; font-size:1.4rem; font-weight:700;'>{total_k}</span>
                <br><span style='color:rgba(245,240,232,0.5); font-size:0.8rem;'>Total komponen</span>
            </div>
            <div>
                <span style='color:#d4a843; font-size:1.4rem; font-weight:700;'>{energi_saat_ini:.1f}%</span>
                <br><span style='color:rgba(245,240,232,0.5); font-size:0.8rem;'>Energi saat ini (k={k_aktif})</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    """Menampilkan footer halaman."""
    st.markdown("""
    <div class='footer-bar'>
        🌿 ForestVision SVD · SDG Goal 15: Life on Land · Aljabar Linier × Konservasi Hutan
    </div>
    """, unsafe_allow_html=True)