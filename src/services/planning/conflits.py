"""
Service Détection de Conflits d'Horaires — Planning.

Détecte automatiquement les chevauchements d'événements dans le calendrier:
- Conflits entre événements du même jour
- Conflits avec les jours fériés / fermetures crèche
- Conflits de trajet (événements consécutifs sans marge)
- Alertes pour les journées surchargées

Usage:
    service = obtenir_service_conflits()
    conflits = service.detecter_conflits_semaine(date_debut)
    conflit = service.verifier_nouvel_evenement(date, heure_debut, heure_fin)
"""

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import StrEnum
from typing import Any

from src.core.decorators import avec_cache
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class NiveauConflit(StrEnum):
    """Niveau de gravité d'un conflit."""

    ERREUR = "erreur"  # Chevauchement total — impossible
    AVERTISSEMENT = "avertissement"  # Risque élevé (pas de marge)
    INFO = "info"  # Information (jour chargé, férié)


class TypeConflit(StrEnum):
    """Type de conflit détecté."""

    CHEVAUCHEMENT = "chevauchement"  # Deux événements en même temps
    SANS_MARGE = "sans_marge"  # Enchaînement trop serré
    JOUR_FERIE = "jour_ferie"  # Événement planifié sur un jour férié
    CRECHE_FERMEE = "creche_fermee"  # Activité Jules quand crèche fermée
    SURCHARGE = "surcharge"  # Trop d'événements dans la journée
    HORS_HORAIRES = "hors_horaires"  # Événement à une heure inhabituelle


@dataclass
class Conflit:
    """Conflit détecté entre événements."""

    type: TypeConflit
    niveau: NiveauConflit
    message: str
    date_jour: date
    evenement_1: dict | None = None  # {titre, heure_debut, heure_fin}
    evenement_2: dict | None = None  # {titre, heure_debut, heure_fin}
    suggestion: str | None = None

    @property
    def emoji(self) -> str:
        return {
            NiveauConflit.ERREUR: "🔴",
            NiveauConflit.AVERTISSEMENT: "🟡",
            NiveauConflit.INFO: "🔵",
        }.get(self.niveau, "⚪")


@dataclass
class RapportConflits:
    """Rapport de conflits pour une période."""

    date_debut: date
    date_fin: date
    conflits: list[Conflit] = field(default_factory=list)

    @property
    def nb_erreurs(self) -> int:
        return sum(1 for c in self.conflits if c.niveau == NiveauConflit.ERREUR)

    @property
    def nb_avertissements(self) -> int:
        return sum(1 for c in self.conflits if c.niveau == NiveauConflit.AVERTISSEMENT)

    @property
    def nb_infos(self) -> int:
        return sum(1 for c in self.conflits if c.niveau == NiveauConflit.INFO)

    @property
    def a_conflits_critiques(self) -> bool:
        return self.nb_erreurs > 0

    @property
    def resume(self) -> str:
        if not self.conflits:
            return "✅ Aucun conflit détecté"
        parts = []
        if self.nb_erreurs:
            parts.append(f"🔴 {self.nb_erreurs} conflit(s)")
        if self.nb_avertissements:
            parts.append(f"🟡 {self.nb_avertissements} avertissement(s)")
        if self.nb_infos:
            parts.append(f"🔵 {self.nb_infos} info(s)")
        return " • ".join(parts)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

MARGE_MINUTES_DEFAUT = 15  # Minutes minimales entre 2 événements
SEUIL_SURCHARGE = 6  # Nombre d'événements max avant alerte surcharge
HEURE_MIN_NORMALE = time(7, 0)  # Événements avant 7h = inhabituel
HEURE_MAX_NORMALE = time(22, 0)  # Événements après 22h = inhabituel


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════


class ServiceConflits:
    """Service de détection des conflits d'horaires.

    Analyse les événements du calendrier pour détecter:
    - Chevauchements d'horaires
    - Enchaînements trop serrés
    - Conflits avec jours fériés / fermetures crèche
    - Journées surchargées
    """

    def detecter_conflits_jour(
        self,
        date_jour: date,
        evenements: list[dict],
        marge_minutes: int = MARGE_MINUTES_DEFAUT,
    ) -> list[Conflit]:
        """Détecte les conflits pour un jour donné.

        Args:
            date_jour: Date à analyser.
            evenements: Liste de dicts {titre, heure_debut, heure_fin, type, pour_jules}.
            marge_minutes: Marge minimale entre événements (minutes).

        Returns:
            Liste des conflits détectés.
        """
        conflits: list[Conflit] = []

        # Filtrer les événements avec horaires
        events_avec_heure = [e for e in evenements if e.get("heure_debut") is not None]

        # Trier par heure de début
        events_avec_heure.sort(key=lambda e: e["heure_debut"])

        # 1. Détecter les chevauchements
        for i in range(len(events_avec_heure)):
            for j in range(i + 1, len(events_avec_heure)):
                evt1 = events_avec_heure[i]
                evt2 = events_avec_heure[j]

                conflit = self._verifier_chevauchement(date_jour, evt1, evt2, marge_minutes)
                if conflit:
                    conflits.append(conflit)

        # 2. Détecter surcharge
        if len(evenements) >= SEUIL_SURCHARGE:
            conflits.append(
                Conflit(
                    type=TypeConflit.SURCHARGE,
                    niveau=NiveauConflit.AVERTISSEMENT,
                    message=f"Journée chargée: {len(evenements)} événements planifiés",
                    date_jour=date_jour,
                    suggestion="Envisagez de reporter certains événements à un autre jour",
                )
            )

        # 3. Détecter événements hors horaires normaux
        for evt in events_avec_heure:
            heure = evt["heure_debut"]
            if isinstance(heure, time):
                if heure < HEURE_MIN_NORMALE:
                    conflits.append(
                        Conflit(
                            type=TypeConflit.HORS_HORAIRES,
                            niveau=NiveauConflit.INFO,
                            message=f"'{evt['titre']}' planifié très tôt ({heure.strftime('%H:%M')})",
                            date_jour=date_jour,
                            evenement_1=evt,
                        )
                    )
                elif heure > HEURE_MAX_NORMALE:
                    conflits.append(
                        Conflit(
                            type=TypeConflit.HORS_HORAIRES,
                            niveau=NiveauConflit.INFO,
                            message=f"'{evt['titre']}' planifié tard ({heure.strftime('%H:%M')})",
                            date_jour=date_jour,
                            evenement_1=evt,
                        )
                    )

        # 4. Vérifier jours fériés et fermetures crèche
        conflits.extend(self._verifier_jours_speciaux(date_jour, evenements))

        return conflits

    def _verifier_chevauchement(
        self,
        date_jour: date,
        evt1: dict,
        evt2: dict,
        marge_minutes: int,
    ) -> Conflit | None:
        """Vérifie si deux événements se chevauchent."""
        h1_debut = evt1.get("heure_debut")
        h1_fin = evt1.get("heure_fin") or _ajouter_duree(h1_debut, 60)
        h2_debut = evt2.get("heure_debut")

        if not all(isinstance(h, time) for h in [h1_debut, h1_fin, h2_debut]):
            return None

        # Chevauchement strict
        if h2_debut < h1_fin:
            return Conflit(
                type=TypeConflit.CHEVAUCHEMENT,
                niveau=NiveauConflit.ERREUR,
                message=(
                    f"'{evt1['titre']}' ({h1_debut.strftime('%H:%M')}-{h1_fin.strftime('%H:%M')}) "
                    f"chevauche '{evt2['titre']}' ({h2_debut.strftime('%H:%M')})"
                ),
                date_jour=date_jour,
                evenement_1=evt1,
                evenement_2=evt2,
                suggestion=(f"Décaler '{evt2['titre']}' après {h1_fin.strftime('%H:%M')}"),
            )

        # Enchaînement sans marge
        marge = timedelta(minutes=marge_minutes)
        h1_fin_dt = datetime.combine(date_jour, h1_fin)
        h2_debut_dt = datetime.combine(date_jour, h2_debut)

        if h2_debut_dt - h1_fin_dt < marge:
            return Conflit(
                type=TypeConflit.SANS_MARGE,
                niveau=NiveauConflit.AVERTISSEMENT,
                message=(
                    f"Enchaînement serré: '{evt1['titre']}' finit à {h1_fin.strftime('%H:%M')}, "
                    f"'{evt2['titre']}' commence à {h2_debut.strftime('%H:%M')} "
                    f"({int((h2_debut_dt - h1_fin_dt).total_seconds() // 60)} min)"
                ),
                date_jour=date_jour,
                evenement_1=evt1,
                evenement_2=evt2,
                suggestion=f"Prévoir au moins {marge_minutes} min entre les deux",
            )

        return None

    def _verifier_jours_speciaux(self, date_jour: date, evenements: list[dict]) -> list[Conflit]:
        """Vérifie les conflits avec jours fériés et fermetures crèche."""
        conflits: list[Conflit] = []

        try:
            from src.services.famille.jours_speciaux import obtenir_service_jours_speciaux

            svc = obtenir_service_jours_speciaux()

            jour_special = svc.est_jour_special(date_jour)
            if jour_special is None:
                return conflits

            if jour_special.type == "ferie":
                # Vérifier si des événements pro/rdv sont planifiés un jour férié
                for evt in evenements:
                    evt_type = evt.get("type", "")
                    if evt_type in ("rdv", "rdv_autre", "routine"):
                        conflits.append(
                            Conflit(
                                type=TypeConflit.JOUR_FERIE,
                                niveau=NiveauConflit.AVERTISSEMENT,
                                message=(
                                    f"'{evt['titre']}' planifié un jour férié "
                                    f"({jour_special.nom})"
                                ),
                                date_jour=date_jour,
                                evenement_1=evt,
                                suggestion="Vérifier que le lieu est ouvert ce jour férié",
                            )
                        )

            if jour_special.type == "creche":
                # Vérifier si des activités supposent que Jules est à la crèche
                for evt in evenements:
                    # Les événements qui ne sont PAS pour Jules mais supposent
                    # la garde par la crèche
                    if not evt.get("pour_jules", False):
                        continue
                    conflits.append(
                        Conflit(
                            type=TypeConflit.CRECHE_FERMEE,
                            niveau=NiveauConflit.AVERTISSEMENT,
                            message=(
                                f"'{evt['titre']}' (Jules) planifié un jour de fermeture crèche "
                                f"({jour_special.nom})"
                            ),
                            date_jour=date_jour,
                            evenement_1=evt,
                            suggestion="Prévoir un mode de garde alternatif pour Jules",
                        )
                    )

        except ImportError:
            logger.debug("Service jours spéciaux non disponible pour les conflits")

        return conflits

    def detecter_conflits_semaine(
        self,
        date_debut: date,
        evenements_par_jour: dict[date, list[dict]] | None = None,
    ) -> RapportConflits:
        """Détecte les conflits pour une semaine complète.

        Args:
            date_debut: Lundi de la semaine.
            evenements_par_jour: Dict {date: [events]}. Si None, charge depuis le calendrier.

        Returns:
            RapportConflits complet.
        """
        from src.core.date_utils import obtenir_debut_semaine

        lundi = obtenir_debut_semaine(date_debut)
        dimanche = lundi + timedelta(days=6)

        rapport = RapportConflits(date_debut=lundi, date_fin=dimanche)

        if evenements_par_jour is None:
            evenements_par_jour = self._charger_evenements_semaine(lundi)

        for i in range(7):
            jour = lundi + timedelta(days=i)
            events_jour = evenements_par_jour.get(jour, [])
            conflits_jour = self.detecter_conflits_jour(jour, events_jour)
            rapport.conflits.extend(conflits_jour)

        return rapport

    def verifier_nouvel_evenement(
        self,
        date_jour: date,
        heure_debut: time,
        heure_fin: time | None,
        titre: str = "Nouvel événement",
    ) -> list[Conflit]:
        """Vérifie si un nouvel événement crée des conflits.

        Utile avant l'ajout pour prévenir l'utilisateur.

        Args:
            date_jour: Date du nouvel événement.
            heure_debut: Heure de début.
            heure_fin: Heure de fin.
            titre: Titre du nouvel événement.

        Returns:
            Liste des conflits potentiels.
        """
        nouveau = {
            "titre": titre,
            "heure_debut": heure_debut,
            "heure_fin": heure_fin or _ajouter_duree(heure_debut, 60),
            "type": "autre",
        }

        events_existants = self._charger_evenements_jour(date_jour)
        events_existants.append(nouveau)

        return self.detecter_conflits_jour(date_jour, events_existants)

    def _charger_evenements_semaine(self, date_debut: date) -> dict[date, list[dict]]:
        """Charge les événements d'une semaine depuis le calendrier."""
        try:
            from src.modules.planning.calendrier.aggregation import (
                construire_semaine_calendrier,
            )
            from src.modules.planning.calendrier.data import charger_donnees_semaine

            donnees = charger_donnees_semaine(date_debut)
            semaine = construire_semaine_calendrier(
                date_debut=date_debut,
                repas=donnees.get("repas", []),
                sessions_batch=donnees.get("sessions_batch", []),
                activites=donnees.get("activites", []),
                events=donnees.get("events", []),
                courses_planifiees=donnees.get("courses_planifiees", []),
                taches_menage=donnees.get("taches_menage", []),
            )

            result: dict[date, list[dict]] = {}
            for jour in semaine.jours:
                result[jour.date_jour] = [
                    {
                        "titre": evt.titre,
                        "heure_debut": evt.heure_debut,
                        "heure_fin": evt.heure_fin,
                        "type": evt.type.value,
                        "pour_jules": evt.pour_jules,
                    }
                    for evt in jour.evenements
                ]
            return result

        except Exception as e:
            logger.error(f"Erreur chargement événements semaine: {e}")
            return {}

    def _charger_evenements_jour(self, date_jour: date) -> list[dict]:
        """Charge les événements d'un jour spécifique."""
        from src.core.date_utils import obtenir_debut_semaine

        lundi = obtenir_debut_semaine(date_jour)
        semaine = self._charger_evenements_semaine(lundi)
        return semaine.get(date_jour, [])


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def _ajouter_duree(heure: time | None, minutes: int) -> time:
    """Ajoute des minutes à une heure."""
    if heure is None:
        return time(23, 59)
    dt = datetime.combine(date.today(), heure) + timedelta(minutes=minutes)
    return dt.time()


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("conflits_planning", tags={"planning"})
def _creer_service_conflits() -> ServiceConflits:
    return ServiceConflits()


def obtenir_service_conflits() -> ServiceConflits:
    """Factory pour obtenir le service de détection de conflits (singleton)."""
    return _creer_service_conflits()
