"""
Service Rappels Intelligents — Délais adaptatifs par type d'événement.

Calcule les rappels appropriés selon le type d'événement:
- RDV médical → rappel à J-1 (24h) + H-2
- Activité famille → rappel H-2
- Courses → rappel H-1
- Batch cooking → rappel J-1 (vérifier ingrédients)
- Événement crèche → rappel J-3 (organiser garde alternative)
- Événement générique → rappel H-1

Usage:
    service = obtenir_service_rappels()
    rappels = service.rappels_a_venir(heures=24)
    delai = service.delai_rappel(TypeEvenement.RDV_MEDICAL)
"""

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import StrEnum

from src.core.decorators import avec_cache
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class PrioriteRappel(StrEnum):
    """Priorité d'un rappel."""

    HAUTE = "haute"  # Ne pas manquer — RDV médical, crèche
    MOYENNE = "moyenne"  # Important — activités, courses
    BASSE = "basse"  # Informatif — routines, tâches ménage


@dataclass
class RegleRappel:
    """Règle de rappel pour un type d'événement."""

    delais: list[timedelta]  # Délais avant l'événement (multiples rappels)
    priorite: PrioriteRappel
    message_template: str  # Template avec {titre}, {heure}, {delai}
    icone: str = "🔔"


@dataclass
class Rappel:
    """Rappel concret pour un événement spécifique."""

    evenement_titre: str
    evenement_type: str
    date_evenement: date
    heure_evenement: time | None
    date_rappel: datetime  # Quand envoyer le rappel
    priorite: PrioriteRappel
    message: str
    icone: str = "🔔"
    est_envoye: bool = False

    @property
    def est_a_envoyer(self) -> bool:
        """True si le rappel doit être envoyé maintenant."""
        return not self.est_envoye and datetime.now() >= self.date_rappel

    @property
    def delai_restant(self) -> timedelta:
        """Temps restant avant le rappel."""
        return max(self.date_rappel - datetime.now(), timedelta(0))

    @property
    def delai_str(self) -> str:
        """Délai restant formaté en texte lisible."""
        delta = self.delai_restant
        heures = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)

        if heures >= 24:
            jours = heures // 24
            return f"{jours}j"
        elif heures > 0:
            return f"{heures}h{minutes:02d}"
        elif minutes > 0:
            return f"{minutes}min"
        else:
            return "maintenant"


# ═══════════════════════════════════════════════════════════
# RÈGLES PAR TYPE D'ÉVÉNEMENT
# ═══════════════════════════════════════════════════════════

# Import des types d'événements (lazy pour éviter imports circulaires)
_REGLES_RAPPEL: dict[str, RegleRappel] = {
    "rdv_medical": RegleRappel(
        delais=[timedelta(hours=24), timedelta(hours=2)],
        priorite=PrioriteRappel.HAUTE,
        message_template="🏥 RDV médical «{titre}» dans {delai}",
        icone="🏥",
    ),
    "rdv_autre": RegleRappel(
        delais=[timedelta(hours=24), timedelta(hours=1)],
        priorite=PrioriteRappel.HAUTE,
        message_template="📅 RDV «{titre}» dans {delai}",
        icone="📅",
    ),
    "activite": RegleRappel(
        delais=[timedelta(hours=2)],
        priorite=PrioriteRappel.MOYENNE,
        message_template="🎨 Activité «{titre}» dans {delai}",
        icone="🎨",
    ),
    "courses": RegleRappel(
        delais=[timedelta(hours=1)],
        priorite=PrioriteRappel.MOYENNE,
        message_template="🛒 Courses «{titre}» dans {delai}",
        icone="🛒",
    ),
    "batch_cooking": RegleRappel(
        delais=[timedelta(hours=24)],
        priorite=PrioriteRappel.MOYENNE,
        message_template="🍳 Batch cooking demain — vérifier les ingrédients !",
        icone="🍳",
    ),
    "creche": RegleRappel(
        delais=[timedelta(days=3), timedelta(hours=24)],
        priorite=PrioriteRappel.HAUTE,
        message_template="🏫 Crèche fermée {delai} — organiser la garde de Jules",
        icone="🏫",
    ),
    "ferie": RegleRappel(
        delais=[timedelta(days=2)],
        priorite=PrioriteRappel.BASSE,
        message_template="{titre} dans {delai}",
        icone="📅",
    ),
    "pont": RegleRappel(
        delais=[timedelta(days=3)],
        priorite=PrioriteRappel.BASSE,
        message_template="🌉 {titre} dans {delai} — planifier ?",
        icone="🌉",
    ),
    "menage": RegleRappel(
        delais=[timedelta(hours=1)],
        priorite=PrioriteRappel.BASSE,
        message_template="🧹 Ménage «{titre}» prévu dans {delai}",
        icone="🧹",
    ),
    "routine": RegleRappel(
        delais=[timedelta(minutes=30)],
        priorite=PrioriteRappel.BASSE,
        message_template="⏰ Routine «{titre}» dans {delai}",
        icone="⏰",
    ),
}

# Règle par défaut
_REGLE_DEFAUT = RegleRappel(
    delais=[timedelta(hours=1)],
    priorite=PrioriteRappel.MOYENNE,
    message_template="🔔 «{titre}» dans {delai}",
    icone="🔔",
)


def _formater_delai(delta: timedelta) -> str:
    """Formate un timedelta en texte lisible."""
    heures_total = int(delta.total_seconds() // 3600)
    minutes = int((delta.total_seconds() % 3600) // 60)

    if heures_total >= 48:
        jours = heures_total // 24
        return f"{jours} jours"
    elif heures_total >= 24:
        return "demain"
    elif heures_total > 0:
        return f"{heures_total}h{minutes:02d}" if minutes else f"{heures_total}h"
    elif minutes > 0:
        return f"{minutes} minutes"
    else:
        return "maintenant"


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════


class ServiceRappels:
    """Service de rappels intelligents adaptatifs.

    Génère des rappels personnalisés selon le type d'événement,
    avec des délais adaptés à chaque situation familiale.
    """

    def regle_pour_type(self, type_evenement: str) -> RegleRappel:
        """Retourne la règle de rappel pour un type d'événement.

        Args:
            type_evenement: Type d'événement (valeur de TypeEvenement).

        Returns:
            Règle de rappel correspondante.
        """
        return _REGLES_RAPPEL.get(type_evenement, _REGLE_DEFAUT)

    def generer_rappels_evenement(
        self,
        titre: str,
        type_evenement: str,
        date_jour: date,
        heure_debut: time | None = None,
    ) -> list[Rappel]:
        """Génère les rappels pour un événement donné.

        Args:
            titre: Titre de l'événement.
            type_evenement: Type d'événement.
            date_jour: Date de l'événement.
            heure_debut: Heure de début (None = journée entière → 8h par défaut).

        Returns:
            Liste de Rappel à envoyer.
        """
        regle = self.regle_pour_type(type_evenement)

        # Construire le datetime de l'événement
        heure = heure_debut or time(8, 0)
        dt_evenement = datetime.combine(date_jour, heure)

        rappels = []
        for delai in regle.delais:
            dt_rappel = dt_evenement - delai

            # Ne pas générer de rappels dans le passé
            if dt_rappel < datetime.now():
                continue

            # Formater le message
            delai_str = _formater_delai(delai)
            message = regle.message_template.format(
                titre=titre,
                heure=heure.strftime("%H:%M"),
                delai=delai_str,
            )

            rappels.append(
                Rappel(
                    evenement_titre=titre,
                    evenement_type=type_evenement,
                    date_evenement=date_jour,
                    heure_evenement=heure_debut,
                    date_rappel=dt_rappel,
                    priorite=regle.priorite,
                    message=message,
                    icone=regle.icone,
                )
            )

        return rappels

    @avec_cache(ttl=300)
    def rappels_a_venir(self, heures: int = 48) -> list[Rappel]:
        """Retourne tous les rappels à venir dans les prochaines heures.

        Charge les événements du calendrier et génère les rappels.

        Args:
            heures: Fenêtre de temps en heures.

        Returns:
            Liste de rappels triés par date.
        """
        rappels: list[Rappel] = []
        maintenant = datetime.now()
        fenetre = maintenant + timedelta(hours=heures)

        try:
            # Charger les événements via le service calendrier
            from src.services.famille.calendrier_planning import (
                obtenir_service_calendrier_planning,
            )

            service_cal = obtenir_service_calendrier_planning()
            events = service_cal.charger_events_periode(
                date_debut=maintenant.date(),
                date_fin=fenetre.date() + timedelta(days=1),
            )

            for evt in events:
                evt_date = getattr(evt, "date_debut", None) or getattr(evt, "date_repas", None)
                if not evt_date:
                    continue

                evt_heure = getattr(evt, "heure_debut", None)
                evt_titre = getattr(evt, "titre", "") or getattr(evt, "description", "Événement")
                evt_type = getattr(evt, "type_evenement", "evenement") or "evenement"

                rappels_evt = self.generer_rappels_evenement(
                    titre=evt_titre,
                    type_evenement=evt_type,
                    date_jour=evt_date,
                    heure_debut=evt_heure,
                )

                # Filtrer dans la fenêtre
                for r in rappels_evt:
                    if maintenant <= r.date_rappel <= fenetre:
                        rappels.append(r)

        except Exception as e:
            logger.warning(f"Impossible de charger les rappels: {e}")

        # Ajouter les rappels pour jours spéciaux
        rappels.extend(self._rappels_jours_speciaux(heures))

        # Trier par date de rappel
        rappels.sort(key=lambda r: r.date_rappel)

        return rappels

    def _rappels_jours_speciaux(self, heures: int = 48) -> list[Rappel]:
        """Génère les rappels pour les prochains jours spéciaux."""
        rappels: list[Rappel] = []

        try:
            from src.services.famille.jours_speciaux import obtenir_service_jours_speciaux

            service_js = obtenir_service_jours_speciaux()
            prochains = service_js.prochains_jours_speciaux(nb=10)

            for js in prochains:
                rappels_js = self.generer_rappels_evenement(
                    titre=js.nom,
                    type_evenement=js.type,
                    date_jour=js.date_jour,
                    heure_debut=None,
                )

                maintenant = datetime.now()
                fenetre = maintenant + timedelta(hours=heures)

                for r in rappels_js:
                    if maintenant <= r.date_rappel <= fenetre:
                        rappels.append(r)

        except Exception as e:
            logger.warning(f"Impossible de charger les rappels jours spéciaux: {e}")

        return rappels

    def rappels_priorite_haute(self, heures: int = 24) -> list[Rappel]:
        """Retourne uniquement les rappels de priorité haute.

        Utile pour les notifications push et le dashboard.

        Args:
            heures: Fenêtre de temps.

        Returns:
            Rappels haute priorité uniquement.
        """
        tous = self.rappels_a_venir(heures)
        return [r for r in tous if r.priorite == PrioriteRappel.HAUTE]


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("rappels_planning", tags={"planning", "notifications"})
def _creer_service_rappels() -> ServiceRappels:
    return ServiceRappels()


def obtenir_service_rappels() -> ServiceRappels:
    """Factory pour obtenir le service rappels (singleton)."""
    return _creer_service_rappels()
