"""
backend.py
==========
Semua logika pemrosesan citra dan kompresi SVD.
Tidak ada kode UI di sini — murni perhitungan matematis.
"""

import numpy as np
from PIL import Image


# ─────────────────────────────────────────────────────────
# BAGIAN 1: MEMUAT & MEMPERSIAPKAN GAMBAR
# ─────────────────────────────────────────────────────────

def muat_gambar_grayscale(file_upload) -> np.ndarray:
    """
    Membuka file gambar dan mengonversinya ke mode grayscale.
    Mengembalikan matriks 2D numpy dengan nilai piksel 0–255.
    """
    gambar_pil = Image.open(file_upload).convert('L')
    matriks_gambar = np.array(gambar_pil, dtype=np.float64)
    return matriks_gambar


def muat_gambar_rgb(file_upload) -> np.ndarray:
    """
    Membuka file gambar dan mengonversinya ke mode RGB.
    Mengembalikan tensor 3D numpy (tinggi x lebar x 3 channel).
    """
    gambar_pil = Image.open(file_upload).convert('RGB')
    tensor_gambar = np.array(gambar_pil, dtype=np.float64)
    return tensor_gambar


# ─────────────────────────────────────────────────────────
# BAGIAN 2: DEKOMPOSISI SVD
# ─────────────────────────────────────────────────────────

def hitung_svd_grayscale(matriks: np.ndarray) -> dict:
    """
    Melakukan dekomposisi SVD pada matriks grayscale 2D.

    SVD: A = U * Sigma * V^T

    Return dict berisi:
        - matriks_U     : vektor singular kiri
        - vektor_sigma  : nilai singular (diagonal Sigma)
        - matriks_Vt    : vektor singular kanan (transpos)
        - jumlah_maks_k : jumlah komponen maksimal yang tersedia
    """
    matriks_U, vektor_sigma, matriks_Vt = np.linalg.svd(
        matriks, full_matrices=False
    )
    return {
        "matriks_U":     matriks_U,
        "vektor_sigma":  vektor_sigma,
        "matriks_Vt":    matriks_Vt,
        "jumlah_maks_k": len(vektor_sigma),
    }


def hitung_svd_rgb(tensor: np.ndarray) -> dict:
    """
    Melakukan dekomposisi SVD secara terpisah pada
    setiap channel warna (R, G, B).

    Return dict berisi hasil SVD untuk masing-masing channel,
    serta jumlah_maks_k berdasarkan channel Merah.
    """
    # Pisahkan channel warna
    channel_merah = tensor[:, :, 0]
    channel_hijau = tensor[:, :, 1]
    channel_biru  = tensor[:, :, 2]

    # Hitung SVD tiap channel
    U_merah, sigma_merah, Vt_merah = np.linalg.svd(channel_merah, full_matrices=False)
    U_hijau, sigma_hijau, Vt_hijau = np.linalg.svd(channel_hijau, full_matrices=False)
    U_biru,  sigma_biru,  Vt_biru  = np.linalg.svd(channel_biru,  full_matrices=False)

    return {
        # Channel Merah
        "U_merah":    U_merah,
        "sigma_merah": sigma_merah,
        "Vt_merah":   Vt_merah,
        # Channel Hijau
        "U_hijau":    U_hijau,
        "sigma_hijau": sigma_hijau,
        "Vt_hijau":   Vt_hijau,
        # Channel Biru
        "U_biru":     U_biru,
        "sigma_biru":  sigma_biru,
        "Vt_biru":    Vt_biru,
        # Referensi jumlah komponen maksimal
        "jumlah_maks_k": len(sigma_merah),
    }


# ─────────────────────────────────────────────────────────
# BAGIAN 3: REKONSTRUKSI GAMBAR TERKOMPRESI
# ─────────────────────────────────────────────────────────

def rekonstruksi_grayscale(hasil_svd: dict, k: int) -> np.ndarray:
    """
    Merekonstruksi gambar grayscale dari hasil SVD
    menggunakan hanya k komponen singular pertama.

    Rumus: Ak = U[:, :k] * diag(sigma[:k]) * Vt[:k, :]

    Return matriks uint8 siap ditampilkan sebagai gambar.
    """
    U     = hasil_svd["matriks_U"]
    sigma = hasil_svd["vektor_sigma"]
    Vt    = hasil_svd["matriks_Vt"]

    # Rekonstruksi dengan k komponen
    matriks_hasil = U[:, :k] @ np.diag(sigma[:k]) @ Vt[:k, :]

    # Clip ke rentang valid piksel [0, 255] lalu konversi ke integer
    matriks_hasil = np.clip(matriks_hasil, 0, 255).astype(np.uint8)
    return matriks_hasil


def rekonstruksi_rgb(hasil_svd: dict, k: int) -> np.ndarray:
    """
    Merekonstruksi gambar RGB dari hasil SVD per channel
    menggunakan hanya k komponen singular pertama.

    Return tensor uint8 (tinggi x lebar x 3) siap ditampilkan.
    """
    # Rekonstruksi tiap channel secara terpisah
    channel_merah_hasil = (
        hasil_svd["U_merah"][:, :k]
        @ np.diag(hasil_svd["sigma_merah"][:k])
        @ hasil_svd["Vt_merah"][:k, :]
    )
    channel_hijau_hasil = (
        hasil_svd["U_hijau"][:, :k]
        @ np.diag(hasil_svd["sigma_hijau"][:k])
        @ hasil_svd["Vt_hijau"][:k, :]
    )
    channel_biru_hasil = (
        hasil_svd["U_biru"][:, :k]
        @ np.diag(hasil_svd["sigma_biru"][:k])
        @ hasil_svd["Vt_biru"][:k, :]
    )

    # Gabungkan kembali menjadi tensor RGB
    tensor_hasil = np.stack(
        (channel_merah_hasil, channel_hijau_hasil, channel_biru_hasil),
        axis=2
    )
    tensor_hasil = np.clip(tensor_hasil, 0, 255).astype(np.uint8)
    return tensor_hasil


# ─────────────────────────────────────────────────────────
# BAGIAN 4: KALKULASI STATISTIK & METRIK
# ─────────────────────────────────────────────────────────

def hitung_energi_visual(vektor_sigma: np.ndarray, k: int) -> float:
    """
    Menghitung persentase 'energi visual' yang dipertahankan
    setelah menggunakan k komponen singular.

    Energi = (jumlah sigma[:k]^2 / jumlah sigma^2) * 100%

    Semakin tinggi nilai ini, semakin mirip gambar dengan aslinya.
    """
    energi_total   = np.sum(vektor_sigma ** 2)
    energi_k_komponen = np.sum(vektor_sigma[:k] ** 2)
    persentase_energi  = (energi_k_komponen / energi_total) * 100
    return round(persentase_energi, 4)


def hitung_rasio_kompresi(
    ukuran_asli: int,
    jumlah_baris: int,
    jumlah_kolom: int,
    k: int,
    adalah_rgb: bool = False
) -> float:
    """
    Memperkirakan rasio kompresi dibanding ukuran asli.

    Semakin besar nilainya, semakin besar penghematan ukuran file.
    Nilai 10x artinya file terkompresi ~10x lebih kecil.
    """
    jumlah_channel = 3 if adalah_rgb else 1
    # Ukuran data yang disimpan: k * (baris + kolom + 1) per channel
    ukuran_terkompresi = jumlah_channel * k * (jumlah_baris + jumlah_kolom + 1)
    rasio = ukuran_asli / max(ukuran_terkompresi, 1)
    return round(rasio, 2)


def hitung_energi_kumulatif(vektor_sigma: np.ndarray, batas: int = 100) -> np.ndarray:
    """
    Menghitung kurva energi kumulatif untuk grafik.
    Berguna untuk menentukan k optimal agar mencapai energi target.

    Return array persentase kumulatif sepanjang min(batas, len(sigma)).
    """
    batas_efektif = min(batas, len(vektor_sigma))
    energi_total  = np.sum(vektor_sigma ** 2)
    energi_kumulatif = np.cumsum(vektor_sigma[:batas_efektif] ** 2) / energi_total * 100
    return energi_kumulatif


def cari_k_untuk_target_energi(vektor_sigma: np.ndarray, target_persen: float) -> int:
    """
    Mencari nilai k minimum yang diperlukan untuk mencapai
    persentase energi target (misal 90% atau 99%).

    Berguna untuk insight: 'berapa k yang dibutuhkan untuk 90% kualitas?'
    """
    energi_kumulatif = hitung_energi_kumulatif(vektor_sigma, batas=len(vektor_sigma))
    for indeks, energi in enumerate(energi_kumulatif):
        if energi >= target_persen:
            return indeks + 1  # indeks mulai 0, k mulai 1
    return len(vektor_sigma)  # fallback: butuh semua komponen


def hitung_energi_multi_k(vektor_sigma: np.ndarray, daftar_k: list) -> list:
    """
    Menghitung energi visual untuk setiap nilai k dalam daftar_k.
    Digunakan untuk membuat grafik perbandingan multi-k.

    Return list of float (persentase energi per k).
    """
    return [hitung_energi_visual(vektor_sigma, k) for k in daftar_k]