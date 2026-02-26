"""
Module Calendrier Événements Jeux — Vue chronologique des tirages et matchs

Fonctionnalités:
- Timeline des prochains tirages (Loto lun/mer/sam, Euromillions mar/ven)
- Matchs importants de la semaine
- Jackpots estimés
- Filtrage par type d'événement
"""

import logging
from datetime import date, datetime, timedelta

import streamlit as st

from src.core.decorators import avec_session_db
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)
_keys = KeyNamespace("calendrier_jeux")


# ═══════════════════════════════════════════════════════════
# Calendrier des tirages récurrents
# ═══════════════════════════════════════════════════════════

JOURS_LOTO = {0: "Lundi", 2: "Mercredi", 5: "Samedi"}
JOURS_EURO = {1: "Mardi", 4: "Vendredi"}

_JOURS_FR = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche",
]
_MOIS_FR = [
    "",
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
]


def _format_date_fr(d: date) -> str:
    """Formate une date en français."""
    return f"{_JOURS_FR[d.weekday()]} {d.day} {_MOIS_FR[d.month]} {d.year}"


def _prochains_tirages(nb: int = 10) -> list[dict]:
    """Calcule les prochains tirages Loto et Euromillions."""
    tirages = []
    jour = date.today()

    while len(tirages) < nb:
        wd = jour.weekday()

        if wd in JOURS_LOTO:
            tirages.append(
                {
                    "date": jour,
                    "type": "🎱 Loto",
                    "jour": JOURS_LOTO[wd],
                    "heure": "20h30",
                }
            )

        if wd in JOURS_EURO:
            tirages.append(
                {
                    "date": jour,
                    "type": "⭐ Euromillions",
                    "jour": JOURS_EURO[wd],
                    "heure": "21h00",
                }
            )

        jour += timedelta(days=1)

    return sorted(tirages, key=lambda x: x["date"])[:nb]


# ═══════════════════════════════════════════════════════════
# Matchs depuis la BD
# ═══════════════════════════════════════════════════════════


@avec_session_db
def _prochains_matchs(jours: int = 7, db=None) -> list[dict]:
    """Charge les prochains matchs depuis la BD."""
    from src.core.models.jeux import Match

    date_limite = date.today() + timedelta(days=jours)
    rows = (
        db.query(Match)
        .filter(Match.date_match >= date.today(), Match.date_match <= date_limite)
        .order_by(Match.date_match.asc())
        .all()
    )
    return [
        {
            "date": r.date_match if isinstance(r.date_match, date) else r.date_match.date(),
            "type": "⚽ Match",
            "description": (
                f"{r.equipe_domicile.nom if r.equipe_domicile else '?'} vs "
                f"{r.equipe_exterieur.nom if r.equipe_exterieur else '?'}"
            ),
            "championnat": r.championnat or "",
            "cote_dom": float(r.cote_domicile) if r.cote_domicile else None,
            "heure": (r.date_match.strftime("%H:%M") if isinstance(r.date_match, datetime) else ""),
        }
        for r in rows
    ]


# ═══════════════════════════════════════════════════════════
# Fusion et affichage
# ═══════════════════════════════════════════════════════════


def _fusionner_evenements(tirages: list[dict], matchs: list[dict]) -> list[dict]:
    """Fusionne et trie tous les événements par date."""
    return sorted(tirages + matchs, key=lambda x: x["date"])


def _afficher_timeline(events: list[dict]) -> None:
    """Affiche la timeline des événements."""
    if not events:
        st.info("Aucun événement à venir")
        return

    date_courante = None

    for ev in events:
        ev_date = ev["date"]

        # Header par jour
        if ev_date != date_courante:
            date_courante = ev_date
            delta = (ev_date - date.today()).days

            if delta == 0:
                jour_relatif = " — **Aujourd'hui**"
            elif delta == 1:
                jour_relatif = " — Demain"
            elif delta <= 7:
                jour_relatif = f" — Dans {delta} jours"
            else:
                jour_relatif = ""

            st.subheader(f"📅 {_format_date_fr(ev_date)}{jour_relatif}")

        # Contenu événement
        col_icon, col_info = st.columns([1, 5])
        with col_icon:
            st.markdown(f"### {ev['type'].split(' ')[0]}")

        with col_info:
            if "description" in ev:
                st.markdown(f"**{ev['type']}** — {ev['description']}")
                if ev.get("championnat"):
                    st.caption(f"🏆 {ev['championnat']}")
                if ev.get("cote_dom") is not None:
                    st.caption(f"Cote dom: {ev['cote_dom']:.2f}")
            else:
                st.markdown(f"**{ev['type']}** — {ev.get('heure', '')}")

        st.divider()


def _afficher_resume(tirages: list[dict], matchs: list[dict]) -> None:
    """Résumé de la semaine."""
    col1, col2, col3 = st.columns(3)
    col1.metric("🎱 Tirages", len(tirages))
    col2.metric("⚽ Matchs", len(matchs))
    col3.metric("📊 Total", len(tirages) + len(matchs))

    events = _fusionner_evenements(tirages, matchs)
    if events:
        prochain = events[0]
        delta = (prochain["date"] - date.today()).days
        label_event = prochain.get("description", prochain.get("heure", ""))
        st.info(
            f"⏰ Prochain: **{prochain['type']}** "
            f"{'— ' + label_event + ' ' if label_event else ''}"
            f"dans **{delta} jour(s)** ({prochain['date'].strftime('%d/%m')})"
        )


# ═══════════════════════════════════════════════════════════
# Point d'entrée
# ═══════════════════════════════════════════════════════════


@profiler_rerun("calendrier_jeux")
def app():
    """Point d'entrée du module Calendrier."""
    st.title("📅 Calendrier des Événements Jeux")
    st.caption("Prochains tirages Loto/Euromillions et matchs importants")

    with error_boundary("calendrier_jeux"):
        horizon = st.slider("Horizon (jours)", 3, 30, 14, key=_keys("horizon"))

        tirages = _prochains_tirages(nb=horizon)
        matchs = _prochains_matchs(jours=horizon)

        _afficher_resume(tirages, matchs)
        st.divider()

        # Filtres
        types = st.multiselect(
            "Types d'événements",
            ["🎱 Loto", "⭐ Euromillions", "⚽ Match"],
            default=["🎱 Loto", "⭐ Euromillions", "⚽ Match"],
            key=_keys("types"),
        )

        tirages_filtre = [t for t in tirages if t["type"] in types]
        matchs_filtre = [m for m in matchs if m["type"] in types]

        events = _fusionner_evenements(tirages_filtre, matchs_filtre)
        _afficher_timeline(events)


def main():
    app()


__all__ = ["app", "main"]
