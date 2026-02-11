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
    # Service
    BarcodeService,
    get_barcode_service,
    # Schémas Pydantic
    BarcodeData,
    BarcodeArticle,
    BarcodeRecette,
    ScanResultat,
)

# ═══════════════════════════════════════════════════════════
# OPENFOODFACTS
# ═══════════════════════════════════════════════════════════

from .produit import (
    # Service
    OpenFoodFactsService,
    get_openfoodfacts_service,
    # Dataclasses
    NutritionInfo,
    ProduitOpenFoodFacts,
    # Constantes
    OPENFOODFACTS_API,
    OPENFOODFACTS_SEARCH,
    CACHE_TTL,
)

# ═══════════════════════════════════════════════════════════
# FACTURE OCR
# ═══════════════════════════════════════════════════════════

from .facture import (
    # Service
    FactureOCRService,
    get_facture_ocr_service,
    # Schémas Pydantic
    DonneesFacture,
    ResultatOCR,
    # Helpers
    PATTERNS_FOURNISSEURS,
    PATTERNS_MONTANTS,
    detecter_fournisseur,
    extraire_montant,
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
