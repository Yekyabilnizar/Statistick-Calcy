"""registry_more.py – sisa metode agar halaman web setara dengan versi Streamlit (52 metode)."""
import re

import numpy as np
import pandas as pd

import reg_models2 as r2
import reg_models3 as r3
from . import legacy
from .registry import (FAM_DES, FAM_REG, M, METHODS, _as_list, any_col, any_multi, any_opt, boolean, cat_multi, cat_opt, de, float_opt,
                       integer, num, num_multi, number, r1, rc, se, select, select_multi)
from .registry import META


def slugify(t):
    t = t.lower().replace("&", "dan")
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t


def _meta(family, key):
    for g, items in META["des" if family == FAM_DES else "reg"].items():
        for it in items:
            if it["key"] == key:
                return g, it
    raise KeyError(key)


def MN(key, family, fields, run, when, assume, read, gen=None):
    g, it = _meta(family, key)
    src = "de" if family == FAM_DES else "rs"
    M(slugify(it["label"]), key, family, g, it["label"], it["desc"], it["tags"], (src, it["sample"]), fields, run, when, assume, read)
    METHODS[-1]["gen"] = gen


def _ys(y, xs, **k):
    return [num("y", "Variabel dependen (Y)", y), num_multi("xs", "Variabel independen (X)", xs, **k)]


# ======================================================================== penjalan
def run_reg0(df, p, a):
    return "reg0", legacy.run_regression(df, p["y"], _as_list(p["xs"]), bool(p.get("ic", True)), a)


def run_fracfact(df, p, a):
    return "fracfact", de.run_fracfact(df, p["resp"], _as_list(p["facs"]), int(p.get("mo", 2)))


def run_manova(df, p, a):
    return "manova", de.run_manova(df, _as_list(p["rs"]), p["fac"], p.get("blk") or None)


def run_rsm(df, p, a):
    return "rsm", de.run_rsm(df, p["resp"], _as_list(p["facs"]), 1 if str(p.get("order", "")).startswith("Orde 1") else 2, a)


MIX = {"Linear (Scheffé)": "linear", "Kuadratik (Scheffé)": "quadratic", "Special cubic": "special_cubic"}


def run_mixture(df, p, a):
    return "mixture", de.run_mixture(df, p["resp"], _as_list(p["comps"]), MIX.get(p.get("model"), "quadratic"))


TG = {"Larger-the-better": "larger", "Smaller-the-better": "smaller", "Nominal-the-best": "nominal"}


def run_taguchi(df, p, a):
    return "taguchi", de.run_taguchi(df, _as_list(p["facs"]), _as_list(p["rs"]), TG.get(p.get("kind"), "larger"))


def run_multinom(df, p, a):
    return "std", rc.run_multinomial(df, p["y"], _as_list(p.get("xn")), _as_list(p.get("xc")), a)


def run_ordinal(df, p, a):
    return "std", rc.run_ordinal(df, p["y"], _as_list(p["xs"]), a)


SELM = {"Stepwise (dua arah)": "stepwise", "Forward selection": "forward", "Backward elimination": "backward",
        "Best subset (semua kombinasi)": "bestsubset"}


def run_select(df, p, a):
    xs, m = _as_list(p["xs"]), SELM.get(p.get("method"), "stepwise")
    if m == "bestsubset" and len(xs) > 12:
        raise ValueError("Best subset dibatasi ≤ 12 variabel; kurangi pilihan variabel atau gunakan stepwise.")
    return "std", r1.run_selection(df, p["y"], xs, m, p.get("crit", "AIC"), a)


def _penal(method):
    def f(df, p, a):
        lam = None if p.get("auto", True) else max(float(p.get("lam") or 0.1), 1e-4)
        nc = int(p.get("nc") or 0) or None
        return "std", r1.run_regularized(df, p["y"], _as_list(p["xs"]), method, a, float(p.get("l1", 0.5)), lam if method in ("ridge", "lasso", "enet") else None, 10, nc)
    return f


def _robust(method):
    return lambda df, p, a: ("std", r1.run_robust(df, p["y"], _as_list(p["xs"]), method, a))


KERN = {"Gaussian": "gaussian", "Epanechnikov": "epanechnikov", "Tricube": "tricube"}
DEG = {"0 (Nadaraya-Watson)": 0, "1 (linear lokal)": 1, "2 (kuadratik lokal)": 2}


def run_kernel(df, p, a):
    h = None if p.get("auto", True) else max(float(p.get("h") or 1.0), 1e-4)
    return "std", r2.run_kernel(df, p["x"], p["y"], KERN.get(p.get("kind"), "gaussian"), DEG.get(p.get("deg"), 1), h, a)


def run_loess(df, p, a):
    span = None if p.get("auto", True) else float(p.get("span", 0.5))
    return "std", r2.run_loess(df, p["x"], p["y"], span, int(p.get("deg", 2)), a, int(p.get("rb", 0)))


SPL = {"Natural cubic spline": "natural", "Regression spline (truncated power)": "truncated"}


def run_spline(df, p, a):
    nk = None if p.get("auto", True) else int(p.get("nk", 4))
    return "std", r2.run_spline(df, p["x"], p["y"], SPL.get(p.get("kind"), "natural"), nk, a)


def run_quantile(df, p, a):
    taus = sorted({float(t) for t in (p.get("taus") or []) if t not in (None, "")})
    if not taus:
        raise ValueError("Pilih minimal satu kuantil.")
    return "std", r2.run_quantile(df, p["y"], _as_list(p["xs"]), tuple(taus), int(p.get("nb", 100)), a)


def run_gam(df, p, a):
    return "std", r2.run_gam(df, p["y"], _as_list(p["sm"]), _as_list(p.get("ln")), int(p.get("nk", 8)), a)


def run_panel(df, p, a):
    return "std", r3.run_panel(df, p["y"], _as_list(p["xs"]), p["ent"], p["tim"], a)


def run_ts(df, p, a):
    return "std", r3.run_arimax(df, p["y"], _as_list(p["xs"]), int(p.get("p", 1)), int(p.get("d", 0)), int(p.get("q", 0)), p.get("tim") or None, a)


def _spatial(kind):
    def f(df, p, a):
        wk = "knn" if str(p.get("wk", "")).startswith("k tetangga") else "invdist"
        return "std", r3.run_spatial(df, p["y"], _as_list(p["xs"]), p["lon"], p["lat"], kind, int(p.get("kn", 5)), wk, a)
    return f


def run_gwr(df, p, a):
    bw = None
    if not p.get("auto", True):
        n, k = len(df), len(_as_list(p["xs"]))
        bw = int(min(max(int(p.get("bw", 30)), k + 5), max(k + 6, n)))
    return "std", r3.run_gwr(df, p["y"], _as_list(p["xs"]), p["lon"], p["lat"], bw, a)


def run_mixed(df, p, a):
    xs, sl = _as_list(p["xs"]), p.get("sl") or None
    if sl and sl not in xs:
        raise ValueError("Slope acak harus salah satu variabel pada efek tetap (X).")
    return "std", r3.run_mixed(df, p["y"], xs, p["grp"], sl, a)


def run_cox(df, p, a):
    return "std", r3.run_cox(df, p["t"], p["ev"], _as_list(p.get("xn")), _as_list(p.get("xc")), a)


def run_tobit(df, p, a):
    lo = float(p["lo"]) if p.get("lo_on", True) and p.get("lo") is not None else None
    hi = None
    if p.get("hi_on", False):
        hi = float(p["hi"]) if p.get("hi") is not None else float(pd.to_numeric(df[p["y"]], errors="coerce").max())
    if lo is None and hi is None:
        raise ValueError("Aktifkan minimal satu batas sensor.")
    return "std", r3.run_tobit(df, p["y"], _as_list(p["xs"]), lo, hi, a)


# ======================================================================== definisi
# ---- regresi linear (halaman lama)
M("regresi-linear-sederhana-berganda", "reg", FAM_REG, "Dasar", "Regresi Linear (sederhana & berganda)",
  "Hubungan linear satu atau beberapa variabel X dengan Y: persamaan, uji F/t, R², uji asumsi klasik, dan kalkulator prediksi.",
  ["OLS", "Sederhana & berganda", "Uji asumsi klasik", "Kalkulator prediksi"], ("se", "reg"),
  [num("y", "Variabel dependen (Y)", "Hasil_Panen_ton"), num_multi("xs", "Variabel independen (X)", None, min=1, auto=99),
   boolean("ic", "Sertakan intersep (konstanta)", True, "Hilangkan centang untuk regresi melalui titik asal.")], run_reg0,
  "Pakai untuk mengukur hubungan satu atau beberapa variabel X dengan satu variabel Y yang berupa angka, misalnya pengaruh luas lahan, pupuk, dan curah hujan terhadap hasil panen.",
  "Hubungan linear, galat menyebar normal dengan ragam konstan, tidak ada autokorelasi, dan tidak ada multikolinearitas berat antar variabel X.",
  "Uji F menilai model secara keseluruhan; uji t menilai tiap koefisien. R² adalah proporsi keragaman Y yang dijelaskan model. Pada tab Prediksi, masukkan nilai X untuk memperoleh prediksi Y beserta selang kepercayaannya.")
METHODS[-1]["gen"] = None

# ---- rancangan: faktorial pecahan, MANOVA, RSM, mixture, Taguchi
MN("fracfact", FAM_DES,
   [num("resp", "Variabel respon", "Hasil"), num_multi("facs", "Faktor (kode −1 / +1)", list("ABCDE"), min=3),
    integer("mo", "Orde interaksi maksimum", 1, 3, 2)], run_fracfact,
   "Pakai bila faktor banyak tetapi unit percobaan terbatas, sehingga hanya sebagian kombinasi (2^(k−p)) yang dijalankan untuk menduga efek utama dan interaksi orde rendah.",
   "Interaksi orde tinggi diabaikan (sparsity of effects). Faktor dikodekan −1/+1. Efek yang beralias tidak dapat dipisahkan dan ditulis bersama aliasnya.",
   "Lihat tabel efek: efek bertanda * atau ** nyata. Pada diagram Pareto dan plot peluang normal, efek yang menjauh dari garis lurus adalah efek nyata. Bila tidak ada derajat bebas galat, uji memakai metode Lenth yang bersifat eksploratif.",
   gen=dict(kind="fracfact", fields=[integer("base", "Jumlah faktor dasar", 3, 6, 4), dict(name="gens", label="Generator (pisahkan koma)", type="text", default="E=ABCD")]))
MN("manova", FAM_DES,
   [cat_opt("blk", "Blok (opsional)"), dict(name="fac", label="Faktor/perlakuan", type="cat", want="Perlakuan", pos=0),
    num_multi("rs", "Variabel respon (≥ 2, numerik)", ["Tinggi", "Bobot", "Kadar"], min=2)], run_manova,
   "Pakai bila beberapa variabel respon yang saling berkorelasi diukur bersamaan pada tiap satuan percobaan, misalnya tinggi, bobot, dan kadar protein tanaman.",
   "Respon menyebar normal multivariat, matriks kovarians homogen antar kelompok (uji Box's M), dan pengamatan saling bebas.",
   "Mulai dari uji multivariat (Pillai, Wilks, Hotelling-Lawley, Roy). Bila nyata, lihat ANOVA univariat per respon dengan P terkoreksi Bonferroni untuk mengetahui respon mana yang berbeda. Pillai paling tahan bila Box's M nyata.")
MN("rsm", FAM_DES,
   [num("resp", "Variabel respon", "Rendemen"), num_multi("facs", "Faktor (2–4, numerik)", ["Suhu", "Waktu"], min=2, max=4),
    select("order", "Orde model", ["Orde 2 (kuadratik penuh)", "Orde 1 (linear)"], "Orde 2 (kuadratik penuh)")], run_rsm,
   "Pakai untuk mencari kondisi optimum proses (suhu, waktu, konsentrasi) dari percobaan bertahap seperti Central Composite atau Box-Behnken.",
   "Model polinomial orde dua cukup mewakili permukaan respon di sekitar optimum, galat normal dan homogen, dan faktor dapat diatur secara tepat.",
   "Periksa P model, R² prediksi, dan lack-of-fit (tidak nyata berarti model cukup). Titik stasioner menunjukkan maksimum, minimum, atau pelana; bila berada di luar daerah percobaan, gunakan optimum terbatas. Plot kontur menggambarkan permukaan respon.",
   gen=dict(kind="rsm", fields=[select("typ", "Rancangan", ["CCD", "Box-Behnken"]), integer("k", "Jumlah faktor", 2, 5, 3), integer("nc", "Titik pusat", 1, 8, 5)]))
MN("mixture", FAM_DES,
   [num("resp", "Variabel respon", "Kekerasan"), num_multi("comps", "Komponen campuran (≥ 3; proporsi total tetap)", ["Tepung", "Air", "Gula"], min=3),
    select("model", "Model", list(MIX.keys()), "Kuadratik (Scheffé)")], run_mixture,
   "Pakai bila respon bergantung pada proporsi komponen campuran yang totalnya tetap (100%), seperti formulasi adonan, pakan, atau pupuk.",
   "Proporsi komponen berjumlah 1 (atau 100%) pada tiap run, model Scheffé tanpa intersep sesuai, galat normal dan homogen.",
   "Koefisien linear menunjukkan respon komponen murni; koefisien interaksi positif berarti sinergi, negatif berarti antagonisme. Diagram segitiga dan tabel optimum menunjukkan komposisi terbaik.")
MN("taguchi", FAM_DES,
   [num_multi("rs", "Kolom respon/replikasi (≥ 1)", ["Y1", "Y2", "Y3"], min=1),
    any_multi("facs", "Faktor kontrol (kolom level)", ["Suhu", "Tekanan", "Waktu", "Kecepatan"], min=1),
    select("kind", "Karakteristik kualitas", list(TG.keys()), "Larger-the-better")], run_taguchi,
   "Pakai untuk merancang proses yang kokoh terhadap gangguan (noise) dengan sedikit percobaan melalui array ortogonal (L4, L8, L9, dan seterusnya).",
   "Faktor kontrol tersusun menurut array ortogonal, replikasi mewakili variasi gangguan, dan interaksi antar faktor diasumsikan kecil.",
   "Pilih level faktor dengan rasio S/N tertinggi. Peringkat delta menunjukkan faktor paling berpengaruh; ANOVA S/N menguji kebermaknaannya. Lakukan percobaan konfirmasi pada kombinasi optimum.")

# ---- regresi: GLM lain
MN("multinom", FAM_REG,
   [any_col("y", "Variabel dependen kategorik (≥ 3 kelas)", "Jenis"), num_multi("xn", "Variabel numerik (X)", ["X1", "X2"]), cat_multi("xc", "Variabel kategorik (dummy)")], run_multinom,
   "Pakai bila respon berupa kategori tanpa urutan dengan tiga kelas atau lebih, misalnya jenis pilihan, jenis penyakit, atau merek.",
   "Observasi saling bebas, independence of irrelevant alternatives, dan jumlah pengamatan per kelas cukup. Tidak ada separasi sempurna.",
   "Kelas pertama menjadi referensi. Exp(koefisien) adalah odds ratio relatif terhadap kelas referensi untuk kenaikan satu satuan X; lihat akurasi klasifikasi untuk ketepatan model.")
MN("ordinal", FAM_REG,
   [num("y", "Variabel dependen ordinal (kategori terurut, mis. 1–4)", "Kepuasan"), num_multi("xs", "Variabel independen (X)", ["X1", "X2"], min=1)], run_ordinal,
   "Pakai bila respon berupa kategori berurutan, seperti skala kepuasan 1–5 atau tingkat keparahan rendah–sedang–tinggi.",
   "Proportional odds (efek X sama pada semua ambang), observasi saling bebas, dan kategori terurut dengan jelas.",
   "Koefisien positif menaikkan peluang berada pada kategori lebih tinggi; exp(koefisien) adalah odds ratio kumulatif. Ambang (threshold) memisahkan kategori yang berdekatan.")
# ---- seleksi & regularisasi
MN("select", FAM_REG,
   _ys("Y", [f"X{i}" for i in range(1, 9)], min=2) + [select("method", "Metode seleksi", list(SELM.keys()), "Stepwise (dua arah)"), select("crit", "Kriteria", ["AIC", "BIC"], "AIC")],
   run_select,
   "Pakai bila ada banyak kandidat variabel X dan ingin memilih himpunan yang paling berperan menjelaskan Y.",
   "Asumsi regresi linear berlaku. P-value pada model terpilih cenderung terlalu optimistis karena variabel dipilih dari data yang sama.",
   "Bandingkan model terpilih dengan model penuh (R² adjusted, AIC, BIC). Jejak langkah menunjukkan variabel yang masuk atau keluar; periksa VIF pada model akhir.")
for _k, _lab, _w, _r in [
    ("ridge", "ridge", "Pakai bila variabel X saling berkorelasi kuat dan Anda ingin koefisien yang lebih stabil.", "Koefisien menyusut mendekati nol tanpa dihapus; semakin besar λ semakin kuat penyusutannya."),
    ("lasso", "lasso", "Pakai bila banyak variabel X dan Anda ingin sekaligus menyeleksi variabel penting.", "Koefisien yang menjadi tepat nol berarti variabelnya dikeluarkan dari model."),
    ("enet", "enet", "Pakai bila X berkorelasi dan banyak, sehingga LASSO saja kurang stabil.", "Rasio L1 mengatur keseimbangan antara seleksi variabel (LASSO) dan penyusutan (Ridge)."),
    ("pcr", "pcr", "Pakai bila X sangat berkorelasi dan Anda ingin meregresikan Y pada komponen utama X.", "Jumlah komponen dipilih lewat validasi silang; lihat ragam X yang dijelaskan tiap komponen."),
    ("pls", "pls", "Pakai bila X banyak dan berkorelasi, dan ingin komponen yang paling relevan terhadap Y.", "Variabel dengan VIP ≥ 1 paling berperan menjelaskan Y.")]:
    flds = _ys("Y", [f"X{i}" for i in range(1, 11)], min=2)
    if _k == "enet":
        flds.append(number("l1", "Rasio L1 (0 = Ridge, 1 = LASSO)", 0.05, 0.95, 0.5, 0.05))
    if _k in ("ridge", "lasso", "enet"):
        flds += [boolean("auto", "Pilih λ otomatis (validasi silang)", True), number("lam", "Nilai λ (bila tidak otomatis)", 0.0001, 100, 0.1, 0.01)]
    else:
        flds.append(integer("nc", "Jumlah komponen (0 = otomatis lewat CV)", 0, 10, 0))
    MN(_k, FAM_REG, flds, _penal(_k), _w,
       "Asumsi dasar regresi linear (hubungan linear, observasi saling bebas). Variabel dibakukan otomatis sebelum penaksiran.",
       _r + " Koefisien sengaja bias demi ragam yang lebih kecil, sehingga tidak disertai uji-t klasik; nilai prediksi dinilai lewat RMSE validasi silang dibanding OLS.")
# ---- robust & nonparametrik
for _k, _w, _r in [
    ("huber", "Pakai bila data memuat pencilan (outlier) yang mengganggu garis regresi biasa.", "Bandingkan koefisien dengan OLS; pengamatan berbobot rendah adalah kandidat pencilan."),
    ("bisquare", "Pakai bila pencilan cukup ekstrem sehingga perlu dibuang pengaruhnya sepenuhnya.", "Pengamatan berbobot nol dikeluarkan dari penaksiran; periksa apakah itu memang data yang keliru."),
    ("lts", "Pakai bila pencilan banyak (hingga sekitar separuh data) atau perlu deteksi pencilan yang kuat.", "Pengamatan yang ditandai outlier dikeluarkan dari penaksiran akhir; telusuri penyebabnya sebelum membuang data.")]:
    MN(_k, FAM_REG, _ys("Y", ["X"], min=1), _robust(_k), _w,
       "Hubungan linear dan sebagian besar data mengikuti model; pencilan berada pada minoritas pengamatan.", _r)
MN("kernel", FAM_REG,
   [num("x", "Variabel independen (X)", "X", 0), num("y", "Variabel dependen (Y)", "Y"), select("kind", "Fungsi kernel", list(KERN.keys()), "Gaussian"),
    select("deg", "Derajat polinomial lokal", list(DEG.keys()), "1 (linear lokal)"), boolean("auto", "Bandwidth otomatis (CV)", True),
    number("h", "Bandwidth h (satuan X, bila tidak otomatis)", 0.0001, 1e6, 1.0, 0.1)], run_kernel,
   "Pakai bila bentuk hubungan X dan Y tidak diketahui dan Anda menginginkan kurva mulus tanpa bentuk fungsi tertentu.",
   "Hubungan mulus (kontinu), galat bebas, dan data cukup rapat di sepanjang X.",
   "Bandwidth kecil membuat kurva bergelombang; besar membuatnya terlalu halus. Uji kelinearan menunjukkan apakah kurva lebih sesuai daripada garis lurus.")
MN("loess", FAM_REG,
   [num("x", "Variabel independen (X)", "X", 0), num("y", "Variabel dependen (Y)", "Y"), boolean("auto", "Span otomatis (CV)", True),
    number("span", "Span (bila tidak otomatis)", 0.1, 1.0, 0.5, 0.05), select("deg", "Derajat lokal", ["1", "2"], "2"), integer("rb", "Iterasi robust (LOWESS)", 0, 4, 0)], run_loess,
   "Pakai untuk menggambar kurva tren mulus yang mengikuti data tanpa menentukan bentuk fungsinya.",
   "Hubungan mulus dan data cukup untuk regresi lokal; iterasi robust membantu bila ada pencilan.",
   "Span adalah proporsi data yang dipakai di tiap titik; semakin kecil, kurva semakin mengikuti data. Pita kepercayaan menunjukkan ketidakpastian kurva.")
MN("spline", FAM_REG,
   [num("x", "Variabel independen (X)", "X", 0), num("y", "Variabel dependen (Y)", "Y"), select("kind", "Jenis spline", list(SPL.keys()), "Natural cubic spline"),
    boolean("auto", "Jumlah knot otomatis", True), integer("nk", "Jumlah knot (bila tidak otomatis)", 1, 12, 4)], run_spline,
   "Pakai bila hubungan X dan Y melengkung dan Anda ingin kurva yang fleksibel namun tetap berupa model regresi.",
   "Galat normal dan homogen; knot cukup untuk menangkap bentuk kurva tanpa overfitting.",
   "Jumlah knot optimal dipilih lewat GCV. Uji kelinearan menunjukkan apakah suku nonlinear nyata dibanding garis lurus.")
MN("quantile", FAM_REG,
   _ys("Y", ["X"], min=1) + [select_multi("taus", "Kuantil (τ)", [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95], [0.1, 0.25, 0.5, 0.75, 0.9]), integer("nb", "Ulangan bootstrap (galat baku)", 50, 500, 100)],
   run_quantile,
   "Pakai bila Anda tertarik pada efek X terhadap kuantil tertentu dari Y (misalnya kasus terbaik atau terburuk), atau ragam galat tidak konstan.",
   "Observasi saling bebas dan model kuantil bersyarat linear. Tidak memerlukan galat normal.",
   "Bandingkan koefisien antar kuantil: bila berbeda nyata, pengaruh X tidak seragam di seluruh sebaran Y. Galat baku dan selang kepercayaan diperoleh dari bootstrap.")
MN("gam", FAM_REG,
   [num("y", "Variabel dependen (Y)", "Y"), num_multi("sm", "Variabel dengan efek mulus (smooth) s(X)", ["X1", "X2"], min=1),
    num_multi("ln", "Variabel dengan efek linear", ["X3"]), integer("nk", "Basis per smooth (fleksibilitas maksimum)", 4, 15, 8)], run_gam,
   "Pakai bila sebagian X berhubungan nonlinear dengan Y sementara lainnya linear, dan Anda ingin melihat bentuk tiap efek.",
   "Efek bersifat aditif (tanpa interaksi antar variabel), galat normal dan bebas.",
   "edf mendekati 1 berarti efeknya hampir linear. Bandingkan GAM dengan regresi linear: bila nyata, komponen nonlinear diperlukan.")
# ---- data terstruktur
MN("panel", FAM_REG,
   [any_col("ent", "Kolom entitas/individu", "Provinsi", 0), any_col("tim", "Kolom waktu", "Tahun", 0),
    num("y", "Variabel dependen (Y)", "Y", 0), num_multi("xs", "Variabel independen (X)", ["X1", "X2"], min=1)], run_panel,
   "Pakai bila individu (provinsi, perusahaan, subjek) diamati berulang pada beberapa periode waktu.",
   "Data panel seimbang atau mendekati seimbang; galat bebas antar entitas. Pemilihan model memakai rangkaian uji Chow, Breusch-Pagan LM, dan Hausman.",
   "Ikuti rekomendasi model terbaik dari rangkaian uji: Common, Fixed, atau Random Effect. Bandingkan koefisien ketiga model dan periksa efek individu.")
MN("ts", FAM_REG,
   [any_opt("tim", "Kolom waktu (untuk pengurutan, opsional)", "Waktu"), num("y", "Variabel dependen (Y)", "Y"), num_multi("xs", "Variabel eksogen (X)", ["X1", "X2"]),
    integer("p", "Orde AR (p)", 0, 4, 1), integer("d", "Diferensiasi (d)", 0, 2, 0), integer("q", "Orde MA (q)", 0, 4, 0)], run_ts,
   "Pakai bila data berurutan waktu dan galat regresi biasa berautokorelasi, sehingga perlu dimodelkan dengan ARIMA.",
   "Data berurutan teratur, galat setelah model ARIMA tidak lagi berautokorelasi, dan deret (setelah diferensiasi) stasioner.",
   "Periksa uji Ljung-Box dan ACF galat: bila tidak nyata, autokorelasi telah tertangani. Bandingkan AIC/BIC untuk memilih orde p, d, q.")
for _k, _w, _r in [("sar", "Pakai bila nilai Y di suatu lokasi dipengaruhi nilai Y di lokasi tetangganya (spillover spasial).", "Parameter ρ yang nyata menunjukkan ketergantungan spasial pada Y; efek langsung dan tidak langsung menggambarkan spillover."),
                   ("sem", "Pakai bila galat model berkorelasi antar lokasi berdekatan akibat variabel yang tidak teramati.", "Parameter λ yang nyata menunjukkan ketergantungan spasial pada galat; periksa Moran's I residual.")]:
    MN(_k, FAM_REG,
       [num("lon", "Koordinat X (bujur/Lon)", "Lon", 0), num("lat", "Koordinat Y (lintang/Lat)", "Lat", 0), num("y", "Variabel dependen (Y)", "Y"),
        num_multi("xs", "Variabel independen (X)", ["X1", "X2"], min=1), select("wk", "Matriks bobot spasial", ["k tetangga terdekat", "Inverse jarak kuadrat"], "k tetangga terdekat"),
        integer("kn", "k tetangga (bila memakai k tetangga)", 3, 15, 5)], _spatial(_k), _w,
       "Data memiliki koordinat lokasi, matriks bobot spasial mencerminkan kedekatan yang bermakna, dan model terspesifikasi dengan benar.", _r)
MN("gwr", FAM_REG,
   [num("lon", "Koordinat X (bujur/Lon)", "Lon", 0), num("lat", "Koordinat Y (lintang/Lat)", "Lat", 0), num("y", "Variabel dependen (Y)", "Y"),
    num_multi("xs", "Variabel independen (X)", ["X1", "X2"], min=1), boolean("auto", "Bandwidth otomatis (validasi silang)", True),
    integer("bw", "Jumlah tetangga terdekat (bila tidak otomatis)", 8, 5000, 30)], run_gwr,
   "Pakai bila hubungan X dan Y diduga berbeda antar lokasi (nonstasioneritas spasial).",
   "Data cukup banyak di sekitar tiap lokasi dan koordinat akurat; bandwidth menentukan seberapa lokal koefisien.",
   "Bandingkan AICc dengan OLS global. Peta koefisien dan R² lokal menunjukkan wilayah tempat pengaruh X kuat atau lemah.")
MN("mixed", FAM_REG,
   [any_col("grp", "Kolom kelompok (efek acak)", "Kelompok", 0), num("y", "Variabel dependen (Y)", "Y"), num_multi("xs", "Efek tetap (X)", ["X"], min=1),
    dict(name="sl", label="Slope acak untuk variabel (opsional; pilih salah satu X)", type="any_opt", want=None, reuse=True)], run_mixed,
   "Pakai bila data bersarang atau berkelompok (siswa dalam kelas, plot dalam lokasi, pengukuran berulang pada individu).",
   "Efek acak menyebar normal, galat normal dan homogen, dan jumlah kelompok cukup untuk menduga komponen ragam.",
   "ICC menunjukkan proporsi ragam akibat perbedaan antar kelompok. Bila ICC kecil, OLS biasa mungkin cukup. Efek tetap dibaca seperti regresi biasa.")
MN("cox", FAM_REG,
   [num("t", "Waktu hingga kejadian/sensor", "Waktu", 0), any_col("ev", "Status (1 = kejadian, 0 = tersensor)", "Status", 0),
    num_multi("xn", "Kovariat numerik", ["Umur", "Skor"]), cat_multi("xc", "Kovariat kategorik (dummy)", ["Perlakuan"])], run_cox,
   "Pakai untuk menganalisis waktu hingga suatu kejadian (kematian, kambuh, kerusakan) ketika sebagian pengamatan tersensor.",
   "Proportional hazards (rasio risiko tetap sepanjang waktu), sensor tidak informatif, dan observasi saling bebas.",
   "Hazard ratio di atas 1 berarti risiko naik; di bawah 1 berarti turun. Periksa uji asumsi PH dan kurva Kaplan-Meier; C-index mendekati 1 menunjukkan diskriminasi yang baik.")
MN("tobit", FAM_REG,
   _ys("Y", ["X1", "X2"], min=1) + [boolean("lo_on", "Sensor kiri (batas bawah)", True), dict(name="lo", label="Batas bawah", type="float", min=-1e12, max=1e12, default=0.0, step=0.1),
                                   boolean("hi_on", "Sensor kanan (batas atas)", False), float_opt("hi", "Batas atas (kosong = nilai maksimum data)")], run_tobit,
   "Pakai bila respon menumpuk di batas tertentu (mis. banyak bernilai 0) sehingga data tersensor.",
   "Galat laten menyebar normal dengan ragam konstan; batas sensor diketahui dan sama untuk seluruh pengamatan.",
   "Koefisien menggambarkan hubungan pada variabel laten; efek marjinal menunjukkan efek pada nilai teramati. Bandingkan dengan OLS yang bias bila banyak data tersensor.")
