"""
Service Jours Spéciaux — Jours fériés français + fermetures crèche.

Fournit:
- Liste des jours fériés français (fixes + mobiles via Pâques)
- Gestion des semaines de fermeture crèche (configurables)
- Vérification si une date est un jour spécial
- Prochains jours spéciaux (pour alertes et suggestions IA)

Usage:
    service = obtenir_service_jours_speciaux()
    feries = service.jours_feries(2026)
    fermetures = service.fermetures_creche(2026)
    est_special = service.est_jour_special(date(2026, 12, 25))
"""

import logging
from datetime import date, timedelta
from typing import NamedTuple

from src.core.decorators import avec_cache
from src.core.state.persistent import PersistentState, persistent_state
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class JourSpecial(NamedTuple):
    """Jour spécial (férié ou fermeture crèche)."""

    date_jour: date
    nom: str
    type: str  # "ferie", "creche", "pont"


# ═══════════════════════════════════════════════════════════
# CALCUL JOURS FÉRIÉS
# ═══════════════════════════════════════════════════════════


def _paques(annee: int) -> date:
    """Calcul du dimanche de Pâques (algorithme de Butcher/Meeus).

    Valable pour toute année du calendrier grégorien.
    """
    a = annee % 19
    b, c = divmod(annee, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7  # noqa: E741
    m = (a + 11 * h + 22 * l) // 451
    mois, jour = divmod(h + l - 7 * m + 114, 31)
    return date(annee, mois, jour + 1)


def jours_feries_france(annee: int) -> list[JourSpecial]:
    """Retourne la liste des jours fériés français pour une année.

    Inclut les 11 jours fériés officiels (métropole).

    Args:
        annee: Année à calculer.

    Returns:
        Liste triée de JourSpecial.
    """
    paques = _paques(annee)

    feries = [
        JourSpecial(date(annee, 1, 1), "Jour de l'An", "ferie"),
        JourSpecial(paques + timedelta(days=1), "Lundi de Pâques", "ferie"),
        JourSpecial(date(annee, 5, 1), "Fête du Travail", "ferie"),
        JourSpecial(date(annee, 5, 8), "Victoire 1945", "ferie"),
        JourSpecial(paques + timedelta(days=39), "Ascension", "ferie"),
        JourSpecial(paques + timedelta(days=50), "Lundi de Pentecôte", "ferie"),
        JourSpecial(date(annee, 7, 14), "Fête Nationale", "ferie"),
        JourSpecial(date(annee, 8, 15), "Assomption", "ferie"),
        JourSpecial(date(annee, 11, 1), "Toussaint", "ferie"),
        JourSpecial(date(annee, 11, 11), "Armistice 1918", "ferie"),
        JourSpecial(date(annee, 12, 25), "Noël", "ferie"),
    ]

    return sorted(feries, key=lambda j: j.date_jour)


def detecter_ponts(annee: int) -> list[JourSpecial]:
    """Détecte les jours de pont potentiels.

    Un pont est un jour ouvré entre un jour férié et un weekend.
    Exemple: si jeudi est férié → vendredi est un pont.

    Args:
        annee: Année à analyser.

    Returns:
        Liste de JourSpecial de type "pont".
    """
    feries = {j.date_jour for j in jours_feries_france(annee)}
    ponts: list[JourSpecial] = []

    for jour_ferie in sorted(feries):
        # Jour férié un jeudi → vendredi est un pont
        if jour_ferie.weekday() == 3:  # Jeudi
            vendredi = jour_ferie + timedelta(days=1)
            if vendredi not in feries:
                ponts.append(
                    JourSpecial(vendredi, f"Pont ({jour_ferie.strftime('%d/%m')})", "pont")
                )

        # Jour férié un mardi → lundi est un pont
        if jour_ferie.weekday() == 1:  # Mardi
            lundi = jour_ferie - timedelta(days=1)
            if lundi not in feries:
                ponts.append(JourSpecial(lundi, f"Pont ({jour_ferie.strftime('%d/%m')})", "pont"))

    return sorted(ponts, key=lambda j: j.date_jour)


# ═══════════════════════════════════════════════════════════
# PERSISTENT STATE — FERMETURES CRÈCHE
# ═══════════════════════════════════════════════════════════


@persistent_state(key="fermetures_creche_config", sync_interval=60, auto_commit=True)
def _obtenir_config_creche() -> dict:
    """Valeurs par défaut des fermetures crèche (5 semaines/an)."""
    return {
        "semaines_fermeture": [],  # Liste de {"debut": "2026-08-03", "fin": "2026-08-21", "label": "Été"}
        "annee_courante": date.today().year,
        "nom_creche": "",
    }


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════


class ServiceJoursSpeciaux:
    """Service de gestion des jours fériés et fermetures crèche.

    Centralise la logique pour:
    - Jours fériés français (calculés automatiquement)
    - Ponts détectés automatiquement
    - Fermetures crèche (configurées par l'utilisateur)
    - Requêtes: prochains jours spéciaux, vérification dates
    """

    @avec_cache(ttl=86400)  # Cache 24h — ne change pas en cours de journée
    def jours_feries(self, annee: int) -> list[JourSpecial]:
        """Retourne les jours fériés français pour une année."""
        return jours_feries_france(annee)

    @avec_cache(ttl=86400)
    def ponts(self, annee: int) -> list[JourSpecial]:
        """Retourne les jours de pont potentiels pour une année."""
        return detecter_ponts(annee)

    def fermetures_creche(self, annee: int | None = None) -> list[JourSpecial]:
        """Retourne les jours de fermeture crèche configurés.

        Args:
            annee: Filtrer par année (None = toutes).

        Returns:
            Liste de JourSpecial pour chaque jour de fermeture.
        """
        pstate: PersistentState = _obtenir_config_creche()
        config = pstate.get_all()
        semaines = config.get("semaines_fermeture", [])
        jours: list[JourSpecial] = []

        for semaine in semaines:
            try:
                debut = date.fromisoformat(semaine["debut"])
                fin = date.fromisoformat(semaine["fin"])
                label = semaine.get("label", "Fermeture crèche")

                # Générer chaque jour de la période
                current = debut
                while current <= fin:
                    if annee is None or current.year == annee:
                        # Exclure weekends
                        if current.weekday() < 5:
                            jours.append(JourSpecial(current, f"Crèche fermée ({label})", "creche"))
                    current += timedelta(days=1)
            except (KeyError, ValueError) as e:
                logger.warning(f"Entrée fermeture crèche invalide: {semaine} — {e}")

        return sorted(jours, key=lambda j: j.date_jour)

    def sauvegarder_fermetures_creche(self, semaines: list[dict], nom_creche: str = "") -> bool:
        """Sauvegarde les semaines de fermeture crèche.

        Args:
            semaines: Liste de {"debut": "YYYY-MM-DD", "fin": "YYYY-MM-DD", "label": "..."}
            nom_creche: Nom de la crèche (optionnel).

        Returns:
            True si sauvegardé avec succès.
        """
        pstate: PersistentState = _obtenir_config_creche()
        pstate.update(
            {
                "semaines_fermeture": semaines,
                "nom_creche": nom_creche,
                "annee_courante": date.today().year,
            }
        )
        return pstate.commit()

    def tous_jours_speciaux(self, annee: int, inclure_ponts: bool = True) -> list[JourSpecial]:
        """Retourne TOUS les jours spéciaux d'une année (triés par date).

        Fusionne: jours fériés + ponts + fermetures crèche.

        Args:
            annee: Année.
            inclure_ponts: Inclure les jours de pont détectés.

        Returns:
            Liste triée de tous les jours spéciaux.
        """
        jours = list(self.jours_feries(annee))

        if inclure_ponts:
            jours.extend(self.ponts(annee))

        jours.extend(self.fermetures_creche(annee))

        return sorted(jours, key=lambda j: j.date_jour)

    def est_jour_special(self, d: date) -> JourSpecial | None:
        """Vérifie si une date est un jour spécial.

        Args:
            d: Date à vérifier.

        Returns:
            JourSpecial si trouvé, None sinon.
        """
        for jour in self.tous_jours_speciaux(d.year):
            if jour.date_jour == d:
                return jour
        return None

    def est_jour_ferie(self, d: date) -> bool:
        """Vérifie si une date est un jour férié français."""
        return any(j.date_jour == d for j in self.jours_feries(d.year))

    def est_fermeture_creche(self, d: date) -> bool:
        """Vérifie si une date est un jour de fermeture crèche."""
        return any(j.date_jour == d for j in self.fermetures_creche(d.year))

    def prochains_jours_speciaux(self, nb: int = 5) -> list[JourSpecial]:
        """Retourne les N prochains jours spéciaux à venir.

        Args:
            nb: Nombre de jours à retourner.

        Returns:
            Liste des prochains jours spéciaux.
        """
        aujourd_hui = date.today()
        annee = aujourd_hui.year

        # Chercher dans l'année courante et la suivante
        tous = self.tous_jours_speciaux(annee) + self.tous_jours_speciaux(annee + 1)
        futurs = [j for j in tous if j.date_jour >= aujourd_hui]

        return futurs[:nb]

    def jours_speciaux_semaine(self, date_debut: date) -> list[JourSpecial]:
        """Retourne les jours spéciaux d'une semaine donnée.

        Args:
            date_debut: Date de début de semaine (lundi).

        Returns:
            Jours spéciaux de la semaine.
        """
        date_fin = date_debut + timedelta(days=6)
        tous = self.tous_jours_speciaux(date_debut.year)

        # Si la semaine chevauche deux années
        if date_fin.year != date_debut.year:
            tous.extend(self.tous_jours_speciaux(date_fin.year))

        return [j for j in tous if date_debut <= j.date_jour <= date_fin]


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("jours_speciaux", tags={"famille", "planning"})
def _creer_service_jours_speciaux() -> ServiceJoursSpeciaux:
    return ServiceJoursSpeciaux()


def obtenir_service_jours_speciaux() -> ServiceJoursSpeciaux:
    """Factory pour obtenir le service jours spéciaux (singleton)."""
    return _creer_service_jours_speciaux()
