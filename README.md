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
| Beranda | Tabel data + filter & pencarian emiten berdasarkan rentang kriteria |
| Elbow & Clustering | Grafik Metode Elbow + slider interaktif jumlah cluster (k) + scatter plot |
| Entropy & TOPSIS | Perbandingan ranking dengan bobot Entropy vs bobot kustom pengguna |
