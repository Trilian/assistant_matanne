"""Webhook Telegram pour les commandes en langage naturel.

Endpoints:
- POST /api/v1/telegram/webhook : reception des updates Telegram

Commandes bot Telegram :
- "Qu'est-ce qu'on mange ce soir ?"
- "Ajoute lait a la liste"
- "Activite samedi ?"
"""

from __future__ import annotations

import html
import logging
import re
import unicodedata
from datetime import date, datetime, timedelta

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from src.api.schemas import MessageResponse
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/telegram", tags=["Telegram"])


COMMANDES_TELEGRAM: tuple[tuple[str, str], ...] = (
    ("/planning", "Afficher le planning repas de la semaine"),
    ("/courses", "Afficher la liste de courses avec cases à cocher"),
    ("/ajout [article]", "Ajouter un article à la liste de courses"),
    ("/repas [midi|soir]", "Voir le repas du jour ou ouvrir la modification"),
    ("/jules", "Résumé Jules: âge et jalons du moment"),
    ("/maison", "Tâches maison du jour"),
    ("/budget", "Résumé budget du mois en cours"),
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
                {"id": "action_budget", "title": "💰 Budget maison/famille"},
            ],
        },
        "outils": {
            "titre": "🧰 <b>Outils</b>",
            "boutons": [
                {"id": "action_meteo", "title": "🌦️ Météo"},
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
        for article in articles[:8]:
            nom_article = getattr(getattr(article, "ingredient", None), "nom", None) or f"Article #{article.id}"
            prefixe = "☑️" if article.achete else "☐"
            lignes.append(f"{prefixe} {html.escape(str(nom_article))}")
            boutons.append(
                {
                    "id": f"courses_toggle_article:{article.id}",
                    "title": f"{prefixe} {str(nom_article)[:28]}",
                }
            )

        if not lignes:
            lignes.append("La liste est vide pour le moment.")

        boutons.extend(
            [
                {"id": f"courses_confirmer:{liste.id}", "title": "✅ Confirmer"},
                {"id": "menu_retour", "title": "🏠 Menu principal"},
            ]
        )

        sauvegarder_etat_conversation(
            chat_id,
            {"type": "courses_confirmation", "liste_id": liste.id},
        )

        message = f"🛒 <b>{html.escape(liste.nom)}</b>\n\n" + "\n".join(lignes)

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
        corps="🍽️ <b>Repas du jour</b>\n\n" + "\n".join(lignes),
        boutons=[
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
    prochains_jalons = ContexteFamilleService()._prochains_jalons_oms(age_mois)
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
    elif callback_data == "action_jules":
        await _envoyer_resume_jules(chat_id)
    elif callback_data == "action_maison":
        await _envoyer_taches_maison(chat_id)
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
    if normalise in {"/courses", "/course"}:
        await _envoyer_courses_commande(chat_id)
        return True
    if normalise == "/jules":
        await _envoyer_resume_jules(chat_id)
        return True
    if normalise == "/maison":
        await _envoyer_taches_maison(chat_id)
        return True
    if normalise == "/budget":
        await _envoyer_resume_budget(chat_id)
        return True
    if normalise == "/meteo":
        await _envoyer_meteo_telegram(chat_id)
        return True
    if normalise.startswith("/ajout"):
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

    return False


async def _traiter_callback_planning(
    callback_data: str,
    callback_query_id: str,
    chat_id: str,
) -> None:
    """Traite les callbacks de planning: valider, modifier, régénérer.
    
    Phase 5.2: Webhook callbacks → endpoints de validation
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
    
    Phase 5.2: Webhook callbacks → endpoints de confirmation
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


@router.post("/webhook", response_model=MessageResponse)
@gerer_exception_api
async def recevoir_update_telegram(request: Request) -> MessageResponse:
    """Recoit un update Telegram et traite les commandes principales et callbacks.
    
    Gère:
    - callback_query (Phase 5.2: planning/courses workflow buttons)
    - message texte (commandes naturelles)
    """
    payload = await request.json()

    # Phase 5.2: Traitement des callbacks (boutons interactifs)
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

        # Dispatch aux handlers Phase 5.2
        if data.startswith("courses_toggle_article:"):
            await _traiter_callback_toggle_article(data, callback_query_id, chat_id)
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
    texte = str(message.get("text") or "").strip()
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
