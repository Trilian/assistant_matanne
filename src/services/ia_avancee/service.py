"""
Service IA Avancée — modules IA avancée.

Service central regroupant les 14 fonctionnalités IA proactives.
Hérite de BaseAIService pour rate limiting + cache + circuit breaker auto.
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, timedelta
from typing import Any

from pydantic import BaseModel

from src.core.ai import obtenir_client_ia
from src.core.db import obtenir_contexte_db
from src.core.decorators import avec_cache, avec_gestion_erreurs
from src.core.monitoring import chronometre
from src.core.validation.sanitizer import NettoyeurEntrees
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

from .types import (
    AdaptationMeteo,
    AdaptationsMeteoResponse,
    AnalysePhotoMultiUsage,
    DiagnosticPlante,
    DocumentAnalyse,
    EstimationTravauxPhoto,
    IdeeCadeau,
    IdeesCadeauxResponse,
    JourVoyage,
    OptimisationRoutine,
    OptimisationRoutinesResponse,
    PlanningAdaptatif,
    PlanningVoyage,
    PredictionPanne,
    PredictionsPannesResponse,
    PrevisionDepenses,
    RecommandationEnergie,
    RecommandationsEnergieResponse,
    SuggestionAchat,
    SuggestionsAchatsResponse,
    SuggestionProactive,
    SuggestionsProactivesResponse,
)

logger = logging.getLogger(__name__)


def _sanitiser(texte: str, max_len: int = 200) -> str:
    """Sanitise un texte utilisateur avant injection dans un prompt IA."""
    return NettoyeurEntrees.nettoyer_chaine(texte, longueur_max=max_len)


class IAAvanceeService(BaseAIService):
    """Service IA avancé — fonctionnalités proactives et contextuelles.

    Hérite de BaseAIService : rate limiting, cache sémantique,
    circuit breaker et parsing JSON/Pydantic automatiques.
    """

    def __init__(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="ia_avancee",
            default_ttl=1800,
            default_temperature=0.7,
            service_name="ia_avancee",
        )

    # ═══════════════════════════════════════════════════════════
    # 6.1 — SUGGESTIONS ACHATS IA (historique consommation)
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=3600, key_func=lambda self, jours: f"suggestions_achats_{jours}")
    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.suggestions_achats", seuil_alerte_ms=10000)
    def suggerer_achats(self, jours: int = 90) -> SuggestionsAchatsResponse | None:
        """Suggère des achats basés sur l'historique de consommation.

        Analyse l'inventaire et l'historique des courses pour prédire
        les produits à racheter.
        """
        contexte = self._collecter_contexte_inventaire(jours)

        prompt = f"""Analyse l'historique de consommation suivant et suggère les achats prioritaires.

{contexte}

Retourne un JSON :
{{"suggestions": [{{"nom": "Lait", "raison": "Stock bas, consommation régulière", "urgence": "haute", "frequence_achat_jours": 7, "quantite_suggeree": "2 bouteilles"}}], "nb_produits_analyses": 50, "periode_analyse_jours": {jours}}}

Règles :
- Prioriose les produits en rupture ou bientôt épuisés
- Indique la fréquence d'achat observée
- Maximum 10 suggestions"""

        result = self.call_with_cache_sync(
            prompt=prompt,
            system_prompt="Tu es un assistant courses intelligent. Retourne UNIQUEMENT du JSON valide.",
            max_tokens=1200,
        )
        if not result:
            return None

        return self._parse_json_safe(result, SuggestionsAchatsResponse)

    def _collecter_contexte_inventaire(self, jours: int) -> str:
        """Collecte le contexte inventaire pour les suggestions."""
        try:
            with obtenir_contexte_db() as session:
                from src.core.models import ArticleInventaire

                articles = session.query(ArticleInventaire).limit(100).all()
                if not articles:
                    return "Inventaire vide — pas de données historiques."

                lignes = []
                for a in articles:
                    stock_status = "OK"
                    if hasattr(a, "quantite_min") and a.quantite is not None:
                        if a.quantite <= 0:
                            stock_status = "RUPTURE"
                        elif a.quantite_min and a.quantite < a.quantite_min:
                            stock_status = "BAS"
                    lignes.append(
                        f"- {a.nom}: quantité={a.quantite}, statut={stock_status}"
                    )
                return f"Inventaire ({len(articles)} produits, {jours}j analyse):\n" + "\n".join(
                    lignes[:50]
                )
        except Exception as e:
            logger.warning("Erreur collecte inventaire: %s", e)
            return "Données inventaire indisponibles."

    # ═══════════════════════════════════════════════════════════
    # 6.2 — PLANNING ADAPTATIF (météo + énergie + budget)
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=1800)
    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.planning_adaptatif", seuil_alerte_ms=12000)
    def generer_planning_adaptatif(
        self,
        meteo: dict | None = None,
        budget_restant: float | None = None,
    ) -> PlanningAdaptatif | None:
        """Génère un planning adapté au contexte multi-sources."""
        contexte_parts = []

        if meteo:
            contexte_parts.append(f"Météo : {json.dumps(meteo, ensure_ascii=False)}")
        if budget_restant is not None:
            contexte_parts.append(f"Budget restant ce mois : {budget_restant}€")

        # Compléter avec données DB
        contexte_parts.append(self._collecter_contexte_planning())
        contexte_str = "\n".join(contexte_parts) if contexte_parts else "Aucun contexte spécifique."

        prompt = f"""Adapte le planning familial en fonction du contexte suivant :

{contexte_str}

Retourne un JSON :
{{"recommandations": ["..."], "repas_suggerees": [{{"jour": "Lundi", "repas": "Soupe chaude", "raison": "Temps froid"}}], "activites_suggerees": [{{"jour": "Samedi", "activite": "Musée", "raison": "Pluie prévue"}}], "score_adaptation": 75, "contexte_utilise": {{"meteo": true, "budget": true}}}}"""

        result = self.call_with_cache_sync(
            prompt=prompt,
            system_prompt="Tu es un assistant familial intelligent. JSON uniquement.",
            max_tokens=1500,
        )
        if not result:
            return None
        return self._parse_json_safe(result, PlanningAdaptatif)

    def _collecter_contexte_planning(self) -> str:
        """Collecte le contexte planning actuel."""
        try:
            with obtenir_contexte_db() as session:
                from src.core.models import Repas

                today = date.today()
                fin = today + timedelta(days=7)
                repas = (
                    session.query(Repas)
                    .filter(Repas.date_repas >= today, Repas.date_repas <= fin)
                    .limit(20)
                    .all()
                )
                if repas:
                    return f"Repas planifiés cette semaine : {len(repas)} repas"
                return "Aucun repas planifié cette semaine."
        except Exception:
            return "Données planning indisponibles."

    # ═══════════════════════════════════════════════════════════
    # 6.3 — DIAGNOSTIC PLANTES PHOTO (Pixtral)
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.diagnostic_plante", seuil_alerte_ms=15000)
    def diagnostiquer_plante_photo(
        self, image_bytes: bytes
    ) -> DiagnosticPlante | None:
        """Diagnostique l'état d'une plante via photo Pixtral."""
        from src.services.integrations.multimodal import obtenir_multimodal_service

        multimodal = obtenir_multimodal_service()
        image_b64 = multimodal._encode_image(image_bytes)

        prompt = """Analyse cette photo de plante et diagnostique son état.

Retourne un JSON :
{"nom_plante": "Basilic", "etat_general": "moyen", "problemes_detectes": ["Feuilles jaunies"], "causes_probables": ["Arrosage excessif"], "traitements_recommandes": ["Réduire l'arrosage"], "arrosage_conseil": "1 fois/semaine", "exposition_conseil": "Mi-ombre", "confiance": 0.8}"""

        try:
            result = multimodal._call_vision_model_sync(
                image_b64=image_b64,
                prompt=prompt,
                system_prompt="Tu es un botaniste expert. Analyse la plante et retourne du JSON.",
            )
            if isinstance(result, dict):
                return DiagnosticPlante(**result)
            if isinstance(result, str):
                return self._parse_json_safe(result, DiagnosticPlante)
        except Exception as e:
            logger.warning("Diagnostic plante vision échoué: %s", e)

        return None

    # ═══════════════════════════════════════════════════════════
    # 6.4 — PRÉVISION DÉPENSES FIN DE MOIS
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=3600)
    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.prevision_depenses", seuil_alerte_ms=10000)
    def prevoir_depenses_fin_mois(self) -> PrevisionDepenses | None:
        """Prévoit les dépenses jusqu'à la fin du mois."""
        contexte = self._collecter_contexte_budget()

        prompt = f"""Analyse les dépenses et prévois le total fin de mois.

{contexte}

Retourne un JSON :
{{"depenses_actuelles": 1200.50, "prevision_fin_mois": 1800.00, "budget_mensuel": 2000.00, "ecart_prevu": 200.00, "tendance": "hausse", "postes_vigilance": [{{"poste": "Alimentation", "depense": 450, "pourcentage_budget": 30}}], "conseils_economies": ["Réduire les repas extérieurs"]}}"""

        result = self.call_with_cache_sync(
            prompt=prompt,
            system_prompt="Tu es un conseiller financier familial. JSON uniquement. Français.",
            max_tokens=1200,
        )
        if not result:
            return None
        return self._parse_json_safe(result, PrevisionDepenses)

    def _collecter_contexte_budget(self) -> str:
        """Collecte le contexte budget pour les prévisions."""
        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func

                from src.core.models import BudgetFamille

                today = date.today()
                debut_mois = today.replace(day=1)

                depenses = (
                    session.query(func.sum(BudgetFamille.montant))
                    .filter(
                        BudgetFamille.date >= debut_mois,
                        BudgetFamille.date <= today,
                    )
                    .scalar()
                    or 0
                )

                jour_actuel = today.day
                jours_mois = 30
                return (
                    f"Dépenses du 1er au {jour_actuel} : {float(depenses):.2f}€\n"
                    f"Jours écoulés : {jour_actuel}/{jours_mois}"
                )
        except Exception:
            return "Données budget indisponibles."

    # ═══════════════════════════════════════════════════════════
    # 6.5 — IDÉES CADEAUX IA (anniversaires)
    # ═══════════════════════════════════════════════════════════

    @avec_cache(
        ttl=86400,
        key_func=lambda self, nom, age, relation, budget, occasion: (
            f"cadeaux_{nom}_{age}_{relation}_{budget}_{occasion}"
        ),
    )
    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.idees_cadeaux", seuil_alerte_ms=8000)
    def suggerer_cadeaux(
        self,
        nom: str,
        age: int,
        relation: str = "famille",
        budget_max: float = 50.0,
        occasion: str = "anniversaire",
    ) -> IdeesCadeauxResponse | None:
        """Suggère des idées cadeaux personnalisées."""
        nom_safe = _sanitiser(nom, 50)
        relation_safe = _sanitiser(relation, 30)
        occasion_safe = _sanitiser(occasion, 30)

        prompt = f"""Suggère 5 idées cadeaux pour {nom_safe}, {age} ans ({relation_safe}).
Occasion : {occasion_safe}. Budget max : {budget_max}€.

Retourne un JSON :
{{"idees": [{{"titre": "Livre illustré", "description": "Album photo personnalisé", "fourchette_prix": "15-25€", "ou_acheter": "Amazon / Fnac", "pertinence": "haute", "raison": "Adapté à l'âge"}}], "destinataire": "{nom_safe}", "occasion": "{occasion_safe}"}}"""

        result = self.call_with_cache_sync(
            prompt=prompt,
            system_prompt="Tu es expert en cadeaux personnalisés. JSON uniquement. Français.",
            max_tokens=1000,
        )
        if not result:
            return None
        return self._parse_json_safe(result, IdeesCadeauxResponse)

    # ═══════════════════════════════════════════════════════════
    # 6.6 — ANALYSE PHOTO MULTI-USAGE
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.analyse_photo_multi", seuil_alerte_ms=15000)
    def analyser_photo_multi_usage(
        self, image_bytes: bytes
    ) -> AnalysePhotoMultiUsage | None:
        """Analyse une photo en détectant automatiquement le contexte.

        Un seul bouton — l'IA détecte si c'est une recette, une plante,
        un problème maison, un document, un plat, etc.
        """
        from src.services.integrations.multimodal import obtenir_multimodal_service

        multimodal = obtenir_multimodal_service()
        image_b64 = multimodal._encode_image(image_bytes)

        prompt = """Analyse cette image et détecte automatiquement son contexte.

Retourne un JSON :
{"contexte_detecte": "recette|plante|maison|document|plat|autre", "resume": "Description de ce que tu vois", "details": {"cle": "valeur spécifique au contexte"}, "actions_suggerees": ["Action 1", "Action 2"], "confiance": 0.85}

Catégories possibles :
- "recette" : photo de recette, livre de cuisine
- "plante" : plante, jardin, fleur
- "maison" : problème maison, travaux, pièce
- "document" : facture, contrat, papier administratif
- "plat" : nourriture, repas cuisiné
- "autre" : tout le reste"""

        try:
            result = multimodal._call_vision_model_sync(
                image_b64=image_b64,
                prompt=prompt,
                system_prompt="Tu es un assistant IA multi-compétences. Analyse et retourne du JSON.",
            )
            if isinstance(result, dict):
                return AnalysePhotoMultiUsage(**result)
            if isinstance(result, str):
                return self._parse_json_safe(result, AnalysePhotoMultiUsage)
        except Exception as e:
            logger.warning("Analyse photo multi-usage échouée: %s", e)

        return None

    # ═══════════════════════════════════════════════════════════
    # 6.7 — OPTIMISATION ROUTINES IA
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=3600)
    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.optimisation_routines", seuil_alerte_ms=10000)
    def optimiser_routines(self) -> OptimisationRoutinesResponse | None:
        """Analyse les routines familiales et suggère des optimisations."""
        contexte = self._collecter_contexte_routines()

        prompt = f"""Analyse les routines familiales suivantes et suggère des optimisations.

{contexte}

Retourne un JSON :
{{"optimisations": [{{"routine_concernee": "Routine matin", "probleme_identifie": "Trop d'étapes", "suggestion": "Regrouper préparation vêtements + sac la veille", "gain_estime": "15 min/jour", "priorite": "haute"}}], "score_efficacite_actuel": 60, "score_efficacite_projete": 80}}"""

        result = self.call_with_cache_sync(
            prompt=prompt,
            system_prompt="Tu es un expert en organisation familiale et productivité. JSON uniquement.",
            max_tokens=1200,
        )
        if not result:
            return None
        return self._parse_json_safe(result, OptimisationRoutinesResponse)

    def _collecter_contexte_routines(self) -> str:
        """Collecte le contexte des routines."""
        try:
            with obtenir_contexte_db() as session:
                from src.core.models.famille import RoutineFamille

                routines = session.query(RoutineFamille).limit(20).all()
                if not routines:
                    return "Aucune routine enregistrée."
                lignes = []
                for r in routines:
                    nom = getattr(r, "nom", "Routine")
                    frequence = getattr(r, "frequence", "quotidien")
                    lignes.append(f"- {nom} ({frequence})")
                return f"Routines existantes ({len(routines)}):\n" + "\n".join(lignes)
        except Exception:
            return "Données routines indisponibles."

    # ═══════════════════════════════════════════════════════════
    # 6.8 — ANALYSE DOCUMENTS PHOTO (OCR + classement)
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.analyse_document", seuil_alerte_ms=15000)
    def analyser_document_photo(
        self, image_bytes: bytes
    ) -> DocumentAnalyse | None:
        """Analyse un document photographié (OCR + classification auto)."""
        from src.services.integrations.multimodal import obtenir_multimodal_service

        multimodal = obtenir_multimodal_service()
        image_b64 = multimodal._encode_image(image_bytes)

        prompt = """Analyse ce document photographié. Extrais les informations clés.

Retourne un JSON :
{"type_document": "facture|contrat|ordonnance|administratif|autre", "titre": "Facture EDF", "date_document": "2026-03-15", "emetteur": "EDF", "montant": 85.50, "informations_cles": ["Numéro client: XXX", "Période: mars 2026"], "categorie_suggeree": "energie", "actions_suggerees": ["Archiver dans Maison > Charges", "Vérifier montant vs mois précédent"]}"""

        try:
            result = multimodal._call_vision_model_sync(
                image_b64=image_b64,
                prompt=prompt,
                system_prompt="Tu es un assistant administratif expert en OCR. Analyse et retourne du JSON.",
            )
            if isinstance(result, dict):
                return DocumentAnalyse(**result)
            if isinstance(result, str):
                return self._parse_json_safe(result, DocumentAnalyse)
        except Exception as e:
            logger.warning("Analyse document OCR échouée: %s", e)

        return None

    # ═══════════════════════════════════════════════════════════
    # 6.9 — ESTIMATION TRAVAUX PHOTO (avant/après)
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.estimation_travaux_photo", seuil_alerte_ms=15000)
    def estimer_travaux_photo(
        self,
        image_bytes: bytes,
        description: str = "",
    ) -> EstimationTravauxPhoto | None:
        """Estime des travaux à partir d'une photo (avant ou après)."""
        from src.services.integrations.multimodal import obtenir_multimodal_service

        multimodal = obtenir_multimodal_service()
        image_b64 = multimodal._encode_image(image_bytes)

        description_safe = _sanitiser(description, 200)
        complement = f"\nDescription additionnelle : {description_safe}" if description_safe else ""

        prompt = f"""Analyse cette photo de travaux/rénovation.{complement}

Retourne un JSON :
{{"type_travaux": "peinture|plomberie|electricite|maconnerie|autre", "description": "Peinture mur salon avec traces d'humidité", "budget_min": 200, "budget_max": 500, "duree_estimee": "2-3 jours", "difficulte": "moyen", "diy_possible": true, "artisans_recommandes": ["peintre", "plaquiste"], "materiaux_necessaires": [{{"nom": "Peinture anti-humidité", "quantite": "5L", "prix_estime": "45€"}}]}}

Prix en euros, contexte France 2026."""

        try:
            result = multimodal._call_vision_model_sync(
                image_b64=image_b64,
                prompt=prompt,
                system_prompt="Tu es un expert en rénovation/bâtiment. Retourne du JSON avec estimations précises.",
            )
            if isinstance(result, dict):
                return EstimationTravauxPhoto(**result)
            if isinstance(result, str):
                return self._parse_json_safe(result, EstimationTravauxPhoto)
        except Exception as e:
            logger.warning("Estimation travaux photo échouée: %s", e)

        return None

    # ═══════════════════════════════════════════════════════════
    # 6.10 — PLANNING VOYAGE IA
    # ═══════════════════════════════════════════════════════════

    @avec_cache(
        ttl=86400,
        key_func=lambda self, dest, jours, budget, avec_enfant: (
            f"voyage_{dest}_{jours}_{budget}_{avec_enfant}"
        ),
    )
    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.planning_voyage", seuil_alerte_ms=15000)
    def generer_planning_voyage(
        self,
        destination: str,
        duree_jours: int = 7,
        budget_total: float | None = None,
        avec_enfant: bool = True,
    ) -> PlanningVoyage | None:
        """Génère un planning de voyage complet."""
        dest_safe = _sanitiser(destination, 100)
        budget_txt = f"Budget total : {budget_total}€" if budget_total else "Budget flexible"
        enfant_txt = "Avec un enfant de ~2 ans (Jules)" if avec_enfant else "Adultes uniquement"

        prompt = f"""Planifie un voyage à {dest_safe} de {duree_jours} jours.
{budget_txt}. {enfant_txt}.

Retourne un JSON :
{{"destination": "{dest_safe}", "duree_jours": {duree_jours}, "budget_total_estime": 1500, "jours": [{{"jour": 1, "date": null, "activites": ["Arrivée et installation", "Visite centre-ville"], "repas_suggerees": ["Restaurant local"], "budget_jour": 150, "conseils": ["Réserver l'hôtel en avance"]}}], "check_list_depart": ["Passeport", "Doudou Jules"], "conseils_generaux": ["Prévoir des pauses régulières"], "adaptations_enfant": ["Emporter poussette compacte"]}}"""

        result = self.call_with_cache_sync(
            prompt=prompt,
            system_prompt="Tu es un expert en voyages familiaux. JSON uniquement. Français.",
            max_tokens=2500,
        )
        if not result:
            return None
        return self._parse_json_safe(result, PlanningVoyage)

    # ═══════════════════════════════════════════════════════════
    # 6.11 — RECOMMANDATIONS ÉCONOMIES ÉNERGIE
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=86400)
    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.recommandations_energie", seuil_alerte_ms=10000)
    def recommander_economies_energie(self) -> RecommandationsEnergieResponse | None:
        """Recommande des économies d'énergie basées sur la consommation."""
        contexte = self._collecter_contexte_energie()

        prompt = f"""Analyse la consommation énergétique et suggère des économies.

{contexte}

Retourne un JSON :
{{"recommandations": [{{"titre": "Programmateur chauffage", "description": "Installer un thermostat programmable pour réduire le chauffage la nuit", "economie_estimee": "15-20% sur le chauffage", "cout_mise_en_oeuvre": "50-150€", "difficulte": "facile", "priorite": "haute", "categorie": "chauffage"}}], "consommation_actuelle_resume": "Consommation élevée en chauffage", "potentiel_economie_global": "200-400€/an"}}"""

        result = self.call_with_cache_sync(
            prompt=prompt,
            system_prompt="Tu es un conseiller en efficacité énergétique. JSON uniquement. Français.",
            max_tokens=1500,
        )
        if not result:
            return None
        return self._parse_json_safe(result, RecommandationsEnergieResponse)

    def _collecter_contexte_energie(self) -> str:
        """Collecte le contexte énergie."""
        try:
            with obtenir_contexte_db() as session:
                from src.core.models.maison_extensions import ReleveCompteur

                releves = (
                    session.query(ReleveCompteur)
                    .order_by(ReleveCompteur.date.desc())
                    .limit(12)
                    .all()
                )
                if not releves:
                    return "Aucun relevé de compteur enregistré."

                lignes = []
                for r in releves:
                    type_c = getattr(r, "type_compteur", "inconnu")
                    valeur = getattr(r, "valeur", 0)
                    date_r = getattr(r, "date", "")
                    lignes.append(f"- {type_c}: {valeur} ({date_r})")
                return f"Relevés compteur ({len(releves)} derniers):\n" + "\n".join(lignes)
        except Exception:
            return "Données énergie indisponibles."

    # ═══════════════════════════════════════════════════════════
    # 6.12 — PRÉDICTION PANNES ENTRETIEN
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=86400)
    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.prediction_pannes", seuil_alerte_ms=10000)
    def predire_pannes(self) -> PredictionsPannesResponse | None:
        """Prédit les pannes probables des équipements."""
        contexte = self._collecter_contexte_equipements()

        prompt = f"""Analyse les équipements et prédit les risques de panne.

{contexte}

Retourne un JSON :
{{"predictions": [{{"equipement": "Chaudière", "risque": "moyen", "probabilite_pct": 35, "delai_estime": "6-12 mois", "signes_alerte": ["Bruit inhabituel", "Baisse de rendement"], "maintenance_preventive": ["Entretien annuel", "Purge radiateurs"], "cout_remplacement_estime": "3000-5000€"}}], "nb_equipements_analyses": 8, "score_sante_global": 70}}"""

        result = self.call_with_cache_sync(
            prompt=prompt,
            system_prompt="Tu es un technicien maintenance préventive expert. JSON uniquement. Français.",
            max_tokens=1500,
        )
        if not result:
            return None
        return self._parse_json_safe(result, PredictionsPannesResponse)

    def _collecter_contexte_equipements(self) -> str:
        """Collecte le contexte des équipements maison."""
        try:
            with obtenir_contexte_db() as session:
                from src.core.models.maison_extensions import Equipement

                equipements = session.query(Equipement).limit(20).all()
                if not equipements:
                    return "Aucun équipement enregistré."

                lignes = []
                for eq in equipements:
                    nom = getattr(eq, "nom", "Équipement")
                    date_achat = getattr(eq, "date_achat", None)
                    lignes.append(f"- {nom} (acheté: {date_achat or 'inconnu'})")
                return f"Équipements ({len(equipements)}):\n" + "\n".join(lignes)
        except Exception:
            return "Données équipements indisponibles."

    # ═══════════════════════════════════════════════════════════
    # 6.13 — SUGGESTIONS PROACTIVES
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=1800)
    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.suggestions_proactives", seuil_alerte_ms=12000)
    def generer_suggestions_proactives(self) -> SuggestionsProactivesResponse | None:
        """Génère des suggestions proactives multi-modules.

        L'app propose sans qu'on demande, basé sur l'état général.
        """
        contexte = self._collecter_contexte_global()

        prompt = f"""Analyse l'état général de la maison/famille et propose des suggestions proactives.

{contexte}

Retourne un JSON :
{{"suggestions": [{{"module": "cuisine", "titre": "Planifier les repas de la semaine", "message": "Aucun repas planifié pour la semaine prochaine. Voulez-vous que je génère un planning ?", "action_url": "/cuisine/planning", "priorite": "haute", "contexte": "Planning vide"}}, {{"module": "maison", "titre": "Entretien chaudière", "message": "L'entretien annuel est prévu dans 2 semaines.", "action_url": "/maison/entretien", "priorite": "normale", "contexte": "Rappel maintenance"}}], "date_generation": "{datetime.now().isoformat()}"}}

Maximum 5 suggestions, les plus pertinentes."""

        result = self.call_with_cache_sync(
            prompt=prompt,
            system_prompt="Tu es un assistant familial proactif. JSON uniquement. Français.",
            max_tokens=1500,
        )
        if not result:
            return None
        return self._parse_json_safe(result, SuggestionsProactivesResponse)

    def _collecter_contexte_global(self) -> str:
        """Collecte le contexte global multi-modules."""
        parties = []

        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func

                from src.core.models import ArticleInventaire, Repas

                today = date.today()
                fin = today + timedelta(days=7)

                # Planning
                repas_count = (
                    session.query(func.count(Repas.id))
                    .filter(Repas.date_repas >= today, Repas.date_repas <= fin)
                    .scalar()
                    or 0
                )
                parties.append(f"Repas planifiés 7j: {repas_count}")

                # Inventaire
                stock_bas = (
                    session.query(func.count(ArticleInventaire.id))
                    .filter(ArticleInventaire.quantite < ArticleInventaire.quantite_min)
                    .scalar()
                    or 0
                )
                parties.append(f"Produits en stock bas: {stock_bas}")

        except Exception:
            parties.append("Données partiellement indisponibles.")

        return "\n".join(parties) if parties else "Contexte minimal."

    # ═══════════════════════════════════════════════════════════
    # 6.14 — MÉTÉO → PLANNING (repas, jardin, activités)
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=3600)
    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.adaptations_meteo", seuil_alerte_ms=10000)
    def adapter_planning_meteo(
        self, previsions_meteo: dict
    ) -> AdaptationsMeteoResponse | None:
        """Adapte le planning en fonction des prévisions météo.

        Impacte repas, jardin, activités famille et entretien maison.
        """
        meteo_str = json.dumps(previsions_meteo, ensure_ascii=False, default=str)

        prompt = f"""Voici les prévisions météo pour les prochains jours :

{meteo_str}

Adapte le planning familial (repas, jardin, activités, entretien) en conséquence.

Retourne un JSON :
{{"adaptations": [{{"type_adaptation": "repas", "condition_meteo": "froid (5°C)", "recommandation": "Prévoir des soupes et plats réconfortants", "impact": "moyen"}}, {{"type_adaptation": "jardin", "condition_meteo": "gel nocturne", "recommandation": "Protéger les plantes fragiles avec un voile d'hivernage", "impact": "fort"}}, {{"type_adaptation": "activites", "condition_meteo": "pluie", "recommandation": "Activités intérieures : musée, cinéma, jeux de société", "impact": "moyen"}}], "meteo_resume": {{"temperature_min": 2, "temperature_max": 12, "conditions": "pluie intermittente"}}, "date_prevision": "{date.today().isoformat()}"}}"""

        result = self.call_with_cache_sync(
            prompt=prompt,
            system_prompt="Tu es un assistant familial expert en adaptation au climat. JSON uniquement. Français.",
            max_tokens=1500,
        )
        if not result:
            return None
        return self._parse_json_safe(result, AdaptationsMeteoResponse)

    # ═══════════════════════════════════════════════════════════
    # HELPERS INTERNES
    # ═══════════════════════════════════════════════════════════

    def _parse_json_safe(
        self, text: str, model: type[BaseModel]
    ) -> BaseModel | None:
        """Parse un texte JSON en modèle Pydantic avec nettoyage."""
        if not text:
            return None
        try:
            # Nettoyer le wrapper markdown si présent
            cleaned = text.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                # Retirer ```json et ```
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned = "\n".join(lines)

            data = json.loads(cleaned)
            return model(**data)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("Erreur parsing JSON pour %s: %s", model.__name__, e)
            return None


@service_factory("ia_avancee", tags={"ia", "avancee"})
def get_ia_avancee_service() -> IAAvanceeService:
    """Factory singleton IAAvanceeService."""
    return IAAvanceeService()
