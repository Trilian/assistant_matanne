"""
Module Scanner Barcode/QR - Interface Streamlit

✅ Scanner codes-barres (vidéo temps réel, photo, manuel)
✅ Ajout rapide articles
✅ Verification stock
✅ Import/Export

Intègre les fonctionnalités avancées de détection:
- pyzbar (principal) avec fallback zxing-cpp
- Streaming webrtc temps réel
- Anti-doublon (scan_cooldown)
"""

import streamlit as st  # noqa: F401 — exposed for @patch compatibility

from src.services.integrations import BarcodeService  # noqa: F401

from .app import app, get_barcode_service
from .detection import BarcodeScanner, detect_barcodes
from .logic import (
    detecter_pays_origine,
    detecter_type_code_barres,
    extraire_infos_produit,
    formater_code_barres,
    nettoyer_code_barres,
    suggerer_categorie_produit,
    valider_checksum_ean13,
    valider_code_barres,
)
from .operations import (
    afficher_ajout_rapide,
    afficher_gestion_barcodes,
    afficher_import_export,
    afficher_verifier_stock,
)
from .scanner import afficher_scanner

__all__ = [
    "BarcodeScanner",
    "afficher_ajout_rapide",
    "afficher_gestion_barcodes",
    "afficher_import_export",
    "afficher_scanner",
    "afficher_verifier_stock",
    "app",
    "detect_barcodes",
    "detecter_pays_origine",
    "detecter_type_code_barres",
    "extraire_infos_produit",
    "formater_code_barres",
    "get_barcode_service",
    "nettoyer_code_barres",
    "suggerer_categorie_produit",
    "valider_checksum_ean13",
    "valider_code_barres",
]
