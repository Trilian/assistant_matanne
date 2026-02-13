"""
Intégrations externes - Services d'intégration avec APIs tierces

Ce package regroupe tous les services d'intégration externe:
- Codes-barres (scan et validation)
- OpenFoodFacts (enrichissement produits)
- OCR Factures (extraction données factures)

Utilisation:
    from src.services.integrations import (
        BarcodeService,
        get_barcode_service,
        OpenFoodFactsService,
        get_openfoodfacts_service,
        FactureOCRService,
        get_facture_ocr_service,
    )
"""

# ═══════════════════════════════════════════════════════════
# CODES-BARRES
# ═══════════════════════════════════════════════════════════

from .codes_barres import (
    BarcodeArticle,
    # Schémas Pydantic
    BarcodeData,
    BarcodeRecette,
    # Service
    BarcodeService,
    ScanResultat,
    get_barcode_service,
)

# ═══════════════════════════════════════════════════════════
# FACTURE OCR
# ═══════════════════════════════════════════════════════════
from .facture import (
    # Helpers
    PATTERNS_FOURNISSEURS,
    PATTERNS_MONTANTS,
    # Schémas Pydantic
    DonneesFacture,
    # Service
    FactureOCRService,
    ResultatOCR,
    detecter_fournisseur,
    extraire_montant,
    get_facture_ocr_service,
)

# ═══════════════════════════════════════════════════════════
# OPENFOODFACTS
# ═══════════════════════════════════════════════════════════
from .produit import (
    CACHE_TTL,
    # Constantes
    OPENFOODFACTS_API,
    OPENFOODFACTS_SEARCH,
    # Dataclasses
    NutritionInfo,
    # Service
    OpenFoodFactsService,
    ProduitOpenFoodFacts,
    get_openfoodfacts_service,
)

# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Codes-barres
    "BarcodeService",
    "get_barcode_service",
    "BarcodeData",
    "BarcodeArticle",
    "BarcodeRecette",
    "ScanResultat",
    # OpenFoodFacts
    "OpenFoodFactsService",
    "get_openfoodfacts_service",
    "NutritionInfo",
    "ProduitOpenFoodFacts",
    "OPENFOODFACTS_API",
    "OPENFOODFACTS_SEARCH",
    "CACHE_TTL",
    # Facture OCR
    "FactureOCRService",
    "get_facture_ocr_service",
    "DonneesFacture",
    "ResultatOCR",
    "PATTERNS_FOURNISSEURS",
    "PATTERNS_MONTANTS",
    "detecter_fournisseur",
    "extraire_montant",
]
