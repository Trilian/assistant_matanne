"""
Service Génération Rapports PDF

Orchestre les mixins de génération PDF:
- PlanningReportMixin (planning_pdf.py)
- BudgetReportMixin (rapports_budget.py)
- GaspillageReportMixin (rapports_gaspillage.py)

Conserve les rapports stocks + utilitaires de téléchargement.
"""

import logging
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_session_db
from src.core.errors_base import ErreurValidation
from src.core.models import ArticleInventaire
from src.services.rapports.planning_pdf import PlanningReportMixin
from src.services.rapports.rapports_budget import BudgetReportMixin
from src.services.rapports.rapports_gaspillage import GaspillageReportMixin
from src.services.rapports.types import RapportStocks

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE RAPPORTS PDF
# ═══════════════════════════════════════════════════════════


class ServiceRapportsPDF(
    PlanningReportMixin,
    BudgetReportMixin,
    GaspillageReportMixin,
):
    """
    Service pour générer des rapports PDF.

    Fonctionnalités:
    - Rapport hebdo stocks
    - Rapport budget/dépenses
    - Analyse gaspillage
    - Export professionnel

    Note: Ce service n'est PAS un CRUD — il génère des PDFs.
    Les accès DB se font via @avec_session_db sur chaque méthode.
    """

    def __init__(self):
        self.cache_ttl = 3600

    # ═══════════════════════════════════════════════════════════
    # RAPPORT STOCKS
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=300)
    @avec_session_db
    def generer_donnees_rapport_stocks(
        self, periode_jours: int = 7, session: Session = None
    ) -> RapportStocks:
        """
        Collecte les données pour rapport stocks.

        Args:
            periode_jours: Nombre de jours à analyser
            session: Session DB

        Returns:
            Données structurées du rapport
        """
        rapport = RapportStocks(periode_jours=periode_jours)

        # Récupérer tous les articles
        articles = session.query(ArticleInventaire).all()
        rapport.articles_total = len(articles)

        # Catégoriser
        categories = {}
        valeur_total = 0.0
        articles_faible = []
        articles_perimes = []

        maintenant = datetime.now()

        for article in articles:
            # Valeur stock
            if article.prix_unitaire:
                valeur = article.quantite * article.prix_unitaire
                valeur_total += valeur

            # Catégories
            if article.categorie not in categories:
                categories[article.categorie] = {"quantite": 0, "valeur": 0.0, "articles": 0}
            categories[article.categorie]["quantite"] += article.quantite
            categories[article.categorie]["articles"] += 1
            if article.prix_unitaire:
                categories[article.categorie]["valeur"] += article.quantite * article.prix_unitaire

            # Stock faible
            if article.quantite < article.quantite_min and article.quantite > 0:
                articles_faible.append(
                    {
                        "nom": article.nom,
                        "quantite": article.quantite,
                        "quantite_min": article.quantite_min,
                        "unite": article.unite,
                        "emplacement": article.emplacement,
                    }
                )

            # Périmés
            if article.date_peremption and article.date_peremption < maintenant:
                jours_ecart = (maintenant - article.date_peremption).days
                articles_perimes.append(
                    {
                        "nom": article.nom,
                        "date_peremption": article.date_peremption,
                        "jours_perime": jours_ecart,
                        "quantite": article.quantite,
                        "unite": article.unite,
                    }
                )

        rapport.articles_faible_stock = sorted(
            articles_faible,
            key=lambda x: x["quantite"] / x["quantite_min"] if x["quantite_min"] > 0 else 0,
        )
        rapport.articles_perimes = sorted(
            articles_perimes, key=lambda x: x["jours_perime"], reverse=True
        )
        rapport.valeur_stock_total = valeur_total
        rapport.categories_resumee = categories

        return rapport

    @avec_session_db
    def generer_pdf_rapport_stocks(
        self, periode_jours: int = 7, session: Session = None
    ) -> BytesIO:
        """
        Génère un PDF du rapport stocks.

        Args:
            periode_jours: Nombre de jours
            session: Session DB

        Returns:
            Fichier PDF en BytesIO
        """
        donnees = self.generer_donnees_rapport_stocks(periode_jours, session=session)

        # Créer le PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#2E7D32"),
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#1976D2"),
            spaceAfter=12,
            spaceBefore=12,
        )

        # Contenu
        elements = []

        # Titre
        elements.append(Paragraph("📊 RAPPORT STOCKS HEBDOMADAIRE", title_style))
        elements.append(
            Paragraph(
                f"Généré le {donnees.date_rapport.strftime('%d/%m/%Y à %H:%M')}", styles["Normal"]
            )
        )
        elements.append(Spacer(1, 0.3 * inch))

        # Résumé général
        elements.append(Paragraph("🔍 RÉSUMÉ GÉNÉRAL", heading_style))
        summary_data = [
            ["Métrique", "Valeur"],
            ["Total articles en stock", str(donnees.articles_total)],
            ["Valeur stock total", f"€{donnees.valeur_stock_total:.2f}"],
            ["Articles faible stock", str(len(donnees.articles_faible_stock))],
            ["Articles périmés", str(len(donnees.articles_perimes))],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Articles faible stock
        if donnees.articles_faible_stock:
            elements.append(Paragraph("⚠️ ARTICLES EN FAIBLE STOCK", heading_style))
            stock_data = [["Article", "Quantité", "Minimum", "Unité", "Emplacement"]]
            for article in donnees.articles_faible_stock[:10]:
                stock_data.append(
                    [
                        article["nom"][:30],
                        f"{article['quantite']}",
                        f"{article['quantite_min']}",
                        article["unite"],
                        article["emplacement"],
                    ]
                )

            stock_table = Table(
                stock_data, colWidths=[1.8 * inch, 1 * inch, 1 * inch, 0.8 * inch, 1.2 * inch]
            )
            stock_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FF9800")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#FFF3E0")],
                        ),
                    ]
                )
            )
            elements.append(stock_table)
            elements.append(Spacer(1, 0.2 * inch))

        # Articles périmés
        if donnees.articles_perimes:
            elements.append(Paragraph("❌ ARTICLES PÉRIMÉS", heading_style))
            perimes_data = [["Article", "Date péremption", "Jours écart", "Quantité"]]
            for article in donnees.articles_perimes[:10]:
                perimes_data.append(
                    [
                        article["nom"][:30],
                        article["date_peremption"].strftime("%d/%m/%Y"),
                        f"{article['jours_perime']} j",
                        f"{article['quantite']} {article['unite']}",
                    ]
                )

            perimes_table = Table(
                perimes_data, colWidths=[2 * inch, 1.5 * inch, 1.2 * inch, 1.3 * inch]
            )
            perimes_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D32F2F")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#FFEBEE")],
                        ),
                    ]
                )
            )
            elements.append(perimes_table)
            elements.append(Spacer(1, 0.2 * inch))

        # Catégories
        if donnees.categories_resumee:
            elements.append(PageBreak())
            elements.append(Paragraph("📦 RÉSUMÉ PAR CATÉGORIE", heading_style))
            cat_data = [["Catégorie", "Articles", "Quantité", "Valeur €"]]
            for cat, data in donnees.categories_resumee.items():
                cat_data.append(
                    [cat, str(data["articles"]), f"{data['quantite']}", f"{data['valeur']:.2f}"]
                )

            cat_table = Table(cat_data, colWidths=[2 * inch, 1.2 * inch, 1.2 * inch, 1.6 * inch])
            cat_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976D2")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightblue]),
                    ]
                )
            )
            elements.append(cat_table)

        # Générer le PDF
        doc.build(elements)
        buffer.seek(0)

        return buffer

    # ═══════════════════════════════════════════════════════════
    # UTILITAIRES
    # ═══════════════════════════════════════════════════════════

    # NOTE: Les méthodes de rapport budget (generer_donnees_rapport_budget,
    # generer_pdf_rapport_budget) sont fournies par BudgetReportMixin
    # (voir rapports_budget.py)

    # NOTE: Les méthodes d'analyse gaspillage (generer_analyse_gaspillage,
    # generer_pdf_analyse_gaspillage) sont fournies par GaspillageReportMixin
    # (voir rapports_gaspillage.py)

    def telecharger_rapport_pdf(
        self, type_rapport: str, periode_jours: int = 30
    ) -> tuple[BytesIO, str]:
        """
        Prépare un rapport pour téléchargement.

        Args:
            type_rapport: 'stocks', 'budget' ou 'gaspillage'
            periode_jours: Période à analyser

        Returns:
            (BytesIO, filename)
        """
        now = datetime.now()

        if type_rapport == "stocks":
            pdf = self.generer_pdf_rapport_stocks(7)  # Toujours hebdo
            filename = f"rapport_stocks_{now.strftime('%Y%m%d_%H%M%S')}.pdf"

        elif type_rapport == "budget":
            pdf = self.generer_pdf_rapport_budget(periode_jours)
            filename = f"rapport_budget_{now.strftime('%Y%m%d_%H%M%S')}.pdf"

        elif type_rapport == "gaspillage":
            pdf = self.generer_pdf_analyse_gaspillage(periode_jours)
            filename = f"analyse_gaspillage_{now.strftime('%Y%m%d_%H%M%S')}.pdf"

        else:
            raise ErreurValidation(f"Type de rapport inconnu: {type_rapport}")

        return pdf, filename

    # NOTE: Les méthodes de rapport planning (generer_donnees_rapport_planning,
    # generer_pdf_rapport_planning, telecharger_rapport_planning) sont fournies
    # par PlanningReportMixin (voir planning_pdf.py)


# ═══════════════════════════════════════════════════════════
# FACTORY FUNCTION (Singleton pattern)
# ═══════════════════════════════════════════════════════════

from src.services.core.registry import service_factory


@service_factory("rapports_pdf", tags={"rapports", "export"})
def obtenir_service_rapports_pdf() -> ServiceRapportsPDF:
    """Retourne l'instance du service de rapports PDF (thread-safe via registre)."""
    return ServiceRapportsPDF()


def get_pdf_reports_service() -> ServiceRapportsPDF:
    """Factory for PDF reports service (English alias)."""
    return obtenir_service_rapports_pdf()


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    "ServiceRapportsPDF",
    "obtenir_service_rapports_pdf",
    "get_pdf_reports_service",
]
