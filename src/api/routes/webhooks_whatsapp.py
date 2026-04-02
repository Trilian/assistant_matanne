"""
Webhook WhatsApp pour la reception des messages entrants Meta Cloud API.

Endpoints:
- GET  /api/v1/whatsapp/webhook : verification Meta (challenge)
- POST /api/v1/whatsapp/webhook : reception messages et reponses boutons

Machine d'etat conversationnelle:
- "planning_valider" : valide le planning propose
- "planning_modifier" : demande quel repas modifier
- "planning_regenerer" : relance la generation IA
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request

from src.api.schemas import MessageResponse
from src.api.utils import gerer_exception_api
from src.core.config import obtenir_parametres

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/whatsapp", tags=["WhatsApp"])


# ============================================================
# VERIFICATION WEBHOOK META
# ============================================================


@router.get("/webhook")
async def verifier_webhook_whatsapp(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
) -> int | str:
    """Endpoint de verification Meta.

    Meta envoie un GET avec hub.mode=subscribe, hub.verify_token et hub.challenge.
    On valide le token et retourne le challenge.
    """
    settings = obtenir_parametres()

    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook WhatsApp verifie par Meta")
        return int(hub_challenge) if hub_challenge else 0

    logger.warning("Tentative de verification webhook invalide")
    raise HTTPException(status_code=403, detail="Token de verification invalide")


# ============================================================
# RECEPTION MESSAGES
# ============================================================


@router.post("/webhook", response_model=MessageResponse)
@gerer_exception_api
async def recevoir_message_whatsapp(request: Request) -> MessageResponse:
    """Recoit les messages WhatsApp entrants (texte ou reponse bouton).

    Traite les interactions du flux planning :
    - Bouton "planning_valider" : valide le planning de la semaine
    - Bouton "planning_modifier" : envoie les options de modification
    - Bouton "planning_regenerer" : relance la suggestion IA
    - Texte libre : interpretation IA basique
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

    logger.info(f"Message WhatsApp recu de {sender[:6]}***, type: {msg_type}")

    # Traiter selon le type
    if msg_type == "interactive":
        interactive = msg.get("interactive", {})
        # Boutons classiques OU r�ponses de liste interactive
        reply = interactive.get("button_reply") or interactive.get("list_reply") or {}
        action_id = reply.get("id", "")
        await _traiter_action_bouton(sender, action_id)
    elif msg_type == "text":
        texte = msg.get("text", {}).get("body", "")
        await _traiter_message_texte(sender, texte)

    return MessageResponse(message="ok", id=0)


# ============================================================
# MACHINE D'ETAT CONVERSATIONNELLE
# ============================================================


async def _traiter_action_bouton(sender: str, action_id: str) -> None:
    """Traite une reponse bouton WhatsApp."""
    from src.services.integrations.whatsapp import (
        effacer_etat_conversation,
        envoyer_message_whatsapp,
        sauvegarder_etat_conversation,
    )

    if action_id == "planning_valider":
        # Valider le planning propos� le plus r�cent
        await _valider_planning_courant()
        await envoyer_message_whatsapp(sender, "[OK] Planning valide ! Bon appetit cette semaine.")

    elif action_id == "planning_modifier":
        sauvegarder_etat_conversation(
            sender,
            {
                "etat": "attente_creneau_modification",
                "source": "planning_modifier",
            },
        )
        await envoyer_message_whatsapp(
            sender,
            "Quel repas veux-tu modifier ?\n"
            "Reponds avec le format : *lundi soir* ou *mercredi midi*",
        )

    elif action_id == "planning_regenerer":
        effacer_etat_conversation(sender)
        await envoyer_message_whatsapp(
            sender,
            "Regeneration du planning en cours...\n"
            "Je te renvoie les nouvelles suggestions dans quelques instants.",
        )
        await _regenerer_planning_ia(sender)
    # --- Boutons digest matinal ---
    elif action_id == "digest_courses":
        await _envoyer_liste_courses(sender)

    elif action_id == "digest_detail":
        await _envoyer_detail_journee(sender)

    # --- Boutons actions courses ---
    elif action_id == "courses_tout_acheter":
        await _marquer_courses_achetees(sender)

    elif action_id == "courses_partager":
        await _partager_liste_courses(sender)

    # --- Boutons entretien ---
    elif action_id == "entretien_fait":
        await _marquer_entretien_fait(sender)

    # --- R�ponses de liste interactive ---
    elif action_id.startswith("cmd_"):
        commande = action_id[4:]
        await _traiter_message_texte(sender, commande)
    else:
        logger.warning(f"Action bouton inconnue : {action_id}")


async def _traiter_message_texte(sender: str, texte: str) -> None:
    """Traite un message texte libre."""
    from src.services.integrations.whatsapp import (
        charger_etat_conversation,
        effacer_etat_conversation,
        envoyer_message_whatsapp,
        sauvegarder_etat_conversation,
    )

    texte_lower = texte.lower().strip()

    # Machine d'�tat persistante multi-turn 
    etat = charger_etat_conversation(sender)
    if etat and etat.get("etat") == "attente_creneau_modification":
        if any(jour in texte_lower for jour in ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")) and any(
            repas in texte_lower for repas in ("midi", "soir", "dejeuner", "diner", "d�jeuner", "d�ner")
        ):
            sauvegarder_etat_conversation(
                sender,
                {
                    "etat": "attente_detail_modification",
                    "creneau": texte.strip(),
                    "source": "planning_modifier",
                },
            )
            await envoyer_message_whatsapp(
                sender,
                f"Parfait, j'ai not� *{texte.strip()}*.\n"
                "Quel changement souhaites-tu ? (ex: 'remplacer par p�tes carbonara')",
            )
            return

        await envoyer_message_whatsapp(
            sender,
            "Je n'ai pas reconnu le cr�neau. R�ponds par exemple *lundi soir* ou *mercredi midi*.",
        )
        return

    if etat and etat.get("etat") == "attente_detail_modification":
        creneau = str(etat.get("creneau", "ce cr�neau"))
        effacer_etat_conversation(sender)
        await envoyer_message_whatsapp(
            sender,
            f"? Demande de modification enregistr�e pour *{creneau}* :\n"
            f"_{texte.strip()}_\n\n"
            "Je vais r�g�n�rer une proposition dans l'application.",
        )
        return

    # Commandes simples
    if texte_lower in ("menu", "planning", "semaine"):
        await _envoyer_planning_courant(sender)
    elif texte_lower in ("ce soir", "diner", "d�ner"):
        await _envoyer_suggestion_ce_soir(sender)
    elif texte_lower in ("courses", "liste"):
        await _envoyer_liste_courses(sender)
    elif texte_lower in ("frigo", "stock", "inventaire"):
        await _envoyer_alerte_stocks(sender)
    # Nouvelles commandes notifications
    elif texte_lower in ("jules", "b�b�", "bebe"):
        await _envoyer_resume_jules(sender)
    elif texte_lower.startswith("ajouter "):
        article = texte.strip()[8:].strip()
        await _ajouter_article_courses_nlp(sender, article)
    elif texte_lower == "budget":
        await _envoyer_resume_budget(sender)
    elif texte_lower in ("anniversaires", "anniversaire"):
        await _envoyer_anniversaires_proches(sender)
    elif texte_lower.startswith("recette "):
        nom = texte.strip()[8:].strip()
        await _envoyer_fiche_recette(sender, nom)
    elif texte_lower in ("t�ches", "taches", "t�che", "tache"):
        await _envoyer_taches_retard(sender)
    elif texte_lower in ("aide admin", "admin"):
        await _envoyer_aide_admin(sender)
    # Nouvelles commandes Phase 5
    elif texte_lower in ("m�t�o", "meteo", "temps"):
        await _envoyer_meteo(sender)
    elif texte_lower in ("jardin", "plantes", "potager"):
        await _envoyer_resume_jardin(sender)
    elif texte_lower in ("�nergie", "energie", "conso"):
        await _envoyer_resume_energie(sender)
    elif texte_lower in ("entretien", "maintenance"):
        await _envoyer_entretien_urgent(sender)
    elif texte_lower in ("aide", "help", "?"):
        effacer_etat_conversation(sender)
        await envoyer_message_whatsapp(
            sender,
            "?? Commandes disponibles :\n"
            "- *menu* : Planning de la semaine\n"
            "- *ce soir* : Suggestion rapide repas\n"
            "- *courses* : Liste de courses en cours\n"
            "- *frigo* : Etat des stocks\n"
            "- *jules* : Resume de Jules\n"
            "- *budget* : Budget mensuel\n"
            "- *recette [nom]* : Fiche recette\n"
            "- *aide* : Cette liste\n\n"
            "?? Tu peux aussi �crire en langage naturel :\n"
            "- _ajoute du lait et des oeufs_\n"
            "- _combien j'ai d�pens� ce mois ?_\n"
            "- _qu'est-ce qu'on mange ce soir ?_",
        )
    else:
        # NLP Mistral: NLP Mistral � interpr�ter les commandes en langage naturel
        await _traiter_commande_nlp(sender, texte)


async def _valider_planning_courant() -> None:
    """Valide le planning propos� le plus r�cent."""
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
            logger.info(f"? Planning #{planning.id} valid� via WhatsApp")


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
            await envoyer_message_whatsapp(sender, "?? Aucun planning actif cette semaine.")
            return

        jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        lignes = []
        for r in repas:
            jour = jours[r.date_repas.weekday()]
            nom = r.recette.nom if r.recette else r.notes or "?"
            emoji = "??" if r.type_repas == "diner" else "??"
            lignes.append(f"{emoji} {jour} {r.type_repas} : {nom}")

        await envoyer_message_whatsapp(
            sender, f"??? *Planning de la semaine*\n\n{''.join(chr(10) + l for l in lignes)}"
        )


async def _envoyer_suggestion_ce_soir(sender: str) -> None:
    """Envoie une suggestion rapide de repas pour ce soir."""
    from datetime import date

    from src.core.db import obtenir_contexte_db
    from src.core.models.planning import Repas
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    with obtenir_contexte_db() as session:
        repas = (
            session.query(Repas)
            .filter(Repas.date_repas == date.today(), Repas.type_repas == "diner")
            .first()
        )

        if repas:
            nom = repas.recette.nom if getattr(repas, "recette", None) else (repas.notes or "Repas du soir")
            await envoyer_message_whatsapp(sender, f"??? Ce soir: *{nom}*.")
            return

    await envoyer_message_whatsapp(
        sender,
        "??? Rien de planifi� pour ce soir. Suggestion rapide: omelette + salade + fruit.",
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
            await envoyer_message_whatsapp(sender, "?? Aucune liste de courses en cours.")
            return

        articles = (
            session.query(ArticleCourses)
            .filter(
                ArticleCourses.liste_id == liste.id,
                ArticleCourses.achete == False,  # noqa: E712
            )
            .all()
        )

        lignes = [f"� {a.ingredient.nom if a.ingredient else '?'}" for a in articles[:20]]
        msg = f"?? *Liste de courses* ({len(articles)} articles)\n\n{''.join(chr(10) + l for l in lignes)}"

        if len(articles) > 20:
            msg += f"\n\n... et {len(articles) - 20} autres"

        from src.services.integrations.whatsapp import envoyer_message_interactif

        await envoyer_message_interactif(
            destinataire=sender,
            corps=msg,
            boutons=[
                {"id": "courses_tout_acheter", "title": "Tout achet�"},
                {"id": "courses_partager", "title": "Partager"},
            ],
        )


async def _envoyer_alerte_stocks(sender: str) -> None:
    """Envoie l'�tat des stocks bas + p�remptions proches."""
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
            lignes.append("?? *Stocks bas :*")
            for a in stocks_bas[:10]:
                lignes.append(f"  � {a.nom} ({a.quantite}/{a.quantite_min})")
        if peremptions:
            lignes.append("\n?? *P�remption proche :*")
            for a in peremptions[:10]:
                lignes.append(f"  � {a.nom} � {a.date_peremption}")

        if not lignes:
            await envoyer_message_whatsapp(sender, "? Tous les stocks sont OK !")
        else:
            await envoyer_message_whatsapp(sender, "\n".join(lignes))


# -----------------------------------------------------------
# NOUVEAUX HANDLERS NOTIFICATIONS
# -----------------------------------------------------------


async def _regenerer_planning_ia(sender: str) -> None:
    """R�g�n�re le planning IA et envoie le r�sultat via WhatsApp."""
    import asyncio
    from datetime import date, timedelta

    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    try:
        from src.services.cuisine import obtenir_planning_service

        service = obtenir_planning_service()
        aujourd_hui = date.today()
        # D�but de la semaine courante (lundi)
        debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())

        # Ex�cution synchrone dans un thread d�di� pour ne pas bloquer la boucle async
        loop = asyncio.get_event_loop()
        planning = await loop.run_in_executor(
            None,
            lambda: service.generer_planning_ia(debut_semaine),
        )

        if not planning:
            await envoyer_message_whatsapp(
                sender,
                "? Impossible de g�n�rer un planning. R�essaye dans quelques instants.",
            )
            return

        # Formater le planning g�n�r�
        jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        lignes = []
        repas = sorted(getattr(planning, "repas", []) or [], key=lambda r: (r.date_repas, r.type_repas))
        for r in repas:
            jour = jours[r.date_repas.weekday()]
            nom = r.recette.nom if getattr(r, "recette", None) else (r.notes or "?")
            emoji = "??" if r.type_repas == "diner" else "??"
            lignes.append(f"{emoji} {jour} : {nom}")

        if not lignes:
            await envoyer_message_whatsapp(sender, "? Nouveau planning g�n�r� (vide). Ouvre l'app pour voir.")
            return

        msg = f"? *Nouveau planning IA*\n\n{''.join(chr(10) + l for l in lignes)}\n\n? Valide ou ?? modifie via l'application."
        await envoyer_message_whatsapp(sender, msg)
        logger.info("? Planning IA r�g�n�r� et envoy� via WhatsApp � %s***", sender[:6])

    except Exception:
        logger.exception("Erreur r�g�n�ration planning IA WhatsApp")
        await envoyer_message_whatsapp(
            sender,
            "? Erreur lors de la g�n�ration du planning. Essaie depuis l'application.",
        )


async def _envoyer_resume_jules(sender: str) -> None:
    """Envoie un r�sum� des activit�s, repas et jalons r�cents de Jules."""
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
                lignes.append("?? *Activit�s (7 derniers jours) :*")
                for a in activites:
                    lignes.append(f"  � {a.nom} ({a.date_activite})")

            jalons = (
                session.query(JalonDeveloppement)
                .order_by(JalonDeveloppement.date_atteinte.desc())
                .limit(3)
                .all()
            )
            if jalons:
                lignes.append("\n?? *Derniers jalons :*")
                for j in jalons:
                    lignes.append(f"  � {j.titre} � {j.date_atteinte}")
        except Exception:
            logger.debug("R�sum� Jules : impossible de charger activit�s/jalons")

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
                lignes.append("\n?? *Repas � venir :*")
                for r in repas:
                    nom = r.recette.nom if getattr(r, "recette", None) else (r.notes or "?")
                    lignes.append(f"  � {r.date_repas} {r.type_repas} : {nom}")
        except Exception:
            logger.debug("R�sum� Jules : impossible de charger les repas")

        if not lignes:
            await envoyer_message_whatsapp(sender, "?? Jules : aucune activit� r�cente enregistr�e.")
        else:
            await envoyer_message_whatsapp(sender, "?? *R�sum� Jules*\n\n" + "\n".join(lignes))


async def _ajouter_article_courses_legacy(sender: str, nom_article: str) -> None:
    """Ajoute un article � la liste de courses active (wrapper legacy)."""
    from src.core.validation import SanitiseurDonnees

    nom_propre = SanitiseurDonnees.nettoyer_texte(nom_article)[:100]
    if not nom_propre:
        from src.services.integrations.whatsapp import envoyer_message_whatsapp
        await envoyer_message_whatsapp(sender, "? Nom d'article invalide.")
        return

    # D�l�gue � la nouvelle impl�mentation NLP avec mod�le Ingredient
    await _ajouter_article_courses_nlp(sender, nom_propre)


async def _envoyer_resume_budget(sender: str) -> None:
    """Envoie le r�sum� du budget mensuel en cours."""
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

            # Essayer de r�cup�rer le budget pr�vu
            budget_prevu_result = session.execute(
                text(
                    "SELECT valeur FROM preferences_utilisateurs"
                    " WHERE user_id IS NOT NULL LIMIT 1"
                ),
            )
            budget_prevu = 2000.0  # Valeur par d�faut si non configur�e

            ecart = total_depense - budget_prevu
            pourcentage = (total_depense / budget_prevu * 100) if budget_prevu > 0 else 0
            emoji_jauge = "??" if pourcentage <= 75 else ("??" if pourcentage <= 95 else "??")

            msg = (
                f"?? *Budget {mois_debut.strftime('%B %Y')}*\n\n"
                f"{emoji_jauge} D�pens� : {total_depense:.2f} � / {budget_prevu:.2f} �\n"
                f"?? Utilisation : {pourcentage:.0f}%\n"
                f"{'?? D�passement' if ecart > 0 else '? Sous budget'} : "
                f"{'+ ' if ecart > 0 else ''}{ecart:.2f} �"
            )
            await envoyer_message_whatsapp(sender, msg)
        except Exception:
            logger.debug("Budget WhatsApp : table depenses_familles indisponible")
            await envoyer_message_whatsapp(sender, "?? Budget : donn�es indisponibles pour l'instant.")


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
                    # Calculer le prochain anniversaire cette ann�e
                    prochain = date_naissance.replace(year=aujourd_hui.year)
                    if prochain < aujourd_hui:
                        prochain = prochain.replace(year=aujourd_hui.year + 1)
                    jours_restants = (prochain - aujourd_hui).days
                    if 0 <= jours_restants <= 30:
                        anniversaires.append((jours_restants, nom, prochain.strftime("%d/%m")))
                except Exception as e:
                    logger.warning("Erreur calcul anniversaire pour %s: %s", nom, e)

            anniversaires.sort(key=lambda x: x[0])

            if not anniversaires:
                await envoyer_message_whatsapp(sender, "?? Aucun anniversaire dans les 30 prochains jours.")
            else:
                lignes = [f"� {nom} � {date_fmt} (dans {j}j)" for j, nom, date_fmt in anniversaires]
                await envoyer_message_whatsapp(
                    sender, "?? *Anniversaires � venir :*\n\n" + "\n".join(lignes)
                )
        except Exception:
            logger.debug("Anniversaires WhatsApp : donn�es indisponibles")
            await envoyer_message_whatsapp(sender, "?? Anniversaires : donn�es indisponibles.")


async def _envoyer_fiche_recette(sender: str, nom_recette: str) -> None:
    """Envoie la fiche d'une recette avec ses ingr�dients."""
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
                await envoyer_message_whatsapp(sender, f"? Recette *{nom_recette}* introuvable.")
                return

            lignes = [
                f"?? *{recette.nom}*",
                f"?? Temps : {recette.temps_preparation or '?'} min",
                f"?? Portions : {recette.nb_portions or '?'}",
                "\n?? *Ingr�dients :*",
            ]

            for ri in (recette.ingredients or [])[:12]:
                qte = f"{ri.quantite} {ri.unite}" if ri.quantite else ""
                nom_ing = ri.ingredient.nom if ri.ingredient else "?"
                lignes.append(f"  � {nom_ing} {qte}".strip())

            await envoyer_message_whatsapp(sender, "\n".join(lignes))
        except Exception:
            logger.debug("Fiche recette WhatsApp : erreur")
            await envoyer_message_whatsapp(sender, f"? Recette introuvable : {nom_recette}")


async def _envoyer_taches_retard(sender: str) -> None:
    """Envoie les t�ches maison en retard."""
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
                await envoyer_message_whatsapp(sender, "? Aucune t�che maison en retard !")
            else:
                lignes = [f"� {titre} (�ch�ance: {echeance})" for titre, echeance in rows]
                await envoyer_message_whatsapp(
                    sender, f"??? *T�ches en retard ({len(rows)}) :*\n\n" + "\n".join(lignes)
                )
        except Exception:
            logger.debug("T�ches retard WhatsApp : table indisponible")
            await envoyer_message_whatsapp(sender, "??? T�ches : donn�es indisponibles.")


async def _envoyer_aide_admin(sender: str) -> None:
    """Envoie la liste des commandes admin (acc�s limit�)."""
    from src.core.config import obtenir_parametres
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    settings = obtenir_parametres()
    # V�rifier que l'exp�diteur est le num�ro admin configur�
    numero_admin = getattr(settings, "WHATSAPP_USER_NUMBER", None)
    if numero_admin and sender != numero_admin:
        logger.warning("Tentative d'acc�s aide admin depuis num�ro non autoris� : %s***", sender[:6])
        await envoyer_message_whatsapp(sender, "? Acc�s refus�.")
        return

    await envoyer_message_whatsapp(
        sender,
        "[Admin] Commandes admin :\n\n"
        "- *menu* / *planning* : Planning semaine\n"
        "- *courses* : Liste de courses\n"
        "- *frigo* : Alertes stocks\n"
        "- *jules* : Resume Jules\n"
        "- *ajouter [article]* : Ajouter a la liste\n"
        "- *budget* : Budget mensuel\n"
        "- *anniversaires* : Prochains anniversaires\n"
        "- *recette [nom]* : Fiche recette\n"
        "- *taches* : Taches en retard\n"
        "- *meteo* : Previsions du jour\n"
        "- *jardin* : Etat du jardin\n"
        "- *energie* : Consommation energie\n"
        "- *entretien* : Entretiens urgents\n"
        "- *aide admin* : Cette liste",
    )

# -------------------------------------------------------------------
# NOUVEAUX HANDLERS � PHASE 5
# -------------------------------------------------------------------


async def _envoyer_meteo(sender: str) -> None:
    """Envoie les pr�visions m�t�o du jour."""
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    try:
        import os

        import httpx

        api_key = os.getenv("OPENWEATHER_API_KEY", "")
        ville = os.getenv("OPENWEATHER_CITY", "Paris")

        if not api_key:
            await envoyer_message_whatsapp(sender, "??? M�t�o : service non configur� (OPENWEATHER_API_KEY manquante).")
            return

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": ville, "appid": api_key, "units": "metric", "lang": "fr"},
            )
            resp.raise_for_status()
            data = resp.json()

        temp = data["main"]["temp"]
        temp_min = data["main"]["temp_min"]
        temp_max = data["main"]["temp_max"]
        description = data["weather"][0]["description"].capitalize()
        humidite = data["main"]["humidity"]
        vent = data.get("wind", {}).get("speed", 0)

        msg = (
            f"??? *M�t�o {ville}*\n\n"
            f"??? {temp:.0f}�C ({temp_min:.0f}� / {temp_max:.0f}�)\n"
            f"?? {description}\n"
            f"?? Humidit� : {humidite}%\n"
            f"?? Vent : {vent:.0f} km/h"
        )
        await envoyer_message_whatsapp(sender, msg)
    except Exception:
        logger.debug("M�t�o WhatsApp : erreur")
        await envoyer_message_whatsapp(sender, "??? M�t�o : donn�es indisponibles.")


async def _envoyer_resume_jardin(sender: str) -> None:
    """Envoie le r�sum� de l'�tat du jardin (plantes, arrosage, r�coltes)."""
    from src.core.db import obtenir_contexte_db
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    with obtenir_contexte_db() as session:
        try:
            from datetime import date, timedelta

            from sqlalchemy import text

            aujourd_hui = date.today()
            dans_3j = aujourd_hui + timedelta(days=3)

            # Plantes n�cessitant un arrosage
            rows_arrosage = session.execute(
                text(
                    "SELECT nom, dernier_arrosage FROM plantes_jardin"
                    " WHERE actif = true"
                    " AND (dernier_arrosage IS NULL OR dernier_arrosage < :seuil)"
                    " ORDER BY dernier_arrosage ASC NULLS FIRST"
                    " LIMIT 10"
                ),
                {"seuil": aujourd_hui - timedelta(days=2)},
            ).fetchall()

            # R�coltes pr�tes
            rows_recolte = session.execute(
                text(
                    "SELECT nom, date_recolte_prevue FROM plantes_jardin"
                    " WHERE actif = true"
                    " AND date_recolte_prevue IS NOT NULL"
                    " AND date_recolte_prevue <= :dans_3j"
                    " ORDER BY date_recolte_prevue ASC"
                    " LIMIT 5"
                ),
                {"dans_3j": dans_3j},
            ).fetchall()

            lignes: list[str] = []
            if rows_arrosage:
                lignes.append("?? *� arroser :*")
                for nom, dernier in rows_arrosage:
                    jours = (aujourd_hui - dernier).days if dernier else "?"
                    lignes.append(f"  � {nom} (dernier arrosage : il y a {jours}j)")

            if rows_recolte:
                lignes.append("\n?? *R�coltes pr�tes :*")
                for nom, date_recolte in rows_recolte:
                    lignes.append(f"  � {nom} � {date_recolte}")

            if not lignes:
                await envoyer_message_whatsapp(sender, "?? Jardin : tout est OK !")
            else:
                await envoyer_message_whatsapp(sender, "?? *�tat du jardin*\n\n" + "\n".join(lignes))
        except Exception:
            logger.debug("Jardin WhatsApp : table indisponible")
            await envoyer_message_whatsapp(sender, "?? Jardin : donn�es indisponibles.")


async def _envoyer_resume_energie(sender: str) -> None:
    """Envoie un r�sum� de la consommation d'�nergie du mois en cours."""
    from src.core.db import obtenir_contexte_db
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    with obtenir_contexte_db() as session:
        try:
            from datetime import date

            from sqlalchemy import text

            mois_debut = date.today().replace(day=1)

            result = session.execute(
                text(
                    "SELECT COALESCE(SUM(valeur), 0), COUNT(*)"
                    " FROM releves_energie"
                    " WHERE date_releve >= :debut"
                ),
                {"debut": mois_debut},
            ).first()

            total_kwh = float(result[0]) if result else 0
            nb_releves = int(result[1]) if result else 0

            if nb_releves == 0:
                await envoyer_message_whatsapp(sender, "? �nergie : aucun relev� ce mois-ci.")
                return

            msg = (
                f"? *�nergie � {mois_debut.strftime('%B %Y')}*\n\n"
                f"?? Consommation : {total_kwh:.1f} kWh\n"
                f"?? {nb_releves} relev�(s) enregistr�(s)"
            )
            await envoyer_message_whatsapp(sender, msg)
        except Exception:
            logger.debug("�nergie WhatsApp : table indisponible")
            await envoyer_message_whatsapp(sender, "? �nergie : donn�es indisponibles.")


async def _envoyer_entretien_urgent(sender: str) -> None:
    """Envoie les t�ches d'entretien urgentes ou en retard."""
    from src.core.db import obtenir_contexte_db
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    with obtenir_contexte_db() as session:
        try:
            from datetime import date

            from sqlalchemy import text

            today = date.today()

            rows = session.execute(
                text(
                    "SELECT titre, date_echeance, priorite FROM entretiens_maison"
                    " WHERE statut NOT IN ('termine', 'annule')"
                    " AND (date_echeance < :today OR priorite = 'urgente')"
                    " ORDER BY date_echeance ASC NULLS LAST"
                    " LIMIT 10"
                ),
                {"today": today},
            ).fetchall()

            if not rows:
                await envoyer_message_whatsapp(sender, "?? Entretien : aucune t�che urgente !")
            else:
                lignes = []
                for titre, echeance, priorite in rows:
                    emoji = "??" if priorite == "urgente" else "??"
                    lignes.append(f"  {emoji} {titre} (�ch�ance: {echeance or 'N/A'})")

                from src.services.integrations.whatsapp import envoyer_message_interactif

                await envoyer_message_interactif(
                    destinataire=sender,
                    corps=f"?? *Entretien urgent ({len(rows)}) :*\n\n" + "\n".join(lignes),
                    boutons=[{"id": "entretien_fait", "title": "Marquer fait"}],
                )
        except Exception:
            logger.debug("Entretien WhatsApp : table indisponible")


# -------------------------------------------------------------------
# NLP MISTRAL POUR COMMANDES NATURELLES
# -------------------------------------------------------------------


async def _traiter_commande_nlp(sender: str, texte: str) -> None:
    """Interpr�te un message en langage naturel via Mistral et ex�cute l'action.

    Exemples support�s :
    - "ajoute du lait et des oeufs" ? ajouter_courses
    - "combien j'ai d�pens� ce mois ?" ? budget
    - "qu'est-ce qu'on mange ce soir ?" ? planning_ce_soir
    - "est-ce qu'il nous reste du beurre ?" ? stock
    """
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    try:
        from src.core.ai import obtenir_client_ia

        client = obtenir_client_ia()
        reponse = client.appeler(
            prompt=(
                f"Message WhatsApp de l'utilisateur : \"{texte}\"\n\n"
                "D�termine l'intent et les param�tres. Retourne un JSON strict :\n"
                '{"intent": "<intent>", "params": {<params>}}\n\n'
                "Intents possibles :\n"
                '- "ajouter_courses" : params = {"articles": ["lait", "oeufs"]}\n'
                '- "budget" : params = {"periode": "mois"|"semaine"}\n'
                '- "planning_ce_soir" : params = {}\n'
                '- "planning_semaine" : params = {}\n'
                '- "stock" : params = {"article": "beurre"} (optionnel)\n'
                '- "recette" : params = {"nom": "..."}\n'
                '- "jules" : params = {}\n'
                '- "taches" : params = {}\n'
                '- "meteo" : params = {}\n'
                '- "conversation" : params = {"reponse": "ta r�ponse"}\n\n'
                "Si tu ne reconnais pas l'intent, utilise 'conversation' et "
                "r�ponds naturellement en tant qu'assistant familial."
            ),
            system_prompt=(
                "Tu es l'assistant familial Matanne. Tu interpr�tes les messages "
                "WhatsApp en JSON d'action. Sois pr�cis et concis."
            ),
            temperature=0.3,
            max_tokens=300,
        )

        import json
        parsed = json.loads(
            reponse.strip().removeprefix("```json").removesuffix("```").strip()
        )
        intent = parsed.get("intent", "conversation")
        params = parsed.get("params", {})

        if intent == "ajouter_courses":
            articles = params.get("articles", [])
            if not articles:
                await envoyer_message_whatsapp(sender, "Quels articles veux-tu ajouter ?")
                return
            nb_ajoutes = 0
            for article in articles:
                await _ajouter_article_courses_nlp(sender, str(article), silencieux=True)
                nb_ajoutes += 1
            await envoyer_message_whatsapp(
                sender,
                f"? {nb_ajoutes} article(s) ajout�(s) � la liste : {', '.join(str(a) for a in articles)}",
            )

        elif intent == "budget":
            await _envoyer_resume_budget(sender)

        elif intent == "planning_ce_soir":
            await _envoyer_suggestion_ce_soir(sender)

        elif intent == "planning_semaine":
            await _envoyer_planning_courant(sender)

        elif intent == "stock":
            article = params.get("article")
            if article:
                await _chercher_stock_article(sender, str(article))
            else:
                await _envoyer_alerte_stocks(sender)

        elif intent == "recette":
            nom = params.get("nom", "")
            if nom:
                await _envoyer_fiche_recette(sender, str(nom))
            else:
                await envoyer_message_whatsapp(sender, "Quelle recette cherches-tu ?")

        elif intent == "jules":
            await _envoyer_resume_jules(sender)

        elif intent == "taches":
            await _envoyer_taches_retard(sender)

        elif intent == "meteo":
            await _envoyer_meteo(sender)

        elif intent == "conversation":
            reponse_texte = params.get("reponse", "")
            if reponse_texte:
                await envoyer_message_whatsapp(sender, str(reponse_texte))
            else:
                await envoyer_message_whatsapp(
                    sender,
                    "?? Je n'ai pas compris. Tape *aide* pour voir les commandes.",
                )
        else:
            await envoyer_message_whatsapp(
                sender,
                "?? Je n'ai pas compris. Tape *aide* pour voir les commandes.",
            )

    except Exception:
        logger.debug("NLP WhatsApp indisponible, envoi aide classique", exc_info=True)
        await envoyer_message_whatsapp(
            sender,
            "?? Commandes : *menu*, *courses*, *frigo*, *budget*, *jules*, "
            "*ajouter [article]*, *recette [nom]*, *taches*, *aide*",
        )


async def _ajouter_article_courses_nlp(sender: str, article: str, *, silencieux: bool = False) -> None:
    """Ajoute un article � la liste de courses active (NLP)."""
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.courses import ArticleCourses, ListeCourses
        from src.core.models.recettes import Ingredient

        with obtenir_contexte_db() as session:
            # Trouver ou cr�er la liste active
            liste = (
                session.query(ListeCourses)
                .filter(ListeCourses.archivee.is_(False))
                .order_by(ListeCourses.date_creation.desc())
                .first()
            )

            if not liste:
                liste = ListeCourses(nom="Courses WhatsApp")
                session.add(liste)
                session.flush()

            # Trouver ou cr�er l'ingr�dient
            ingredient = (
                session.query(Ingredient)
                .filter(Ingredient.nom.ilike(article.strip()))
                .first()
            )
            if not ingredient:
                ingredient = Ingredient(nom=article.strip().capitalize())
                session.add(ingredient)
                session.flush()

            # V�rifier si d�j� sur la liste
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
                if not silencieux:
                    await envoyer_message_whatsapp(
                        sender, f"?? '{article}' est d�j� sur la liste."
                    )
                return

            nouveau = ArticleCourses(
                liste_id=liste.id,
                ingredient_id=ingredient.id,
                quantite_necessaire=1,
                achete=False,
            )
            session.add(nouveau)
            session.commit()

        if not silencieux:
            await envoyer_message_whatsapp(sender, f"? '{article}' ajout� � la liste !")
    except Exception:
        logger.debug("Erreur ajout article WhatsApp", exc_info=True)
        if not silencieux:
            await envoyer_message_whatsapp(sender, f"? Impossible d'ajouter '{article}'.")


async def _chercher_stock_article(sender: str, article: str) -> None:
    """Recherche un article sp�cifique dans l'inventaire."""
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.inventaire import ArticleInventaire

        with obtenir_contexte_db() as session:
            resultats = (
                session.query(ArticleInventaire)
                .filter(
                    ArticleInventaire.nom.ilike(f"%{article}%"),
                    ArticleInventaire.quantite > 0,
                )
                .limit(5)
                .all()
            )

        if not resultats:
            await envoyer_message_whatsapp(
                sender,
                f"? Aucun '{article}' trouv� en stock. Veux-tu l'ajouter aux courses ?",
            )
        else:
            lignes = [
                f"- {r.nom}: {r.quantite} {r.unite or 'pcs'}"
                + (f" (p�remption: {r.date_peremption:%d/%m})" if r.date_peremption else "")
                for r in resultats
            ]
            await envoyer_message_whatsapp(
                sender,
                f"?? Stock '{article}':\n" + "\n".join(lignes),
            )
    except Exception:
        logger.debug("Erreur recherche stock WhatsApp", exc_info=True)
        await envoyer_message_whatsapp(sender, "? Impossible de v�rifier le stock.")


# -------------------------------------------------------------------
# HANDLERS BOUTONS INTERACTIFS � PHASE 5
# -------------------------------------------------------------------


async def _envoyer_detail_journee(sender: str) -> None:
    """Envoie un d�tail complet de la journ�e (bouton digest_detail)."""
    from datetime import date

    from src.core.db import obtenir_contexte_db
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    aujourd_hui = date.today()
    sections: list[str] = []

    with obtenir_contexte_db() as session:
        try:
            from sqlalchemy import text

            # Repas
            rows = session.execute(
                text(
                    "SELECT r.type_repas, rec.nom"
                    " FROM repas r LEFT JOIN recettes rec ON r.recette_id = rec.id"
                    " WHERE r.date_repas = :today ORDER BY r.type_repas"
                ),
                {"today": aujourd_hui},
            ).fetchall()
            if rows:
                sections.append("??? *Repas :*\n" + "\n".join(f"  � {t} : {n or '?'}" for t, n in rows))
        except Exception as e:
            logger.error("Erreur r�cup�ration repas du jour: %s", e)

        try:
            from sqlalchemy import text

            # T�ches du jour
            rows = session.execute(
                text(
                    "SELECT titre, priorite FROM taches_maison"
                    " WHERE statut NOT IN ('termine', 'annule')"
                    " AND date_echeance = :today"
                    " ORDER BY priorite DESC LIMIT 10"
                ),
                {"today": aujourd_hui},
            ).fetchall()
            if rows:
                sections.append(
                    "?? *T�ches :*\n" + "\n".join(f"  � {t} ({p or '-'})" for t, p in rows)
                )
        except Exception as e:
            logger.error("Erreur r�cup�ration t�ches du jour: %s", e)

        try:
            from datetime import timedelta

            from sqlalchemy import text

            # P�remptions
            seuil = aujourd_hui + timedelta(days=2)
            rows = session.execute(
                text(
                    "SELECT nom, date_peremption, quantite FROM inventaire"
                    " WHERE date_peremption IS NOT NULL"
                    " AND date_peremption <= :seuil"
                    " LIMIT 8"
                ),
                {"seuil": seuil},
            ).fetchall()
            if rows:
                sections.append(
                    "?? *P�remptions :*\n"
                    + "\n".join(f"  � {n} ({q or '?'}) � {d}" for n, d, q in rows)
                )
        except Exception as e:
            logger.error("Erreur r�cup�ration p�remptions: %s", e)

    if not sections:
        msg = f"?? *D�tail {aujourd_hui.strftime('%A %d %B')}*\n\nAucune donn�e pour aujourd'hui."
    else:
        msg = f"?? *D�tail {aujourd_hui.strftime('%A %d %B')}*\n\n" + "\n\n".join(sections)

    await envoyer_message_whatsapp(sender, msg)


async def _marquer_courses_achetees(sender: str) -> None:
    """Marque tous les articles de la liste active comme achet�s."""
    from src.core.db import obtenir_contexte_db
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

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
                await envoyer_message_whatsapp(sender, "?? Aucune liste de courses active.")
                return

            nb = (
                session.query(ArticleCourses)
                .filter(
                    ArticleCourses.liste_id == liste.id,
                    ArticleCourses.achete == False,  # noqa: E712
                )
                .update({"achete": True})
            )
            session.commit()
            await envoyer_message_whatsapp(sender, f"? {nb} article(s) marqu�(s) comme achet�(s) !")
        except Exception:
            logger.debug("Courses achet�es WhatsApp : erreur")
            await envoyer_message_whatsapp(sender, "? Erreur lors du marquage des courses.")


async def _partager_liste_courses(sender: str) -> None:
    """Partage la liste de courses sous forme de texte format�."""
    from src.core.db import obtenir_contexte_db
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

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
                await envoyer_message_whatsapp(sender, "?? Aucune liste � partager.")
                return

            articles = (
                session.query(ArticleCourses)
                .filter(
                    ArticleCourses.liste_id == liste.id,
                    ArticleCourses.achete == False,  # noqa: E712
                )
                .order_by(ArticleCourses.categorie, ArticleCourses.nom)
                .all()
            )

            if not articles:
                await envoyer_message_whatsapp(sender, "? Tous les articles sont achet�s !")
                return

            # Grouper par cat�gorie
            par_cat: dict[str, list[str]] = {}
            for a in articles:
                cat = a.categorie or "Autre"
                par_cat.setdefault(cat, []).append(
                    f"  ? {a.nom}" + (f" �{a.quantite}" if a.quantite and a.quantite > 1 else "")
                )

            lignes = [f"?? *{liste.nom}*\n"]
            for cat, items in sorted(par_cat.items()):
                lignes.append(f"*{cat}*")
                lignes.extend(items)
                lignes.append("")

            lignes.append(f"?? {len(articles)} article(s) restant(s)")
            await envoyer_message_whatsapp(sender, "\n".join(lignes))
        except Exception:
            logger.debug("Partage courses WhatsApp : erreur")
            await envoyer_message_whatsapp(sender, "? Erreur lors du partage.")


async def _marquer_entretien_fait(sender: str) -> None:
    """Marque la t�che d'entretien la plus urgente comme termin�e."""
    from src.core.db import obtenir_contexte_db
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    with obtenir_contexte_db() as session:
        try:
            from datetime import date

            from sqlalchemy import text

            today = date.today()

            # Trouver la t�che la plus urgente
            row = session.execute(
                text(
                    "SELECT id, titre FROM entretiens_maison"
                    " WHERE statut NOT IN ('termine', 'annule')"
                    " AND (date_echeance < :today OR priorite = 'urgente')"
                    " ORDER BY date_echeance ASC NULLS LAST"
                    " LIMIT 1"
                ),
                {"today": today},
            ).first()

            if not row:
                await envoyer_message_whatsapp(sender, "? Aucune t�che d'entretien en attente !")
                return

            tache_id, titre = row
            session.execute(
                text("UPDATE entretiens_maison SET statut = 'termine' WHERE id = :id"),
                {"id": tache_id},
            )
            session.commit()
            await envoyer_message_whatsapp(sender, f"? *{titre}* marqu� comme termin� !")
        except Exception:
            logger.debug("Entretien fait WhatsApp : erreur")
            await envoyer_message_whatsapp(sender, "? Erreur lors du marquage de l'entretien.")
