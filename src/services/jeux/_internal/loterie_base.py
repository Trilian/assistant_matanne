"""
Base commune pour les services CRUD de loterie (Loto, Euromillions).

Factorise les opérations CRUD identiques entre les jeux de type loterie:
- Insertion de tirages avec dédoublonnage
- Chargement de tirages
- Enregistrement de grilles
- Chargement de grilles

Chaque sous-classe définit les attributs de classe (_tirage_cls, _grille_cls,
_cout_defaut, _nom_jeu) et implémente les méthodes template pour les champs
spécifiques à chaque jeu (numéro chance pour le Loto, étoiles pour Euromillions).
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class LoterieCrudBase:
    """Opérations CRUD communes pour les jeux de loterie.

    Attributs de classe à définir dans les sous-classes:
        _tirage_cls: Modèle SQLAlchemy du tirage
        _grille_cls: Modèle SQLAlchemy de la grille
        _cout_defaut: Coût par défaut d'une grille
        _nom_jeu: Nom du jeu pour les logs
    """

    _tirage_cls: Any  # type: Modèle SQLAlchemy du tirage
    _grille_cls: Any  # type: Modèle SQLAlchemy de la grille
    _cout_defaut: Decimal = Decimal("0")
    _nom_jeu: str = "loterie"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    # ── Méthodes template (à surcharger) ─────────────────

    def _champs_secondaires_tirage(self, data: dict[str, Any]) -> dict[str, int] | None:
        """Extraire les champs secondaires d'un tirage depuis les données brutes.

        Retourne None si les données secondaires sont invalides/manquantes.
        """
        raise NotImplementedError

    def _champs_extra_tirage(self, data: dict[str, Any]) -> dict[str, Any]:
        """Champs supplémentaires spécifiques au jeu (ex: code_my_million)."""
        return {}

    def _serialiser_tirage(self, t: Any) -> dict[str, Any]:
        """Sérialiser un tirage ORM en dictionnaire."""
        raise NotImplementedError

    def _serialiser_grille(self, g: Any) -> dict[str, Any]:
        """Sérialiser une grille ORM en dictionnaire."""
        raise NotImplementedError

    # ── Utilitaires ──────────────────────────────────────

    @staticmethod
    def _parser_date(date_value: Any) -> date | None:
        """Parse une date depuis différents formats (ISO, FR)."""
        if isinstance(date_value, date):
            return date_value
        if isinstance(date_value, str):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.strptime(date_value, fmt).date()
                except ValueError:
                    continue
        return None

    # ── Implémentations communes ─────────────────────────

    def _inserer_tirages_impl(
        self, tirages: list[dict[str, Any]], db: Session | None
    ) -> int:
        """Insère des tirages avec dédoublonnage par date.

        Attend des dicts avec clés: date_tirage, numeros, + clés secondaires.
        """
        assert db is not None
        nb_ajoutes = 0
        for t in tirages:
            date_t = self._parser_date(t.get("date_tirage", ""))
            if not date_t:
                continue

            if db.query(self._tirage_cls).filter_by(date_tirage=date_t).first():
                continue

            numeros = t.get("numeros", [])
            if len(numeros) < 5:
                continue

            secondaires = self._champs_secondaires_tirage(t)
            if secondaires is None:
                continue

            numeros_tries = sorted(numeros[:5])
            tirage = self._tirage_cls(
                date_tirage=date_t,
                numero_1=numeros_tries[0],
                numero_2=numeros_tries[1],
                numero_3=numeros_tries[2],
                numero_4=numeros_tries[3],
                numero_5=numeros_tries[4],
                jackpot_euros=t.get("jackpot_euros"),
                **secondaires,
                **self._champs_extra_tirage(t),
            )
            db.add(tirage)
            nb_ajoutes += 1

        if nb_ajoutes:
            db.commit()
        logger.info(f"{nb_ajoutes} tirages {self._nom_jeu} insérés")
        return nb_ajoutes

    def _charger_tirages_impl(
        self, db: Session | None, limite: int | None = None
    ) -> list[dict[str, Any]]:
        """Charge les tirages triés par date décroissante."""
        assert db is not None
        query = db.query(self._tirage_cls).order_by(
            self._tirage_cls.date_tirage.desc()
        )
        if limite:
            query = query.limit(limite)
        return [self._serialiser_tirage(t) for t in query.all()]

    def _enregistrer_grille_impl(
        self,
        db: Session | None,
        numeros: list[int],
        champs_secondaires: dict[str, int],
        source: str = "manuel",
        est_virtuelle: bool = True,
        mise: Decimal | None = None,
        notes: str | None = None,
    ) -> int:
        """Enregistre une grille et retourne son ID."""
        assert db is not None
        numeros_tries = sorted(numeros)
        grille = self._grille_cls(
            numero_1=numeros_tries[0],
            numero_2=numeros_tries[1],
            numero_3=numeros_tries[2],
            numero_4=numeros_tries[3],
            numero_5=numeros_tries[4],
            source_prediction=source,
            est_virtuelle=est_virtuelle,
            mise=mise or self._cout_defaut,
            notes=notes,
            **champs_secondaires,
        )
        db.add(grille)
        db.commit()
        return grille.id

    def _charger_grilles_impl(
        self, db: Session | None, limite: int | None = None
    ) -> list[dict[str, Any]]:
        """Charge les grilles triées par date décroissante."""
        assert db is not None
        query = db.query(self._grille_cls).order_by(
            self._grille_cls.date_creation.desc()
        )
        if limite:
            query = query.limit(limite)
        return [self._serialiser_grille(g) for g in query.all()]
