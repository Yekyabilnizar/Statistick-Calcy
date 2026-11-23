"""Terjemahan modul belajar. Satu berkas per kelompok modul; tiap berkas mengisi MOD_EN[slug] = dict(...)."""
import importlib
import pkgutil

MOD_EN = {}
for _m in pkgutil.iter_modules(__path__):
    importlib.import_module(f"{__name__}.{_m.name}")
