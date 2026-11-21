"""
pages_reg.py – halaman Streamlit untuk metode regresi lanjutan.
Setiap fungsi form_* menampilkan pilihan variabel/parameter, memanggil mesin analisis, lalu mengembalikan hasil standar.
"""
import numpy as np
import pandas as pd
import streamlit as st

import reg_core as rc
import reg_models1 as r1
import reg_models2 as r2
import reg_models3 as r3
from reg_samples import sample_reg
from ui_core import (H, section, form_header, crumb, all_cols, cat_like, num_cols, pick, pick_multi, pick_optional, render_result, safe_run)

# --------------------------------------------------------------------------
# Form per metode. Argumen: (df, alpha, k) dengan k = kunci unik untuk widget.
# --------------------------------------------------------------------------


def _y_xs(df, k, y_want, xs_want, y_label="Variabel dependen (Y)", x_label="Variabel independen (X)", min_x=1):
    num = num_cols(df)
    if len(num) < 2:
        H["n_warn"]("Data memerlukan minimal 2 kolom numerik.")
        return None, None
    c1, c2 = st.columns(2)
    with c1:
        y = pick(y_label, num, f"{k}_y", y_want, -1)
    with c2:
        xs = pick_multi(x_label, [c for c in num if c != y], f"{k}_xs", xs_want)
    if len(xs) < min_x:
        H["n_info"](f"Pilih minimal {min_x} variabel independen.")
        return y, None
    return y, xs


def _xy(df, k, x_want, y_want):
    num = num_cols(df)
    if len(num) < 2:
        H["n_warn"]("Data memerlukan minimal 2 kolom numerik.")
        return None, None
    c1, c2 = st.columns(2)
    with c1:
        x = pick("Variabel independen (X)", num, f"{k}_x", x_want, 0)
    with c2:
        y = pick("Variabel dependen (Y)", [c for c in num if c != x], f"{k}_y", y_want, -1)
    return x, y


def form_dummy(df, a, k):
    num = num_cols(df)
    cats = [c for c in cat_like(df) if c not in ()]
    c1, c2 = st.columns(2)
    y = pick("Variabel dependen (Y)", num, f"{k}_y", "Hasil", -1)
    xn = pick_multi("Variabel numerik (X)", [c for c in num if c != y], f"{k}_xn", ["Dosis"])
    xc = pick_multi("Variabel kategorik (dijadikan dummy)", [c for c in cats if c != y and c not in xn], f"{k}_xc",
                    ["Jenis_Pupuk", "Lokasi"])
    if not xn and not xc:
        H["n_info"]("Pilih minimal satu variabel independen.")
        return None
    return safe_run(r1.run_dummy, df, y, xn, xc, alpha=a)


def form_poly(df, a, k):
    x, y = _xy(df, k, "X", "Y")
    if x is None:
        return None
    deg = st.slider("Derajat polinomial", 1, 6, 2, key=f"{k}_deg")
    cen = st.checkbox("Pusatkan X (kurangi multikolinearitas)", True, key=f"{k}_cen")
    return safe_run(rc.run_polynomial, df, x, y, deg, cen, a)


def form_diag(df, a, k):
    y, xs = _y_xs(df, k, "Hasil", ["Luas", "Pupuk", "Hujan"])
    if xs is None:
        return None
    ic = st.checkbox("Sertakan intersep (konstanta)", True, key=f"{k}_ic",
                     help="Hilangkan centang untuk regresi melalui titik asal (tanpa intersep).")
    return safe_run(rc.run_diagnostics, df, y, xs, ic, a)


def form_nonlin(df, a, k):
    x, y = _xy(df, k, "Waktu", "Respon")
    if x is None:
        return None
    mdl = st.selectbox("Model nonlinear", list(rc.NL_MODELS.keys()), index=3, key=f"{k}_m",
                       help="Seluruh model dibandingkan pada hasil; model terpilih ditampilkan lebih rinci.")
    return safe_run(rc.run_nonlinear, df, x, y, mdl, a)


def _glm_form(kind):
    def f(df, a, k):
        cols = all_cols(df)
        num = num_cols(df)
        ywant = {"logit": "Beli", "probit": "Beli", "poisson": "Jumlah", "negbin": "Jumlah", "gamma": "Biaya"}[kind]
        y = pick("Variabel dependen (Y)", cols, f"{k}_y", ywant, -1)
        cats = [c for c in cat_like(df) if c != y]
        xn = pick_multi("Variabel numerik (X)", [c for c in num if c != y], f"{k}_xn", [c for c in num if c != y][:4])
        xc = pick_multi("Variabel kategorik (dummy)", [c for c in cats if c not in xn], f"{k}_xc")
        if not xn and not xc:
            H["n_info"]("Pilih minimal satu variabel independen.")
            return None
        cut = 0.5
        if kind in ("logit", "probit"):
            cut = st.slider("Titik potong klasifikasi", 0.1, 0.9, 0.5, 0.05, key=f"{k}_cut")
        return safe_run(rc.run_glm, df, y, xn, xc, kind, a, cut)
    return f


def form_multinom(df, a, k):
    cols = all_cols(df)
    num = num_cols(df)
    y = pick("Variabel dependen kategorik (≥ 3 kelas)", cols, f"{k}_y", "Jenis", -1)
    xn = pick_multi("Variabel numerik (X)", [c for c in num if c != y], f"{k}_xn", ["X1", "X2"])
    xc = pick_multi("Variabel kategorik (dummy)", [c for c in cat_like(df) if c != y and c not in xn], f"{k}_xc")
    if not xn and not xc:
        H["n_info"]("Pilih minimal satu variabel independen.")
        return None
    return safe_run(rc.run_multinomial, df, y, xn, xc, a)


def form_ordinal(df, a, k):
    y, xs = _y_xs(df, k, "Kepuasan", ["X1", "X2"], "Variabel dependen ordinal (kategori terurut, mis. 1–4)")
    if xs is None:
        return None
    return safe_run(rc.run_ordinal, df, y, xs, a)


def form_select(df, a, k):
    y, xs = _y_xs(df, k, "Y", [f"X{i}" for i in range(1, 9)], min_x=2)
    if xs is None:
        return None
    c1, c2 = st.columns(2)
    m = c1.selectbox("Metode seleksi", ["stepwise", "forward", "backward", "bestsubset"], key=f"{k}_m",
                     format_func=lambda v: {"stepwise": "Stepwise (dua arah)", "forward": "Forward selection",
                                            "backward": "Backward elimination", "bestsubset": "Best subset (semua kombinasi)"}[v])
    crit = c2.selectbox("Kriteria", ["AIC", "BIC"], key=f"{k}_c")
    if m == "bestsubset" and len(xs) > 12:
        H["n_warn"]("Best subset dibatasi ≤ 12 variabel; kurangi pilihan variabel atau gunakan stepwise.")
        return None
    return safe_run(r1.run_selection, df, y, xs, m, crit, a)


def form_penal(method):
    def f(df, a, k):
        y, xs = _y_xs(df, k, "Y", [f"X{i}" for i in range(1, 11)], min_x=2)
        if xs is None:
            return None
        l1, lam, ncomp = 0.5, None, None
        c1, c2 = st.columns(2)
        if method == "enet":
            l1 = c1.slider("Rasio L1 (0 = Ridge, 1 = LASSO)", 0.05, 0.95, 0.5, 0.05, key=f"{k}_l1")
        if method in ("ridge", "lasso", "enet"):
            auto = c2.checkbox("Pilih λ otomatis (validasi silang)", True, key=f"{k}_auto")
            if not auto:
                lam = c2.number_input("Nilai λ", min_value=0.0001, value=0.1, format="%.4f", key=f"{k}_lam")
        else:
            ncomp = c1.slider("Jumlah komponen (0 = otomatis lewat CV)", 0, max(1, min(len(xs), 10)), 0, key=f"{k}_nc") or None
        return safe_run(r1.run_regularized, df, y, xs, method, a, l1, lam, 10, ncomp)
    return f


def form_robust(method):
    def f(df, a, k):
        y, xs = _y_xs(df, k, "Y", ["X"])
        if xs is None:
            return None
        return safe_run(r1.run_robust, df, y, xs, method, a)
    return f


def form_kernel(df, a, k):
    x, y = _xy(df, k, "X", "Y")
    if x is None:
        return None
    c1, c2, c3 = st.columns(3)
    kind = c1.selectbox("Fungsi kernel", ["gaussian", "epanechnikov", "tricube"], key=f"{k}_k")
    deg = c2.selectbox("Derajat polinomial lokal", [0, 1, 2], index=1, key=f"{k}_dg",
                       format_func=lambda v: {0: "0 (Nadaraya-Watson)", 1: "1 (linear lokal)", 2: "2 (kuadratik lokal)"}[v])
    auto = c3.checkbox("Bandwidth otomatis (CV)", True, key=f"{k}_auto")
    h = None
    if not auto:
        h = st.number_input("Bandwidth h (satuan X)", min_value=0.0001, value=1.0, key=f"{k}_h")
    return safe_run(r2.run_kernel, df, x, y, kind, deg, h, a)


def form_loess(df, a, k):
    x, y = _xy(df, k, "X", "Y")
    if x is None:
        return None
    c1, c2, c3 = st.columns(3)
    auto = c1.checkbox("Span otomatis (CV)", True, key=f"{k}_auto")
    span = None if auto else c1.slider("Span", 0.1, 1.0, 0.5, 0.05, key=f"{k}_sp")
    deg = c2.selectbox("Derajat lokal", [1, 2], index=1, key=f"{k}_dg")
    rob = c3.slider("Iterasi robust (LOWESS)", 0, 4, 0, key=f"{k}_rb")
    return safe_run(r2.run_loess, df, x, y, span, deg, a, rob)


def form_spline(df, a, k):
    x, y = _xy(df, k, "X", "Y")
    if x is None:
        return None
    c1, c2 = st.columns(2)
    kind = c1.selectbox("Jenis spline", ["natural", "truncated"], key=f"{k}_k",
                        format_func=lambda v: {"natural": "Natural cubic spline", "truncated": "Regression spline (truncated power)"}[v])
    auto = c2.checkbox("Jumlah knot otomatis", True, key=f"{k}_auto")
    nk = None if auto else c2.slider("Jumlah knot", 1, 12, 4, key=f"{k}_nk")
    return safe_run(r2.run_spline, df, x, y, kind, nk, a)


def form_quantile(df, a, k):
    y, xs = _y_xs(df, k, "Y", ["X"])
    if xs is None:
        return None
    taus = st.multiselect("Kuantil (τ)", [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95], default=[0.1, 0.25, 0.5, 0.75, 0.9], key=f"{k}_tau")
    nb = st.slider("Ulangan bootstrap (galat baku)", 50, 500, 100, 50, key=f"{k}_nb")
    if not taus:
        H["n_info"]("Pilih minimal satu kuantil.")
        return None
    return safe_run(r2.run_quantile, df, y, xs, tuple(sorted(taus)), nb, a)


def form_gam(df, a, k):
    num = num_cols(df)
    if len(num) < 2:
        H["n_warn"]("Data memerlukan minimal 2 kolom numerik.")
        return None
    y = pick("Variabel dependen (Y)", num, f"{k}_y", "Y", -1)
    rest = [c for c in num if c != y]
    sm = pick_multi("Variabel dengan efek mulus (smooth) s(X)", rest, f"{k}_sm", ["X1", "X2"])
    ln = pick_multi("Variabel dengan efek linear", [c for c in rest if c not in sm], f"{k}_ln", ["X3"])
    nk = st.slider("Basis per smooth (fleksibilitas maksimum)", 4, 15, 8, key=f"{k}_nk")
    if not sm:
        H["n_info"]("Pilih minimal satu variabel smooth.")
        return None
    return safe_run(r2.run_gam, df, y, sm, ln, nk, a)


def form_panel(df, a, k):
    cols = all_cols(df)
    num = num_cols(df)
    c1, c2 = st.columns(2)
    ent = c1.selectbox("Kolom entitas/individu", cols, index=cols.index("Provinsi") if "Provinsi" in cols else 0, key=f"{k}_e")
    tim = c2.selectbox("Kolom waktu", [c for c in cols if c != ent], index=0, key=f"{k}_t") if len(cols) > 1 else None
    pool = [c for c in num if c not in (ent, tim)]
    if len(pool) < 2:
        H["n_warn"]("Data memerlukan kolom Y dan minimal satu X numerik di luar kolom entitas/waktu.")
        return None
    y = pick("Variabel dependen (Y)", pool, f"{k}_y", "Y", 0)
    xs = pick_multi("Variabel independen (X)", [c for c in pool if c != y], f"{k}_xs", ["X1", "X2"])
    if not xs:
        H["n_info"]("Pilih minimal satu variabel independen.")
        return None
    return safe_run(r3.run_panel, df, y, xs, ent, tim, a)


def form_ts(df, a, k):
    cols = all_cols(df)
    num = num_cols(df)
    tim = pick_optional("Kolom waktu (untuk pengurutan, opsional)", cols, f"{k}_t", "Waktu")
    pool = [c for c in num if c != tim]
    y = pick("Variabel dependen (Y)", pool, f"{k}_y", "Y", -1)
    xs = pick_multi("Variabel eksogen (X)", [c for c in pool if c != y], f"{k}_xs", ["X1", "X2"])
    c1, c2, c3 = st.columns(3)
    p = c1.number_input("Orde AR (p)", 0, 4, 1, key=f"{k}_p")
    d = c2.number_input("Diferensiasi (d)", 0, 2, 0, key=f"{k}_d")
    q = c3.number_input("Orde MA (q)", 0, 4, 0, key=f"{k}_q")
    return safe_run(r3.run_arimax, df, y, xs, int(p), int(d), int(q), tim, a)


def form_spatial(kind):
    def f(df, a, k):
        num = num_cols(df)
        if len(num) < 4:
            H["n_warn"]("Data spasial memerlukan koordinat (2 kolom), Y, dan minimal satu X.")
            return None
        c1, c2 = st.columns(2)
        lon = c1.selectbox("Koordinat X (bujur/Lon)", num, index=num.index("Lon") if "Lon" in num else 0, key=f"{k}_lo")
        lat = c2.selectbox("Koordinat Y (lintang/Lat)", [c for c in num if c != lon],
                           index=([c for c in num if c != lon].index("Lat") if "Lat" in num else 0), key=f"{k}_la")
        pool = [c for c in num if c not in (lon, lat)]
        if len(pool) < 2:
            H["n_warn"]("Perlu kolom Y dan minimal satu X selain koordinat.")
            return None
        y = pick("Variabel dependen (Y)", pool, f"{k}_y", "Y", -1)
        xs = pick_multi("Variabel independen (X)", [c for c in pool if c != y], f"{k}_xs", ["X1", "X2"])
        if not xs:
            H["n_info"]("Pilih minimal satu variabel independen.")
            return None
        if kind == "gwr":
            auto = st.checkbox("Bandwidth otomatis (validasi silang)", True, key=f"{k}_auto")
            bw = None if auto else st.slider("Jumlah tetangga terdekat", len(xs) + 5, max(len(xs) + 6, len(df)), min(30, len(df)), key=f"{k}_bw")
            return safe_run(r3.run_gwr, df, y, xs, lon, lat, bw, a)
        c3, c4 = st.columns(2)
        wk = c3.selectbox("Matriks bobot spasial", ["knn", "invdist"], key=f"{k}_w",
                          format_func=lambda v: {"knn": "k tetangga terdekat", "invdist": "Inverse jarak kuadrat"}[v])
        kn = c4.slider("k tetangga", 3, 15, 5, key=f"{k}_kn") if wk == "knn" else 5
        return safe_run(r3.run_spatial, df, y, xs, lon, lat, kind, kn, wk, a)
    return f


def form_mixed(df, a, k):
    cols = all_cols(df)
    num = num_cols(df)
    grp = pick("Kolom kelompok (efek acak)", cols, f"{k}_g", "Kelompok", 0)
    pool = [c for c in num if c != grp]
    if len(pool) < 2:
        H["n_warn"]("Data memerlukan kolom Y dan minimal satu X numerik.")
        return None
    y = pick("Variabel dependen (Y)", pool, f"{k}_y", "Y", -1)
    xs = pick_multi("Efek tetap (X)", [c for c in pool if c != y], f"{k}_xs", ["X"])
    if not xs:
        H["n_info"]("Pilih minimal satu efek tetap.")
        return None
    sl = pick_optional("Slope acak untuk variabel (opsional)", xs, f"{k}_sl")
    return safe_run(r3.run_mixed, df, y, xs, grp, sl, a)


def form_cox(df, a, k):
    cols = all_cols(df)
    num = num_cols(df)
    c1, c2 = st.columns(2)
    t = c1.selectbox("Waktu hingga kejadian/sensor", num, index=num.index("Waktu") if "Waktu" in num else 0, key=f"{k}_t")
    ev_opts = [c for c in cols if c != t]
    ev = c2.selectbox("Status (1 = kejadian, 0 = tersensor)", ev_opts, index=ev_opts.index("Status") if "Status" in ev_opts else 0, key=f"{k}_e")
    rest = [c for c in cols if c not in (t, ev)]
    xn = pick_multi("Kovariat numerik", [c for c in rest if c in num], f"{k}_xn", ["Umur", "Skor"])
    xc = pick_multi("Kovariat kategorik (dummy)", [c for c in rest if c in cat_like(df) and c not in xn], f"{k}_xc", ["Perlakuan"])
    if not xn and not xc:
        H["n_info"]("Pilih minimal satu kovariat.")
        return None
    return safe_run(r3.run_cox, df, t, ev, xn, xc, a)


def form_tobit(df, a, k):
    y, xs = _y_xs(df, k, "Y", ["X1", "X2"])
    if xs is None:
        return None
    c1, c2 = st.columns(2)
    lo_on = c1.checkbox("Sensor kiri (batas bawah)", True, key=f"{k}_lo")
    lo = c1.number_input("Batas bawah", value=0.0, key=f"{k}_lov") if lo_on else None
    hi_on = c2.checkbox("Sensor kanan (batas atas)", False, key=f"{k}_hi")
    hi = c2.number_input("Batas atas", value=float(pd.to_numeric(df[y], errors="coerce").max()), key=f"{k}_hiv") if hi_on else None
    if lo is None and hi is None:
        H["n_info"]("Aktifkan minimal satu batas sensor.")
        return None
    return safe_run(r3.run_tobit, df, y, xs, lo, hi, a)


# --------------------------------------------------------------------------
# Registri: grup -> daftar (kunci, label, sampel, form, judul, deskripsi, tag)
# --------------------------------------------------------------------------
def M(key, label, sample, form, desc, tags):
    return dict(key=key, label=label, sample=sample, form=form, desc=desc, tags=tags)


REG_GROUPS = {
    "Dasar": [
        M("dummy", "Regresi dengan Variabel Dummy", "dummy", form_dummy,
          "Regresi dengan prediktor numerik dan kategorik; kategori diubah menjadi variabel dummy dengan kategori pertama sebagai referensi.",
          ["Dummy", "Referensi", "Koefisien per kategori"]),
        M("poly", "Regresi Polinomial", "poly", form_poly,
          "Model kurva berderajat tinggi dengan uji kenaikan derajat, pita kepercayaan, dan pemilihan derajat berdasarkan AIC/BIC.",
          ["Derajat 1–6", "AIC · BIC", "Pita kepercayaan"]),
        M("diag", "Diagnostik & Regresi Tanpa Intersep", "diag", form_diag,
          "Uji asumsi lengkap: normalitas, heteroskedastisitas, autokorelasi, multikolinearitas (VIF), serta pengamatan berpengaruh (Cook's D, leverage). Mendukung regresi melalui titik asal.",
          ["Shapiro · JB · AD", "BP · White · Glejser", "DW · BG", "VIF · Cook's D"]),
    ],
    "Nonlinear": [
        M("nonlin", "Regresi Nonlinear", "nonlin", form_nonlin,
          "Eksponensial, logaritmik, pangkat, logistik (pertumbuhan), Michaelis-Menten, dan Gompertz dengan perbandingan seluruh model.",
          ["6 model", "Nonlinear least squares", "Perbandingan AIC"]),
    ],
    "GLM": [
        M("logit", "Regresi Logistik Biner", "logit", _glm_form("logit"),
          "Model peluang kejadian biner: odds ratio, uji Wald dan LR, Hosmer-Lemeshow, tabel klasifikasi, serta kurva ROC/AUC.",
          ["Odds ratio", "ROC · AUC", "Hosmer-Lemeshow"]),
        M("probit", "Regresi Probit", "probit", _glm_form("probit"),
          "Model biner dengan fungsi hubung normal baku; hasil klasifikasi dan kecocokan model.", ["Probit", "ROC · AUC"]),
        M("multinom", "Regresi Logistik Multinomial", "multinom", form_multinom,
          "Variabel respon nominal dengan tiga kelas atau lebih; kelas pertama sebagai referensi.", ["Nominal ≥ 3 kelas", "Odds ratio relatif"]),
        M("ordinal", "Regresi Logistik Ordinal", "ordinal", form_ordinal,
          "Respon berskala berurutan (proportional odds): koefisien, ambang (threshold), odds ratio, dan uji kecocokan.", ["Proportional odds", "Threshold"]),
        M("poisson", "Regresi Poisson", "poisson", _glm_form("poisson"),
          "Data cacahan (count): incidence rate ratio, uji overdispersi, dan kecocokan deviance.", ["IRR", "Overdispersi"]),
        M("negbin", "Regresi Binomial Negatif", "negbin", _glm_form("negbin"),
          "Data cacahan dengan overdispersi; parameter dispersi diduga bersama koefisien.", ["IRR", "Dispersi α"]),
        M("gamma", "Regresi Gamma", "gamma", _glm_form("gamma"),
          "Respon kontinu positif dan condong ke kanan (biaya, lama waktu) dengan fungsi hubung log.", ["Link log", "Respon positif"]),
    ],
    "Seleksi & Regularisasi": [
        M("select", "Seleksi Variabel", "select", form_select,
          "Forward, backward, stepwise, dan best subset berdasarkan AIC atau BIC, lengkap dengan jejak langkah dan perbandingan model.",
          ["Forward · Backward", "Stepwise", "Best subset"]),
        M("ridge", "Regresi Ridge", "penal", form_penal("ridge"), "Penyusutan koefisien L2 untuk multikolinearitas; λ dipilih lewat validasi silang.", ["L2", "Validasi silang"]),
        M("lasso", "Regresi LASSO", "penal", form_penal("lasso"), "Penyusutan L1 yang sekaligus menyeleksi variabel (koefisien menjadi tepat nol).", ["L1", "Seleksi variabel"]),
        M("enet", "Elastic Net", "penal", form_penal("enet"), "Kombinasi penalti L1 dan L2 untuk prediktor yang saling berkorelasi.", ["L1 + L2"]),
        M("pcr", "Principal Component Regression (PCR)", "penal", form_penal("pcr"), "Regresi pada komponen utama untuk mengatasi multikolinearitas.", ["PCA", "Komponen utama"]),
        M("pls", "Partial Least Squares (PLS)", "penal", form_penal("pls"), "Regresi pada komponen yang memaksimalkan kovarians dengan Y (algoritma NIPALS).", ["NIPALS", "Komponen laten"]),
    ],
    "Robust & Nonparametrik": [
        M("huber", "Regresi Robust – M-estimator Huber", "outlier", form_robust("huber"), "Mengurangi pengaruh pencilan dengan pembobotan Huber (IRLS) dan galat baku sandwich.", ["Huber", "Tahan pencilan"]),
        M("bisquare", "Regresi Robust – Tukey Bisquare", "outlier", form_robust("bisquare"), "M-estimator redescending yang membuang pengaruh pencilan ekstrem.", ["Bisquare"]),
        M("lts", "Regresi Robust – Least Trimmed Squares (LTS)", "outlier", form_robust("lts"), "Estimator dengan titik runtuh tinggi (≈ 50%) lewat pemangkasan residu terbesar.", ["Breakdown 50%", "Deteksi pencilan"]),
        M("kernel", "Regresi Kernel", "curve", form_kernel, "Regresi nonparametrik berbobot kernel dengan pemilihan bandwidth otomatis.", ["Nadaraya-Watson", "Linear lokal"]),
        M("loess", "LOESS / LOWESS", "curve", form_loess, "Regresi polinomial lokal dengan span optimal dan opsi iterasi robust.", ["Span CV", "LOWESS"]),
        M("spline", "Regresi Spline", "curve", form_spline, "Natural cubic spline atau truncated power spline dengan knot otomatis.", ["Spline", "Knot"]),
        M("quantile", "Regresi Kuantil", "quantile", form_quantile, "Hubungan X–Y pada berbagai kuantil, bukan hanya rata-rata; galat baku lewat bootstrap.", ["Kuantil", "Bootstrap"]),
        M("gam", "Generalized Additive Model (GAM)", "gam", form_gam, "Efek mulus tiap variabel (penalized spline, GCV) digabung dengan efek linear.", ["s(X)", "Derajat bebas efektif"]),
    ],
    "Data Terstruktur": [
        M("panel", "Regresi Data Panel", "panel", form_panel, "Common, Fixed, dan Random Effect dengan uji Chow, Breusch-Pagan LM, dan Hausman untuk memilih model terbaik.", ["CEM · FEM · REM", "Chow · BP-LM · Hausman"]),
        M("ts", "Regresi Deret Waktu (ARIMAX)", "ts", form_ts, "Regresi dengan galat ARIMA(p,d,q): koreksi autokorelasi, uji Ljung-Box, dan ACF galat.", ["ARIMAX", "Ljung-Box", "ACF"]),
        M("sar", "Regresi Spasial – SAR (Lag)", "spatial", form_spatial("sar"), "Ketergantungan spasial pada variabel respon: ρ, efek langsung/tidak langsung, dan Moran's I.", ["SAR", "Moran's I", "Spillover"]),
        M("sem", "Regresi Spasial – SEM (Error)", "spatial", form_spatial("sem"), "Ketergantungan spasial pada galat: λ, uji LM, dan Moran's I galat.", ["SEM", "Moran's I"]),
        M("gwr", "Geographically Weighted Regression (GWR)", "spatial", form_spatial("gwr"), "Koefisien yang berbeda tiap lokasi (nonstasioneritas spasial), peta koefisien, dan perbandingan dengan OLS.", ["GWR", "Peta koefisien", "AICc"]),
        M("mixed", "Mixed Effect Model", "mixed", form_mixed, "Efek tetap + efek acak (intersep dan slope) dengan REML; ICC dan R² marginal/kondisional.", ["REML", "ICC", "Random slope"]),
        M("cox", "Regresi Cox (Survival)", "cox", form_cox, "Cox proportional hazards: hazard ratio, concordance, kurva Kaplan-Meier, dan uji asumsi PH.", ["Hazard ratio", "Kaplan-Meier", "C-index"]),
        M("tobit", "Regresi Tobit", "tobit", form_tobit, "Regresi untuk data tersensor (kiri/kanan); koefisien laten, efek marjinal, dan pembanding OLS.", ["Sensor", "Efek marjinal"]),
    ],
}

REG_FLAT = {m["key"]: m for g in REG_GROUPS.values() for m in g}


def run_reg_page(mkey, alpha):
    m = REG_FLAT[mkey]
    from ui_core import hero_for, load_data_generic
    hero_for(m["label"], m["desc"], m["tags"], alpha)
    crumb("Regresi Lanjutan", _group_of(mkey), m["label"])
    df, src = load_data_generic(sample_reg, m["sample"], f"reg_{mkey}")
    if df is None:
        return
    if src == "contoh":
        H["n_info"]("Menggunakan **data contoh**. Pilih 'Unggah file' atau 'Input manual' pada sidebar untuk data Anda sendiri.")
    with st.expander("👁️ Pratinjau data", expanded=False):
        H["show_df"](df.head(200), hide_index=True)
    with st.container(border=True):
        form_header("Pengaturan model")
        R = m["form"](df, alpha, f"r_{mkey}")
    if R is None:
        return
    render_result(R, f"r_{mkey}", f"hasil_{mkey}.xlsx")


def _group_of(mkey):
    for g, items in REG_GROUPS.items():
        if any(i["key"] == mkey for i in items):
            return g
    return ""
