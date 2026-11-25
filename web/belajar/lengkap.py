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


def _load():
    import importlib
    for name in ("lengkap_dasar", "lengkap_des", "lengkap_reg"):
        try:
            importlib.import_module(f"{__package__}.{name}")
        except ModuleNotFoundError as e:
            if name not in str(e):
                raise
