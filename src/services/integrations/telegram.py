"""
Client Telegram via Bot API.

100% gratuit — aucune limite de messages, pas de catégories payantes.
Boutons interactifs illimités (InlineKeyboardMarkup).

Utilisé pour :
- Envoyer le planning de la semaine + validation via boutons
- Recevoir la validation "OK" / "Changer lundi soir" par message
- Alertes péremption
- Digest matinal
- Toutes notifications proactives (CRON jobs)

Transport : HTTP POST vers https://api.telegram.org/bot{TOKEN}/...
Webhook : POST /api/v1/telegram/webhook
"""

import logging
import time
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

import httpx

from src.core.config import obtenir_parametres

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org"


# ═══════════════════════════════════════════════════════════
# RATE LIMITING (persisté en DB via etats_persistants)
# Telegram n'a pas de limites payantes, mais on garde un
# rate limit interne pour éviter de spammer l'utilisateur.
# ═══════════════════════════════════════════════════════════

_LIMITE_PAR_HEURE = 30  # Gratuit, pas de limite officielle
_LIMITE_PAR_JOUR = 200

# In-memory fallback
_compteurs_heure: dict[str, list[float]] = defaultdict(list)
_compteurs_jour: list[float] = []


# ═══════════════════════════════════════════════════════════
# CONVERSATION STATE (persisté en DB)
# ═══════════════════════════════════════════════════════════

_NAMESPACE_ETAT_CONVERSATION = "telegram_conversation_state"
_TTL_ETAT_SECONDES = 24 * 3600


def charger_etat_conversation(destinataire: str) -> dict[str, Any] | None:
    """Charge l'état conversationnel persistant d'un destinataire."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.persistent_state import EtatPersistantDB

        with obtenir_contexte_db() as session:
            state = (
                session.query(EtatPersistantDB)
                .filter(
                    EtatPersistantDB.namespace == _NAMESPACE_ETAT_CONVERSATION,
                    EtatPersistantDB.user_id == destinataire,
                )
                .first()
            )
            if not state or not state.data:
                return None

            updated_at_str = str(state.data.get("updated_at", ""))
            if updated_at_str:
                try:
                    updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                    age_seconds = (datetime.now(UTC) - updated_at).total_seconds()
                    if age_seconds > _TTL_ETAT_SECONDES:
                        session.delete(state)
                        session.commit()
                        return None
                except Exception:
                    pass

            return dict(state.data)
    except Exception:
        logger.debug("Impossible de charger l'état conversation Telegram", exc_info=True)
        return None


def sauvegarder_etat_conversation(destinataire: str, etat: dict[str, Any]) -> None:
    """Sauvegarde l'état conversationnel persistant d'un destinataire."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.persistent_state import EtatPersistantDB

        payload = dict(etat)
        payload["updated_at"] = datetime.now(UTC).isoformat()

        with obtenir_contexte_db() as session:
            state = (
                session.query(EtatPersistantDB)
                .filter(
                    EtatPersistantDB.namespace == _NAMESPACE_ETAT_CONVERSATION,
                    EtatPersistantDB.user_id == destinataire,
                )
                .first()
            )
            if state is None:
                state = EtatPersistantDB(
                    namespace=_NAMESPACE_ETAT_CONVERSATION,
                    user_id=destinataire,
                    data=payload,
                )
                session.add(state)
            else:
                state.data = payload
            session.commit()
    except Exception:
        logger.warning("Impossible de sauvegarder l'état conversation Telegram")


def effacer_etat_conversation(destinataire: str) -> None:
    """Supprime l'état conversationnel persistant d'un destinataire."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.persistent_state import EtatPersistantDB

        with obtenir_contexte_db() as session:
            state = (
                session.query(EtatPersistantDB)
                .filter(
                    EtatPersistantDB.namespace == _NAMESPACE_ETAT_CONVERSATION,
                    EtatPersistantDB.user_id == destinataire,
                )
                .first()
            )
            if state is not None:
                session.delete(state)
                session.commit()
    except Exception:
        logger.debug("Impossible d'effacer l'état conversation Telegram", exc_info=True)


def _charger_compteur_db(destinataire: str) -> tuple[int, int]:
    """Charge les compteurs rate limit depuis la DB."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.persistent_state import EtatPersistantDB

        with obtenir_contexte_db() as session:
            state = (
                session.query(EtatPersistantDB)
                .filter(
                    EtatPersistantDB.namespace == "telegram_rate_limit",
                    EtatPersistantDB.user_id == "global",
                )
                .first()
            )
            if not state or not state.data:
                return 0, 0

            envois = state.data.get("envois", [])
            now = time.time()
            heure_count = sum(
                1 for e in envois
                if e.get("dest") == destinataire and now - e.get("ts", 0) < 3600
            )
            jour_count = sum(
                1 for e in envois
                if now - e.get("ts", 0) < 86400
            )
            return heure_count, jour_count
    except Exception:
        return -1, -1


def _enregistrer_envoi_db(destinataire: str) -> None:
    """Enregistre un envoi en DB. Historique glissant de 48h max."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.persistent_state import EtatPersistantDB

        with obtenir_contexte_db() as session:
            state = (
                session.query(EtatPersistantDB)
                .filter(
                    EtatPersistantDB.namespace == "telegram_rate_limit",
                    EtatPersistantDB.user_id == "global",
                )
                .first()
            )
            now = time.time()
            seuil_48h = now - 172800

            if not state:
                state = EtatPersistantDB(
                    namespace="telegram_rate_limit",
                    user_id="global",
                    data={"envois": []},
                )
                session.add(state)

            envois = [e for e in (state.data or {}).get("envois", []) if e.get("ts", 0) > seuil_48h]
            envois.append({"dest": destinataire, "ts": now})
            state.data = {"envois": envois}
            session.commit()
    except Exception as e:
        logger.warning(f"Impossible de persister rate limit Telegram: {e}")


def _nettoyer_compteur_heure(dest: str) -> None:
    seuil = time.monotonic() - 3600
    _compteurs_heure[dest] = [t for t in _compteurs_heure[dest] if t > seuil]


def _nettoyer_compteur_jour() -> None:
    global _compteurs_jour
    seuil = time.monotonic() - 86400
    _compteurs_jour = [t for t in _compteurs_jour if t > seuil]


def _verifier_rate_limit(destinataire: str) -> tuple[bool, str]:
    """Vérifie si l'envoi est autorisé (DB first, in-memory fallback)."""
    heure_count, jour_count = _charger_compteur_db(destinataire)

    if heure_count >= 0:
        if heure_count >= _LIMITE_PAR_HEURE:
            return False, f"Limite horaire atteinte ({_LIMITE_PAR_HEURE}/h)"
        if jour_count >= _LIMITE_PAR_JOUR:
            return False, f"Limite journalière atteinte ({_LIMITE_PAR_JOUR}/jour)"
        return True, ""

    _nettoyer_compteur_heure(destinataire)
    if len(_compteurs_heure[destinataire]) >= _LIMITE_PAR_HEURE:
        return False, f"Limite horaire atteinte ({_LIMITE_PAR_HEURE}/h)"

    _nettoyer_compteur_jour()
    if len(_compteurs_jour) >= _LIMITE_PAR_JOUR:
        return False, f"Limite journalière atteinte ({_LIMITE_PAR_JOUR}/jour)"

    return True, ""


def _enregistrer_envoi(destinataire: str) -> None:
    now = time.monotonic()
    _compteurs_heure[destinataire].append(now)
    _compteurs_jour.append(now)
    _enregistrer_envoi_db(destinataire)


# ═══════════════════════════════════════════════════════════
# HELPERS TELEGRAM
# ═══════════════════════════════════════════════════════════

def _get_bot_url(method: str) -> str:
    """Construit l'URL de l'API Telegram Bot."""
    settings = obtenir_parametres()
    return f"{TELEGRAM_API_BASE}/bot{settings.TELEGRAM_BOT_TOKEN}/{method}"


def _build_inline_keyboard(boutons: list[dict[str, str]]) -> dict:
    """Construit un InlineKeyboardMarkup à partir d'une liste de boutons.

    Args:
        boutons: Liste de {"id": "callback_data", "title": "Texte bouton"}

    Returns:
        Dict compatible avec reply_markup de Telegram
    """
    keyboard = []
    for bouton in boutons:
        item = {"text": bouton["title"]}
        if bouton.get("url"):
            item["url"] = bouton["url"]
        else:
            item["callback_data"] = bouton["id"][:64]  # Telegram limite à 64 bytes
        keyboard.append([item])
    return {"inline_keyboard": keyboard}


# ═══════════════════════════════════════════════════════════
# FONCTIONS D'ENVOI PRINCIPALES
# ═══════════════════════════════════════════════════════════

async def envoyer_message_telegram(
    destinataire: str,
    texte: str,
) -> bool:
    """Envoie un message texte Telegram via Bot API.

    Args:
        destinataire: Chat ID Telegram (ex: "123456789")
        texte: Message à envoyer (supporte HTML : <b>, <i>, <code>)

    Returns:
        True si envoyé avec succès
    """
    settings = obtenir_parametres()

    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.debug("Telegram non configuré — message ignoré")
        return False

    chat_id = destinataire or settings.TELEGRAM_CHAT_ID

    autorise, raison = _verifier_rate_limit(chat_id)
    if not autorise:
        logger.warning("Telegram rate limit : %s", raison)
        return False

    url = _get_bot_url("sendMessage")
    payload = {
        "chat_id": chat_id,
        "text": texte,
        "parse_mode": "HTML",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("ok"):
                logger.error(f"Telegram API error: {data.get('description')}")
                return False
            logger.info(f"✅ Message Telegram envoyé à [{chat_id[:4]}...]")
            _enregistrer_envoi(chat_id)
            return True
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Erreur Telegram HTTP {e.response.status_code}: {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur Telegram : {e}")
        return False


async def envoyer_message_interactif(
    destinataire: str,
    corps: str,
    boutons: list[dict[str, str]],
) -> bool:
    """Envoie un message avec boutons interactifs (InlineKeyboard).

    Args:
        destinataire: Chat ID Telegram
        corps: Texte principal du message (HTML supporté)
        boutons: Liste de {"id": "callback_data", "title": "Texte bouton"}
                 Pas de limite de nombre sur les boutons inline.
    """
    settings = obtenir_parametres()

    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return False

    chat_id = destinataire or settings.TELEGRAM_CHAT_ID

    autorise, raison = _verifier_rate_limit(chat_id)
    if not autorise:
        logger.warning("Telegram interactif rate limit : %s", raison)
        return False

    url = _get_bot_url("sendMessage")
    payload = {
        "chat_id": chat_id,
        "text": corps,
        "parse_mode": "HTML",
        "reply_markup": _build_inline_keyboard(boutons),
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("ok"):
                logger.error(f"Telegram API error: {data.get('description')}")
                return False
            _enregistrer_envoi(chat_id)
            return True
    except Exception as e:
        logger.error(f"❌ Erreur Telegram interactif : {e}")
        return False


async def repondre_callback_query(
    callback_query_id: str,
    texte: str | None = None,
    show_alert: bool = False,
) -> bool:
    """Répond à un callback_query (clic sur bouton inline).

    Doit être appelé dans les 10 secondes suivant le clic.

    Args:
        callback_query_id: ID du callback_query reçu via webhook
        texte: Texte optionnel à afficher (notification ou popup)
        show_alert: True pour popup, False pour notification discrète
    """
    settings = obtenir_parametres()
    if not settings.TELEGRAM_BOT_TOKEN:
        return False

    url = _get_bot_url("answerCallbackQuery")
    payload: dict[str, Any] = {"callback_query_id": callback_query_id}
    if texte:
        payload["text"] = texte
        payload["show_alert"] = show_alert

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json().get("ok", False)
    except Exception as e:
        logger.error(f"❌ Erreur answerCallbackQuery : {e}")
        return False


async def modifier_message(
    chat_id: str,
    message_id: int,
    texte: str,
    boutons: list[dict[str, str]] | None = None,
) -> bool:
    """Modifie un message existant (utile après validation pour retirer les boutons).

    Args:
        chat_id: Chat ID Telegram
        message_id: ID du message à modifier
        texte: Nouveau texte
        boutons: Nouveaux boutons (None pour supprimer les boutons)
    """
    settings = obtenir_parametres()
    if not settings.TELEGRAM_BOT_TOKEN:
        return False

    url = _get_bot_url("editMessageText")
    payload: dict[str, Any] = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": texte,
        "parse_mode": "HTML",
    }
    if boutons:
        payload["reply_markup"] = _build_inline_keyboard(boutons)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json().get("ok", False)
    except Exception as e:
        logger.error(f"❌ Erreur editMessageText : {e}")
        return False


async def telecharger_fichier_telegram(file_id: str) -> bytes | None:
    """Télécharge un fichier Telegram à partir de son `file_id`."""
    settings = obtenir_parametres()
    if not settings.TELEGRAM_BOT_TOKEN or not file_id:
        return None

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            reponse_meta = await client.post(_get_bot_url("getFile"), json={"file_id": file_id})
            reponse_meta.raise_for_status()
            data = reponse_meta.json()
            file_path = ((data or {}).get("result") or {}).get("file_path")
            if not file_path:
                logger.warning("Téléchargement Telegram impossible: file_path absent")
                return None

            url_fichier = f"{TELEGRAM_API_BASE}/file/bot{settings.TELEGRAM_BOT_TOKEN}/{file_path}"
            reponse_fichier = await client.get(url_fichier)
            reponse_fichier.raise_for_status()
            return reponse_fichier.content
    except Exception as exc:
        logger.error("❌ Erreur téléchargement fichier Telegram: %s", exc)
        return None


# ═══════════════════════════════════════════════════════════
# FONCTIONS MÉTIER
# ═══════════════════════════════════════════════════════════

async def envoyer_planning_semaine(
    planning_texte: str,
    planning_id: int | None = None,
    resume_ia: str | None = None,
) -> bool:
    """Envoie le planning semaine avec boutons de validation.

    Args:
        planning_texte: Texte formaté du planning à afficher
        planning_id: ID du planning pour générer des callbacks ciblés
        resume_ia: Synthèse courte expliquant le fil conducteur du planning
    """
    settings = obtenir_parametres()
    chat_id = settings.TELEGRAM_CHAT_ID

    if not chat_id:
        logger.debug("TELEGRAM_CHAT_ID non configuré")
        return False

    sections = ["🍽️ <b>Planning repas de la semaine</b>"]
    if resume_ia:
        sections.append(f"🧠 <i>Lecture IA</i> : {resume_ia}")
    sections.append(planning_texte)
    sections.append("Utilisez les boutons ci-dessous pour valider, modifier ou régénérer rapidement.")
    message = "\n\n".join(section for section in sections if section)

    # Callbacks avec planning_id pour cibler la bonne semaine (max 64 bytes par callback_data)
    # Format: "planning_valider:ID", "planning_modifier:ID", "planning_regenerer:ID"
    if planning_id:
        boutons = [
            {"id": f"planning_valider:{planning_id}", "title": "✅ Valider"},
            {"id": f"planning_modifier:{planning_id}", "title": "✏️ Modifier"},
            {"id": f"planning_regenerer:{planning_id}", "title": "🔄 Régénérer"},
        ]
    else:
        # Backward compat: callbacks sans ID (anciens flux)
        boutons = [
            {"id": "planning_valider", "title": "✅ Valider"},
            {"id": "planning_modifier", "title": "✏️ Modifier"},
            {"id": "planning_regenerer", "title": "🔄 Régénérer"},
        ]

    return await envoyer_message_interactif(
        destinataire=chat_id,
        corps=message,
        boutons=boutons,
    )


async def envoyer_alerte_peremption(articles: list[dict]) -> bool:
    """Envoie une alerte pour les articles proches de la péremption."""
    settings = obtenir_parametres()
    chat_id = settings.TELEGRAM_CHAT_ID

    if not chat_id or not articles:
        return False

    lignes = [f"• {a['nom']} — expire le {a['date']}" for a in articles[:10]]
    message = f"⚠️ <b>Alerte péremption</b>\n\n{chr(10).join(lignes)}\n\nPense à les utiliser !"

    return await envoyer_message_telegram(chat_id, message)


async def envoyer_rappel_creche(message_creche: str) -> bool:
    """Envoie un rappel lié à la crèche."""
    settings = obtenir_parametres()
    chat_id = settings.TELEGRAM_CHAT_ID

    if not chat_id:
        return False

    message = f"👶 <b>Rappel crèche</b>\n\n{message_creche}"
    return await envoyer_message_telegram(chat_id, message)


async def envoyer_liste_courses_partagee(
    articles: list[str],
    nom_liste: str = "Courses",
    liste_id: int | None = None,
) -> bool:
    """Envoie la liste de courses active via Telegram avec boutons interactifs.
    
    Args:
        articles: Liste d'articles à afficher
        nom_liste: Nom de la liste (ex: "Courses lundi")
        liste_id: ID de la liste pour générer des callbacks ciblés
    """
    settings = obtenir_parametres()
    chat_id = settings.TELEGRAM_CHAT_ID

    if not chat_id or not articles:
        return False

    lignes = "\n".join(f"☐ {a}" for a in articles[:30])
    message = f"🛒 <b>{nom_liste}</b>\n\n{lignes}"

    # Callbacks avec liste_id pour cibler la bonne liste.
    if liste_id:
        boutons = [
            {"id": f"courses_confirmer:{liste_id}", "title": "✅ Confirmer"},
            {"id": f"courses_ajouter:{liste_id}", "title": "✏️ Ajouter"},
            {"id": f"courses_refaire:{liste_id}", "title": "❌ Refaire"},
        ]
    else:
        # Backward compat: callbacks sans ID
        boutons = [
            {"id": "courses_confirmer", "title": "✅ Confirmer"},
            {"id": "courses_ajouter", "title": "✏️ Ajouter"},
            {"id": "courses_refaire", "title": "❌ Refaire"},
        ]

    return await envoyer_message_interactif(
        destinataire=chat_id,
        corps=message,
        boutons=boutons,
    )


async def envoyer_rapport_hebdo_telegram(texte_resume: str) -> bool:
    """Envoie le rapport hebdomadaire compact via Telegram."""
    settings = obtenir_parametres()
    chat_id = settings.TELEGRAM_CHAT_ID

    if not chat_id:
        return False

    message = f"📋 <b>Résumé de la semaine</b>\n\n{texte_resume}"
    return await envoyer_message_interactif(
        destinataire=chat_id,
        corps=message,
        boutons=[
            {"id": "resume_vu", "title": "👍 Vu !"},
            {"id": "resume_detail", "title": "📊 Détail"},
        ],
    )


async def envoyer_suggestion_recette_du_jour(message: str) -> bool:
    """Suggestion recette — Suggestion recette du jour."""
    settings = obtenir_parametres()
    chat_id = settings.TELEGRAM_CHAT_ID
    if not chat_id:
        return False
    return await envoyer_message_telegram(chat_id, f"🍽️ <b>Suggestion recette du jour</b>\n\n{message}")


async def envoyer_alerte_diagnostic_maison(message: str) -> bool:
    """Alerte diagnostic maison — Alerte diagnostic maison."""
    settings = obtenir_parametres()
    chat_id = settings.TELEGRAM_CHAT_ID
    if not chat_id:
        return False
    return await envoyer_message_interactif(
        destinataire=chat_id,
        corps=f"🛠️ <b>Diagnostic maison</b>\n\n{message}",
        boutons=[
            {"id": "diagnostic_vu", "title": "✅ Vu"},
            {"id": "diagnostic_artisan", "title": "👷 Artisans"},
        ],
    )


async def envoyer_resume_weekend_suggestions(message: str) -> bool:
    """Résumé weekend — Résumé weekend suggestions."""
    settings = obtenir_parametres()
    chat_id = settings.TELEGRAM_CHAT_ID
    if not chat_id:
        return False
    return await envoyer_message_interactif(
        destinataire=chat_id,
        corps=f"🎡 <b>Weekend en vue</b>\n\n{message}",
        boutons=[
            {"id": "weekend_ok", "title": "✅ OK"},
            {"id": "weekend_autres", "title": "🔄 Autres idées"},
        ],
    )


async def envoyer_alerte_budget_depassement(message: str) -> bool:
    """Alerte budget — Alerte budget dépassement."""
    settings = obtenir_parametres()
    chat_id = settings.TELEGRAM_CHAT_ID
    if not chat_id:
        return False
    return await envoyer_message_telegram(chat_id, f"💸 <b>Alerte budget</b>\n\n{message}")


async def envoyer_bilan_nutrition_semaine(message: str) -> bool:
    """Bilan nutrition — Bilan nutrition de la semaine."""
    settings = obtenir_parametres()
    chat_id = settings.TELEGRAM_CHAT_ID
    if not chat_id:
        return False
    return await envoyer_message_telegram(chat_id, f"🥗 <b>Bilan nutrition semaine</b>\n\n{message}")


async def envoyer_rappel_entretien_maison(message: str) -> bool:
    """Rappel entretien — Rappel entretien maison."""
    settings = obtenir_parametres()
    chat_id = settings.TELEGRAM_CHAT_ID
    if not chat_id:
        return False
    return await envoyer_message_interactif(
        destinataire=chat_id,
        corps=f"🧰 <b>Rappel entretien maison</b>\n\n{message}",
        boutons=[
            {"id": "entretien_fait", "title": "✅ Fait"},
            {"id": "entretien_plus_tard", "title": "⏳ Plus tard"},
        ],
    )


async def envoyer_digest_matinal() -> bool:
    """Digest matinal : résumé de la journée à venir.

    Contenu :
    - Repas prévus aujourd'hui
    - Tâches/rendez-vous du jour
    - Alertes péremption imminentes

    Appelé par le CRON job matinal (7h-8h).
    """
    from datetime import date, timedelta

    settings = obtenir_parametres()
    chat_id = settings.TELEGRAM_CHAT_ID

    if not chat_id:
        return False

    aujourd_hui = date.today()
    sections: list[str] = []

    # 1. Repas du jour
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.planning import Repas

        with obtenir_contexte_db() as session:
            repas = (
                session.query(Repas)
                .filter(Repas.date_repas == aujourd_hui)
                .order_by(Repas.type_repas)
                .all()
            )
            if repas:
                lignes = []
                for r in repas:
                    nom = r.recette.nom if getattr(r, "recette", None) else (r.notes or "?")
                    emoji = "🌙" if r.type_repas == "diner" else "☀️"
                    lignes.append(f"  {emoji} {r.type_repas.capitalize()} : {nom}")
                sections.append("🍽️ <b>Repas du jour :</b>\n" + "\n".join(lignes))
    except Exception:
        logger.debug("Digest matinal : repas indisponibles")

    # 2. Alertes péremption (J0-J2)
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ArticleInventaire

        with obtenir_contexte_db() as session:
            seuil = aujourd_hui + timedelta(days=2)
            peremptions = (
                session.query(ArticleInventaire)
                .filter(
                    ArticleInventaire.date_peremption.isnot(None),
                    ArticleInventaire.date_peremption <= seuil,
                )
                .limit(5)
                .all()
            )
            if peremptions:
                lignes = [f"  • {a.nom} — {a.date_peremption}" for a in peremptions]
                sections.append("⚠️ <b>Péremptions proches :</b>\n" + "\n".join(lignes))
    except Exception:
        logger.debug("Digest matinal : péremptions indisponibles")

    # 3. Tâches du jour (entretien/maison)
    try:
        from src.core.db import obtenir_contexte_db

        with obtenir_contexte_db() as session:
            from sqlalchemy import text

            rows = session.execute(
                text(
                    "SELECT titre FROM taches_maison"
                    " WHERE statut NOT IN ('termine', 'annule')"
                    " AND date_echeance = :today"
                    " LIMIT 5"
                ),
                {"today": aujourd_hui},
            ).fetchall()
            if rows:
                lignes = [f"  • {titre}" for (titre,) in rows]
                sections.append("📋 <b>Tâches du jour :</b>\n" + "\n".join(lignes))
    except Exception:
        logger.debug("Digest matinal : tâches indisponibles")

    if not sections:
        message = f"☀️ <b>Bonjour !</b> — {aujourd_hui.strftime('%A %d %B')}\n\nRien de spécial prévu aujourd'hui. Bonne journée !"
    else:
        message = f"☀️ <b>Bonjour !</b> — {aujourd_hui.strftime('%A %d %B')}\n\n" + "\n\n".join(sections)

    return await envoyer_message_interactif(
        destinataire=chat_id,
        corps=message,
        boutons=[
            {"id": "digest_courses", "title": "🛒 Courses"},
            {"id": "digest_detail", "title": "📊 Détail"},
        ],
    )


# ═══════════════════════════════════════════════════════════
# PHASE E — NOUVEAUX FONCTIONS TELEGRAM
# ═══════════════════════════════════════════════════════════


async def envoyer_resume_mensuel_jeux(
    mois: int,
    annee: int,
    nb_paris: int = 0,
    mises_totales: float = 0.0,
    gains_totaux: float = 0.0,
    bilan_net: float = 0.0,
    taux_reussite_pct: float | None = None,
) -> bool:
    """E2: Résumé mensuel automatique des dépenses jeux → Telegram."""
    settings = obtenir_parametres()
    chat_id = settings.TELEGRAM_CHAT_ID
    if not chat_id:
        return False

    import calendar
    nom_mois = calendar.month_name[mois].capitalize()
    emoji_bilan = "📈" if bilan_net >= 0 else "📉"
    signe = "+" if bilan_net >= 0 else ""

    lignes = [
        f"🎲 <b>Bilan jeux — {nom_mois} {annee}</b>",
        "",
        f"• Paris joués : {nb_paris}",
        f"• Mises totales : {mises_totales:.2f}€",
        f"• Gains totaux : {gains_totaux:.2f}€",
        f"• Bilan net : {signe}{bilan_net:.2f}€ {emoji_bilan}",
    ]
    if taux_reussite_pct is not None:
        lignes.append(f"• Taux de réussite : {taux_reussite_pct:.1f}%")

    corps = "\n".join(lignes)
    return await envoyer_message_interactif(
        destinataire=chat_id,
        corps=corps,
        boutons=[
            {"id": "jeux_detail_mois", "title": "📊 Détail"},
            {"id": "jeux_stats_generales", "title": "📈 Historique"},
        ],
    )


async def envoyer_alerte_inventaire_bas(articles_bas: list[dict]) -> bool:
    """E4: Notification Telegram — inventaire bas → ajouter à la prochaine liste."""
    settings = obtenir_parametres()
    chat_id = settings.TELEGRAM_CHAT_ID
    if not chat_id:
        return False

    if not articles_bas:
        return True

    noms = [a.get("nom", "?") for a in articles_bas[:5]]
    autres = len(articles_bas) - 5 if len(articles_bas) > 5 else 0

    lignes = ["📦 <b>Stock bas — à racheter bientôt</b>", ""]
    for article in articles_bas[:5]:
        nom = article.get("nom", "?")
        qte = article.get("quantite", 0)
        unite = article.get("unite", "")
        lignes.append(f"⚠️ {nom} ({qte} {unite} restant(s))")

    if autres > 0:
        lignes.append(f"… et {autres} autre(s) article(s)")

    lignes += ["", "Voulez-vous les ajouter à la prochaine liste de courses ?"]

    return await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"id": "inventaire_ajouter_liste", "title": "✅ Ajouter à la liste"},
            {"id": "inventaire_ignorer", "title": "⏭️ Ignorer"},
        ],
    )


async def envoyer_confirmation_batch_cooking(
    nom_session: str = "Batch cooking",
    nb_recettes: int = 0,
    photo_url: str | None = None,
    session_id: int | None = None,
) -> bool:
    """E6: Confirmation Telegram — fin de session batch cooking ✅."""
    settings = obtenir_parametres()
    chat_id = settings.TELEGRAM_CHAT_ID
    if not chat_id:
        return False

    corps = (
        f"✅ <b>Batch cooking terminé !</b>\n\n"
        f"📦 Session : {nom_session}\n"
        f"🍽️ {nb_recettes} recette(s) préparée(s)\n\n"
        "Le planning a été mis à jour automatiquement. "
        "Retrouvez les repas prêts dans votre agenda."
    )

    if photo_url:
        try:
            return await envoyer_message_interactif(
                destinataire=chat_id,
                corps=corps,
                boutons=[
                    {"id": f"batch_voir_{session_id or 0}", "title": "👁️ Voir le récap"},
                    {"id": "planning_semaine", "title": "📅 Planning"},
                ],
            )
        except Exception:
            pass

    return await envoyer_message_interactif(
        destinataire=chat_id,
        corps=corps,
        boutons=[
            {"id": f"batch_voir_{session_id or 0}", "title": "👁️ Voir le récap"},
            {"id": "planning_semaine", "title": "📅 Planning"},
        ],
    )
