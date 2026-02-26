"""Module Utilitaires — Outils divers pour la gestion familiale."""

import importlib

_MODULE_MAP = {
    # Existants
    "barcode": ".barcode",
    "notifications_push": ".notifications_push",
    "rapports": ".rapports",
    "chat_ia": ".chat_ia",
    "scan_factures": ".scan_factures",
    "recherche_produits": ".recherche_produits",
    # Nouveaux modules
    "export_global": ".export_global",
    "import_masse": ".import_masse",
    "notes_memos": ".notes_memos",
    "journal_bord": ".journal_bord",
    "convertisseur_unites": ".convertisseur_unites",
    "calculatrice_portions": ".calculatrice_portions",
    "qr_code_gen": ".qr_code_gen",
    "minuteur": ".minuteur",
    "meteo": ".meteo",
    "mots_de_passe": ".mots_de_passe",
    "annuaire_contacts": ".annuaire_contacts",
    "presse_papiers": ".presse_papiers",
    "liens_utiles": ".liens_utiles",
    "saisonnalite": ".saisonnalite",
    "suivi_energie": ".suivi_energie",
    "compte_rebours": ".compte_rebours",
    "substitutions": ".substitutions",
    "cout_repas": ".cout_repas",
}


def __getattr__(name: str):
    if name in _MODULE_MAP:
        return importlib.import_module(_MODULE_MAP[name], __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(_MODULE_MAP.keys())
