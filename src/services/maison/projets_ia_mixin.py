"""
Mixin IA Projets — Méthodes d'intelligence artificielle du service projets.

Extrait de projets_service.py pour maintenir chaque fichier sous 500 LOC.
Contient:
- Estimation complète de projet (budget, tâches, matériaux)
- Suggestions de tâches
- Estimation budget
- Suggestions alternatives économiques
- Priorisation et planification IA
- Identification des risques
- Calcul ROI rénovations
"""

from __future__ import annotations

import logging
from decimal import Decimal

from ..maison.schemas import (
    MaterielProjet,
    ProjetEstimation,
    TacheProjetCreate,
)

logger = logging.getLogger(__name__)


class ProjetsIAMixin:
    """Mixin fournissant les méthodes IA du service projets.

    Requiert que la classe parente hérite de BaseAIService
    (pour self.call_with_cache et self.client).
    """

    # ─────────────────────────────────────────────────────────
    # ESTIMATION COMPLÈTE
    # ─────────────────────────────────────────────────────────

    async def estimer_projet(
        self, nom: str, description: str, categorie: str = "travaux"
    ) -> ProjetEstimation:
        """Estimation complète d'un projet par l'IA.

        Args:
            nom: Nom du projet
            description: Description détaillée
            categorie: Catégorie du projet

        Returns:
            ProjetEstimation avec budget, tâches, matériaux
        """
        prompt = f"""Analyse ce projet maison et fournis une estimation complète:

Projet: {nom}
Description: {description}
Catégorie: {categorie}

Génère en JSON:
{{
    "budget_min": 100,
    "budget_max": 200,
    "duree_jours": 2,
    "taches": [
        {{"nom": "Préparation", "ordre": 1, "duree_min": 60, "materiels": ["bâche"]}},
        ...
    ],
    "materiels": [
        {{"nom": "Peinture blanche 10L", "quantite": 2, "prix": 35, "magasin": "Leroy Merlin", "alternatif": "Marque distributeur 25€"}},
        ...
    ],
    "risques": ["Mauvaise préparation des murs", ...],
    "conseils": ["Bien protéger le sol", ...]
}}

Sois réaliste sur les prix (France 2026)."""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es entrepreneur en rénovation avec 20 ans d'expérience. Donne des estimations précises.",
                max_tokens=1200,
            )
            import json

            data = json.loads(response)

            taches = [
                TacheProjetCreate(
                    nom=t.get("nom", "Tâche"),
                    ordre=t.get("ordre", 0),
                    duree_estimee_min=t.get("duree_min"),
                    materiels_requis=t.get("materiels", []),
                )
                for t in data.get("taches", [])
            ]

            materiels = [
                MaterielProjet(
                    nom=m.get("nom", "Matériel"),
                    quantite=m.get("quantite", 1),
                    prix_estime=Decimal(str(m.get("prix", 0))) if m.get("prix") else None,
                    magasin_suggere=m.get("magasin"),
                    alternatif_eco=m.get("alternatif"),
                )
                for m in data.get("materiels", [])
            ]

            return ProjetEstimation(
                nom_projet=nom,
                description_analysee=description,
                budget_estime_min=Decimal(str(data.get("budget_min", 50))),
                budget_estime_max=Decimal(str(data.get("budget_max", 100))),
                duree_estimee_jours=data.get("duree_jours", 1),
                taches_suggerees=taches,
                materiels_necessaires=materiels,
                risques_identifies=data.get("risques", []),
                conseils_ia=data.get("conseils", []),
            )

        except Exception as e:
            logger.warning(f"Estimation projet IA échouée: {e}")
            return ProjetEstimation(
                nom_projet=nom,
                description_analysee=description,
                budget_estime_min=Decimal("50"),
                budget_estime_max=Decimal("200"),
                duree_estimee_jours=2,
                taches_suggerees=[
                    TacheProjetCreate(nom="Préparation", ordre=1),
                    TacheProjetCreate(nom="Exécution", ordre=2),
                    TacheProjetCreate(nom="Finition", ordre=3),
                ],
                materiels_necessaires=[],
                risques_identifies=["Estimation automatique non disponible"],
                conseils_ia=["Demander un devis professionnel pour validation"],
            )

    async def suggerer_taches(self, nom_projet: str, description: str) -> str:
        """Suggère des tâches pour un projet.

        Args:
            nom_projet: Nom du projet
            description: Description du projet

        Returns:
            Texte avec tâches suggérées
        """
        prompt = f"""Pour le projet "{nom_projet}" : {description}
Suggère 5-7 tâches concrètes et numérotées. Ordonne par ordre logique.
Inclus le temps estimé pour chaque tâche."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en gestion de projets domestiques",
            max_tokens=700,
        )

    # ─────────────────────────────────────────────────────────
    # ESTIMATION BUDGET
    # ─────────────────────────────────────────────────────────

    async def estimer_budget(
        self, nom_projet: str, complexite: str = "moyen"
    ) -> dict[str, Decimal]:
        """Estime le budget d'un projet.

        Args:
            nom_projet: Nom du projet
            complexite: Niveau de complexité (simple, moyen, complexe)

        Returns:
            Dict avec budget min/max
        """
        prompt = f"""Pour un projet "{nom_projet}" de complexité {complexite}:
- Estime le budget matériaux (min-max)
- Estime le budget si fait par pro (min-max)

Format JSON: {{"materiaux_min": 100, "materiaux_max": 200, "pro_min": 500, "pro_max": 1000}}"""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es expert en estimation de coûts travaux",
                max_tokens=300,
            )
            import json

            data = json.loads(response)
            return {
                "materiaux_min": Decimal(str(data.get("materiaux_min", 50))),
                "materiaux_max": Decimal(str(data.get("materiaux_max", 200))),
                "pro_min": Decimal(str(data.get("pro_min", 300))),
                "pro_max": Decimal(str(data.get("pro_max", 800))),
            }
        except Exception as e:
            logger.warning(f"Estimation budget échouée: {e}")
            return {
                "materiaux_min": Decimal("50"),
                "materiaux_max": Decimal("200"),
                "pro_min": Decimal("300"),
                "pro_max": Decimal("800"),
            }

    async def suggerer_alternatives(self, materiels: list[MaterielProjet]) -> list[MaterielProjet]:
        """Suggère des alternatives économiques pour les matériaux.

        Args:
            materiels: Liste de matériaux originaux

        Returns:
            Liste de matériaux avec alternatives
        """
        if not materiels:
            return []

        materiels_txt = "\n".join(
            f"- {m.nom}: {m.prix_estime}€" for m in materiels if m.prix_estime
        )

        prompt = f"""Pour ces matériaux de bricolage:
{materiels_txt}

Suggère pour chaque une alternative moins chère mais de qualité acceptable.
Format JSON: [{{"original": "Nom", "alternatif": "Alternative", "prix_alternatif": 20}}]"""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es expert en matériaux de construction et rapport qualité/prix",
                max_tokens=600,
            )
            import json

            alternatives = json.loads(response)

            for m in materiels:
                for alt in alternatives:
                    if m.nom in alt.get("original", ""):
                        m.alternatif_eco = alt.get("alternatif")
                        if alt.get("prix_alternatif"):
                            m.alternatif_prix = Decimal(str(alt["prix_alternatif"]))

            return materiels
        except Exception as e:
            logger.warning(f"Suggestion alternatives échouée: {e}")
            return materiels

    # ─────────────────────────────────────────────────────────
    # PRIORISATION & PLANIFICATION
    # ─────────────────────────────────────────────────────────

    async def prioriser_taches(self, nom_projet: str, taches: list[str]) -> list[str]:
        """Priorise les tâches d'un projet.

        Args:
            nom_projet: Nom du projet
            taches: Liste des tâches à prioriser

        Returns:
            Liste des tâches réordonnées
        """
        taches_txt = "\n".join(f"- {t}" for t in taches)

        prompt = f"""Pour le projet "{nom_projet}", réordonne ces tâches par priorité:
{taches_txt}

Critères: dépendances, criticité, ordre logique.
Explique brièvement l'ordre choisi."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en priorisation et planification",
            max_tokens=500,
        )

    async def identifier_risques(self, nom_projet: str, description: str) -> list[str]:
        """Identifie les risques potentiels d'un projet.

        Args:
            nom_projet: Nom du projet
            description: Description du projet

        Returns:
            Liste des risques identifiés
        """
        prompt = f"""Pour "{nom_projet}" : {description}
Identifie 3-5 risques/blocages principaux et comment les éviter.
Format liste."""

        response = await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en gestion de risques de projets",
            max_tokens=500,
        )

        return [
            line.strip("- •").strip()
            for line in response.split("\n")
            if line.strip() and line.strip()[0] in "-•"
        ]

    # ─────────────────────────────────────────────────────────
    # ROI RÉNOVATIONS
    # ─────────────────────────────────────────────────────────

    async def calculer_roi(self, type_renovation: str, cout_estime: Decimal) -> dict[str, any]:
        """Calcule le ROI d'une rénovation énergétique.

        Args:
            type_renovation: Type (isolation, fenêtres, chaudière)
            cout_estime: Coût estimé du projet

        Returns:
            Dict avec économies annuelles et temps de retour
        """
        prompt = f"""Pour une rénovation "{type_renovation}" coûtant {cout_estime}€:
- Estime les économies d'énergie annuelles (€)
- Calcule le temps de retour sur investissement
- Indique les aides disponibles (MaPrimeRénov, CEE)

Format JSON: {{"economies_annuelles": 200, "retour_annees": 5, "aides_estimees": 500}}"""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es conseiller en rénovation énergétique certifié",
                max_tokens=400,
            )
            import json

            return json.loads(response)
        except Exception as e:
            logger.warning(f"Calcul ROI échoué: {e}")
            return {
                "economies_annuelles": 0,
                "retour_annees": None,
                "aides_estimees": 0,
            }
