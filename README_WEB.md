# StatCalc Web (Render)

Website baru (halaman per metode + API perhitungan) dengan Starlette. Mesin perhitungan (numpy/scipy) dipakai ulang dari aplikasi Streamlit.

## Jalankan lokal
```bash
pip install -r requirements-web.txt
uvicorn web.main:app --reload --port 8000     # buka http://localhost:8000
```

## Deploy ke Render
1. Push seluruh repo ke GitHub (file baru: `web/`, `Dockerfile`, `render.yaml`, `requirements-web.txt`, `.dockerignore`).
2. Render → **New → Blueprint** → pilih repo → Apply. (Atau **New → Web Service**, runtime **Docker**, region **Singapore**.)
3. Setelah build selesai, buka alamat `namaapp.onrender.com`. Cek `/healthz` menjawab `ok`.
4. Paket gratis "tertidur" setelah 15 menit tanpa kunjungan; ganti ke paket berbayar termurah sebelum mengajukan AdSense.

## Domain sendiri
1. Beli domain di registrar (Cloudflare, Niagahoster, dll.).
2. Render → layanan → **Settings → Custom Domains → Add**; ikuti catatan DNS yang tampil (CNAME untuk subdomain `www`, A/ALIAS untuk domain utama).
3. Isi Environment: `SITE_URL=https://domainanda.com` dan `PRIMARY_HOST=domainanda.com` (mengalihkan permanen alamat `onrender.com` ke domain Anda; penting untuk SEO). Lalu Deploy ulang.
4. Isi `CONTACT_EMAIL` agar kontak tampil di halaman Tentang dan Privasi.

## Menambah metode
Tambahkan satu entri `M(...)` di `web/registry.py` (isian formulir, fungsi `run_...`, dan teks penjelasan). Halaman, pencarian, sitemap, dan alur metode ikut otomatis.

## Catatan
- Data pengguna hanya diproses di memori, tidak disimpan.
- Batas: 3 MB teks / 50.000 baris / 80 kolom; 2 perhitungan serentak; 60 perhitungan per IP per menit (`RATE_LIMIT`).
- Setelah deploy pertama berhasil, kunci versi paket dengan `pip freeze` ke `requirements-web.txt`.


## Cakupan (sama dengan aplikasi Streamlit)
52 metode: 18 rancangan percobaan dan 34 regresi, ditambah halaman Panduan Metode (tabel situasi → metode), Alur Metode (flowchart), Masukan, Tentang, dan Privasi.
Fitur hasil: uji lanjut dapat diganti setelah hasil muncul (BNT, DMRT, Tukey, Scheffé, Dunnett + pilihan kontrol), batang galat SD/SE, kalkulator prediksi regresi, input manual di tabel, pembangkit rancangan (CCD/Box-Behnken, faktorial pecahan), unduh Excel.

## Menu Masukan (disimpan di repo GitHub privat)
Token tidak pernah masuk repo. Isi di Render → Environment:
| Variabel | Isi |
|---|---|
| `FEEDBACK_TOKEN` | token GitHub (fine-grained, izin Contents: Read and write, hanya repo masukan) |
| `FEEDBACK_REPO` | `pemilik/nama-repo-privat` |
| `FEEDBACK_PATH` | opsional, default `masukan.csv` |
| `FEEDBACK_BRANCH` | opsional, default `main` |
Bila token/repo kosong, halaman Masukan menampilkan pemberitahuan bahwa fitur belum aktif.

## Modul belajar (/belajar)
62 modul ringkas: 10 dasar statistika, 18 rancangan percobaan, 34 regresi. Isi ada di `web/belajar/*.py` (satu fungsi `T(...)`/`D(...)`/`R(...)` per modul: tujuan, ide, rumus, langkah, cara baca, kesalahan umum, latihan). Setiap modul metode tersambung ke kalkulatornya, dan halaman kalkulator menautkan balik ke modulnya. Penanda "selesai" disimpan di peramban (localStorage), tanpa akun.
Menambah modul: tambahkan satu entri di file yang sesuai; urutan jalur mengikuti urutan penulisan.


## Konten modul mendalam
Setiap dari 62 modul di /belajar kini punya tab 📐 Teori (notasi, persamaan LaTeX via KaTeX self-hosted), 🧪 Contoh hitung (angka terverifikasi), dan ❓ FAQ. Isi di web/belajar/teori_*.py (fungsi X). Validasi persamaan: jalankan skrip validasi KaTeX. Mohon tinjau ketepatan materi sebelum dipublikasikan luas.
