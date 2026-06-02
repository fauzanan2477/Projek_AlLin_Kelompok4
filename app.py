import streamlit as st
import numpy as np
import pandas as pd

# Mengatur tampilan halaman web
st.set_page_config(page_title="Kalkulator Gizi SPL", layout="centered")

def main():
    st.title("Aplikasi Pemodelan Gizi dengan Aljabar Linier (SPL)")
    st.write("""
    Aplikasi ini mendemonstrasikan penyelesaian **Sistem Persamaan Linier (SPL)** untuk menentukan porsi makanan berdasarkan target nutrisi (SDG 3: *Good Health and Well-being*).
    """)

    # Menampilkan Data Makanan
    st.subheader("Data Kandungan Gizi Makanan (per porsi)")
    data_gizi = {
        "Makanan": ["Nasi (x1)", "Ayam (x2)", "Tempe (x3)"],
        "Karbohidrat (g)": [40, 0, 10],
        "Protein (g)": [4, 15, 10],
        "Lemak (g)": [0, 10, 5]
    }
    df_gizi = pd.DataFrame(data_gizi)
    st.table(df_gizi.set_index("Makanan"))

    st.subheader("Masukkan Target Nutrisi Harian")
    
    # Input dari pengguna
    col1, col2, col3 = st.columns(3)
    with col1:
        target_karbo = st.number_input("Target Karbohidrat (g)", min_value=0, value=200, step=10)
    with col2:
        target_protein = st.number_input("Target Protein (g)", min_value=0, value=50, step=5)
    with col3:
        target_lemak = st.number_input("Target Lemak (g)", min_value=0, value=40, step=5)

    # Eksekusi Perhitungan Matriks
    if st.button("Hitung Porsi Makanan (Metode SPL)", type="primary"):
        # Matriks A (Koefisien Gizi)
        A = np.array([
            [40,  0, 10],  # Baris Karbohidrat
            [ 4, 15, 10],  # Baris Protein
            [ 0, 10,  5]   # Baris Lemak
        ])
        
        # Matriks B (Konstanta / Target)
        B = np.array([target_karbo, target_protein, target_lemak])
        
        try:
            # Penyelesaian Matriks AX = B
            X = np.linalg.solve(A, B)
            
            st.success("Kalkulasi Matriks SPL Berhasil!")
            
            st.subheader("Hasil Kalkulasi Porsi:")
            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric("Porsi Nasi (x1)", f"{X[0]:.2f}")
            res_col2.metric("Porsi Ayam (x2)", f"{X[1]:.2f}")
            res_col3.metric("Porsi Tempe (x3)", f"{X[2]:.2f}")
            
            st.divider()
            
            # Validasi Porsi Negatif (Kelemahan SPL)
            if any(porsi < 0 for porsi in X):
                st.error("⚠️ KESIMPULAN VALIDASI: Terdapat porsi makanan bernilai NEGATIF!")
                st.info("""
                **Analisis:** Secara matematis aljabar jawabannya benar, namun secara fungsionalitas di dunia nyata tidak mungkin memakan porsi minus. 
                Ini membuktikan bahwa SPL murni perlu modifikasi batasan variabel (x ≥ 0) saat diterapkan pada dunia nyata.
                """)
            else:
                st.success("Hasil porsi saat ini logis (tidak ada yang bernilai negatif).")
                
        except np.linalg.LinAlgError:
            st.error("Matriks Singular! Sistem tidak memiliki solusi pasti.")

if __name__ == "__main__":
    main()