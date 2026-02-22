"""
SeriesService - Service partagé pour le calcul des séries (Loi des séries).

Utilisé par Paris Sportifs et Loto pour:
- Calculer la fréquence historique d'un événement
- Tracker la série actuelle (nb événements depuis dernière occurrence)
- Calculer la "value" (fréquence × série)
- Détecter les opportunités (value > seuil)
- Créer des alertes

Formule Value:
    value = fréquence_historique × série_actuelle

Interprétation:
    - value < 1.0 : En dessous de la moyenne statistique
    - value ≈ 1.0 : Dans la moyenne
    - value > 2.0 : Opportunité potentielle (série inhabituelle)
    - value > 2.5 : Forte opportunité
"""

import logging
from datetime import date, datetime
from typing import Literal

from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.core.models import AlerteJeux, SerieJeux
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════

# Seuils par défaut
SEUIL_VALUE_ALERTE = 2.0  # Créer alerte si value >= ce seuil
SEUIL_VALUE_HAUTE = 2.5  # Haute opportunité
SEUIL_SERIES_MINIMUM = 3  # Ignorer séries < 3 (bruit statistique)

# Types de jeux
TypeJeu = Literal["paris", "loto"]


# ═══════════════════════════════════════════════════════════════════
# SERVICE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════


class SeriesService:
    """
    Service de gestion des séries pour la loi des séries.

    Fournit les méthodes partagées pour Paris et Loto.
    """

    def __init__(self, session: Session | None = None):
        """
        Initialise le service.

        Args:
            session: Session SQLAlchemy optionnelle (sinon créée à la demande)
        """
        self._session = session

    # ─────────────────────────────────────────────────────────────────
    # CALCULS DE BASE
    # ─────────────────────────────────────────────────────────────────

    @staticmethod
    def calculer_value(frequence: float, serie: int) -> float:
        """
        Calcule la value = fréquence × série.

        Args:
            frequence: Fréquence historique (0.0 à 1.0)
            serie: Nombre d'événements depuis dernière occurrence

        Returns:
            Value calculée
        """
        return frequence * serie

    @staticmethod
    def calculer_frequence(nb_occurrences: int, nb_total: int) -> float:
        """
        Calcule la fréquence historique.

        Args:
            nb_occurrences: Nombre de fois où l'événement est arrivé
            nb_total: Nombre total d'événements analysés

        Returns:
            Fréquence (0.0 à 1.0)
        """
        if nb_total == 0:
            return 0.0
        return nb_occurrences / nb_total

    @staticmethod
    def est_opportunite(value: float, seuil: float = SEUIL_VALUE_ALERTE) -> bool:
        """
        Vérifie si une value représente une opportunité.

        Args:
            value: Value calculée
            seuil: Seuil minimum (défaut: 2.0)

        Returns:
            True si value >= seuil
        """
        return value >= seuil

    @staticmethod
    def niveau_opportunite(value: float) -> str:
        """
        Retourne le niveau d'opportunité pour affichage.

        Args:
            value: Value calculée

        Returns:
            Emoji indicateur: "🟢" haute, "🟡" moyenne, "⚪" faible
        """
        if value >= SEUIL_VALUE_HAUTE:
            return "🟢"
        elif value >= SEUIL_VALUE_ALERTE:
            return "🟡"
        else:
            return "⚪"

    # ─────────────────────────────────────────────────────────────────
    # GESTION DES SÉRIES EN BASE
    # ─────────────────────────────────────────────────────────────────

    @avec_session_db
    def obtenir_serie(
        self,
        type_jeu: TypeJeu,
        marche: str,
        championnat: str | None = None,
        db: Session | None = None,
    ) -> SerieJeux | None:
        """
        Récupère une série existante.

        Args:
            type_jeu: "paris" ou "loto"
            marche: Identifiant du marché (ex: "domicile_mi_temps" ou "7")
            championnat: Championnat (pour paris uniquement)
            db: Session injectée

        Returns:
            SerieJeux ou None si non trouvée
        """
        query = db.query(SerieJeux).filter(
            SerieJeux.type_jeu == type_jeu,
            SerieJeux.marche == marche,
        )
        if championnat:
            query = query.filter(SerieJeux.championnat == championnat)
        else:
            query = query.filter(SerieJeux.championnat.is_(None))

        return query.first()

    @avec_session_db
    def creer_ou_maj_serie(
        self,
        type_jeu: TypeJeu,
        marche: str,
        championnat: str | None = None,
        serie_actuelle: int = 0,
        frequence: float = 0.0,
        nb_occurrences: int = 0,
        nb_total: int = 0,
        derniere_occurrence: date | None = None,
        db: Session | None = None,
    ) -> SerieJeux:
        """
        Crée ou met à jour une série.

        Args:
            type_jeu: "paris" ou "loto"
            marche: Identifiant du marché
            championnat: Championnat (pour paris)
            serie_actuelle: Série actuelle
            frequence: Fréquence calculée
            nb_occurrences: Nombre d'occurrences
            nb_total: Total analysé
            derniere_occurrence: Date dernière occurrence
            db: Session injectée

        Returns:
            SerieJeux créée ou mise à jour
        """
        serie = self.obtenir_serie(type_jeu, marche, championnat, db=db)

        if serie:
            # Mise à jour
            serie.serie_actuelle = serie_actuelle
            serie.frequence = frequence
            serie.nb_occurrences = nb_occurrences
            serie.nb_total = nb_total
            if derniere_occurrence:
                serie.derniere_occurrence = derniere_occurrence
            serie.derniere_mise_a_jour = datetime.utcnow()
        else:
            # Création
            serie = SerieJeux(
                type_jeu=type_jeu,
                championnat=championnat,
                marche=marche,
                serie_actuelle=serie_actuelle,
                frequence=frequence,
                nb_occurrences=nb_occurrences,
                nb_total=nb_total,
                derniere_occurrence=derniere_occurrence,
            )
            db.add(serie)

        db.commit()
        db.refresh(serie)
        return serie

    @avec_session_db
    def incrementer_serie(
        self,
        type_jeu: TypeJeu,
        marche: str,
        championnat: str | None = None,
        db: Session | None = None,
    ) -> SerieJeux | None:
        """
        Incrémente la série de 1 (événement non survenu).

        Args:
            type_jeu: "paris" ou "loto"
            marche: Identifiant du marché
            championnat: Championnat (pour paris)
            db: Session injectée

        Returns:
            SerieJeux mise à jour
        """
        serie = self.obtenir_serie(type_jeu, marche, championnat, db=db)
        if serie:
            serie.serie_actuelle += 1
            serie.nb_total += 1
            serie.frequence = self.calculer_frequence(serie.nb_occurrences, serie.nb_total)
            serie.derniere_mise_a_jour = datetime.utcnow()
            db.commit()
            db.refresh(serie)
        return serie

    @avec_session_db
    def reset_serie(
        self,
        type_jeu: TypeJeu,
        marche: str,
        championnat: str | None = None,
        date_occurrence: date | None = None,
        db: Session | None = None,
    ) -> SerieJeux | None:
        """
        Remet la série à 0 (événement survenu).

        Args:
            type_jeu: "paris" ou "loto"
            marche: Identifiant du marché
            championnat: Championnat (pour paris)
            date_occurrence: Date de l'occurrence
            db: Session injectée

        Returns:
            SerieJeux mise à jour
        """
        serie = self.obtenir_serie(type_jeu, marche, championnat, db=db)
        if serie:
            serie.serie_actuelle = 0
            serie.nb_occurrences += 1
            serie.nb_total += 1
            serie.frequence = self.calculer_frequence(serie.nb_occurrences, serie.nb_total)
            serie.derniere_occurrence = date_occurrence or date.today()
            serie.derniere_mise_a_jour = datetime.utcnow()
            db.commit()
            db.refresh(serie)
        return serie

    # ─────────────────────────────────────────────────────────────────
    # ALERTES
    # ─────────────────────────────────────────────────────────────────

    @avec_session_db
    def detecter_opportunites(
        self,
        type_jeu: TypeJeu | None = None,
        seuil: float = SEUIL_VALUE_ALERTE,
        db: Session | None = None,
    ) -> list[SerieJeux]:
        """
        Détecte les séries avec value >= seuil.

        Args:
            type_jeu: Filtrer par type (optionnel)
            seuil: Seuil minimum de value
            db: Session injectée

        Returns:
            Liste des séries avec opportunités
        """
        query = db.query(SerieJeux).filter(SerieJeux.serie_actuelle >= SEUIL_SERIES_MINIMUM)

        if type_jeu:
            query = query.filter(SerieJeux.type_jeu == type_jeu)

        series = query.all()

        # Filtrer par value calculée
        opportunites = [s for s in series if s.value >= seuil]

        # Trier par value décroissante
        opportunites.sort(key=lambda s: s.value, reverse=True)

        return opportunites

    @avec_session_db
    def creer_alerte(
        self,
        serie: SerieJeux,
        seuil_utilise: float = SEUIL_VALUE_ALERTE,
        db: Session | None = None,
    ) -> AlerteJeux:
        """
        Crée une alerte pour une série.

        Args:
            serie: Série concernée
            seuil_utilise: Seuil qui a déclenché l'alerte
            db: Session injectée

        Returns:
            AlerteJeux créée
        """
        alerte = AlerteJeux(
            serie_id=serie.id,
            type_jeu=serie.type_jeu,
            championnat=serie.championnat,
            marche=serie.marche,
            value_alerte=serie.value,
            serie_alerte=serie.serie_actuelle,
            frequence_alerte=serie.frequence,
            seuil_utilise=seuil_utilise,
        )
        db.add(alerte)
        db.commit()
        db.refresh(alerte)

        logger.info(
            f"Alerte créée: {serie.type_jeu}/{serie.marche} "
            f"value={serie.value:.2f} série={serie.serie_actuelle}"
        )

        return alerte

    @avec_session_db
    def obtenir_alertes_non_notifiees(
        self,
        type_jeu: TypeJeu | None = None,
        db: Session | None = None,
    ) -> list[AlerteJeux]:
        """
        Récupère les alertes non encore notifiées.

        Args:
            type_jeu: Filtrer par type (optionnel)
            db: Session injectée

        Returns:
            Liste des alertes à notifier
        """
        query = db.query(AlerteJeux).filter(AlerteJeux.notifie == False)

        if type_jeu:
            query = query.filter(AlerteJeux.type_jeu == type_jeu)

        return query.order_by(AlerteJeux.value_alerte.desc()).all()

    @avec_session_db
    def marquer_alerte_notifiee(
        self,
        alerte_id: int,
        db: Session | None = None,
    ) -> None:
        """
        Marque une alerte comme notifiée.

        Args:
            alerte_id: ID de l'alerte
            db: Session injectée
        """
        alerte = db.query(AlerteJeux).filter(AlerteJeux.id == alerte_id).first()
        if alerte:
            alerte.notifie = True
            alerte.date_notification = datetime.utcnow()
            db.commit()

    # ─────────────────────────────────────────────────────────────────
    # STATISTIQUES
    # ─────────────────────────────────────────────────────────────────

    @avec_session_db
    def obtenir_series_par_championnat(
        self,
        championnat: str,
        db: Session | None = None,
    ) -> list[SerieJeux]:
        """
        Récupère toutes les séries d'un championnat.

        Args:
            championnat: Nom du championnat
            db: Session injectée

        Returns:
            Liste des séries triées par value décroissante
        """
        series = (
            db.query(SerieJeux)
            .filter(
                SerieJeux.type_jeu == "paris",
                SerieJeux.championnat == championnat,
            )
            .all()
        )
        series.sort(key=lambda s: s.value, reverse=True)
        return series

    @avec_session_db
    def obtenir_series_loto(
        self,
        db: Session | None = None,
    ) -> list[SerieJeux]:
        """
        Récupère toutes les séries Loto (numéros).

        Args:
            db: Session injectée

        Returns:
            Liste des séries triées par série décroissante
        """
        series = db.query(SerieJeux).filter(SerieJeux.type_jeu == "loto").all()
        series.sort(key=lambda s: s.serie_actuelle, reverse=True)
        return series

    @avec_session_db
    def statistiques_globales(
        self,
        type_jeu: TypeJeu | None = None,
        db: Session | None = None,
    ) -> dict:
        """
        Calcule des statistiques globales sur les séries.

        Args:
            type_jeu: Filtrer par type (optionnel)
            db: Session injectée

        Returns:
            Dict avec stats: nb_series, serie_max, value_max, nb_opportunites
        """
        query = db.query(SerieJeux)
        if type_jeu:
            query = query.filter(SerieJeux.type_jeu == type_jeu)

        series = query.all()

        if not series:
            return {
                "nb_series": 0,
                "serie_max": 0,
                "value_max": 0.0,
                "nb_opportunites": 0,
            }

        return {
            "nb_series": len(series),
            "serie_max": max(s.serie_actuelle for s in series),
            "value_max": max(s.value for s in series),
            "nb_opportunites": sum(1 for s in series if s.value >= SEUIL_VALUE_ALERTE),
        }


# ═══════════════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════════════


def obtenir_service_series(session: Session | None = None) -> SeriesService:
    """
    Factory pour obtenir une instance de SeriesService (convention française).

    Args:
        session: Session SQLAlchemy optionnelle

    Returns:
        Instance de SeriesService
    """
    return SeriesService(session)


@service_factory("series", tags={"jeux", "crud", "series"})
def get_series_service(session: Session | None = None) -> SeriesService:
    """
    Factory pour obtenir une instance de SeriesService (alias anglais).

    Args:
        session: Session SQLAlchemy optionnelle

    Returns:
        Instance de SeriesService
    """
    return obtenir_service_series(session)
