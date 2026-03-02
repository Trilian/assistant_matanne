"""
Module Planificateur de Repas - Génération PDF
"""

import logging
import re
from datetime import date, datetime, timedelta
from io import BytesIO

logger = logging.getLogger(__name__)

_EMOJI_RE = re.compile(
    "["
    "\U0001f600-\U0001f64f"  # emoticons
    "\U0001f300-\U0001f5ff"  # symbols & pictographs
    "\U0001f680-\U0001f6ff"  # transport & map
    "\U0001f700-\U0001f77f"  # alchemical
    "\U0001f780-\U0001f7ff"  # geometric extended
    "\U0001f800-\U0001f8ff"  # misc arrows
    "\U0001f900-\U0001f9ff"  # supplemental symbols
    "\U0001fa00-\U0001fa6f"  # chess
    "\U0001fa70-\U0001faff"  # symbols & pictographs extended
    "\U00002300-\U00002bff"  # misc technical & dingbats
    "\U0000fe00-\U0000fe0f"  # variation selectors
    "\U00020000-\U0002a6df"
    "\U0002a700-\U0002b73f"
    "\U0002b740-\U0002b81f"
    "\U0002b820-\U0002ceaf"
    "\u200d"  # zero-width joiner
    "\u2640-\u2642"  # gender signs
    "\u2600-\u26ff"  # misc symbols
    "\u2700-\u27bf"  # dingbats
    "]",
    flags=re.UNICODE,
)


def _pdf_text(text: str) -> str:
    """Supprime les emojis pour compatibilité avec les polices ReportLab."""
    return _EMOJI_RE.sub("", text).strip()


def generer_pdf_planning_session(
    planning_data: dict, date_debut: date, conseils: str = "", suggestions_bio: list = None
) -> BytesIO | None:
    """
    Génère un PDF du planning depuis les données en session.

    Args:
        planning_data: Données du planning {jour: {midi, soir, gouter}}
        date_debut: Date de début du planning
        conseils: Conseils batch cooking
        suggestions_bio: Liste de suggestions bio/local

    Returns:
        BytesIO contenant le PDF ou None en cas d'erreur
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm, inch
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

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
            textColor=colors.HexColor("#4CAF50"),
            spaceAfter=20,
            alignment=TA_CENTER,
        )
        subtitle_style = ParagraphStyle(
            "PlanningSubtitle",
            parent=styles["Normal"],
            fontSize=12,
            textColor=colors.HexColor("#666666"),
            spaceAfter=20,
            alignment=TA_CENTER,
        )
        day_style = ParagraphStyle(
            "DayHeader",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#1976D2"),
            spaceAfter=8,
            spaceBefore=15,
        )

        elements = []

        # En-tête
        date_fin = date_debut + timedelta(days=len(planning_data) - 1)
        elements.append(Paragraph("Planning Repas Famille Matanne", title_style))
        elements.append(
            Paragraph(
                f"Du {date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}",
                subtitle_style,
            )
        )
        elements.append(Spacer(1, 0.2 * inch))

        # Table repas par jour
        type_repas_emoji = {
            "midi": "☀️",
            "soir": "🌙",
            "gouter": "🍪",
        }

        for i, (jour, repas) in enumerate(planning_data.items()):
            jour_date = date_debut + timedelta(days=i)

            # Tableau pour ce jour
            day_data = [[f"📅 {jour} {jour_date.strftime('%d/%m')}", "Repas"]]

            for type_repas in ["midi", "soir", "gouter"]:
                if type_repas in repas and repas[type_repas]:
                    recette_nom = repas[type_repas]
                    if isinstance(recette_nom, dict):
                        recette_nom = recette_nom.get("nom", str(recette_nom))
                    emoji = type_repas_emoji.get(type_repas, "🍴")
                    label = {"midi": "Déjeuner", "soir": "Dîner", "gouter": "Goûter"}.get(
                        type_repas, type_repas
                    )
                    day_data.append([f"{emoji} {label}", str(recette_nom)[:40]])

            day_table = Table(day_data, colWidths=[2.5 * inch, 4 * inch])
            day_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2196F3")),
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
                            [colors.white, colors.HexColor("#E3F2FD")],
                        ),
                    ]
                )
            )
            elements.append(day_table)
            elements.append(Spacer(1, 0.15 * inch))

        # Conseils batch cooking
        if conseils:
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph("Conseils Batch Cooking", day_style))
            elements.append(Paragraph(_pdf_text(conseils), styles["Normal"]))

        # Suggestions bio
        if suggestions_bio:
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph("Suggestions Bio/Local", day_style))
            for sug in suggestions_bio:
                elements.append(Paragraph(f"- {_pdf_text(sug)}", styles["Normal"]))

        # Footer
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(
            Paragraph(
                f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} - Assistant Matanne",
                ParagraphStyle(
                    "Footer",
                    parent=styles["Normal"],
                    fontSize=8,
                    textColor=colors.grey,
                    alignment=TA_CENTER,
                ),
            )
        )

        doc.build(elements)
        buffer.seek(0)

        return buffer

    except Exception as e:
        logger.error(f"❌ Erreur génération PDF planning: {e}")
        return None
