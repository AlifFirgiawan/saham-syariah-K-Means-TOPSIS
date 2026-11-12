# Dashboard Rekomendasi Saham Syariah JII

Dashboard interaktif hasil integrasi K-Means Clustering, Metode Elbow, Entropy
Weighting, dan TOPSIS untuk rekomendasi saham syariah pada Jakarta Islamic
Index (JII).

## Struktur File

```
dashboard/
├── app.py            -> tampilan dashboard (Streamlit)
├── logic.py           -> logika komputasi (preprocessing, K-Means, Entropy, TOPSIS)
├── Dataset.xlsx        -> data rasio fundamental saham JII 2023-2026
├── requirements.txt    -> daftar pustaka yang dibutuhkan
└── README.md
```

## Cara Menjalankan

1. Install Python 3.10 ke atas.
2. Install seluruh dependency:
   ```
   pip install -r requirements.txt
   ```
3. Jalankan dashboard:
   ```
   streamlit run app.py
   ```
4. Dashboard otomatis terbuka di browser pada `http://localhost:8501`.

## Halaman Dashboard

| Halaman | Isi |
|---|---|
| Beranda | Ringkasan penelitian dan panduan penggunaan |
| Data Saham | Tabel data + filter & pencarian emiten berdasarkan rentang kriteria |
| Elbow & Clustering | Grafik Metode Elbow + slider interaktif jumlah cluster (k) + scatter plot |
| Simulasi Bobot TOPSIS | Perbandingan ranking dengan bobot Entropy vs bobot kustom pengguna |
| Detail Saham | Profil lengkap satu emiten (radar chart rasio fundamental) |

## Deploy ke Streamlit Community Cloud (opsional, untuk sidang)

1. Push folder ini ke repository GitHub (public atau private).
2. Buka [share.streamlit.io](https://share.streamlit.io), hubungkan ke repo tersebut.
3. Pilih `app.py` sebagai entry point, klik Deploy.
4. Kamu akan mendapat link publik yang bisa dibagikan ke dosen penguji.
