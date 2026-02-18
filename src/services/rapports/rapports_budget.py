"""
Mixin Rapport Budget PDF.

Extrait de generation.py - Contient la génération de rapports PDF
pour l'analyse budget et dépenses.
"""

import logging
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.core.models import ArticleInventaire
from src.services.rapports.types import RapportBudget

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# MIXIN RAPPORT BUDGET
# ═══════════════════════════════════════════════════════════


class BudgetReportMixin:
    """Mixin fournissant les méthodes de rapport budget/dépenses PDF."""

    @avec_session_db
    def generer_donnees_rapport_budget(
        self, periode_jours: int = 30, session: Session = None
    ) -> RapportBudget:
        """
        Collecte les données pour rapport budget.

        Args:
            periode_jours: Nombre de jours à analyser
            session: Session DB

        Returns:
            Données structurées
        """
        rapport = RapportBudget(periode_jours=periode_jours)

        # TODO: Implémenter avec historique d'achats si disponible
        # Pour maintenant, calculer à partir du stock actuel

        articles = session.query(ArticleInventaire).all()
        depenses_par_cat = {}
        articles_couteux = []

        for article in articles:
            if article.prix_unitaire:
                cout = article.quantite * article.prix_unitaire
                rapport.depenses_total += cout

                if article.categorie not in depenses_par_cat:
                    depenses_par_cat[article.categorie] = 0.0
                depenses_par_cat[article.categorie] += cout

                if cout > 10:  # Articles coûteux
                    articles_couteux.append(
                        {
                            "nom": article.nom,
                            "quantite": article.quantite,
                            "unite": article.unite,
                            "prix_unitaire": article.prix_unitaire,
                            "cout_total": cout,
                            "categorie": article.categorie,
                        }
                    )

        rapport.depenses_par_categorie = depenses_par_cat
        rapport.articles_couteux = sorted(
            articles_couteux, key=lambda x: x["cout_total"], reverse=True
        )[:10]

        return rapport

    @avec_session_db
    def generer_pdf_rapport_budget(
        self, periode_jours: int = 30, session: Session = None
    ) -> BytesIO:
        """
        Génère un PDF du rapport budget.

        Args:
            periode_jours: Nombre de jours
            session: Session DB

        Returns:
            Fichier PDF en BytesIO
        """
        donnees = self.generer_donnees_rapport_budget(periode_jours, session=session)

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
            textColor=colors.HexColor("#D32F2F"),
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
        elements.append(Paragraph("💰 RAPPORT BUDGET/DÉPENSES", title_style))
        elements.append(
            Paragraph(
                f"Généré le {donnees.date_rapport.strftime('%d/%m/%Y à %H:%M')}", styles["Normal"]
            )
        )
        elements.append(Spacer(1, 0.3 * inch))

        # Résumé
        elements.append(Paragraph("💵 RÉSUMÉ FINANCIER", heading_style))
        summary_data = [
            ["Métrique", "Valeur"],
            ["Dépenses totales", f"€{donnees.depenses_total:.2f}"],
            ["Période analysée", f"{donnees.periode_jours} jours"],
            ["Articles coûteux", str(len(donnees.articles_couteux))],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D32F2F")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.lightyellow),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Dépenses par catégorie
        if donnees.depenses_par_categorie:
            elements.append(Paragraph("📊 DÉPENSES PAR CATÉGORIE", heading_style))
            cat_data = [["Catégorie", "Montant €", "% du total"]]
            for cat, montant in sorted(
                donnees.depenses_par_categorie.items(), key=lambda x: x[1], reverse=True
            ):
                pct = (montant / donnees.depenses_total * 100) if donnees.depenses_total > 0 else 0
                cat_data.append([cat, f"€{montant:.2f}", f"{pct:.1f}%"])

            cat_table = Table(cat_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch])
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
            elements.append(Spacer(1, 0.2 * inch))

        # Articles coûteux
        if donnees.articles_couteux:
            elements.append(Paragraph("⭐ ARTICLES LES PLUS COÛTEUX", heading_style))
            costly_data = [["Article", "Catégorie", "Quantité", "Coût total €"]]
            for article in donnees.articles_couteux[:10]:
                costly_data.append(
                    [
                        article["nom"][:25],
                        article["categorie"],
                        f"{article['quantite']} {article['unite']}",
                        f"€{article['cout_total']:.2f}",
                    ]
                )

            costly_table = Table(
                costly_data, colWidths=[1.8 * inch, 1.5 * inch, 1.5 * inch, 1.2 * inch]
            )
            costly_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F57F17")),
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
            elements.append(costly_table)

        # Générer le PDF
        doc.build(elements)
        buffer.seek(0)

        return buffer
