"""
Mixin Tâches Jardin - Génération automatique des tâches.

Fonctionnalités:
- Génération de tâches selon le calendrier de semis/plantation
- Tâches d'arrosage basées sur la météo
- Alertes météo (gel, etc.)
- Entretien régulier planifié
"""

import logging
from datetime import date

from .jardin_catalogue_mixin import JardinCatalogueMixin

logger = logging.getLogger(__name__)


class JardinTachesMixin(JardinCatalogueMixin):
    """Mixin pour la génération automatique des tâches jardin."""

    # ─────────────────────────────────────────────────────────
    # GÉNÉRATION AUTOMATIQUE DES TÂCHES
    # ─────────────────────────────────────────────────────────

    def generer_taches(self, plantes: list[dict], meteo: dict | None = None) -> list[dict]:
        """
        Génère automatiquement les tâches du jardin.

        Args:
            plantes: Liste des plantes (dict avec plante_id, semis_fait, plante_en_terre)
            meteo: Données météo optionnelles

        Returns:
            Liste de tâches triées par priorité
        """
        meteo = meteo or {}
        taches = []
        catalogue = self.charger_catalogue_plantes()
        aujourd_hui = date.today()
        mois = aujourd_hui.month

        # 1. Tâches liées au calendrier
        for plante_id, plante_data in catalogue.get("plantes", {}).items():
            taches.extend(self._generer_taches_calendrier(plante_id, plante_data, plantes, mois))

        # 2. Tâches d'arrosage
        taches.extend(self._generer_taches_arrosage(plantes, meteo, catalogue))

        # 3. Tâches météo
        taches.extend(self._generer_taches_meteo(plantes, meteo))

        # 4. Entretien régulier
        taches.extend(self._generer_taches_entretien(plantes, aujourd_hui))

        # Trier par priorité
        ordre_priorite = {"urgente": 0, "haute": 1, "normale": 2, "basse": 3}
        taches.sort(key=lambda t: ordre_priorite.get(t.get("priorite", "normale"), 2))

        return taches

    def _generer_taches_calendrier(
        self, plante_id: str, plante_data: dict, mes_plantes: list[dict], mois: int
    ) -> list[dict]:
        """Génère les tâches liées au calendrier de semis/plantation."""
        taches = []

        # Semis en intérieur
        if mois in plante_data.get("semis_interieur", []):
            deja_semis = any(
                p.get("plante_id") == plante_id and p.get("semis_fait") for p in mes_plantes
            )
            if not deja_semis:
                taches.append(
                    {
                        "type": "semis",
                        "titre": f"Semer {plante_data.get('nom', plante_id)} en intérieur",
                        "description": f"C'est la bonne période pour semer les {plante_data.get('nom')} en godets.",
                        "emoji": plante_data.get("emoji", "🌱"),
                        "priorite": "haute"
                        if mois == plante_data.get("semis_interieur", [0])[-1]
                        else "normale",
                        "duree_min": 20,
                        "plante_id": plante_id,
                    }
                )

        # Semis direct
        if mois in plante_data.get("semis_direct", []):
            deja_semis = any(
                p.get("plante_id") == plante_id and p.get("semis_fait") for p in mes_plantes
            )
            if not deja_semis:
                taches.append(
                    {
                        "type": "semis",
                        "titre": f"Semer {plante_data.get('nom', plante_id)} en pleine terre",
                        "description": f"Semis direct possible pour les {plante_data.get('nom')}.",
                        "emoji": plante_data.get("emoji", "🌱"),
                        "priorite": "normale",
                        "duree_min": 30,
                        "plante_id": plante_id,
                    }
                )

        # Plantation extérieur
        if mois in plante_data.get("plantation_exterieur", []):
            a_planter = [
                p
                for p in mes_plantes
                if p.get("plante_id") == plante_id
                and p.get("semis_fait")
                and not p.get("plante_en_terre")
            ]
            if a_planter:
                taches.append(
                    {
                        "type": "plantation",
                        "titre": f"Planter {plante_data.get('nom', plante_id)} en extérieur",
                        "description": f"Vos plants de {plante_data.get('nom')} sont prêts à être repiqués.",
                        "emoji": plante_data.get("emoji", "🌱"),
                        "priorite": "haute",
                        "duree_min": 45,
                        "plante_id": plante_id,
                    }
                )

        return taches

    def _generer_taches_arrosage(
        self, mes_plantes: list[dict], meteo: dict, catalogue: dict
    ) -> list[dict]:
        """Génère les tâches d'arrosage basées sur météo."""
        taches = []
        plantes_en_terre = [p for p in mes_plantes if p.get("plante_en_terre")]

        if plantes_en_terre and not meteo.get("pluie_prevue"):
            besoin_eau_eleve = any(
                catalogue.get("plantes", {}).get(p.get("plante_id"), {}).get("besoin_eau")
                == "élevé"
                for p in plantes_en_terre
            )

            if meteo.get("temperature", 20) > 20 or besoin_eau_eleve:
                taches.append(
                    {
                        "type": "arrosage",
                        "titre": "Arroser le potager",
                        "description": f"Température de {meteo.get('temperature')}°C. Arrosez de préférence le soir.",
                        "emoji": "💧",
                        "priorite": "urgente" if meteo.get("temperature", 0) > 28 else "haute",
                        "duree_min": 20,
                    }
                )

        return taches

    def _generer_taches_meteo(self, mes_plantes: list[dict], meteo: dict) -> list[dict]:
        """Génère les tâches liées aux alertes météo."""
        taches = []

        if meteo.get("gel_risque"):
            if any(p.get("plante_en_terre") for p in mes_plantes):
                taches.append(
                    {
                        "type": "protection",
                        "titre": "Protéger les plants du gel",
                        "description": "Risque de gel annoncé. Installez voiles d'hivernage ou rentrez les pots.",
                        "emoji": "🥶",
                        "priorite": "urgente",
                        "duree_min": 30,
                    }
                )

        return taches

    def _generer_taches_entretien(self, mes_plantes: list[dict], aujourd_hui: date) -> list[dict]:
        """Génère les tâches d'entretien régulier."""
        taches = []
        jour_semaine = aujourd_hui.weekday()
        plantes_en_terre = [p for p in mes_plantes if p.get("plante_en_terre")]

        if jour_semaine == 5 and plantes_en_terre:  # Samedi
            taches.append(
                {
                    "type": "entretien",
                    "titre": "Désherber et biner",
                    "description": "Entretien hebdomadaire: désherbage et aération du sol.",
                    "emoji": "🧹",
                    "priorite": "normale",
                    "duree_min": 45,
                }
            )

        if jour_semaine == 2:  # Mercredi
            taches.append(
                {
                    "type": "observation",
                    "titre": "Inspecter les plants",
                    "description": "Vérifiez l'état sanitaire, cherchez ravageurs et maladies.",
                    "emoji": "🔍",
                    "priorite": "normale",
                    "duree_min": 15,
                }
            )

        return taches
