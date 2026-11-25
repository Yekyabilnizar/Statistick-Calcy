"""Materi lengkap: pendalaman teori, contoh hitung kedua, soal latihan berkunci, dan referensi per modul.

L(slug, teori, soal, ref, contoh2=None)
  teori   : [(judul, [paragraf...], [persamaan_latex...])]   (paragraf boleh memuat \\( ... \\))
  soal    : [(pertanyaan, jawaban)]                          (keduanya boleh memuat \\( ... \\))
  ref     : [str]  rujukan buku/artikel
  contoh2 : dict(judul, soal, data=[[...]] atau None, langkah=[(teks, persamaan_latex_atau_None)], simpul)
"""

LENGKAP = {}


def L(slug, teori, soal, ref, contoh2=None):
    LENGKAP[slug] = dict(teori=[(h, list(p), list(e)) for h, p, e in teori], soal=[tuple(s) for s in soal], ref=list(ref), contoh2=contoh2)


def D(slug, teori=(), soal=()):
    """Pendalaman tambahan untuk modul yang sudah punya materi lengkap (ditambahkan di belakang)."""
    lk = LENGKAP[slug]
    lk["teori"] += [(h, list(p), list(e)) for h, p, e in teori]
    lk["soal"] += [tuple(x) for x in soal]


def _load():
    import importlib
    for name in ("lengkap_dasar", "lengkap_dasar2", "lengkap_des", "lengkap_des2", "lengkap_reg", "lengkap_reg2", "lengkap_reg3", "lengkap_reg4"):
        try:
            importlib.import_module(f"{__package__}.{name}")
        except ModuleNotFoundError as e:
            if name not in str(e):
                raise
