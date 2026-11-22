"""flows.py – flowchart alur analisis untuk tiap metode (HTML/CSS murni, tanpa library tambahan)."""
import html as _h
try:
    import flows_en as _E
except ImportError:  # pragma: no cover
    _E = None

# Jenis simpul: in (data), proc (proses), chk (pemeriksaan + cabang), dec (keputusan + cabang), out (hasil)
ICON = {"in": "📥", "proc": "⚙️", "chk": "🧪", "dec": "🔀", "out": "📤"}
LABEL = {"in": "Data masuk", "proc": "Proses", "chk": "Pemeriksaan", "dec": "Keputusan", "out": "Hasil"}

# --------------------------------------------------------------------------
# Rancangan percobaan bertipe ANOVA: (data, model, uji F, hasil khusus)
# --------------------------------------------------------------------------
DES = {
    "ral": ("Satu faktor perlakuan pada satuan percobaan yang homogen; jumlah ulangan boleh tidak sama.",
            "Yᵢⱼ = μ + τᵢ + εᵢⱼ; jumlah kuadrat sekuensial.", "F = KT perlakuan ÷ KT galat (db galat = N − t).",
            "Tabel ANOVA, KK, rata-rata dengan notasi huruf."),
    "rak": ("Satu faktor dengan kelompok/blok (lokasi, waktu, ulangan); tiap perlakuan sekali per kelompok.",
            "Yᵢⱼ = μ + τᵢ + βⱼ + εᵢⱼ.", "F perlakuan dan F kelompok terhadap KT galat (db galat = (t−1)(r−1)).",
            "Tabel ANOVA, KK, efisiensi relatif terhadap RAL, notasi huruf."),
    "rbsl": ("t perlakuan tersusun t × t; tiap perlakuan muncul sekali pada setiap baris dan kolom.",
             "Y = μ + baris + kolom + perlakuan + galat.", "F perlakuan terhadap KT galat (db galat = (t−1)(t−2)).",
             "Tabel ANOVA, KK, notasi huruf, pengaruh baris dan kolom."),
    "graeco": ("t × t dengan tiga sumber pengelompokan: baris, kolom, dan huruf Yunani; perlakuan huruf Latin.",
               "Y = μ + baris + kolom + Yunani + perlakuan + galat.", "F perlakuan terhadap KT galat (db galat = (t−1)(t−3)).",
               "Tabel ANOVA, notasi huruf, efek setiap faktor pengelompok."),
    "bib": ("Blok tidak memuat semua perlakuan; tiap pasangan perlakuan bertemu λ kali (BIB) atau tersusun Lattice.",
            "Analisis intra-blok: perlakuan disesuaikan terhadap blok.", "F perlakuan (terkoreksi blok) terhadap galat intra-blok.",
            "ANOVA, rata-rata terkoreksi blok, uji berpasangan (LSD/Bonferroni), notasi huruf."),
    "factorial": ("2–4 faktor, semua kombinasi level, jumlah ulangan sama; opsional kelompok (RAK faktorial).",
                  "Efek utama + semua interaksi (+ kelompok).", "F setiap efek dan interaksi terhadap KT galat.",
                  "ANOVA, plot interaksi, rata-rata kombinasi dengan notasi huruf."),
    "split": ("Faktor petak utama dan anak petak dalam kelompok; ukuran satuan percobaan berbeda.",
              "Dua tingkat galat: Galat (a) untuk petak utama, Galat (b) untuk anak petak dan interaksi.",
              "F petak utama terhadap Galat (a); F anak petak dan interaksi terhadap Galat (b).", "ANOVA, KK (a) dan KK (b), notasi huruf."),
    "splitsplit": ("Tiga faktor bertingkat: petak utama, anak petak, anak-anak petak, dalam kelompok.",
                   "Tiga tingkat galat: (a), (b), (c).", "Setiap efek diuji terhadap galat tingkatnya sendiri.",
                   "ANOVA, KK (a), (b), (c), notasi huruf."),
    "strip": ("Dua faktor pada jalur horizontal dan vertikal yang bersilangan, dalam kelompok.",
              "Galat (a) untuk faktor A, Galat (b) untuk faktor B, Galat (c) untuk interaksi.",
              "F A terhadap Galat (a), F B terhadap Galat (b), F A×B terhadap Galat (c).", "ANOVA, tiga KK, notasi huruf."),
    "nested": ("Faktor B tersarang dalam A (mis. pohon dalam lokasi); B acak atau tetap.",
               "Y = μ + A + B(A) + galat.", "A diuji terhadap B(A) bila B acak; B(A) terhadap galat.",
               "ANOVA, komponen ragam (σ²), rata-rata tersarang."),
    "repeated": ("Subjek yang sama diukur pada beberapa waktu/kondisi (format panjang).",
                 "Y = μ + subjek + waktu + galat (within-subject).", "F waktu terhadap galat subjek × waktu; koreksi bila sphericity gagal.",
                 "ANOVA, Mauchly, ε Greenhouse-Geisser/Huynh-Feldt, uji berpasangan Bonferroni."),
    "crossover": ("Subjek menerima perlakuan bergantian antar periode pada urutan berbeda (2×2).",
                  "Y = μ + urutan + subjek(urutan) + periode + perlakuan + galat.", "Perlakuan & periode terhadap galat dalam-subjek; urutan terhadap galat antar-subjek.",
                  "ANOVA, selisih perlakuan terkoreksi periode & subjek, catatan carry-over."),
    "ancova": ("Respon, kelompok/perlakuan, dan satu kovariat numerik.",
               "Y = μ + perlakuan + b·kovariat + galat (kemiringan sejajar).", "F perlakuan setelah dikoreksi kovariat; F kovariat.",
               "ANOVA, rata-rata terkoreksi kovariat, uji berpasangan, notasi huruf."),
}
DES_ASSUME = {"repeated": ("Sphericity (Mauchly)", "Gunakan koreksi Greenhouse-Geisser/Huynh-Feldt atau MANOVA"),
              "ancova": ("Kemiringan regresi homogen antar kelompok", "Model berinteraksi / analisis per kelompok")}

# --------------------------------------------------------------------------
# Rancangan non-ANOVA: daftar simpul lengkap
# --------------------------------------------------------------------------
CUSTOM = {
    "manova": [("in", "Data", "Beberapa respon numerik, satu faktor (opsional blok)."),
               ("proc", "Matriks SSCP", "Hitung matriks jumlah kuadrat-hasil kali galat (E) dan hipotesis (H)."),
               ("chk", "Box's M", "Matriks kovarians homogen?", "Gunakan Pillai's trace (paling tahan pelanggaran)."),
               ("proc", "Uji multivariat", "Pillai, Wilks, Hotelling-Lawley, Roy → F aproksimasi."),
               ("dec", "Efek multivariat nyata?", "Lanjut ke ANOVA univariat per respon (P Bonferroni).", "Berhenti: vektor rata-rata tidak berbeda."),
               ("out", "Hasil", "Tabel multivariat, ANOVA univariat, rata-rata, korelasi respon.")],
    "rsm": [("in", "Data", "2–4 faktor numerik dan satu respon dari rancangan CCD atau Box-Behnken."),
            ("proc", "Pengkodean", "Ubah faktor ke skala terkode (−1, 0, +1)."),
            ("proc", "Model", "Regresi orde 1 atau kuadratik: β₀ + Σβᵢxᵢ + Σβᵢᵢxᵢ² + Σβᵢⱼxᵢxⱼ."),
            ("chk", "Lack-of-fit", "Model cukup tepat (P lack-of-fit > α)?", "Naikkan orde model atau tambah titik percobaan."),
            ("proc", "Titik stasioner", "Selesaikan ∇ŷ = 0; eigenvalue → maksimum / minimum / pelana."),
            ("dec", "Titik di dalam daerah percobaan?", "Pakai sebagai optimum.", "Gunakan optimum terbatas pada daerah percobaan."),
            ("out", "Hasil", "Koefisien, ANOVA, R² prediksi, plot kontur, optimum.")],
    "mixture": [("in", "Data", "Proporsi ≥ 3 komponen yang berjumlah tetap dan satu respon."),
                ("proc", "Model Scheffé", "Tanpa intersep: linear, kuadratik, atau special cubic."),
                ("chk", "Signifikansi model", "P model < α dan R² memadai?", "Pilih model dengan orde lebih tinggi."),
                ("proc", "Optimasi", "Cari komposisi pada simpleks yang memaksimumkan/meminimumkan respon."),
                ("out", "Hasil", "Koefisien, ANOVA, diagram segitiga, komposisi optimum.")],
    "taguchi": [("in", "Data", "Kolom level faktor kontrol (array ortogonal) dan beberapa replikasi respon."),
                ("proc", "Rasio S/N", "Larger-, smaller-the-better, atau nominal-the-best per run."),
                ("proc", "Rata-rata S/N per level", "Hitung respon utama tiap level faktor; delta dan peringkat."),
                ("proc", "ANOVA S/N", "Faktor berpengaruh kecil di-pool menjadi galat."),
                ("proc", "Kombinasi optimum", "Pilih level dengan S/N tertinggi; prediksi S/N optimum."),
                ("out", "Hasil", "Tabel S/N, peringkat faktor, ANOVA, kombinasi optimum, percobaan konfirmasi.")],
    "fracfact": [("in", "Data", "Faktor berkode −1/+1 dari desain 2^(k−p) dan satu respon."),
                 ("proc", "Struktur alias", "Efek yang tidak terpisahkan digabung dan ditulis dengan alias-nya."),
                 ("dec", "Ada derajat bebas galat?", "Uji t efek dengan KT galat.", "Gunakan metode Lenth (PSE) yang bersifat eksploratif."),
                 ("out", "Hasil", "Tabel efek, diagram Pareto, plot peluang normal efek.")],
}

# --------------------------------------------------------------------------
# Regresi: (data, model, estimasi, uji, pemeriksaan, jika gagal, hasil)
# --------------------------------------------------------------------------
REG = {
    "reg": ("Y numerik, satu/lebih X numerik.", "Y = β₀ + β₁X₁ + … + ε", "OLS (kuadrat terkecil).", "Uji F simultan, uji t per koefisien, R².",
            "Normalitas, homoskedastisitas, autokorelasi, multikolinearitas.", "Transformasi, metode robust, atau regresi lanjutan.", "Persamaan, tabel koefisien, kalkulator prediksi."),
    "dummy": ("Y numerik; X numerik dan kategorik.", "Kategori diubah menjadi dummy (level pertama = referensi).", "OLS.", "Uji t tiap dummy terhadap referensi, uji F.",
              "Asumsi OLS dan perhatian pada kategori jarang.", "Gabung kategori atau gunakan model campuran.", "Koefisien per kategori, persamaan, grafik."),
    "poly": ("Y numerik, satu X dengan hubungan melengkung.", "Y = β₀ + β₁X + β₂X² + … (derajat 1–6, X dipusatkan).", "OLS.", "Uji kenaikan derajat, AIC/BIC.",
             "Overfitting pada derajat tinggi; residual.", "Turunkan derajat atau gunakan spline/LOESS.", "Derajat terbaik, kurva dan pita kepercayaan."),
    "diag": ("Y numerik dan X numerik.", "Model linear (dengan atau tanpa intersep).", "OLS.", "Ringkasan model.",
             "Shapiro/JB/AD; BP/White/Glejser; DW/BG; VIF; Cook's D, leverage.", "Transformasi, robust, GLS, atau hapus variabel kolinear.", "Tabel setiap uji, pengamatan berpengaruh, grafik diagnostik."),
    "nonlin": ("Y dan X numerik dengan pola pertumbuhan/saturasi/peluruhan.", "Eksponensial, logaritmik, pangkat, logistik, Michaelis-Menten, Gompertz.", "Nonlinear least squares dengan nilai awal otomatis.",
               "Galat baku parameter, perbandingan AIC.", "Konvergensi dan sebaran residual.", "Ganti bentuk model.", "Parameter, kurva, perbandingan enam model."),
    "logit": ("Y biner (0/1); X numerik/kategorik.", "logit P(Y=1) = β₀ + ΣβX.", "Maximum likelihood (IRLS).", "Uji Wald, uji LR simultan.",
              "Hosmer-Lemeshow, separasi sempurna, multikolinearitas.", "Gabung kategori, regularisasi, atau tambah data.", "Odds ratio, tabel klasifikasi, ROC/AUC."),
    "probit": ("Y biner (0/1).", "Φ⁻¹(P) = β₀ + ΣβX.", "Maximum likelihood.", "Uji Wald, uji LR.", "Hosmer-Lemeshow dan klasifikasi.", "Coba logit atau tambah data.", "Koefisien, klasifikasi, ROC/AUC."),
    "multinom": ("Y nominal dengan ≥ 3 kelas.", "log(P_k / P_ref) = β_k₀ + β_kX.", "Maximum likelihood.", "Uji LR, uji Wald per koefisien.", "Separasi dan ukuran sampel per kelas.",
                 "Gabung kelas jarang.", "Koefisien tiap kelas, odds ratio relatif, akurasi."),
    "ordinal": ("Y kategori berurutan.", "Proportional odds: logit P(Y ≤ k) = θ_k − Xβ.", "Maximum likelihood.", "Uji Wald, uji LR.",
                "Asumsi proportional odds.", "Gunakan multinomial.", "Koefisien, ambang, odds ratio, matriks konfusi."),
    "poisson": ("Y cacahan (0, 1, 2, …).", "log(μ) = β₀ + ΣβX.", "Maximum likelihood (IRLS).", "Uji Wald, deviance.", "Overdispersi (deviance/db ≫ 1).", "Gunakan binomial negatif.", "Incidence rate ratio, kecocokan."),
    "negbin": ("Y cacahan dengan ragam > rata-rata.", "log(μ) = β₀ + ΣβX; ragam μ + αμ².", "Maximum likelihood (α ikut diduga).", "Uji Wald, AIC; dispersi α.", "Kecocokan model.", "Gunakan model zero-inflated bila banyak nol.", "IRR, parameter dispersi α."),
    "gamma": ("Y positif dan condong ke kanan.", "log(μ) = β₀ + ΣβX; ragam ∝ μ².", "Maximum likelihood (IRLS).", "Uji Wald, deviance.", "Sebaran residual deviance.", "Transformasi log + OLS.", "exp(β), kecocokan."),
    "select": ("Y numerik dan banyak kandidat X.", "Model linear dengan himpunan X terpilih.", "Forward, backward, stepwise, atau best subset.", "Kriteria AIC/BIC tiap langkah.",
               "Stabilitas pilihan dan multikolinearitas.", "Gunakan LASSO bila kandidat banyak.", "Jejak seleksi, model akhir, perbandingan model."),
    "ridge": ("Y numerik, X banyak/berkorelasi.", "OLS + penalti λΣβ².", "Bentuk tertutup; λ dari validasi silang.", "RMSE validasi silang.", "Jalur koefisien.", "Coba LASSO/Elastic Net.", "Koefisien menyusut, λ optimum."),
    "lasso": ("Y numerik, banyak X.", "OLS + penalti λΣ|β|.", "Coordinate descent; λ dari validasi silang.", "RMSE validasi silang.", "Variabel terpilih stabil?", "Elastic Net bila X berkorelasi.", "Variabel terpilih, jalur koefisien."),
    "enet": ("Y numerik, X berkorelasi.", "Campuran penalti L1 dan L2 (rasio L1 diatur).", "Coordinate descent; λ dari validasi silang.", "RMSE validasi silang.", "Pilihan rasio L1.", "Ubah rasio L1.", "Koefisien dan jalur."),
    "pcr": ("Y numerik, X sangat berkorelasi.", "Regresi pada komponen utama X.", "PCA lalu OLS; jumlah komponen dari validasi silang.", "RMSE validasi silang.", "Varians yang dijelaskan.", "Gunakan PLS.", "Komponen, loading, koefisien asal."),
    "pls": ("Y numerik, X banyak/berkorelasi.", "Komponen laten dengan kovarians maksimum terhadap Y.", "NIPALS; jumlah komponen dari validasi silang.", "RMSE validasi silang.", "Varians X dan Y.", "Ubah jumlah komponen.", "Komponen, VIP, koefisien."),
    "huber": ("Y dan X numerik dengan pencilan.", "M-estimator Huber.", "IRLS dengan bobot Huber.", "Galat baku sandwich.", "Bobot pengamatan.", "Gunakan bisquare/LTS bila pencilan ekstrem.", "Koefisien robust vs OLS, bobot."),
    "bisquare": ("Y dan X numerik dengan pencilan ekstrem.", "M-estimator Tukey bisquare.", "IRLS.", "Galat baku sandwich.", "Bobot nol = dibuang.", "LTS bila pencilan banyak.", "Koefisien dan bobot."),
    "lts": ("Y dan X numerik, pencilan hingga ≈ 50%.", "Meminimumkan jumlah kuadrat residual terkecil (trimmed).", "Banyak awal acak + langkah konsentrasi.", "Skala MAD, galat baku.", "Daftar pencilan.", "—", "Koefisien LTS, pencilan terdeteksi."),
    "kernel": ("Y dan X numerik, bentuk hubungan bebas.", "Regresi lokal berbobot kernel (Gaussian/Epanechnikov/tricube).", "Bandwidth h dari validasi silang.", "Pita kepercayaan.", "Over/undersmoothing.", "Ubah bandwidth.", "Kurva mulus."),
    "loess": ("Y dan X numerik.", "Polinomial lokal derajat 1–2 dengan kernel tricube.", "Span dari validasi silang (LOO); iterasi robust opsional.", "Pita kepercayaan aproksimasi.", "Residual.", "Naikkan span.", "Kurva LOESS."),
    "spline": ("Y dan X numerik.", "Natural cubic atau truncated power spline.", "Knot otomatis; kuadrat terkecil.", "R², AIC/BIC, perbandingan dengan model linear.", "Posisi knot.", "Ubah jumlah knot.", "Kurva spline dan pita."),
    "quantile": ("Y dan X numerik; ragam tidak konstan atau ekor penting.", "Q_τ(Y|X) = β₀(τ) + β(τ)X untuk beberapa τ.", "Pemrograman linear; galat baku bootstrap.", "Selang kepercayaan per kuantil.", "Perbedaan koefisien antar kuantil.", "—", "Koefisien tiap τ, plot koefisien vs τ."),
    "gam": ("Y numerik; X dengan efek mulus dan/atau linear.", "Y = β₀ + Σs(Xⱼ) + Σβₖ Xₖ.", "Penalized spline, GCV memilih kehalusan.", "Derajat bebas efektif (edf) tiap s(), R².", "Residual.", "Kurangi basis.", "Kurva s(X), R² vs model linear."),
    "panel": ("Entitas × periode; Y dan X numerik.", "Common, Fixed, dan Random Effect (Swamy-Arora).", "Pooled OLS, within, dan GLS.", "Uji Chow, Breusch-Pagan LM, Hausman.",
              "Pemilihan model dari rangkaian uji.", "—", "Model terbaik, koefisien tiga model, efek individu."),
    "ts": ("Data berurutan waktu; Y dan X eksogen.", "Regresi dengan galat ARIMA(p,d,q).", "Conditional sum of squares (BFGS).", "Galat baku Hessian, AIC/BIC.", "Ljung-Box dan ACF galat.", "Naikkan p/q atau d.", "Koefisien, AR/MA, prediksi 1 langkah."),
    "sar": ("Data berlokasi (koordinat); Y dan X.", "Y = ρWY + Xβ + ε.", "Maximum likelihood terkonsentrasi.", "Uji LM-lag, LR terhadap OLS.", "Moran's I residual.", "Coba SEM atau GWR.", "ρ, efek langsung/tidak langsung/total."),
    "sem": ("Data berlokasi (koordinat).", "Y = Xβ + u, u = λWu + ε.", "Maximum likelihood terkonsentrasi.", "Uji LM-error, LR.", "Moran's I residual.", "Coba SAR.", "λ, koefisien, peta."),
    "gwr": ("Data berlokasi; relasi berubah antar lokasi.", "Koefisien lokal β(uᵢ, vᵢ).", "Kernel bisquare adaptif; bandwidth via CV.", "AICc vs OLS, % lokasi nyata.", "Nonstasioneritas spasial.", "Gunakan model global bila AICc tak lebih baik.", "Peta koefisien dan R² lokal."),
    "mixed": ("Data berkelompok/bersarang; Y dan X.", "Efek tetap + intersep (dan slope) acak per kelompok.", "REML.", "LRT efek acak, uji t efek tetap.", "ICC, residual.", "Gunakan OLS bila ICC kecil.", "Efek tetap, komponen ragam, ICC, BLUP."),
    "cox": ("Waktu, status (1/0), dan kovariat.", "h(t|X) = h₀(t)·exp(Xβ).", "Partial likelihood (Breslow).", "LR dan Wald; HR dan selang kepercayaan.", "Proportional hazards (Grambsch-Therneau).", "Stratifikasi atau interaksi dengan waktu.", "Hazard ratio, C-index, kurva KM dan survival."),
    "tobit": ("Y tersensor (kiri/kanan); X numerik.", "Y* = Xβ + ε, Y = max(Y*, batas).", "Maximum likelihood tersensor.", "Uji LR, Wald.", "Perbandingan dengan OLS.", "—", "Koefisien laten, efek marjinal."),
}


def nodes_for(key, family, lang="id"):
    """Daftar simpul: (tipe, judul, detail, cabang_tidak=None)."""
    if lang == "en":
        import flows_en as E
        DES_, DA_, CU_, RE_, G = E.DES, E.DES_ASSUME, E.CUSTOM, E.REG, E.GEN
    else:
        DES_, DA_, CU_, RE_, G = DES, DES_ASSUME, CUSTOM, REG, None
    if family == "des":
        if key in CU_:
            return CU_[key]
        if key in DES_:
            data, model, ftest, out = DES_[key]
            en = G is not None
            nodes = [("in", G["data"] if en else "Data", data), ("proc", G["model"] if en else "Model", model), ("proc", G["anova"] if en else "Analisis ragam", ftest)]
            if key in DA_:
                a, alt = DA_[key]
                nodes.append(("chk", a, G["assume_ok"] if en else "Asumsi terpenuhi?", alt))
            nodes += [("chk", G["assump"] if en else "Asumsi galat", G["assump_d"] if en else "Normalitas (Shapiro-Wilk) dan homogenitas ragam (Levene) terpenuhi?",
                       G["assump_no"] if en else "Transformasi (log/akar) atau uji nonparametrik."),
                      ("dec", G["ftest"] if en else "Uji F nyata?", G["ftest_yes"] if en else "Uji lanjut: BNT, DMRT, Tukey, Scheffé, atau Dunnett → notasi huruf.",
                       G["ftest_no"] if en else "Berhenti: perlakuan tidak berbeda nyata."),
                      ("out", G["result"] if en else "Hasil", out)]
            return nodes
    if family == "reg" and key in RE_:
        data, model, est, tests, chk, alt, out = RE_[key]
        en = G is not None
        nodes = [("in", "Data", data), ("proc", "Model", model), ("proc", G["estimation"] if en else "Penaksiran", est), ("proc", G["testing"] if en else "Pengujian", tests)]
        nodes.append(("chk", G["checks"] if en else "Pemeriksaan & validasi", chk, alt) if alt != "—" else ("proc", G["checks2"] if en else "Pemeriksaan", chk))
        nodes.append(("out", G["result"] if en else "Hasil", out))
        return nodes
    if G:
        return G["fallback"]
    return [("in", "Data", "Pilih kolom yang sesuai."), ("proc", "Analisis", "Metode dijalankan."), ("out", "Hasil", "Tabel, grafik, interpretasi.")]


def flow_html(nodes, lang="id"):
    parts = ['<div class="flow">']
    for i, n in enumerate(nodes):
        typ, title, detail = n[0], n[1], n[2]
        no = n[3] if len(n) > 3 else None
        parts.append(f'<div class="fnode {typ}"><div class="fh"><span class="fi">{ICON[typ]}</span>'
                     f'<span class="fk">{(_E.LABEL if lang == "en" else LABEL)[typ]}</span><b>{_h.escape(title)}</b></div><div class="fd">{_h.escape(detail)}</div>')
        if typ in ("chk", "dec") and no:
            yes = ("Continue to the next step" if lang == "en" else "Lanjut ke langkah berikutnya") if typ == "chk" else detail
            if typ == "dec":
                parts[-1] = parts[-1].replace(f'<div class="fd">{_h.escape(detail)}</div>', '<div class="fd">' + ("Yes / No?" if lang == "en" else "Ya / Tidak?") + '</div>')
            parts.append(f'<div class="fbr"><span class="y">{"✔ Yes → " if lang == "en" else "✔ Ya → "}{_h.escape(yes)}</span><span class="n">{"✖ No → " if lang == "en" else "✖ Tidak → "}{_h.escape(no)}</span></div>')
        parts.append('</div>')
        if i < len(nodes) - 1:
            parts.append('<div class="farrow"><svg width="18" height="26" viewBox="0 0 18 26"><path d="M9 0v20M3 14l6 8 6-8" fill="none" stroke="#2563EB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')
    parts.append('</div>')
    return "".join(parts)


FLOW_CSS = """<style>
.stApp .flow {max-width:760px; margin:8px auto 6px; display:flex; flex-direction:column; align-items:stretch;}
.stApp .farrow {display:flex; justify-content:center; height:30px; align-items:center;}
.stApp .fnode {background:#fff; border:1px solid #D5E3F3; border-left:6px solid #2563EB; border-radius:16px; padding:13px 18px; box-shadow:0 6px 18px rgba(30,64,120,.08);}
.stApp .fnode.in {border-left-color:#2563EB; background:linear-gradient(120deg,#FFFFFF,#EEF5FF);}
.stApp .fnode.proc {border-left-color:#0D9488;}
.stApp .fnode.chk {border-left-color:#F59E0B; background:linear-gradient(120deg,#FFFFFF,#FFF9EB);}
.stApp .fnode.dec {border-left-color:#7C3AED; background:linear-gradient(120deg,#FFFFFF,#F6F1FF);}
.stApp .fnode.out {border-left-color:#16A34A; background:linear-gradient(120deg,#FFFFFF,#EDFBF3);}
.stApp .fh {display:flex; align-items:center; gap:9px; flex-wrap:wrap;}
.stApp .fk {font-size:.68rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; color:#52667D !important; background:#EEF4FC; border-radius:999px; padding:2px 9px;}
.stApp .fh b {color:#0F2A43 !important; font-size:1.02rem;}
.stApp .fd {color:#41566F !important; font-size:.93rem; line-height:1.55; margin-top:5px;}
.stApp .fbr {display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px;}
.stApp .fbr span {border-radius:10px; padding:7px 11px; font-size:.84rem; line-height:1.45; font-weight:600;}
.stApp .fbr .y {background:#DCFCE7; color:#14532D !important;}
.stApp .fbr .n {background:#FEE2E2; color:#7F1D1D !important;}
@media (max-width:640px){.stApp .fbr {grid-template-columns:1fr;}}
</style>"""
