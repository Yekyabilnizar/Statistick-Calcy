"""home.py – halaman Beranda, Panduan Metode, dan Tentang (seperti situs web: pengantar sebelum masuk ke analisis)."""
import html as _h

import streamlit as st

import nav

PAGE_HOME, PAGE_APP, PAGE_GUIDE, PAGE_FLOW, PAGE_FB, PAGE_ABOUT = "🏠 Beranda", "📊 Analisis", "🧭 Panduan Metode", "🗺️ Alur Metode", "💬 Masukan", "ℹ️ Tentang"
PAGES = [PAGE_HOME, PAGE_APP, PAGE_GUIDE, PAGE_FLOW, PAGE_FB, PAGE_ABOUT]

HOME_CSS = """<style>
.stApp .sec-h {font-size:1.7rem; font-weight:800; color:#0F2A43 !important; margin:34px 0 4px; line-height:1.2;}
.stApp .sec-s {color:#52667D !important; font-size:1.02rem; margin:0 0 16px; max-width:820px; line-height:1.6;}
.stApp .stat-row {display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:14px; margin:6px 0 10px;}
.stApp .stat {background:#fff; border:1px solid #D5E3F3; border-radius:18px; padding:18px 20px; text-align:center; box-shadow:0 6px 18px rgba(30,64,120,.07);}
.stApp .stat b {display:block; font-size:2.1rem; font-weight:800; color:#1D4ED8 !important; line-height:1.1;}
.stApp .stat span {color:#52667D !important; font-size:.88rem; font-weight:600;}
.stApp .steps {display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:16px;}
.stApp .stepc {background:#fff; border:1px solid #D5E3F3; border-radius:20px; padding:22px 24px; box-shadow:0 6px 18px rgba(30,64,120,.07); position:relative;}
.stApp .stepc .n {display:inline-flex; width:38px; height:38px; border-radius:12px; background:linear-gradient(120deg,#1D4ED8,#0E7FA8); color:#fff !important; font-weight:800; align-items:center; justify-content:center; margin-bottom:10px;}
.stApp .stepc h4 {margin:0 0 6px; font-size:1.1rem; color:#0F2A43 !important;}
.stApp .stepc p {margin:0; color:#41566F !important; line-height:1.6; font-size:.95rem;}
.stApp .feat {display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:14px;}
.stApp .featc {background:linear-gradient(160deg,#FFFFFF,#F3F8FF); border:1px solid #D5E3F3; border-radius:18px; padding:18px 20px;}
.stApp .featc i {font-style:normal; font-size:1.5rem;}
.stApp .featc h5 {margin:6px 0 4px; font-size:1rem; color:#0F2A43 !important;}
.stApp .featc p {margin:0; color:#41566F !important; font-size:.92rem; line-height:1.55;}
.stApp .fam {border-radius:24px; padding:28px 30px; color:#fff !important; min-height:190px; box-shadow:0 14px 34px rgba(30,64,120,.22);}
.stApp .fam.a {background:linear-gradient(135deg,#1E3A8A,#2563EB 70%,#38BDF8);}
.stApp .fam.b {background:linear-gradient(135deg,#0F4C5C,#0D9488 70%,#5EEAD4);}
.stApp .fam h3 {color:#fff !important; border:none !important; padding:0 !important; margin:0 0 8px; font-size:1.5rem;}
.stApp .fam p, .stApp .fam li {color:#EAF4FF !important; line-height:1.6; font-size:.96rem;}
.stApp .fam ul {margin:8px 0 0; padding-left:18px;}
.stApp .mrow {display:flex; flex-wrap:wrap; gap:8px; margin:4px 0 8px;}
.stApp .mrow span {background:#fff; border:1px solid #CFE0F3; color:#1E3A8A !important; border-radius:999px; padding:4px 12px; font-size:.84rem; font-weight:700;}
.stApp .foot {text-align:center; color:#64748B !important; font-size:.85rem; margin:40px 0 6px;}
.stApp .read {width:100%; border-collapse:separate; border-spacing:0; background:#fff; border:1px solid #D5E3F3; border-radius:14px; overflow:hidden; font-size:.94rem;}
.stApp .read td, .stApp .read th {padding:10px 14px; border-bottom:1px solid #E8EFF8; color:#0F2A43 !important; text-align:left; vertical-align:top;}
.stApp .read th {background:#16325C; color:#fff !important; font-size:.76rem; letter-spacing:.06em; text-transform:uppercase;}
</style>"""



LEGAL_CSS = """<style>
.stApp .legal-note {display:flex; gap:10px; align-items:flex-start; background:rgba(255,255,255,.6); border:1px solid #D5E3F3; border-radius:12px; padding:9px 14px; margin:22px 0 8px; font-size:.84rem; color:#52667D !important; line-height:1.5;}
.stApp .legal-note b {color:#334E68 !important;}
.stApp .legal h5 {margin:14px 0 4px; color:#0F2A43 !important; font-size:1rem;}
.stApp .legal p, .stApp .legal li {color:#334E68 !important; font-size:.93rem; line-height:1.65;}
</style>"""

DISCLAIMER_SHORT = ("<b>Penafian:</b> hasil bersifat alat bantu analisis, bukan pengganti konsultasi dengan ahli statistika. "
                    "Pengguna bertanggung jawab atas pemilihan metode, kebenaran data, dan penggunaan hasilnya.")

PRIVACY_HTML = """<div class="legal">
<h5>Kebijakan Privasi</h5>
<ul>
<li><b>Data yang Anda masukkan</b> (unggahan file atau input manual) hanya diproses di memori selama sesi berjalan untuk menghitung hasil. Aplikasi ini tidak menyimpan data Anda ke basis data atau berkas permanen, dan tidak membagikannya kepada pihak lain.</li>
<li><b>Penyedia hosting</b> dapat mencatat data teknis standar (mis. alamat IP, waktu akses, log kesalahan) sesuai kebijakan mereka sendiri. Aplikasi tidak menambahkan pelacak atau iklan.</li>
<li><b>Jangan mengunggah data pribadi sensitif</b> (identitas, data kesehatan individual, dan sejenisnya) tanpa persetujuan dan anonimisasi yang layak. Gunakan kode atau ID samaran untuk subjek penelitian.</li>
<li><b>Formulir Masukan:</b> bila Anda mengirim masukan, isi pesan, jenis masukan, metode terkait, penilaian, dan kontak (jika Anda isi) disimpan di repositori privat milik pengembang yang hanya dapat diakses pengembang, semata-mata untuk memperbaiki aplikasi. Data analisis yang Anda unggah tidak ikut tersimpan. Untuk meminta penghapusan masukan Anda, hubungi pengembang.</li>
<li>Berkas Excel hasil unduhan dibuat di sesi Anda dan menjadi tanggung jawab Anda sepenuhnya setelah diunduh.</li>
<li>Kebijakan ini dapat diperbarui sewaktu-waktu; versi terbaru selalu ditampilkan di halaman ini.</li>
</ul>
<h5>Penafian</h5>
<ul>
<li><b>Hasil bersifat alat bantu, bukan pengganti konsultasi statistika.</b> Keputusan penelitian, kebijakan, medis, keuangan, atau hukum tidak boleh didasarkan semata-mata pada keluaran aplikasi ini.</li>
<li>Pemilihan metode, pemenuhan asumsi, dan interpretasi tetap menjadi tanggung jawab pengguna. Interpretasi otomatis bersifat umum dan tidak mempertimbangkan konteks penelitian Anda.</li>
<li>Perhitungan dikerjakan dengan sungguh-sungguh dan diuji, tetapi tidak ada jaminan bebas dari kesalahan. Untuk publikasi ilmiah atau pengambilan keputusan penting, verifikasi dengan perangkat lunak statistik lain dan konsultasikan dengan ahli statistika.</li>
<li>Aplikasi disediakan "apa adanya" tanpa jaminan tersurat maupun tersirat. Pengelola tidak bertanggung jawab atas kerugian yang timbul dari penggunaan aplikasi atau hasilnya.</li>
</ul></div>"""


def legal_block(expanded=False):
    """Penafian ringkas + kebijakan privasi dalam expander (tidak mengganggu tampilan utama)."""
    st.markdown(LEGAL_CSS, unsafe_allow_html=True)
    st.markdown(f'<div class="legal-note"><span>⚖️</span><div>{DISCLAIMER_SHORT}</div></div>', unsafe_allow_html=True)
    with st.expander("🔒 Kebijakan Privasi & Penafian lengkap", expanded=expanded):
        st.markdown(PRIVACY_HTML, unsafe_allow_html=True)


def _go(page=PAGE_APP, family=None, group=None, label=None):
    """Callback tombol: pindah halaman (dan opsional langsung memilih metode)."""
    st.session_state["page"] = page
    if family:
        st.session_state["family"] = family
        pre = "r" if family == nav.FAMILY_REG else "d"
        if group:
            st.session_state[f"{pre}_grp"] = group
            if label:
                st.session_state[f"{pre}_m_{group}"] = label


SEARCH_CSS = """<style>
.stApp .st-key-hero_searchbox {position:relative; z-index:60; height:0; margin:0 0 -1rem 0; overflow:visible;}
.stApp .st-key-hero_searchbox [data-testid="stSelectbox"] {position:absolute; top:20px; right:26px; width:min(400px,62%);}
.stApp .st-key-hero_searchbox [data-baseweb="select"] > div {border-radius:999px !important; background:#fff !important; border:1px solid rgba(255,255,255,.7) !important;
    box-shadow:0 8px 22px rgba(15,42,67,.25); min-height:42px; padding-left:6px;}
.stApp .st-key-hero_searchbox [data-baseweb="select"] input, .stApp .st-key-hero_searchbox [data-baseweb="select"] div {font-size:.9rem;}
@media (max-width:760px) {
  .stApp .st-key-hero_searchbox {height:auto; margin:0;}
  .stApp .st-key-hero_searchbox [data-testid="stSelectbox"] {position:static; width:100%;}
}
</style>"""


def _search_items(reg_groups, des_groups):
    """Daftar yang bisa dicari: metode (dengan kelompoknya) dan halaman informasi."""
    reg, des = _catalog(reg_groups, des_groups)
    items = []
    for fam, groups, short in ((nav.FAMILY_DES, des, "Rancangan"), (nav.FAMILY_REG, reg, "Regresi")):
        for g, ms in groups.items():
            for m in ms:
                items.append((f"{m['label']}  ·  {short} › {g}", ("m", fam, g, m["label"])))
    for p in (PAGE_GUIDE, PAGE_FLOW, PAGE_FB, PAGE_ABOUT):
        items.append((p, ("p", p)))
    return items


def _search_go(items):
    i = st.session_state.get("hero_search")
    if i is None:
        return
    tgt = items[i][1]
    if tgt[0] == "p":
        _go(tgt[1])
    else:
        _go(PAGE_APP, tgt[1], tgt[2], tgt[3])
    st.session_state["hero_search"] = None


def search_overlay(reg_groups, des_groups):
    """Kotak pencarian di pojok kanan atas banner; memilih hasil langsung membuka metode/halamannya."""
    st.markdown(SEARCH_CSS, unsafe_allow_html=True)
    items = _search_items(reg_groups, des_groups)
    with st.container(key="hero_searchbox"):
        st.selectbox("Cari metode", list(range(len(items))), index=None, key="hero_search",
                     format_func=lambda i: items[i][0], placeholder="🔍 Cari metode… (mis. logistik, RAK, panel)",
                     label_visibility="collapsed", on_change=_search_go, args=(items,))


def _head(title, sub=None):
    st.markdown(f'<div class="sec-h">{_h.escape(title)}</div>' + (f'<div class="sec-s">{_h.escape(sub)}</div>' if sub else ""),
                unsafe_allow_html=True)


def _catalog(reg_groups, des_groups):
    reg, des = nav._groups(reg_groups, des_groups)
    return reg, des


def method_buttons(groups, family, prefix):
    """Katalog metode: tiap kelompok berisi kartu metode dengan tombol 'Buka'."""
    for gi, (g, items) in enumerate(groups.items()):
        st.markdown(f'<div class="sec-s" style="margin:18px 0 6px"><b style="color:#0F2A43">{_h.escape(g)}</b> · {len(items)} metode</div>',
                    unsafe_allow_html=True)
        for i in range(0, len(items), 3):
            cols = st.columns(3)
            for c, m in zip(cols, items[i:i + 3]):
                with c:
                    with st.container(border=True):
                        st.markdown(f"**{m['label']}**")
                        st.caption(m["desc"] if len(m["desc"]) < 130 else m["desc"][:127] + "…")
                        st.button("Buka →", key=f"{prefix}_{gi}_{m['key']}", on_click=_go, args=(PAGE_APP, family, g, m["label"]))


def page_home(reg_groups, des_groups, hero):
    st.markdown(HOME_CSS, unsafe_allow_html=True)
    reg, des = _catalog(reg_groups, des_groups)
    n_reg, n_des = sum(len(v) for v in reg.values()), sum(len(v) for v in des.values())
    hero("Dari data ke kesimpulan, tanpa menulis kode",
         "StatCalc adalah kalkulator analisis statistika untuk penelitian dan percobaan: pilih metode, masukkan data, lalu dapatkan tabel, "
         "grafik, uji asumsi, dan interpretasi otomatis dalam bahasa Indonesia.",
         ["Rancangan percobaan", "Regresi", "Interpretasi otomatis", "Unduh Excel"])
    c1, c2, c3 = st.columns([1.3, 1.3, 2])
    c1.button("🚀 Mulai analisis", key="cta_start", type="primary", on_click=_go, use_container_width=True)
    c2.button("🧭 Bingung memilih metode?", key="cta_guide", on_click=_go, args=(PAGE_GUIDE,), use_container_width=True)

    st.markdown(f'''<div class="stat-row">
<div class="stat"><b>{n_reg + n_des}</b><span>metode analisis</span></div>
<div class="stat"><b>{n_des}</b><span>rancangan percobaan</span></div>
<div class="stat"><b>{n_reg}</b><span>metode regresi</span></div>
<div class="stat"><b>5</b><span>uji lanjut (BNT, DMRT, Tukey, Scheffé, Dunnett)</span></div></div>''', unsafe_allow_html=True)

    _head("Cara menggunakan", "Tiga langkah dari data mentah sampai laporan yang siap dipakai.")
    st.markdown('''<div class="steps">
<div class="stepc"><div class="n">1</div><h4>Pilih metode</h4><p>Pilih jenis analisis dan metodenya di sidebar. Tidak yakin? Buka <b>Panduan Metode</b> dan pilih situasi data Anda.</p></div>
<div class="stepc"><div class="n">2</div><h4>Masukkan data</h4><p>Pakai data contoh untuk mencoba, unggah file CSV/Excel, atau ketik langsung di tabel. Lalu pilih kolom untuk Y, X, perlakuan, atau kelompok.</p></div>
<div class="stepc"><div class="n">3</div><h4>Baca hasil</h4><p>Tabel ANOVA/koefisien, grafik, uji asumsi, dan interpretasi otomatis tampil seketika. Unduh semuanya ke Excel.</p></div></div>''',
                unsafe_allow_html=True)

    _head("Dua keluarga analisis")
    a, b = st.columns(2)
    with a:
        st.markdown(f'''<div class="fam b"><h3>🧪 Rancangan Percobaan</h3><p>Analisis ragam untuk percobaan terkontrol, dari RAL dan RAK sampai
rancangan lanjutan.</p><ul><li>RAL, RAK, RBSL, Graeco-Latin, BIB/Lattice</li><li>Faktorial, split-plot, strip-plot, nested</li>
<li>Repeated measures, cross-over, ANCOVA, MANOVA</li><li>RSM, mixture, Taguchi, faktorial pecahan</li></ul></div>''', unsafe_allow_html=True)
        st.button("Jelajahi rancangan percobaan →", key="go_des", on_click=_go, args=(PAGE_APP, nav.FAMILY_DES, "Rancangan Dasar", nav.LEGACY_DES[0]["label"]),
                  use_container_width=True)
    with b:
        st.markdown('''<div class="fam a"><h3>📈 Regresi</h3><p>Dari regresi linear sederhana sampai model untuk data biner, cacahan,
panel, spasial, dan survival.</p><ul><li>Linear, dummy, polinomial, nonlinear, diagnostik lengkap</li><li>Logistik, Poisson, binomial negatif, gamma, probit</li>
<li>Ridge, LASSO, robust, LOESS, spline, kuantil, GAM</li><li>Panel, ARIMAX, SAR/SEM/GWR, mixed effect, Cox, Tobit</li></ul></div>''', unsafe_allow_html=True)
        st.button("Jelajahi metode regresi →", key="go_reg", on_click=_go, args=(PAGE_APP, nav.FAMILY_REG, "Dasar", nav.LEGACY_REG["label"]),
                  use_container_width=True)

    _head("Yang Anda dapatkan di setiap analisis")
    st.markdown('''<div class="feat">
<div class="featc"><i>📋</i><h5>Tabel siap kutip</h5><p>ANOVA, koefisien, hazard ratio, uji lanjut bernotasi huruf, lengkap dengan P-value dan tanda signifikansi.</p></div>
<div class="featc"><i>🧪</i><h5>Uji asumsi</h5><p>Normalitas, homogenitas ragam, autokorelasi, multikolinearitas, dan pengamatan berpengaruh diperiksa otomatis.</p></div>
<div class="featc"><i>📈</i><h5>Grafik interaktif</h5><p>Plot residual, interaksi, kontur permukaan respon, peta spasial, kurva survival, dan lainnya.</p></div>
<div class="featc"><i>📝</i><h5>Interpretasi otomatis</h5><p>Kesimpulan ditulis dalam bahasa Indonesia, termasuk peringatan jika asumsi atau data bermasalah.</p></div>
<div class="featc"><i>📂</i><h5>Data fleksibel</h5><p>Data contoh, unggah CSV/Excel, atau input manual di tabel yang bisa disalin-tempel dari Excel.</p></div>
<div class="featc"><i>⬇️</i><h5>Unduh ke Excel</h5><p>Semua tabel hasil dikemas dalam satu berkas Excel; grafik dapat disimpan sebagai gambar.</p></div></div>''', unsafe_allow_html=True)

    _head("Katalog metode", "Klik “Buka” pada metode yang ingin dipakai; Anda langsung diarahkan ke halaman analisisnya.")
    t1, t2 = st.tabs(["🧪 Rancangan Percobaan", "📈 Regresi"])
    with t1:
        method_buttons(des, nav.FAMILY_DES, "hd")
    with t2:
        method_buttons(reg, nav.FAMILY_REG, "hr")

    _head("Pertanyaan umum")
    with st.expander("Apakah data saya disimpan?"):
        st.write("Tidak. Data hanya diproses selama sesi Anda berjalan untuk menghitung hasil dan tidak disimpan oleh aplikasi.")
    with st.expander("Format data seperti apa yang dibutuhkan?"):
        st.write("Satu baris = satu pengamatan, satu kolom = satu variabel, dan baris pertama berisi nama kolom. "
                 "Gunakan titik sebagai desimal. Lihat tab 'Data contoh' di tiap metode untuk format yang diharapkan.")
    with st.expander("Bagaimana membaca tanda ** , * , dan tn?"):
        st.write("** = sangat nyata (P < 0,01), * = nyata (P < 0,05), tn = tidak nyata. Taraf nyata α dapat diubah di sidebar.")
    with st.expander("Hasil saya berbeda dengan software lain"):
        st.write("Periksa jenis jumlah kuadrat (aplikasi memakai Tipe I sekuensial pada data seimbang), kategori referensi pada variabel dummy, "
                 "dan metode penaksiran (mis. REML pada mixed model). Pada data seimbang, hasil ANOVA umumnya sama dengan software lain; verifikasi tetap dianjurkan untuk publikasi.")
    legal_block()
    st.markdown('<div class="foot">StatCalc · Kalkulator analisis statistika</div>', unsafe_allow_html=True)


def page_guide(reg_groups, des_groups, hero):
    st.markdown(HOME_CSS, unsafe_allow_html=True)
    reg, des = _catalog(reg_groups, des_groups)
    hero("Panduan Memilih Metode", "Pilih situasi data atau percobaan Anda; kami tunjukkan metode yang cocok dan membukanya langsung.",
         ["Rancangan percobaan", "Regresi"])
    tabs = st.tabs(["🧪 Rancangan Percobaan", "📈 Regresi"])
    for tab, guide, targets, fam, pre in ((tabs[0], nav.GUIDE_DES, nav.TARGET_DES, nav.FAMILY_DES, "gd"), (tabs[1], nav.GUIDE_REG, nav.TARGET_REG, nav.FAMILY_REG, "gr")):
        with tab:
            st.markdown('<div class="sec-s">Cari baris yang paling mirip dengan kondisi Anda.</div>', unsafe_allow_html=True)
            for i, (sit, rec, grp) in enumerate(guide):
                c1, c2, c3 = st.columns([3, 3, 1.2])
                c1.markdown(f"**{sit}**")
                c2.markdown(f"➜ {rec}  \n<small style='color:#64748B'>{grp}</small>", unsafe_allow_html=True)
                lab = targets[i]
                c3.button("Buka", key=f"{pre}_{i}", on_click=_go, args=(PAGE_APP, fam, grp, lab))
                st.divider()


def page_about(hero):
    st.markdown(HOME_CSS, unsafe_allow_html=True)
    hero("Tentang StatCalc", "Cara membaca hasil, asumsi perhitungan, dan batasan yang perlu diketahui.", ["Panduan membaca hasil"])
    _head("Cara membaca hasil")
    st.markdown('''<table class="read"><thead><tr><th>Istilah</th><th>Arti</th></tr></thead><tbody>
<tr><td><b>** / * / tn</b></td><td>Sangat nyata (P&lt;0,01) / nyata (P&lt;0,05) / tidak nyata.</td></tr>
<tr><td><b>KK</b></td><td>Koefisien keragaman = akar KT galat ÷ rata-rata umum × 100%. Makin kecil makin teliti percobaannya.</td></tr>
<tr><td><b>Notasi huruf</b></td><td>Rata-rata yang diikuti huruf sama tidak berbeda nyata pada uji lanjut yang dipilih.</td></tr>
<tr><td><b>R², R² adj</b></td><td>Proporsi keragaman Y yang dijelaskan model (adj = disesuaikan jumlah variabel).</td></tr>
<tr><td><b>VIF</b></td><td>Ukuran multikolinearitas; &gt; 10 menandakan masalah serius.</td></tr>
<tr><td><b>AIC / BIC</b></td><td>Kriteria pemilihan model; nilai lebih kecil lebih baik.</td></tr>
<tr><td><b>Odds ratio / IRR / HR</b></td><td>Pengali peluang (logistik), laju kejadian (Poisson), dan risiko (Cox) untuk kenaikan 1 satuan X.</td></tr>
</tbody></table>''', unsafe_allow_html=True)
    _head("Catatan metodologi")
    st.markdown("""
- Analisis ragam memakai jumlah kuadrat **sekuensial (Tipe I)**; pada data seimbang sama dengan Tipe II/III.
- Uji asumsi bersifat pendukung; ukuran sampel kecil membuat uji kurang bertenaga, jadi lihat juga grafik residual.
- Uji lanjut sebaiknya dipakai hanya bila uji F nyata. **BNT** tidak mengendalikan galat tipe I pada banyak perbandingan; **Tukey** dan **Scheffé** lebih konservatif; **Dunnett** khusus perbandingan terhadap kontrol.
- Model lanjutan (panel, spasial, mixed, Cox, Tobit) bersifat **alat bantu analisis**; periksa asumsi model dan konsultasikan dengan ahli statistika untuk publikasi.
""")
    _head("Kebijakan privasi & penafian")
    st.markdown(LEGAL_CSS, unsafe_allow_html=True)
    st.markdown(PRIVACY_HTML, unsafe_allow_html=True)
    st.markdown('<div class="foot">StatCalc · Kalkulator analisis statistika</div>', unsafe_allow_html=True)


def page_flow(reg_groups, des_groups, hero):
    """Flowchart alur analisis tiap metode (halaman tersendiri agar halaman analisis tetap bersih)."""
    import flows
    st.markdown(HOME_CSS, unsafe_allow_html=True)
    st.markdown(flows.FLOW_CSS, unsafe_allow_html=True)
    reg, des = _catalog(reg_groups, des_groups)
    hero("Alur Analisis Setiap Metode", "Lihat urutan langkah dari data masuk, pemeriksaan asumsi, sampai hasil. Pilih metodenya di bawah.",
         ["Flowchart", "Asumsi & keputusan", "Hasil"])
    with st.container(border=True):
        c1, c2, c3 = st.columns([1.2, 1.4, 2.2])
        fam = c1.radio("Jenis analisis", [nav.FAMILY_DES, nav.FAMILY_REG], key="fl_fam")
        groups = des if fam == nav.FAMILY_DES else reg
        pre = "fd" if fam == nav.FAMILY_DES else "fr"
        grp = c2.selectbox("Kelompok", list(groups.keys()), key=f"{pre}_grp")
        labels = {m["label"]: m for m in groups[grp]}
        lab = c3.selectbox("Metode", list(labels.keys()), key=f"{pre}_m_{grp}")
    m = labels[lab]
    family = "des" if fam == nav.FAMILY_DES else "reg"
    _head(m["label"], m["desc"])
    st.markdown(flows.flow_html(flows.nodes_for(m["key"], family)), unsafe_allow_html=True)
    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
    b1, b2, _ = st.columns([1.4, 1.4, 3])
    b1.button("Buka metode ini →", key="fl_open", type="primary", on_click=_go, args=(PAGE_APP, fam, grp, lab), use_container_width=True)
    b2.button("Panduan memilih metode", key="fl_guide", on_click=_go, args=(PAGE_GUIDE,), use_container_width=True)
    st.markdown('<div class="foot">Flowchart bersifat ringkasan alur; detail perhitungan ada di halaman analisis tiap metode.</div>', unsafe_allow_html=True)
