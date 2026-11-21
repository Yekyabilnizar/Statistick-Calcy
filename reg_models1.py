"""
reg_models1.py – regresi variabel dummy, seleksi variabel, regularisasi (Ridge, LASSO, Elastic Net, PCR, PLS)
dan regresi robust (M-estimator Huber/Tukey, LTS). Murni numpy + scipy.
"""
import itertools

import numpy as np
import pandas as pd
from scipy import stats

from stats_engine import f4, fmt_p, sig_mark
from reg_core import (ols, coef_table, numeric_frame, build_X, std_result, spec_xy, spec_bar, resid_specs,
                      aic_ols, bic_ols, vif_table)


# ============================================================================
# Regresi dengan variabel dummy
# ============================================================================
def run_dummy(df, y, xs_num, xs_cat, alpha=0.05):
    if not xs_cat:
        raise ValueError("Pilih minimal satu variabel kategorik (dummy).")
    d, X, refs = build_X(df, y, xs_num, xs_cat)
    yv = d[y].values.astype(float)
    n = len(yv)
    Xm = X.values.astype(float)
    o = ols(Xm, yv)
    if o["dfe"] < 1:
        raise ValueError("Data terlalu sedikit dibanding jumlah parameter.")
    names = list(X.columns)
    tbl = coef_table(names, o["beta"], o["se"], "t", o["dfe"], alpha)
    sst = float(((yv - yv.mean()) ** 2).sum())
    ssr = sst - o["rss"]
    dfr = o["rank"] - 1
    Fm = (ssr / dfr) / o["s2"]
    pm = float(stats.f.sf(Fm, dfr, o["dfe"]))
    anova = pd.DataFrame([["Regresi", dfr, f4(ssr), f4(ssr / dfr), f4(Fm), fmt_p(pm), sig_mark(pm)],
                          ["Galat", o["dfe"], f4(o["rss"]), f4(o["s2"]), "", "", ""],
                          ["Total", n - 1, f4(sst), "", "", "", ""]],
                         columns=["Sumber Keragaman", "db", "JK", "KT", "F hitung", "P-value", "Sig."])
    # uji F parsial untuk tiap variabel kategorik (JK tambahan / tipe III)
    prow = []
    for c in xs_cat:
        keep = [i for i, nm in enumerate(names) if not nm.startswith(f"{c}[")]
        o2 = ols(Xm[:, keep], yv)
        dfd = o["rank"] - o2["rank"]
        Fp = ((o2["rss"] - o["rss"]) / dfd) / o["s2"]
        pp = float(stats.f.sf(Fp, dfd, o["dfe"]))
        prow.append([c, dfd, f4(o2["rss"] - o["rss"]), f4(Fp), fmt_p(pp), sig_mark(pp)])
    part = pd.DataFrame(prow, columns=["Variabel kategorik", "db", "JK tambahan", "F parsial", "P-value", "Sig."])
    r2, r2a = 1 - o["rss"] / sst, 1 - (o["rss"] / o["dfe"]) / (sst / (n - 1))
    b = o["beta"]
    eq = "Ŷ = " + " ".join(f"{b[0]:.4f}" if i == 0 else f"{'+' if b[i] >= 0 else '−'} {abs(b[i]):.4f}·{nm}"
                           for i, nm in enumerate(names))
    notes = [f"**Uji simultan:** F = {Fm:.3f}, P = {fmt_p(pm)} → model {'signifikan' if pm < alpha else 'tidak signifikan'}; R² = {r2:.4f}.",
             "Kategori referensi: " + "; ".join(f"{c} = {r}" for c, r in refs.items()) + ". Koefisien dummy = selisih rata-rata Y terhadap referensi (variabel lain tetap)."]
    for _, r_ in part.iterrows():
        notes.append(f"**{r_['Variabel kategorik']}** (uji F parsial): P = {r_['P-value']} → "
                     + ("berpengaruh nyata." if r_["Sig."] != "tn" else "tidak berpengaruh nyata."))
    plots = [spec_xy("Aktual vs Prediksi", "Prediksi", "Aktual",
                     [{"x": o["fit"], "y": yv, "mode": "markers", "name": "Data"},
                      {"x": [float(min(o["fit"].min(), yv.min())), float(max(o["fit"].max(), yv.max()))],
                       "y": [float(min(o["fit"].min(), yv.min())), float(max(o["fit"].max(), yv.max()))],
                       "mode": "lines", "name": "y = x", "dash": "dash"}])]
    for c in xs_cat:
        g = d.groupby(c)[y].agg(["mean", "std", "count"])
        plots.append(spec_bar(f"Rata-rata {y} menurut {c}", c, y, g.index.astype(str), g["mean"], err=(g["std"] / np.sqrt(g["count"])).fillna(0)))
    plots += resid_specs(o["fit"], o["res"])
    return std_result("dummy", "Regresi dengan Variabel Dummy", d,
                      [("n", n), ("R²", f"{r2:.4f}"), ("R² Adjusted", f"{r2a:.4f}"), ("F hitung", f"{Fm:.3f}"),
                       ("P-value (F)", fmt_p(pm)), ("RMSE", f"{np.sqrt(o['s2']):.4f}")],
                      {"Koefisien": tbl, "ANOVA": anova, "Uji F parsial": part,
                       "Nilai aktual & prediksi": pd.DataFrame({"Y aktual": yv, "Prediksi": o["fit"], "Galat": o["res"]}, index=d.index).round(4)},
                      plots, notes=notes, eq=eq, extra={"fitted": o["fit"], "resid": o["res"]})


# ============================================================================
# Seleksi variabel
# ============================================================================
def _rss_subset(X, y, idx, intercept=True):
    Z = np.column_stack([np.ones(len(y)), X[:, idx]]) if intercept else X[:, idx]
    if Z.shape[1] == 0:
        return float(((y - y.mean()) ** 2).sum() if intercept else (y ** 2).sum()), 0
    b = np.linalg.lstsq(Z, y, rcond=None)[0]
    r = y - Z @ b
    return float(r @ r), Z.shape[1]


def _crit(rss, n, k, kind):
    return n * np.log(rss / n) + (2 * k if kind == "AIC" else np.log(n) * k)


def run_selection(df, y, xs, method="stepwise", criterion="AIC", alpha=0.05):
    d = numeric_frame(df, [y] + list(xs))
    n, p = len(d), len(xs)
    if n < p + 3:
        raise ValueError(f"Data terlalu sedikit: n = {n} untuk {p} kandidat variabel.")
    X, yv = d[list(xs)].values.astype(float), d[y].values.astype(float)
    full_rss, _ = _rss_subset(X, yv, list(range(p)))
    steps = []
    sst = float(((yv - yv.mean()) ** 2).sum())

    def score(idx):
        rss, k = _rss_subset(X, yv, idx)
        return _crit(max(rss, 1e-300), n, k, criterion), rss

    if method == "bestsubset":
        if p > 15:
            raise ValueError("Best subset dibatasi maksimum 15 kandidat variabel.")
        s2full = full_rss / (n - p - 1)
        rows = []
        for k in range(0, p + 1):
            best = None
            for idx in itertools.combinations(range(p), k):
                rss, kk = _rss_subset(X, yv, list(idx))
                if best is None or rss < best[0]:
                    best = (rss, idx)
            rss, idx = best
            r2 = 1 - rss / sst
            r2a = 1 - (rss / (n - k - 1)) / (sst / (n - 1)) if n - k - 1 > 0 else np.nan
            cp = rss / s2full - (n - 2 * (k + 1))
            rows.append([k, ", ".join(xs[i] for i in idx) or "(hanya intersep)", r2, r2a, cp,
                         _crit(rss, n, k + 1, "AIC"), _crit(rss, n, k + 1, "BIC"), idx])
        tab = pd.DataFrame(rows, columns=["Jumlah X", "Subset terbaik", "R²", "R² Adjusted", "Mallows Cp", "AIC", "BIC", "_idx"])
        key = {"AIC": "AIC", "BIC": "BIC"}[criterion]
        sel_row = tab.loc[tab[key].idxmin()]
        sel = list(sel_row["_idx"])
        hist = tab.drop(columns="_idx").round(4)
        hist_title = "Subset terbaik untuk tiap ukuran model"
        plots = [spec_xy("Kriteria vs Jumlah Variabel", "Jumlah variabel X", "Nilai kriteria",
                         [{"x": tab["Jumlah X"], "y": tab["AIC"], "mode": "lines+markers", "name": "AIC"},
                          {"x": tab["Jumlah X"], "y": tab["BIC"], "mode": "lines+markers", "name": "BIC"}]),
                 spec_xy("R² Adjusted vs Jumlah Variabel", "Jumlah variabel X", "R² Adjusted",
                         [{"x": tab["Jumlah X"], "y": tab["R² Adjusted"], "mode": "lines+markers", "name": "R² adj"}])]
    else:
        cur = list(range(p)) if method == "backward" else []
        s_cur, _ = score(cur)
        steps.append(["Awal", "-", ", ".join(xs[i] for i in cur) or "(hanya intersep)", s_cur])
        while True:
            cands = []
            if method in ("forward", "stepwise"):
                for j in range(p):
                    if j not in cur:
                        cands.append(("+", j, score(sorted(cur + [j]))[0]))
            if method in ("backward", "stepwise"):
                for j in cur:
                    cands.append(("−", j, score([i for i in cur if i != j])[0]))
            if not cands:
                break
            op, j, sc = min(cands, key=lambda c: c[2])
            if sc >= s_cur - 1e-9:
                break
            cur = sorted(cur + [j]) if op == "+" else [i for i in cur if i != j]
            s_cur = sc
            steps.append([f"Langkah {len(steps)}", f"{op} {xs[j]}", ", ".join(xs[i] for i in cur) or "(hanya intersep)", s_cur])
            if len(steps) > 4 * p + 2:
                break
        sel = cur
        hist = pd.DataFrame(steps, columns=["Langkah", "Perubahan", "Model saat ini", criterion]).round(4)
        hist_title = "Riwayat seleksi"
        plots = [spec_xy("Perjalanan Kriteria selama Seleksi", "Langkah", criterion,
                         [{"x": list(range(len(steps))), "y": [s[3] for s in steps], "mode": "lines+markers", "name": criterion}])]
    if not sel:
        raise ValueError("Tidak ada variabel yang terpilih (model hanya intersep lebih baik menurut kriteria). Coba kriteria lain.")
    names = [xs[i] for i in sel]
    Xs = np.column_stack([np.ones(n), X[:, sel]])
    o = ols(Xs, yv)
    tbl = coef_table(["Intersep"] + names, o["beta"], o["se"], "t", o["dfe"], alpha)
    r2 = 1 - o["rss"] / sst
    r2a = 1 - (o["rss"] / o["dfe"]) / (sst / (n - 1))
    ssr = sst - o["rss"]
    Fm = (ssr / len(sel)) / o["s2"]
    pm = float(stats.f.sf(Fm, len(sel), o["dfe"]))
    ofull = ols(np.column_stack([np.ones(n), X]), yv)
    cmp_ = pd.DataFrame([["Model penuh", p, 1 - ofull["rss"] / sst, 1 - (ofull["rss"] / ofull["dfe"]) / (sst / (n - 1)),
                          _crit(ofull["rss"], n, p + 1, "AIC"), _crit(ofull["rss"], n, p + 1, "BIC")],
                         ["Model terpilih", len(sel), r2, r2a, _crit(o["rss"], n, len(sel) + 1, "AIC"), _crit(o["rss"], n, len(sel) + 1, "BIC")]],
                        columns=["Model", "Jumlah X", "R²", "R² Adjusted", "AIC", "BIC"]).round(4)
    out = [x for x in xs if x not in names]
    b = o["beta"]
    eq = "Ŷ = " + " ".join(f"{b[0]:.4f}" if i == 0 else f"{'+' if b[i] >= 0 else '−'} {abs(b[i]):.4f}·{nm}"
                           for i, nm in enumerate(["Intersep"] + names))
    label = {"forward": "Forward selection", "backward": "Backward elimination", "stepwise": "Stepwise (dua arah)",
             "bestsubset": "Best subset"}[method]
    notes = [f"**{label}** dengan kriteria **{criterion}** memilih {len(sel)} dari {p} variabel: {', '.join(names)}.",
             ("Variabel tidak terpilih: " + ", ".join(out) + ".") if out else "Seluruh variabel dipertahankan.",
             f"**Model terpilih:** R² adjusted = {r2a:.4f} (model penuh {cmp_.iloc[0]['R² Adjusted']:.4f}); uji F: P = {fmt_p(pm)}.",
             "P-value pada koefisien model terpilih cenderung terlalu optimistis karena variabel dipilih dari data yang sama (post-selection inference)."]
    tables = {"Koefisien model terpilih": tbl, hist_title: hist, "Perbandingan dengan model penuh": cmp_}
    if len(sel) >= 2:
        tables["Multikolinearitas (VIF)"] = vif_table(X[:, sel], names)
    return std_result("select", f"Seleksi Variabel – {label}", d,
                      [("n", n), ("Kandidat X", p), ("X terpilih", len(sel)), ("R² Adjusted", f"{r2a:.4f}"),
                       (criterion, f"{_crit(o['rss'], n, len(sel) + 1, criterion):.2f}"), ("P-value (F)", fmt_p(pm))],
                      tables, plots + resid_specs(o["fit"], o["res"]), notes=notes, eq=eq,
                      extra={"selected": names, "fitted": o["fit"], "resid": o["res"]})


# ============================================================================
# Regularisasi
# ============================================================================
def _standardize(X):
    mu, sd = X.mean(0), X.std(0, ddof=1)
    sd = np.where(sd == 0, 1.0, sd)
    return (X - mu) / sd, mu, sd


def _soft(z, g):
    return np.sign(z) * np.maximum(np.abs(z) - g, 0.0)


def coord_descent(Z, yc, lam, l1_ratio, maxit=5000, tol=1e-9, b0=None):
    """min 1/(2n)||y - Zb||² + lam*(l1*||b||1 + (1-l1)/2 ||b||²). Z standar, yc terpusat."""
    n, p = Z.shape
    b = np.zeros(p) if b0 is None else b0.copy()
    r = yc - Z @ b
    cn = (Z ** 2).sum(0) / n
    for it in range(maxit):
        mx = 0.0
        for j in range(p):
            zj = Z[:, j]
            rho = zj @ r / n + cn[j] * b[j]
            bn = _soft(rho, lam * l1_ratio) / (cn[j] + lam * (1 - l1_ratio))
            if bn != b[j]:
                r -= zj * (bn - b[j])
                mx = max(mx, abs(bn - b[j]))
                b[j] = bn
        if mx < tol:
            break
    return b


def ridge_fit(Z, yc, lam):
    n, p = Z.shape
    return np.linalg.solve(Z.T @ Z / n + lam * np.eye(p), Z.T @ yc / n)


def _folds(n, k, seed=1):
    idx = np.random.default_rng(seed).permutation(n)
    return np.array_split(idx, k)


def _cv_path(X, y, fit_fn, grid, k=10):
    """Kembalikan MSE CV (len(grid) × k) dengan standarisasi di dalam lipatan."""
    n = len(y)
    out = np.zeros((len(grid), k))
    for f, te in enumerate(_folds(n, k)):
        tr = np.setdiff1d(np.arange(n), te)
        Z, mu, sd = _standardize(X[tr])
        ym = y[tr].mean()
        Zte = (X[te] - mu) / sd
        b0 = None
        for gi, g in enumerate(grid):
            b = fit_fn(Z, y[tr] - ym, g, b0)
            b0 = b
            out[gi, f] = np.mean((y[te] - ym - Zte @ b) ** 2)
    return out


def _lam_grid_lasso(Z, yc, l1_ratio, m=60):
    lmax = np.max(np.abs(Z.T @ yc)) / len(yc) / max(l1_ratio, 1e-3)
    return np.exp(np.linspace(np.log(lmax), np.log(lmax * 1e-4), m))


def run_regularized(df, y, xs, method="ridge", alpha=0.05, l1_ratio=0.5, lam=None, k_folds=10, n_comp=None):
    d = numeric_frame(df, [y] + list(xs))
    n, p = len(d), len(xs)
    if n < 10:
        raise ValueError("Data terlalu sedikit untuk validasi silang (minimal 10 pengamatan).")
    if p < 2:
        raise ValueError("Metode ini memerlukan minimal 2 variabel independen.")
    X, yv = d[list(xs)].values.astype(float), d[y].values.astype(float)
    k_folds = min(k_folds, n)
    Z, mu, sd = _standardize(X)
    ym = yv.mean()
    yc = yv - ym
    tables, plots, notes = {}, [], []
    label = {"ridge": "Ridge Regression", "lasso": "LASSO", "enet": "Elastic Net", "pcr": "Principal Component Regression (PCR)",
             "pls": "Partial Least Squares (PLS)"}[method]
    ols_b = np.linalg.lstsq(Z, yc, rcond=None)[0]
    extra_kp = []

    if method in ("ridge", "lasso", "enet"):
        l1 = {"ridge": 0.0, "lasso": 1.0, "enet": l1_ratio}[method]
        if method == "ridge":
            grid = np.exp(np.linspace(np.log(100), np.log(1e-4), 60))
            fn = lambda Zt, yt, g, b0: ridge_fit(Zt, yt, g)
        else:
            grid = _lam_grid_lasso(Z, yc, l1)
            fn = lambda Zt, yt, g, b0: coord_descent(Zt, yt, g, l1, b0=b0)
        cv = _cv_path(X, yv, fn, grid, k_folds)
        m_, se_ = cv.mean(1), cv.std(1, ddof=1) / np.sqrt(k_folds)
        i_min = int(np.argmin(m_))
        i_1se = int(np.where(m_ <= m_[i_min] + se_[i_min])[0].min())
        lam_min, lam_1se = grid[i_min], grid[i_1se]
        lam_use = lam if lam else lam_min
        b = fn(Z, yc, lam_use, None)
        path = np.array([fn(Z, yc, g, None) for g in grid]) if method != "ridge" else np.array([ridge_fit(Z, yc, g) for g in grid])
        plots.append(spec_xy("Validasi Silang: MSE vs λ", "log(λ)", "MSE validasi silang",
                             [{"x": np.log(grid), "y": m_, "mode": "lines+markers", "name": "MSE CV"}],
                             vlines=[float(np.log(lam_use)), float(np.log(lam_1se))]))
        plots.append(spec_xy("Lintasan Koefisien (terstandar)", "log(λ)", "Koefisien terstandar",
                             [{"x": np.log(grid), "y": path[:, j], "mode": "lines", "name": xs[j]} for j in range(p)],
                             vlines=[float(np.log(lam_use))]))
        df_eff = float(np.trace(Z @ np.linalg.solve(Z.T @ Z + n * lam_use * np.eye(p), Z.T))) if method == "ridge" else int((b != 0).sum())
        extra_kp = [("λ terpilih (CV)", f"{lam_use:.4g}"), ("λ (aturan 1-SE)", f"{lam_1se:.4g}"),
                    ("Derajat bebas efektif", f"{df_eff:.2f}")]
        extra_t = {"Jalur validasi silang": pd.DataFrame({"λ": grid, "log(λ)": np.log(grid), "MSE CV": m_, "SE": se_}).iloc[::3].round(5)}
        notes.append(f"**λ optimal** (MSE CV minimum, {k_folds}-fold) = {lam_use:.4g}; aturan 1-SE menyarankan λ = {lam_1se:.4g} (model lebih sederhana).")
        if method == "lasso":
            kept = [xs[j] for j in range(p) if b[j] != 0]
            notes.append(f"**LASSO** mempertahankan {len(kept)} dari {p} variabel: {', '.join(kept) or '-'}; "
                         f"koefisien lain dipaksa tepat nol.")
        elif method == "enet":
            notes.append(f"**Elastic Net** (rasio L1 = {l1_ratio}) menyusutkan koefisien; {int((b != 0).sum())} dari {p} variabel tidak nol.")
        else:
            notes.append("**Ridge** menyusutkan semua koefisien mendekati nol tanpa menghilangkannya; efektif mengatasi multikolinearitas.")
    elif method == "pcr":
        U, S, Vt = np.linalg.svd(Z, full_matrices=False)
        scores = Z @ Vt.T
        kmax = min(p, n - 2)

        def fn_pcr(Zt, yt, g, b0):
            Ut, St, Vtt = np.linalg.svd(Zt, full_matrices=False)
            T = Zt @ Vtt.T[:, :int(g)]
            return Vtt.T[:, :int(g)] @ np.linalg.lstsq(T, yt, rcond=None)[0]

        grid = np.arange(1, kmax + 1)
        cv = _cv_path(X, yv, fn_pcr, grid, k_folds)
        m_ = cv.mean(1)
        a = int(grid[int(np.argmin(m_))]) if not n_comp else int(n_comp)
        b = Vt.T[:, :a] @ np.linalg.lstsq(scores[:, :a], yc, rcond=None)[0]
        ev = S ** 2 / (n - 1)
        expl = ev / ev.sum()
        plots.append(spec_xy("Validasi Silang: MSE vs Jumlah Komponen", "Jumlah komponen", "MSE validasi silang",
                             [{"x": grid, "y": m_, "mode": "lines+markers", "name": "MSE CV"}], vlines=[float(a)]))
        plots.append(spec_bar("Ragam yang Dijelaskan per Komponen", "Komponen", "Proporsi ragam",
                              [f"PC{i + 1}" for i in range(p)], expl))
        extra_kp = [("Komponen dipakai", a), ("Ragam dijelaskan", f"{expl[:a].sum() * 100:.1f}%")]
        extra_t = {"Ragam per komponen": pd.DataFrame({"Komponen": [f"PC{i + 1}" for i in range(p)], "Eigenvalue": ev,
                                                       "Proporsi": expl, "Kumulatif": np.cumsum(expl)}).round(4),
                   "Loading komponen": pd.DataFrame(Vt.T[:, :min(a + 1, p)], index=xs, columns=[f"PC{i + 1}" for i in range(min(a + 1, p))]).round(4).reset_index().rename(columns={"index": "Variabel"})}
        notes.append(f"**PCR** memakai {a} komponen utama ({expl[:a].sum() * 100:.1f}% ragam X), dipilih lewat validasi silang.")
        df_eff = a
    else:  # PLS1 (NIPALS)
        def pls_fit(Zt, yt, A):
            Zr, yr = Zt.copy(), yt.copy()
            W, P, Q = [], [], []
            for _ in range(int(A)):
                w = Zr.T @ yr
                nw = np.linalg.norm(w)
                if nw < 1e-12:
                    break
                w /= nw
                t = Zr @ w
                tt = t @ t
                pl = Zr.T @ t / tt
                q = (yr @ t) / tt
                Zr = Zr - np.outer(t, pl)
                yr = yr - q * t
                W.append(w)
                P.append(pl)
                Q.append(q)
            W, P, Q = np.array(W).T, np.array(P).T, np.array(Q)
            return W @ np.linalg.solve(P.T @ W, Q), W, P, Q

        grid = np.arange(1, min(p, n - 2, 12) + 1)
        fn_pls = lambda Zt, yt, g, b0: pls_fit(Zt, yt, g)[0]
        cv = _cv_path(X, yv, fn_pls, grid, k_folds)
        m_ = cv.mean(1)
        a = int(grid[int(np.argmin(m_))]) if not n_comp else int(n_comp)
        b, W, P, Q = pls_fit(Z, yc, a)
        T = Z @ W
        r2x = (T ** 2).sum(0) / (Z ** 2).sum()
        plots.append(spec_xy("Validasi Silang: MSE vs Jumlah Komponen", "Jumlah komponen", "MSE validasi silang",
                             [{"x": grid, "y": m_, "mode": "lines+markers", "name": "MSE CV"}], vlines=[float(a)]))
        vip = np.sqrt(p * ((W ** 2) * ((Q ** 2) * (T ** 2).sum(0))).sum(1) / ((Q ** 2) * (T ** 2).sum(0)).sum())
        plots.append(spec_bar("VIP (Variable Importance in Projection)", "Variabel", "VIP", xs, vip))
        extra_kp = [("Komponen dipakai", a)]
        extra_t = {"VIP": pd.DataFrame({"Variabel": xs, "VIP": vip, "Keterangan": ["Penting (≥ 1)" if v >= 1 else "Kurang penting" for v in vip]}).round(4)}
        notes.append(f"**PLS** memakai {a} komponen laten (dipilih lewat validasi silang). Variabel dengan VIP ≥ 1 paling berperan menjelaskan Y.")
        df_eff = a

    # koefisien pada skala asli
    b_orig = b / sd
    b0_orig = ym - float(mu @ b_orig)
    fit = b0_orig + X @ b_orig
    res = yv - fit
    sst = float(((yv - ym) ** 2).sum())
    r2 = 1 - float(res @ res) / sst
    ols_o = ols(np.column_stack([np.ones(n), X]), yv)
    coef = pd.DataFrame({"Variabel": ["Intersep"] + list(xs),
                         "Koefisien (skala asli)": [b0_orig] + list(b_orig),
                         "Koefisien terstandar": [np.nan] + list(b),
                         "Koefisien OLS": list(ols_o["beta"]),
                         "Penyusutan vs OLS": [np.nan] + [("-" if abs(ols_o["beta"][j + 1]) < 1e-12 else f"{b_orig[j] / ols_o['beta'][j + 1] * 100:.0f}%") for j in range(p)]}).round(4)
    # kinerja CV
    cv_mse = float(m_[np.argmin(m_)]) if method != "ridge" and method != "lasso" and method != "enet" else float(m_[i_min])
    ols_cv = float(np.mean(_cv_path(X, yv, lambda Zt, yt, g, b0: np.linalg.lstsq(Zt, yt, rcond=None)[0], [0], k_folds)))
    perf = pd.DataFrame([["OLS (tanpa regularisasi)", 1 - ols_o["rss"] / sst, np.sqrt(ols_o["rss"] / n), np.sqrt(ols_cv)],
                         [label, r2, np.sqrt(float(res @ res) / n), np.sqrt(cv_mse)]],
                        columns=["Model", "R² (data latih)", "RMSE latih", "RMSE validasi silang"]).round(4)
    notes.append(f"**Kinerja prediksi:** RMSE validasi silang {label} = {np.sqrt(cv_mse):.4f} vs OLS = {np.sqrt(ols_cv):.4f} "
                 f"({'lebih baik' if cv_mse < ols_cv else 'tidak lebih baik'} daripada OLS).")
    notes.append("Koefisien metode regularisasi bersifat bias demi variansi lebih kecil, sehingga tidak disertai uji-t/P-value klasik.")
    tables = {"Koefisien": coef, "Perbandingan dengan OLS": perf, **extra_t,
              "Nilai aktual & prediksi": pd.DataFrame({"Y aktual": yv, "Prediksi": fit, "Galat": res}, index=d.index).round(4)}
    plots += [spec_xy("Aktual vs Prediksi", "Prediksi", "Aktual",
                      [{"x": fit, "y": yv, "mode": "markers", "name": "Data"},
                       {"x": [float(min(fit.min(), yv.min())), float(max(fit.max(), yv.max()))],
                        "y": [float(min(fit.min(), yv.min())), float(max(fit.max(), yv.max()))], "mode": "lines", "name": "y = x", "dash": "dash"}])]
    plots += resid_specs(fit, res)[:2]
    eq = "Ŷ = " + " ".join(f"{b0_orig:.4f}" if j == -1 else f"{'+' if b_orig[j] >= 0 else '−'} {abs(b_orig[j]):.4f}·{xs[j]}" for j in range(-1, p))
    return std_result("reg", f"Regresi {label}", d,
                      [("n", n), ("Jumlah X", p), ("R² (latih)", f"{r2:.4f}"), ("RMSE CV", f"{np.sqrt(cv_mse):.4f}")] + extra_kp,
                      tables, plots, notes=notes, eq=eq,
                      extra={"fitted": fit, "resid": res, "beta": b_orig, "b0": b0_orig, "xs": list(xs)})


# ============================================================================
# Regresi robust
# ============================================================================
def _mad(r):
    return float(np.median(np.abs(r - np.median(r))) / 0.6745)


def _weights(u, psi):
    a = np.abs(u)
    if psi == "huber":
        return np.where(a <= 1.345, 1.0, 1.345 / np.maximum(a, 1e-12))
    return np.where(a < 4.685, (1 - (u / 4.685) ** 2) ** 2, 0.0)  # Tukey bisquare


def m_estimator(X, y, psi="huber", maxit=200, tol=1e-9):
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    for _ in range(maxit):
        r = y - X @ b
        s = max(_mad(r), 1e-12)
        w = _weights(r / s, psi)
        W = w[:, None]
        bn = np.linalg.solve(X.T @ (W * X), X.T @ (w * y))
        if np.max(np.abs(bn - b)) < tol:
            b = bn
            break
        b = bn
    r = y - X @ b
    s = max(_mad(r), 1e-12)
    w = _weights(r / s, psi)
    # kovarians sandwich (Huber)
    u = r / s
    if psi == "huber":
        psi_p = (np.abs(u) <= 1.345).astype(float)
        psi_v = np.clip(u, -1.345, 1.345)
    else:
        a = np.abs(u) < 4.685
        psi_p = a * (1 - (u / 4.685) ** 2) * (1 - 5 * (u / 4.685) ** 2)
        psi_v = a * u * (1 - (u / 4.685) ** 2) ** 2
    n, p = X.shape
    K = 1 + p / n * np.var(psi_p, ddof=1) / max(np.mean(psi_p) ** 2, 1e-12)
    cov = K ** 2 * s ** 2 * (np.sum(psi_v ** 2) / (n - p)) / max(np.mean(psi_p) ** 2, 1e-12) * np.linalg.inv(X.T @ X)
    return b, cov, s, w


def lts_fit(X, y, h=None, n_starts=500, seed=0):
    n, p = X.shape
    h = h or (n + p + 1) // 2
    rng = np.random.default_rng(seed)
    best = (np.inf, None)
    for _ in range(n_starts):
        idx = rng.choice(n, size=min(p + 1, n), replace=False)
        b = np.linalg.lstsq(X[idx], y[idx], rcond=None)[0]
        for _ in range(10):
            r2 = (y - X @ b) ** 2
            sub = np.argsort(r2)[:h]
            bn = np.linalg.lstsq(X[sub], y[sub], rcond=None)[0]
            if np.allclose(bn, b, atol=1e-10):
                break
            b = bn
        obj = np.sort((y - X @ b) ** 2)[:h].sum()
        if obj < best[0]:
            best = (obj, b)
    b = best[1]
    s0 = max(_mad(y - X @ b), 1e-12)  # skala robust (MAD) dari galat sekitar fit LTS
    inl = np.abs(y - X @ b) / s0 <= 2.5
    b2 = np.linalg.lstsq(X[inl], y[inl], rcond=None)[0]
    o = ols(X[inl], y[inl])
    return b2, o, inl, s0


def run_robust(df, y, xs, method="huber", alpha=0.05):
    d = numeric_frame(df, [y] + list(xs))
    n, k = len(d), len(xs)
    if n < k + 5:
        raise ValueError(f"Data terlalu sedikit: n = {n}.")
    X = np.column_stack([np.ones(n), d[list(xs)].values.astype(float)])
    yv = d[y].values.astype(float)
    names = ["Intersep"] + list(xs)
    o = ols(X, yv)
    sst = float(((yv - yv.mean()) ** 2).sum())
    label = {"huber": "M-estimator (Huber)", "bisquare": "M-estimator (Tukey bisquare)", "lts": "LTS (Least Trimmed Squares)"}[method]
    tables, plots = {}, []
    if method in ("huber", "bisquare"):
        b, cov, s, w = m_estimator(X, yv, method)
        se = np.sqrt(np.clip(np.diag(cov), 0, None))
        tbl = coef_table(names, b, se, "t", n - k - 1, alpha)
        resid = yv - X @ b
        fit = X @ b
        flag = w < 0.5
        extra_kp = [("Skala robust (MAD)", f"{s:.4f}"), ("Bobot < 0,5", int(flag.sum()))]
        notes = [f"**{label}** menurunkan bobot pengamatan dengan galat besar (bobot < 0,5 pada {int(flag.sum())} dari {n} pengamatan).",
                 "Galat baku memakai penduga sandwich Huber; uji-t bersifat aproksimasi."]
        outl = pd.DataFrame({"Pengamatan": d.index.astype(str), "Galat": resid, "Galat terstandar (robust)": resid / s,
                             "Bobot": w, "Catatan": np.where(flag, "Outlier (bobot rendah)", "")}).round(4)
        plots.append(spec_bar("Bobot Robust per Pengamatan", "Pengamatan", "Bobot", [str(i) for i in d.index], w))
    else:
        h = (n + k + 2) // 2
        b, o2, inl, s0 = lts_fit(X, yv, h)
        se = o2["se"]
        tbl = coef_table(names, b, se, "t", o2["dfe"], alpha)
        resid = yv - X @ b
        fit = X @ b
        flag = ~inl
        extra_kp = [("Skala LTS", f"{s0:.4f}"), ("Outlier terdeteksi", int(flag.sum()))]
        notes = [f"**LTS** (h = {h} dari {n}) lalu pembobotan ulang: {int(flag.sum())} pengamatan dideteksi sebagai outlier (|galat/skala| > 2,5) dan dikeluarkan dari penaksiran akhir.",
                 "Galat baku dihitung dari OLS pada pengamatan non-outlier (aproksimasi)."]
        outl = pd.DataFrame({"Pengamatan": d.index.astype(str), "Galat": resid, "Galat terstandar (robust)": resid / s0,
                             "Catatan": np.where(flag, "Outlier", "")}).round(4)
        plots.append(spec_bar("Galat Terstandar Robust", "Pengamatan", "Galat / skala LTS", [str(i) for i in d.index], resid / s0))
    cmp_ = pd.DataFrame({"Variabel": names, "OLS": o["beta"], label: b,
                         "Selisih": b - o["beta"]}).round(4)
    cmp_["Perubahan (%)"] = [("-" if abs(o["beta"][i]) < 1e-12 else f"{(b[i] - o['beta'][i]) / abs(o['beta'][i]) * 100:.1f}%") for i in range(k + 1)]
    r2r = 1 - float(((yv - fit) ** 2).sum()) / sst
    big = int(np.argmax(np.abs((b - o["beta"])[1:] / np.maximum(np.abs(o["beta"][1:]), 1e-12)))) + 1 if k else None
    notes.append(f"**Dibanding OLS:** koefisien {names[big]} berubah dari {o['beta'][big]:.4f} menjadi {b[big]:.4f}." if big else "")
    notes = [x for x in notes if x]
    if k == 1:
        g = np.linspace(d[xs[0]].min(), d[xs[0]].max(), 100)
        plots.insert(0, spec_xy(f"Garis Regresi: OLS vs {label}", xs[0], y,
                                [{"x": d[xs[0]].values, "y": yv, "mode": "markers", "name": "Data"},
                                 {"x": g, "y": o["beta"][0] + o["beta"][1] * g, "mode": "lines", "name": "OLS", "dash": "dash"},
                                 {"x": g, "y": b[0] + b[1] * g, "mode": "lines", "name": label}]))
    plots += resid_specs(fit, resid)[:2]
    tables = {"Koefisien": tbl, "Perbandingan dengan OLS": cmp_, "Diagnostik outlier": outl,
              "Nilai aktual & prediksi": pd.DataFrame({"Y aktual": yv, "Prediksi": fit, "Galat": resid}, index=d.index).round(4)}
    eq = "Ŷ = " + " ".join(f"{b[0]:.4f}" if i == 0 else f"{'+' if b[i] >= 0 else '−'} {abs(b[i]):.4f}·{nm}" for i, nm in enumerate(names))
    return std_result("robust", f"Regresi Robust – {label}", d,
                      [("n", n), ("R² (pada data)", f"{r2r:.4f}"), ("R² OLS", f"{1 - o['rss'] / sst:.4f}")] + extra_kp,
                      tables, plots, notes=notes, eq=eq, extra={"fitted": fit, "resid": resid, "flag": flag})
