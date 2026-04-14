"""Handlers de callbacks Telegram (boutons interactifs)."""

from __future__ import annotations

import logging
from datetime import datetime

from ._cuisine import (
    _envoyer_courses_commande,
    _envoyer_inventaire_commande,
    _envoyer_planning_commande,
    _envoyer_repas_moment,
    _envoyer_resume_batch_cooking,
)
from ._famille import (
    _envoyer_meteo_telegram,
    _envoyer_resume_budget,
    _envoyer_resume_jules,
    _envoyer_resume_weekend,
)
from ._helpers import _extraire_id_depuis_callback, _normaliser_texte, _obtenir_url_app
from ._maison import (
    _envoyer_rappels_groupes,
    _envoyer_resume_energie,
    _envoyer_resume_jardin,
    _envoyer_taches_maison,
)
from ._menus import _envoyer_aide_telegram, _envoyer_menu_module, _envoyer_menu_principal
from ._outils import _creer_note_rapide_telegram, _lancer_minuteur_telegram

logger = logging.getLogger(__name__)


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

            nom_article = (
                getattr(getattr(article, "ingredient", None), "nom", None)
                or f"Article #{article.id}"
            )
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

    await repondre_callback_query(
        callback_query_id, str(resultat.get("message") or "✅ OK"), show_alert=False
    )
    await _envoyer_courses_commande(chat_id, liste_id=int(resultat["liste_id"]))


async def _traiter_callback_sondage_repas(
    callback_data: str,
    callback_query_id: str,
    chat_id: str,
) -> None:
    import html as html_mod

    from src.services.integrations.telegram import envoyer_message_telegram, repondre_callback_query

    choix = callback_data.split(":", 1)[1] if ":" in callback_data else "surprise"
    libelles = {
        "midi": "un repas plutôt simple pour midi",
        "soir": "un dîner réconfortant pour ce soir",
        "surprise": "une idée surprise",
    }
    message = libelles.get(choix, choix)
    await repondre_callback_query(callback_query_id, "🍽️ Préférence notée", show_alert=False)
    await envoyer_message_telegram(
        chat_id, f"🍽️ Bien noté, vous avez envie de {html_mod.escape(message)}."
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
            nom_article = (
                getattr(getattr(article, "ingredient", None), "nom", None)
                or f"Article #{article.id}"
            )
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

        await envoyer_message_telegram(
            chat_id, f"❌ {result.get('error', 'Validation impossible')}"
        )
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
            await envoyer_message_telegram(
                chat_id, "✅ Liste de courses confirmée depuis Telegram."
            )
            return True

        await envoyer_message_telegram(
            chat_id, f"❌ {result.get('error', 'Confirmation impossible')}"
        )
        return True

    return False


async def _traiter_callback_planning(
    callback_data: str,
    callback_query_id: str,
    chat_id: str,
    message_id: int | None = None,
) -> None:
    from src.api.utils import executer_async, executer_avec_session
    from src.services.integrations.telegram import modifier_message, repondre_callback_query

    if ":" in callback_data:
        action, id_str = callback_data.split(":", 1)
        try:
            planning_id = int(id_str)
        except ValueError:
            await repondre_callback_query(callback_query_id, "❌ Erreur: ID invalide")
            logger.error(f"Invalid planning ID in callback: {callback_data}")
            return
    else:
        action = callback_data
        planning_id = None

    logger.info(f"Callback planning reçu: action={action}, planning_id={planning_id}")

    if action == "planning_valider":
        try:

            def _valider():
                from datetime import date, timedelta

                from src.core.models.planning import Planning

                with executer_avec_session() as session:
                    planning = None

                    # Tenter de cibler le planning demandé s'il est encore brouillon.
                    if planning_id:
                        planning = (
                            session.query(Planning).filter(Planning.id == planning_id).first()
                        )
                        if planning:
                            if planning.etat in ("valide", "actif"):
                                # Le planning est déjà validé — on considère c'est un succès.
                                return {
                                    "message": "Planning déjà validé",
                                    "id": planning.id,
                                    "status": 200,
                                    "deja_valide": True,
                                }
                            if planning.etat != "brouillon":
                                # Planning archivé ou état inattendu → chercher le brouillon courant.
                                planning = None

                    # Fallback : dernier brouillon de la semaine en cours.
                    if not planning:
                        aujourd_hui = date.today()
                        lundi = aujourd_hui - timedelta(days=aujourd_hui.weekday())
                        planning = (
                            session.query(Planning)
                            .filter(
                                Planning.semaine_debut >= lundi,
                                Planning.etat == "brouillon",
                            )
                            .order_by(Planning.semaine_debut.desc(), Planning.id.desc())
                            .first()
                        )

                    if not planning:
                        return {
                            "error": "Aucun brouillon de planning pour cette semaine",
                            "status": 404,
                        }

                    planning.etat = "valide"
                    session.commit()
                    return {
                        "message": "Planning validé",
                        "id": planning.id,
                        "status": 200,
                        "deja_valide": False,
                    }

            result = await executer_async(_valider)
            if result.get("status") == 200:
                if result.get("deja_valide"):
                    await repondre_callback_query(
                        callback_query_id, "✅ Planning déjà validé !", show_alert=False
                    )
                else:
                    await repondre_callback_query(
                        callback_query_id, "✅ Planning validé !", show_alert=False
                    )
                    if message_id:
                        await modifier_message(
                            chat_id,
                            message_id,
                            "✅ <b>Planning validé</b>\n\nVotre planning a été validé. Vous pouvez maintenant générer la liste de courses.",
                            boutons=None,
                        )
            else:
                await repondre_callback_query(
                    callback_query_id, f"❌ {result.get('error', 'Erreur')}", show_alert=True
                )
        except Exception as e:
            logger.error(f"❌ Erreur traitement callback planning_valider: {e}", exc_info=True)
            await repondre_callback_query(callback_query_id, "❌ Erreur serveur", show_alert=True)

    elif action == "planning_modifier":
        web_url = "https://matanne.vercel.app/cuisine/planning"
        await repondre_callback_query(
            callback_query_id,
            f"Ouvrez l'app pour modifier le planning :\n{web_url}",
            show_alert=True,
        )

    elif action == "planning_regenerer":
        web_url = "https://matanne.vercel.app/cuisine/planning"
        await repondre_callback_query(
            callback_query_id,
            f"Utilisez le bouton « Régénérer » dans l'app pour relancer l'IA :\n{web_url}",
            show_alert=True,
        )
        if message_id:
            await modifier_message(
                chat_id,
                message_id,
                "🔄 <b>Régénération IA</b>\n\nOuvrez l'app pour relancer la génération IA du planning.",
                boutons=None,
            )


async def _traiter_callback_courses(
    callback_data: str,
    callback_query_id: str,
    chat_id: str,
    message_id: int | None = None,
) -> None:
    from src.api.utils import executer_async, executer_avec_session
    from src.services.integrations.telegram import modifier_message, repondre_callback_query

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
        try:

            def _confirmer():
                from src.core.models.courses import ListeCourses

                with executer_avec_session() as session:
                    if liste_id:
                        liste = (
                            session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
                        )
                    else:
                        liste = (
                            session.query(ListeCourses)
                            .filter(ListeCourses.etat == "brouillon")
                            .order_by(ListeCourses.cree_le.desc())
                            .first()
                        )

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
                    callback_query_id, "✅ Liste confirmée!", show_alert=False
                )
                if message_id:
                    await modifier_message(
                        chat_id,
                        message_id,
                        "✅ <b>Liste de courses confirmée</b>\n\nVous pouvez maintenant faire les courses!",
                        boutons=None,
                    )
            else:
                await repondre_callback_query(
                    callback_query_id, f"❌ {result.get('error', 'Erreur')}", show_alert=True
                )
        except Exception as e:
            logger.error(f"❌ Erreur traitement callback courses_confirmer: {e}", exc_info=True)
            await repondre_callback_query(callback_query_id, "❌ Erreur serveur", show_alert=True)

    elif action == "courses_ajouter":
        web_url = "https://matanne.vercel.app/cuisine/courses"
        await repondre_callback_query(
            callback_query_id, f"Ouvrez l'app pour ajouter des articles :\n{web_url}", show_alert=True
        )

    elif action == "courses_refaire":
        try:

            def _refaire():
                from src.core.models.courses import ListeCourses

                with executer_avec_session() as session:
                    if liste_id:
                        old_liste = (
                            session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
                        )
                    else:
                        old_liste = (
                            session.query(ListeCourses)
                            .filter(ListeCourses.etat == "brouillon")
                            .order_by(ListeCourses.cree_le.desc())
                            .first()
                        )

                    if not old_liste:
                        return {"error": "Liste non trouvée", "status": 404}

                    old_liste.archivee = True
                    session.flush()

                    new_liste = ListeCourses(nom=f"{old_liste.nom} (refait)", etat="brouillon")
                    session.add(new_liste)
                    session.commit()
                    return {"message": "Liste refaite", "id": new_liste.id, "status": 200}

            result = await executer_async(_refaire)
            if result.get("status") == 200:
                await repondre_callback_query(
                    callback_query_id, "\U0001f504 Nouvelle liste créée en brouillon.", show_alert=False
                )
                if message_id:
                    await modifier_message(
                        chat_id,
                        message_id,
                        "\U0001f504 <b>Liste refaite</b>\n\nUne nouvelle liste brouillon a été créée.",
                        boutons=None,
                    )
            else:
                await repondre_callback_query(
                    callback_query_id, f"❌ {result.get('error', 'Erreur')}", show_alert=True
                )
        except Exception as e:
            logger.error(f"❌ Erreur traitement callback courses_refaire: {e}", exc_info=True)
            await repondre_callback_query(callback_query_id, "❌ Erreur serveur", show_alert=True)


async def _traiter_callback_tache(
    callback_data: str,
    callback_query_id: str,
    chat_id: str,
) -> None:
    """Gère les callbacks boutons inline pour les tâches de projet (valider / reporter)."""
    import html as html_mod

    from src.api.utils import executer_async, executer_avec_session
    from src.services.integrations.telegram import envoyer_message_telegram, repondre_callback_query

    if ":" not in callback_data:
        await repondre_callback_query(callback_query_id, "❌ Données incomplètes", show_alert=True)
        return

    action, id_str = callback_data.split(":", 1)
    try:
        tache_id = int(id_str)
    except ValueError:
        await repondre_callback_query(callback_query_id, "❌ Erreur: ID invalide", show_alert=True)
        logger.error(f"Invalid tache ID in callback: {callback_data}")
        return

    logger.info(f"Callback tâche reçu: action={action}, tache_id={tache_id}")

    if action == "tache_valider":

        def _valider() -> dict[str, object]:
            from src.core.models.maison import TacheProjet

            with executer_avec_session() as session:
                tache = session.query(TacheProjet).filter(TacheProjet.id == tache_id).first()
                if not tache:
                    return {"error": "Tâche non trouvée", "status": 404}
                if tache.statut == "terminé":
                    return {"message": "Tâche déjà terminée", "nom": tache.nom, "status": 200}
                tache.statut = "terminé"
                session.commit()
                return {"message": "Tâche terminée", "nom": tache.nom, "status": 200}

        try:
            result = await executer_async(_valider)
            if result.get("status") == 200:
                nom = html_mod.escape(str(result.get("nom", "")))
                await repondre_callback_query(
                    callback_query_id, f"✅ {result.get('nom')} — terminée !", show_alert=False
                )
                await envoyer_message_telegram(chat_id, f"✅ <b>{nom}</b> marquée comme terminée.")
            else:
                await repondre_callback_query(
                    callback_query_id, f"❌ {result.get('error', 'Erreur')}", show_alert=True
                )
        except Exception as e:
            logger.error(f"❌ Erreur callback tache_valider: {e}", exc_info=True)
            await repondre_callback_query(callback_query_id, "❌ Erreur serveur", show_alert=True)

    elif action == "tache_reporter":

        def _reporter() -> dict[str, object]:
            from datetime import timedelta

            from src.core.models.maison import TacheProjet

            with executer_avec_session() as session:
                tache = session.query(TacheProjet).filter(TacheProjet.id == tache_id).first()
                if not tache:
                    return {"error": "Tâche non trouvée", "status": 404}
                if tache.date_echeance:
                    tache.date_echeance = tache.date_echeance + timedelta(days=1)
                    nouvelle_echeance = tache.date_echeance.strftime("%d/%m")
                else:
                    nouvelle_echeance = "demain"
                session.commit()
                return {
                    "message": "Tâche reportée",
                    "nom": tache.nom,
                    "echeance": nouvelle_echeance,
                    "status": 200,
                }

        try:
            result = await executer_async(_reporter)
            if result.get("status") == 200:
                nom = html_mod.escape(str(result.get("nom", "")))
                echeance = html_mod.escape(str(result.get("echeance", "demain")))
                await repondre_callback_query(
                    callback_query_id, f"🔄 Reportée au {result.get('echeance')}", show_alert=False
                )
                await envoyer_message_telegram(chat_id, f"🔄 <b>{nom}</b> reportée au {echeance}.")
            else:
                await repondre_callback_query(
                    callback_query_id, f"❌ {result.get('error', 'Erreur')}", show_alert=True
                )
        except Exception as e:
            logger.error(f"❌ Erreur callback tache_reporter: {e}", exc_info=True)
            await repondre_callback_query(callback_query_id, "❌ Erreur serveur", show_alert=True)

    else:
        await repondre_callback_query(callback_query_id, "❌ Action inconnue", show_alert=True)


async def _obtenir_message_id(callback_query_id: str) -> int | None:
    """Stub pour obtenir le message_id depuis callback_query_id."""
    return None
