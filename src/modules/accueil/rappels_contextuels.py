"""
Rappels contextuels enrichis pour le dashboard.

Agrège des rappels issus de multiples sources:
- RDV du lendemain (calendrier/planning)
- Stocks critiques détaillés
- Anniversaires / jalons Jules
- Tâches ménage en retard
- Fin de conservation batch cooking
- Alertes budget
"""

import logging
from datetime import date, datetime, timedelta

import streamlit as st

from src.ui.fragments import auto_refresh
from src.ui.keys import KeyNamespace
from src.ui.tokens import Couleur
from src.ui.tokens_semantic import Sem

logger = logging.getLogger(__name__)

_keys = KeyNamespace("rappels_contextuels")


# ═══════════════════════════════════════════════════════════
# COLLECTE DES RAPPELS
# ═══════════════════════════════════════════════════════════


def _collecter_rappels() -> list[dict]:
    """Collecte tous les rappels contextuels depuis les différentes sources.

    Returns:
        Liste de dicts {icone, titre, detail, priorite, module}.
    """
    rappels = []

    aujourdhui = date.today()
    demain = aujourdhui + timedelta(days=1)

    # ── RDV de demain ──
    try:
        from src.modules.planning.timeline_ui import charger_events_periode

        events_demain = charger_events_periode(demain, demain + timedelta(days=1))
        if events_demain:
            for event in events_demain[:3]:
                titre_event = event.get("titre", "Événement")
                heure = ""
                if hasattr(event.get("date_debut"), "strftime"):
                    heure = f" à {event['date_debut'].strftime('%H:%M')}"
                rappels.append(
                    {
                        "icone": "📅",
                        "titre": f"{titre_event}{heure} demain",
                        "detail": event.get("lieu", ""),
                        "priorite": "haute",
                        "module": "planning.calendrier",
                    }
                )
    except Exception as e:
        logger.debug(f"Événements demain indisponibles: {e}")

    # ── Stocks critiques détaillés ──
    try:
        from src.services.inventaire import obtenir_service_inventaire

        inventaire = obtenir_service_inventaire().get_inventaire_complet()
        critiques = [a for a in inventaire if a.get("statut") in ("critique", "sous_seuil")]

        for art in critiques[:5]:
            nom = art.get("ingredient_nom", art.get("nom", "Article"))
            quantite = art.get("quantite", 0)
            unite = art.get("unite", "")
            rappels.append(
                {
                    "icone": "🛒",
                    "titre": f"Stock bas : {nom}",
                    "detail": f"Reste {quantite} {unite}" if quantite else "Épuisé",
                    "priorite": "haute" if art.get("statut") == "critique" else "moyenne",
                    "module": "cuisine.inventaire",
                }
            )

        # Péremption proche
        peremption = [a for a in inventaire if a.get("statut") == "peremption_proche"]
        for art in peremption[:3]:
            nom = art.get("ingredient_nom", art.get("nom", "Article"))
            jours = art.get("jours_avant_peremption", "?")
            rappels.append(
                {
                    "icone": "⏳",
                    "titre": f"{nom} périme bientôt",
                    "detail": f"Dans {jours} jour(s)",
                    "priorite": "haute",
                    "module": "cuisine.inventaire",
                }
            )
    except Exception as e:
        logger.debug(f"Inventaire indisponible: {e}")

    # ── Jules — jalons et anniversaire mensuel ──
    try:
        from src.core.constants import JULES_NAISSANCE

        # Calcul de l'âge en mois calendaires (précis)
        mois_age = (aujourdhui.year - JULES_NAISSANCE.year) * 12 + (
            aujourdhui.month - JULES_NAISSANCE.month
        )
        if aujourdhui.day < JULES_NAISSANCE.day:
            mois_age -= 1
        mois_age = max(0, mois_age)

        # Vérifier si c'est exactement le jour d'anniversaire mensuel
        # (même jour du mois que la naissance, ou dernier jour du mois si
        #  le jour de naissance n'existe pas dans le mois courant)
        import calendar

        dernier_jour_mois = calendar.monthrange(aujourdhui.year, aujourdhui.month)[1]
        jour_pivot = min(JULES_NAISSANCE.day, dernier_jour_mois)
        est_moisiversaire = aujourdhui.day == jour_pivot

        if est_moisiversaire:
            rappels.append(
                {
                    "icone": "🎂",
                    "titre": f"Jules a {mois_age} mois aujourd'hui ! 🎉",
                    "detail": "Un nouveau mois de découvertes",
                    "priorite": "moyenne",
                    "module": "famille.jules",
                }
            )

        # Jalons de développement importants (seulement le jour exact)
        jalons_importants = {
            18: "Premiers mots combinés, autonomie croissante",
            20: "Marche assurée, vocabulaire de ~50 mots",
            21: "Début d'association de 2 mots",
            24: "Grande étape — 2 ans !",
        }
        if est_moisiversaire and mois_age in jalons_importants:
            rappels.append(
                {
                    "icone": "⭐",
                    "titre": f"Jalon développement : {mois_age} mois",
                    "detail": jalons_importants[mois_age],
                    "priorite": "basse",
                    "module": "famille.jules",
                }
            )
    except Exception as e:
        logger.debug(f"Jules indisponible: {e}")

    # ── Tâches ménage en retard ──
    try:
        from src.services.accueil_data_service import get_accueil_data_service

        taches = get_accueil_data_service().get_taches_en_retard(limit=5)
        if taches:
            for t in taches[:3]:
                rappels.append(
                    {
                        "icone": "🧹",
                        "titre": f"{t['nom']} en retard",
                        "detail": f"{t['jours_retard']}j de retard",
                        "priorite": "haute" if t["jours_retard"] > 7 else "moyenne",
                        "module": "maison.entretien",
                    }
                )
    except Exception:
        pass

    # ── Batch cooking — conservation ──
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import SessionBatchCooking

        with obtenir_contexte_db() as session:
            sessions_actives = (
                session.query(SessionBatchCooking)
                .filter(SessionBatchCooking.statut == "termine")
                .all()
            )
            for s in sessions_actives:
                if hasattr(s, "date_fin") and s.date_fin:
                    # Conservation typique 3-5 jours frigo
                    fin_conservation = s.date_fin + timedelta(days=4)
                    jours_restants = (fin_conservation - aujourdhui).days
                    if 0 <= jours_restants <= 2:
                        rappels.append(
                            {
                                "icone": "🍱",
                                "titre": "Batch cooking à consommer",
                                "detail": f"Conservation fin dans {jours_restants}j",
                                "priorite": "haute",
                                "module": "cuisine.batch_cooking",
                            }
                        )
    except Exception:
        pass

    # ── Budget — alerte dépassement ──
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import BudgetMensuelDB, Depense

        mois_courant = aujourdhui.replace(day=1)
        with obtenir_contexte_db() as session:
            budget = (
                session.query(BudgetMensuelDB).filter(BudgetMensuelDB.mois == mois_courant).first()
            )
            if budget and budget.montant_prevu:
                from sqlalchemy import extract, func

                total_depenses = (
                    session.query(func.sum(Depense.montant))
                    .filter(
                        extract("month", Depense.date_depense) == aujourdhui.month,
                        extract("year", Depense.date_depense) == aujourdhui.year,
                    )
                    .scalar()
                ) or 0

                ratio = (total_depenses / budget.montant_prevu) * 100
                if ratio > 90:
                    rappels.append(
                        {
                            "icone": "💸",
                            "titre": f"Budget à {ratio:.0f}% !",
                            "detail": f"{total_depenses:.0f}€ / {budget.montant_prevu:.0f}€",
                            "priorite": "haute",
                            "module": "maison.depenses",
                        }
                    )
                elif ratio > 75:
                    rappels.append(
                        {
                            "icone": "💰",
                            "titre": f"Budget à {ratio:.0f}%",
                            "detail": f"{total_depenses:.0f}€ / {budget.montant_prevu:.0f}€",
                            "priorite": "moyenne",
                            "module": "maison.depenses",
                        }
                    )
    except Exception:
        pass

    # Trier par priorité
    priorites = {"haute": 0, "moyenne": 1, "basse": 2}
    rappels.sort(key=lambda r: priorites.get(r.get("priorite", "basse"), 2))

    return rappels


# ═══════════════════════════════════════════════════════════
# WIDGET UI
# ═══════════════════════════════════════════════════════════


@auto_refresh(seconds=120)
def afficher_rappels_contextuels():
    """Affiche les rappels contextuels enrichis."""
    from src.core.state import GestionnaireEtat, rerun

    rappels = _collecter_rappels()
    # Guard: ensure we have a list (some sources might return False/None)
    if not isinstance(rappels, list):
        logger.debug(f"Rappels non-list reçu: {rappels!r}")
        return

    if not rappels:
        return  # Pas de rappels, pas d'affichage

    st.markdown("### 🔔 Rappels")

    for rappel in rappels:
        _couleur = {
            "haute": Couleur.RED_500,
            "moyenne": Couleur.ORANGE,
            "basse": Couleur.INFO,
        }.get(rappel.get("priorite", "basse"), Couleur.INFO)

        col_content, col_action = st.columns([5, 1])

        with col_content:
            detail_val = rappel.get("detail")
            detail_html = f"— {detail_val}" if detail_val else ""
            small_detail = (
                f'<div><span style="color: {Sem.ON_SURFACE_SECONDARY}; font-size: 0.85rem; display:block; margin-top:4px;">{detail_html}</span></div>'
                if detail_html
                else ""
            )
            # build safe HTML block for the reminder
            html = (
                f'<div style="padding: 6px 10px; margin: 3px 0; '
                f'background: {Sem.SURFACE_ALT}; border-radius: 6px; '
                f'border-left: 3px solid {_couleur};">'
                f'<div style="white-space:nowrap;">{rappel["icone"]} <strong>{rappel["titre"]}</strong></div>'
                f"{small_detail}"
                f"</div>"
            )
            st.markdown(html, unsafe_allow_html=True)

        with col_action:
            module = rappel.get("module")
            if module:
                # Libellé lisible à partir de la clé de module
                _label_module = module.split(".")[-1].capitalize()
                if st.button(
                    "↗",
                    key=_keys("nav", module, rappel["titre"][:10]),
                    help=f"Voir dans {_label_module}",
                    use_container_width=True,
                ):
                    GestionnaireEtat.naviguer_vers(module)
                    rerun()


__all__ = ["afficher_rappels_contextuels"]
