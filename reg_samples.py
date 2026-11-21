"""reg_samples.py – data contoh untuk seluruh metode regresi."""
import numpy as np
import pandas as pd

ALIAS = {"ridge": "penal", "lasso": "penal", "enet": "penal", "pcr": "penal", "pls": "penal",
         "stepwise": "select", "bestsubset": "select", "lts": "outlier", "robust": "outlier",
         "kernel": "curve", "loess": "curve", "spline": "curve", "gwr": "spatial", "sar": "spatial",
         "sem": "spatial", "ar1": "ts", "arimax": "ts", "diag": "regx", "reg0": "regx"}


def sample_reg(kind):
    kind = ALIAS.get(kind, kind)
    rng = np.random.default_rng(11)
    r = lambda a, k=2: np.round(a, k)
    if kind == "poly":
        x = np.round(np.linspace(0, 10, 30), 2)
        return pd.DataFrame({"X": x, "Y": r(5 + 2 * x - 0.25 * x ** 2 + rng.normal(0, 1, 30))})
    if kind == "nonlin":
        x = np.arange(0, 31.5, 1.5)
        return pd.DataFrame({"Waktu": x, "Respon": r(100 / (1 + np.exp(-0.3 * (x - 15))) + rng.normal(0, 2, len(x)))})
    if kind in ("logit", "probit"):
        n = 150
        umur, inc, edu = rng.uniform(20, 60, n), rng.uniform(2, 20, n), rng.integers(6, 18, n)
        z = -6 + 0.05 * umur + 0.25 * inc + 0.1 * edu
        y = (rng.uniform(size=n) < 1 / (1 + np.exp(-z))).astype(int)
        return pd.DataFrame({"Umur": r(umur, 0), "Pendapatan": r(inc, 1), "Pendidikan": edu, "Beli": y})
    if kind == "multinom":
        n = 180
        x1, x2 = rng.normal(0, 1, n), rng.normal(0, 1, n)
        u = np.column_stack([np.zeros(n), 1.2 * x1 - 0.5 * x2, -0.8 * x1 + 1.3 * x2])
        p = np.exp(u) / np.exp(u).sum(1, keepdims=True)
        y = [("A", "B", "C")[rng.choice(3, p=pi)] for pi in p]
        return pd.DataFrame({"X1": r(x1), "X2": r(x2), "Jenis": y})
    if kind == "ordinal":
        n = 200
        x1, x2 = rng.normal(0, 1, n), rng.normal(0, 1, n)
        lat = 1.0 * x1 - 0.6 * x2 + rng.logistic(size=n)
        y = np.digitize(lat, [-1.5, 0, 1.5]) + 1
        return pd.DataFrame({"X1": r(x1), "X2": r(x2), "Kepuasan": y})
    if kind == "poisson":
        n = 150
        a, b = rng.uniform(0, 2, n), rng.uniform(0, 3, n)
        return pd.DataFrame({"Luas": r(a), "Usia": r(b), "Jumlah": rng.poisson(np.exp(0.3 + 0.8 * a - 0.3 * b))})
    if kind == "negbin":
        n = 150
        a, b = rng.uniform(0, 2, n), rng.uniform(0, 3, n)
        mu = np.exp(0.5 + 0.7 * a - 0.2 * b) * rng.gamma(2.0, 0.5, n)
        return pd.DataFrame({"Luas": r(a), "Usia": r(b), "Jumlah": rng.poisson(mu)})
    if kind == "gamma":
        n = 120
        a, b = rng.uniform(0, 2, n), rng.uniform(0, 3, n)
        mu = np.exp(1 + 0.6 * a - 0.2 * b)
        return pd.DataFrame({"X1": r(a), "X2": r(b), "Biaya": r(rng.gamma(5, mu / 5))})
    if kind == "dummy":
        n = 60
        jenis = rng.choice(["A", "B", "C"], n)
        lok = rng.choice(["Utara", "Selatan"], n)
        dosis = rng.uniform(50, 150, n)
        e = {"A": 0, "B": 3, "C": 6}
        y = 10 + 0.05 * dosis + np.vectorize(e.get)(jenis) + np.where(lok == "Selatan", 2, 0) + rng.normal(0, 1, n)
        return pd.DataFrame({"Jenis_Pupuk": jenis, "Lokasi": lok, "Dosis": r(dosis, 1), "Hasil": r(y)})
    if kind == "regx":
        n = 60
        a, b, c = rng.uniform(1, 5, n), rng.uniform(50, 200, n), rng.uniform(100, 300, n)
        y = 2 + 1.8 * a + 0.03 * b + 0.01 * c + rng.normal(0, .8, n) * (1 + a / 5)
        return pd.DataFrame({"Luas": r(a), "Pupuk": r(b, 1), "Hujan": r(c, 1), "Hasil": r(y)})
    if kind == "select":
        n = 80
        Z = rng.normal(0, 1, (n, 8))
        Z[:, 1] = 0.7 * Z[:, 0] + 0.5 * Z[:, 1]
        y = 3 + 2 * Z[:, 0] - 1.5 * Z[:, 2] + 1.0 * Z[:, 4] + rng.normal(0, 1, n)
        d = pd.DataFrame(r(Z), columns=[f"X{i + 1}" for i in range(8)])
        d["Y"] = r(y)
        return d
    if kind == "penal":
        n, p = 100, 10
        Z = rng.normal(0, 1, (n, p))
        for j in range(1, p):
            Z[:, j] = 0.6 * Z[:, j - 1] + 0.8 * Z[:, j]
        y = 5 + 3 * Z[:, 0] - 2 * Z[:, 2] + 1.5 * Z[:, 5] + 1 * Z[:, 8] + rng.normal(0, 2, n)
        d = pd.DataFrame(r(Z), columns=[f"X{i + 1}" for i in range(p)])
        d["Y"] = r(y)
        return d
    if kind == "outlier":
        n = 40
        x = rng.uniform(0, 10, n)
        y = 3 + 2 * x + rng.normal(0, 1, n)
        y[[3, 11, 25, 33]] += np.array([25, -22, 30, -28])
        x[[3, 25]] = x[[3, 25]] * 0.2
        return pd.DataFrame({"X": r(x), "Y": r(y)})
    if kind == "curve":
        n = 80
        x = np.sort(rng.uniform(0, 10, n))
        return pd.DataFrame({"X": r(x), "Y": r(2 * np.sin(x) + 0.3 * x + rng.normal(0, .4, n))})
    if kind == "gam":
        n = 150
        a, b, c = rng.uniform(0, 10, n), rng.uniform(0, 1, n), rng.normal(0, 1, n)
        y = np.sin(a) * 2 + 4 * (b - 0.5) ** 2 + 0.8 * c + rng.normal(0, .4, n)
        return pd.DataFrame({"X1": r(a), "X2": r(b), "X3": r(c), "Y": r(y)})
    if kind == "quantile":
        n = 200
        x = rng.uniform(0, 5, n)
        return pd.DataFrame({"X": r(x), "Y": r(2 + 1.5 * x + (0.4 + 0.5 * x) * rng.normal(0, 1, n))})
    if kind == "panel":
        N, T = 20, 6
        rows = []
        for i in range(N):
            ai = rng.normal(0, 3)
            for t in range(T):
                x1 = rng.normal(5 + 0.5 * ai, 1)
                x2 = rng.normal(0, 1)
                rows.append([f"P{i + 1:02d}", 2018 + t, 10 + ai + 1.5 * x1 + 0.8 * x2 + rng.normal(0, 1), x1, x2])
        return pd.DataFrame(rows, columns=["Provinsi", "Tahun", "Y", "X1", "X2"]).round(3)
    if kind == "ts":
        n = 80
        x1, x2 = np.cumsum(rng.normal(0, 1, n)) * .3 + 10, rng.normal(0, 1, n)
        e = np.zeros(n)
        for t in range(1, n):
            e[t] = 0.7 * e[t - 1] + rng.normal(0, 1)
        return pd.DataFrame({"Waktu": np.arange(1, n + 1), "X1": r(x1), "X2": r(x2), "Y": r(5 + 1.2 * x1 + 0.8 * x2 + e)})
    if kind == "spatial":
        n = 100
        lon, lat = rng.uniform(0, 10, n), rng.uniform(0, 10, n)
        x1, x2 = rng.normal(0, 1, n), rng.normal(0, 1, n)
        b1 = 1 + 0.3 * lon
        return pd.DataFrame({"Lon": r(lon), "Lat": r(lat), "X1": r(x1), "X2": r(x2),
                             "Y": r(2 + b1 * x1 + 0.5 * x2 + rng.normal(0, 0.6, n))})
    if kind == "mixed":
        rows = []
        for g in range(15):
            a, b = rng.normal(0, 2), rng.normal(0, .4)
            for _ in range(8):
                x = rng.uniform(0, 10)
                rows.append([f"G{g + 1:02d}", x, 10 + a + (1 + b) * x + rng.normal(0, 1)])
        return pd.DataFrame(rows, columns=["Kelompok", "X", "Y"]).round(3)
    if kind == "cox":
        n = 120
        umur, trt, skor = rng.normal(55, 10, n), rng.integers(0, 2, n), rng.normal(0, 1, n)
        lam = 0.02 * np.exp(0.03 * (umur - 55) - 0.8 * trt + 0.5 * skor)
        t = rng.exponential(1 / lam)
        c = rng.uniform(20, 80, n)
        return pd.DataFrame({"Waktu": r(np.minimum(t, c)), "Status": (t <= c).astype(int), "Umur": r(umur, 0),
                             "Perlakuan": trt, "Skor": r(skor)})
    if kind == "tobit":
        n = 150
        x1, x2 = rng.uniform(0, 10, n), rng.normal(0, 1, n)
        lat = -4 + 1.0 * x1 + 1.5 * x2 + rng.normal(0, 2, n)
        return pd.DataFrame({"X1": r(x1), "X2": r(x2), "Y": r(np.maximum(lat, 0))})
    raise KeyError(kind)
