"""Fonctions utilitaires partagées pour le bot Telegram."""

from __future__ import annotations

import html
import re
import unicodedata
from datetime import date


def _normaliser_texte(texte: str) -> str:
    valeur = " ".join((texte or "").lower().strip().split())
    return unicodedata.normalize("NFKD", valeur).encode("ascii", "ignore").decode("ascii")


def _extraire_article_depuis_commande(texte: str) -> str:
    """Extrait l'article cible depuis "ajoute ... a la liste".

    Fallback: texte apres le premier mot de commande.
    """
    nettoye = (texte or "").strip()
    motif = re.compile(r"^(?:ajoute|ajouter)\s+(.+?)\s+(?:a|à)\s+la\s+liste\s*$", re.IGNORECASE)
    match = motif.match(nettoye)
    if match:
        return match.group(1).strip()

    morceaux = nettoye.split(" ", 1)
    if len(morceaux) == 2:
        return morceaux[1].strip()
    return ""


def _extraire_commande_telegram(texte: str) -> str:
    """Extrait la commande Telegram en gérant le suffixe éventuel @botname."""
    premier_mot = (texte or "").strip().split(maxsplit=1)
    if not premier_mot:
        return ""

    commande = _normaliser_texte(premier_mot[0])
    if commande.startswith("/") and "@" in commande:
        return commande.split("@", 1)[0]
    return commande


def _extraire_id_depuis_callback(callback_data: str, prefix: str) -> int | None:
    """Extrait l'ID depuis le callback_data (format: 'prefix:ID').

    Args:
        callback_data: Données du callback (ex: 'planning_valider:123')
        prefix: Préfixe attendu (ex: 'planning_valider')

    Returns:
        ID extrait ou None si format invalide
    """
    if not callback_data.startswith(f"{prefix}:"):
        return None
    try:
        return int(callback_data.split(":", 1)[1])
    except (ValueError, IndexError):
        return None


def _obtenir_url_app(chemin: str) -> str:
    chemin_normalise = chemin if chemin.startswith("/") else f"/{chemin}"
    return f"https://matanne.vercel.app/app{chemin_normalise}"


def _extraire_mois_depuis_texte(texte: str | None) -> set[int]:
    valeurs: set[int] = set()
    for brute in re.findall(r"\d{1,2}", texte or ""):
        valeur = int(brute)
        if 1 <= valeur <= 12:
            valeurs.add(valeur)
    return valeurs


def _emoji_peremption(date_peremption: date | None) -> str:
    if date_peremption is None:
        return "⚪"
    delta = (date_peremption - date.today()).days
    if delta <= 1:
        return "🔴"
    if delta <= 3:
        return "🟡"
    return "🟢"


def _resume_statut_article(article) -> tuple[str, str]:
    note_normalisee = _normaliser_texte(getattr(article, "notes", "") or "")
    if getattr(article, "achete", False):
        return "✅", "acheté"
    if "pas trouve" in note_normalisee or "introuvable" in note_normalisee:
        return "❌", "pas trouvé"
    if "report" in note_normalisee or "plus tard" in note_normalisee:
        return "🔄", "reporté"
    return "⬜", "à acheter"


def _construire_message_aide() -> str:
    from ._schemas import COMMANDES_TELEGRAM

    lignes = ["🤖 <b>Commandes Telegram disponibles</b>"]
    for commande, description in COMMANDES_TELEGRAM:
        lignes.append(f"• <code>{html.escape(commande)}</code> — {html.escape(description)}")
    lignes.append("")
    lignes.append(
        "Réponse rapide: envoyez <b>OK</b> après un planning ou une liste pour valider l'action proposée."
    )
    return "\n".join(lignes)


def _boutons_planning(planning_id: int) -> list[dict[str, str]]:
    return [
        {"id": f"planning_valider:{planning_id}", "title": "✅ Valider"},
        {"id": f"planning_modifier:{planning_id}", "title": "✏️ Modifier"},
        {"id": f"planning_regenerer:{planning_id}", "title": "🔄 Régénérer"},
        {"id": "menu_retour", "title": "🏠 Menu principal"},
    ]


def _formater_planning_html(repas_tries) -> str:
    """Formate une liste de repas en HTML structuré groupé par jour.

    Produit des blocs par jour avec titre en gras, un repas par ligne avec emoji.
    Compatible avec parse_mode HTML Telegram.
    """
    from collections import defaultdict

    JOURS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    TYPES_REPAS: dict[str, tuple[str, str]] = {
        "petit_dejeuner": ("🌅", "Petit-déjeuner"),
        "dejeuner": ("☀️", "Déjeuner"),
        "gouter": ("🍎", "Goûter"),
        "collation": ("🍎", "Goûter"),
        "diner": ("🌙", "Dîner"),
    }
    ORDRE_REPAS = {"petit_dejeuner": 0, "dejeuner": 1, "gouter": 2, "collation": 2, "diner": 3}

    par_jour: dict = defaultdict(list)
    for repas in repas_tries:
        par_jour[repas.date_repas].append(repas)

    blocs: list[str] = []
    for jour_date in sorted(par_jour):
        nom_jour = JOURS_FR[jour_date.weekday()]
        lignes_jour = [f"<b>{nom_jour} {jour_date.strftime('%d/%m')} :</b>"]
        for repas in sorted(par_jour[jour_date], key=lambda r: ORDRE_REPAS.get(r.type_repas, 99)):
            emoji, libelle = TYPES_REPAS.get(
                repas.type_repas, ("🍽️", repas.type_repas.capitalize())
            )
            nom_recette = (
                getattr(getattr(repas, "recette", None), "nom", None)
                or getattr(repas, "notes", None)
                or "—"
            )
            # Reste réchauffé
            if getattr(repas, "est_reste", False) and getattr(repas, "reste_description", None):
                nom_recette = f"♻ {nom_recette} <i>({html.escape(str(repas.reste_description))})</i>"
                lignes_jour.append(f"{emoji} {libelle} : {nom_recette}")
            else:
                lignes_jour.append(f"{emoji} {libelle} : {html.escape(str(nom_recette))}")

            # Détails supplémentaires selon le type
            type_repas = getattr(repas, "type_repas", "")
            if type_repas in ("dejeuner", "diner"):
                entree = getattr(repas, "entree", None)
                legumes = getattr(repas, "legumes", None)
                feculents = getattr(repas, "feculents", None)
                dessert = getattr(repas, "dessert", None)
                laitage = getattr(repas, "laitage", None)
                if entree:
                    lignes_jour.append(f"  🥗 Entrée : {html.escape(str(entree))}")
                if legumes:
                    lignes_jour.append(f"  🥦 Légumes : {html.escape(str(legumes))}")
                if feculents:
                    lignes_jour.append(f"  🌾 Féculents : {html.escape(str(feculents))}")
                if dessert:
                    lignes_jour.append(f"  🍮 Dessert : {html.escape(str(dessert))}")
                if laitage:
                    lignes_jour.append(f"  🥛 Laitage : {html.escape(str(laitage))}")
            elif type_repas == "gouter":
                gateau = getattr(repas, "gateau_gouter", None)
                laitage = getattr(repas, "laitage", None)
                fruit = getattr(repas, "fruit_gouter", None)
                nom_principal = getattr(getattr(repas, "recette", None), "nom", None) or getattr(repas, "notes", None) or ""
                if gateau and gateau.lower() != nom_principal.lower():
                    lignes_jour.append(f"  🍪 Gâteau : {html.escape(str(gateau))}")
                if laitage:
                    lignes_jour.append(f"  🥛 Laitage : {html.escape(str(laitage))}")
                if fruit:
                    lignes_jour.append(f"  🍎 Fruit : {html.escape(str(fruit))}")
        blocs.append("\n".join(lignes_jour))

    return "\n\n".join(blocs) if blocs else "Aucun repas saisi."


def _selectionner_liste_courses(session, liste_id: int | None = None):
    from src.core.models.courses import ListeCourses

    if liste_id is not None:
        return session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()

    liste = (
        session.query(ListeCourses)
        .filter(ListeCourses.archivee.is_(False), ListeCourses.etat == "active")
        .order_by(ListeCourses.cree_le.desc())
        .first()
    )
    if liste:
        return liste

    return (
        session.query(ListeCourses)
        .filter(ListeCourses.archivee.is_(False))
        .order_by(ListeCourses.cree_le.desc())
        .first()
    )
