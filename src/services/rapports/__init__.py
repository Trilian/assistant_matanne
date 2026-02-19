"""
Package PDF unifié.

Fusionne les 2 anciens services:
- pdf_export.py → export.py (exports recettes, planning, courses)
- rapports_pdf.py → rapports.py (rapports stocks, budget, gaspillage)

Tous renommés en français avec alias rétrocompatibilité.
"""

# ═══════════════════════════════════════════════════════════
# TYPES ET SCHÉMAS
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# SERVICES
# ═══════════════════════════════════════════════════════════
from src.services.rapports.export import (
    ServiceExportPDF,
    obtenir_service_export_pdf,
)
from src.services.rapports.generation import (
    # Alias rétrocompatibilité
    RapportsPDFService,
    ServiceRapportsPDF,
    get_rapports_pdf_service,
    obtenir_service_rapports_pdf,
)
from src.services.rapports.types import (
    AnalyseGaspillage,
    DonneesCoursesPDF,
    DonneesPlanningPDF,
    DonneesRecettePDF,
    RapportBudget,
    RapportPlanning,
    RapportStocks,
)

# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # === TYPES (français) ===
    "DonneesRecettePDF",
    "DonneesPlanningPDF",
    "DonneesCoursesPDF",
    "RapportStocks",
    "RapportBudget",
    "AnalyseGaspillage",
    "RapportPlanning",
    # === SERVICES (français) ===
    "ServiceExportPDF",
    "obtenir_service_export_pdf",
    "ServiceRapportsPDF",
    "obtenir_service_rapports_pdf",
    # === ALIAS RÉTROCOMPATIBILITÉ ===
    "RapportsPDFService",
    "get_rapports_pdf_service",
]
