"""
ParisCrudService - Opérations CRUD et sync pour les paris sportifs.

Regroupe la logique de base de données auparavant dispersée dans:
- src/modules/jeux/paris/crud.py
- src/modules/jeux/paris/utils.py
- src/modules/jeux/paris/sync.py
- src/modules/jeux/paris/gestion.py

Utilisation:
    service = get_paris_crud_service()
    equipes = service.charger_equipes("Ligue 1")
    service.enregistrer_pari(match_id=1, prediction="1", cote=1.8)
"""

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session, joinedload

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import Equipe, Match, PariSportif
from src.services.core.base import BaseService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════


class ParisCrudService(BaseService[PariSportif]):
    """Service CRUD pour les paris sportifs, équipes et matchs.

    Hérite de BaseService[PariSportif] pour le CRUD générique sur les paris.
    Les méthodes spécialisées gèrent les relations Match/Equipe/PariSportif.
    """

    def __init__(self):
        super().__init__(model=PariSportif, cache_ttl=60)

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

    # ── Écriture ────────────────────────────────────────

    @avec_session_db
    def enregistrer_pari(
        self,
        match_id: int,
        prediction: str,
        cote: float,
        mise: float = 0,
        est_virtuel: bool = True,
        db: Session | None = None,
    ) -> bool:
        """Enregistre un nouveau pari.

        Returns:
            True si enregistrement réussi
        """
        pari = PariSportif(
            match_id=match_id,
            type_pari="1N2",
            prediction=prediction,
            cote=cote,
            mise=Decimal(str(mise)),
            est_virtuel=est_virtuel,
            statut="en_attente",
        )
        db.add(pari)
        db.commit()
        return True

    @avec_session_db
    def ajouter_equipe(self, nom: str, championnat: str, db: Session | None = None) -> bool:
        """Ajoute une nouvelle équipe.

        Returns:
            True si ajout réussi
        """
        equipe = Equipe(nom=nom, championnat=championnat)
        db.add(equipe)
        db.commit()
        return True

    @avec_session_db
    def ajouter_match(
        self,
        equipe_dom_id: int,
        equipe_ext_id: int,
        championnat: str,
        date_match: date,
        heure: str | None = None,
        db: Session | None = None,
    ) -> bool:
        """Ajoute un nouveau match.

        Returns:
            True si ajout réussi
        """
        match = Match(
            equipe_domicile_id=equipe_dom_id,
            equipe_exterieur_id=equipe_ext_id,
            championnat=championnat,
            date_match=date_match,
            heure=heure,
            joue=False,
        )
        db.add(match)
        db.commit()
        return True

    @avec_session_db
    def enregistrer_resultat_match(
        self,
        match_id: int,
        score_dom: int,
        score_ext: int,
        db: Session | None = None,
    ) -> bool:
        """Enregistre le résultat d'un match et résout les paris liés.

        Returns:
            True si enregistrement réussi
        """
        match = db.query(Match).get(match_id)
        if not match:
            return False

        match.score_domicile = score_dom
        match.score_exterieur = score_ext
        match.joue = True

        # Déterminer le résultat
        if score_dom > score_ext:
            match.resultat = "1"
        elif score_ext > score_dom:
            match.resultat = "2"
        else:
            match.resultat = "N"

        # Mettre à jour les paris liés
        for pari in match.paris:
            if pari.statut == "en_attente":
                if pari.prediction == match.resultat:
                    pari.statut = "gagne"
                    pari.gain = pari.mise * Decimal(str(pari.cote))
                else:
                    pari.statut = "perdu"
                    pari.gain = Decimal("0")

        db.commit()
        return True

    @avec_session_db
    def supprimer_match(self, match_id: int, db: Session | None = None) -> bool:
        """Supprime un match et ses paris associés.

        Returns:
            True si suppression réussie
        """
        match = db.query(Match).get(match_id)
        if not match:
            logger.warning(f"Match {match_id} non trouvé")
            return False

        for pari in match.paris:
            db.delete(pari)

        db.delete(match)
        db.commit()
        logger.info(f"🗑️ Match {match_id} supprimé")
        return True

    # ── Synchronisation ─────────────────────────────────

    @avec_session_db
    def sync_equipes_depuis_api(
        self,
        championnat: str,
        classement: list[dict],
        db: Session | None = None,
    ) -> int:
        """Synchronise les équipes depuis les données API.

        Args:
            championnat: Nom du championnat
            classement: Données API du classement

        Returns:
            Nombre d'équipes ajoutées/mises à jour
        """
        count = 0
        for equipe_api in classement:
            try:
                equipe = (
                    db.query(Equipe)
                    .filter(Equipe.nom == equipe_api["nom"], Equipe.championnat == championnat)
                    .first()
                )

                if equipe:
                    equipe.matchs_joues = equipe_api.get("matchs_joues", equipe.matchs_joues)
                    equipe.victoires = equipe_api.get("victoires", equipe.victoires)
                    equipe.nuls = equipe_api.get("nuls", equipe.nuls)
                    equipe.defaites = equipe_api.get("defaites", equipe.defaites)
                    equipe.buts_marques = equipe_api.get("buts_marques", equipe.buts_marques)
                    equipe.buts_encaisses = equipe_api.get("buts_encaisses", equipe.buts_encaisses)
                else:
                    equipe = Equipe(
                        nom=equipe_api["nom"],
                        championnat=championnat,
                        matchs_joues=equipe_api.get("matchs_joues", 0),
                        victoires=equipe_api.get("victoires", 0),
                        nuls=equipe_api.get("nuls", 0),
                        defaites=equipe_api.get("defaites", 0),
                        buts_marques=equipe_api.get("buts_marques", 0),
                        buts_encaisses=equipe_api.get("buts_encaisses", 0),
                    )
                    db.add(equipe)
                count += 1
            except Exception as e:
                logger.debug(f"Erreur equipe {equipe_api.get('nom')}: {e}")
                continue

        try:
            db.commit()
        except Exception as e:
            logger.error(f"Erreur commit equipes: {e}")
            db.rollback()

        return count

    @avec_session_db
    def sync_matchs_a_venir(
        self,
        championnat: str,
        matchs_api: list[dict],
        db: Session | None = None,
    ) -> int:
        """Synchronise les matchs à venir depuis les données API.

        Args:
            championnat: Nom du championnat
            matchs_api: Données API des matchs

        Returns:
            Nombre de matchs ajoutés
        """
        count = 0
        for match_api in matchs_api:
            dom_nom = match_api.get("equipe_domicile", "")
            ext_nom = match_api.get("equipe_exterieur", "")
            date_match = match_api.get("date")

            if not dom_nom or not ext_nom or not date_match:
                continue

            dom = (
                db.query(Equipe)
                .filter(Equipe.nom.ilike(f"%{dom_nom}%"), Equipe.championnat == championnat)
                .first()
            )
            ext = (
                db.query(Equipe)
                .filter(Equipe.nom.ilike(f"%{ext_nom}%"), Equipe.championnat == championnat)
                .first()
            )

            if not dom or not ext:
                continue

            existing = (
                db.query(Match)
                .filter(
                    Match.equipe_domicile_id == dom.id,
                    Match.equipe_exterieur_id == ext.id,
                    Match.date_match == date_match,
                )
                .first()
            )
            if existing:
                continue

            nouveau_match = Match(
                equipe_domicile_id=dom.id,
                equipe_exterieur_id=ext.id,
                championnat=championnat,
                date_match=date_match,
                heure=match_api.get("heure"),
                cote_dom=match_api.get("cote_domicile"),
                cote_nul=match_api.get("cote_nul"),
                cote_ext=match_api.get("cote_exterieur"),
                joue=False,
            )
            db.add(nouveau_match)
            count += 1

        if count > 0:
            db.commit()

        return count

    @avec_session_db
    def refresh_scores_matchs(
        self,
        matchs_api_par_champ: dict[str, list[dict]],
        db: Session | None = None,
    ) -> int:
        """Met à jour les scores des matchs terminés.

        Args:
            matchs_api_par_champ: {championnat: [matchs_terminés_api]}

        Returns:
            Nombre de matchs mis à jour
        """
        matchs_a_maj = (
            db.query(Match)
            .options(joinedload(Match.equipe_domicile), joinedload(Match.equipe_exterieur))
            .filter(Match.joue == False, Match.date_match < date.today())
            .all()
        )

        if not matchs_a_maj:
            return 0

        count = 0
        for match_bd in matchs_a_maj:
            matchs_api = matchs_api_par_champ.get(match_bd.championnat, [])
            dom_nom = match_bd.equipe_domicile.nom if match_bd.equipe_domicile else ""
            ext_nom = match_bd.equipe_exterieur.nom if match_bd.equipe_exterieur else ""

            for match_api in matchs_api:
                api_dom = match_api.get("equipe_domicile", "")
                api_ext = match_api.get("equipe_exterieur", "")

                if (dom_nom.lower() in api_dom.lower() or api_dom.lower() in dom_nom.lower()) and (
                    ext_nom.lower() in api_ext.lower() or api_ext.lower() in ext_nom.lower()
                ):
                    score_d = match_api.get("score_domicile")
                    score_e = match_api.get("score_exterieur")

                    if score_d is not None and score_e is not None:
                        match_bd.score_domicile = score_d
                        match_bd.score_exterieur = score_e
                        match_bd.joue = True
                        count += 1
                    break

        if count > 0:
            db.commit()
            logger.info(f"✅ {count} matchs mis à jour avec scores")

        return count


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════

_instance: ParisCrudService | None = None


@service_factory("paris_crud", tags={"jeux", "crud", "paris"})
def get_paris_crud_service() -> ParisCrudService:
    """Factory pour ParisCrudService (singleton)."""
    global _instance
    if _instance is None:
        _instance = ParisCrudService()
    return _instance


def obtenir_service_paris_crud() -> ParisCrudService:
    """Alias français pour get_paris_crud_service."""
    return get_paris_crud_service()
