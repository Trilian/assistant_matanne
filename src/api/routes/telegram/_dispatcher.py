"""Dispatcher des commandes Telegram (slash-commands et langage naturel)."""

from __future__ import annotations

from ._helpers import _normaliser_texte
from ._menus import _envoyer_aide_telegram, _envoyer_menu_principal
from ._cuisine import (
    _ajouter_article_liste,
    _envoyer_courses_commande,
    _envoyer_inventaire_commande,
    _envoyer_planning_commande,
    _envoyer_recette_commande,
    _envoyer_repas_moment,
    _envoyer_resume_batch_cooking,
)
from ._famille import (
    _envoyer_digest_commande,
    _envoyer_meteo_telegram,
    _envoyer_projection_budget_telegram,
    _envoyer_rapport_hebdo,
    _envoyer_recap_journee,
    _envoyer_resume_budget,
    _envoyer_resume_jules,
    _envoyer_resume_weekend,
)
from ._maison import (
    _envoyer_rappels_groupes,
    _envoyer_resume_energie,
    _envoyer_resume_jardin,
    _envoyer_taches_maison,
    _envoyer_taches_projets,
)
from ._outils import (
    _creer_note_rapide_telegram,
    _envoyer_aide_photo_telegram,
    _lancer_minuteur_telegram,
)


async def _dispatcher_commande_telegram(chat_id: str, texte: str, normalise: str) -> bool:
    """Dispatch une commande Telegram vers le handler approprié.

    Returns True si la commande a été reconnue et traitée.
    """
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
    if normalise in {"/taches", "/projets"}:
        await _envoyer_taches_projets(chat_id)
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
    if normalise == "/projection":
        await _envoyer_projection_budget_telegram(chat_id)
        return True
    if normalise == "/recap":
        await _envoyer_recap_journee(chat_id)
        return True
    if normalise in {"/digest", "/resume"}:
        await _envoyer_digest_commande(chat_id)
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
    if (
        normalise.startswith("/ajout")
        or normalise.startswith("/ajouter_course")
        or normalise.startswith("/acheter")
    ):
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
