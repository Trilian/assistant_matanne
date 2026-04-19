"""

LotoCrudService - Opérations CRUD pour les tirages et grilles Loto.



Regroupe la logique de base de données auparavant dispersée dans:

- src/modules/jeux/loto/crud.py

- src/modules/jeux/loto/utils.py

- src/modules/jeux/loto/sync.py

- src/modules/jeux/scraper_loto.py



Utilisation:

    service = obtenir_loto_crud_service()

    tirages = service.charger_tirages()

    service.sauvegarder_grille([1, 5, 12, 33, 49], 7)

"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import GrilleLoto, StatistiquesLoto, TirageLoto
from src.services.core.base import BaseService
from src.services.core.events import obtenir_bus
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════

# CONSTANTES

# ═══════════════════════════════════════════════════════════


COUT_GRILLE = Decimal("2.20")


# ═══════════════════════════════════════════════════════════

# SERVICE

# ═══════════════════════════════════════════════════════════


class LotoCrudService(BaseService[GrilleLoto]):
    """Service CRUD pour les tirages et grilles Loto.



    Hérite de BaseService[GrilleLoto] pour le CRUD générique sur les grilles.

    Les méthodes spécialisées gèrent les tirages et la synchronisation.

    """

    def __init__(self):

        super().__init__(model=GrilleLoto, cache_ttl=120)

    # ── Lecture ──────────────────────────────────────────

    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def charger_tirages(self, limite: int | None = None, db: Session | None = None) -> list[dict]:
        """Charge les tirages depuis la base de données.



        Args:

            limite: Nombre max de tirages (None = tous)



        Returns:

            Liste de dictionnaires tirage

        """

        query = db.query(TirageLoto).order_by(TirageLoto.date_tirage.desc())

        if limite:
            query = query.limit(limite)

        tirages = query.all()

        return [
            {
                "id": t.id,
                "date_tirage": t.date_tirage,
                "numero_1": t.numero_1,
                "numero_2": t.numero_2,
                "numero_3": t.numero_3,
                "numero_4": t.numero_4,
                "numero_5": t.numero_5,
                "numero_chance": t.numero_chance,
                "jackpot_euros": t.jackpot_euros,
            }
            for t in tirages
        ]

    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def charger_grilles_utilisateur(self, db: Session | None = None) -> list[dict]:
        """Charge les grilles enregistrées par l'utilisateur.



        Returns:

            Liste de dictionnaires grille

        """

        grilles = db.query(GrilleLoto).order_by(GrilleLoto.date_creation.desc()).all()

        return [
            {
                "id": g.id,
                "numeros": [g.numero_1, g.numero_2, g.numero_3, g.numero_4, g.numero_5],
                "numero_chance": g.numero_chance,
                "date_creation": g.date_creation,
                "strategie": g.strategie,
                "note": g.note,
            }
            for g in grilles
        ]

    # ── Écriture ────────────────────────────────────────

    @avec_session_db
    def sauvegarder_grille(
        self,
        numeros: list[int],
        numero_chance: int,
        strategie: str = "manuel",
        note: str | None = None,
        db: Session | None = None,
    ) -> int:
        """Sauvegarde une grille dans la base de données.



        Args:

            numeros: 5 numéros triés

            numero_chance: Numéro chance

            strategie: Source de la stratégie

            note: Note optionnelle



        Returns:

            ID de la grille créée

        """

        numeros_tries = sorted(numeros)

        grille = GrilleLoto(
            numero_1=numeros_tries[0],
            numero_2=numeros_tries[1],
            numero_3=numeros_tries[2],
            numero_4=numeros_tries[3],
            numero_5=numeros_tries[4],
            numero_chance=numero_chance,
            strategie=strategie,
            note=note,
        )

        db.add(grille)

        db.commit()

        # Émettre événement domaine

        obtenir_bus().emettre(
            "loto.modifie",
            {"element_id": grille.id, "type_element": "grille", "action": "creee"},
            source="loto",
        )

        return grille.id

    @avec_session_db
    def enregistrer_grille(
        self,
        numeros: list[int],
        chance: int,
        source: str = "manuel",
        est_virtuelle: bool = True,
        db: Session | None = None,
    ) -> bool:
        """Enregistre une nouvelle grille (version CRUD simple).



        Args:

            numeros: 5 numéros

            chance: Numéro chance

            source: Source de la prédiction

            est_virtuelle: Grille virtuelle ou réelle



        Returns:

            True si enregistrement réussi

        """

        if len(numeros) != 5:
            return False

        numeros_tries = sorted(numeros)

        grille = GrilleLoto(
            numero_1=numeros_tries[0],
            numero_2=numeros_tries[1],
            numero_3=numeros_tries[2],
            numero_4=numeros_tries[3],
            numero_5=numeros_tries[4],
            numero_chance=chance,
            source_prediction=source,
            est_virtuelle=est_virtuelle,
            mise=COUT_GRILLE,
        )

        db.add(grille)

        db.commit()

        # Émettre événement domaine

        obtenir_bus().emettre(
            "loto.modifie",
            {"element_id": grille.id, "type_element": "grille", "action": "creee"},
            source="loto",
        )

        return True

    @avec_session_db
    def ajouter_tirage(
        self,
        date_t: date,
        numeros: list[int],
        chance: int,
        jackpot: int | None = None,
        verifier_fn=None,
        db: Session | None = None,
    ) -> bool:
        """Ajoute un tirage et met à jour les grilles en attente.



        Args:

            date_t: Date du tirage

            numeros: 5 numéros tirés

            chance: Numéro chance

            jackpot: Montant du jackpot

            verifier_fn: Fonction de vérification de grille (injectable)



        Returns:

            True si ajout réussi

        """

        if len(numeros) != 5:
            return False

        numeros_tries = sorted(numeros)

        tirage = TirageLoto(
            date_tirage=date_t,
            numero_1=numeros_tries[0],
            numero_2=numeros_tries[1],
            numero_3=numeros_tries[2],
            numero_4=numeros_tries[3],
            numero_5=numeros_tries[4],
            numero_chance=chance,
            jackpot_euros=jackpot,
        )

        db.add(tirage)

        db.commit()

        # Émettre événement domaine

        obtenir_bus().emettre(
            "loto.modifie",
            {"element_id": tirage.id, "type_element": "tirage", "action": "ajoutee"},
            source="loto",
        )

        # Mettre à jour les grilles en attente

        grilles = db.query(GrilleLoto).filter(GrilleLoto.tirage_id == None).all()

        if verifier_fn and grilles:
            tirage_dict = {
                "numero_1": numeros_tries[0],
                "numero_2": numeros_tries[1],
                "numero_3": numeros_tries[2],
                "numero_4": numeros_tries[3],
                "numero_5": numeros_tries[4],
                "numero_chance": chance,
                "jackpot_euros": jackpot or 2_000_000,
            }

            for grille in grilles:
                grille_data = {"numeros": grille.numeros, "numero_chance": grille.numero_chance}

                resultat = verifier_fn(grille_data, tirage_dict)

                grille.tirage_id = tirage.id

                grille.numeros_trouves = resultat["bons_numeros"]

                grille.chance_trouvee = resultat["chance_ok"]

                grille.rang = resultat["rang"]

                grille.gain = resultat["gain"]

            db.commit()

        return True

    # ── Synchronisation ─────────────────────────────────

    @avec_session_db
    def sync_tirages(
        self,
        tirages_api: list[dict],
        db: Session | None = None,
    ) -> int:
        """Insère des tirages provenant d'une source externe (API/scraper).



        Vérifie les doublons par date avant insertion.



        Args:

            tirages_api: Liste de dicts avec date, numeros, numero_chance, jackpot



        Returns:

            Nombre de nouveaux tirages ajoutés

        """

        count = 0

        for tirage_api in tirages_api:
            try:
                # Parser la date

                date_tirage = self._parser_date_tirage(tirage_api.get("date"))

                if not date_tirage:
                    continue

                # Vérifier doublon

                existing = (
                    db.query(TirageLoto).filter(TirageLoto.date_tirage == date_tirage).first()
                )

                if existing:
                    continue

                # Créer le tirage

                numeros = tirage_api.get("numeros", [])

                numero_chance = tirage_api.get("numero_chance")

                jackpot = tirage_api.get("jackpot", 0)

                if len(numeros) >= 5 and numero_chance:
                    numeros_tries = sorted(numeros[:5])

                    tirage = TirageLoto(
                        date_tirage=date_tirage,
                        numero_1=numeros_tries[0],
                        numero_2=numeros_tries[1],
                        numero_3=numeros_tries[2],
                        numero_4=numeros_tries[3],
                        numero_5=numeros_tries[4],
                        numero_chance=numero_chance,
                        jackpot_euros=jackpot,
                    )

                    db.add(tirage)

                    count += 1

            except Exception as e:
                logger.debug(f"Erreur tirage: {e}")

                continue

        if count > 0:
            try:
                db.commit()

                logger.info(f"📊 {count} nouveaux tirages ajoutés")

            except Exception as e:
                logger.error(f"Erreur commit: {e}")

                db.rollback()

        return count

    @avec_session_db
    def inserer_tirages_scraper(
        self,
        tirages: list[dict],
        stats: dict | None = None,
        db: Session | None = None,
    ) -> bool:
        """Insère des tirages depuis le scraper FDJ + statistiques.



        Args:

            tirages: Liste de tirages scrapés

            stats: Statistiques calculées (fréquences)



        Returns:

            True si insertion réussie

        """

        for tirage_data in tirages:
            existing = db.query(TirageLoto).filter(TirageLoto.date == tirage_data["date"]).first()

            if not existing:
                tirage = TirageLoto(
                    date=tirage_data["date"],
                    numeros=tirage_data["numeros"],
                    numero_chance=tirage_data.get("numero_chance"),
                    source=tirage_data.get("source", "FDJ API"),
                )

                db.add(tirage)

        if stats:
            stats_entry = StatistiquesLoto(type_stat="frequences", donnees_json=stats)

            db.add(stats_entry)

        db.commit()

        logger.info(f"✅ {len(tirages)} tirages insérés en BD")

        return True

    # ── Fallback BD ──────────────────────────────────────

    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def charger_tirages_fallback(self, limite: int = 50, db: Session | None = None) -> list[dict]:
        """Charge les tirages depuis la BD (fallback quand l'API échoue).



        Utilise le champ TirageLoto.date (format scraper).



        Returns:

            Liste de dicts compatibles scraper

        """

        tirages_bd = db.query(TirageLoto).order_by(TirageLoto.date.desc()).limit(limite).all()

        return [
            {
                "date": str(t.date),
                "numeros": t.numeros,
                "numero_chance": t.numero_chance,
                "source": "BD",
            }
            for t in tirages_bd
        ]

    @avec_session_db
    @avec_gestion_erreurs(default_return={})
    def charger_stats_fallback(self, db: Session | None = None) -> dict:
        """Charge les statistiques Loto depuis la BD (fallback).



        Returns:

            Dictionnaire de statistiques ou {}

        """

        stat_entry = (
            db.query(StatistiquesLoto)
            .filter_by(type_stat="frequences")
            .order_by(StatistiquesLoto.id.desc())
            .first()
        )

        if stat_entry:
            return stat_entry.donnees_json

        return {}

    # ── Utilitaires privés ───────────────────────────────

    @staticmethod
    def _parser_date_tirage(date_value: Any) -> date | None:
        """Parse une date de tirage depuis différents formats."""

        if isinstance(date_value, date):
            return date_value

        if isinstance(date_value, str):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.strptime(date_value, fmt).date()

                except ValueError:
                    continue

        return None


# ═══════════════════════════════════════════════════════════

# FACTORY

# ═══════════════════════════════════════════════════════════


@service_factory("loto_crud", tags={"jeux", "crud", "loto"})
def obtenir_loto_crud_service() -> LotoCrudService:
    """Factory singleton pour LotoCrudService."""

    return LotoCrudService()


def obtenir_service_loto_crud() -> LotoCrudService:
    """Alias français pour obtenir_loto_crud_service."""

    return obtenir_loto_crud_service()
