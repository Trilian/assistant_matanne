"""
Service Suggestions IA — Créneaux libres et optimisation.

Analyse la charge de la semaine et identifie:
- Les créneaux libres par jour
- Les meilleurs moments pour ajouter des activités
- Les suggestions de rééquilibrage (jours chargés → jours vides)
- Les recommandations contextuelles (météo, jours spéciaux, Jules)

Usage:
    service = obtenir_service_suggestions()
    creneaux = service.creneaux_libres(semaine)
    suggestions = service.suggestions_ia(semaine)
"""

import logging
from dataclasses import dataclass, field
from datetime import date, time, timedelta

from src.core.decorators import avec_cache
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class CreneauLibre:
    """Créneau libre identifié dans le planning."""

    date_jour: date
    heure_debut: time
    heure_fin: time
    duree_minutes: int
    score_qualite: int  # 0-100 — plus c'est haut, mieux c'est
    raison: str = ""  # Pourquoi ce créneau est bon

    @property
    def duree_str(self) -> str:
        """Durée formatée."""
        h = self.duree_minutes // 60
        m = self.duree_minutes % 60
        if h > 0 and m > 0:
            return f"{h}h{m:02d}"
        elif h > 0:
            return f"{h}h"
        else:
            return f"{m}min"

    @property
    def horaire_str(self) -> str:
        """Plage horaire formatée."""
        return f"{self.heure_debut.strftime('%H:%M')}–{self.heure_fin.strftime('%H:%M')}"


@dataclass
class SuggestionPlanning:
    """Suggestion d'optimisation du planning."""

    titre: str
    description: str
    priorite: int  # 1-5, 5 = plus important
    categories: list[str] = field(default_factory=list)  # ["activite", "repos", "courses"]
    icone: str = "💡"

    @property
    def emoji_priorite(self) -> str:
        """Emoji représentant la priorité."""
        return {5: "🔴", 4: "🟠", 3: "🟡", 2: "🟢", 1: "🔵"}.get(self.priorite, "⚪")


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

# Plage horaire considérée (hors nuit)
HEURE_DEBUT_JOURNEE = time(7, 0)
HEURE_FIN_JOURNEE = time(21, 0)

# Durée minimale pour qu'un créneau soit considéré "libre"
DUREE_MIN_CRENEAU = 30  # minutes

# Seuils de charge
SEUIL_CHARGE_HAUTE = 60
SEUIL_CHARGE_BASSE = 20


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════


class ServiceSuggestions:
    """Service de suggestions IA pour le planning familial.

    Analyse la charge et les créneaux pour proposer des optimisations.
    """

    def creneaux_libres(
        self,
        jours: list,
        duree_min: int = DUREE_MIN_CRENEAU,
    ) -> list[CreneauLibre]:
        """Identifie les créneaux libres dans une semaine.

        Args:
            jours: Liste de JourCalendrier.
            duree_min: Durée minimale d'un créneau en minutes.

        Returns:
            Liste de créneaux libres triés par qualité.
        """
        tous_creneaux: list[CreneauLibre] = []

        for jour in jours:
            creneaux_jour = self._creneaux_jour(jour, duree_min)
            tous_creneaux.extend(creneaux_jour)

        # Trier par score de qualité décroissant
        tous_creneaux.sort(key=lambda c: (-c.score_qualite, c.date_jour, c.heure_debut))

        return tous_creneaux

    def _creneaux_jour(self, jour, duree_min: int) -> list[CreneauLibre]:
        """Trouve les créneaux libres d'un jour.

        Algorithme:
        1. Collecter les heures occupées (triées)
        2. Trouver les trous entre événements
        3. Évaluer la qualité de chaque trou
        """
        # Collecter les plages occupées
        occupations: list[tuple[time, time]] = []

        for evt in jour.evenements:
            if evt.heure_debut and evt.heure_fin:
                occupations.append((evt.heure_debut, evt.heure_fin))
            elif evt.heure_debut:
                # Estimer 1h si pas de fin
                fin = time(
                    min(evt.heure_debut.hour + 1, 23),
                    evt.heure_debut.minute,
                )
                occupations.append((evt.heure_debut, fin))

        # Trier par heure de début
        occupations.sort(key=lambda x: x[0])

        # Trouver les trous
        creneaux: list[CreneauLibre] = []
        curseur = HEURE_DEBUT_JOURNEE

        for debut_occ, fin_occ in occupations:
            if debut_occ <= curseur:
                # Chevauchement ou pas de trou
                if fin_occ > curseur:
                    curseur = fin_occ
                continue

            # Trou trouvé entre curseur et debut_occ
            duree = self._minutes_diff(curseur, debut_occ)
            if duree >= duree_min:
                score = self._evaluer_creneau(jour, curseur, debut_occ, duree)
                creneaux.append(
                    CreneauLibre(
                        date_jour=jour.date_jour,
                        heure_debut=curseur,
                        heure_fin=debut_occ,
                        duree_minutes=duree,
                        score_qualite=score,
                        raison=self._raison_creneau(curseur, duree, jour.charge_score),
                    )
                )

            curseur = max(curseur, fin_occ)

        # Vérifier le trou après le dernier événement
        if curseur < HEURE_FIN_JOURNEE:
            duree = self._minutes_diff(curseur, HEURE_FIN_JOURNEE)
            if duree >= duree_min:
                score = self._evaluer_creneau(jour, curseur, HEURE_FIN_JOURNEE, duree)
                creneaux.append(
                    CreneauLibre(
                        date_jour=jour.date_jour,
                        heure_debut=curseur,
                        heure_fin=HEURE_FIN_JOURNEE,
                        duree_minutes=duree,
                        score_qualite=score,
                        raison=self._raison_creneau(curseur, duree, jour.charge_score),
                    )
                )

        return creneaux

    def _minutes_diff(self, t1: time, t2: time) -> int:
        """Calcule la différence en minutes entre deux heures."""
        return (t2.hour * 60 + t2.minute) - (t1.hour * 60 + t1.minute)

    def _evaluer_creneau(self, jour, debut: time, fin: time, duree: int) -> int:
        """Évalue la qualité d'un créneau libre (0-100).

        Critères:
        - Durée (plus c'est long, mieux c'est)
        - Heure (matin/après-midi préférés)
        - Charge du jour (jour léger = bonus)
        - Weekend bonus
        """
        score = 50  # Base

        # Bonus durée
        if duree >= 120:
            score += 20  # >= 2h
        elif duree >= 60:
            score += 10  # >= 1h

        # Bonus horaire
        if 9 <= debut.hour <= 11:
            score += 10  # Matinée idéale
        elif 14 <= debut.hour <= 16:
            score += 10  # Après-midi idéal

        # Bonus jour léger
        charge = jour.charge_score
        if charge < SEUIL_CHARGE_BASSE:
            score += 15  # Jour très léger
        elif charge < SEUIL_CHARGE_HAUTE:
            score += 5  # Jour normal

        # Bonus weekend
        if jour.date_jour.weekday() >= 5:
            score += 5

        return min(score, 100)

    def _raison_creneau(self, debut: time, duree: int, charge: int) -> str:
        """Génère une raison lisible pour un créneau."""
        raisons = []

        if duree >= 120:
            raisons.append("long créneau disponible")
        if charge < SEUIL_CHARGE_BASSE:
            raisons.append("journée légère")
        if 9 <= debut.hour <= 11:
            raisons.append("matinée idéale")
        elif 14 <= debut.hour <= 16:
            raisons.append("après-midi idéal")

        return ", ".join(raisons) if raisons else "disponible"

    def suggestions_planning(
        self,
        jours: list,
    ) -> list[SuggestionPlanning]:
        """Génère des suggestions d'optimisation du planning.

        Analyse la charge globale et propose des actions.

        Args:
            jours: Liste de JourCalendrier.

        Returns:
            Liste de suggestions triées par priorité.
        """
        suggestions: list[SuggestionPlanning] = []

        charges = [j.charge_score for j in jours]
        charge_moy = sum(charges) / len(charges) if charges else 0
        jours_charges = [j for j in jours if j.charge_score >= SEUIL_CHARGE_HAUTE]
        jours_vides = [j for j in jours if j.charge_score < SEUIL_CHARGE_BASSE]

        # Rééquilibrage si déséquilibre
        if jours_charges and jours_vides:
            for jc in jours_charges:
                for jv in jours_vides:
                    suggestions.append(
                        SuggestionPlanning(
                            titre=f"Rééquilibrer {jc.jour_semaine} → {jv.jour_semaine}",
                            description=(
                                f"{jc.jour_semaine} est surchargé ({jc.charge_score}%) "
                                f"tandis que {jv.jour_semaine} est léger ({jv.charge_score}%). "
                                f"Déplacer une activité ?"
                            ),
                            priorite=4,
                            categories=["equilibrage"],
                            icone="⚖️",
                        )
                    )

        # Activités pour Jules si peu d'activités
        nb_activites_jules = sum(1 for j in jours for e in j.evenements if e.pour_jules)
        if nb_activites_jules < 3:
            creneaux = self.creneaux_libres(jours, duree_min=60)
            if creneaux:
                meilleur = creneaux[0]
                if nb_activites_jules == 0:
                    _jules_msg = "Jules n'a aucune activité prévue cette semaine."
                else:
                    _jules_msg = f"Jules n'a que {nb_activites_jules} activité{'s' if nb_activites_jules > 1 else ''} prévue{'s' if nb_activites_jules > 1 else ''} cette semaine."
                suggestions.append(
                    SuggestionPlanning(
                        titre=f"Activité Jules — {meilleur.date_jour.strftime('%A')}",
                        description=(
                            f"{_jules_msg} "
                            f"Créneau idéal: {meilleur.horaire_str} ({meilleur.raison})"
                        ),
                        priorite=3,
                        categories=["jules", "activite"],
                        icone="👶",
                    )
                )

        # Repas manquants
        nb_repas = sum(1 for j in jours if j.repas_midi) + sum(1 for j in jours if j.repas_soir)
        if nb_repas < 10:  # Moins de ~70% planifiés
            if nb_repas == 0:
                _repas_msg = "Aucun repas planifié cette semaine."
            else:
                _repas_msg = f"Seulement {nb_repas}/14 repas planifiés."
            suggestions.append(
                SuggestionPlanning(
                    titre="Planifier les repas manquants",
                    description=f"{_repas_msg} Le planificateur IA peut compléter !",
                    priorite=4,
                    categories=["repas"],
                    icone="🍽️",
                )
            )

        # Pas de batch cooking
        has_batch = any(j.batch_cooking for j in jours)
        if not has_batch and nb_repas >= 6:
            suggestions.append(
                SuggestionPlanning(
                    titre="Ajouter une session batch cooking",
                    description="Préparer plusieurs repas en avance économise du temps en semaine.",
                    priorite=2,
                    categories=["batch", "optimisation"],
                    icone="🍳",
                )
            )

        # Jours spéciaux — suggestions contextuelles
        for jour in jours:
            if hasattr(jour, "jours_speciaux"):
                for js in jour.jours_speciaux:
                    if "creche" in str(getattr(js, "type", "")):
                        suggestions.append(
                            SuggestionPlanning(
                                titre=f"Garde Jules — {jour.jour_semaine}",
                                description=(
                                    f"Crèche fermée le {jour.date_jour.strftime('%d/%m')} "
                                    f"({js.titre}). Prévoir une solution de garde !"
                                ),
                                priorite=5,
                                categories=["jules", "garde"],
                                icone="🏫",
                            )
                        )

        # Trier par priorité décroissante
        suggestions.sort(key=lambda s: -s.priorite)

        return suggestions


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("suggestions_planning", tags={"planning", "ia"})
def _creer_service_suggestions() -> ServiceSuggestions:
    return ServiceSuggestions()


def obtenir_service_suggestions() -> ServiceSuggestions:
    """Factory pour obtenir le service suggestions (singleton)."""
    return _creer_service_suggestions()
