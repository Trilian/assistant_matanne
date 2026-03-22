"""
Module Planificateur de Repas - Génération PDF
"""

import logging
import re
from datetime import date, datetime, timedelta
from io import BytesIO
import unicodedata

import streamlit as st

from src.core.session_keys import SK

logger = logging.getLogger(__name__)

_EMOJI_RE = re.compile(
    "["
    "\U0001f600-\U0001f64f"
    "\U0001f300-\U0001f5ff"
    "\U0001f680-\U0001f6ff"
    "\U0001f700-\U0001f77f"
    "\U0001f780-\U0001f7ff"
    "\U0001f800-\U0001f8ff"
    "\U0001f900-\U0001f9ff"
    "\U0001fa00-\U0001fa6f"
    "\U0001fa70-\U0001faff"
    "\U00002300-\U00002bff"
    "\U0000fe00-\U0000fe0f"
    "\U00020000-\U0002a6df"
    "\U0002a700-\U0002b73f"
    "\U0002b740-\U0002b81f"
    "\U0002b820-\U0002ceaf"
    "\u200d"
    "\u2640-\u2642"
    "\u2600-\u26ff"
    "\u2700-\u27bf"
    "]",
    flags=re.UNICODE,
)

# Couleurs palette
_VERT = "#4CAF50"
_VERT_CLAIR = "#E8F5E9"
_BLEU = "#1976D2"
_BLEU_CLAIR = "#E3F2FD"
_GRIS = "#757575"
_GRIS_CLAIR = "#F5F5F5"
_BLANC = "#FFFFFF"
_ORANGE = "#FF9800"
_TEXTE = "#212121"

_JOURS_FR = {
    "Monday": "Lundi",
    "Tuesday": "Mardi",
    "Wednesday": "Mercredi",
    "Thursday": "Jeudi",
    "Friday": "Vendredi",
    "Saturday": "Samedi",
    "Sunday": "Dimanche",
}

_REPAS_LABEL = {
    "midi": "Déjeuner",
    "soir": "Dîner",
    "gouter": "Goûter",
}


def _t(text: str) -> str:
    """Supprime les emojis pour compatibilité avec les polices ReportLab."""
    return _EMOJI_RE.sub("", str(text)).strip()


def _normaliser_texte(texte: str) -> str:
    """Normalise en minuscules ASCII pour matching souple."""
    ascii_text = unicodedata.normalize("NFKD", str(texte or ""))
    ascii_text = ascii_text.encode("ascii", "ignore").decode("ascii")
    return ascii_text.lower().strip()


def _obtenir_nom_foyer() -> str:
    """Retourne le nom de foyer configuré, avec fallback sûr."""
    try:
        cfg = st.session_state.get(SK.FOYER_CONFIG, {}) or {}
        if isinstance(cfg, dict):
            nom_foyer = str(cfg.get("nom_foyer", "")).strip()
            if nom_foyer:
                return nom_foyer
            nom_utilisateur = str(cfg.get("nom_utilisateur", "")).strip()
            if nom_utilisateur:
                return f"Foyer de {nom_utilisateur}"
    except Exception:
        pass
    return "Famille"


def _adapter_suggestions_bio_au_planning(
    planning_data: dict,
    suggestions_bio: list[str] | None,
) -> list[str]:
    """Filtre/complète les suggestions bio selon les repas réellement planifiés."""
    suggestions = [str(s).strip() for s in (suggestions_bio or []) if str(s).strip()]

    mots_cles: set[str] = set()
    proteines: set[str] = set()
    for repas_jour in planning_data.values():
        if not isinstance(repas_jour, dict):
            continue
        for slot in ["midi", "soir"]:
            meal = repas_jour.get(slot)
            if not isinstance(meal, dict):
                continue

            prot = _normaliser_texte(meal.get("proteine", ""))
            if prot:
                proteines.add(prot)
                mots_cles.add(prot)

            for ing in meal.get("ingredients", []) or []:
                if isinstance(ing, dict):
                    nom = _normaliser_texte(ing.get("nom", ""))
                    if nom:
                        mots_cles.add(nom)

    if suggestions and mots_cles:
        suggestions_filtrees = [
            s
            for s in suggestions
            if any(mot in _normaliser_texte(s) for mot in mots_cles)
        ]
    else:
        suggestions_filtrees = []

    suggestions_finales: list[str] = suggestions_filtrees[:8]

    catalogue = {
        "poulet": "Filets de poulet fermier bio ou Label Rouge (meilleure qualité gustative)",
        "dinde": "Dinde fermière locale (souvent plus tendre et moins transformée)",
        "boeuf": "Boeuf Label Rouge ou local (traçabilité et meilleure maturation)",
        "porc": "Porc fermier local (viande plus goûteuse pour mijotés)",
        "agneau": "Agneau local de saison (origine claire et fraîcheur)",
        "cabillaud": "Cabillaud certifié pêche durable (MSC) ou Label Rouge",
        "colin": "Colin sauvage certifié MSC (poisson durable)",
        "merlu": "Merlu de pêche durable (meilleur rapport qualité/prix)",
        "saumon": "Saumon Label Rouge ou bio (chair plus ferme et moins grasse)",
        "thon": "Thon en conserve label pêche responsable (MSC)",
        "sardine": "Sardines en boîte artisanales à l'huile d'olive vierge",
        "maquereau": "Filets de maquereau pêchés en Atlantique Nord-Est",
        "crevettes": "Crevettes certifiées ASC/MSC (origine et traçabilité)",
        "oeufs": "Oeufs plein air Label Rouge (meilleure qualité nutritionnelle)",
        "tofu": "Tofu bio français (filière soja locale)",
        "legumineuses": "Légumineuses bio en vrac (lentilles/pois chiches) pour réduire le coût",
    }

    for prot in sorted(proteines):
        cle_trouvee = None
        for cle in catalogue:
            if cle in prot or prot in cle:
                cle_trouvee = cle
                break
        if cle_trouvee:
            proposition = catalogue[cle_trouvee]
            if proposition not in suggestions_finales:
                suggestions_finales.append(proposition)
        if len(suggestions_finales) >= 8:
            break

    return suggestions_finales[:8]


def generer_pdf_planning_session(
    planning_data: dict, date_debut: date, conseils: str = "", suggestions_bio: list = None
) -> BytesIO | None:
    """Génère un PDF du planning depuis les données en session."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            HRFlowable,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )

        buffer = BytesIO()
        nom_foyer = _t(_obtenir_nom_foyer())

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.8 * cm,
            leftMargin=1.8 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
            title=f"Planning Repas {nom_foyer}",
        )

        styles = getSampleStyleSheet()

        # â”€â”€ Styles â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        s_title = ParagraphStyle(
            "Title",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=20,
            textColor=colors.HexColor(_VERT),
            spaceAfter=10,
            alignment=TA_CENTER,
        )
        s_subtitle = ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            textColor=colors.HexColor(_GRIS),
            spaceBefore=0,
            spaceAfter=16,
            alignment=TA_CENTER,
        )
        s_day = ParagraphStyle(
            "Day",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=colors.white,
        )
        s_meal_type = ParagraphStyle(
            "MealType",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=colors.HexColor(_BLEU),
        )
        s_meal_name = ParagraphStyle(
            "MealName",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor(_TEXTE),
        )
        s_jules = ParagraphStyle(
            "Jules",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8,
            textColor=colors.HexColor(_ORANGE),
            leftIndent=8,
        )
        s_section = ParagraphStyle(
            "Section",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=colors.HexColor(_BLEU),
            spaceBefore=12,
            spaceAfter=6,
        )
        s_normal = ParagraphStyle(
            "Normal2",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor(_TEXTE),
            spaceAfter=3,
        )
        s_footer = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=colors.HexColor(_GRIS),
            alignment=TA_CENTER,
        )

        PAGE_W = A4[0] - 3.6 * cm  # largeur utile

        elements = []

        # â”€â”€ En-tête â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        date_fin = date_debut + timedelta(days=len(planning_data) - 1)
        elements.append(Paragraph(f"Planning Repas — {nom_foyer}", s_title))
        elements.append(
            Paragraph(
                f"Du {date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}",
                s_subtitle,
            )
        )
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor(_VERT)))
        elements.append(Spacer(1, 10))

        # â”€â”€ Planning par jour â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        for i, (jour, repas) in enumerate(planning_data.items()):
            jour_date = date_debut + timedelta(days=i)
            jour_nom = _t(jour)
            date_str = jour_date.strftime("%A %d/%m").replace(
                jour_date.strftime("%A"),
                _JOURS_FR.get(jour_date.strftime("%A"), jour_date.strftime("%A")),
            )

            # En-tête du jour — pleine largeur, fond vert
            day_header = Table(
                [[Paragraph(f"{jour_nom}  —  {date_str}", s_day)]],
                colWidths=[PAGE_W],
            )
            day_header.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(_VERT)),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("ROUNDEDCORNERS", [4, 4, 0, 0]),  # ignoré par ReportLab mais sans erreur
                    ]
                )
            )
            elements.append(day_header)

            # Lignes repas
            rows = []
            row_colors = []

            for j, type_repas in enumerate(["midi", "gouter", "soir"]):
                r = repas.get(type_repas)
                if not r:
                    continue
                nom = _t(r.get("nom", "—")) if isinstance(r, dict) else _t(str(r))
                temps = r.get("temps_minutes", "") if isinstance(r, dict) else ""
                temps_str = f"  ({temps} min)" if temps else ""
                jules = _t(r.get("jules_adaptation", "")) if isinstance(r, dict) else ""

                label = _REPAS_LABEL.get(type_repas, type_repas.capitalize())
                cell_type = Paragraph(label, s_meal_type)
                cell_nom_content = [Paragraph(f"{nom}{temps_str}", s_meal_name)]
                if jules:
                    cell_nom_content.append(Paragraph(f"Jules : {jules[:120]}", s_jules))

                rows.append([cell_type, cell_nom_content])
                row_colors.append(_BLEU_CLAIR if j % 2 == 0 else _BLANC)

            if rows:
                meal_table = Table(rows, colWidths=[2.5 * cm, PAGE_W - 2.5 * cm])
                style = TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#DDDDDD")),
                        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(_GRIS)),
                    ]
                )
                for k, bg in enumerate(row_colors):
                    style.add("BACKGROUND", (0, k), (-1, k), colors.HexColor(bg))
                meal_table.setStyle(style)
                elements.append(meal_table)
            else:
                empty = Table(
                    [[Paragraph("Aucun repas planifié", s_normal)]],
                    colWidths=[PAGE_W],
                )
                empty.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(_GRIS_CLAIR)),
                            ("TOPPADDING", (0, 0), (-1, -1), 6),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                            ("LEFTPADDING", (0, 0), (-1, -1), 8),
                            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(_GRIS)),
                        ]
                    )
                )
                elements.append(empty)

            elements.append(Spacer(1, 6))

        # â”€â”€ Conseils batch cooking â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if conseils:
            elements.append(Spacer(1, 8))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(_GRIS)))
            elements.append(Paragraph("Conseils Batch Cooking", s_section))
            elements.append(Paragraph(_t(conseils), s_normal))

        # â”€â”€ Suggestions bio â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        suggestions_contextualisees = _adapter_suggestions_bio_au_planning(
            planning_data=planning_data,
            suggestions_bio=suggestions_bio,
        )
        if suggestions_contextualisees:
            elements.append(Spacer(1, 8))
            elements.append(Paragraph("Suggestions Bio / Local", s_section))
            for sug in suggestions_contextualisees:
                elements.append(Paragraph(f"• {_t(sug)}", s_normal))

        # â”€â”€ Footer â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor(_GRIS)))
        elements.append(
            Paragraph(
                f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} — Assistant Matanne",
                s_footer,
            )
        )

        doc.build(elements)
        buffer.seek(0)
        return buffer

    except Exception as e:
        logger.error(f"Erreur génération PDF planning: {e}")
        return None
