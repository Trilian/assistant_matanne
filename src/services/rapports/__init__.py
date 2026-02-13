"""
Package PDF unifié.

Fusionne les 2 anciens services:
- pdf_export.py â†’ export.py (exports recettes, planning, courses)
- rapports_pdf.py â†’ rapports.py (rapports stocks, budget, gaspillage)

Tous renommés en français avec alias rétrocompatibilité.
"""

# ═══════════════════════════════════════════════════════════
# TYPES ET SCHÉMAS
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# SERVICES
# ═══════════════════════════════════════════════════════════
from src.services.rapports.export import (
    # Alias rétrocompatibilité
    PDFExportService,
    ServiceExportPDF,
    get_pdf_export_service,
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
    CoursesPDFData,
    DonneesCoursesPDF,
    DonneesPlanningPDF,
    # Schémas export (français)
    DonneesRecettePDF,
    PlanningPDFData,
    RapportBudget,
    RapportPlanning,
    # Schémas rapports (français)
    RapportStocks,
    # Alias rétrocompatibilité
    RecettePDFData,
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
    # Types
    "RecettePDFData",
    "PlanningPDFData",
    "CoursesPDFData",
    # Services
    "PDFExportService",
    "get_pdf_export_service",
    "RapportsPDFService",
    "get_rapports_pdf_service",
]
