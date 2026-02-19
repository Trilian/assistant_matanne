"""Module Utilitaires - Scanner, rapports, notifications."""

import importlib

_MODULE_MAP = {
    "barcode": ".barcode",
    "notifications_push": ".notifications_push",
    "rapports": ".rapports",
}


def __getattr__(name: str):
    if name in _MODULE_MAP:
        return importlib.import_module(_MODULE_MAP[name], __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["rapports", "barcode", "notifications_push"]
