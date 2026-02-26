"""
Mixin Rapport Planning PDF.

Extrait de generation.py - Contient la génération de rapports PDF
pour les plannings de repas hebdomadaires.
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
from sqlalchemy.orm import Session, selectinload

from src.core.decorators import avec_session_db
from src.core.exceptions import ErreurNonTrouve
from src.core.models import (
    Planning,
    Recette,
    RecetteIngredient,
    Repas,
)
from src.services.rapports.types import RapportPlanning
from src.ui.tokens import Couleur

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# MIXIN RAPPORT PLANNING
# ═══════════════════════════════════════════════════════════


class PlanningReportMixin:
    """Mixin fournissant les méthodes de rapport planning PDF."""

    @avec_session_db
    def generer_donnees_rapport_planning(
        self, planning_id: int, session: Session = None
    ) -> RapportPlanning:
        """
        Collecte les données pour rapport planning.

        Args:
            planning_id: ID du planning
            session: Session DB

        Returns:
            Données structurées du rapport
        """
        # Eager loading pour éviter N+1 queries
        planning = (
            session.query(Planning)
            .options(
                selectinload(Planning.repas)
                .selectinload(Repas.recette)
                .selectinload(Recette.ingredients)
                .selectinload(RecetteIngredient.ingredient)
            )
            .filter_by(id=planning_id)
            .first()
        )

        if not planning:
            raise ErreurNonTrouve(f"Planning {planning_id} non trouvé")

        rapport = RapportPlanning(
            planning_id=planning.id,
            nom_planning=planning.nom,
            semaine_debut=planning.semaine_debut,
            semaine_fin=planning.semaine_fin,
        )

        # Organiser les repas par jour
        repas_par_jour = {}
        ingredients_needed = {}

        for repas in planning.repas:
            date_str = repas.date_repas.strftime("%Y-%m-%d")

            if date_str not in repas_par_jour:
                repas_par_jour[date_str] = []

            repas_info = {
                "type": repas.type_repas,
                "recette_nom": repas.recette.nom if repas.recette else "Repas libre",
                "portions": repas.portion_ajustee
                or (repas.recette.portions if repas.recette else 2),
                "prepare": repas.prepare,
                "notes": repas.notes,
            }
            repas_par_jour[date_str].append(repas_info)
            rapport.total_repas += 1

            # Collecter ingrédients pour liste courses
            if repas.recette and hasattr(repas.recette, "ingredients"):
                for ri in repas.recette.ingredients:
                    if ri.ingredient:
                        nom = ri.ingredient.nom
                        if nom not in ingredients_needed:
                            ingredients_needed[nom] = {
                                "nom": nom,
                                "quantite": 0,
                                "unite": ri.unite or ri.ingredient.unite_defaut or "unité",
                            }
                        ingredients_needed[nom]["quantite"] += ri.quantite or 0

        rapport.repas_par_jour = repas_par_jour
        rapport.liste_courses_estimee = list(ingredients_needed.values())

        return rapport

    @avec_session_db
    def generer_pdf_rapport_planning(self, planning_id: int, session: Session = None) -> BytesIO:
        """
        Génère un PDF du planning de repas.

        Args:
            planning_id: ID du planning
            session: Session DB

        Returns:
            Fichier PDF en BytesIO
        """
        donnees = self.generer_donnees_rapport_planning(planning_id, session=session)

        # Créer le PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "PlanningTitle",
            parent=styles["Heading1"],
            fontSize=22,
            textColor=colors.HexColor(Couleur.SUCCESS),
            spaceAfter=20,
            alignment=TA_CENTER,
        )
        subtitle_style = ParagraphStyle(
            "PlanningSubtitle",
            parent=styles["Normal"],
            fontSize=12,
            textColor=colors.HexColor(Couleur.TEXT_SECONDARY),
            spaceAfter=20,
            alignment=TA_CENTER,
        )
        day_style = ParagraphStyle(
            "DayHeader",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor(Couleur.BLUE_700),
            spaceAfter=8,
            spaceBefore=15,
        )

        elements = []

        # En-tête
        elements.append(Paragraph(f"🍽️ {donnees.nom_planning}", title_style))

        date_range = ""
        if donnees.semaine_debut and donnees.semaine_fin:
            date_range = f"Du {donnees.semaine_debut.strftime('%d/%m/%Y')} au {donnees.semaine_fin.strftime('%d/%m/%Y')}"
        elements.append(Paragraph(date_range, subtitle_style))
        elements.append(Spacer(1, 0.2 * inch))

        # Statistiques rapides
        stats_data = [
            ["📊 Statistiques", ""],
            ["Total repas planifiés", str(donnees.total_repas)],
            ["Ingrédients nécessaires", str(len(donnees.liste_courses_estimee))],
        ]
        stats_table = Table(stats_data, colWidths=[3 * inch, 2 * inch])
        stats_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(Couleur.SUCCESS)),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor(Couleur.BG_LIGHT_GREEN)],
                    ),
                ]
            )
        )
        elements.append(stats_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Planning jour par jour
        elements.append(Paragraph("📅 PLANNING DE LA SEMAINE", day_style))
        elements.append(Spacer(1, 0.1 * inch))

        jours_fr = {
            0: "Lundi",
            1: "Mardi",
            2: "Mercredi",
            3: "Jeudi",
            4: "Vendredi",
            5: "Samedi",
            6: "Dimanche",
        }

        type_repas_emoji = {
            "petit_déjeuner": "🌅",
            "déjeuner": "☀️",
            "goûter": "🍪",
            "dîner": "🌙",
        }

        for date_str in sorted(donnees.repas_par_jour.keys()):
            repas_jour = donnees.repas_par_jour[date_str]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            jour_nom = jours_fr.get(date_obj.weekday(), "")

            # Tableau pour ce jour
            day_data = [
                [f"📅 {jour_nom} {date_obj.strftime('%d/%m')}", "Recette", "Portions", "Status"]
            ]

            for repas in sorted(
                repas_jour,
                key=lambda x: (
                    ["petit_déjeuner", "déjeuner", "goûter", "dîner"].index(x["type"])
                    if x["type"] in ["petit_déjeuner", "déjeuner", "goûter", "dîner"]
                    else 99
                ),
            ):
                emoji = type_repas_emoji.get(repas["type"], "🍴")
                status = "✅" if repas["prepare"] else "⏳"
                day_data.append(
                    [
                        f"{emoji} {repas['type'].replace('_', ' ').title()}",
                        repas["recette_nom"][:25],
                        str(repas["portions"]),
                        status,
                    ]
                )

            day_table = Table(day_data, colWidths=[2 * inch, 2.5 * inch, 1 * inch, 0.8 * inch])
            day_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(Couleur.INFO)),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("ALIGN", (2, 0), (3, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor(Couleur.BG_LIGHT_BLUE)],
                        ),
                    ]
                )
            )
            elements.append(day_table)
            elements.append(Spacer(1, 0.15 * inch))

        # Liste des courses
        if donnees.liste_courses_estimee:
            elements.append(PageBreak())
            elements.append(Paragraph("🛒 LISTE DE COURSES ESTIMÉE", day_style))
            elements.append(Spacer(1, 0.1 * inch))

            courses_data = [["Ingrédient", "Quantité", "Unité"]]
            for ing in sorted(donnees.liste_courses_estimee, key=lambda x: x["nom"]):
                courses_data.append(
                    [
                        ing["nom"][:30],
                        f"{ing['quantite']:.0f}" if ing["quantite"] else "-",
                        ing["unite"],
                    ]
                )

            courses_table = Table(courses_data, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch])
            courses_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(Couleur.ORANGE)),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor(Couleur.BG_LIGHT_ORANGE)],
                        ),
                    ]
                )
            )
            elements.append(courses_table)

        # Footer
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(
            Paragraph(
                f"Généré le {donnees.date_rapport.strftime('%d/%m/%Y à %H:%M')} • Assistant Matanne 🏠",
                ParagraphStyle(
                    "Footer",
                    parent=styles["Normal"],
                    fontSize=8,
                    textColor=colors.grey,
                    alignment=TA_CENTER,
                ),
            )
        )

        # Générer le PDF
        doc.build(elements)
        buffer.seek(0)

        return buffer

    def telecharger_rapport_planning(self, planning_id: int) -> tuple[BytesIO, str]:
        """
        Prépare un rapport planning pour téléchargement.

        Args:
            planning_id: ID du planning

        Returns:
            (BytesIO, filename)
        """
        now = datetime.now()
        pdf = self.generer_pdf_rapport_planning(planning_id)
        filename = f"planning_semaine_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
        return pdf, filename


__all__ = [
    "PlanningReportMixin",
]
