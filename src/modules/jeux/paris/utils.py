"""
Imports communs et constantes pour le module paris sportifs.
"""

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.core.db import obtenir_contexte_db
from src.core.models import Equipe, HistoriqueJeux, Match, PariSportif

logger = logging.getLogger(__name__)

# Imports directs depuis le service unifié jeux
from src.services.jeux import charger_classement as api_charger_classement
from src.services.jeux import charger_historique_equipe, charger_matchs_termines
from src.services.jeux import charger_matchs_a_venir as api_charger_matchs_a_venir
from src.services.jeux import vider_cache as api_vider_cache

from .constants import CHAMPIONNATS, SEUIL_SERIE_SANS_NUL
from .forme import calculer_forme_equipe, calculer_historique_face_a_face
from .stats import analyser_tendances_championnat, calculer_performance_paris

__all__ = [
    "st",
    "date",
    "timedelta",
    "Decimal",
    "Dict",
    "pd",
    "go",
    "px",
    "logging",
    "obtenir_contexte_db",
    "Equipe",
    "Match",
    "PariSportif",
    "HistoriqueJeux",
    "logger",
    "CHAMPIONNATS",
    "calculer_forme_equipe",
    "calculer_historique_face_a_face",
    "calculer_performance_paris",
    "analyser_tendances_championnat",
    "SEUIL_SERIE_SANS_NUL",
    "api_charger_classement",
    "api_charger_matchs_a_venir",
    "charger_historique_equipe",
    "charger_matchs_termines",
    "api_vider_cache",
]

# ============================================================
# Fonctions importées depuis utilitaires.py
# ============================================================


def charger_championnats_disponibles():
    """Retourne la liste des championnats disponibles"""
    return CHAMPIONNATS


def charger_equipes(championnat: str = None):
    """Charge les equipes, optionnellement filtrees par championnat"""
    try:
        with obtenir_contexte_db() as session:
            query = session.query(Equipe)
            if championnat:
                query = query.filter(Equipe.championnat == championnat)
            equipes = query.order_by(Equipe.nom).all()
            return [
                {
                    "id": e.id,
                    "nom": e.nom,
                    "championnat": e.championnat,
                    "matchs_joues": e.matchs_joues or 0,
                    "victoires": e.victoires or 0,
                    "nuls": e.nuls or 0,
                    "defaites": e.defaites or 0,
                    "buts_marques": e.buts_marques or 0,
                    "buts_encaisses": e.buts_encaisses or 0,
                    "points": (e.victoires or 0) * 3 + (e.nuls or 0),
                }
                for e in equipes
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement equipes: {e}")
        return []


def charger_matchs_a_venir(jours: int = 7, championnat: str = None):
    """Charge les matchs à venir depuis la BD"""
    try:
        with obtenir_contexte_db() as session:
            date_limite = date.today() + timedelta(days=jours)

            query = session.query(Match).filter(
                Match.date_match >= date.today(),
                Match.date_match <= date_limite,
                Match.joue == False,
            )

            if championnat:
                query = query.filter(Match.championnat == championnat)

            matchs = query.order_by(Match.date_match).all()

            return [
                {
                    "id": m.id,
                    "date": m.date_match,
                    "heure": m.heure,
                    "championnat": m.championnat,
                    "equipe_domicile_id": m.equipe_domicile_id,
                    "equipe_exterieur_id": m.equipe_exterieur_id,
                    "dom_nom": m.equipe_domicile.nom if m.equipe_domicile else "?",
                    "ext_nom": m.equipe_exterieur.nom if m.equipe_exterieur else "?",
                    "cote_dom": m.cote_dom,
                    "cote_nul": m.cote_nul,
                    "cote_ext": m.cote_ext,
                }
                for m in matchs
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement matchs: {e}")
        return []


def charger_matchs_recents(equipe_id: int, nb_matchs: int = 10):
    """Charge les derniers matchs joues par une equipe"""
    try:
        with obtenir_contexte_db() as session:
            matchs = (
                session.query(Match)
                .filter(
                    (Match.equipe_domicile_id == equipe_id)
                    | (Match.equipe_exterieur_id == equipe_id),
                    Match.joue == True,
                )
                .order_by(Match.date_match.desc())
                .limit(nb_matchs)
                .all()
            )

            return [
                {
                    "id": m.id,
                    "date": m.date_match,
                    "equipe_domicile_id": m.equipe_domicile_id,
                    "equipe_exterieur_id": m.equipe_exterieur_id,
                    "score_domicile": m.score_domicile,
                    "score_exterieur": m.score_exterieur,
                }
                for m in reversed(matchs)  # Du plus ancien au plus recent
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement matchs recents: {e}")
        return []


def charger_paris_utilisateur(statut: str = None):
    """Charge les paris de l'utilisateur"""
    try:
        with obtenir_contexte_db() as session:
            query = session.query(PariSportif)
            if statut:
                query = query.filter(PariSportif.statut == statut)

            paris = query.order_by(PariSportif.cree_le.desc()).limit(100).all()

            return [
                {
                    "id": p.id,
                    "match_id": p.match_id,
                    "type_pari": p.type_pari,
                    "prediction": p.prediction,
                    "cote": p.cote,
                    "mise": p.mise,
                    "statut": p.statut,
                    "gain": p.gain,
                    "est_virtuel": p.est_virtuel,
                    "date": p.cree_le,
                }
                for p in paris
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement paris: {e}")
        return []


__all__ = [
    "charger_championnats_disponibles",
    "charger_equipes",
    "charger_matchs_a_venir",
    "charger_matchs_recents",
    "charger_paris_utilisateur",
]
