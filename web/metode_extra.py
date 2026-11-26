"""Penjelasan tambahan per halaman kalkulator (/metode/<slug>).

EXTRA[slug] = dict(
    kasus = str              contoh situasi nyata pemakaian metode
    data  = [str]            cara menyiapkan data untuk kalkulator ini
    baca  = [(label, str)]   cara membaca bagian-bagian hasil kalkulator
    salah = [str]            kesalahan yang sering terjadi
    lapor = str              contoh kalimat pelaporan (skripsi/artikel)
    faq   = [(q, a)]         tanya-jawab singkat
)
"""

EXTRA = {}


def X(slug, kasus, data, baca, salah, lapor, faq):
    EXTRA[slug] = dict(kasus=kasus, data=list(data), baca=list(baca), salah=list(salah), lapor=lapor, faq=list(faq))


def _load():
    import importlib
    for name in ("metode_extra_des", "metode_extra_reg1", "metode_extra_reg2", "metode_extra_reg3"):
        try:
            importlib.import_module(f"{__package__}.{name}" if __package__ else name)
        except ModuleNotFoundError as e:
            if name not in str(e):
                raise


_load()
