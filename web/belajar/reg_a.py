from . import T

S = "Tahap 3 · Regresi"


def R(slug, title, ringkas, tujuan, ide, rumus, langkah, baca, jebakan, latihan, pra=()):
    return T(slug, title, ringkas, tujuan, ide, rumus, langkah, baca, jebakan, latihan, pra=pra, tahap=S, method=slug)


R("regresi-linear-sederhana-berganda", "Regresi Linear (Sederhana dan Berganda)",
  "Menyatakan Y sebagai fungsi linear satu atau beberapa X dan mengujinya.",
  ["Memahami model dan penaksiran kuadrat terkecil", "Membaca uji F, uji t, dan R²", "Memakai kalkulator prediksi dengan CI dan PI"],
  ["Regresi linear mencari garis (atau bidang) yang meminimalkan jumlah kuadrat residual. Koefisien βⱼ menyatakan perubahan rata-rata Y bila Xⱼ naik satu satuan dengan variabel lain tetap.",
   "Uji F menilai apakah model secara keseluruhan lebih baik daripada hanya memakai rata-rata Y. Uji t menilai tiap koefisien. R² adalah proporsi keragaman Y yang dijelaskan; R² adjusted menghukum penambahan variabel yang tidak berguna."],
  [("Model", "Y = β₀ + β₁X₁ + … + βₖXₖ + ε"), ("Penaksir", "b = (XᵀX)⁻¹ Xᵀy"), ("R²", "R² = 1 − JKG / JKT"), ("Uji t", "t = bⱼ / SE(bⱼ), db = n − k − 1")],
  ["Gambar diagram pencar.", "Pilih Y dan X, jalankan regresi.", "Baca uji F, R², dan koefisien.", "Periksa asumsi dan pengamatan berpengaruh.", "Gunakan tab Prediksi bila tujuannya meramal."],
  ["Koefisien positif berarti Y naik bila X naik; bacalah dalam satuan aslinya.", "Beta terstandar membantu membandingkan pengaruh antar X berbeda satuan.", "R² tinggi tidak menjamin model benar; periksa residual."],
  ["Memakai model di luar rentang X (ekstrapolasi).", "Menyimpulkan sebab-akibat dari korelasi.", "Menambah variabel hanya untuk menaikkan R²."],
  "Jalankan data contoh, lalu buka tab Prediksi dan masukkan nilai X di dalam dan di luar rentang data; bandingkan lebar CI dan PI serta baca peringatan ekstrapolasi.",
  pra=["dasar-korelasi", "dasar-asumsi-residual"])

R("regresi-dummy", "Regresi dengan Variabel Dummy",
  "Memasukkan prediktor kategori ke regresi dengan mengubahnya menjadi variabel 0/1.",
  ["Memahami kodifikasi dummy dan kategori referensi", "Membaca koefisien dummy", "Menghindari jebakan variabel dummy"],
  ["Kategori tidak bisa langsung dimasukkan ke persamaan. Untuk faktor dengan m kategori dibuat m − 1 variabel dummy bernilai 0 atau 1; satu kategori menjadi referensi.",
   "Koefisien dummy menyatakan selisih rata-rata respon kategori itu terhadap kategori referensi, dengan variabel lain tetap. Regresi dengan dummy setara dengan ANOVA, dan menjadi ANCOVA bila bercampur dengan prediktor numerik."],
  [("Model", "Y = β₀ + β₁D₁ + β₂D₂ + … + γX + ε"), ("Arti β₀", "rata-rata Y kategori referensi (saat X = 0)")],
  ["Tentukan kategori referensi (kalkulator: kategori pertama).", "Pilih respon, prediktor numerik, dan prediktor kategori.", "Baca koefisien dan ujinya."],
  ["Koefisien D positif: kategori itu lebih tinggi daripada referensi.", "Mengganti referensi mengubah koefisien tetapi tidak mengubah prediksi model."],
  ["Memasukkan m dummy sekaligus bersama intersep (dummy variable trap).", "Mengira koefisien dummy membandingkan dua kategori non-referensi.", "Kategori dengan observasi sangat sedikit."],
  "Jalankan data contoh, catat kategori referensi, lalu hitung sendiri selisih rata-rata respon kategori lain terhadap referensi dan cocokkan dengan koefisien.",
  pra=["regresi-linear-sederhana-berganda"])

R("regresi-polinomial", "Regresi Polinomial",
  "Model kurva melengkung dengan menambahkan pangkat X.",
  ["Memahami model berderajat tinggi", "Memilih derajat dengan uji kenaikan derajat dan AIC/BIC", "Mengenal bahaya overfitting"],
  ["Bila hubungan X dan Y melengkung, tambahkan X², X³, dan seterusnya. Model tetap linear pada koefisiennya sehingga dapat ditaksir dengan kuadrat terkecil.",
   "Derajat dipilih serendah mungkin yang masih nyata. Derajat terlalu tinggi mengikuti derau (overfitting) dan berperilaku liar di ujung rentang."],
  [("Model", "Y = β₀ + β₁X + β₂X² + … + β_dX^d + ε"), ("AIC", "AIC = n·ln(JKG/n) + 2p")],
  ["Lihat diagram pencar.", "Coba derajat 1 sampai maksimum yang wajar.", "Gunakan uji kenaikan derajat dan AIC/BIC.", "Pilih derajat terendah yang memadai."],
  ["Suku derajat tertinggi nyata: kenaikan derajat bermanfaat.", "AIC/BIC terendah dipilih; bila berbeda, utamakan BIC untuk model lebih sederhana."],
  ["Memilih derajat tinggi hanya karena R² naik.", "Ekstrapolasi.", "Kolinearitas antar suku pangkat; pusatkan X bila perlu."],
  "Jalankan data contoh dan bandingkan derajat 1, 2, dan 3. Pilih satu dan jelaskan alasannya dengan AIC serta uji kenaikan derajat.",
  pra=["regresi-linear-sederhana-berganda"])

R("diagnostik-regresi-tanpa-intersep", "Diagnostik dan Regresi Tanpa Intersep",
  "Pemeriksaan asumsi regresi secara lengkap, plus model melalui titik asal.",
  ["Melakukan uji normalitas, heteroskedastisitas, autokorelasi, dan multikolinearitas", "Membaca Cook's D dan leverage", "Mengetahui kapan intersep dihilangkan"],
  ["Diagnostik regresi memeriksa asumsi klasik: normalitas residual (Shapiro-Wilk, Jarque-Bera, Anderson-Darling), ragam konstan (Breusch-Pagan, White, Glejser), tanpa autokorelasi (Durbin-Watson, Breusch-Godfrey), dan tanpa multikolinearitas (VIF).",
   "Pengamatan berpengaruh diperiksa lewat Cook's D dan leverage. Regresi tanpa intersep memaksa garis melewati titik asal; hanya dipakai bila secara teori Y = 0 ketika X = 0, dan R² tidak sebanding dengan model berintersep."],
  [("Durbin-Watson", "DW ≈ 2 berarti tanpa autokorelasi"), ("VIF", "VIFⱼ = 1 / (1 − Rⱼ²); > 10 bermasalah"), ("Cook's D", "batas kasar 4/n")],
  ["Jalankan model dan baca tabel uji asumsi.", "Lihat grafik residual dan Cook's D.", "Periksa VIF tiap prediktor.", "Perbaiki: transformasi, hapus variabel kolinear, atau metode robust."],
  ["P > α pada uji asumsi berarti tidak ada bukti pelanggaran.", "Cook's D di atas batas berarti pengamatan itu berpengaruh besar; telusuri sebabnya."],
  ["Mengandalkan satu uji saja.", "Membuang pengamatan berpengaruh tanpa alasan substantif.", "Menghilangkan intersep untuk menaikkan R²."],
  "Jalankan data contoh dan susun tabel kecil: asumsi apa saja yang terpenuhi, yang tidak, dan tindakan yang Anda sarankan.",
  pra=["dasar-asumsi-residual", "regresi-linear-sederhana-berganda"])

R("regresi-nonlinear", "Regresi Nonlinear",
  "Kurva pertumbuhan dan kinetik yang tidak linear pada parameternya.",
  ["Mengenal enam model umum", "Membandingkan model dengan AIC", "Membaca parameter biologis"],
  ["Beberapa proses mengikuti kurva yang tidak linear pada parameter: pertumbuhan eksponensial, logistik, dan Gompertz; kinetik enzim Michaelis-Menten; serta bentuk logaritmik dan pangkat.",
   "Penaksiran dilakukan dengan kuadrat terkecil nonlinear secara iteratif dari nilai awal. Parameter bermakna fisik (asimtot, laju, titik belok), sehingga mudah ditafsirkan."],
  [("Logistik", "Y = K / (1 + e^(−r(x − x₀)))"), ("Michaelis-Menten", "Y = Vmax·x / (Km + x)"), ("Eksponensial", "Y = a·e^(bx)")],
  ["Lihat bentuk pencar data.", "Jalankan seluruh model dan lihat perbandingan AIC.", "Pilih model yang masuk akal secara teori dan AIC rendah.", "Baca parameter dan galat bakunya."],
  ["AIC lebih kecil = model lebih baik secara relatif.", "Galat baku kecil berarti parameter dapat dipercaya."],
  ["Nilai awal buruk membuat iterasi tidak konvergen.", "Memilih model hanya dari R².", "Memakai data yang tidak mencakup fase penting (misalnya belum mencapai asimtot)."],
  "Jalankan data contoh dan bandingkan seluruh model. Pilih satu dan jelaskan makna biologis parameternya.",
  pra=["regresi-polinomial"])

R("regresi-logistik-biner", "Regresi Logistik Biner",
  "Memodelkan peluang kejadian dua kategori (0/1) dari prediktor.",
  ["Memahami fungsi hubung logit dan odds ratio", "Membaca uji Wald, uji LR, dan Hosmer-Lemeshow", "Menilai model dengan tabel klasifikasi dan ROC/AUC"],
  ["Bila respon hanya dua kemungkinan (sembuh/tidak, lulus/tidak), regresi linear tidak cocok karena prediksi bisa keluar dari [0,1]. Regresi logistik memodelkan log odds sebagai fungsi linear X.",
   "Koefisien dibaca lewat odds ratio, OR = e^β: faktor pengali odds kejadian untuk kenaikan satu satuan X."],
  [("Model", "ln[p / (1 − p)] = β₀ + β₁X₁ + … + βₖXₖ"), ("Peluang", "p = 1 / (1 + e^−(β₀ + βX))"), ("Odds ratio", "OR = e^β")],
  ["Kodekan respon sebagai 0/1.", "Jalankan model dan baca koefisien serta OR.", "Periksa Hosmer-Lemeshow untuk kecocokan.", "Nilai daya diskriminasi dengan ROC/AUC."],
  ["OR > 1: kejadian lebih mungkin bila X naik; OR < 1: kurang mungkin; OR = 1: tidak berpengaruh.", "AUC 0,5 sama dengan menebak; mendekati 1 berarti membedakan dengan baik.", "Hosmer-Lemeshow tidak nyata berarti kecocokan memadai."],
  ["Menyebut OR sebagai risiko relatif.", "Terlalu sedikit kejadian per prediktor.", "Pemisahan sempurna (perfect separation) membuat koefisien tak hingga."],
  "Jalankan data contoh, hitung peluang prediksi untuk satu kasus dari koefisien secara manual, lalu cocokkan dengan intuisi dari OR.",
  pra=["regresi-linear-sederhana-berganda"])

R("regresi-probit", "Regresi Probit",
  "Seperti logistik, tetapi memakai fungsi hubung normal baku.",
  ["Memahami fungsi hubung probit", "Membandingkannya dengan logit", "Membaca hasil dosis-respon"],
  ["Probit memodelkan peluang dengan fungsi sebaran normal baku: Φ⁻¹(p) = β₀ + βX. Bentuknya mirip logit, dengan ekor sedikit lebih ringan.",
   "Probit lazim di toksikologi dan uji dosis-respon, misalnya menaksir LD50, yaitu dosis yang membunuh 50% individu."],
  [("Model", "Φ⁻¹(p) = β₀ + β₁X"), ("LD50", "x = −β₀ / β₁")],
  ["Kodekan respon 0/1 atau proporsi.", "Jalankan model.", "Baca koefisien dalam skor-z dan klasifikasinya.", "Bandingkan dengan logit bila perlu."],
  ["Koefisien menyatakan perubahan skor-z peluang per satuan X.", "Prediksi logit dan probit umumnya sangat mirip."],
  ["Membaca koefisien sebagai odds ratio.", "Memilih probit hanya karena kebiasaan.", "Data dosis tanpa rentang yang memuat respon 50%."],
  "Jalankan data contoh pada probit dan logit, lalu bandingkan peluang prediksinya untuk beberapa nilai X.",
  pra=["regresi-logistik-biner"])

R("regresi-logistik-multinomial", "Regresi Logistik Multinomial",
  "Respon nominal dengan tiga kelas atau lebih.",
  ["Memahami kelas referensi", "Membaca odds ratio relatif", "Menilai akurasi klasifikasi"],
  ["Untuk respon nominal tanpa urutan (jenis pilihan, kategori penyakit), model membandingkan tiap kelas dengan satu kelas referensi lewat sekumpulan persamaan logit.",
   "Exp(β) adalah odds ratio relatif: perubahan odds berada di kelas itu dibanding kelas referensi, untuk kenaikan satu satuan X."],
  [("Model", "ln[P(kelas j) / P(referensi)] = β₀ⱼ + β₁ⱼX₁ + …")],
  ["Tentukan kelas referensi.", "Jalankan model.", "Baca OR relatif tiap kelas.", "Periksa akurasi klasifikasi."],
  ["OR relatif dibaca terhadap kelas referensi, bukan terhadap kelas lain.", "Akurasi yang tinggi harus dibandingkan dengan proporsi kelas terbesar."],
  ["Memakai pada data ordinal (lebih tepat logistik ordinal).", "Kelas dengan sedikit data.", "Menafsirkan OR tanpa menyebut referensi."],
  "Jalankan data contoh, ganti pembacaan referensi, dan jelaskan satu odds ratio relatif dengan kalimat sendiri.",
  pra=["regresi-logistik-biner"])

R("regresi-logistik-ordinal", "Regresi Logistik Ordinal",
  "Respon berurutan (rendah, sedang, tinggi) dengan asumsi proportional odds.",
  ["Memahami model odds proporsional", "Membaca threshold", "Menafsirkan odds ratio kumulatif"],
  ["Respon ordinal memanfaatkan urutan kategori. Model memodelkan odds kumulatif berada pada kategori ≤ j. Satu set koefisien berlaku untuk semua ambang, asumsi proportional odds, sedangkan intersep (threshold) berbeda tiap batas.",
   "Koefisien positif menaikkan peluang berada pada kategori lebih tinggi; exp(β) adalah odds ratio kumulatif."],
  [("Model", "ln[P(Y ≤ j) / P(Y > j)] = θⱼ − βX")],
  ["Pastikan kategori terurut benar.", "Jalankan model.", "Baca β, OR kumulatif, dan threshold.", "Periksa uji kecocokan."],
  ["Threshold memisahkan kategori yang berdekatan.", "OR kumulatif sama untuk semua ambang berkat asumsi odds proporsional."],
  ["Urutan kategori terbalik.", "Asumsi odds proporsional dilanggar.", "Kategori terlalu jarang."],
  "Jalankan data contoh dan terjemahkan satu koefisien ke bahasa sehari-hari.",
  pra=["regresi-logistik-multinomial"])

R("regresi-poisson", "Regresi Poisson",
  "Memodelkan data cacahan (0, 1, 2, ...) dengan rate ratio.",
  ["Memahami fungsi hubung log", "Membaca incidence rate ratio", "Memeriksa overdispersi"],
  ["Data cacahan seperti jumlah kejadian, kunjungan, atau spesimen memiliki ragam yang bergantung pada rata-rata. Regresi Poisson memodelkan ln(rata-rata) sebagai fungsi linear X, dengan asumsi ragam = rata-rata.",
   "Exp(β) adalah rate ratio: faktor pengali rata-rata cacahan untuk kenaikan satu satuan X."],
  [("Model", "ln(μ) = β₀ + β₁X₁ + …"), ("Rate ratio", "IRR = e^β"), ("Dispersi", "φ = deviance / db; ≈ 1 sesuai asumsi")],
  ["Pastikan respon bilangan bulat tak negatif.", "Jalankan model.", "Periksa dispersi.", "Bila φ jauh di atas 1, pindah ke binomial negatif."],
  ["IRR 1,2 berarti rata-rata cacahan naik 20% per satuan X.", "Overdispersi membuat galat baku terlalu kecil sehingga uji terlalu mudah nyata."],
  ["Mengabaikan overdispersi.", "Cacahan dari jangka paparan berbeda tanpa offset.", "Banyak nol berlebihan."],
  "Jalankan data contoh dan periksa dispersi; putuskan apakah model sudah memadai.",
  pra=["regresi-logistik-biner"])

R("regresi-binomial-negatif", "Regresi Binomial Negatif",
  "Alternatif Poisson bila ragam cacahan lebih besar daripada rata-rata.",
  ["Memahami overdispersi", "Membaca parameter dispersi α", "Memilih antara Poisson dan binomial negatif"],
  ["Pada banyak data cacahan nyata, ragam melebihi rata-rata (overdispersi) karena ada heterogenitas yang tidak teramati. Binomial negatif menambah parameter dispersi α yang menaikkan ragam: Var = μ + αμ².",
   "Bila α nyata berbeda dari 0, binomial negatif lebih layak dibandingkan Poisson."],
  [("Ragam", "Var(Y) = μ + αμ²"), ("Rate ratio", "IRR = e^β")],
  ["Jalankan Poisson dan periksa dispersi.", "Bila overdispersi, jalankan binomial negatif.", "Baca α dan IRR.", "Bandingkan AIC."],
  ["α > 0 nyata membenarkan model ini.", "IRR dibaca seperti pada Poisson."],
  ["Memakai pada cacahan dengan banyak nol berlebih tanpa mempertimbangkan model zero-inflated.", "Mengabaikan perbandingan dengan Poisson."],
  "Jalankan data contoh pada Poisson dan binomial negatif dan bandingkan galat baku serta AIC.",
  pra=["regresi-poisson"])

R("regresi-gamma", "Regresi Gamma",
  "Respon kontinu positif dan miring ke kanan seperti biaya atau durasi.",
  ["Memahami sebaran gamma dan fungsi hubung log", "Membaca rasio perubahan rata-rata", "Memilih GLM gamma dibandingkan transformasi log"],
  ["Respon positif yang condong ke kanan (biaya, lama rawat, durasi) tidak cocok dengan galat normal. Regresi gamma memodelkan rata-rata respon dengan fungsi hubung log dan koefisien variasi tetap.",
   "Exp(β) adalah rasio perubahan rata-rata respon per satuan X."],
  [("Model", "ln(μ) = β₀ + β₁X₁ + …"), ("Ragam", "Var(Y) = φμ²")],
  ["Pastikan respon > 0.", "Jalankan model dan periksa residual.", "Baca exp(β) sebagai rasio.", "Bandingkan dengan regresi pada ln(Y) bila perlu."],
  ["exp(β) = 1,10 berarti rata-rata respon naik 10% per satuan X.", "Deviance dan residual menilai kecocokan."],
  ["Respon bernilai nol atau negatif.", "Menafsirkan β sebagai perubahan absolut.", "Mengabaikan pengaruh pencilan."],
  "Jalankan data contoh dan jelaskan satu koefisien sebagai persen perubahan.",
  pra=["regresi-poisson"])
