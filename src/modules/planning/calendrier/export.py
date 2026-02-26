"""
Fonctions d'export pour le Calendrier Familial Unifié.

Export vers:
- Texte formaté (pour impression frigo)
- HTML (pour impression navigateur)
- PDF (via reportlab, téléchargeable)
"""

import io
import logging
from datetime import date

from .types import SemaineCalendrier, TypeEvenement

logger = logging.getLogger(__name__)


def generer_texte_semaine_pour_impression(semaine: SemaineCalendrier) -> str:
    """
    Genère un texte formate de la semaine pour impression.

    Returns:
        Texte formate pour être colle sur le frigo
    """
    lignes = []
    lignes.append(f"═══ SEMAINE DU {semaine.titre} ═══")
    lignes.append("")

    for jour in semaine.jours:
        lignes.append(f"▶ {jour.jour_semaine.upper()} {jour.date_jour.strftime('%d/%m')}")
        lignes.append("-" * 30)

        if jour.repas_midi:
            lignes.append(f"  🌞 Midi: {jour.repas_midi.titre}")
            if jour.repas_midi.version_jules:
                lignes.append(f"     👶 Jules: {jour.repas_midi.version_jules[:50]}...")

        if jour.repas_soir:
            lignes.append(f"  🌙 Soir: {jour.repas_soir.titre}")
            if jour.repas_soir.version_jules:
                lignes.append(f"     👶 Jules: {jour.repas_soir.version_jules[:50]}...")

        if jour.gouter:
            lignes.append(f"  🍰 Goûter: {jour.gouter.titre}")

        if jour.batch_cooking:
            lignes.append(f"  🍳 BATCH COOKING {jour.batch_cooking.heure_str}")

        for courses in jour.courses:
            lignes.append(f"  🛒 Courses: {courses.magasin} {courses.heure_str}")

        for activite in jour.activites:
            lignes.append(f"  🎨 {activite.titre} {activite.heure_str}")

        for rdv in jour.rdv:
            emoji = "🏥" if rdv.type == TypeEvenement.RDV_MEDICAL else "📅"
            lignes.append(f"  {emoji} {rdv.titre} {rdv.heure_str}")

        # Jours spéciaux
        for js in jour.jours_speciaux:
            lignes.append(f"  {js.emoji} {js.titre}")

        if jour.est_vide:
            lignes.append("  (rien de planifie)")

        lignes.append("")

    lignes.append("═" * 35)
    lignes.append(
        f"📊 {semaine.nb_repas_planifies} repas | {semaine.nb_sessions_batch} batch | {semaine.nb_courses} courses"
    )

    return "\n".join(lignes)


def generer_html_semaine_pour_impression(semaine: SemaineCalendrier) -> str:
    """
    Genère un HTML formate de la semaine pour impression.

    Returns:
        HTML prêt à imprimer
    """
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 12px; }}
            h1 {{ text-align: center; font-size: 16px; margin-bottom: 10px; }}
            .jour {{ margin-bottom: 15px; page-break-inside: avoid; }}
            .jour-titre {{ font-weight: bold; background: #f0f0f0; padding: 5px; }}
            .repas {{ margin-left: 20px; }}
            .event {{ margin-left: 20px; color: #555; }}
            .jules {{ color: #e91e63; font-size: 10px; }}
        </style>
    </head>
    <body>
        <h1>📅 SEMAINE DU {semaine.titre}</h1>
    """

    for jour in semaine.jours:
        html += f"""
        <div class="jour">
            <div class="jour-titre">{jour.jour_semaine} {jour.date_jour.strftime("%d/%m")}</div>
        """

        if jour.repas_midi:
            html += f'<div class="repas">🌞 Midi: <b>{jour.repas_midi.titre}</b></div>'
            if jour.repas_midi.version_jules:
                html += f'<div class="jules">👶 {jour.repas_midi.version_jules[:60]}...</div>'

        if jour.repas_soir:
            html += f'<div class="repas">🌙 Soir: <b>{jour.repas_soir.titre}</b></div>'
            if jour.repas_soir.version_jules:
                html += f'<div class="jules">👶 {jour.repas_soir.version_jules[:60]}...</div>'

        if jour.batch_cooking:
            html += f'<div class="event">🍳 Batch Cooking {jour.batch_cooking.heure_str}</div>'

        for courses in jour.courses:
            html += f'<div class="event">🛒 {courses.magasin} {courses.heure_str}</div>'

        for rdv in jour.rdv:
            html += f'<div class="event">🏥 {rdv.titre} {rdv.heure_str}</div>'

        html += "</div>"

    html += """
    </body>
    </html>
    """

    return html


__all__ = [
    "generer_texte_semaine_pour_impression",
    "generer_html_semaine_pour_impression",
    "generer_pdf_semaine",
]


# ═══════════════════════════════════════════════════════════
# EXPORT PDF (via reportlab)
# ═══════════════════════════════════════════════════════════


def generer_pdf_semaine(semaine: SemaineCalendrier) -> bytes | None:
    """Génère un PDF formaté de la semaine pour téléchargement.

    Utilise reportlab pour créer un PDF avec:
    - Titre et période
    - Un bloc par jour avec repas, activités, RDV, jours spéciaux
    - Statistiques en bas

    Returns:
        Contenu PDF en bytes, ou None si erreur.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm, mm
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError:
        logger.warning("reportlab non installé — PDF impossible")
        return None

    buffer = io.BytesIO()

    # Créer le document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    # Styles
    styles = getSampleStyleSheet()
    titre_style = ParagraphStyle(
        "TitreSemaine",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=6 * mm,
        alignment=1,  # centré
    )
    jour_style = ParagraphStyle(
        "TitreJour",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=4 * mm,
        spaceAfter=2 * mm,
        textColor=colors.HexColor("#1565C0"),
    )
    item_style = ParagraphStyle(
        "ItemEvent",
        parent=styles["Normal"],
        fontSize=9,
        leftIndent=10 * mm,
        spaceBefore=1 * mm,
    )
    special_style = ParagraphStyle(
        "JourSpecial",
        parent=styles["Normal"],
        fontSize=9,
        leftIndent=10 * mm,
        spaceBefore=1 * mm,
        textColor=colors.HexColor("#D32F2F"),
    )
    stats_style = ParagraphStyle(
        "Stats",
        parent=styles["Normal"],
        fontSize=10,
        alignment=1,
        spaceBefore=6 * mm,
        textColor=colors.HexColor("#757575"),
    )

    elements = []

    # Titre
    elements.append(Paragraph(f"Calendrier Familial — Semaine du {semaine.titre}", titre_style))

    # Chaque jour
    for jour in semaine.jours:
        marqueur = " (aujourd'hui)" if jour.est_aujourdhui else ""
        elements.append(
            Paragraph(
                f"{jour.jour_semaine} {jour.date_jour.strftime('%d/%m')}{marqueur}",
                jour_style,
            )
        )

        # Jours spéciaux en premier
        for js in jour.jours_speciaux:
            emoji_txt = {"ferie": "[FERIE]", "creche": "[CRECHE FERMEE]", "pont": "[PONT]"}.get(
                js.type.value if hasattr(js.type, "value") else str(js.type), ""
            )
            elements.append(Paragraph(f"{emoji_txt} {js.titre}", special_style))

        # Repas
        if jour.repas_midi:
            elements.append(Paragraph(f"Midi: {jour.repas_midi.titre}", item_style))
        if jour.repas_soir:
            elements.append(Paragraph(f"Soir: {jour.repas_soir.titre}", item_style))
        if jour.gouter:
            elements.append(Paragraph(f"Gouter: {jour.gouter.titre}", item_style))

        # Batch
        if jour.batch_cooking:
            elements.append(Paragraph(f"BATCH COOKING {jour.batch_cooking.heure_str}", item_style))

        # Courses
        for c in jour.courses:
            elements.append(Paragraph(f"Courses: {c.magasin} {c.heure_str}", item_style))

        # Activités
        for act in jour.activites:
            jules = " (Jules)" if act.pour_jules else ""
            elements.append(Paragraph(f"Activite: {act.titre} {act.heure_str}{jules}", item_style))

        # RDV
        for rdv in jour.rdv:
            lieu = f" @ {rdv.lieu}" if rdv.lieu else ""
            elements.append(Paragraph(f"RDV: {rdv.titre} {rdv.heure_str}{lieu}", item_style))

        # Tâches ménage
        for tache in jour.taches_menage:
            elements.append(Paragraph(f"Menage: {tache.titre}", item_style))

        if jour.est_vide and not jour.jours_speciaux:
            elements.append(Paragraph("(rien de planifie)", item_style))

        elements.append(Spacer(1, 2 * mm))

    # Statistiques
    stats = semaine.stats
    elements.append(
        Paragraph(
            f"{stats.get('repas', 0)} repas | "
            f"{semaine.nb_sessions_batch} batch | "
            f"{stats.get('activites', 0)} activites | "
            f"Charge moyenne: {stats.get('charge_moyenne', 0)}%",
            stats_style,
        )
    )

    # Générer
    try:
        doc.build(elements)
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"Erreur génération PDF: {e}")
        return None
