# StatCalc – Dashboard Analisis Statistika

Kalkulator analisis statistika berbasis Streamlit: pilih kategori dan metode, masukkan data (contoh / unggah CSV-Excel / input manual),
lalu lihat tabel, grafik, interpretasi otomatis, dan unduh hasil ke Excel.

## Analisis

**Dasar** – Regresi Linear (sederhana, berganda, tanpa intersep), RAL, RAK.

**Rancangan Percobaan Lanjutan**
- Lingkungan: RBSL (Latin square), Graeco-Latin, Blok Tidak Lengkap (BIB/Lattice)
- Perlakuan: Faktorial (2–4 faktor), Faktorial Pecahan, Split-plot, Split-split-plot, Strip-plot, Nested
- Pengukuran berulang: Repeated Measures (Mauchly, GG/HF), Cross-Over
- ANCOVA, MANOVA
- Optimasi: RSM (CCD, Box-Behnken), Mixture, Taguchi
- Uji lanjut pada semua rancangan: BNT/LSD, DMRT, Tukey (BNJ), Scheffé, Dunnett

**Regresi Lanjutan**
- Dasar: dummy, polinomial, diagnostik lengkap (normalitas, heteroskedastisitas, autokorelasi, VIF, Cook's D/leverage), tanpa intersep
- Nonlinear: eksponensial, logaritmik, pangkat, logistik, Michaelis-Menten, Gompertz
- GLM: logistik biner/multinomial/ordinal, probit, Poisson, binomial negatif, gamma
- Seleksi & regularisasi: forward, backward, stepwise, best subset, Ridge, LASSO, Elastic Net, PCR, PLS
- Robust & nonparametrik: Huber, Bisquare, LTS, kernel, LOESS, spline, kuantil, GAM
- Data terstruktur: panel (Common/Fixed/Random + Chow, BP-LM, Hausman), ARIMAX, spasial (SAR, SEM, GWR, Moran's I), mixed effect (REML), Cox, Tobit

## Menjalankan
```
pip install -r requirements.txt
streamlit run app.py
```

## Struktur
- `app.py` – tampilan utama, menu, dan halaman Regresi Linear / RAL / RAK
- `stats_engine.py` – perhitungan RAL, RAK, uji lanjut, regresi linear (statsmodels)
- `design_engine.py` – mesin rancangan percobaan lanjutan (ANOVA sekuensial, numpy/scipy)
- `posthoc_ext.py` – uji lanjut Scheffé dan Dunnett
- `reg_core.py`, `reg_models1.py`, `reg_models2.py`, `reg_models3.py` – mesin regresi lanjutan (numpy/scipy)
- `reg_samples.py` – data contoh regresi
- `ui_core.py`, `pages_reg.py`, `pages_design.py` – penggambar grafik dan halaman tiap metode
- `requirements.txt`, `.streamlit/config.toml`

## Formulir Masukan (opsional, untuk developer)
Masukan pengguna disimpan sebagai baris CSV di repo GitHub **privat** milik Anda lewat GitHub API.
1. Buat repo privat baru, mis. `statcalc-masukan` (boleh kosong; berkas dibuat otomatis).
2. GitHub › Settings › Developer settings › Fine-grained tokens: buat token khusus repo tersebut dengan izin **Contents: Read and write**.
3. Streamlit Cloud › App › Settings › Secrets, isi:
```
[feedback]
token  = "github_pat_xxx"
repo   = "username/statcalc-masukan"
path   = "masukan.csv"
branch = "main"
```
4. Jangan commit token. Lokal: simpan di `.streamlit/secrets.toml` (sudah ada di `.gitignore`).
Tanpa secrets, halaman Masukan menampilkan pemberitahuan bahwa fitur belum aktif.
