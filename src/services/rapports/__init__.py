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

from src.services.rapports.types import (
    # Schémas export (français)
    DonneesRecettePDF,
    DonneesPlanningPDF,
    DonneesCoursesPDF,
    # Schémas rapports (français)
    RapportStocks,
    RapportBudget,
    AnalyseGaspillage,
    RapportPlanning,
    # Alias rétrocompatibilité
    RecettePDFData,
    PlanningPDFData,
    CoursesPDFData,
)

# ═══════════════════════════════════════════════════════════
# SERVICES
# ═══════════════════════════════════════════════════════════

from src.services.rapports.export import (
    ServiceExportPDF,
    obtenir_service_export_pdf,
    # Alias rétrocompatibilité
    PDFExportService,
    get_pdf_export_service,
)

from src.services.rapports.generation import (
    ServiceRapportsPDF,
    obtenir_service_rapports_pdf,
    # Alias rétrocompatibilité
    RapportsPDFService,
    get_rapports_pdf_service,
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
