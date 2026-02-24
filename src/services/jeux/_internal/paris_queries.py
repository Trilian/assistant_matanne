"""
Opérations de lecture pour les paris sportifs.

Mixin extrait de ParisCrudService (Phase 4 Audit, item 18 — split >500 LOC).
Contient toutes les méthodes charger_* (queries + fallback BD).
"""

import logging
from datetime import date, timedelta

from sqlalchemy.orm import Session, joinedload

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import Equipe, Match, PariSportif

logger = logging.getLogger(__name__)


class ParisQueryMixin:
    """Mixin pour les opérations de lecture paris/matchs/équipes."""

    # ── Lecture ──────────────────────────────────────────

    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def charger_equipes(
        self, championnat: str | None = None, db: Session | None = None
    ) -> list[dict]:
        """Charge les équipes, optionnellement filtrées par championnat.

        Args:
            championnat: Filtre optionnel par championnat

        Returns:
            Liste de dictionnaires équipe
        """
        query = db.query(Equipe)
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

    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def charger_matchs_a_venir(
        self, jours: int = 7, championnat: str | None = None, db: Session | None = None
    ) -> list[dict]:
        """Charge les matchs à venir depuis la BD.

        Args:
            jours: Nombre de jours à venir
            championnat: Filtre optionnel

        Returns:
            Liste de dictionnaires match
        """
        date_limite = date.today() + timedelta(days=jours)

        query = db.query(Match).filter(
            Match.date_match >= date.today(),
            Match.date_match <= date_limite,
            Match.joue == False,
        )

        if championnat:
            query = query.filter(Match.championnat == championnat)

        matchs = (
            query.options(
                joinedload(Match.equipe_domicile),
                joinedload(Match.equipe_exterieur),
            )
            .order_by(Match.date_match)
            .all()
        )

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

    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def charger_matchs_recents(
        self, equipe_id: int, nb_matchs: int = 10, db: Session | None = None
    ) -> list[dict]:
        """Charge les derniers matchs joués par une équipe.

        Args:
            equipe_id: ID de l'équipe
            nb_matchs: Nombre de matchs à charger

        Returns:
            Liste de dicts du plus ancien au plus récent
        """
        matchs = (
            db.query(Match)
            .filter(
                (Match.equipe_domicile_id == equipe_id) | (Match.equipe_exterieur_id == equipe_id),
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
            for m in reversed(matchs)
        ]

    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def charger_paris_utilisateur(
        self, statut: str | None = None, db: Session | None = None
    ) -> list[dict]:
        """Charge les paris de l'utilisateur.

        Args:
            statut: Filtre optionnel (en_attente, gagne, perdu)

        Returns:
            Liste de dictionnaires pari
        """
        query = db.query(PariSportif)
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

    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def charger_matchs_passes_non_joues(self, db: Session | None = None) -> list[dict]:
        """Charge les matchs passés non encore joués (pour enregistrer les résultats).

        Returns:
            Liste de dicts match avec noms d'équipes
        """
        matchs = (
            db.query(Match)
            .options(joinedload(Match.equipe_domicile), joinedload(Match.equipe_exterieur))
            .filter(Match.date_match <= date.today(), Match.joue == False)
            .all()
        )
        return [
            {
                "id": m.id,
                "date_match": m.date_match,
                "dom_nom": m.equipe_domicile.nom if m.equipe_domicile else "?",
                "ext_nom": m.equipe_exterieur.nom if m.equipe_exterieur else "?",
            }
            for m in matchs
        ]

    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def charger_matchs_recents_tous(
        self, limite: int = 50, championnat: str | None = None, db: Session | None = None
    ) -> list[dict]:
        """Charge les matchs récents (pour la page suppression).

        Args:
            limite: Nombre max de matchs
            championnat: Filtre optionnel (None = tous)

        Returns:
            Liste de dicts match
        """
        query = (
            db.query(Match)
            .options(joinedload(Match.equipe_domicile), joinedload(Match.equipe_exterieur))
            .order_by(Match.date_match.desc())
        )
        if championnat:
            query = query.filter(Match.championnat == championnat)
        matchs = query.limit(limite).all()
        return [
            {
                "id": m.id,
                "date_match": m.date_match,
                "championnat": m.championnat,
                "dom_nom": m.equipe_domicile.nom if m.equipe_domicile else "?",
                "ext_nom": m.equipe_exterieur.nom if m.equipe_exterieur else "?",
                "joue": m.joue,
                "score_domicile": m.score_domicile,
                "score_exterieur": m.score_exterieur,
            }
            for m in matchs
        ]

    # ── Fallback BD ──────────────────────────────────────

    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def charger_matchs_fallback(
        self, championnat: str, jours: int = 7, db: Session | None = None
    ) -> list[dict]:
        """Charge les matchs depuis la BD (fallback quand l'API échoue).

        Returns:
            Liste de dicts compatibles API
        """
        debut = date.today()
        fin = debut + timedelta(days=jours)

        matchs = (
            db.query(Match)
            .options(joinedload(Match.equipe_domicile), joinedload(Match.equipe_exterieur))
            .filter(
                Match.date_match >= debut,
                Match.date_match <= fin,
                Match.championnat == championnat,
                Match.joue == False,
            )
            .order_by(Match.date_match, Match.heure)
            .all()
        )

        return [
            {
                "id": m.id,
                "date": str(m.date_match),
                "heure": str(m.heure) if m.heure else "",
                "championnat": m.championnat,
                "dom_nom": m.equipe_domicile.nom if m.equipe_domicile else "?",
                "ext_nom": m.equipe_exterieur.nom if m.equipe_exterieur else "?",
                "cote_dom": m.cote_domicile or 1.8,
                "cote_nul": m.cote_nul or 3.5,
                "cote_ext": m.cote_exterieur or 4.2,
                "source": "BD",
            }
            for m in matchs
        ]

    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def charger_classement_fallback(
        self, championnat: str, db: Session | None = None
    ) -> list[dict]:
        """Charge le classement depuis la BD (fallback quand l'API échoue).

        Returns:
            Liste de dicts classement
        """
        equipes = (
            db.query(Equipe)
            .filter_by(championnat=championnat)
            .order_by(Equipe.points.desc(), Equipe.buts_marques.desc())
            .all()
        )

        return [
            {
                "position": i,
                "nom": e.nom,
                "matchs_joues": e.matchs_joues,
                "victoires": e.victoires,
                "nuls": e.nuls,
                "defaites": e.defaites,
                "buts_marques": e.buts_marques,
                "buts_encaisses": e.buts_encaisses,
                "points": e.points,
            }
            for i, e in enumerate(equipes, 1)
        ]

    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def charger_historique_equipe_fallback(
        self, nom_equipe: str, db: Session | None = None
    ) -> list[dict]:
        """Charge l'historique d'une équipe depuis la BD (fallback).

        Returns:
            Liste de dicts match joué
        """
        matches = (
            db.query(Match)
            .options(joinedload(Match.equipe_domicile), joinedload(Match.equipe_exterieur))
            .filter(
                (Match.equipe_domicile.has(nom=nom_equipe))
                | (Match.equipe_exterieur.has(nom=nom_equipe))
            )
            .filter(Match.joue == True)
            .order_by(Match.date_match.desc())
            .limit(10)
            .all()
        )

        return [
            {
                "date": str(m.date_match),
                "equipe_domicile": m.equipe_domicile.nom if m.equipe_domicile else "?",
                "equipe_exterieur": m.equipe_exterieur.nom if m.equipe_exterieur else "?",
                "score_domicile": m.score_domicile,
                "score_exterieur": m.score_exterieur,
            }
            for m in matches
        ]
