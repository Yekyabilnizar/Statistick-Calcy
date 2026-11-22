"""feedback_web.py – menyimpan masukan pengguna sebagai baris CSV di repo GitHub PRIVAT lewat GitHub Contents API.
Konfigurasi lewat variabel lingkungan (jangan commit token):
    FEEDBACK_TOKEN   fine-grained token, izin Contents: Read and write, hanya untuk repo masukan
    FEEDBACK_REPO    mis. username/statcalc-masukan
    FEEDBACK_PATH    (opsional) default masukan.csv
    FEEDBACK_BRANCH  (opsional) default main
    FEEDBACK_API     (opsional, untuk pengujian) default https://api.github.com
"""
import base64
import csv
import io
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

HEADER = ["waktu_utc", "kategori", "metode", "penilaian", "pesan", "kontak"]
MAX_MSG, MAX_CONTACT = 2000, 120
CATEGORIES = ["💡 Saran fitur / metode baru", "🐞 Laporan masalah (bug)", "❓ Pertanyaan", "👍 Kesan & pesan", "📝 Lainnya"]


def get_config():
    token, repo = os.environ.get("FEEDBACK_TOKEN", "").strip(), os.environ.get("FEEDBACK_REPO", "").strip()
    if not token or not repo or "/" not in repo:
        return None
    return {"token": token, "repo": repo, "path": os.environ.get("FEEDBACK_PATH", "masukan.csv").strip() or "masukan.csv",
            "branch": os.environ.get("FEEDBACK_BRANCH", "main").strip() or "main",
            "api": os.environ.get("FEEDBACK_API", "https://api.github.com").rstrip("/")}


def sanitize(text, limit):
    """Batasi panjang dan netralkan 'CSV injection' (sel berawalan = + - @ dianggap rumus oleh Excel)."""
    t = " ".join(str(text or "").replace("\r", " ").split("\n")).strip()[:limit]
    if t[:1] in ("=", "+", "-", "@", "\t"):
        t = "'" + t
    return t


def make_row(kategori, metode, penilaian, pesan, kontak, now=None):
    now = now or datetime.now(timezone.utc)
    return [now.strftime("%Y-%m-%d %H:%M:%S"), sanitize(kategori, 60), sanitize(metode, 120), penilaian if penilaian else "",
            sanitize(pesan, MAX_MSG), sanitize(kontak, MAX_CONTACT)]


def _row_to_csv(row):
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerow(row)
    return buf.getvalue()


def _call(method, url, headers, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, {}


def append_row(cfg, row, retries=4):
    url = f"{cfg['api']}/repos/{cfg['repo']}/contents/{cfg['path']}"
    headers = {"Authorization": f"Bearer {cfg['token']}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "statcalc-feedback", "Content-Type": "application/json"}
    last = None
    for attempt in range(retries):
        code, info = _call("GET", f"{url}?ref={cfg['branch']}", headers)
        if code == 200:
            current = base64.b64decode(info["content"]).decode("utf-8")
            sha = info["sha"]
            if current and not current.endswith("\n"):
                current += "\n"
        elif code == 404:
            current, sha = _row_to_csv(HEADER), None
        else:
            raise RuntimeError(f"GitHub GET {code}")
        body = {"message": "Masukan baru", "content": base64.b64encode((current + _row_to_csv(row)).encode("utf-8")).decode("ascii")}
        if sha or last not in (404, 409, 422):
            body["branch"] = cfg["branch"]
        if sha:
            body["sha"] = sha
        code, _ = _call("PUT", url, headers, body)
        if code in (200, 201):
            return True
        last = code
        if code in (404, 409, 422) and attempt < retries - 1:
            time.sleep(0.4 * (attempt + 1))
            continue
        raise RuntimeError(f"GitHub PUT {code}")
    raise RuntimeError("Gagal menulis setelah beberapa percobaan")
