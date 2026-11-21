"""nav.py – navigasi sidebar bertahap: Jenis analisis → Kelompok → Metode, plus pemandu "Bingung memilih metode?"."""
import html as _h

import streamlit as st

LEGACY_REG = dict(key="reg", label="Regresi Linear (sederhana & berganda)",
                  desc="Hubungan linear satu atau beberapa variabel X dengan Y: persamaan, uji F/t, R², uji asumsi klasik, dan kalkulator prediksi.")
LEGACY_DES = [
    dict(key="ral", label="Rancangan Acak Lengkap (RAL)",
         desc="Satu faktor pada satuan percobaan yang homogen: ANOVA, KK, dan uji lanjut BNT/DMRT/BNJ."),
    dict(key="rak", label="Rancangan Acak Kelompok (RAK)",
         desc="Satu faktor dengan pengelompokan (blok) untuk mengendalikan keragaman: ANOVA, efisiensi relatif, uji lanjut."),
]

# (situasi, metode, kelompok)
GUIDE_REG = [
    ("Y angka kontinu, hubungan lurus dan data biasa", "Regresi Linear (sederhana & berganda)", "Dasar"),
    ("Y angka kontinu, ada variabel kategori (jenis, lokasi)", "Regresi dengan Variabel Dummy", "Dasar"),
    ("Y angka kontinu, hubungan melengkung sederhana", "Regresi Polinomial", "Dasar"),
    ("Ingin memeriksa asumsi / pencilan model linear", "Diagnostik & Regresi Tanpa Intersep", "Dasar"),
    ("Hubungan berpola tertentu (pertumbuhan, saturasi, peluruhan)", "Regresi Nonlinear", "Nonlinear"),
    ("Y ya/tidak (0/1)", "Regresi Logistik Biner", "GLM"),
    ("Y kategori tanpa urutan (≥ 3 kelas)", "Regresi Logistik Multinomial", "GLM"),
    ("Y kategori berurutan (skala 1–5, rendah–tinggi)", "Regresi Logistik Ordinal", "GLM"),
    ("Y cacahan / jumlah kejadian (0, 1, 2, …)", "Regresi Poisson (atau Binomial Negatif bila ragam ≫ rata-rata)", "GLM"),
    ("Y positif dan condong ke kanan (biaya, durasi)", "Regresi Gamma", "GLM"),
    ("Banyak variabel X, ingin memilih yang penting", "Seleksi Variabel (atau LASSO)", "Seleksi & Regularisasi"),
    ("Variabel X saling berkorelasi kuat (multikolinearitas)", "Regresi Ridge / Elastic Net / PLS", "Seleksi & Regularisasi"),
    ("Ada pencilan (outlier) yang mengganggu", "Regresi Robust (Huber / Bisquare / LTS)", "Robust & Nonparametrik"),
    ("Bentuk hubungan tidak diketahui, ingin kurva mulus", "LOESS / Regresi Kernel / Spline / GAM", "Robust & Nonparametrik"),
    ("Ingin efek X pada kuantil (mis. kasus terbaik/terburuk)", "Regresi Kuantil", "Robust & Nonparametrik"),
    ("Individu/provinsi diamati berulang tiap periode", "Regresi Data Panel", "Data Terstruktur"),
    ("Data berurutan waktu dan galat berautokorelasi", "Regresi Deret Waktu (ARIMAX)", "Data Terstruktur"),
    ("Data punya koordinat lokasi", "Regresi Spasial (SAR/SEM) atau GWR", "Data Terstruktur"),
    ("Data bersarang/berkelompok (siswa dalam kelas, plot dalam lokasi)", "Mixed Effect Model", "Data Terstruktur"),
    ("Waktu hingga kejadian dengan data tersensor", "Regresi Cox (Survival)", "Data Terstruktur"),
    ("Y menumpuk di batas (mis. banyak bernilai 0)", "Regresi Tobit", "Data Terstruktur"),
]
GUIDE_DES = [
    ("Satu faktor, satuan percobaan homogen", "Rancangan Acak Lengkap (RAL)", "Rancangan Dasar"),
    ("Satu faktor, ada kelompok/blok (lokasi, waktu, ulangan)", "Rancangan Acak Kelompok (RAK)", "Rancangan Dasar"),
    ("Dua sumber keragaman sekaligus (baris dan kolom)", "Rancangan Bujur Sangkar Latin (RBSL)", "Rancangan Lingkungan"),
    ("Blok tidak cukup memuat semua perlakuan", "Blok Tidak Lengkap (BIB / Lattice)", "Rancangan Lingkungan"),
    ("Dua faktor atau lebih, ingin melihat interaksi", "Percobaan Faktorial", "Rancangan Perlakuan"),
    ("Faktor banyak tetapi unit percobaan terbatas", "Faktorial Pecahan", "Rancangan Perlakuan"),
    ("Satu faktor sulit diubah (petak besar) dan faktor lain pada petak kecil", "Petak Terbagi (Split-Plot)", "Rancangan Perlakuan"),
    ("Faktor B bersarang dalam A (pohon dalam lokasi)", "Rancangan Tersarang (Nested)", "Rancangan Perlakuan"),
    ("Subjek yang sama diukur berulang kali", "Pengukuran Berulang (Repeated Measures)", "Pengukuran Berulang"),
    ("Tiap subjek menerima semua perlakuan bergantian", "Rancangan Cross-Over", "Pengukuran Berulang"),
    ("Ada kovariat numerik (mis. bobot awal)", "ANCOVA", "Peubah Pendamping & Multivariat"),
    ("Beberapa respon diukur bersamaan", "MANOVA", "Peubah Pendamping & Multivariat"),
    ("Mencari kondisi optimum proses (suhu, waktu, dll.)", "Response Surface Methodology (RSM)", "Optimasi Proses"),
    ("Komponen campuran dengan total 100%", "Rancangan Campuran (Mixture)", "Optimasi Proses"),
    ("Rancangan kokoh dengan array ortogonal", "Metode Taguchi", "Optimasi Proses"),
]

TARGET_REG = [LEGACY_REG["label"], "Regresi dengan Variabel Dummy", "Regresi Polinomial", "Diagnostik & Regresi Tanpa Intersep", "Regresi Nonlinear",
              "Regresi Logistik Biner", "Regresi Logistik Multinomial", "Regresi Logistik Ordinal", "Regresi Poisson", "Regresi Gamma",
              "Seleksi Variabel", "Regresi Ridge", "Regresi Robust – M-estimator Huber", "LOESS / LOWESS", "Regresi Kuantil",
              "Regresi Data Panel", "Regresi Deret Waktu (ARIMAX)", "Regresi Spasial – SAR (Lag)", "Mixed Effect Model", "Regresi Cox (Survival)", "Regresi Tobit"]
TARGET_DES = [LEGACY_DES[0]["label"], LEGACY_DES[1]["label"], "Rancangan Bujur Sangkar Latin (RBSL)", "Blok Tidak Lengkap (BIB / Lattice)",
              "Percobaan Faktorial", "Faktorial Pecahan (Fractional Factorial)", "Petak Terbagi (Split-Plot)", "Rancangan Tersarang (Nested)",
              "Pengukuran Berulang (Repeated Measures)", "Rancangan Cross-Over", "ANCOVA (Analisis Kovarians)", "MANOVA",
              "Response Surface Methodology (RSM)", "Rancangan Campuran (Mixture)", "Metode Taguchi"]
assert len(TARGET_REG) == len(GUIDE_REG) and len(TARGET_DES) == len(GUIDE_DES)

FAMILY_REG = "📈 Regresi"
FAMILY_DES = "🧪 Rancangan Percobaan"


def _groups(reg_groups, des_groups):
    reg = {}
    reg["Dasar"] = [LEGACY_REG] + list(reg_groups.get("Dasar", []))
    for g, items in reg_groups.items():
        if g != "Dasar":
            reg[g] = list(items)
    des = {"Rancangan Dasar": list(LEGACY_DES)}
    for g, items in des_groups.items():
        des[g] = list(items)
    return reg, des


def _step(n, text):
    st.sidebar.markdown(f'<div class="step"><span>{n}</span>{_h.escape(text)}</div>', unsafe_allow_html=True)


def sidebar_nav(reg_groups, des_groups):
    """Mengembalikan (mode, kunci) dengan mode in {legacy, reg, design}."""
    import home
    page = st.sidebar.radio("Halaman", home.PAGES, key="page")
    if page != home.PAGE_APP:
        return "page", page
    st.sidebar.markdown('<hr style="margin:10px 0 0;border:none;border-top:1px solid #CFE0F3">', unsafe_allow_html=True)
    reg, des = _groups(reg_groups, des_groups)
    _step(1, "Pilih jenis analisis")
    family = st.sidebar.radio("Jenis analisis", [FAMILY_REG, FAMILY_DES], key="family", label_visibility="collapsed")
    groups, guide = (reg, GUIDE_REG) if family == FAMILY_REG else (des, GUIDE_DES)
    pre = "r" if family == FAMILY_REG else "d"

    _step(2, "Pilih kelompok metode")
    names = list(groups.keys())
    grp = st.sidebar.selectbox("Kelompok metode", names, key=f"{pre}_grp", label_visibility="collapsed",
                               format_func=lambda g: f"{g}  ({len(groups[g])})")
    _step(3, "Pilih metode")
    items = groups[grp]
    labels = {m["label"]: m for m in items}
    lab = st.sidebar.selectbox("Metode", list(labels.keys()), key=f"{pre}_m_{grp}", label_visibility="collapsed")
    m = labels[lab]
    st.sidebar.markdown(f'<div class="mcard"><b>{_h.escape(m["label"])}</b><br>{_h.escape(m["desc"])}</div>', unsafe_allow_html=True)

    with st.sidebar.expander("🤔 Bingung memilih metode?"):
        st.caption("Pilih situasi data Anda, lalu ikuti petunjuk metode yang disarankan.")
        sit = st.selectbox("Situasi data/percobaan saya", [g[0] for g in guide], key=f"{pre}_guide", label_visibility="collapsed")
        _, rec, path = [g for g in guide if g[0] == sit][0]
        st.markdown(f'<div class="rec"><span>Disarankan</span><b>{_h.escape(rec)}</b>'
                    f'<small>Menu: {_h.escape(family.split(" ", 1)[1])} › {_h.escape(path)}</small></div>', unsafe_allow_html=True)

    if m["key"] in ("reg", "ral", "rak"):
        return "legacy", m["key"]
    return ("reg" if family == FAMILY_REG else "design"), m["key"]


NAV_CSS = """<style>
.stApp .step {display:flex; align-items:center; gap:9px; font-weight:800; font-size:.92rem; color:#0F2A43 !important; margin:14px 0 4px;}
.stApp .step span {display:inline-flex; align-items:center; justify-content:center; width:22px; height:22px; border-radius:50%; background:#1D4ED8; color:#fff !important; font-size:.78rem;}
.stApp .mcard {background:#fff; border:1px solid #D5E3F3; border-left:4px solid #2563EB; border-radius:12px; padding:10px 13px; margin:8px 0 6px; font-size:.84rem; line-height:1.5; color:#334E68 !important;}
.stApp .mcard b {color:#0F2A43 !important; font-size:.92rem;}
.stApp .rec {background:#EAF2FF; border:1px solid #BCD3F2; border-radius:12px; padding:10px 13px; margin-top:6px; display:flex; flex-direction:column; gap:3px;}
.stApp .rec span {font-size:.7rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; color:#1D4ED8 !important;}
.stApp .rec b {color:#0B2545 !important; font-size:.95rem;}
.stApp .rec small {color:#52667D !important; font-size:.8rem;}
section[data-testid="stSidebar"] [data-testid="stRadio"] label {padding:2px 0;}
</style>"""
