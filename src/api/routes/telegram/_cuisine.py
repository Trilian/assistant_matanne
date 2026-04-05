"""Commandes Telegram liées au module Cuisine (planning, courses, inventaire, recettes, batch)."""

from __future__ import annotations

import html
import logging
from datetime import date, timedelta

from ._helpers import (
    _boutons_planning,
    _emoji_peremption,
    _obtenir_url_app,
    _resume_statut_article,
    _selectionner_liste_courses,
)

logger = logging.getLogger(__name__)


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
    import html as html_mod

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
    lignes.append(f"Session : <b>{html_mod.escape(str(getattr(cible, 'nom', 'Batch')))}</b>")
    if date_session:
        lignes.append(f"📅 {date_session.strftime('%d/%m/%Y')}")
    if heure:
        lignes.append(f"🕒 Début prévu : {heure.strftime('%H:%M')}")
    lignes.append(f"Statut : <b>{html_mod.escape(str(etat))}</b>")
    lignes.append(f"Recettes : {nb_recettes} • Étapes : {nb_etapes}")

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"url": _obtenir_url_app("/cuisine/batch-cooking"), "title": "🍱 Ouvrir batch cooking"},
            {"id": "menu_cuisine", "title": "🍽️ Menu Cuisine"},
        ],
    )


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


async def _envoyer_quoi_manger(chat_id: str) -> None:
    """Suggère des recettes réalisables avec le stock frigo actuel."""
    from src.core.db import obtenir_contexte_db
    from src.services.cuisine.inter_module_inventaire_planning import (
        obtenir_service_inventaire_planning_interaction,
    )
    from src.services.integrations.telegram import envoyer_message_interactif

    try:
        with obtenir_contexte_db() as session:
            resultat = obtenir_service_inventaire_planning_interaction().suggerer_recettes_selon_stock(
                limite=5, db=session,
            )
    except Exception:
        logger.exception("Erreur suggestion recettes depuis stock")
        resultat = {}

    recettes = resultat.get("recettes", [])

    if not recettes:
        await envoyer_message_interactif(
            destinataire=chat_id,
            corps=(
                "🍽️ <b>Quoi manger ?</b>\n\n"
                "Aucune recette trouvée pour le stock actuel.\n"
                "Remplis d'abord l'inventaire ou envoie une photo du frigo !"
            ),
            boutons=[
                {"url": _obtenir_url_app("/cuisine/inventaire"), "title": "🥫 Inventaire"},
                {"id": "menu_cuisine", "title": "🍽️ Menu Cuisine"},
            ],
        )
        return

    lignes = ["🍽️ <b>Quoi manger ?</b>", "Recettes possibles avec ton stock :", ""]
    for r in recettes[:5]:
        couverture = r.get("couverture_stock_pct", 0)
        nom = html.escape(str(r.get("nom", "Recette")))
        couverts = r.get("ingredients_couverts", 0)
        total = r.get("ingredients_total", 0)
        lignes.append(f"• <b>{nom}</b> — {couverture:.0f}% ({couverts}/{total} ingrédients)")

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"url": _obtenir_url_app("/cuisine/recettes"), "title": "📖 Voir les recettes"},
            {"url": _obtenir_url_app("/cuisine/planning"), "title": "📅 Planning"},
            {"id": "menu_cuisine", "title": "🍽️ Menu Cuisine"},
        ],
    )
