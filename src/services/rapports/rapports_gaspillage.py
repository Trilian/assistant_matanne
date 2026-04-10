"""
Mixin Rapport Gaspillage PDF.

Extrait de generation.py - Contient la génération de rapports PDF
pour l'analyse du gaspillage alimentaire.
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
from src.core.models import ArticleInventaire
from src.services.rapports._couleurs import Couleur
from src.services.rapports.types import AnalyseGaspillage

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# MIXIN RAPPORT GASPILLAGE
# ═══════════════════════════════════════════════════════════


class GaspillageReportMixin:
    """Mixin fournissant les méthodes d'analyse gaspillage PDF."""

    @avec_cache(ttl=300)
    @avec_session_db
    def generer_analyse_gaspillage(
        self, periode_jours: int = 30, session: Session = None
    ) -> AnalyseGaspillage:
        """
        Analyse le gaspillage (articles périmés, etc).

        Args:
            periode_jours: Nombre de jours à analyser
            session: Session DB

        Returns:
            Analyse détaillée
        """
        analyse = AnalyseGaspillage(periode_jours=periode_jours)

        articles = session.query(ArticleInventaire).all()
        maintenant = datetime.now()
        gaspillage_par_cat = {}

        for article in articles:
            # Articles périmés
            if article.date_peremption and article.date_peremption < maintenant:
                analyse.articles_perimes_total += 1

                if article.prix_unitaire:
                    valeur_perdue = article.quantite * article.prix_unitaire
                    analyse.valeur_perdue += valeur_perdue

                # Par catégorie
                if article.categorie not in gaspillage_par_cat:
                    gaspillage_par_cat[article.categorie] = {"articles": 0, "valeur": 0.0}
                gaspillage_par_cat[article.categorie]["articles"] += 1
                if article.prix_unitaire:
                    gaspillage_par_cat[article.categorie]["valeur"] += valeur_perdue

                # Détail
                analyse.articles_perimes_detail.append(
                    {
                        "nom": article.nom,
                        "date_peremption": article.date_peremption,
                        "jours_perime": (maintenant - article.date_peremption).days,
                        "quantite": article.quantite,
                        "unite": article.unite,
                        "valeur_perdue": article.prix_unitaire * article.quantite
                        if article.prix_unitaire
                        else 0,
                    }
                )

        analyse.categories_gaspillage = gaspillage_par_cat

        # Recommandations
        analyse.recommandations = []
        if analyse.articles_perimes_total > 5:
            analyse.recommandations.append(
                "⚠️ Gaspillage important détecté: améliorer la planification des achats"
            )
        if analyse.valeur_perdue > 50:
            analyse.recommandations.append(
                f"💰 Valeur perdue: €{analyse.valeur_perdue:.2f} - Optimiser l'inventaire"
            )
        if analyse.articles_perimes_detail:
            analyse.recommandations.append("📅 Mettre en place un FIFO (First In First Out) strict")

        return analyse

    @avec_session_db
    def generer_pdf_analyse_gaspillage(
        self, periode_jours: int = 30, session: Session = None
    ) -> BytesIO:
        """
        Génère un PDF de l'analyse gaspillage.

        Args:
            periode_jours: Nombre de jours
            session: Session DB

        Returns:
            Fichier PDF en BytesIO
        """
        analyse = self.generer_analyse_gaspillage(periode_jours, session=session)

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
            textColor=colors.HexColor(Couleur.CHART_SNACK),
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor(Couleur.BLUE_700),
            spaceAfter=12,
            spaceBefore=12,
        )

        # Contenu
        elements = []

        # Titre
        elements.append(Paragraph("🗑️ ANALYSE GASPILLAGE", title_style))
        elements.append(
            Paragraph(
                f"Généré le {analyse.date_rapport.strftime('%d/%m/%Y à %H:%M')}", styles["Normal"]
            )
        )
        elements.append(Spacer(1, 0.3 * inch))

        # Résumé
        elements.append(Paragraph("📊 RÉSUMÉ GASPILLAGE", heading_style))
        summary_data = [
            ["Métrique", "Valeur"],
            ["Articles périmés", str(analyse.articles_perimes_total)],
            ["Valeur perdue", f"€{analyse.valeur_perdue:.2f}"],
            [
                "Moyenne par article",
                f"€{analyse.valeur_perdue / max(analyse.articles_perimes_total, 1):.2f}",
            ],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(Couleur.CHART_SNACK)),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor(Couleur.BG_LIGHT_PINK)),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Recommandations
        if analyse.recommandations:
            elements.append(Paragraph("💡 RECOMMANDATIONS", heading_style))
            for rec in analyse.recommandations:
                elements.append(Paragraph(f"• {rec}", styles["Normal"]))
            elements.append(Spacer(1, 0.2 * inch))

        # Articles périmés détail
        if analyse.articles_perimes_detail:
            elements.append(Paragraph("❌ ARTICLES PÉRIMÉS DÉTAIL", heading_style))

            detail_data = [["Article", "Périmé depuis", "Quantité", "Valeur perdue"]]
            for article in analyse.articles_perimes_detail[:15]:
                detail_data.append(
                    [
                        article["nom"][:25],
                        f"{article['jours_perime']} j",
                        f"{article['quantite']} {article['unite']}",
                        f"€{article['valeur_perdue']:.2f}",
                    ]
                )

            detail_table = Table(
                detail_data, colWidths=[1.8 * inch, 1.2 * inch, 1.2 * inch, 1.8 * inch]
            )
            detail_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(Couleur.SCALE_CRITICAL)),
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
                            [colors.white, colors.HexColor(Couleur.BG_LIGHT_RED_ALT)],
                        ),
                    ]
                )
            )
            elements.append(detail_table)
            elements.append(Spacer(1, 0.2 * inch))

        # Gaspillage par catégorie
        if analyse.categories_gaspillage:
            elements.append(PageBreak())
            elements.append(Paragraph("📦 GASPILLAGE PAR CATÉGORIE", heading_style))

            cat_data = [["Catégorie", "Articles", "Valeur perdue"]]
            for cat, data in sorted(
                analyse.categories_gaspillage.items(), key=lambda x: x[1]["valeur"], reverse=True
            ):
                cat_data.append([cat, str(data["articles"]), f"€{data['valeur']:.2f}"])

            cat_table = Table(cat_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch])
            cat_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(Couleur.AMBER_800)),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor(Couleur.BG_LIGHT_ORANGE)],
                        ),
                    ]
                )
            )
            elements.append(cat_table)

        # Générer le PDF
        doc.build(elements)
        buffer.seek(0)

        return buffer
