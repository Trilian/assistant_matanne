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

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CODES-BARRES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

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

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# OPENFOODFACTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

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

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FACTURE OCR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

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

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# EXPORTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

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
