"""
Fonctions helpers pour charger les données depuis la BD.
"""

from ._common import (
    st, date, timedelta, logger,
    get_session, Equipe, Match, PariSportif,
    CHAMPIONNATS,
)


def charger_championnats_disponibles():
    """Retourne la liste des championnats disponibles"""
    return CHAMPIONNATS


def charger_equipes(championnat: str = None):
    """Charge les équipes, optionnellement filtrées par championnat"""
    try:
        with get_session() as session:
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
                    "points": (e.victoires or 0) * 3 + (e.nuls or 0)
                }
                for e in equipes
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement équipes: {e}")
        return []


def charger_matchs_a_venir(jours: int = 7, championnat: str = None):
    """Charge les matchs à venir depuis la BD"""
    try:
        with get_session() as session:
            date_limite = date.today() + timedelta(days=jours)
            
            query = session.query(Match).filter(
                Match.date_match >= date.today(),
                Match.date_match <= date_limite,
                Match.joue == False
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
                    "cote_ext": m.cote_ext
                }
                for m in matchs
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement matchs: {e}")
        return []


def charger_matchs_recents(equipe_id: int, nb_matchs: int = 10):
    """Charge les derniers matchs joués par une équipe"""
    try:
        with get_session() as session:
            matchs = session.query(Match).filter(
                (Match.equipe_domicile_id == equipe_id) | 
                (Match.equipe_exterieur_id == equipe_id),
                Match.joue == True
            ).order_by(Match.date_match.desc()).limit(nb_matchs).all()
            
            return [
                {
                    "id": m.id,
                    "date": m.date_match,
                    "equipe_domicile_id": m.equipe_domicile_id,
                    "equipe_exterieur_id": m.equipe_exterieur_id,
                    "score_domicile": m.score_domicile,
                    "score_exterieur": m.score_exterieur
                }
                for m in reversed(matchs)  # Du plus ancien au plus récent
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement matchs récents: {e}")
        return []


def charger_paris_utilisateur(statut: str = None):
    """Charge les paris de l'utilisateur"""
    try:
        with get_session() as session:
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
                    "date": p.cree_le
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
