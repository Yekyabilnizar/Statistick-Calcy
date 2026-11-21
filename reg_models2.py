"""
reg_models2.py – regresi nonparametrik: Kernel, LOESS, Spline, Kuantil, Generalized Additive Model (GAM).
Murni numpy + scipy.
"""
import numpy as np
import pandas as pd
from scipy import stats, optimize

from stats_engine import f4, fmt_p, sig_mark
from reg_core import ols, coef_table, numeric_frame, std_result, spec_xy, spec_bar, resid_specs


# ============================================================================
# Kernel & LOESS (regresi lokal)
# ============================================================================
def _kern(u, kind):
    a = np.abs(u)
    if kind == "gaussian":
        return np.exp(-0.5 * u ** 2)
    if kind == "epanechnikov":
        return np.where(a < 1, 0.75 * (1 - u ** 2), 0.0)
    return np.where(a < 1, (1 - a ** 3) ** 3, 0.0)  # tricube


def local_poly(x, y, x0, h, degree=1, kind="gaussian", return_hat=False):
    """Taksiran regresi polinomial lokal pada titik x0 (array). h: bandwidth (skala x)."""
    n = len(x)
    out = np.zeros(len(x0))
    L = np.zeros((len(x0), n)) if return_hat else None
    for i, t in enumerate(x0):
        hh = h[i] if hasattr(h, "__len__") else h
        w = _kern((x - t) / hh, kind)
        B = np.vander(x - t, degree + 1, increasing=True)
        W = w[:, None]
        A = B.T @ (W * B) + 1e-10 * np.eye(degree + 1)
        row = np.linalg.solve(A, (B * W).T)[0]   # baris pertama = penaksir pada t
        out[i] = row @ y
        if return_hat:
            L[i] = row
    return (out, L) if return_hat else out


def _loo_cv(x, y, h, degree, kind):
    fit, L = local_poly(x, y, x, h, degree, kind, return_hat=True)
    lii = np.clip(np.diag(L), None, 0.999)
    return float(np.mean(((y - fit) / (1 - lii)) ** 2))


def run_kernel(df, x, y, kind="gaussian", degree=1, h=None, alpha=0.05):
    d = numeric_frame(df, [x, y]).sort_values(x)
    xv, yv = d[x].values.astype(float), d[y].values.astype(float)
    n = len(xv)
    if n < 10:
        raise ValueError("Regresi kernel memerlukan minimal 10 pengamatan.")
    rng = xv.max() - xv.min()
    grid = np.exp(np.linspace(np.log(rng / 40), np.log(rng / 1.5), 40)) if kind != "gaussian" else np.exp(np.linspace(np.log(rng / 80), np.log(rng / 3), 40))
    cv = np.array([_loo_cv(xv, yv, g, degree, kind) for g in grid])
    h_opt = float(grid[int(np.argmin(cv))])
    h_use = h or h_opt
    fit, L = local_poly(xv, yv, xv, h_use, degree, kind, return_hat=True)
    res = yv - fit
    tr = float(np.trace(L))
    dfe = max(n - 2 * tr + float(np.trace(L @ L.T)), 1.0)
    s2 = float(res @ res) / dfe
    g = np.linspace(xv.min(), xv.max(), 150)
    fg, Lg = local_poly(xv, yv, g, h_use, degree, kind, return_hat=True)
    se = np.sqrt(s2 * (Lg ** 2).sum(1))
    z = stats.norm.ppf(1 - alpha / 2)
    sst = float(((yv - yv.mean()) ** 2).sum())
    r2 = 1 - float(res @ res) / sst
    lin = ols(np.column_stack([np.ones(n), xv]), yv)
    name = {"gaussian": "Gaussian", "epanechnikov": "Epanechnikov", "tricube": "Tricube"}[kind]
    meth = "Nadaraya-Watson (lokal konstan)" if degree == 0 else "Polinomial lokal derajat " + str(degree)
    plots = [spec_xy(f"Regresi Kernel {name} ({meth})", x, y,
                     [{"x": xv, "y": yv, "mode": "markers", "name": "Data"}, {"x": g, "y": fg, "mode": "lines", "name": f"Kernel (h = {h_use:.3g})"},
                      {"x": g, "y": lin["beta"][0] + lin["beta"][1] * g, "mode": "lines", "name": "Regresi linear", "dash": "dash"}],
                     band={"x": g, "lo": fg - z * se, "hi": fg + z * se, "name": f"CI {int((1 - alpha) * 100)}% (aproksimasi)"}),
             spec_xy("Pemilihan Bandwidth (CV leave-one-out)", "Bandwidth h", "MSE CV", [{"x": grid, "y": cv, "mode": "lines+markers", "name": "CV"}],
                     vlines=[h_opt])]
    plots += resid_specs(fit, res)[:2]
    # uji linearitas (F aproksimasi: linear vs kernel)
    df1 = tr - 2
    Flin = ((lin["rss"] - float(res @ res)) / max(df1, 1e-9)) / s2 if df1 > 0.5 else np.nan
    plin = float(stats.f.sf(Flin, df1, dfe)) if np.isfinite(Flin) else np.nan
    notes = [f"**Bandwidth optimal** (CV leave-one-out) h = {h_opt:.4g}" + (f"; dipakai h = {h_use:.4g}." if h else "."),
             f"**Derajat bebas efektif** model = {tr:.2f} (regresi linear = 2); R² = {r2:.4f} (R² linear = {1 - lin['rss'] / sst:.4f}).",
             ("**Uji kelinearan (aproksimasi):** F = %.3f, P = %s → %s." % (Flin, fmt_p(plin), "hubungan nonlinear nyata, kernel lebih sesuai daripada garis lurus" if plin < alpha else "tidak ada bukti penyimpangan dari linear")) if np.isfinite(Flin) else "",
             "Bandwidth kecil → kurva bergelombang (variansi tinggi); besar → terlalu halus (bias tinggi)."]
    return std_result("np", "Regresi Kernel", d,
                      [("n", n), ("Bandwidth (h)", f"{h_use:.4g}"), ("df efektif", f"{tr:.2f}"), ("R²", f"{r2:.4f}"), ("RMSE", f"{np.sqrt(float(res @ res) / n):.4f}"),
                       ("MSE CV (LOO)", f"{cv.min():.4f}")],
                      {"Perbandingan bandwidth": pd.DataFrame({"h": grid, "MSE CV": cv}).iloc[::2].round(5),
                       "Nilai aktual & prediksi": pd.DataFrame({x: xv, y: yv, "Prediksi": fit, "Galat": res}).round(4)},
                      plots, notes=[n_ for n_ in notes if n_], extra={"fitted": fit, "resid": res})


def run_loess(df, x, y, span=None, degree=2, alpha=0.05, robust_iter=0):
    d = numeric_frame(df, [x, y]).sort_values(x)
    xv, yv = d[x].values.astype(float), d[y].values.astype(float)
    n = len(xv)
    if n < 10:
        raise ValueError("LOESS memerlukan minimal 10 pengamatan.")

    def smooth(xe, spn, yy, rw=None):
        q = max(int(np.ceil(spn * n)), degree + 2)
        out = np.zeros(len(xe))
        Lm = np.zeros((len(xe), n))
        for i, t in enumerate(xe):
            dist = np.abs(xv - t)
            hh = max(np.sort(dist)[min(q, n) - 1], 1e-12)
            w = _kern(dist / hh, "tricube") * (rw if rw is not None else 1.0)
            B = np.vander(xv - t, degree + 1, increasing=True)
            A = B.T @ (w[:, None] * B) + 1e-10 * np.eye(degree + 1)
            row = np.linalg.solve(A, (B * w[:, None]).T)[0]
            out[i] = row @ yy
            Lm[i] = row
        return out, Lm

    spans = np.linspace(0.2, 0.95, 16)
    cvs = []
    for sp in spans:
        f_, L_ = smooth(xv, sp, yv)
        lii = np.clip(np.diag(L_), None, 0.999)
        cvs.append(float(np.mean(((yv - f_) / (1 - lii)) ** 2)))
    sp_opt = float(spans[int(np.argmin(cvs))])
    sp = span or sp_opt
    fit, L = smooth(xv, sp, yv)
    rw = None
    for _ in range(robust_iter):
        r = yv - fit
        s = np.median(np.abs(r)) * 6
        rw = np.where(np.abs(r / s) < 1, (1 - (r / s) ** 2) ** 2, 0.0)
        fit, L = smooth(xv, sp, yv, rw)
    res = yv - fit
    tr = float(np.trace(L))
    dfe = max(n - 2 * tr + float(np.trace(L @ L.T)), 1.0)
    s2 = float(res @ res) / dfe
    g = np.linspace(xv.min(), xv.max(), 150)
    fg, Lg = smooth(g, sp, yv, rw)
    se = np.sqrt(s2 * (Lg ** 2).sum(1))
    z = stats.t.ppf(1 - alpha / 2, dfe)
    sst = float(((yv - yv.mean()) ** 2).sum())
    r2 = 1 - float(res @ res) / sst
    plots = [spec_xy(f"Kurva LOESS (span = {sp:.2f}, derajat {degree})", x, y,
                     [{"x": xv, "y": yv, "mode": "markers", "name": "Data"}, {"x": g, "y": fg, "mode": "lines", "name": "LOESS"}],
                     band={"x": g, "lo": fg - z * se, "hi": fg + z * se, "name": f"CI {int((1 - alpha) * 100)}%"}),
             spec_xy("Pemilihan Span (CV leave-one-out)", "Span", "MSE CV", [{"x": spans, "y": cvs, "mode": "lines+markers", "name": "CV"}], vlines=[sp_opt])]
    plots += resid_specs(fit, res)[:2]
    notes = [f"**Span optimal** (CV LOO) = {sp_opt:.2f}" + (f"; dipakai {sp:.2f}." if span else "."),
             f"**Derajat bebas efektif** = {tr:.2f}; R² = {r2:.4f}; simpangan baku galat ≈ {np.sqrt(s2):.4f}.",
             "Span = proporsi data yang dipakai di tiap titik: kecil → mengikuti data lebih ketat." + (" Iterasi robust (bisquare) diaktifkan untuk meredam outlier." if robust_iter else "")]
    return std_result("np", "Regresi LOESS", d,
                      [("n", n), ("Span", f"{sp:.2f}"), ("df efektif", f"{tr:.2f}"), ("R²", f"{r2:.4f}"), ("RMSE", f"{np.sqrt(float(res @ res) / n):.4f}")],
                      {"Perbandingan span": pd.DataFrame({"Span": spans, "MSE CV": cvs}).round(5),
                       "Nilai aktual & prediksi": pd.DataFrame({x: xv, y: yv, "Prediksi": fit, "Galat": res}).round(4)},
                      plots, notes=notes, extra={"fitted": fit, "resid": res})


# ============================================================================
# Spline regresi
# ============================================================================
def tp_basis(x, knots, degree=3):
    cols = [x ** k for k in range(1, degree + 1)] + [np.maximum(x - kn, 0.0) ** degree for kn in knots]
    return np.column_stack(cols)


def ns_basis(x, knots):
    """Natural cubic spline (basis Hastie-Tibshirani), knot dalam + batas."""
    kn = np.asarray(knots)
    K = len(kn)

    def d(k):
        return (np.maximum(x - kn[k], 0) ** 3 - np.maximum(x - kn[-1], 0) ** 3) / (kn[-1] - kn[k])

    cols = [x] + [d(k) - d(K - 2) for k in range(K - 2)]
    return np.column_stack(cols)


def run_spline(df, x, y, kind="natural", n_knots=None, alpha=0.05):
    d = numeric_frame(df, [x, y]).sort_values(x)
    xv, yv = d[x].values.astype(float), d[y].values.astype(float)
    n = len(xv)
    if n < 12:
        raise ValueError("Regresi spline memerlukan minimal 12 pengamatan.")

    def design(xe, nk):
        if kind == "natural":
            kn = np.quantile(xv, np.linspace(0, 1, nk + 2))
            return np.column_stack([np.ones(len(xe)), ns_basis(xe, kn)]), kn
        kn = np.quantile(xv, np.linspace(0, 1, nk + 2)[1:-1])
        return np.column_stack([np.ones(len(xe)), tp_basis(xe, kn)]), kn

    rows, fits = [], {}
    for nk in range(0, min(10, n // 3)):
        if kind == "natural" and nk < 1:
            continue
        X, _ = design(xv, nk)
        o = ols(X, yv)
        if o["dfe"] <= 1:
            break
        h = np.einsum("ij,jk,ik->i", X, o["XtXi"], X)
        loo = float(np.mean((o["res"] / (1 - np.clip(h, None, 0.999))) ** 2))
        gcv = n * o["rss"] / (n - X.shape[1]) ** 2
        rows.append([nk, X.shape[1], o["rss"] / (n - X.shape[1]) if False else 1 - o["rss"] / float(((yv - yv.mean()) ** 2).sum()), np.sqrt(o["rss"] / n), gcv, loo])
        fits[nk] = X.shape[1]
    tab = pd.DataFrame(rows, columns=["Jumlah knot", "Parameter", "R²", "RMSE", "GCV", "MSE CV (LOO)"]).round(5)
    nk_opt = int(tab.loc[tab["GCV"].idxmin(), "Jumlah knot"])
    nk = n_knots if n_knots is not None else nk_opt
    X, kn = design(xv, nk)
    o = ols(X, yv)
    g = np.linspace(xv.min(), xv.max(), 200)
    Xg, _ = design(g, nk)
    fg = Xg @ o["beta"]
    sg = np.sqrt(np.clip(np.einsum("ij,jk,ik->i", Xg, o["cov"], Xg), 0, None))
    t = stats.t.ppf(1 - alpha / 2, o["dfe"])
    sst = float(((yv - yv.mean()) ** 2).sum())
    r2 = 1 - o["rss"] / sst
    r2a = 1 - (o["rss"] / o["dfe"]) / (sst / (n - 1))
    lin = ols(np.column_stack([np.ones(n), xv]), yv)
    dfn = X.shape[1] - 2
    Fl = ((lin["rss"] - o["rss"]) / dfn) / o["s2"] if dfn > 0 else np.nan
    pl = float(stats.f.sf(Fl, dfn, o["dfe"])) if np.isfinite(Fl) else np.nan
    interior = kn[1:-1] if kind == "natural" else kn
    label = "Natural cubic spline" if kind == "natural" else "Spline kubik (truncated power)"
    plots = [spec_xy(f"{label} dengan {nk} knot", x, y,
                     [{"x": xv, "y": yv, "mode": "markers", "name": "Data"}, {"x": g, "y": fg, "mode": "lines", "name": "Spline"},
                      {"x": g, "y": lin["beta"][0] + lin["beta"][1] * g, "mode": "lines", "name": "Linear", "dash": "dash"}],
                     band={"x": g, "lo": fg - t * sg, "hi": fg + t * sg, "name": f"CI {int((1 - alpha) * 100)}%"},
                     vlines=[float(k) for k in interior]),
             spec_xy("GCV vs Jumlah Knot", "Jumlah knot", "GCV", [{"x": tab["Jumlah knot"], "y": tab["GCV"], "mode": "lines+markers", "name": "GCV"}], vlines=[float(nk_opt)])]
    plots += resid_specs(o["fit"], o["res"])[:2]
    notes = [f"**Jumlah knot optimal** (GCV minimum) = {nk_opt}" + (f"; dipakai {nk}." if n_knots is not None else "."),
             f"**Model:** {label}, {X.shape[1]} parameter; R² = {r2:.4f}, R² adjusted = {r2a:.4f}.",
             ("**Uji kelinearan:** F = %.3f, P = %s → %s." % (Fl, fmt_p(pl), "suku nonlinear nyata (spline lebih baik dari garis lurus)" if pl < alpha else "tidak ada bukti nonlinearitas")) if np.isfinite(Fl) else "",
             "Posisi knot ditempatkan pada kuantil X (garis putus-putus pada grafik)."]
    return std_result("np", f"Regresi Spline – {label}", d,
                      [("n", n), ("Knot", nk), ("Parameter", X.shape[1]), ("R²", f"{r2:.4f}"), ("R² Adjusted", f"{r2a:.4f}"), ("RMSE", f"{np.sqrt(o['s2']):.4f}")],
                      {"Pemilihan jumlah knot": tab, "Posisi knot": pd.DataFrame({"Knot": [f"k{i + 1}" for i in range(len(interior))], x: interior}).round(4),
                       "Nilai aktual & prediksi": pd.DataFrame({x: xv, y: yv, "Prediksi": o["fit"], "Galat": o["res"]}).round(4)},
                      plots, notes=[n_ for n_ in notes if n_], extra={"fitted": o["fit"], "resid": o["res"]})


# ============================================================================
# Regresi kuantil
# ============================================================================
def quantile_fit(X, y, tau):
    n, p = X.shape
    # min tau*sum(u+) + (1-tau)*sum(u-)  s.t. Xb + u+ - u- = y
    c = np.concatenate([np.zeros(2 * p), tau * np.ones(n), (1 - tau) * np.ones(n)])
    A = np.hstack([X, -X, np.eye(n), -np.eye(n)])
    r = optimize.linprog(c, A_eq=A, b_eq=y, bounds=[(0, None)] * (2 * p + 2 * n), method="highs")
    if not r.success:
        raise ValueError("Optimasi regresi kuantil gagal.")
    return r.x[:p] - r.x[p:2 * p]


def run_quantile(df, y, xs, taus=(0.1, 0.25, 0.5, 0.75, 0.9), n_boot=200, alpha=0.05, seed=0):
    d = numeric_frame(df, [y] + list(xs))
    n, k = len(d), len(xs)
    if n < max(15, 3 * (k + 1)):
        raise ValueError("Data terlalu sedikit untuk regresi kuantil.")
    X = np.column_stack([np.ones(n), d[list(xs)].values.astype(float)])
    yv = d[y].values.astype(float)
    names = ["Intersep"] + list(xs)
    rng = np.random.default_rng(seed)
    idxs = [rng.integers(0, n, n) for _ in range(n_boot)]
    rows, B, plots_series = [], {}, []
    for tau in taus:
        b = quantile_fit(X, yv, tau)
        bs = []
        for ix in idxs:
            try:
                bs.append(quantile_fit(X[ix], yv[ix], tau))
            except Exception:
                continue
        bs = np.array(bs)
        se = bs.std(0, ddof=1)
        B[tau] = (b, se)
        for i, nm in enumerate(names):
            z = b[i] / se[i] if se[i] > 0 else np.nan
            pv = 2 * stats.norm.sf(abs(z)) if np.isfinite(z) else np.nan
            lo, hi = np.quantile(bs[:, i], [alpha / 2, 1 - alpha / 2])
            rows.append([f"τ = {tau}", nm, b[i], se[i], z, fmt_p(pv), sig_mark(pv) if np.isfinite(pv) else "", lo, hi])
    tbl = pd.DataFrame(rows, columns=["Kuantil", "Variabel", "Koefisien", "SE (bootstrap)", "z", "P-value", "Sig.",
                                      f"CI {int((1 - alpha) * 100)}% bawah", f"CI {int((1 - alpha) * 100)}% atas"]).round(4)
    o = ols(X, yv)
    plots = []
    if k == 1:
        g = np.linspace(X[:, 1].min(), X[:, 1].max(), 100)
        ser = [{"x": X[:, 1], "y": yv, "mode": "markers", "name": "Data"},
               {"x": g, "y": o["beta"][0] + o["beta"][1] * g, "mode": "lines", "name": "OLS (rata-rata)", "dash": "dash"}]
        for tau in taus:
            ser.append({"x": g, "y": B[tau][0][0] + B[tau][0][1] * g, "mode": "lines", "name": f"τ = {tau}"})
        plots.append(spec_xy(f"Garis Regresi Kuantil ({y} ~ {xs[0]})", xs[0], y, ser))
    for j, nm in enumerate(names[1:], start=1):
        bb = [B[t][0][j] for t in taus]
        ss = [B[t][1][j] for t in taus]
        plots.append(spec_xy(f"Koefisien {nm} menurut Kuantil", "Kuantil (τ)", f"Koefisien {nm}",
                             [{"x": list(taus), "y": bb, "mode": "lines+markers", "name": "Kuantil"},
                              {"x": list(taus), "y": [o["beta"][j]] * len(taus), "mode": "lines", "name": "OLS", "dash": "dash"}],
                             band={"x": list(taus), "lo": [b - 1.96 * s for b, s in zip(bb, ss)], "hi": [b + 1.96 * s for b, s in zip(bb, ss)], "name": "CI 95%"}))
    med = B[0.5][0] if 0.5 in B else B[taus[len(taus) // 2]][0]
    fit = X @ med
    res = yv - fit
    notes = ["**Regresi kuantil** memodelkan kuantil bersyarat Y, bukan hanya rata-rata; koefisien boleh berbeda antar kuantil (heterogenitas efek).",
             f"Galat baku dan CI diperoleh lewat bootstrap ({n_boot} ulangan)."]
    for j, nm in enumerate(names[1:], start=1):
        lo_t, hi_t = taus[0], taus[-1]
        b_lo, b_hi = B[lo_t][0][j], B[hi_t][0][j]
        z = (b_hi - b_lo) / np.sqrt(B[lo_t][1][j] ** 2 + B[hi_t][1][j] ** 2)
        notes.append(f"**{nm}:** efek pada τ = {lo_t} adalah {b_lo:.4f} dan pada τ = {hi_t} adalah {b_hi:.4f} (OLS: {o['beta'][j]:.4f}); "
                     + ("perbedaan antar kuantil nyata (|z| > 1,96), efeknya tidak seragam di seluruh sebaran Y." if abs(z) > 1.96 else "perbedaan antar kuantil tidak nyata."))
    return std_result("quantile", "Regresi Kuantil", d, [("n", n), ("Jumlah X", k), ("Kuantil dihitung", len(taus)), ("Bootstrap", n_boot)],
                      {"Koefisien per kuantil": tbl,
                       "Nilai aktual & prediksi (median)": pd.DataFrame({"Y aktual": yv, "Prediksi median": fit, "Galat": res}, index=d.index).round(4)},
                      plots + resid_specs(fit, res)[:1], notes=notes, extra={"fitted": fit, "resid": res})


# ============================================================================
# GAM: model aditif dengan spline terpenalti (ridge pada suku knot), λ dari GCV
# ============================================================================
def _gam_design(x, nk=8):
    z = (x - x.min()) / (x.max() - x.min() or 1.0)
    kn = np.quantile(z, np.linspace(0, 1, nk + 2)[1:-1])
    B = np.column_stack([z, z ** 2, z ** 3] + [np.maximum(z - k, 0) ** 3 for k in kn])
    return B, kn, (x.min(), x.max() - x.min() or 1.0)


def _gam_basis_new(xn, kn, mn, rg):
    z = (xn - mn) / rg
    return np.column_stack([z, z ** 2, z ** 3] + [np.maximum(z - k, 0) ** 3 for k in kn])


def run_gam(df, y, smooth_xs, linear_xs=(), nk=8, alpha=0.05):
    xs_all = list(smooth_xs) + list(linear_xs)
    d = numeric_frame(df, [y] + xs_all)
    n = len(d)
    yv = d[y].values.astype(float)
    if not smooth_xs:
        raise ValueError("Pilih minimal satu variabel dengan efek halus (smooth).")
    if n < 8 * (len(smooth_xs) + 1):
        raise ValueError("Data terlalu sedikit untuk GAM dengan jumlah variabel ini.")
    cols, pen, blocks, meta = [np.ones(n)], [0.0], {}, {}
    pos = 1
    for v in smooth_xs:
        B, kn, (mn, rg) = _gam_design(d[v].values.astype(float), nk)
        Bc = B - B.mean(0)
        cols += [Bc[:, j] for j in range(B.shape[1])]
        pen += [0.0, 0.0, 0.0] + [1.0] * len(kn)
        blocks[v] = list(range(pos, pos + B.shape[1]))
        meta[v] = (kn, mn, rg, B.mean(0))
        pos += B.shape[1]
    for v in linear_xs:
        cols.append(d[v].values.astype(float))
        pen.append(0.0)
        blocks[v] = [pos]
        pos += 1
    X = np.column_stack(cols)
    P = np.diag(pen)

    def solve(lam):
        A = X.T @ X + lam * P
        Ai = np.linalg.pinv(A)
        H = X @ Ai @ X.T
        beta = Ai @ X.T @ yv
        return beta, H, Ai

    lams = np.exp(np.linspace(np.log(1e-4), np.log(1e4), 40))
    gcv = []
    for lam in lams:
        beta, H, _ = solve(lam)
        r = yv - X @ beta
        gcv.append(n * float(r @ r) / (n - np.trace(H)) ** 2)
    lam = float(lams[int(np.argmin(gcv))])
    beta, H, Ai = solve(lam)
    fit = X @ beta
    res = yv - fit
    edf = float(np.trace(H))
    dfe = n - edf
    s2 = float(res @ res) / dfe
    cov = s2 * Ai @ X.T @ X @ Ai
    sst = float(((yv - yv.mean()) ** 2).sum())
    r2 = 1 - float(res @ res) / sst
    dev_expl = r2
    plots, rows, ptab = [], [], []
    # model linear pembanding
    Xl = np.column_stack([np.ones(n)] + [d[v].values.astype(float) for v in xs_all])
    ol = ols(Xl, yv)
    for v in smooth_xs:
        idx = blocks[v]
        kn, mn, rg, bm = meta[v]
        xg = np.linspace(d[v].min(), d[v].max(), 120)
        Bg = _gam_basis_new(xg, kn, mn, rg) - bm
        f = Bg @ beta[idx]
        sef = np.sqrt(np.clip(np.einsum("ij,jk,ik->i", Bg, cov[np.ix_(idx, idx)], Bg), 0, None))
        t = stats.t.ppf(1 - alpha / 2, dfe)
        bd = np.column_stack([x_ for x_ in [d[v].values.astype(float)]]).ravel()
        Bd = _gam_basis_new(bd, kn, mn, rg) - bm
        part = Bd @ beta[idx]
        plots.append(spec_xy(f"Efek Halus s({v})", v, f"s({v})",
                             [{"x": xg, "y": f, "mode": "lines", "name": f"s({v})"},
                              {"x": bd, "y": part + res, "mode": "markers", "name": "Residual parsial"}],
                             band={"x": xg, "lo": f - t * sef, "hi": f + t * sef, "name": "CI 95%"}, hlines=[0.0]))
        # edf per suku & uji (Wald pendekatan pada blok)
        Hv = X[:, idx] @ Ai[np.ix_(idx, range(X.shape[1]))] @ X.T
        edf_v = float(np.trace(Hv))
        Xr = np.delete(X, idx, axis=1)
        Pr = np.delete(np.delete(P, idx, 0), idx, 1)
        br = np.linalg.pinv(Xr.T @ Xr + lam * Pr) @ Xr.T @ yv
        rr = yv - Xr @ br
        Hr = Xr @ np.linalg.pinv(Xr.T @ Xr + lam * Pr) @ Xr.T
        dfr = n - np.trace(Hr)
        Fv = ((float(rr @ rr) - float(res @ res)) / max(dfr - dfe, 1e-9)) / s2
        pv = float(stats.f.sf(Fv, max(dfr - dfe, 1e-9), dfe))
        # nonlinearitas: bandingkan dengan efek linear v
        lin_cols = [Xl[:, 0]] + [d[w].values.astype(float) for w in xs_all]
        rows.append([f"s({v})", edf_v, Fv, fmt_p(pv), sig_mark(pv)])
        ptab.append(v)
    smooth_tbl = pd.DataFrame(rows, columns=["Suku halus", "edf", "F", "P-value", "Sig."]).round(4)
    if linear_xs:
        lt = []
        for v in linear_xs:
            i = blocks[v][0]
            se_ = np.sqrt(cov[i, i])
            tv = beta[i] / se_
            pv = 2 * stats.t.sf(abs(tv), dfe)
            lt.append([v, beta[i], se_, tv, fmt_p(pv), sig_mark(pv)])
        lin_tbl = pd.DataFrame(lt, columns=["Variabel (linear)", "Koefisien", "Std. Error", "t", "P-value", "Sig."]).round(4)
    else:
        lin_tbl = None
    r2l = 1 - ol["rss"] / sst
    F_cmp = ((ol["rss"] - float(res @ res)) / max(edf - (len(xs_all) + 1), 1e-9)) / s2
    p_cmp = float(stats.f.sf(F_cmp, max(edf - (len(xs_all) + 1), 1e-9), dfe))
    cmp_ = pd.DataFrame([["Regresi linear berganda", len(xs_all) + 1, r2l, np.sqrt(ol["rss"] / n)],
                         ["GAM (spline terpenalti)", edf, r2, np.sqrt(float(res @ res) / n)]],
                        columns=["Model", "df efektif", "R²", "RMSE"]).round(4)
    plots.append(spec_xy("Aktual vs Prediksi", "Prediksi", "Aktual",
                         [{"x": fit, "y": yv, "mode": "markers", "name": "Data"},
                          {"x": [float(min(fit.min(), yv.min())), float(max(fit.max(), yv.max()))],
                           "y": [float(min(fit.min(), yv.min())), float(max(fit.max(), yv.max()))], "mode": "lines", "name": "y = x", "dash": "dash"}]))
    plots += resid_specs(fit, res)[:2]
    notes = [f"**GAM** menjumlahkan efek halus tiap variabel: Y = β₀ + Σ s(Xⱼ) + Σ βₖ·Zₖ; derajat kehalusan dipilih otomatis (GCV, λ = {lam:.3g}).",
             f"**Derajat bebas efektif** total = {edf:.2f}; R² GAM = {r2:.4f} vs regresi linear {r2l:.4f}.",
             f"**GAM vs linear:** F = {F_cmp:.3f}, P = {fmt_p(p_cmp)} → " + ("ada komponen nonlinear nyata; GAM lebih sesuai daripada model linear." if p_cmp < alpha else "model linear sudah memadai.")]
    for _, r_ in smooth_tbl.iterrows():
        notes.append(f"**{r_['Suku halus']}**: edf = {r_['edf']:.2f}, P = {r_['P-value']} → " + ("efek nyata." if r_["Sig."] != "tn" else "efek tidak nyata.")
                     + (" (edf ≈ 1: hampir linear)" if r_["edf"] < 1.5 else ""))
    tables = {"Suku halus": smooth_tbl}
    if lin_tbl is not None:
        tables["Suku linear"] = lin_tbl
    tables["GAM vs regresi linear"] = cmp_
    tables["Nilai aktual & prediksi"] = pd.DataFrame({"Y aktual": yv, "Prediksi": fit, "Galat": res}, index=d.index).round(4)
    return std_result("gam", "Generalized Additive Model (GAM)", d,
                      [("n", n), ("df efektif", f"{edf:.2f}"), ("R²", f"{r2:.4f}"), ("RMSE", f"{np.sqrt(float(res @ res) / n):.4f}"),
                       ("λ (GCV)", f"{lam:.3g}"), ("P (GAM vs linear)", fmt_p(p_cmp))],
                      tables, plots, notes=notes, extra={"fitted": fit, "resid": res})
