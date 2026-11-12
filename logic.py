import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

CRITERIA = ["PER", "PBV", "ROE", "DER", "NPM"]

ARAH_KRITERIA = {
    "PER": "cost",
    "PBV": "cost",
    "ROE": "benefit",
    "DER": "cost",
    "NPM": "benefit",
}

RANDOM_STATE = 42


# =================================================================================
# DATA SELECTION
# =================================================================================
def load_data_rata_rata(file_path: str, sheet_name: str = "Fundamental") -> pd.DataFrame:
    """Mengambil KODE dan kolom RATA-RATA (PER, PBV, ROE, DER, NPM) tiap saham."""
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    kode_saham = df_raw.iloc[2:, 0].dropna().tolist()
    n = len(kode_saham)

    data = df_raw.iloc[2:2 + n, 31:36].astype(float).reset_index(drop=True)
    data.columns = CRITERIA
    data.insert(0, "KODE", kode_saham)
    return data


# =================================================================================
# PRE-PROCESSING
# =================================================================================
def normalisasi_min_max(data: pd.DataFrame) -> np.ndarray:
    """Normalisasi Min-Max agar seluruh kriteria bersakala 0-1 sebelum K-Means."""
    scaler = MinMaxScaler()
    return scaler.fit_transform(data[CRITERIA].values)


# =================================================================================
# DATA MINING: ELBOW + K-MEANS
# =================================================================================
def hitung_wcss_silhouette(X_norm: np.ndarray, k_max: int = 10):
    """Menghitung WCSS dan Silhouette Score untuk k=1..k_max."""
    K_range = list(range(1, k_max + 1))
    wcss = []
    for k in K_range:
        km = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=RANDOM_STATE)
        km.fit(X_norm)
        wcss.append(km.inertia_)

    silhouette = {}
    for k in range(2, k_max):
        km = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=RANDOM_STATE)
        labels = km.fit_predict(X_norm)
        silhouette[k] = silhouette_score(X_norm, labels)

    return K_range, wcss, silhouette


def kmeans_clustering(X_norm: np.ndarray, k: int) -> np.ndarray:
    """Menjalankan K-Means final dengan jumlah cluster k tertentu."""
    kmeans = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=RANDOM_STATE)
    return kmeans.fit_predict(X_norm) + 1


# =================================================================================
# PEMBOBOTAN: METODE ENTROPY
# =================================================================================
def entropy_weighting(data: pd.DataFrame, kriteria: list = CRITERIA) -> pd.Series:
    """Menghitung bobot tiap kriteria secara objektif dengan Metode Entropy."""
    X = data[kriteria].values.astype(float)
    m = X.shape[0]
    k = 1 / np.log(m)

    P = X / X.sum(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        P_lnP = np.where(P > 0, P * np.log(P), 0.0)
    E = -k * np.sum(P_lnP, axis=0)
    d = 1 - E
    w = d / d.sum()

    return pd.Series(w, index=kriteria)


# =================================================================================
# PERANKINGAN: TOPSIS
# =================================================================================
def topsis(data: pd.DataFrame, bobot: pd.Series, kriteria: list = CRITERIA,
           arah: dict = ARAH_KRITERIA) -> pd.DataFrame:
    """Meranking alternatif (saham) menggunakan TOPSIS (Hwang & Yoon, 1981)."""
    X = data[kriteria].values.astype(float)

    penyebut = np.sqrt((X ** 2).sum(axis=0))
    R = X / penyebut
    V = R * bobot.values

    A_plus, A_minus = [], []
    for j, crit in enumerate(kriteria):
        if arah[crit] == "benefit":
            A_plus.append(V[:, j].max())
            A_minus.append(V[:, j].min())
        else:
            A_plus.append(V[:, j].min())
            A_minus.append(V[:, j].max())
    A_plus = np.array(A_plus)
    A_minus = np.array(A_minus)

    D_plus = np.sqrt(((V - A_plus) ** 2).sum(axis=1))
    D_minus = np.sqrt(((V - A_minus) ** 2).sum(axis=1))
    C = D_minus / (D_plus + D_minus)

    hasil = data.copy()
    hasil["D_plus"] = D_plus
    hasil["D_minus"] = D_minus
    hasil["Skor_TOPSIS"] = C
    hasil["Ranking"] = hasil["Skor_TOPSIS"].rank(ascending=False).astype(int)
    return hasil.sort_values("Ranking").reset_index(drop=True)


# =================================================================================
# PEMUATAN DATA TERPADU
# =================================================================================
def load_semua_data(file_path: str) -> pd.DataFrame:
    """Memuat data rata-rata rasio fundamental sebagai data utama."""
    return load_data_rata_rata(file_path)
