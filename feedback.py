"""
feedback.py – formulir masukan pengguna. Setiap masukan ditambahkan sebagai satu baris CSV ke sebuah berkas di repositori GitHub
PRIVAT milik developer (lewat GitHub Contents API). Token disimpan di Streamlit Secrets, tidak pernah di kode atau repo.

Konfigurasi (Streamlit Cloud: Settings > Secrets, atau .streamlit/secrets.toml saat lokal):
    [feedback]
    token  = "github_pat_xxx"          # fine-grained token, izin Contents: Read and write, HANYA untuk repo masukan
    repo   = "username/statcalc-masukan"   # repo PRIVAT
    path   = "masukan.csv"             # opsional
    branch = "main"                    # opsional
"""
import base64
import csv
import io
import time
from datetime import datetime, timezone

import requests
import streamlit as st

API = "https://api.github.com"
HEADER = ["waktu_utc", "kategori", "metode", "penilaian", "pesan", "kontak"]
MAX_MSG, MAX_CONTACT = 2000, 120
CATEGORIES = ["💡 Saran fitur / metode baru", "🐞 Laporan masalah (bug)", "❓ Pertanyaan", "👍 Kesan & pesan", "📝 Lainnya"]


def get_config():
    """Mengembalikan dict konfigurasi atau None bila belum diatur."""
    try:
        c = dict(st.secrets["feedback"])
    except Exception:  # noqa: BLE001
        return None
    if not c.get("token") or not c.get("repo"):
        return None
    c.setdefault("path", "masukan.csv")
    c.setdefault("branch", "main")
    return c


def sanitize(text, limit):
    """Batasi panjang dan netralkan 'CSV injection' (sel yang diawali = + - @ dianggap rumus oleh Excel)."""
    t = " ".join(str(text or "").replace("\r", " ").split("\n")).strip()[:limit]
    if t[:1] in ("=", "+", "-", "@", "\t"):
        t = "'" + t
    return t


def make_row(kategori, metode, penilaian, pesan, kontak, now=None):
    now = now or datetime.now(timezone.utc)
    return [now.strftime("%Y-%m-%d %H:%M:%S"), sanitize(kategori, 60), sanitize(metode, 120),
            penilaian if penilaian else "", sanitize(pesan, MAX_MSG), sanitize(kontak, MAX_CONTACT)]


def _row_to_csv(row):
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerow(row)
    return buf.getvalue()


def append_row(cfg, row, session=None, retries=4):
    """Tambahkan satu baris ke berkas CSV di GitHub. Aman terhadap penulisan bersamaan (SHA + ulang)."""
    s = session or requests
    url = f"{API}/repos/{cfg['repo']}/contents/{cfg['path']}"
    headers = {"Authorization": f"Bearer {cfg['token']}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    last_status = None
    for attempt in range(retries):
        r = s.get(url, headers=headers, params={"ref": cfg["branch"]}, timeout=15)
        if r.status_code == 200:
            info = r.json()
            current = base64.b64decode(info["content"]).decode("utf-8")
            sha = info["sha"]
            if current and not current.endswith("\n"):
                current += "\n"
        elif r.status_code == 404:
            current, sha = _row_to_csv(HEADER), None
        else:
            raise RuntimeError(f"GitHub GET {r.status_code}")
        new = current + _row_to_csv(row)
        body = {"message": "Masukan baru", "content": base64.b64encode(new.encode("utf-8")).decode("ascii")}
        # Repo kosong (belum ada branch): percobaan pertama tanpa 'branch' agar GitHub membuat branch bawaan.
        if sha or last_status not in (404, 409, 422):
            body["branch"] = cfg["branch"]
        if sha:
            body["sha"] = sha
        w = s.put(url, headers=headers, json=body, timeout=15)
        if w.status_code in (200, 201):
            return True
        last_status = w.status_code
        if w.status_code in (404, 409, 422) and attempt < retries - 1:  # bentrok penulisan / repo kosong → coba lagi
            time.sleep(0.4 * (attempt + 1))
            continue
        raise RuntimeError(f"GitHub PUT {w.status_code}")
    raise RuntimeError("Gagal menulis setelah beberapa percobaan")


def page_feedback(hero, kpi_notice, method_options):
    from home import HOME_CSS, _head
    st.markdown(HOME_CSS, unsafe_allow_html=True)
    hero("Kirim Masukan", "Temukan kekurangan, butuh metode baru, atau punya pertanyaan? Tulis di sini; masukan Anda dibaca langsung oleh pengembang.",
         ["Saran fitur", "Laporan masalah", "Pertanyaan"])
    cfg = get_config()
    if cfg is None:
        kpi_notice("Fitur masukan belum diaktifkan oleh pengelola situs. Silakan coba lagi nanti.")
        return
    if st.session_state.get("fb_done"):
        st.success("Terima kasih! Masukan Anda sudah terkirim.")
        if st.button("Kirim masukan lain", key="fb_again"):
            st.session_state["fb_done"] = False
            st.rerun()
        return

    with st.form("fb_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        kategori = c1.selectbox("Jenis masukan", CATEGORIES, key="fb_cat")
        metode = c2.selectbox("Metode terkait (opsional)", ["(umum / tidak spesifik)"] + list(method_options), key="fb_met")
        pesan = st.text_area("Pesan Anda", height=170, max_chars=MAX_MSG, key="fb_msg",
                             placeholder="Ceritakan sejelas mungkin. Untuk laporan masalah: apa yang Anda lakukan, apa yang terjadi, dan apa yang diharapkan.")
        nilai = st.select_slider("Penilaian aplikasi (opsional; geser, 0 = tidak menilai)", options=[0, 1, 2, 3, 4, 5], value=0, key="fb_rate",
                                 format_func=lambda v: "—" if v == 0 else "⭐" * v)
        kontak = st.text_input("Email/kontak bila ingin dibalas (opsional)", max_chars=MAX_CONTACT, key="fb_contact")
        st.caption("Jangan menuliskan data pribadi sensitif atau data penelitian mentah pada pesan. Data analisis yang Anda unggah **tidak** ikut terkirim.")
        setuju = st.checkbox("Saya setuju masukan ini disimpan oleh pengembang untuk perbaikan aplikasi.", key="fb_ok")
        # kolom jebakan anti-spam: pengguna asli tidak melihatnya
        st.markdown("<style>div[data-testid='stTextInput']:has(input[aria-label='Situs web']){position:absolute;left:-9999px;height:0;overflow:hidden}</style>",
                    unsafe_allow_html=True)
        jebakan = st.text_input("Situs web", key="fb_hp", label_visibility="collapsed")
        kirim = st.form_submit_button("Kirim masukan", type="primary")

    if kirim:
        now = time.time()
        if jebakan:
            st.stop()
        if len((pesan or "").strip()) < 10:
            st.warning("Pesan terlalu pendek (minimal 10 karakter).")
        elif not setuju:
            st.warning("Centang persetujuan penyimpanan masukan terlebih dahulu.")
        elif now - st.session_state.get("fb_last", 0) < 30:
            st.warning("Mohon tunggu sebentar sebelum mengirim lagi.")
        else:
            met = "" if metode.startswith("(umum") else metode
            try:
                with st.spinner("Mengirim…"):
                    append_row(cfg, make_row(kategori, met, nilai, pesan, kontak))
                st.session_state["fb_last"] = now
                st.session_state["fb_done"] = True
                st.rerun()
            except Exception as e:  # noqa: BLE001
                import sys
                print(f"[feedback] gagal mengirim: {type(e).__name__}: {e}", file=sys.stderr)  # tampil di log pengembang, tanpa token
                kode = str(e)[:40] if str(e).startswith("GitHub") else type(e).__name__
                st.error(f"Maaf, masukan belum berhasil terkirim. Silakan coba lagi beberapa saat lagi. (kode: {kode})")
