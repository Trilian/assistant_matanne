"""
Synchronisation des paris sportifs avec les données API.

Mixin extrait de ParisCrudService (Phase 4 Audit, item 18 — split >500 LOC).
Contient les méthodes de synchronisation API → BD.
"""

import logging
from datetime import date

from sqlalchemy.orm import Session, joinedload

from src.core.decorators import avec_session_db
from src.core.models import Equipe, Match
from src.services.core.event_bus_mixin import emettre_evenement_simple

logger = logging.getLogger(__name__)


class ParisSyncMixin:
    """Mixin pour la synchronisation API → BD."""

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

        if count > 0:
            emettre_evenement_simple(
                "paris.modifie",
                {"element_id": 0, "type_element": "equipe", "action": "sync", "count": count},
                source="paris_sync",
            )
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

            emettre_evenement_simple(
                "paris.modifie",
                {"element_id": 0, "type_element": "match", "action": "sync", "count": count},
                source="paris_sync",
            )

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

            emettre_evenement_simple(
                "paris.modifie",
                {
                    "element_id": 0,
                    "type_element": "resultat",
                    "action": "scores_maj",
                    "count": count,
                },
                source="paris_sync",
            )

        return count
