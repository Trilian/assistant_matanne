"""
Webhook WhatsApp â€” RÃ©ception des messages entrants Meta Cloud API.

Endpoints :
- GET  /api/v1/whatsapp/webhook : VÃ©rification Meta (challenge)
- POST /api/v1/whatsapp/webhook : RÃ©ception messages et rÃ©ponses boutons

Machine d'Ã©tat conversationnelle :
- "planning_valider" â†’ valide le planning proposÃ©
- "planning_modifier" â†’ demande quel repas modifier
- "planning_regenerer" â†’ relance la gÃ©nÃ©ration IA
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request

from src.api.schemas import MessageResponse
from src.api.utils import gerer_exception_api
from src.core.config import obtenir_parametres

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/whatsapp", tags=["WhatsApp"])


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VÃ‰RIFICATION WEBHOOK META
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get("/webhook")
async def verifier_webhook_whatsapp(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
) -> int | str:
    """Endpoint de vÃ©rification Meta.

    Meta envoie un GET avec hub.mode=subscribe, hub.verify_token et hub.challenge.
    On valide le token et retourne le challenge.
    """
    settings = obtenir_parametres()

    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("âœ… Webhook WhatsApp vÃ©rifiÃ© par Meta")
        return int(hub_challenge) if hub_challenge else 0

    logger.warning("âš ï¸ Tentative de vÃ©rification webhook invalide")
    raise HTTPException(status_code=403, detail="Token de vÃ©rification invalide")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# RÃ‰CEPTION MESSAGES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post("/webhook", response_model=MessageResponse)
@gerer_exception_api
async def recevoir_message_whatsapp(request: Request) -> MessageResponse:
    """ReÃ§oit les messages WhatsApp entrants (texte ou rÃ©ponse bouton).

    Traite les interactions du flux planning :
    - Bouton "planning_valider" â†’ valide le planning de la semaine
    - Bouton "planning_modifier" â†’ envoie les options de modification
    - Bouton "planning_regenerer" â†’ relance la suggestion IA
    - Texte libre â†’ interprÃ©tation IA basique
    """
    body = await request.json()

    # Extraire le message entrant
    entry = body.get("entry", [])
    if not entry:
        return MessageResponse(message="ok", id=0)

    changes = entry[0].get("changes", [])
    if not changes:
        return MessageResponse(message="ok", id=0)

    value = changes[0].get("value", {})
    messages = value.get("messages", [])
    if not messages:
        return MessageResponse(message="ok", id=0)

    msg = messages[0]
    sender = msg.get("from", "")
    msg_type = msg.get("type", "")

    logger.info(f"ðŸ“¨ Message WhatsApp reÃ§u de {sender[:6]}***, type: {msg_type}")

    # Traiter selon le type
    if msg_type == "interactive":
        button_reply = msg.get("interactive", {}).get("button_reply", {})
        action_id = button_reply.get("id", "")
        await _traiter_action_bouton(sender, action_id)
    elif msg_type == "text":
        texte = msg.get("text", {}).get("body", "")
        await _traiter_message_texte(sender, texte)

    return MessageResponse(message="ok", id=0)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MACHINE D'Ã‰TAT CONVERSATIONNELLE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


async def _traiter_action_bouton(sender: str, action_id: str) -> None:
    """Traite une rÃ©ponse bouton WhatsApp."""
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    if action_id == "planning_valider":
        # Valider le planning proposÃ© le plus rÃ©cent
        await _valider_planning_courant()
        await envoyer_message_whatsapp(sender, "âœ… Planning validÃ© ! Bon appÃ©tit cette semaine ðŸ½ï¸")

    elif action_id == "planning_modifier":
        await envoyer_message_whatsapp(
            sender,
            "âœï¸ Quel repas veux-tu modifier ?\n"
            "RÃ©ponds avec le format : *lundi soir* ou *mercredi midi*",
        )

    elif action_id == "planning_regenerer":
        await envoyer_message_whatsapp(
            sender,
            "ðŸ”„ RÃ©gÃ©nÃ©ration du planning en cours...\n"
            "Je te renvoie les nouvelles suggestions dans quelques instants.",
        )
        await _regenerer_planning_ia(sender)

    else:
        logger.warning(f"Action bouton inconnue : {action_id}")


async def _traiter_message_texte(sender: str, texte: str) -> None:
    """Traite un message texte libre."""
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    texte_lower = texte.lower().strip()

    # Commandes simples
    if texte_lower in ("menu", "planning", "semaine"):
        await _envoyer_planning_courant(sender)
    elif texte_lower in ("courses", "liste"):
        await _envoyer_liste_courses(sender)
    elif texte_lower in ("frigo", "stock", "inventaire"):
        await _envoyer_alerte_stocks(sender)
    # Nouvelles commandes Sprint 13
    elif texte_lower in ("jules", "bÃ©bÃ©", "bebe"):
        await _envoyer_resume_jules(sender)
    elif texte_lower.startswith("ajouter "):
        article = texte.strip()[8:].strip()
        await _ajouter_article_courses(sender, article)
    elif texte_lower == "budget":
        await _envoyer_resume_budget(sender)
    elif texte_lower in ("anniversaires", "anniversaire"):
        await _envoyer_anniversaires_proches(sender)
    elif texte_lower.startswith("recette "):
        nom = texte.strip()[8:].strip()
        await _envoyer_fiche_recette(sender, nom)
    elif texte_lower in ("tÃ¢ches", "taches", "tÃ¢che", "tache"):
        await _envoyer_taches_retard(sender)
    elif texte_lower in ("aide admin", "admin"):
        await _envoyer_aide_admin(sender)
    else:
        await envoyer_message_whatsapp(
            sender,
            "ðŸ¤– Commandes disponibles :\n"
            "â€¢ *menu* â€” Planning de la semaine\n"
            "â€¢ *courses* â€” Liste de courses en cours\n"
            "â€¢ *frigo* â€” Ã‰tat des stocks\n"
            "â€¢ *jules* â€” RÃ©sumÃ© de Jules\n"
            "â€¢ *ajouter [article]* â€” Ajouter Ã  la liste\n"
            "â€¢ *budget* â€” Budget mensuel\n"
            "â€¢ *anniversaires* â€” Prochains anniversaires\n"
            "â€¢ *recette [nom]* â€” Fiche recette\n"
            "â€¢ *tÃ¢ches* â€” TÃ¢ches maison en retard",
        )


async def _valider_planning_courant() -> None:
    """Valide le planning proposÃ© le plus rÃ©cent."""
    from src.core.db import obtenir_contexte_db
    from src.core.models.planning import Planning

    with obtenir_contexte_db() as session:
        planning = (
            session.query(Planning)
            .filter(Planning.statut == "propose")
            .order_by(Planning.date_creation.desc())
            .first()
        )
        if planning:
            planning.statut = "actif"
            session.commit()
            logger.info(f"âœ… Planning #{planning.id} validÃ© via WhatsApp")


async def _envoyer_planning_courant(sender: str) -> None:
    """Envoie le planning actif de la semaine."""
    from datetime import date, timedelta

    from src.core.db import obtenir_contexte_db
    from src.core.models.planning import Planning, Repas
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    with obtenir_contexte_db() as session:
        aujourd_hui = date.today()
        debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        fin_semaine = debut_semaine + timedelta(days=6)

        repas = (
            session.query(Repas)
            .join(Planning)
            .filter(
                Planning.statut == "actif",
                Repas.date_repas >= debut_semaine,
                Repas.date_repas <= fin_semaine,
            )
            .order_by(Repas.date_repas, Repas.type_repas)
            .all()
        )

        if not repas:
            await envoyer_message_whatsapp(sender, "ðŸ“… Aucun planning actif cette semaine.")
            return

        jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        lignes = []
        for r in repas:
            jour = jours[r.date_repas.weekday()]
            nom = r.recette.nom if r.recette else r.notes or "?"
            emoji = "ðŸŒ™" if r.type_repas == "diner" else "â˜€ï¸"
            lignes.append(f"{emoji} {jour} {r.type_repas} : {nom}")

        await envoyer_message_whatsapp(
            sender, f"ðŸ½ï¸ *Planning de la semaine*\n\n{''.join(chr(10) + l for l in lignes)}"
        )


async def _envoyer_liste_courses(sender: str) -> None:
    """Envoie la liste de courses active."""
    from src.core.db import obtenir_contexte_db
    from src.core.models.courses import ArticleCourses, ListeCourses
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    with obtenir_contexte_db() as session:
        liste = (
            session.query(ListeCourses)
            .filter(ListeCourses.archivee == False)  # noqa: E712
            .order_by(ListeCourses.date_creation.desc())
            .first()
        )

        if not liste:
            await envoyer_message_whatsapp(sender, "ðŸ›’ Aucune liste de courses en cours.")
            return

        articles = (
            session.query(ArticleCourses)
            .filter(
                ArticleCourses.liste_id == liste.id,
                ArticleCourses.achete == False,  # noqa: E712
            )
            .all()
        )

        lignes = [f"â€¢ {a.ingredient.nom if a.ingredient else '?'}" for a in articles[:20]]
        msg = f"ðŸ›’ *Liste de courses* ({len(articles)} articles)\n\n{''.join(chr(10) + l for l in lignes)}"

        if len(articles) > 20:
            msg += f"\n\n... et {len(articles) - 20} autres"

        await envoyer_message_whatsapp(sender, msg)


async def _envoyer_alerte_stocks(sender: str) -> None:
    """Envoie l'Ã©tat des stocks bas + pÃ©remptions proches."""
    from datetime import date, timedelta

    from src.core.db import obtenir_contexte_db
    from src.core.models import ArticleInventaire
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    with obtenir_contexte_db() as session:
        aujourd_hui = date.today()
        seuil = aujourd_hui + timedelta(days=3)

        stocks_bas = (
            session.query(ArticleInventaire)
            .filter(ArticleInventaire.quantite <= ArticleInventaire.quantite_min)
            .all()
        )

        peremptions = (
            session.query(ArticleInventaire)
            .filter(
                ArticleInventaire.date_peremption.isnot(None),
                ArticleInventaire.date_peremption <= seuil,
            )
            .all()
        )

        lignes = []
        if stocks_bas:
            lignes.append("ðŸ“‰ *Stocks bas :*")
            for a in stocks_bas[:10]:
                lignes.append(f"  â€¢ {a.nom} ({a.quantite}/{a.quantite_min})")
        if peremptions:
            lignes.append("\nâš ï¸ *PÃ©remption proche :*")
            for a in peremptions[:10]:
                lignes.append(f"  â€¢ {a.nom} â€” {a.date_peremption}")

        if not lignes:
            await envoyer_message_whatsapp(sender, "âœ… Tous les stocks sont OK !")
        else:
            await envoyer_message_whatsapp(sender, "\n".join(lignes))


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# NOUVEAUX HANDLERS â€” SPRINT 13
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


async def _regenerer_planning_ia(sender: str) -> None:
    """RÃ©gÃ©nÃ¨re le planning IA et envoie le rÃ©sultat via WhatsApp."""
    import asyncio
    from datetime import date, timedelta

    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    try:
        from src.services.cuisine import obtenir_planning_service

        service = obtenir_planning_service()
        aujourd_hui = date.today()
        # DÃ©but de la semaine courante (lundi)
        debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())

        # ExÃ©cution synchrone dans un thread dÃ©diÃ© pour ne pas bloquer la boucle async
        loop = asyncio.get_event_loop()
        planning = await loop.run_in_executor(
            None,
            lambda: service.generer_planning_ia(debut_semaine),
        )

        if not planning:
            await envoyer_message_whatsapp(
                sender,
                "âŒ Impossible de gÃ©nÃ©rer un planning. RÃ©essaye dans quelques instants.",
            )
            return

        # Formater le planning gÃ©nÃ©rÃ©
        jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        lignes = []
        repas = sorted(getattr(planning, "repas", []) or [], key=lambda r: (r.date_repas, r.type_repas))
        for r in repas:
            jour = jours[r.date_repas.weekday()]
            nom = r.recette.nom if getattr(r, "recette", None) else (r.notes or "?")
            emoji = "ðŸŒ™" if r.type_repas == "diner" else "â˜€ï¸"
            lignes.append(f"{emoji} {jour} : {nom}")

        if not lignes:
            await envoyer_message_whatsapp(sender, "âœ… Nouveau planning gÃ©nÃ©rÃ© (vide). Ouvre l'app pour voir.")
            return

        msg = f"âœ¨ *Nouveau planning IA*\n\n{''.join(chr(10) + l for l in lignes)}\n\nâœ… Valide ou ðŸ“ modifie via l'application."
        await envoyer_message_whatsapp(sender, msg)
        logger.info("âœ… Planning IA rÃ©gÃ©nÃ©rÃ© et envoyÃ© via WhatsApp Ã  %s***", sender[:6])

    except Exception:
        logger.exception("Erreur rÃ©gÃ©nÃ©ration planning IA WhatsApp")
        await envoyer_message_whatsapp(
            sender,
            "âŒ Erreur lors de la gÃ©nÃ©ration du planning. Essaie depuis l'application.",
        )


async def _envoyer_resume_jules(sender: str) -> None:
    """Envoie un rÃ©sumÃ© des activitÃ©s, repas et jalons rÃ©cents de Jules."""
    from datetime import date, timedelta

    from src.core.db import obtenir_contexte_db
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    with obtenir_contexte_db() as session:
        hier = date.today() - timedelta(days=1)
        semaine_passee = date.today() - timedelta(days=7)
        lignes: list[str] = []

        try:
            from src.core.models.famille import ActiviteFamille, JalonDeveloppement

            activites = (
                session.query(ActiviteFamille)
                .filter(ActiviteFamille.date_activite >= semaine_passee)
                .order_by(ActiviteFamille.date_activite.desc())
                .limit(5)
                .all()
            )
            if activites:
                lignes.append("ðŸŽ® *ActivitÃ©s (7 derniers jours) :*")
                for a in activites:
                    lignes.append(f"  â€¢ {a.nom} ({a.date_activite})")

            jalons = (
                session.query(JalonDeveloppement)
                .order_by(JalonDeveloppement.date_atteinte.desc())
                .limit(3)
                .all()
            )
            if jalons:
                lignes.append("\nðŸŒŸ *Derniers jalons :*")
                for j in jalons:
                    lignes.append(f"  â€¢ {j.titre} â€” {j.date_atteinte}")
        except Exception:
            logger.debug("RÃ©sumÃ© Jules : impossible de charger activitÃ©s/jalons")

        try:
            from src.core.models.planning import Repas
            repas = (
                session.query(Repas)
                .filter(Repas.date_repas >= hier)
                .order_by(Repas.date_repas)
                .limit(4)
                .all()
            )
            if repas:
                lignes.append("\nðŸ¼ *Repas Ã  venir :*")
                for r in repas:
                    nom = r.recette.nom if getattr(r, "recette", None) else (r.notes or "?")
                    lignes.append(f"  â€¢ {r.date_repas} {r.type_repas} : {nom}")
        except Exception:
            logger.debug("RÃ©sumÃ© Jules : impossible de charger les repas")

        if not lignes:
            await envoyer_message_whatsapp(sender, "ðŸ‘¶ Jules : aucune activitÃ© rÃ©cente enregistrÃ©e.")
        else:
            await envoyer_message_whatsapp(sender, "ðŸ‘¶ *RÃ©sumÃ© Jules*\n\n" + "\n".join(lignes))


async def _ajouter_article_courses(sender: str, nom_article: str) -> None:
    """Ajoute un article Ã  la liste de courses active."""
    from src.core.db import obtenir_contexte_db
    from src.core.validation import SanitiseurDonnees
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    nom_propre = SanitiseurDonnees.nettoyer_texte(nom_article)[:100]
    if not nom_propre:
        await envoyer_message_whatsapp(sender, "âŒ Nom d'article invalide.")
        return

    with obtenir_contexte_db() as session:
        try:
            from src.core.models.courses import ArticleCourses, ListeCourses

            liste = (
                session.query(ListeCourses)
                .filter(ListeCourses.archivee == False)  # noqa: E712
                .order_by(ListeCourses.date_creation.desc())
                .first()
            )

            if not liste:
                # CrÃ©er une nouvelle liste si aucune n'existe
                from datetime import date
                liste = ListeCourses(
                    nom=f"Courses {date.today().strftime('%d/%m/%Y')}",
                    archivee=False,
                )
                session.add(liste)
                session.flush()

            article = ArticleCourses(
                liste_id=liste.id,
                nom=nom_propre,
                achete=False,
            )
            session.add(article)
            session.commit()
            await envoyer_message_whatsapp(
                sender, f"âœ… *{nom_propre}* ajoutÃ© Ã  la liste de courses !"
            )
            logger.info("Article '%s' ajoutÃ© via WhatsApp", nom_propre)
        except Exception:
            logger.exception("Erreur ajout article courses via WhatsApp")
            await envoyer_message_whatsapp(sender, "âŒ Erreur lors de l'ajout. RÃ©essaye.")


async def _envoyer_resume_budget(sender: str) -> None:
    """Envoie le rÃ©sumÃ© du budget mensuel en cours."""
    from datetime import date

    from src.core.db import obtenir_contexte_db
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    with obtenir_contexte_db() as session:
        try:
            from sqlalchemy import text

            mois_debut = date.today().replace(day=1)
            result = session.execute(
                text(
                    "SELECT COALESCE(SUM(montant), 0) FROM depenses_familles"
                    " WHERE date_depense >= :debut"
                ),
                {"debut": mois_debut},
            )
            total_depense = float(result.scalar() or 0)

            # Essayer de rÃ©cupÃ©rer le budget prÃ©vu
            budget_prevu_result = session.execute(
                text(
                    "SELECT valeur FROM preferences_utilisateurs"
                    " WHERE user_id IS NOT NULL LIMIT 1"
                ),
            )
            budget_prevu = 2000.0  # Valeur par dÃ©faut si non configurÃ©e

            ecart = total_depense - budget_prevu
            pourcentage = (total_depense / budget_prevu * 100) if budget_prevu > 0 else 0
            emoji_jauge = "ðŸŸ¢" if pourcentage <= 75 else ("ðŸŸ¡" if pourcentage <= 95 else "ðŸ”´")

            msg = (
                f"ðŸ’° *Budget {mois_debut.strftime('%B %Y')}*\n\n"
                f"{emoji_jauge} DÃ©pensÃ© : {total_depense:.2f} â‚¬ / {budget_prevu:.2f} â‚¬\n"
                f"ðŸ“Š Utilisation : {pourcentage:.0f}%\n"
                f"{'ðŸ”´ DÃ©passement' if ecart > 0 else 'âœ… Sous budget'} : "
                f"{'+ ' if ecart > 0 else ''}{ecart:.2f} â‚¬"
            )
            await envoyer_message_whatsapp(sender, msg)
        except Exception:
            logger.debug("Budget WhatsApp : table depenses_familles indisponible")
            await envoyer_message_whatsapp(sender, "ðŸ’° Budget : donnÃ©es indisponibles pour l'instant.")


async def _envoyer_anniversaires_proches(sender: str) -> None:
    """Envoie les anniversaires dans les 30 prochains jours."""
    from datetime import date, timedelta

    from src.core.db import obtenir_contexte_db
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    with obtenir_contexte_db() as session:
        try:
            from sqlalchemy import text

            aujourd_hui = date.today()
            dans_30j = aujourd_hui + timedelta(days=30)

            # Chercher dans plusieurs tables potentielles
            rows = session.execute(
                text(
                    "SELECT nom, date_naissance FROM membres_famille"
                    " WHERE date_naissance IS NOT NULL"
                    " UNION ALL"
                    " SELECT nom, date_naissance FROM contacts_famille"
                    " WHERE date_naissance IS NOT NULL"
                )
            ).fetchall()

            anniversaires: list[tuple[int, str, str]] = []
            for nom, date_naissance in rows:
                try:
                    # Calculer le prochain anniversaire cette annÃ©e
                    prochain = date_naissance.replace(year=aujourd_hui.year)
                    if prochain < aujourd_hui:
                        prochain = prochain.replace(year=aujourd_hui.year + 1)
                    jours_restants = (prochain - aujourd_hui).days
                    if 0 <= jours_restants <= 30:
                        anniversaires.append((jours_restants, nom, prochain.strftime("%d/%m")))
                except Exception:
                    pass

            anniversaires.sort(key=lambda x: x[0])

            if not anniversaires:
                await envoyer_message_whatsapp(sender, "ðŸŽ‚ Aucun anniversaire dans les 30 prochains jours.")
            else:
                lignes = [f"â€¢ {nom} â€” {date_fmt} (dans {j}j)" for j, nom, date_fmt in anniversaires]
                await envoyer_message_whatsapp(
                    sender, "ðŸŽ‚ *Anniversaires Ã  venir :*\n\n" + "\n".join(lignes)
                )
        except Exception:
            logger.debug("Anniversaires WhatsApp : donnÃ©es indisponibles")
            await envoyer_message_whatsapp(sender, "ðŸŽ‚ Anniversaires : donnÃ©es indisponibles.")


async def _envoyer_fiche_recette(sender: str, nom_recette: str) -> None:
    """Envoie la fiche d'une recette avec ses ingrÃ©dients."""
    from src.core.db import obtenir_contexte_db
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    with obtenir_contexte_db() as session:
        try:
            from src.core.models.recettes import Ingredient, Recette, RecetteIngredient

            recette = (
                session.query(Recette)
                .filter(Recette.nom.ilike(f"%{nom_recette}%"))
                .first()
            )

            if not recette:
                await envoyer_message_whatsapp(sender, f"âŒ Recette *{nom_recette}* introuvable.")
                return

            lignes = [
                f"ðŸ³ *{recette.nom}*",
                f"â±ï¸ Temps : {recette.temps_preparation or '?'} min",
                f"ðŸ‘¥ Portions : {recette.nb_portions or '?'}",
                "\nðŸ§¾ *IngrÃ©dients :*",
            ]

            for ri in (recette.ingredients or [])[:12]:
                qte = f"{ri.quantite} {ri.unite}" if ri.quantite else ""
                nom_ing = ri.ingredient.nom if ri.ingredient else "?"
                lignes.append(f"  â€¢ {nom_ing} {qte}".strip())

            await envoyer_message_whatsapp(sender, "\n".join(lignes))
        except Exception:
            logger.debug("Fiche recette WhatsApp : erreur")
            await envoyer_message_whatsapp(sender, f"âŒ Recette introuvable : {nom_recette}")


async def _envoyer_taches_retard(sender: str) -> None:
    """Envoie les tÃ¢ches maison en retard."""
    from datetime import date

    from src.core.db import obtenir_contexte_db
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    with obtenir_contexte_db() as session:
        try:
            from sqlalchemy import text

            today = date.today()
            rows = session.execute(
                text(
                    "SELECT titre, date_echeance FROM taches_maison"
                    " WHERE statut NOT IN ('termine', 'annule')"
                    " AND date_echeance < :today"
                    " ORDER BY date_echeance ASC LIMIT 10"
                ),
                {"today": today},
            ).fetchall()

            if not rows:
                await envoyer_message_whatsapp(sender, "âœ… Aucune tÃ¢che maison en retard !")
            else:
                lignes = [f"â€¢ {titre} (Ã©chÃ©ance: {echeance})" for titre, echeance in rows]
                await envoyer_message_whatsapp(
                    sender, f"ðŸšï¸ *TÃ¢ches en retard ({len(rows)}) :*\n\n" + "\n".join(lignes)
                )
        except Exception:
            logger.debug("TÃ¢ches retard WhatsApp : table indisponible")
            await envoyer_message_whatsapp(sender, "ðŸšï¸ TÃ¢ches : donnÃ©es indisponibles.")


async def _envoyer_aide_admin(sender: str) -> None:
    """Envoie la liste des commandes admin (accÃ¨s limitÃ©)."""
    from src.core.config import obtenir_parametres
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    settings = obtenir_parametres()
    # VÃ©rifier que l'expÃ©diteur est le numÃ©ro admin configurÃ©
    numero_admin = getattr(settings, "WHATSAPP_USER_NUMBER", None)
    if numero_admin and sender != numero_admin:
        logger.warning("Tentative d'accÃ¨s aide admin depuis numÃ©ro non autorisÃ© : %s***", sender[:6])
        await envoyer_message_whatsapp(sender, "âŒ AccÃ¨s refusÃ©.")
        return

    await envoyer_message_whatsapp(
        sender,
        "ðŸ”§ *Commandes admin :*\n\n"
        "â€¢ *menu* / *planning* â€” Planning semaine\n"
        "â€¢ *courses* â€” Liste de courses\n"
        "â€¢ *frigo* â€” Alertes stocks\n"
        "â€¢ *jules* â€” RÃ©sumÃ© Jules\n"
        "â€¢ *ajouter [article]* â€” Ajouter Ã  la liste\n"
        "â€¢ *budget* â€” Budget mensuel\n"
        "â€¢ *anniversaires* â€” Prochains anniversaires\n"
        "â€¢ *recette [nom]* â€” Fiche recette\n"
        "â€¢ *tÃ¢ches* â€” TÃ¢ches en retard\n"
        "â€¢ *aide admin* â€” Cette liste",
    )

