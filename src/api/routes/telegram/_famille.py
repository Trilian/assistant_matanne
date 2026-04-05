"""Commandes Telegram liées au module Famille (jules, budget, weekend, rapport, météo)."""

from __future__ import annotations

import html
import logging
from datetime import date, timedelta

from ._helpers import _obtenir_url_app

logger = logging.getLogger(__name__)


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


async def _envoyer_projection_budget_telegram(chat_id: str) -> None:
    from src.services.ia_avancee import get_ia_avancee_service
    from src.services.integrations.telegram import envoyer_message_interactif

    try:
        prediction = get_ia_avancee_service().prevoir_depenses_fin_mois()
    except Exception as exc:
        logger.warning("Projection budget Telegram indisponible: %s", exc)
        prediction = None

    if prediction is None:
        await envoyer_message_interactif(
            destinataire=chat_id,
            corps=(
                "📈 <b>Projection budget</b>\n\n"
                "La projection IA n'est pas disponible pour le moment, mais le module Budget reste accessible."
            ),
            boutons=[
                {"url": _obtenir_url_app("/famille/budget"), "title": "💰 Ouvrir Budget"},
                {"id": "menu_famille", "title": "👶 Menu Famille"},
            ],
        )
        return

    depenses_actuelles = float(getattr(prediction, "depenses_actuelles", 0) or 0)
    prevision_fin_mois = float(getattr(prediction, "prevision_fin_mois", 0) or 0)
    budget_mensuel = float(getattr(prediction, "budget_mensuel", 0) or 0)
    ecart_prevu = float(getattr(prediction, "ecart_prevu", 0) or 0)
    tendance = html.escape(str(getattr(prediction, "tendance", "stable") or "stable"))

    lignes = [
        "📈 <b>Projection budget</b>",
        f"Dépensé à date : <b>{depenses_actuelles:.2f}€</b>",
        f"Fin de mois estimée : <b>{prevision_fin_mois:.2f}€</b>",
    ]
    if budget_mensuel > 0:
        lignes.append(f"🎯 Budget mensuel : <b>{budget_mensuel:.2f}€</b>")
        lignes.append(f"Écart prévu : <b>{ecart_prevu:+.2f}€</b> • tendance {tendance}")

    postes_vigilance = getattr(prediction, "postes_vigilance", []) or []
    if postes_vigilance:
        lignes.append("")
        lignes.append("Postes à surveiller :")
        for poste in postes_vigilance[:3]:
            if isinstance(poste, dict):
                nom = html.escape(str(poste.get("categorie") or poste.get("poste") or "Catégorie"))
                montant = poste.get("montant") or poste.get("prevision")
                if isinstance(montant, int | float):
                    lignes.append(f"• {nom} : {float(montant):.2f}€")
                else:
                    lignes.append(f"• {nom}")

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"url": _obtenir_url_app("/ia-avancee/prevision-depenses"), "title": "📊 Voir le détail"},
            {"id": "menu_famille", "title": "👶 Menu Famille"},
        ],
    )


async def _envoyer_recap_journee(chat_id: str) -> None:
    from sqlalchemy import func

    from src.core.db import obtenir_contexte_db
    from src.core.models.courses import ArticleCourses, ListeCourses
    from src.core.models.famille import ActiviteFamille
    from src.core.models.maison import TacheProjet
    from src.core.models.planning import Repas
    from src.services.integrations.telegram import envoyer_message_interactif

    aujourd_hui = date.today()
    repas_du_jour: list[str] = []
    activites_du_jour: list[str] = []
    courses_restantes = 0
    taches_a_suivre = 0

    try:
        with obtenir_contexte_db() as session:
            repas = (
                session.query(Repas)
                .filter(Repas.date_repas == aujourd_hui)
                .order_by(Repas.type_repas.asc())
                .all()
            )
            for item in repas[:3]:
                recette = getattr(item, "recette", None)
                nom = getattr(recette, "nom", None) or getattr(item, "notes", None) or "Repas prévu"
                repas_du_jour.append(f"{item.type_repas}: {nom}")

            activites = (
                session.query(ActiviteFamille)
                .filter(
                    ActiviteFamille.date_prevue == aujourd_hui,
                    ActiviteFamille.statut.in_(["planifié", "planifie", "à venir", "a venir"]),
                )
                .order_by(ActiviteFamille.heure_debut.asc())
                .limit(3)
                .all()
            )
            for activite in activites:
                heure = activite.heure_debut.strftime("%H:%M") if activite.heure_debut else "libre"
                activites_du_jour.append(f"{heure} — {activite.titre}")

            courses_restantes = int(
                (
                    session.query(func.count(ArticleCourses.id))
                    .join(ListeCourses, ListeCourses.id == ArticleCourses.liste_id)
                    .filter(
                        ArticleCourses.achete.is_(False),
                        ListeCourses.statut.in_(["active", "en_cours", "brouillon"]),
                    )
                    .scalar()
                )
                or 0
            )
            taches_a_suivre = int(
                (
                    session.query(func.count(TacheProjet.id))
                    .filter(
                        TacheProjet.statut.notin_(["termine", "terminé", "done"]),
                        TacheProjet.date_echeance.isnot(None),
                        TacheProjet.date_echeance <= aujourd_hui,
                    )
                    .scalar()
                )
                or 0
            )
    except Exception as exc:
        logger.warning("Récap journée Telegram partiel: %s", exc)

    lignes = [f"🗓️ <b>Récap du {aujourd_hui.strftime('%d/%m')}</b>"]
    if repas_du_jour:
        lignes.append("")
        lignes.append("🍽️ Repas du jour :")
        lignes.extend(f"• {html.escape(str(repas))}" for repas in repas_du_jour)
    if activites_du_jour:
        lignes.append("")
        lignes.append("🎯 Activités :")
        lignes.extend(f"• {html.escape(str(activite))}" for activite in activites_du_jour)

    lignes.append("")
    lignes.append(f"🛒 {courses_restantes} article(s) encore en attente")
    lignes.append(f"🧰 {taches_a_suivre} tâche(s) à surveiller")

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"url": _obtenir_url_app("/ma-journee"), "title": "📋 Ouvrir Ma journée"},
            {"url": _obtenir_url_app("/cuisine/courses"), "title": "🛒 Voir les courses"},
            {"id": "menu_principal", "title": "🏠 Menu principal"},
        ],
    )


async def _envoyer_meteo_telegram(chat_id: str) -> None:
    from src.services.famille.inter_module_meteo_activites import obtenir_service_meteo_activites_interaction
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
