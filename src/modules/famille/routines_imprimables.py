"""
Routines Imprimables – Génération de fiches PDF pour routines familiales.

Utilise ReportLab pour la génération PDF.
Routines: matin, soir, ménage, courses.
"""

from __future__ import annotations

import io
import logging
from datetime import date

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)
_keys = KeyNamespace("routines_imprimables")


# ═══════════════════════════════════════════════════════════
# TEMPLATES DE ROUTINES
# ═══════════════════════════════════════════════════════════

ROUTINES_TEMPLATES = {
    "matin": {
        "titre": "☀️ Routine du Matin",
        "etapes": [
            "Se lever à l'heure prévue",
            "Changer / habiller Jules",
            "Petit-déjeuner famille",
            "Brossage de dents (tout le monde)",
            "Préparation du sac de Jules",
            "Vérifier la météo",
            "Départ à l'heure",
        ],
    },
    "soir": {
        "titre": "🌙 Routine du Soir",
        "etapes": [
            "Bain de Jules (18h30)",
            "Préparation du dîner",
            "Dîner en famille",
            "Brossage de dents Jules",
            "Histoire / câlin",
            "Coucher Jules (20h)",
            "Temps couple / détente",
            "Préparer les affaires du lendemain",
        ],
    },
    "menage": {
        "titre": "🧹 Routine Ménage Hebdo",
        "etapes": [
            "Lundi: Aspirateur salon + cuisine",
            "Mardi: Salle de bain + toilettes",
            "Mercredi: Poussière + rangement chambre Jules",
            "Jeudi: Lessive + repassage",
            "Vendredi: Courses + rangement cuisine",
            "Samedi: Jardin / extérieur",
            "Dimanche: Meals prep semaine",
        ],
    },
    "courses": {
        "titre": "🛒 Routine Courses",
        "etapes": [
            "Vérifier le réfrigérateur et les placards",
            "Consulter le planning repas de la semaine",
            "Compléter la liste de courses",
            "Vérifier les promotions en cours",
            "Préparer les sacs réutilisables",
            "Courses (priorité frais en dernier)",
            "Rangement et stockage",
        ],
    },
}


# ═══════════════════════════════════════════════════════════
# GÉNÉRATION PDF
# ═══════════════════════════════════════════════════════════


def _generer_pdf(routine_key: str, etapes_custom: list[str] | None = None) -> bytes | None:
    """Génère un PDF pour une routine donnée."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError:
        logger.warning("ReportLab non installé")
        return None

    template = ROUTINES_TEMPLATES.get(routine_key, {})
    titre = template.get("titre", "Routine")
    etapes = etapes_custom or template.get("etapes", [])

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)

    styles = getSampleStyleSheet()
    titre_style = ParagraphStyle(
        "TitreRoutine",
        parent=styles["Title"],
        fontSize=24,
        spaceAfter=20,
    )
    etape_style = ParagraphStyle(  # noqa: F841
        "Etape",
        parent=styles["Normal"],
        fontSize=14,
        spaceAfter=8,
        leftIndent=20,
    )

    elements = []

    # Titre
    elements.append(Paragraph(titre, titre_style))
    elements.append(Spacer(1, 10))
    elements.append(
        Paragraph(
            f"Famille Matanne — {date.today().strftime('%d/%m/%Y')}",
            styles["Normal"],
        )
    )
    elements.append(Spacer(1, 20))

    # Tableau avec cases à cocher
    data = [["", "Étape", "✓"]]
    for i, etape in enumerate(etapes, 1):
        data.append([str(i), etape, "☐"])

    table = Table(data, colWidths=[1.5 * cm, 13 * cm, 1.5 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a90d9")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (-1, 0), (-1, -1), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("FONTSIZE", (0, 1), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
                ("TOPPADDING", (0, 1), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Notes:", styles["Heading3"]))
    elements.append(Spacer(1, 10))
    for _ in range(5):
        elements.append(Paragraph("_" * 80, styles["Normal"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    return buffer.getvalue()


# ═══════════════════════════════════════════════════════════
# INTERFACE
# ═══════════════════════════════════════════════════════════


def _afficher_routine(key: str, template: dict):
    """Affiche une routine avec prévisualisation et bouton PDF."""
    etapes = template.get("etapes", [])

    with st.container(border=True):
        st.markdown(f"### {template.get('titre', '?')}")

        for i, etape in enumerate(etapes, 1):
            st.write(f"☐ **{i}.** {etape}")

        with st.expander("✏️ Personnaliser"):
            etapes_custom = st.text_area(
                "Étapes (une par ligne)",
                value="\n".join(etapes),
                height=200,
                key=_keys(f"custom_{key}"),
            )

        col1, col2 = st.columns([3, 1])
        with col2:
            etapes_finales = (
                etapes_custom.split("\n") if etapes_custom != "\n".join(etapes) else None
            )

            pdf_data = _generer_pdf(key, etapes_finales)
            if pdf_data:
                st.download_button(
                    "📥 PDF",
                    data=pdf_data,
                    file_name=f"routine_{key}_{date.today().isoformat()}.pdf",
                    mime="application/pdf",
                    key=_keys(f"dl_{key}"),
                    use_container_width=True,
                )
            else:
                st.warning("ReportLab requis")


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


@profiler_rerun("routines_imprimables")
def app():
    """Point d'entrée Routines Imprimables."""
    st.title("📋 Routines Imprimables")
    st.caption("Fiches PDF personnalisables pour vos routines familiales")

    with error_boundary(titre="Erreur routines imprimables"):
        try:
            import reportlab  # noqa: F401

            reportlab_ok = True
        except ImportError:
            reportlab_ok = False
            st.warning(
                "⚠️ La bibliothèque `reportlab` n'est pas installée. "
                "Installez-la avec `pip install reportlab` pour générer des PDF."
            )

        st.markdown("---")

        routine_choisie = st.selectbox(
            "Choisir une routine",
            options=list(ROUTINES_TEMPLATES.keys()),
            format_func=lambda k: ROUTINES_TEMPLATES[k]["titre"],
            key=_keys("routine_select"),
        )

        if routine_choisie:
            _afficher_routine(routine_choisie, ROUTINES_TEMPLATES[routine_choisie])

        st.markdown("---")
        if reportlab_ok:
            if st.button(
                "📥 Télécharger toutes les routines (PDF)",
                key=_keys("dl_all"),
                use_container_width=True,
            ):
                for key, template in ROUTINES_TEMPLATES.items():
                    pdf = _generer_pdf(key)
                    if pdf:
                        st.download_button(
                            f"📥 {template['titre']}",
                            data=pdf,
                            file_name=f"routine_{key}_{date.today().isoformat()}.pdf",
                            mime="application/pdf",
                            key=_keys(f"dl_all_{key}"),
                        )
