# StatCalc – Dashboard Analisis Statistika

Kalkulator analisis statistika berbasis Streamlit: pilih analisis, masukkan data, lalu lihat ringkasan, tabel, dan visualisasinya.

## Analisis
- Regresi Linear (sederhana & berganda)
- Rancangan Acak Lengkap (RAL)
- Rancangan Acak Kelompok (RAK)

## Menjalankan
```
pip install -r requirements.txt
streamlit run app.py
```

## Struktur
- `app.py` – tampilan dashboard
- `stats_engine.py` – perhitungan statistika
- `requirements.txt` – daftar library
- `.streamlit/config.toml` – pengaturan tema
