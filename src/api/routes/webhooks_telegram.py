"""Webhook Telegram pour les commandes en langage naturel.

Endpoints:
- POST /api/v1/telegram/webhook : reception des updates Telegram

Commandes bot Telegram :
- "Qu'est-ce qu'on mange ce soir ?"
- "Ajoute lait a la liste"
- "Activite samedi ?"
"""

from __future__ import annotations

import asyncio
import html
import logging
import re
import unicodedata
from datetime import date, datetime, timedelta

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from src.api.schemas import MessageResponse
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/telegram", tags=["Telegram"])


COMMANDES_TELEGRAM: tuple[tuple[str, str], ...] = (
    ("/planning", "Afficher le planning repas de la semaine"),
    ("/courses", "Afficher la liste de courses avec actions rapides"),
    ("/courses_live", "Ouvrir la liste interactive avec boutons inline"),
    ("/inventaire", "Voir le frigo avec alertes de péremption"),
    ("/recette [nom]", "Trouver une recette rapide et ses ingrédients"),
    ("/batch", "Résumé du batch cooking en cours ou planifié"),
    ("/ajout [article]", "Ajouter un article à la liste de courses"),
    ("/ajouter_course [article]", "Ajouter un article à la liste active"),
    ("/repas [midi|soir]", "Voir le repas du jour et répondre au mini-sondage"),
    ("/jules", "Résumé Jules: âge et jalons du moment"),
    ("/maison", "Tâches maison du jour"),
    ("/jardin", "Tâches jardin et récoltes à venir"),
    ("/weekend", "Suggestions et activités du prochain weekend"),
    ("/energie", "KPIs énergie du mois / de l’année"),
    ("/rappels", "Voir tous les rappels groupés"),
    ("/timer [Xmin]", "Lancer un minuteur Telegram"),
    ("/note [texte]", "Créer une note rapide"),
    ("/budget", "Résumé budget du mois en cours"),
    ("/rapport", "Résumé hebdomadaire de la famille"),
    ("/photo", "Recevoir l’aide pour analyser une photo du frigo ou de la maison"),
    ("/meteo", "Météo du jour et impact sur les activités"),
    ("/menu", "Ouvrir le menu principal Telegram"),
    ("/aide", "Lister toutes les commandes disponibles"),
)


class EnvoyerPlanningTelegramRequest(BaseModel):
    """Payload pour l'envoi manuel d'un planning via Telegram."""

    planning_id: int
    contenu: str | None = None


class EnvoyerCoursesTelegramRequest(BaseModel):
    """Payload pour l'envoi manuel d'une liste de courses via Telegram."""

    liste_id: int
    nom_liste: str | None = None


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


def _construire_message_aide() -> str:
    lignes = ["🤖 <b>Commandes Telegram disponibles</b>"]
    for commande, description in COMMANDES_TELEGRAM:
        lignes.append(f"• <code>{html.escape(commande)}</code> — {html.escape(description)}")
    lignes.append("")
    lignes.append("Réponse rapide: envoyez <b>OK</b> après un planning ou une liste pour valider l'action proposée.")
    return "\n".join(lignes)


def _boutons_planning(planning_id: int) -> list[dict[str, str]]:
    return [
        {"id": f"planning_valider:{planning_id}", "title": "✅ Valider"},
        {"id": f"planning_modifier:{planning_id}", "title": "✏️ Modifier"},
        {"id": f"planning_regenerer:{planning_id}", "title": "🔄 Régénérer"},
        {"id": "menu_retour", "title": "🏠 Menu principal"},
    ]


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


async def _envoyer_aide_telegram(chat_id: str) -> None:
    from src.services.integrations.telegram import envoyer_message_interactif

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps=_construire_message_aide(),
        boutons=[
            {"id": "menu_principal", "title": "🏠 Menu principal"},
            {"id": "action_planning", "title": "🍽️ Planning"},
            {"id": "action_courses", "title": "🛒 Courses"},
        ],
    )


async def _envoyer_menu_principal(chat_id: str) -> None:
    from src.services.integrations.telegram import envoyer_message_interactif

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps=(
            "📲 <b>Menu principal MaTanne</b>\n\n"
            "Choisissez un module pour ouvrir les actions rapides Telegram."
        ),
        boutons=[
            {"id": "menu_cuisine", "title": "🍽️ Cuisine"},
            {"id": "menu_famille", "title": "👶 Famille"},
            {"id": "menu_maison", "title": "🏠 Maison"},
            {"id": "menu_outils", "title": "🧰 Outils"},
            {"id": "menu_aide", "title": "❓ Aide"},
        ],
    )


async def _envoyer_menu_module(chat_id: str, module_id: str) -> None:
    from src.services.integrations.telegram import envoyer_message_interactif

    configuration = {
        "cuisine": {
            "titre": "🍽️ <b>Cuisine</b>",
            "boutons": [
                {"id": "action_planning", "title": "📅 Planning semaine"},
                {"id": "action_courses", "title": "🛒 Liste de courses"},
                {"id": "action_inventaire", "title": "🥫 Inventaire"},
                {"id": "action_batch", "title": "🍱 Batch cooking"},
                {"id": "action_repas_midi", "title": "☀️ Repas midi"},
                {"id": "action_repas_soir", "title": "🌙 Repas ce soir"},
            ],
        },
        "famille": {
            "titre": "👶 <b>Famille</b>",
            "boutons": [
                {"id": "action_jules", "title": "👶 Résumé Jules"},
                {"id": "action_budget", "title": "💰 Budget"},
                {"id": "action_meteo", "title": "🌦️ Météo & activités"},
            ],
        },
        "maison": {
            "titre": "🏠 <b>Maison</b>",
            "boutons": [
                {"id": "action_maison", "title": "🧹 Tâches du jour"},
                {"id": "action_jardin", "title": "🌿 Jardin"},
                {"id": "action_energie", "title": "⚡ Énergie"},
                {"id": "action_rappels", "title": "⏰ Rappels"},
                {"id": "action_budget", "title": "💰 Budget maison/famille"},
            ],
        },
        "outils": {
            "titre": "🧰 <b>Outils</b>",
            "boutons": [
                {"id": "action_meteo", "title": "🌦️ Météo"},
                {"id": "action_timer_10", "title": "⏱️ Timer 10 min"},
                {"id": "action_note_modele", "title": "📝 Note rapide"},
                {"id": "menu_aide", "title": "❓ Aide"},
            ],
        },
    }

    module = configuration.get(module_id)
    if not module:
        await _envoyer_menu_principal(chat_id)
        return

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps=f"{module['titre']}\n\nActions rapides disponibles:",
        boutons=[*module["boutons"], {"id": "menu_retour", "title": "🏠 Menu principal"}],
    )


async def _envoyer_planning_commande(chat_id: str) -> None:
    from src.core.db import obtenir_contexte_db
    from src.core.models.planning import Planning
    from src.services.integrations.telegram import envoyer_message_interactif, sauvegarder_etat_conversation

    aujourd_hui = date.today()
    lundi = aujourd_hui - timedelta(days=aujourd_hui.weekday())

    with obtenir_contexte_db() as session:
        planning = (
            session.query(Planning)
            .filter(Planning.semaine_debut == lundi, Planning.etat != "archive")
            .order_by(Planning.id.desc())
            .first()
        )
        if planning is None:
            planning = (
                session.query(Planning)
                .filter(Planning.etat != "archive")
                .order_by(Planning.semaine_debut.desc(), Planning.id.desc())
                .first()
            )

        if planning is None:
            await envoyer_message_interactif(
                destinataire=chat_id,
                corps="🍽️ Aucun planning trouvé pour le moment.",
                boutons=[{"id": "menu_retour", "title": "🏠 Menu principal"}],
            )
            return

        repas_tries = sorted(planning.repas, key=lambda item: (item.date_repas, item.type_repas))
        lignes = []
        for repas in repas_tries:
            type_repas = "Midi" if repas.type_repas == "dejeuner" else repas.type_repas.capitalize()
            nom_recette = getattr(getattr(repas, "recette", None), "nom", None) or repas.notes or "Repas à préciser"
            lignes.append(
                f"• {repas.date_repas.strftime('%a %d/%m')} {html.escape(type_repas)} : {html.escape(str(nom_recette))}"
            )

        message = (
            f"🍽️ <b>Planning de la semaine</b>\n"
            f"Du {planning.semaine_debut.strftime('%d/%m')} au {planning.semaine_fin.strftime('%d/%m')}\n\n"
            + ("\n".join(lignes) if lignes else "Aucun repas saisi.")
        )

        sauvegarder_etat_conversation(
            chat_id,
            {"type": "planning_validation", "planning_id": planning.id},
        )

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps=message,
        boutons=_boutons_planning(planning.id),
    )


async def _envoyer_courses_commande(chat_id: str, liste_id: int | None = None) -> None:
    from src.core.db import obtenir_contexte_db
    from src.core.models.courses import ArticleCourses
    from src.services.integrations.telegram import envoyer_message_interactif, sauvegarder_etat_conversation

    with obtenir_contexte_db() as session:
        liste = _selectionner_liste_courses(session, liste_id=liste_id)
        if liste is None:
            await envoyer_message_interactif(
                destinataire=chat_id,
                corps="🛒 Aucune liste de courses active pour le moment.",
                boutons=[
                    {"id": "menu_retour", "title": "🏠 Menu principal"},
                    {"id": "menu_cuisine", "title": "🍽️ Cuisine"},
                ],
            )
            return

        articles = (
            session.query(ArticleCourses)
            .filter(ArticleCourses.liste_id == liste.id)
            .order_by(ArticleCourses.achete.asc(), ArticleCourses.id.asc())
            .all()
        )

        lignes = []
        boutons: list[dict[str, str]] = []
        for article in articles[:6]:
            nom_article = getattr(getattr(article, "ingredient", None), "nom", None) or f"Article #{article.id}"
            prefixe, statut = _resume_statut_article(article)
            lignes.append(f"{prefixe} {html.escape(str(nom_article))} <i>({html.escape(statut)})</i>")

            if article.achete:
                boutons.append(
                    {
                        "id": f"courses_toggle_article:{article.id}",
                        "title": f"↩️ Décocher {str(nom_article)[:20]}",
                    }
                )
            else:
                boutons.extend(
                    [
                        {
                            "id": f"courses_action:achete:{article.id}",
                            "title": f"✅ {str(nom_article)[:22]}",
                        },
                        {
                            "id": f"courses_action:manquant:{article.id}",
                            "title": f"❌ {str(nom_article)[:22]}",
                        },
                        {
                            "id": f"courses_action:reporter:{article.id}",
                            "title": f"🔄 {str(nom_article)[:22]}",
                        },
                    ]
                )

        if not lignes:
            lignes.append("La liste est vide pour le moment.")

        boutons.extend(
            [
                {"id": f"courses_confirmer:{liste.id}", "title": "✅ Confirmer la liste"},
                {"url": _obtenir_url_app("/cuisine/courses"), "title": "🛒 Ouvrir les courses"},
                {"id": "menu_retour", "title": "🏠 Menu principal"},
            ]
        )

        sauvegarder_etat_conversation(
            chat_id,
            {"type": "courses_confirmation", "liste_id": liste.id},
        )

        message = (
            f"🛒 <b>{html.escape(liste.nom)}</b>\n\n"
            + "\n".join(lignes)
            + "\n\nChoisissez une action rapide : ✅ acheté • ❌ pas trouvé • 🔄 reporter"
        )

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps=message,
        boutons=boutons,
    )


async def _envoyer_repas_moment(chat_id: str, type_repas: str | None = None) -> None:
    from src.core.db import obtenir_contexte_db
    from src.core.models.planning import Repas
    from src.services.integrations.telegram import envoyer_message_interactif, envoyer_message_telegram

    mapping = {
        "midi": "dejeuner",
        "dejeuner": "dejeuner",
        "soir": "diner",
        "diner": "diner",
    }
    type_cible = mapping.get((type_repas or "").lower())

    with obtenir_contexte_db() as session:
        requete = session.query(Repas).filter(Repas.date_repas == date.today())
        if type_cible:
            requete = requete.filter(Repas.type_repas == type_cible)
        repas_liste = requete.order_by(Repas.type_repas.asc()).all()

    if not repas_liste:
        libelle = "aujourd'hui" if not type_cible else ("ce midi" if type_cible == "dejeuner" else "ce soir")
        await envoyer_message_telegram(chat_id, f"🍽️ Aucun repas planifié {libelle}.")
        return

    lignes = []
    for repas in repas_liste:
        type_libelle = "Midi" if repas.type_repas == "dejeuner" else "Soir"
        nom = getattr(getattr(repas, "recette", None), "nom", None) or repas.notes or "Repas à préciser"
        lignes.append(f"• {type_libelle} : {html.escape(str(nom))}")

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="🍽️ <b>Repas du jour</b>\n\n" + "\n".join(lignes) + "\n\nQu'est-ce qui vous ferait plaisir ?",
        boutons=[
            {"id": "repas_sondage:midi", "title": "☀️ Plutôt simple"},
            {"id": "repas_sondage:soir", "title": "🌙 Réconfortant"},
            {"id": "repas_sondage:surprise", "title": "🎲 Surprise"},
            {"id": "action_planning", "title": "📅 Ouvrir le planning"},
            {"id": "menu_retour", "title": "🏠 Menu principal"},
        ],
    )


async def _envoyer_resume_jules(chat_id: str) -> None:
    from src.services.famille.contexte import ContexteFamilleService
    from src.services.famille.jules import obtenir_service_jules
    from src.services.integrations.telegram import envoyer_message_interactif, envoyer_message_telegram

    service = obtenir_service_jules()
    date_naissance = service.get_date_naissance_jules()
    if not date_naissance:
        await envoyer_message_telegram(chat_id, "👶 Profil Jules non configuré pour le moment.")
        return

    age_mois = service.get_age_mois()
    prochains_jalons = ContexteFamilleService()._prochains_jalons_developpement(age_mois)
    lignes = [f"👶 <b>Jules</b>", f"Âge: <b>{age_mois} mois</b>"]
    if prochains_jalons:
        lignes.append("")
        lignes.append("Prochains jalons probables:")
        lignes.extend(f"• {html.escape(str(jalon))}" for jalon in prochains_jalons[:3])

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"id": "menu_famille", "title": "👶 Menu Famille"},
            {"id": "menu_retour", "title": "🏠 Menu principal"},
        ],
    )


async def _envoyer_taches_maison(chat_id: str) -> None:
    from src.services.integrations.telegram import envoyer_message_interactif, envoyer_message_telegram
    from src.services.maison import obtenir_service_contexte_maison

    taches = obtenir_service_contexte_maison().obtenir_taches_jour()
    if not taches:
        await envoyer_message_telegram(chat_id, "🏠 Aucune tâche maison prioritaire aujourd'hui.")
        return

    lignes = []
    for tache in taches[:6]:
        categorie = getattr(tache, "categorie", None) or "maison"
        nom = getattr(tache, "nom", None) or str(tache)
        lignes.append(f"• {html.escape(str(nom))} <i>({html.escape(str(categorie))})</i>")

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="🏠 <b>Tâches maison du jour</b>\n\n" + "\n".join(lignes),
        boutons=[
            {"id": "menu_maison", "title": "🏠 Menu Maison"},
            {"id": "menu_retour", "title": "🏠 Menu principal"},
        ],
    )


async def _envoyer_resume_budget(chat_id: str) -> None:
    from sqlalchemy import extract, func

    from src.core.db import obtenir_contexte_db
    from src.core.models.famille import BudgetFamille
    from src.services.integrations.telegram import envoyer_message_interactif, envoyer_message_telegram

    aujourd_hui = date.today()
    with obtenir_contexte_db() as session:
        total = (
            session.query(func.sum(BudgetFamille.montant))
            .filter(
                extract("month", BudgetFamille.date) == aujourd_hui.month,
                extract("year", BudgetFamille.date) == aujourd_hui.year,
            )
            .scalar()
        ) or 0

        top_categories = (
            session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant).label("total"))
            .filter(
                extract("month", BudgetFamille.date) == aujourd_hui.month,
                extract("year", BudgetFamille.date) == aujourd_hui.year,
            )
            .group_by(BudgetFamille.categorie)
            .order_by(func.sum(BudgetFamille.montant).desc())
            .limit(3)
            .all()
        )

    if not total:
        await envoyer_message_telegram(chat_id, "💰 Aucune dépense enregistrée ce mois-ci.")
        return

    lignes = [f"💰 <b>Budget du mois</b>", f"Total dépensé: <b>{round(float(total), 2)}€</b>"]
    if top_categories:
        lignes.append("")
        lignes.append("Top catégories:")
        lignes.extend(
            f"• {html.escape(str(categorie))}: {round(float(montant), 2)}€"
            for categorie, montant in top_categories
        )

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"id": "menu_famille", "title": "👶 Menu Famille"},
            {"id": "menu_retour", "title": "🏠 Menu principal"},
        ],
    )


async def _envoyer_meteo_telegram(chat_id: str) -> None:
    from src.services.famille.bridges_meteo_activites import obtenir_service_meteo_activites_interaction
    from src.services.integrations.telegram import envoyer_message_interactif
    from src.services.utilitaires.meteo_service import obtenir_meteo_service

    meteo = obtenir_meteo_service().obtenir_meteo()
    actuelle = getattr(meteo, "actuelle", None)
    suggestions = obtenir_service_meteo_activites_interaction().suggerer_activites_selon_meteo(
        jours_horizon=1
    )

    lignes = [f"🌦️ <b>Météo du jour</b> — {html.escape(str(getattr(meteo, 'ville', 'Maison')))}"]
    if actuelle:
        lignes.append(
            f"{getattr(actuelle, 'emoji', '🌤️')} {html.escape(str(getattr(actuelle, 'condition', 'variable')))} — {getattr(actuelle, 'temperature', '?')}°C"
        )

    idee = None
    suggestions_liste = (suggestions or {}).get("suggestions") or []
    if suggestions_liste:
        idee = suggestions_liste[0].get("idee")
    elif getattr(meteo, "suggestions", None):
        idee = meteo.suggestions[0]

    if idee:
        lignes.append("")
        lignes.append(f"💡 {html.escape(str(idee))}")

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"id": "menu_famille", "title": "👶 Menu Famille"},
            {"id": "menu_retour", "title": "🏠 Menu principal"},
        ],
    )


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


async def _envoyer_inventaire_commande(chat_id: str) -> None:
    from src.core.db import obtenir_contexte_db
    from src.core.models.inventaire import ArticleInventaire
    from src.services.integrations.telegram import envoyer_message_interactif, envoyer_message_telegram

    with obtenir_contexte_db() as session:
        articles = (
            session.query(ArticleInventaire)
            .filter(ArticleInventaire.quantite > 0)
            .all()
        )

    articles_tries = sorted(
        articles,
        key=lambda article: (
            getattr(article, "date_peremption", None) is None,
            getattr(article, "date_peremption", None) or date.max,
            (getattr(article, "nom", None) or "").lower(),
        ),
    )

    if not articles_tries:
        await envoyer_message_telegram(chat_id, "🥫 Inventaire vide pour le moment.")
        return

    lignes = ["🥫 <b>Inventaire / frigo</b>"]
    for article in articles_tries[:8]:
        nom = getattr(article, "nom", None) or f"Article #{article.id}"
        quantite = f"{float(getattr(article, 'quantite', 0) or 0):g}"
        unite = getattr(article, "unite", None) or ""
        peremption = getattr(article, "date_peremption", None)
        infos = [f"{quantite} {unite}".strip()]
        if peremption:
            infos.append(f"à consommer avant le {peremption.strftime('%d/%m')}")
        if getattr(article, "emplacement", None):
            infos.append(str(article.emplacement))
        if getattr(article, "est_stock_bas", False):
            infos.append("stock bas")
        lignes.append(f"{_emoji_peremption(peremption)} {html.escape(str(nom))} — {html.escape(' • '.join(filter(None, infos)))}")

    lignes.append("")
    lignes.append("Légende : 🟢 OK • 🟡 à surveiller • 🔴 urgent")

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"id": "action_rappels", "title": "⏰ Voir les rappels"},
            {"url": _obtenir_url_app("/cuisine/inventaire"), "title": "🥫 Ouvrir l'inventaire"},
            {"id": "menu_cuisine", "title": "🍽️ Menu Cuisine"},
        ],
    )


async def _envoyer_recette_commande(chat_id: str, recherche: str | None = None) -> None:
    from src.core.db import obtenir_contexte_db
    from src.core.models.recettes import Recette
    from src.services.integrations.telegram import envoyer_message_interactif, envoyer_message_telegram

    terme = (recherche or "").strip()
    with obtenir_contexte_db() as session:
        requete = session.query(Recette)
        if terme:
            recette = (
                requete.filter(Recette.nom.ilike(f"%{terme}%"))
                .order_by(Recette.est_rapide.desc(), Recette.compatible_bebe.desc(), Recette.id.desc())
                .first()
            )
        else:
            recette = (
                requete.filter(Recette.est_rapide.is_(True))
                .order_by(Recette.compatible_bebe.desc(), Recette.id.desc())
                .first()
            ) or requete.order_by(Recette.id.desc()).first()

    if recette is None:
        await envoyer_message_telegram(chat_id, "🍽️ Aucune recette trouvée pour cette recherche.")
        return

    ingredients = []
    for item in getattr(recette, "ingredients", [])[:8]:
        nom = getattr(getattr(item, "ingredient", None), "nom", None) or "Ingrédient"
        quantite = getattr(item, "quantite", None)
        unite = getattr(item, "unite", None) or ""
        prefixe = f"{float(quantite):g} " if quantite is not None else ""
        ingredients.append(f"• {html.escape(prefixe + str(unite)).strip()} {html.escape(str(nom))}".replace("•  ", "• "))

    tags = ", ".join(recette.tags[:4]) if getattr(recette, "tags", None) else "familiale"
    lignes = [
        f"🍽️ <b>{html.escape(str(recette.nom))}</b>",
        f"⏱️ {recette.temps_total} min • 👨‍👩‍👦 {recette.portions} portions • {html.escape(tags)}",
    ]
    if getattr(recette, "description", None):
        lignes.append("")
        lignes.append(html.escape(str(recette.description))[:240])
    if ingredients:
        lignes.append("")
        lignes.append("<b>Ingrédients</b>")
        lignes.extend(ingredients)

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"id": "action_planning", "title": "📅 Voir le planning"},
            {"url": _obtenir_url_app("/cuisine/recettes"), "title": "📖 Ouvrir les recettes"},
            {"id": "menu_cuisine", "title": "🍽️ Menu Cuisine"},
        ],
    )


async def _envoyer_resume_batch_cooking(chat_id: str) -> None:
    from src.services.cuisine.batch_cooking import obtenir_service_batch_cooking
    from src.services.integrations.telegram import envoyer_message_interactif, envoyer_message_telegram

    service = obtenir_service_batch_cooking()
    session_active = service.get_session_active()
    prochaine = None
    if session_active is None:
        sessions = service.obtenir_sessions_planifiees(
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=14),
        )
        prochaine = sessions[0] if sessions else None

    cible = session_active or prochaine
    if cible is None:
        await envoyer_message_telegram(chat_id, "🍱 Aucun batch cooking en cours ou planifié pour le moment.")
        return

    etat = getattr(cible, "statut", "planifiee")
    date_session = getattr(cible, "date_session", None)
    heure = getattr(cible, "heure_debut", None)
    nb_recettes = len(getattr(cible, "recettes_selectionnees", []) or [])
    nb_etapes = len(getattr(cible, "etapes", []) or [])

    lignes = ["🍱 <b>Batch cooking</b>"]
    lignes.append(f"Session : <b>{html.escape(str(getattr(cible, 'nom', 'Batch')))}</b>")
    if date_session:
        lignes.append(f"📅 {date_session.strftime('%d/%m/%Y')}")
    if heure:
        lignes.append(f"🕒 Début prévu : {heure.strftime('%H:%M')}")
    lignes.append(f"Statut : <b>{html.escape(str(etat))}</b>")
    lignes.append(f"Recettes : {nb_recettes} • Étapes : {nb_etapes}")

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"url": _obtenir_url_app("/cuisine/batch-cooking"), "title": "🍱 Ouvrir batch cooking"},
            {"id": "menu_cuisine", "title": "🍽️ Menu Cuisine"},
        ],
    )


async def _envoyer_resume_jardin(chat_id: str) -> None:
    from src.core.db import obtenir_contexte_db
    from src.core.models.habitat import TacheEntretien
    from src.core.models.temps_entretien import PlanteJardin
    from src.services.integrations.telegram import envoyer_message_interactif, envoyer_message_telegram

    mois_courant = date.today().month
    mois_prochain = 1 if mois_courant == 12 else mois_courant + 1

    with obtenir_contexte_db() as session:
        taches = (
            session.query(TacheEntretien)
            .filter(TacheEntretien.categorie == "jardin", TacheEntretien.fait.is_(False))
            .order_by(TacheEntretien.prochaine_fois.asc(), TacheEntretien.id.asc())
            .limit(5)
            .all()
        )
        plantes = session.query(PlanteJardin).order_by(PlanteJardin.nom.asc()).limit(12).all()

    recoltes = [
        plante
        for plante in plantes
        if {mois_courant, mois_prochain} & _extraire_mois_depuis_texte(getattr(plante, "mois_recolte", None))
    ]

    if not taches and not recoltes:
        await envoyer_message_telegram(chat_id, "🌿 Aucun rappel jardin urgent pour le moment.")
        return

    lignes = ["🌿 <b>Jardin</b>"]
    if taches:
        lignes.append("")
        lignes.append("<b>Prochaines tâches</b>")
        for tache in taches[:4]:
            echeance = (
                tache.prochaine_fois.strftime('%d/%m')
                if getattr(tache, "prochaine_fois", None)
                else "à planifier"
            )
            lignes.append(f"• {html.escape(str(tache.nom))} — {echeance}")
    if recoltes:
        lignes.append("")
        lignes.append("<b>Récoltes proches</b>")
        for plante in recoltes[:4]:
            etat = getattr(plante, "etat", "bon")
            lignes.append(f"• {html.escape(str(plante.nom))} — état {html.escape(str(etat))}")

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"url": _obtenir_url_app("/maison/jardin"), "title": "🌿 Ouvrir le jardin"},
            {"id": "menu_maison", "title": "🏠 Menu Maison"},
        ],
    )


async def _envoyer_resume_energie(chat_id: str) -> None:
    from src.services.integrations.telegram import envoyer_message_interactif, envoyer_message_telegram
    from src.services.utilitaires import obtenir_energie_service

    totaux = obtenir_energie_service().totaux_annuels(date.today().year)
    if not totaux:
        await envoyer_message_telegram(chat_id, "⚡ Aucun relevé énergie disponible pour le moment.")
        return

    libelles = {
        "electricite": "⚡ Électricité",
        "gaz": "🔥 Gaz",
        "eau": "💧 Eau",
    }
    lignes = [f"⚡ <b>Énergie {date.today().year}</b>"]
    for type_energie, valeurs in sorted(totaux.items()):
        consommation = float(valeurs.get("total_consommation", 0) or 0)
        montant = float(valeurs.get("total_montant", 0) or 0)
        lignes.append(
            f"• {libelles.get(type_energie, type_energie.title())} : {consommation:g} — {montant:.2f}€"
        )

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"url": _obtenir_url_app("/maison/energie"), "title": "⚡ Ouvrir énergie"},
            {"id": "menu_maison", "title": "🏠 Menu Maison"},
        ],
    )


async def _envoyer_resume_weekend(chat_id: str) -> None:
    from src.services.famille.weekend import obtenir_service_weekend
    from src.services.famille.weekend_ai import obtenir_weekend_ai_service
    from src.services.integrations.telegram import envoyer_message_interactif

    service = obtenir_service_weekend()
    samedi, dimanche = service.get_next_weekend()
    activites = service.lister_activites_weekend(samedi, dimanche) or {}
    budget = service.get_budget_weekend(samedi, dimanche) or {"estime": 0, "reel": 0}

    samedi_activites = activites.get("saturday", []) or []
    dimanche_activites = activites.get("sunday", []) or []

    lignes = [f"🎡 <b>Weekend {samedi.strftime('%d/%m')} → {dimanche.strftime('%d/%m')}</b>"]

    if samedi_activites or dimanche_activites:
        for libelle, items in (("Samedi", samedi_activites), ("Dimanche", dimanche_activites)):
            if not items:
                continue
            lignes.append("")
            lignes.append(f"<b>{libelle}</b>")
            for activite in items[:3]:
                titre = html.escape(str(getattr(activite, "titre", "Activité")))
                details: list[str] = [titre]
                heure = getattr(activite, "heure_debut", None)
                cout = getattr(activite, "cout_estime", None)
                if heure:
                    details.append(heure.strftime('%H:%M'))
                if isinstance(cout, int | float) and cout:
                    details.append(f"{float(cout):.0f}€")
                lignes.append(f"• {' — '.join(details)}")

        lignes.append("")
        lignes.append(f"💸 Budget estimé : {float(budget.get('estime', 0) or 0):.0f}€")
    else:
        suggestion = ""
        try:
            suggestion = await obtenir_weekend_ai_service().suggerer_activites(
                meteo="variable",
                age_enfant_mois=36,
                budget=60,
                region="France",
                nb_suggestions=3,
            )
        except Exception as exc:
            logger.warning("Impossible de générer les suggestions weekend Telegram: %s", exc)

        lignes.append("")
        lignes.append("Aucune activité n'est encore planifiée.")
        if suggestion:
            suggestion_compacte = html.escape(suggestion.strip())
            if len(suggestion_compacte) > 900:
                suggestion_compacte = suggestion_compacte[:900].rstrip() + "…"
            lignes.append("")
            lignes.append(suggestion_compacte)
        else:
            lignes.append("💡 Ouvre le module Famille pour préparer le prochain weekend.")

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"url": _obtenir_url_app("/famille"), "title": "🎡 Ouvrir Famille"},
            {"id": "menu_famille", "title": "👶 Menu Famille"},
        ],
    )


async def _envoyer_rapport_hebdo(chat_id: str) -> None:
    from src.services.famille.resume_hebdo import obtenir_service_resume_hebdo
    from src.services.integrations.telegram import envoyer_message_interactif, envoyer_message_telegram

    try:
        resume = obtenir_service_resume_hebdo().generer_resume_semaine_sync()
    except Exception as exc:
        logger.warning("Impossible de générer le résumé hebdo Telegram: %s", exc)
        await envoyer_message_telegram(chat_id, "📋 Le résumé hebdo n'est pas disponible pour le moment.")
        return

    lignes = [
        f"📋 <b>Résumé hebdo {html.escape(str(getattr(resume, 'semaine', '')))}</b>",
        f"⭐ Score semaine : <b>{int(getattr(resume, 'score_semaine', 0) or 0)}/100</b>",
    ]

    repas = getattr(resume, "repas", None)
    if repas is not None:
        lignes.append(
            f"🍽️ Repas : {int(getattr(repas, 'nb_repas_realises', 0) or 0)}/"
            f"{int(getattr(repas, 'nb_repas_planifies', 0) or 0)} réalisés"
        )

    budget = getattr(resume, "budget", None)
    if budget is not None:
        lignes.append(f"💸 Dépenses : {float(getattr(budget, 'total_depenses', 0) or 0):.2f}€")

    activites = getattr(resume, "activites", None)
    if activites is not None:
        lignes.append(f"🎯 Activités : {int(getattr(activites, 'nb_activites', 0) or 0)}")

    taches = getattr(resume, "taches", None)
    if taches is not None:
        lignes.append(
            f"🧰 Tâches : {int(getattr(taches, 'nb_taches_realisees', 0) or 0)} faites • "
            f"{int(getattr(taches, 'nb_taches_en_retard', 0) or 0)} en retard"
        )

    narratif = str(getattr(resume, "resume_narratif", "") or "").strip()
    if narratif:
        narratif_echappe = html.escape(narratif)
        if len(narratif_echappe) > 900:
            narratif_echappe = narratif_echappe[:900].rstrip() + "…"
        lignes.append("")
        lignes.append(narratif_echappe)

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"url": _obtenir_url_app("/famille"), "title": "📋 Ouvrir Famille"},
            {"id": "menu_principal", "title": "🏠 Menu principal"},
        ],
    )


async def _envoyer_aide_photo_telegram(chat_id: str) -> None:
    from src.services.integrations.telegram import envoyer_message_interactif

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps=(
            "📸 <b>Aide photo</b>\n\n"
            "Envoie directement une photo du <b>frigo</b>, d'une <b>plante</b> ou d'une <b>pièce de la maison</b> "
            "et je te répondrai avec une analyse rapide."
        ),
        boutons=[
            {"url": _obtenir_url_app("/cuisine/inventaire"), "title": "🥫 Ouvrir l'inventaire"},
            {"url": _obtenir_url_app("/maison/jardin"), "title": "🌿 Ouvrir le jardin"},
            {"id": "menu_principal", "title": "🏠 Menu principal"},
        ],
    )


async def _envoyer_rappels_groupes(chat_id: str) -> None:
    from src.core.db import obtenir_contexte_db
    from src.core.models.habitat import TacheEntretien
    from src.core.models.inventaire import ArticleInventaire
    from src.core.models.utilitaires import NoteMemo
    from src.services.integrations.telegram import envoyer_message_interactif, envoyer_message_telegram

    aujourd_hui = date.today()
    maintenant = datetime.utcnow()

    with obtenir_contexte_db() as session:
        taches = (
            session.query(TacheEntretien)
            .filter(
                TacheEntretien.fait.is_(False),
                TacheEntretien.prochaine_fois.isnot(None),
                TacheEntretien.prochaine_fois <= aujourd_hui + timedelta(days=2),
            )
            .order_by(TacheEntretien.prochaine_fois.asc(), TacheEntretien.id.asc())
            .limit(4)
            .all()
        )
        peremptions = (
            session.query(ArticleInventaire)
            .filter(
                ArticleInventaire.quantite > 0,
                ArticleInventaire.date_peremption.isnot(None),
                ArticleInventaire.date_peremption <= aujourd_hui + timedelta(days=2),
            )
            .order_by(ArticleInventaire.date_peremption.asc(), ArticleInventaire.id.asc())
            .limit(4)
            .all()
        )
        notes = (
            session.query(NoteMemo)
            .filter(
                NoteMemo.archive.is_(False),
                NoteMemo.rappel_date.isnot(None),
                NoteMemo.rappel_date <= maintenant + timedelta(days=1),
            )
            .order_by(NoteMemo.rappel_date.asc(), NoteMemo.id.asc())
            .limit(3)
            .all()
        )

    if not taches and not peremptions and not notes:
        await envoyer_message_telegram(chat_id, "⏰ Aucun rappel en attente pour le moment.")
        return

    lignes = ["⏰ <b>Rappels en attente</b>"]
    if taches:
        lignes.append("")
        lignes.append("<b>Maison / entretien</b>")
        for tache in taches:
            date_label = tache.prochaine_fois.strftime('%d/%m') if tache.prochaine_fois else "bientôt"
            lignes.append(f"• {html.escape(str(tache.nom))} — {date_label}")
    if peremptions:
        lignes.append("")
        lignes.append("<b>Inventaire</b>")
        for article in peremptions:
            nom = getattr(article, "nom", None) or f"Article #{article.id}"
            date_label = article.date_peremption.strftime('%d/%m') if article.date_peremption else "sans date"
            lignes.append(f"• {html.escape(str(nom))} — {date_label}")
    if notes:
        lignes.append("")
        lignes.append("<b>Notes & pense-bêtes</b>")
        for note in notes:
            date_label = note.rappel_date.strftime('%d/%m %H:%M') if note.rappel_date else "à voir"
            lignes.append(f"• {html.escape(str(note.titre))} — {date_label}")

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"id": "action_maison", "title": "🏠 Tâches maison"},
            {"id": "action_inventaire", "title": "🥫 Inventaire"},
            {"url": _obtenir_url_app("/outils/notes"), "title": "📝 Ouvrir les notes"},
        ],
    )


async def _notifier_fin_minuteur(chat_id: str, minutes: int) -> None:
    from src.services.integrations.telegram import envoyer_message_interactif

    await asyncio.sleep(minutes * 60)
    await envoyer_message_interactif(
        destinataire=chat_id,
        corps=f"⏰ <b>Minuteur terminé</b> — {minutes} min écoulées.",
        boutons=[
            {"id": "action_repas_soir", "title": "🍽️ Voir le repas"},
            {"id": "menu_retour", "title": "🏠 Menu principal"},
        ],
    )


async def _lancer_minuteur_telegram(chat_id: str, argument: str) -> None:
    from src.services.integrations.telegram import envoyer_message_telegram

    match = re.search(r"(\d{1,3})", argument or "")
    if not match:
        await envoyer_message_telegram(chat_id, "⏱️ Utilise par exemple <code>/timer 15</code>.")
        return

    minutes = max(1, min(int(match.group(1)), 180))
    asyncio.create_task(_notifier_fin_minuteur(chat_id, minutes))
    await envoyer_message_telegram(chat_id, f"⏱️ Minuteur lancé pour <b>{minutes} min</b>.")


async def _creer_note_rapide_telegram(chat_id: str, texte_note: str) -> None:
    from src.services.integrations.telegram import envoyer_message_telegram
    from src.services.utilitaires import obtenir_notes_service

    contenu = (texte_note or "").strip()
    if not contenu:
        await envoyer_message_telegram(chat_id, "📝 Utilise <code>/note ton texte</code> pour créer un pense-bête.")
        return

    note = obtenir_notes_service().creer(
        titre=(contenu[:57] + "...") if len(contenu) > 60 else contenu,
        contenu=contenu,
        categorie="telegram",
        couleur="#FFF7CC",
        epingle=False,
        est_checklist=False,
    )
    await envoyer_message_telegram(chat_id, f"📝 Note créée avec succès (#{note.id}).")


async def _traiter_callback_action_article(
    callback_data: str,
    callback_query_id: str,
    chat_id: str,
) -> None:
    from src.api.utils import executer_async, executer_avec_session
    from src.services.integrations.telegram import repondre_callback_query

    morceaux = callback_data.split(":")
    if len(morceaux) != 3:
        await repondre_callback_query(callback_query_id, "❌ Action invalide", show_alert=True)
        return

    _, action, article_brut = morceaux
    try:
        article_id = int(article_brut)
    except ValueError:
        await repondre_callback_query(callback_query_id, "❌ Article invalide", show_alert=True)
        return

    def _appliquer_action() -> dict[str, object]:
        from src.core.models.courses import ArticleCourses

        with executer_avec_session() as session:
            article = session.query(ArticleCourses).filter(ArticleCourses.id == article_id).first()
            if not article:
                return {"status": 404, "error": "Article non trouvé"}

            nom_article = getattr(getattr(article, "ingredient", None), "nom", None) or f"Article #{article.id}"
            if action == "achete":
                article.achete = True
                article.achete_le = datetime.utcnow()
                article.notes = "Validé depuis Telegram"
                message = f"✅ {nom_article} acheté"
            elif action == "manquant":
                article.achete = False
                article.achete_le = None
                article.notes = "Pas trouvé en magasin (Telegram)"
                message = f"❌ {nom_article} marqué comme introuvable"
            elif action == "reporter":
                article.achete = False
                article.achete_le = None
                article.notes = "À reporter / vérifier plus tard (Telegram)"
                message = f"🔄 {nom_article} reporté"
            else:
                return {"status": 400, "error": "Action inconnue"}

            session.commit()
            return {"status": 200, "message": message, "liste_id": article.liste_id}

    resultat = await executer_async(_appliquer_action)
    if resultat.get("status") != 200:
        await repondre_callback_query(
            callback_query_id,
            f"❌ {resultat.get('error', 'Erreur')}",
            show_alert=True,
        )
        return

    await repondre_callback_query(callback_query_id, str(resultat.get("message") or "✅ OK"), show_alert=False)
    await _envoyer_courses_commande(chat_id, liste_id=int(resultat["liste_id"]))


async def _traiter_callback_sondage_repas(
    callback_data: str,
    callback_query_id: str,
    chat_id: str,
) -> None:
    from src.services.integrations.telegram import envoyer_message_telegram, repondre_callback_query

    choix = callback_data.split(":", 1)[1] if ":" in callback_data else "surprise"
    libelles = {
        "midi": "un repas plutôt simple pour midi",
        "soir": "un dîner réconfortant pour ce soir",
        "surprise": "une idée surprise",
    }
    message = libelles.get(choix, choix)
    await repondre_callback_query(callback_query_id, "🍽️ Préférence notée", show_alert=False)
    await envoyer_message_telegram(chat_id, f"🍽️ Bien noté, vous avez envie de {html.escape(message)}.")


async def _traiter_photo_frigo_telegram(chat_id: str, photos: list[dict[str, object]]) -> None:
    from src.services.cuisine.photo_frigo import obtenir_photo_frigo_service
    from src.services.integrations.telegram import (
        envoyer_message_interactif,
        envoyer_message_telegram,
        telecharger_fichier_telegram,
    )

    if not photos:
        await envoyer_message_telegram(chat_id, "📸 Photo reçue, mais le fichier est introuvable.")
        return

    photo = max(photos, key=lambda item: int(item.get("file_size") or 0))
    file_id = str(photo.get("file_id") or "")
    if not file_id:
        await envoyer_message_telegram(chat_id, "📸 Photo reçue, mais le fichier est incomplet.")
        return

    await envoyer_message_telegram(chat_id, "📸 Photo du frigo reçue, j’analyse les ingrédients…")
    image_bytes = await telecharger_fichier_telegram(file_id)
    if not image_bytes:
        await envoyer_message_telegram(chat_id, "📸 Analyse indisponible : téléchargement Telegram impossible.")
        return

    resultat = await obtenir_photo_frigo_service().analyser_photo_frigo(image_bytes)
    if not resultat.ingredients_detectes and not resultat.recettes_db and not resultat.recettes_suggerees:
        await envoyer_message_telegram(chat_id, "📸 Je n’ai pas détecté assez d’ingrédients exploitables sur cette photo.")
        return

    ingredients = ", ".join(ingredient.nom for ingredient in resultat.ingredients_detectes[:6]) or "aucun"
    recettes = [recette.nom for recette in resultat.recettes_db[:3]] or [
        recette.nom for recette in resultat.recettes_suggerees[:3]
    ]
    lignes = [
        "📸 <b>Analyse photo frigo</b>",
        f"Ingrédients détectés : {html.escape(ingredients)}",
    ]
    if recettes:
        lignes.append("")
        lignes.append("<b>Idées de recettes</b>")
        lignes.extend(f"• {html.escape(str(nom))}" for nom in recettes[:3])

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"id": "action_courses", "title": "🛒 Voir les courses"},
            {"id": "action_planning", "title": "🍽️ Voir le planning"},
            {"url": _obtenir_url_app("/cuisine/recettes"), "title": "📖 Ouvrir les recettes"},
        ],
    )


async def _traiter_callback_toggle_article(
    callback_data: str,
    callback_query_id: str,
    chat_id: str,
) -> None:
    from src.api.utils import executer_async, executer_avec_session
    from src.services.integrations.telegram import repondre_callback_query

    article_id = _extraire_id_depuis_callback(callback_data, "courses_toggle_article")
    if article_id is None:
        await repondre_callback_query(callback_query_id, "❌ Article invalide", show_alert=True)
        return

    def _toggle() -> dict[str, object]:
        from src.core.models.courses import ArticleCourses

        with executer_avec_session() as session:
            article = session.query(ArticleCourses).filter(ArticleCourses.id == article_id).first()
            if not article:
                return {"status": 404, "error": "Article non trouvé"}

            article.achete = not bool(article.achete)
            article.achete_le = datetime.utcnow() if article.achete else None
            nom_article = getattr(getattr(article, "ingredient", None), "nom", None) or f"Article #{article.id}"
            liste_id = article.liste_id
            session.commit()
            return {
                "status": 200,
                "achete": article.achete,
                "nom": nom_article,
                "liste_id": liste_id,
            }

    result = await executer_async(_toggle)
    if result.get("status") != 200:
        await repondre_callback_query(
            callback_query_id,
            f"❌ {result.get('error', 'Erreur')}",
            show_alert=True,
        )
        return

    prefixe = "☑️" if result.get("achete") else "☐"
    await repondre_callback_query(
        callback_query_id,
        f"{prefixe} {result.get('nom')}",
        show_alert=False,
    )
    await _envoyer_courses_commande(chat_id, liste_id=int(result["liste_id"]))


async def _traiter_callback_menu(
    callback_data: str,
    callback_query_id: str,
    chat_id: str,
) -> None:
    from src.services.integrations.telegram import repondre_callback_query

    await repondre_callback_query(callback_query_id, "Ouverture...", show_alert=False)

    if callback_data in {"menu_principal", "menu_retour"}:
        await _envoyer_menu_principal(chat_id)
    elif callback_data == "menu_cuisine":
        await _envoyer_menu_module(chat_id, "cuisine")
    elif callback_data == "menu_famille":
        await _envoyer_menu_module(chat_id, "famille")
    elif callback_data == "menu_maison":
        await _envoyer_menu_module(chat_id, "maison")
    elif callback_data == "menu_outils":
        await _envoyer_menu_module(chat_id, "outils")
    elif callback_data == "menu_aide":
        await _envoyer_aide_telegram(chat_id)
    elif callback_data == "action_planning":
        await _envoyer_planning_commande(chat_id)
    elif callback_data == "action_courses":
        await _envoyer_courses_commande(chat_id)
    elif callback_data == "action_repas_midi":
        await _envoyer_repas_moment(chat_id, "midi")
    elif callback_data == "action_repas_soir":
        await _envoyer_repas_moment(chat_id, "soir")
    elif callback_data == "action_inventaire":
        await _envoyer_inventaire_commande(chat_id)
    elif callback_data == "action_batch":
        await _envoyer_resume_batch_cooking(chat_id)
    elif callback_data == "action_jules":
        await _envoyer_resume_jules(chat_id)
    elif callback_data == "action_maison":
        await _envoyer_taches_maison(chat_id)
    elif callback_data == "action_jardin":
        await _envoyer_resume_jardin(chat_id)
    elif callback_data == "action_energie":
        await _envoyer_resume_energie(chat_id)
    elif callback_data == "action_rappels":
        await _envoyer_rappels_groupes(chat_id)
    elif callback_data == "action_note_modele":
        await _creer_note_rapide_telegram(chat_id, "Pense-bête Telegram")
    elif callback_data == "action_timer_10":
        await _lancer_minuteur_telegram(chat_id, "10")
    elif callback_data == "action_budget":
        await _envoyer_resume_budget(chat_id)
    elif callback_data == "action_meteo":
        await _envoyer_meteo_telegram(chat_id)
    else:
        await _envoyer_menu_principal(chat_id)


async def _traiter_reponse_rapide_ok(chat_id: str) -> bool:
    from src.api.utils import executer_async, executer_avec_session
    from src.services.integrations.telegram import (
        charger_etat_conversation,
        effacer_etat_conversation,
        envoyer_message_telegram,
    )

    etat = charger_etat_conversation(chat_id)
    if not etat:
        return False

    type_etat = etat.get("type")
    if type_etat == "planning_validation":
        planning_id = etat.get("planning_id")

        def _valider() -> dict[str, object]:
            from src.core.models.planning import Planning

            with executer_avec_session() as session:
                planning = session.query(Planning).filter(Planning.id == planning_id).first()
                if not planning:
                    return {"status": 404, "error": "Planning non trouvé"}
                if planning.etat == "valide":
                    return {"status": 200, "message": "Planning déjà validé"}
                if planning.etat != "brouillon":
                    return {"status": 409, "error": f"Planning déjà {planning.etat}"}
                planning.etat = "valide"
                session.commit()
                return {"status": 200, "message": "Planning validé"}

        result = await executer_async(_valider)
        if result.get("status") == 200:
            effacer_etat_conversation(chat_id)
            await envoyer_message_telegram(chat_id, "✅ Planning validé depuis Telegram.")
            return True

        await envoyer_message_telegram(chat_id, f"❌ {result.get('error', 'Validation impossible')}")
        return True

    if type_etat == "courses_confirmation":
        liste_id = etat.get("liste_id")

        def _confirmer() -> dict[str, object]:
            from src.core.models.courses import ListeCourses

            with executer_avec_session() as session:
                liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
                if not liste:
                    return {"status": 404, "error": "Liste non trouvée"}
                if liste.etat == "active":
                    return {"status": 200, "message": "Liste déjà active"}
                if liste.etat != "brouillon":
                    return {"status": 409, "error": f"Liste déjà {liste.etat}"}
                liste.etat = "active"
                session.commit()
                return {"status": 200, "message": "Liste confirmée"}

        result = await executer_async(_confirmer)
        if result.get("status") == 200:
            effacer_etat_conversation(chat_id)
            await envoyer_message_telegram(chat_id, "✅ Liste de courses confirmée depuis Telegram.")
            return True

        await envoyer_message_telegram(chat_id, f"❌ {result.get('error', 'Confirmation impossible')}")
        return True

    return False


async def _dispatcher_commande_telegram(chat_id: str, texte: str, normalise: str) -> bool:
    argument = ""
    if texte.strip():
        morceaux = texte.strip().split(maxsplit=1)
        if len(morceaux) > 1:
            argument = morceaux[1].strip()

    if normalise in {"/menu", "menu"}:
        await _envoyer_menu_principal(chat_id)
        return True
    if normalise in {"/aide", "/help", "aide", "help"}:
        await _envoyer_aide_telegram(chat_id)
        return True
    if normalise == "/planning":
        await _envoyer_planning_commande(chat_id)
        return True
    if normalise in {"/courses", "/course", "/courses_live"}:
        await _envoyer_courses_commande(chat_id)
        return True
    if normalise == "/inventaire":
        await _envoyer_inventaire_commande(chat_id)
        return True
    if normalise == "/recette":
        await _envoyer_recette_commande(chat_id, argument)
        return True
    if normalise == "/batch":
        await _envoyer_resume_batch_cooking(chat_id)
        return True
    if normalise == "/jules":
        await _envoyer_resume_jules(chat_id)
        return True
    if normalise == "/maison":
        await _envoyer_taches_maison(chat_id)
        return True
    if normalise == "/jardin":
        await _envoyer_resume_jardin(chat_id)
        return True
    if normalise == "/weekend":
        await _envoyer_resume_weekend(chat_id)
        return True
    if normalise == "/energie":
        await _envoyer_resume_energie(chat_id)
        return True
    if normalise == "/rappels":
        await _envoyer_rappels_groupes(chat_id)
        return True
    if normalise == "/budget":
        await _envoyer_resume_budget(chat_id)
        return True
    if normalise == "/rapport":
        await _envoyer_rapport_hebdo(chat_id)
        return True
    if normalise == "/photo":
        await _envoyer_aide_photo_telegram(chat_id)
        return True
    if normalise == "/meteo":
        await _envoyer_meteo_telegram(chat_id)
        return True
    if normalise.startswith("/ajout") or normalise.startswith("/ajouter_course"):
        await _ajouter_article_liste(chat_id, argument)
        return True
    if normalise.startswith("/repas"):
        argument_norm = _normaliser_texte(argument)
        if any(mot in argument_norm for mot in ("midi", "dejeuner")):
            await _envoyer_repas_moment(chat_id, "midi")
        elif any(mot in argument_norm for mot in ("soir", "diner")):
            await _envoyer_repas_moment(chat_id, "soir")
        else:
            await _envoyer_repas_moment(chat_id)
        return True
    if normalise.startswith("/timer"):
        await _lancer_minuteur_telegram(chat_id, argument)
        return True
    if normalise.startswith("/note"):
        await _creer_note_rapide_telegram(chat_id, argument)
        return True

    return False


async def _traiter_callback_planning(
    callback_data: str,
    callback_query_id: str,
    chat_id: str,
) -> None:
    """Traite les callbacks de planning: valider, modifier, régénérer.

    Relie les boutons Telegram aux endpoints de validation du planning.
    """
    from src.api.utils import executer_async, executer_avec_session
    from src.services.integrations.telegram import repondre_callback_query, modifier_message
    
    # Parse callback_data: "planning_valider:ID" ou "planning_valider" (backward compat)
    if ":" in callback_data:
        action, id_str = callback_data.split(":", 1)
        try:
            planning_id = int(id_str)
        except ValueError:
            await repondre_callback_query(callback_query_id, "❌ Erreur: ID invalide")
            logger.error(f"Invalid planning ID in callback: {callback_data}")
            return
    else:
        # Backward compat: prendre le planning de la semaine actuelle
        action = callback_data
        planning_id = None

    logger.info(f"Callback planning reçu: action={action}, planning_id={planning_id}")

    if action == "planning_valider":
        # Trigger: POST /api/v1/planning/{planning_id}/valider
        try:
            def _valider():
                from src.core.db import obtenir_contexte_db
                from src.core.models.planning import Planning

                with executer_avec_session() as session:
                    if planning_id:
                        planning = session.query(Planning).filter(Planning.id == planning_id).first()
                    else:
                        planning = session.query(Planning).order_by(Planning.semaine_debut.desc()).first()

                    if not planning:
                        return {"error": "Planning non trouvé", "status": 404}

                    if planning.etat != "brouillon":
                        return {"error": f"Planning déjà {planning.etat}", "status": 409}

                    planning.etat = "valide"
                    session.commit()
                    return {"message": "Planning validé", "id": planning.id, "status": 200}

            result = await executer_async(_valider)
            if result.get("status") == 200:
                await repondre_callback_query(
                    callback_query_id,
                    "✅ Planning validé!",
                    show_alert=False,
                )
                await modifier_message(
                    chat_id,
                    (await _obtenir_message_id(callback_query_id)) or 0,
                    "✅ <b>Planning validé</b>\n\nVotre planning a été validé et les courses sont générées.",
                    boutons=None,
                )
            else:
                await repondre_callback_query(
                    callback_query_id,
                    f"❌ {result.get('error', 'Erreur')}",
                    show_alert=True,
                )
        except Exception as e:
            logger.error(f"❌ Erreur traitement callback planning_valider: {e}", exc_info=True)
            await repondre_callback_query(callback_query_id, "❌ Erreur serveur", show_alert=True)

    elif action == "planning_modifier":
        # Instruction pour modifier via web
        web_url = "https://matanne.vercel.app/app/cuisine/planning"
        await repondre_callback_query(
            callback_query_id,
            f"Ouvrez ce lien pour modifier: {web_url}",
            show_alert=False,
        )

    elif action == "planning_regenerer":
        # Trigger: POST /api/v1/planning/{planning_id}/regenerer
        try:
            def _regenerer():
                from src.core.db import obtenir_contexte_db
                from src.core.models.planning import Planning

                with executer_avec_session() as session:
                    if planning_id:
                        old_planning = session.query(Planning).filter(Planning.id == planning_id).first()
                    else:
                        old_planning = session.query(Planning).order_by(Planning.semaine_debut.desc()).first()

                    if not old_planning:
                        return {"error": "Planning non trouvé", "status": 404}

                    if old_planning.etat == "archive":
                        return {"error": "Planning archivé ne peut pas être régénéré", "status": 409}

                    # Archive old planning
                    old_planning.etat = "archive"
                    session.flush()

                    # Create new planning (brouillon)
                    # This would normally be done by a service
                    new_planning = Planning(
                        nom=f"{old_planning.nom} (refait)",
                        semaine_debut=old_planning.semaine_debut,
                        semaine_fin=old_planning.semaine_fin,
                        etat="brouillon",
                    )
                    session.add(new_planning)
                    session.commit()
                    return {"message": "Planning régénéré", "id": new_planning.id, "status": 200}

            result = await executer_async(_regenerer)
            if result.get("status") == 200:
                await repondre_callback_query(
                    callback_query_id,
                    "🔄 Planning en cours de régénération...",
                    show_alert=False,
                )
                await modifier_message(
                    chat_id,
                    (await _obtenir_message_id(callback_query_id)) or 0,
                    "🔄 <b>Planning régénéré</b>\n\nLe nouveau planning en brouillon est prêt.",
                    boutons=None,
                )
            else:
                await repondre_callback_query(
                    callback_query_id,
                    f"❌ {result.get('error', 'Erreur')}",
                    show_alert=True,
                )
        except Exception as e:
            logger.error(f"❌ Erreur traitement callback planning_regenerer: {e}", exc_info=True)
            await repondre_callback_query(callback_query_id, "❌ Erreur serveur", show_alert=True)


async def _traiter_callback_courses(
    callback_data: str,
    callback_query_id: str,
    chat_id: str,
) -> None:
    """Traite les callbacks de courses: confirmer, ajouter, refaire.

    Relie les boutons Telegram aux endpoints de confirmation de liste.
    """
    from src.api.utils import executer_async, executer_avec_session
    from src.services.integrations.telegram import repondre_callback_query, modifier_message
    
    # Parse callback_data: "courses_confirmer:ID" ou "courses_confirmer" (backward compat)
    if ":" in callback_data:
        action, id_str = callback_data.split(":", 1)
        try:
            liste_id = int(id_str)
        except ValueError:
            await repondre_callback_query(callback_query_id, "❌ Erreur: ID invalide")
            logger.error(f"Invalid courses list ID in callback: {callback_data}")
            return
    else:
        action = callback_data
        liste_id = None

    logger.info(f"Callback courses reçu: action={action}, liste_id={liste_id}")

    if action == "courses_confirmer":
        # Trigger: POST /api/v1/courses/{liste_id}/confirmer
        try:
            def _confirmer():
                from src.core.db import obtenir_contexte_db
                from src.core.models.courses import ListeCourses

                with executer_avec_session() as session:
                    if liste_id:
                        liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
                    else:
                        liste = session.query(ListeCourses).filter(
                            ListeCourses.etat == "brouillon"
                        ).order_by(ListeCourses.cree_le.desc()).first()

                    if not liste:
                        return {"error": "Liste non trouvée", "status": 404}

                    if liste.etat != "brouillon":
                        return {"error": f"Liste déjà {liste.etat}", "status": 409}

                    liste.etat = "active"
                    session.commit()
                    return {"message": "Liste confirmée", "id": liste.id, "status": 200}

            result = await executer_async(_confirmer)
            if result.get("status") == 200:
                await repondre_callback_query(
                    callback_query_id,
                    "✅ Liste confirmée!",
                    show_alert=False,
                )
                await modifier_message(
                    chat_id,
                    (await _obtenir_message_id(callback_query_id)) or 0,
                    "✅ <b>Liste de courses confirmée</b>\n\nVous pouvez maintenant faire les courses!",
                    boutons=None,
                )
            else:
                await repondre_callback_query(
                    callback_query_id,
                    f"❌ {result.get('error', 'Erreur')}",
                    show_alert=True,
                )
        except Exception as e:
            logger.error(f"❌ Erreur traitement callback courses_confirmer: {e}", exc_info=True)
            await repondre_callback_query(callback_query_id, "❌ Erreur serveur", show_alert=True)

    elif action == "courses_ajouter":
        # Instruction pour ajouter via web
        web_url = "https://matanne.vercel.app/app/cuisine/courses"
        await repondre_callback_query(
            callback_query_id,
            f"Ouvrez ce lien pour ajouter: {web_url}",
            show_alert=False,
        )

    elif action == "courses_refaire":
        # Archive current list and create new brouillon
        try:
            def _refaire():
                from src.core.db import obtenir_contexte_db
                from src.core.models.courses import ListeCourses

                with executer_avec_session() as session:
                    if liste_id:
                        old_liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
                    else:
                        old_liste = session.query(ListeCourses).filter(
                            ListeCourses.etat == "brouillon"
                        ).order_by(ListeCourses.cree_le.desc()).first()

                    if not old_liste:
                        return {"error": "Liste non trouvée", "status": 404}

                    # Archive old list
                    old_liste.archivee = True
                    session.flush()

                    # Create new list (brouillon)
                    new_liste = ListeCourses(nom=f"{old_liste.nom} (refait)", etat="brouillon")
                    session.add(new_liste)
                    session.commit()
                    return {"message": "Liste refaite", "id": new_liste.id, "status": 200}

            result = await executer_async(_refaire)
            if result.get("status") == 200:
                await repondre_callback_query(
                    callback_query_id,
                    "🔄 Liste en cours de refonte...",
                    show_alert=False,
                )
                await modifier_message(
                    chat_id,
                    (await _obtenir_message_id(callback_query_id)) or 0,
                    "🔄 <b>Liste refaite</b>\n\nUne nouvelle liste brouillon a été créée.",
                    boutons=None,
                )
            else:
                await repondre_callback_query(
                    callback_query_id,
                    f"❌ {result.get('error', 'Erreur')}",
                    show_alert=True,
                )
        except Exception as e:
            logger.error(f"❌ Erreur traitement callback courses_refaire: {e}", exc_info=True)
            await repondre_callback_query(callback_query_id, "❌ Erreur serveur", show_alert=True)


async def _obtenir_message_id(callback_query_id: str) -> int | None:
    """Stub pour obtenir le message_id depuis callback_query_id (normally in payload)."""
    # Note: This would normally come from the webhook payload
    # For now, return None to indicate we can't modify the message
    return None


async def _envoyer_repas_du_soir(chat_id: str) -> None:
    from src.core.db import obtenir_contexte_db
    from src.core.models.planning import Repas
    from src.services.integrations.telegram import envoyer_message_telegram

    with obtenir_contexte_db() as session:
        repas = (
            session.query(Repas)
            .filter(Repas.date_repas == date.today(), Repas.type_repas == "diner")
            .first()
        )

    if repas:
        nom = repas.recette.nom if getattr(repas, "recette", None) else (repas.notes or "Repas du soir")
        await envoyer_message_telegram(chat_id, f"🍽️ Ce soir: <b>{nom}</b>.")
        return

    await envoyer_message_telegram(
        chat_id,
        "🍽️ Rien de planifie pour ce soir. Suggestion rapide: omelette + salade + fruit.",
    )


async def _ajouter_article_liste(chat_id: str, article: str) -> None:
    from src.core.db import obtenir_contexte_db
    from src.core.models.courses import ArticleCourses, ListeCourses
    from src.core.models.recettes import Ingredient
    from src.services.integrations.telegram import envoyer_message_telegram

    nom_article = (article or "").strip()
    if not nom_article:
        await envoyer_message_telegram(chat_id, "🛒 Quel article veux-tu ajouter exactement ?")
        return

    with obtenir_contexte_db() as session:
        liste = (
            session.query(ListeCourses)
            .filter(ListeCourses.archivee.is_(False))
            .order_by(ListeCourses.cree_le.desc())
            .first()
        )
        if not liste:
            liste = ListeCourses(nom="Courses Telegram")
            session.add(liste)
            session.flush()

        ingredient = session.query(Ingredient).filter(Ingredient.nom.ilike(nom_article)).first()
        if not ingredient:
            ingredient = Ingredient(nom=nom_article.capitalize())
            session.add(ingredient)
            session.flush()

        existant = (
            session.query(ArticleCourses)
            .filter(
                ArticleCourses.liste_id == liste.id,
                ArticleCourses.ingredient_id == ingredient.id,
                ArticleCourses.achete.is_(False),
            )
            .first()
        )
        if existant:
            await envoyer_message_telegram(chat_id, f"🛒 '{nom_article}' est deja sur la liste.")
            return

        session.add(
            ArticleCourses(
                liste_id=liste.id,
                ingredient_id=ingredient.id,
                quantite_necessaire=1,
                achete=False,
            )
        )
        session.commit()

    await envoyer_message_telegram(chat_id, f"✅ '{nom_article}' ajoute a la liste.")


async def _envoyer_activites_samedi(chat_id: str) -> None:
    from src.core.db import obtenir_contexte_db
    from src.core.models.famille import ActiviteFamille
    from src.services.integrations.telegram import envoyer_message_telegram

    aujourd_hui = date.today()
    jours_jusqua_samedi = (5 - aujourd_hui.weekday()) % 7
    prochain_samedi = aujourd_hui + timedelta(days=jours_jusqua_samedi)

    with obtenir_contexte_db() as session:
        activites = (
            session.query(ActiviteFamille)
            .filter(
                ActiviteFamille.date_prevue == prochain_samedi,
                ActiviteFamille.statut.in_(["planifié", "planifie", "à venir", "a venir"]),
            )
            .order_by(ActiviteFamille.heure_debut.asc())
            .limit(3)
            .all()
        )

    if not activites:
        await envoyer_message_telegram(
            chat_id,
            "🎯 Rien de planifie samedi pour le moment. Suggestion: parc le matin, activite calme l'apres-midi.",
        )
        return

    lignes: list[str] = []
    for activite in activites:
        heure = activite.heure_debut.strftime("%H:%M") if activite.heure_debut else "horaire libre"
        lieu = f" - {activite.lieu}" if activite.lieu else ""
        lignes.append(f"- {heure} : {activite.titre}{lieu}")

    await envoyer_message_telegram(
        chat_id,
        "🎯 <b>Activites prevues samedi</b>\n\n" + "\n".join(lignes),
    )


@router.post("/envoyer-planning", response_model=MessageResponse)
@gerer_exception_api
async def envoyer_planning_telegram(payload: EnvoyerPlanningTelegramRequest) -> MessageResponse:
    """Envoie un planning existant sur Telegram avec boutons interactifs."""
    from src.api.utils import executer_async, executer_avec_session
    from src.core.models.planning import Planning
    from src.services.integrations.telegram import envoyer_planning_semaine

    def _charger_planning() -> dict[str, object]:
        with executer_avec_session() as session:
            planning = session.query(Planning).filter(Planning.id == payload.planning_id).first()
            if not planning:
                raise HTTPException(status_code=404, detail="Planning non trouvé")

            lignes = []
            repas_tries = sorted(planning.repas, key=lambda item: (item.date_repas, item.type_repas))
            for repas in repas_tries:
                nom_recette = None
                if getattr(repas, "recette", None) is not None:
                    nom_recette = getattr(repas.recette, "nom", None)
                lignes.append(
                    f"• {repas.date_repas.strftime('%d/%m')} {repas.type_repas} : {nom_recette or 'Repas à préciser'}"
                )

            return {
                "planning_id": planning.id,
                "contenu": payload.contenu
                or "\n".join(lignes)
                or f"Planning {planning.nom} du {planning.semaine_debut.strftime('%d/%m')} au {planning.semaine_fin.strftime('%d/%m')}",
            }

    resultat = await executer_async(_charger_planning)
    succes = await envoyer_planning_semaine(
        str(resultat["contenu"]),
        planning_id=int(resultat["planning_id"]),
    )
    if not succes:
        raise HTTPException(status_code=502, detail="Envoi Telegram impossible")

    return MessageResponse(message="planning_envoye", id=int(resultat["planning_id"]))


class EnvoyerCoursesMagasinRequest(BaseModel):
    """Payload pour l'envoi d'une sous-liste de courses par magasin via Telegram."""

    liste_id: int
    magasin: str = Field(..., min_length=1, max_length=50, description="Magasin cible (bio_coop, grand_frais, etc.)")
    nom_liste: str | None = None


LIBELLES_MAGASINS: dict[str, str] = {
    "bio_coop": "🥬 Bio Coop",
    "grand_frais": "🧀 Grand Frais",
    "carrefour_drive": "🛒 Carrefour Drive",
}


@router.post("/envoyer-courses", response_model=MessageResponse)
@gerer_exception_api
async def envoyer_courses_telegram(payload: EnvoyerCoursesTelegramRequest) -> MessageResponse:
    """Envoie une liste de courses existante sur Telegram avec boutons interactifs."""
    from src.api.utils import executer_async, executer_avec_session
    from src.core.models.courses import ListeCourses
    from src.services.integrations.telegram import envoyer_liste_courses_partagee

    def _charger_liste() -> dict[str, object]:
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == payload.liste_id).first()
            if not liste:
                raise HTTPException(status_code=404, detail="Liste de courses non trouvée")

            articles = []
            for article in liste.articles:
                ingredient = getattr(article, "ingredient", None)
                nom_article = getattr(ingredient, "nom", None) or f"Article #{article.id}"
                articles.append(nom_article)

            if not articles:
                raise HTTPException(status_code=400, detail="La liste ne contient aucun article")

            return {
                "liste_id": liste.id,
                "nom_liste": payload.nom_liste or liste.nom,
                "articles": articles,
            }

    resultat = await executer_async(_charger_liste)
    succes = await envoyer_liste_courses_partagee(
        list(resultat["articles"]),
        nom_liste=str(resultat["nom_liste"]),
        liste_id=int(resultat["liste_id"]),
    )
    if not succes:
        raise HTTPException(status_code=502, detail="Envoi Telegram impossible")

    return MessageResponse(message="courses_envoyees", id=int(resultat["liste_id"]))


@router.post("/envoyer-courses-magasin", response_model=MessageResponse)
@gerer_exception_api
async def envoyer_courses_par_magasin(payload: EnvoyerCoursesMagasinRequest) -> MessageResponse:
    """Envoie sur Telegram les articles d'une liste filtrés par magasin cible.

    Idéal pour envoyer la sous-liste Bio Coop ou Grand Frais sur le téléphone
    avant d'aller en magasin physique.
    """
    from src.api.utils import executer_async, executer_avec_session
    from src.core.models.courses import ArticleCourses, ListeCourses
    from src.services.integrations.telegram import envoyer_liste_courses_partagee

    def _charger_articles() -> dict[str, object]:
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == payload.liste_id).first()
            if not liste:
                raise HTTPException(status_code=404, detail="Liste de courses non trouvée")

            articles_db = (
                session.query(ArticleCourses)
                .filter(
                    ArticleCourses.liste_id == liste.id,
                    ArticleCourses.magasin_cible == payload.magasin,
                    ArticleCourses.achete.is_(False),
                )
                .order_by(ArticleCourses.rayon_magasin, ArticleCourses.id)
                .all()
            )

            articles = []
            for article in articles_db:
                ingredient = getattr(article, "ingredient", None)
                nom = getattr(ingredient, "nom", None) or f"Article #{article.id}"
                qte = article.quantite_necessaire
                unite = getattr(ingredient, "unite", "") or ""
                ligne = f"{nom} ({qte} {unite})".strip() if qte != 1 else nom
                articles.append(ligne)

            if not articles:
                raise HTTPException(
                    status_code=400,
                    detail=f"Aucun article non acheté pour le magasin '{payload.magasin}'",
                )

            libelle = LIBELLES_MAGASINS.get(payload.magasin, payload.magasin)
            nom_liste = payload.nom_liste or f"{libelle} — {liste.nom}"

            return {
                "liste_id": liste.id,
                "nom_liste": nom_liste,
                "articles": articles,
            }

    resultat = await executer_async(_charger_articles)
    succes = await envoyer_liste_courses_partagee(
        list(resultat["articles"]),
        nom_liste=str(resultat["nom_liste"]),
        liste_id=int(resultat["liste_id"]),
    )
    if not succes:
        raise HTTPException(status_code=502, detail="Envoi Telegram impossible")

    return MessageResponse(message="courses_magasin_envoyees", id=int(resultat["liste_id"]))


@router.post("/webhook", response_model=MessageResponse)
@gerer_exception_api
async def recevoir_update_telegram(request: Request) -> MessageResponse:
    """Recoit un update Telegram et traite les commandes principales et callbacks.

    Gère:
    - callback_query pour les boutons planning et courses
    - message texte pour les commandes naturelles
    """
    payload = await request.json()

    # Traitement des callbacks issus des boutons interactifs.
    callback_query = payload.get("callback_query") or {}
    if callback_query:
        data = str(callback_query.get("data") or "").strip()
        message_info = callback_query.get("message") or {}
        chat_id = str((message_info.get("chat") or {}).get("id") or "")
        callback_query_id = callback_query.get("id") or ""
        message_id = message_info.get("message_id")

        if not chat_id or not data or not callback_query_id:
            logger.warning(f"Callback incomplet: chat_id={chat_id}, data={data}, id={callback_query_id}")
            return MessageResponse(message="invalid_callback", id=0)

        logger.info(f"Callback Telegram reçu: {data} (msg_id={message_id})")

        # Dispatch vers le handler correspondant.
        if data.startswith("courses_toggle_article:"):
            await _traiter_callback_toggle_article(data, callback_query_id, chat_id)
        elif data.startswith("courses_action:"):
            await _traiter_callback_action_article(data, callback_query_id, chat_id)
        elif data.startswith("repas_sondage:"):
            await _traiter_callback_sondage_repas(data, callback_query_id, chat_id)
        elif data.startswith("planning_"):
            await _traiter_callback_planning(data, callback_query_id, chat_id)
        elif data.startswith("courses_"):
            await _traiter_callback_courses(data, callback_query_id, chat_id)
        elif data.startswith("menu_") or data.startswith("action_"):
            await _traiter_callback_menu(data, callback_query_id, chat_id)
        else:
            # Backward compat: anciennes commandes
            if data == "cmd_ce_soir":
                await _envoyer_repas_du_soir(chat_id)
            elif data == "cmd_courses":
                await _ajouter_article_liste(chat_id, "lait")
            elif data == "cmd_samedi":
                await _envoyer_activites_samedi(chat_id)

        return MessageResponse(message="ok", id=0)

    # Traitement des messages texte (commandes naturelles, backward compat)
    message = payload.get("message") or {}
    if not message:
        return MessageResponse(message="ok", id=0)

    chat_id = str((message.get("chat") or {}).get("id") or "")
    photos = message.get("photo") or []
    texte = str(message.get("text") or "").strip()

    if chat_id and photos:
        await _traiter_photo_frigo_telegram(chat_id, list(photos))
        return MessageResponse(message="ok", id=0)

    if not chat_id or not texte:
        return MessageResponse(message="ok", id=0)

    normalise = _normaliser_texte(texte)
    logger.info("Message Telegram recu (%s): %s", chat_id[:6], normalise)

    if normalise in {"ok", "oui", "vas-y", "go", "valide"}:
        if await _traiter_reponse_rapide_ok(chat_id):
            return MessageResponse(message="ok", id=0)

    commande = _extraire_commande_telegram(texte)
    if commande.startswith("/") or commande in {"menu", "aide", "help"}:
        if await _dispatcher_commande_telegram(chat_id, texte, commande):
            return MessageResponse(message="ok", id=0)

    if "ce soir" in normalise or "qu'est-ce qu'on mange" in normalise or "quest ce quon mange" in normalise:
        await _envoyer_repas_du_soir(chat_id)
    elif normalise.startswith("ajoute ") or normalise.startswith("ajouter "):
        await _ajouter_article_liste(chat_id, _extraire_article_depuis_commande(texte))
    elif "activite samedi" in normalise or "activite pour samedi" in normalise:
        await _envoyer_activites_samedi(chat_id)
    else:
        from src.services.integrations.telegram import envoyer_message_interactif

        await envoyer_message_interactif(
            destinataire=chat_id,
            corps=_construire_message_aide(),
            boutons=[
                {"id": "menu_principal", "title": "🏠 Menu principal"},
                {"id": "action_planning", "title": "🍽️ Planning"},
                {"id": "action_courses", "title": "🛒 Courses"},
            ],
        )

    return MessageResponse(message="ok", id=0)
