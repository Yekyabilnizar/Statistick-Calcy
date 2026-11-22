"""registry.py – daftar metode yang tersedia di website, definisi isian, dan fungsi penjalannya.

Menambah metode baru = menambah satu entri M(...) di bawah (isian + fungsi run + teks penjelasan)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pandas as pd  # noqa: E402

import design_engine as de  # noqa: E402
import reg_core as rc  # noqa: E402
import reg_models1 as r1  # noqa: E402
import reg_samples as rs  # noqa: E402
import stats_engine as se  # noqa: E402

FAM_DES, FAM_REG = "des", "reg"
FAM_NAME = {FAM_DES: "Rancangan Percobaan", FAM_REG: "Regresi"}
FAM_PATH = {FAM_DES: "rancangan-percobaan", FAM_REG: "regresi"}


# ---------------------------------------------------------------- isian formulir
def num(name, label, want=None, pos=-1, **k):
    return dict(name=name, label=label, type="num", want=want, pos=pos, **k)


def cat(name, label, want=None, pos=0, **k):
    return dict(name=name, label=label, type="cat", want=want, pos=pos, **k)


def cat_opt(name, label, want=None, **k):
    return dict(name=name, label=label, type="cat_opt", want=want, **k)


def num_multi(name, label, want=None, **k):
    return dict(name=name, label=label, type="num_multi", want=want or [], **k)


def cat_multi(name, label, want=None, **k):
    return dict(name=name, label=label, type="cat_multi", want=want or [], **k)


def any_col(name, label, want=None, pos=-1, **k):
    return dict(name=name, label=label, type="any", want=want, pos=pos, **k)


def any_multi(name, label, want=None, **k):
    return dict(name=name, label=label, type="any_multi", want=want or [], **k)


def any_opt(name, label, want=None, **k):
    return dict(name=name, label=label, type="any_opt", want=want, **k)


def float_opt(name, label, placeholder=""):
    return dict(name=name, label=label, type="float_opt", placeholder=placeholder)


def select_multi(name, label, options, default):
    return dict(name=name, label=label, type="select_multi", options=list(options), default=list(default))


def integer(name, label, lo, hi, default):
    return dict(name=name, label=label, type="int", min=lo, max=hi, default=default)


def number(name, label, lo, hi, default, step):
    return dict(name=name, label=label, type="float", min=lo, max=hi, default=default, step=step)


def boolean(name, label, default=True, help=None):
    return dict(name=name, label=label, type="bool", default=default, help=help)


def select(name, label, options, default=None, help=None):
    return dict(name=name, label=label, type="select", options=list(options), default=default or options[0], help=help)


# ---------------------------------------------------------------- penjalan metode
def _as_list(v):
    return [] if v in (None, "") else (v if isinstance(v, list) else [v])


def run_ral(df, p, a):
    R = se.run_ral(df, p["resp"], p["trt"])
    R["dropped"] = len(df) - len(R["data"])
    return "legacy", R


def run_rak(df, p, a):
    R = se.run_rak(df, p["resp"], p["trt"], p["blk"])
    R["dropped"] = len(df) - len(R["data"])
    return "legacy", R


def run_rbsl(df, p, a):
    return "anova", de.run_latin(df, p["resp"], p["trt"], p["row"], p["col"])


def run_graeco(df, p, a):
    return "anova", de.run_graeco(df, p["resp"], p["trt"], p["gr"], p["row"], p["col"])


def run_bib(df, p, a):
    return "anova", de.run_incomplete(df, p["resp"], p["trt"], p["blk"], p.get("rep") or None, a, p.get("adj", "LSD"))


def run_factorial(df, p, a):
    return "anova", de.run_factorial(df, p["resp"], _as_list(p["facs"]), p.get("blk") or None)


def run_split(df, p, a):
    return "anova", de.run_split_plot(df, p["resp"], p["blk"], p["main"], p["sub"])


def run_splitsplit(df, p, a):
    return "anova", de.run_split_split(df, p["resp"], p["blk"], p["main"], p["sub"], p["ss"])


def run_strip(df, p, a):
    return "anova", de.run_strip_plot(df, p["resp"], p["blk"], p["fa"], p["fb"])


def run_nested(df, p, a):
    return "anova", de.run_nested(df, p["resp"], p["fa"], p["fb"], bool(p.get("rnd", True)))


def run_repeated(df, p, a):
    return "anova", de.run_repeated(df, p["resp"], p["sub"], p["wit"], a)


def run_crossover(df, p, a):
    return "anova", de.run_crossover(df, p["resp"], p["seq"], p["sub"], p["per"], p["trt"], a)


def run_ancova(df, p, a):
    return "anova", de.run_ancova(df, p["resp"], p["grp"], p["cov"], a, p.get("adj", "LSD"))


def run_dummy(df, p, a):
    return "std", r1.run_dummy(df, p["y"], _as_list(p.get("xn")), _as_list(p.get("xc")), a)


def run_poly(df, p, a):
    return "std", rc.run_polynomial(df, p["x"], p["y"], int(p.get("deg", 2)), bool(p.get("cen", True)), a)


def run_diag(df, p, a):
    return "std", rc.run_diagnostics(df, p["y"], _as_list(p["xs"]), bool(p.get("ic", True)), a)


def run_nonlin(df, p, a):
    return "std", rc.run_nonlinear(df, p["x"], p["y"], p["model"], a)


def _glm(kind):
    def f(df, p, a):
        return "std", rc.run_glm(df, p["y"], _as_list(p.get("xn")), _as_list(p.get("xc")), kind, a, float(p.get("cut", 0.5)))
    return f


# ---------------------------------------------------------------- definisi metode
METHODS = []


def M(slug, key, family, group, title, desc, tags, sample, fields, run, when, assume, read):
    METHODS.append(dict(slug=slug, key=key, family=family, group=group, title=title, desc=desc, tags=tags, sample=sample,
                        fields=fields, run=run, when=when, assume=assume, read=read))


# ---- Rancangan percobaan
M("rancangan-acak-lengkap", "ral", FAM_DES, "Rancangan Dasar", "Rancangan Acak Lengkap (RAL)",
  "Analisis ragam satu faktor untuk percobaan dengan satuan percobaan yang homogen, lengkap dengan uji lanjut bernotasi huruf.",
  ["ANOVA satu arah", "Uji lanjut", "Uji asumsi"], ("se", "ral"),
  [any_col("trt", "Kolom perlakuan", "Perlakuan", 0), num("resp", "Kolom respon (numerik)", "Hasil")], run_ral,
  "Pakai RAL bila satuan percobaan relatif seragam (misalnya percobaan di laboratorium atau rumah kaca dengan kondisi terkendali) dan hanya ada satu faktor perlakuan.",
  "Galat menyebar normal, ragam antar perlakuan homogen, dan pengamatan saling bebas. Penempatan perlakuan harus diacak ke seluruh satuan percobaan.",
  "Lihat P-value pada tabel ANOVA: bila lebih kecil dari taraf nyata (α), perlakuan berpengaruh nyata. Lanjutkan dengan uji lanjut; perlakuan yang memiliki huruf sama tidak berbeda nyata. Koefisien keragaman (KK) menunjukkan ketelitian percobaan.")

M("rancangan-acak-kelompok", "rak", FAM_DES, "Rancangan Dasar", "Rancangan Acak Kelompok (RAK)",
  "Analisis ragam satu faktor dengan pengelompokan untuk mengendalikan keragaman lokasi, waktu, atau ulangan.",
  ["ANOVA dua arah", "Pengelompokan", "Uji lanjut"], ("se", "rak"),
  [any_col("trt", "Kolom perlakuan", "Perlakuan", 0), any_col("blk", "Kolom kelompok (blok)", "Kelompok", 0),
   num("resp", "Kolom respon (numerik)", "Hasil")], run_rak,
  "Pakai RAK bila satuan percobaan tidak seragam tetapi dapat dikelompokkan menjadi blok yang relatif homogen di dalamnya (lahan miring, waktu berbeda, operator berbeda).",
  "Galat menyebar normal dan homogen, tidak ada interaksi perlakuan × kelompok, dan setiap perlakuan muncul sekali di setiap kelompok.",
  "Periksa efek perlakuan pada tabel ANOVA. Efek kelompok yang nyata menunjukkan pengelompokan efektif. Lanjutkan dengan uji lanjut pada perlakuan yang berpengaruh nyata.")

M("rancangan-bujur-sangkar-latin", "rbsl", FAM_DES, "Rancangan Lingkungan", "Rancangan Bujur Sangkar Latin (RBSL)",
  "Mengendalikan dua sumber keragaman sekaligus (baris dan kolom); tiap perlakuan muncul sekali pada tiap baris dan kolom.",
  ["Dua arah pengelompokan", "ANOVA Latin"], ("de", "rbsl"),
  [num("resp", "Variabel respon (numerik)", "Hasil"), cat("trt", "Perlakuan", "Perlakuan", 2),
   cat("row", "Baris", "Baris", 0), cat("col", "Kolom", "Kolom", 0)], run_rbsl,
  "Pakai RBSL bila ada dua sumber keragaman yang dapat dikendalikan bersamaan, misalnya lajur lahan (baris) dan gradien kesuburan (kolom).",
  "Jumlah baris = jumlah kolom = jumlah perlakuan, tidak ada interaksi antar faktor, serta galat normal dan homogen.",
  "Perlakuan diuji terhadap galat setelah pengaruh baris dan kolom dikeluarkan. Bila nyata, lanjutkan dengan uji lanjut.")

M("rancangan-graeco-latin", "graeco", FAM_DES, "Rancangan Lingkungan", "Rancangan Graeco-Latin",
  "Perluasan RBSL dengan tiga sumber pengelompokan (baris, kolom, dan huruf Yunani) untuk perlakuan.",
  ["Tiga pengelompokan"], ("de", "graeco"),
  [num("resp", "Variabel respon (numerik)", "Hasil"), cat("trt", "Perlakuan (huruf Latin)", "Perlakuan", 2),
   cat("gr", "Faktor ke-3 (huruf Yunani)", "Greek", 0), cat("row", "Baris", "Baris", 0), cat("col", "Kolom", "Kolom", 0)], run_graeco,
  "Pakai bila ada tiga sumber keragaman yang perlu dikendalikan sekaligus dalam satu percobaan berukuran t × t.",
  "Keempat faktor saling ortogonal (setiap pasangan muncul sekali), tanpa interaksi, galat normal dan homogen.",
  "Efek perlakuan diuji setelah baris, kolom, dan faktor Yunani dikeluarkan. Derajat bebas galat kecil, jadi kesimpulan perlu hati-hati.")

M("blok-tidak-lengkap-bib-lattice", "bib", FAM_DES, "Rancangan Lingkungan", "Blok Tidak Lengkap (BIB / Lattice)",
  "Balanced Incomplete Block dan Lattice: rata-rata perlakuan terkoreksi blok dan uji berpasangan.",
  ["BIB", "Lattice", "Terkoreksi blok"], ("de", "bib"),
  [num("resp", "Variabel respon (numerik)", "Hasil"), cat("trt", "Perlakuan", "Perlakuan", 0), cat("blk", "Blok", "Blok", 0),
   cat_opt("rep", "Ulangan/replikasi (khusus Lattice, opsional)"), select("adj", "Koreksi uji berpasangan", ["LSD", "Bonferroni"])], run_bib,
  "Pakai bila blok tidak cukup besar untuk memuat semua perlakuan, sehingga setiap blok hanya memuat sebagian perlakuan.",
  "Rancangan seimbang (setiap pasangan perlakuan bertemu jumlah blok yang sama pada BIB), galat normal dan homogen.",
  "Bandingkan rata-rata terkoreksi blok, bukan rata-rata mentah. Uji berpasangan memakai koreksi yang Anda pilih.")

M("percobaan-faktorial", "factorial", FAM_DES, "Rancangan Perlakuan", "Percobaan Faktorial",
  "Dua sampai empat faktor sekaligus dengan semua interaksinya; dapat dilengkapi kelompok (RAK faktorial).",
  ["2–4 faktor", "Interaksi", "Uji lanjut"], ("de", "factorial"),
  [num("resp", "Variabel respon (numerik)", "Hasil"), cat_multi("facs", "Faktor (2–4)", ["Dosis", "Varietas"], min=2, max=4),
   cat_opt("blk", "Kelompok/blok (opsional, jadi RAK faktorial)", "Kelompok")], run_factorial,
  "Pakai bila ingin menguji beberapa faktor sekaligus dan melihat apakah pengaruh satu faktor bergantung pada level faktor lain (interaksi).",
  "Data seimbang (setiap kombinasi perlakuan memiliki jumlah ulangan sama), galat normal dan homogen.",
  "Periksa interaksi lebih dulu. Bila interaksi nyata, tafsirkan rata-rata kombinasi, bukan efek utama saja.")

M("petak-terbagi-split-plot", "split", FAM_DES, "Rancangan Perlakuan", "Petak Terbagi (Split-Plot)",
  "Satu faktor pada petak utama dan faktor lain pada anak petak, dengan galat terpisah untuk masing-masing.",
  ["Dua galat", "Petak utama", "Anak petak"], ("de", "split"),
  [num("resp", "Variabel respon (numerik)", "Hasil"), cat("blk", "Kelompok (ulangan)", "Kelompok", 0),
   cat("main", "Petak utama (main plot)", "Petak_Utama", 0), cat("sub", "Anak petak (sub plot)", "Anak_Petak", 0)], run_split,
  "Pakai bila satu faktor sulit atau mahal diubah (misalnya pengolahan tanah atau irigasi) sehingga diterapkan pada petak besar, sedangkan faktor lain pada petak kecil di dalamnya.",
  "Galat petak utama dan galat anak petak berbeda; masing-masing normal dan homogen. Data lengkap dan seimbang.",
  "Petak utama diuji terhadap galat (a), sedangkan anak petak dan interaksinya diuji terhadap galat (b). Anak petak biasanya lebih teliti.")

M("petak-terbagi-dua-kali-split-split-plot", "splitsplit", FAM_DES, "Rancangan Perlakuan", "Petak-Petak Terbagi (Split-Split-Plot)",
  "Tiga faktor bertingkat: petak utama, anak petak, dan anak-anak petak dengan tiga galat.",
  ["Tiga galat", "Tiga faktor"], ("de", "splitsplit"),
  [num("resp", "Variabel respon (numerik)", "Hasil"), cat("blk", "Kelompok (ulangan)", "Kelompok", 0),
   cat("main", "Petak utama", "Petak_Utama", 0), cat("sub", "Anak petak", "Anak_Petak", 0),
   cat("ss", "Anak-anak petak", "Anak_anak_Petak", 0)], run_splitsplit,
  "Pakai bila ada tiga faktor dengan tingkat kesulitan penerapan yang berbeda sehingga disusun bertingkat.",
  "Tiga galat berbeda, data lengkap dan seimbang, galat normal dan homogen pada tiap tingkat.",
  "Tiap tingkat faktor diuji terhadap galat tingkatnya sendiri. Faktor tingkat bawah biasanya diuji lebih peka.")

M("petak-jalur-strip-plot", "strip", FAM_DES, "Rancangan Perlakuan", "Petak Jalur (Strip-Plot)",
  "Dua faktor yang diterapkan pada jalur horizontal dan vertikal yang saling memotong.",
  ["Jalur silang", "Tiga galat"], ("de", "strip"),
  [num("resp", "Variabel respon (numerik)", "Hasil"), cat("blk", "Kelompok (ulangan)", "Kelompok", 0),
   cat("fa", "Faktor A (jalur horizontal)", "Faktor_A", 0), cat("fb", "Faktor B (jalur vertikal)", "Faktor_B", 0)], run_strip,
  "Pakai bila kedua faktor sulit diterapkan pada petak kecil, misalnya pengolahan tanah pada satu arah dan jenis irigasi pada arah tegak lurus.",
  "Data lengkap dan seimbang, galat normal dan homogen. Faktor A, faktor B, dan interaksinya diuji dengan galat berbeda.",
  "Faktor A diuji terhadap galat (a), B terhadap galat (b), dan interaksi A × B terhadap galat (c).")

M("rancangan-tersarang-nested", "nested", FAM_DES, "Rancangan Perlakuan", "Rancangan Tersarang (Nested)",
  "Faktor B bersarang dalam faktor A (misalnya pohon dalam lokasi), dengan komponen ragam.",
  ["B(A)", "Komponen ragam"], ("de", "nested"),
  [num("resp", "Variabel respon (numerik)", "Hasil"), cat("fa", "Faktor A (tingkat atas)", "Lokasi", 0),
   cat("fb", "Faktor B (tersarang dalam A)", "Pohon", 0),
   boolean("rnd", "Faktor B bersifat acak (random)", True, "Acak: A diuji terhadap B(A). Tetap: A diuji terhadap galat.")], run_nested,
  "Pakai bila level faktor B hanya bermakna di dalam satu level faktor A, misalnya pohon-pohon yang berbeda pada tiap lokasi.",
  "Galat normal dan homogen; bila B acak, efek B menyebar normal.",
  "Periksa efek B(A) lebih dulu. Komponen ragam menunjukkan seberapa besar keragaman berasal dari tiap tingkat.")

M("pengukuran-berulang-repeated-measures", "repeated", FAM_DES, "Pengukuran Berulang", "Pengukuran Berulang (Repeated Measures)",
  "Subjek yang sama diukur berulang kali; dilengkapi uji sphericity Mauchly dan koreksi Greenhouse-Geisser serta Huynh-Feldt.",
  ["Within-subject", "Sphericity", "GG · HF"], ("de", "repeated"),
  [num("resp", "Variabel respon (numerik)", "Respon"), cat("sub", "Subjek", "Subjek", 0),
   cat("wit", "Faktor within-subject (waktu/kondisi)", "Waktu", 0)], run_repeated,
  "Pakai bila subjek yang sama diukur pada beberapa waktu atau kondisi, sehingga pengamatan pada subjek yang sama berkorelasi.",
  "Sphericity (ragam selisih antar pasangan waktu sama), normalitas, dan data lengkap untuk setiap subjek.",
  "Bila sphericity dilanggar (Mauchly nyata), gunakan P yang dikoreksi Greenhouse-Geisser atau Huynh-Feldt.")

M("rancangan-cross-over", "crossover", FAM_DES, "Pengukuran Berulang", "Rancangan Cross-Over",
  "Tiap subjek menerima semua perlakuan secara bergantian menurut urutan tertentu, dengan efek periode dan carry-over.",
  ["Urutan", "Periode", "Carry-over"], ("de", "crossover"),
  [num("resp", "Variabel respon (numerik)", "Respon"), cat("seq", "Urutan (sequence)", "Urutan", 0), cat("sub", "Subjek", "Subjek", 0),
   cat("per", "Periode", "Periode", 0), cat("trt", "Perlakuan", "Perlakuan", 0)], run_crossover,
  "Pakai bila setiap subjek menjadi kontrolnya sendiri dengan menerima beberapa perlakuan pada periode berbeda.",
  "Tidak ada efek carry-over yang berarti (perlu masa pencucian yang cukup), galat normal dan homogen.",
  "Periksa efek perlakuan, periode, dan urutan. Efek urutan yang nyata dapat mengindikasikan carry-over.")

M("ancova-analisis-kovarians", "ancova", FAM_DES, "Peubah Pendamping & Multivariat", "ANCOVA (Analisis Kovarians)",
  "Membandingkan kelompok setelah memperhitungkan kovariat numerik, dengan uji kehomogenan kemiringan.",
  ["Kovariat", "Rata-rata terkoreksi", "Uji kemiringan"], ("de", "ancova"),
  [cat("grp", "Kelompok/perlakuan", "Perlakuan", 0), num("resp", "Variabel respon", "Pertambahan_Bobot"),
   num("cov", "Kovariat (numerik)", "Bobot_Awal", 0), select("adj", "Koreksi uji berpasangan", ["LSD", "Bonferroni"])], run_ancova,
  "Pakai bila ada variabel numerik yang memengaruhi respon dan tidak dapat dikendalikan, misalnya bobot awal ternak.",
  "Kemiringan regresi sama di semua kelompok (tidak ada interaksi kelompok × kovariat), hubungan linear, galat normal dan homogen.",
  "Periksa dulu uji kehomogenan kemiringan. Bila terpenuhi, bandingkan rata-rata terkoreksi antar kelompok.")

# ---- Regresi
M("diagnostik-regresi-tanpa-intersep", "diag", FAM_REG, "Dasar", "Regresi Linear Berganda & Diagnostik",
  "Regresi linear dengan uji asumsi lengkap: normalitas, heteroskedastisitas, autokorelasi, multikolinearitas, dan pengamatan berpengaruh.",
  ["OLS", "VIF · Cook's D", "Uji asumsi klasik"], ("rs", "diag"),
  [num("y", "Variabel dependen (Y)", "Hasil"), num_multi("xs", "Variabel independen (X)", ["Luas", "Pupuk", "Hujan"], min=1),
   boolean("ic", "Sertakan intersep (konstanta)", True, "Hilangkan centang untuk regresi melalui titik asal.")], run_diag,
  "Pakai untuk menjelaskan atau memprediksi satu variabel numerik dari satu atau lebih variabel numerik lain.",
  "Hubungan linear, galat normal dengan ragam konstan, tidak ada autokorelasi, dan tidak ada multikolinearitas berat antar variabel independen.",
  "Lihat R² dan uji F untuk kecocokan model keseluruhan, uji t untuk tiap koefisien, lalu periksa tabel uji asumsi dan pengamatan berpengaruh.")

M("regresi-dummy", "dummy", FAM_REG, "Dasar", "Regresi dengan Variabel Dummy",
  "Regresi dengan prediktor numerik dan kategorik; kategori diubah menjadi variabel dummy dengan kategori pertama sebagai referensi.",
  ["Dummy", "Referensi", "Koefisien per kategori"], ("rs", "dummy"),
  [num("y", "Variabel dependen (Y)", "Hasil"), num_multi("xn", "Variabel numerik (X)", ["Dosis"]),
   cat_multi("xc", "Variabel kategorik (dijadikan dummy)", ["Jenis_Pupuk", "Lokasi"])], run_dummy,
  "Pakai bila sebagian prediktor berupa kategori (jenis pupuk, lokasi, jenis kelamin) yang perlu dimasukkan ke model regresi.",
  "Sama seperti regresi linear: linearitas, galat normal dan homogen, bebas autokorelasi dan multikolinearitas.",
  "Koefisien dummy menunjukkan selisih rata-rata respon kategori tersebut terhadap kategori referensi, dengan variabel lain tetap.")

M("regresi-polinomial", "poly", FAM_REG, "Dasar", "Regresi Polinomial",
  "Model kurva berderajat tinggi dengan uji kenaikan derajat, pita kepercayaan, dan pemilihan derajat berdasarkan AIC/BIC.",
  ["Derajat 1–6", "AIC · BIC", "Pita kepercayaan"], ("rs", "poly"),
  [num("x", "Variabel independen (X)", "X", 0), num("y", "Variabel dependen (Y)", "Y"), integer("deg", "Derajat polinomial", 1, 6, 2),
   boolean("cen", "Pusatkan X (kurangi multikolinearitas)", True)], run_poly,
  "Pakai bila hubungan X dan Y melengkung, misalnya respon yang naik lalu turun terhadap dosis.",
  "Galat normal dan homogen, bentuk kurva memang polinomial, dan derajat tidak dinaikkan berlebihan (risiko overfitting).",
  "Pilih derajat terendah yang masih signifikan secara uji kenaikan derajat dan memiliki AIC/BIC kecil.")

M("regresi-nonlinear", "nonlin", FAM_REG, "Nonlinear", "Regresi Nonlinear",
  "Eksponensial, logaritmik, pangkat, logistik (pertumbuhan), Michaelis-Menten, dan Gompertz dengan perbandingan seluruh model.",
  ["6 model", "Nonlinear least squares", "Perbandingan AIC"], ("rs", "nonlin"),
  [num("x", "Variabel independen (X)", "Waktu", 0), num("y", "Variabel dependen (Y)", "Respon"),
   select("model", "Model nonlinear", list(rc.NL_MODELS.keys()), list(rc.NL_MODELS.keys())[3])], run_nonlin,
  "Pakai bila hubungan X dan Y mengikuti kurva dengan bentuk tertentu, seperti pertumbuhan atau kinetika enzim.",
  "Bentuk fungsi sesuai proses yang diamati, galat normal dan homogen, dan nilai awal yang wajar (dicari otomatis).",
  "Bandingkan AIC antar model; parameter dengan galat baku kecil lebih dapat dipercaya.")

for _kind, _title, _desc, _tags, _y, _when, _read in [
    ("logit", "Regresi Logistik Biner", "Respon dua kategori (0/1) dengan odds ratio, klasifikasi, dan kurva ROC.", ["Odds ratio", "ROC", "Klasifikasi"], "Beli",
     "Pakai bila respon berupa dua kategori, seperti ya/tidak, sembuh/tidak, atau beli/tidak beli.",
     "Odds ratio lebih dari 1 berarti peluang kejadian naik bila X naik; kurang dari 1 berarti turun. AUC mendekati 1 menunjukkan model membedakan kelompok dengan baik."),
    ("probit", "Regresi Probit", "Seperti logistik, dengan fungsi hubung normal baku; sering dipakai pada uji dosis-respon.", ["Probit", "ROC"], "Beli",
     "Pakai bila respon biner dan Anda lebih suka asumsi sebaran normal laten, umum pada bioassay.",
     "Koefisien menunjukkan perubahan skor-z peluang kejadian per satuan X."),
    ("poisson", "Regresi Poisson", "Respon cacahan (0, 1, 2, ...) dengan rate ratio dan uji overdispersi.", ["Rate ratio", "Overdispersi"], "Jumlah",
     "Pakai bila respon berupa hitungan kejadian, misalnya jumlah hama atau jumlah kunjungan.",
     "Exp(koefisien) adalah rate ratio. Periksa dispersi: bila jauh di atas 1, pertimbangkan binomial negatif."),
    ("negbin", "Regresi Binomial Negatif", "Untuk data cacahan dengan overdispersi (ragam lebih besar dari rata-rata).", ["Overdispersi", "Rate ratio"], "Jumlah",
     "Pakai bila data cacahan menunjukkan ragam jauh lebih besar dari rata-rata sehingga Poisson tidak cocok.",
     "Parameter dispersi α yang berbeda nyata dari 0 membenarkan model ini dibandingkan Poisson."),
    ("gamma", "Regresi Gamma", "Respon positif dan miring ke kanan (biaya, durasi) dengan fungsi hubung log.", ["Fungsi hubung log", "Respon positif"], "Biaya",
     "Pakai bila respon selalu positif dan menjulur ke kanan, seperti biaya, waktu tunggu, atau konsentrasi.",
     "Exp(koefisien) adalah rasio perubahan rata-rata respon per satuan X.")]:
    M("regresi-" + {"logit": "logistik-biner", "probit": "probit", "poisson": "poisson", "negbin": "binomial-negatif", "gamma": "gamma"}[_kind],
      _kind, FAM_REG, "GLM", _title, _desc, _tags, ("rs", _kind),
      [any_col("y", "Variabel dependen (Y)", _y)] + [num_multi("xn", "Variabel numerik (X)", None, auto=True),
                                                       cat_multi("xc", "Variabel kategorik (dummy)")] +
      ([number("cut", "Titik potong klasifikasi", 0.1, 0.9, 0.5, 0.05)] if _kind in ("logit", "probit") else []),
      _glm(_kind), _when,
      "Observasi saling bebas, fungsi hubung sesuai, dan tidak ada multikolinearitas berat. Jumlah kejadian sebaiknya cukup untuk jumlah prediktor.",
      _read)

import json as _json  # noqa: E402

META = _json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "meta.json"), encoding="utf-8"))
from . import registry_more  # noqa: E402,F401

_ORDER = {}
for _fam, _k in ((FAM_DES, "des"), (FAM_REG, "reg")):
    _legacy = ["ral", "rak"] if _fam == FAM_DES else ["reg"]
    _order = _legacy + [it["key"] for gs in META[_k].values() for it in gs]
    for _i, _key in enumerate(_order):
        _ORDER[(_fam, _key)] = _i
GROUP_ORDER = {FAM_DES: ["Rancangan Dasar"] + list(META["des"].keys()), FAM_REG: list(META["reg"].keys())}
_LABEL = {(f, it["key"]): it["label"] for f, k in ((FAM_DES, "des"), (FAM_REG, "reg")) for gs in META[k].values() for it in gs}
for _m in METHODS:
    _m.setdefault("gen", None)
    _m["title"] = _LABEL.get((_m["family"], _m["key"]), _m["title"])
    _m["label"] = _m["title"]
METHODS.sort(key=lambda m: (m["family"], GROUP_ORDER[m["family"]].index(m["group"]), _ORDER.get((m["family"], m["key"]), 999)))

BY_SLUG = {m["slug"]: m for m in METHODS}
BY_KEY = {(m["family"], m["key"]): m for m in METHODS}


def groups(family):
    out = {}
    for m in METHODS:
        if m["family"] == family:
            out.setdefault(m["group"], []).append(m)
    return out


def sample_df(m):
    src, kind = m["sample"]
    return {"se": se.sample_data, "de": de.sample_design, "rs": rs.sample_reg}[src](kind)
