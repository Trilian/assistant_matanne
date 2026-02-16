"""
Fonctions d'export pour le Calendrier Familial Unifié.

Export vers:
- Texte formaté (pour impression frigo)
- HTML (pour impression navigateur)
"""

from .types import SemaineCalendrier, TypeEvenement


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
]
