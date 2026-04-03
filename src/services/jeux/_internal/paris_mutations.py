"""
Opérations d'écriture pour les paris sportifs.

Mixin extrait de ParisCrudService (Audit qualité — split >500 LOC).
Contient les méthodes de création, mise à jour et suppression.
"""

import logging
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.core.models import Equipe, Match, PariSportif
from src.services.core.events import obtenir_bus

logger = logging.getLogger(__name__)


class ParisMutationMixin:
    """Mixin pour les opérations d'écriture paris/matchs/équipes."""

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

        # Émettre événement domaine
        obtenir_bus().emettre(
            "paris.modifie",
            {"element_id": pari.id, "type_element": "pari", "action": "enregistre"},
            source="paris",
        )

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

        # Émettre événement domaine
        obtenir_bus().emettre(
            "paris.modifie",
            {"element_id": equipe.id, "type_element": "equipe", "action": "ajoute"},
            source="paris",
        )

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

        # Émettre événement domaine
        obtenir_bus().emettre(
            "paris.modifie",
            {"element_id": match.id, "type_element": "match", "action": "ajoute"},
            source="paris",
        )

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

        # Émettre événement domaine
        obtenir_bus().emettre(
            "paris.modifie",
            {"element_id": match_id, "type_element": "resultat", "action": "resultat"},
            source="paris",
        )

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

        # Émettre événement domaine
        obtenir_bus().emettre(
            "paris.modifie",
            {"element_id": match_id, "type_element": "match", "action": "supprime"},
            source="paris",
        )

        logger.info(f"🗑️ Match {match_id} supprimé")
        return True
