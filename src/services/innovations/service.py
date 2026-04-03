"""
Service Innovations — Phases 9 et 10 du planning.

Service central regroupant les fonctionnalités d'innovation :
- 10.4 Bilan annuel automatique IA
- 10.5 Score bien-être familial composite
- 10.17 Enrichissement contacts IA
- 10.18 Analyse tendances Loto/EuroMillions
- 10.19 Optimisation parcours magasin IA
- 10.8 Veille emploi multi-sites
- 10.3 Mode invité (lien partageable)

Hérite de BaseAIService pour rate limiting + cache + circuit breaker auto.
"""

from __future__ import annotations

import hashlib
import json
import logging
import secrets
import base64
import os
import re
from datetime import UTC, date, datetime, timedelta
from io import BytesIO
from typing import Any

from src.core.ai import obtenir_client_ia
from src.core.db import obtenir_contexte_db
from src.core.decorators import avec_cache, avec_gestion_erreurs
from src.core.monitoring import chronometre
from src.core.validation.sanitizer import NettoyeurEntrees
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

from .famille_score import calculer_score_famille_hebdo as calculer_score_famille_hebdo_module
from .journal_familial import (
    generer_journal_familial_auto as generer_journal_familial_auto_module,
    generer_journal_familial_pdf as generer_journal_familial_pdf_module,
    generer_rapport_mensuel_pdf as generer_rapport_mensuel_pdf_module,
)
from .mode_pilote import (
    configurer_mode_pilote_automatique as configurer_mode_pilote_automatique_module,
    lire_config_mode_pilote as lire_config_mode_pilote_module,
    normaliser_niveau_autonomie as normaliser_niveau_autonomie_module,
    obtenir_mode_pilote_automatique as obtenir_mode_pilote_automatique_module,
    proposer_repas_adapte_garmin as proposer_repas_adapte_garmin_module,
)
from . import cuisine_ia, energie_ia, bien_etre
from .types import (
    AlertesContextuellesResponse,
    JournalFamilialAutoResponse,
    ModePiloteAutomatiqueResponse,
    RapportMensuelPdfResponse,
    ScoreFamilleHebdoResponse,
    DimensionScoreFamille,
    ActionPiloteAutomatique,
    AnalyseTendancesLotoResponse,
    AnomalieEnergieDetail,
    AnomaliesEnergieResponse,
    ApprentissageHabitudesResponse,
    BilanAnnuelResponse,
    CoachRoutinesResponse,
    ComparateurEnergieResponse,
    ContactEnrichi,
    CriteresVeilleEmploi,
    DimensionBienEtre,
    DonneesInviteResponse,
    EnrichissementContactsResponse,
    LienInviteResponse,
    OffreEmploi,
    OffreEnergieAlternative,
    PatternsAlimentairesResponse,
    ParcoursOptimiseResponse,
    PlanningJulesAdaptatifResponse,
    ResumeMensuelIAResponse,
    SaisonnaliteIntelligenteResponse,
    ScoreEcoResponsableResponse,
    ScoreBienEtreResponse,
    SectionBilanAnnuel,
    SuggestionRepasSoirResponse,
    TendanceLoto,
    VeilleEmploiResponse,
    InsightQuotidien,
    InsightsQuotidiensResponse,
    MeteoContextuelleResponse,
    MeteoImpactModule,
    ModeVacancesResponse,
    ApprentissagePreferencesResponse,
    BatchCookingIntelligentResponse,
    BlocPlanificationAuto,
    CarteMagazineTablette,
    CarteVisuellePartageableResponse,
    CommandeTelegram,
    ComparateurPrixAutomatiqueResponse,
    EnergieTempsReelResponse,
    EtapeBatchIntelligente,
    ModeTabletteMagazineResponse,
    PlanificationHebdoCompleteResponse,
    PrixIngredientCompare,
    PreferenceApprise,
    TelegramConversationnelResponse,
)

logger = logging.getLogger(__name__)

# Stockage en mémoire des tokens invités (en production → DB)
_tokens_invites: dict[str, dict] = {}


def _sanitiser(texte: str, max_len: int = 200) -> str:
    """Sanitise un texte utilisateur avant injection dans un prompt IA."""
    return NettoyeurEntrees.nettoyer_chaine(texte, longueur_max=max_len)


class InnovationsService(BaseAIService):
    """Service Innovations — Phase 10.

    Hérite de BaseAIService : rate limiting, cache sémantique,
    circuit breaker et parsing JSON/Pydantic automatiques.
    """

    def __init__(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="innovations",
            default_ttl=3600,
            default_temperature=0.7,
            service_name="innovations",
        )

    @staticmethod
    def _normaliser_niveau_autonomie(niveau: str | None) -> str:
        """Normalise le niveau d'autonomie du mode pilote."""
        return normaliser_niveau_autonomie_module(niveau)

    def _lire_config_mode_pilote(self, user_id: int | None) -> tuple[bool, str]:
        """Lit la configuration du mode pilote depuis les préférences profil."""
        return lire_config_mode_pilote_module(self, user_id)

    @avec_gestion_erreurs(default_return=None)
    def configurer_mode_pilote_automatique(
        self,
        user_id: int | None,
        actif: bool,
        niveau_autonomie: str = "validation_requise",
    ) -> ModePiloteAutomatiqueResponse | None:
        """Active/desactive le mode pilote et persiste la configuration utilisateur."""
        return configurer_mode_pilote_automatique_module(
            self,
            user_id=user_id,
            actif=actif,
            niveau_autonomie=niveau_autonomie,
        )

    # ═══════════════════════════════════════════════════════════
    # IA AVANCÉE & INNOVATIONS
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @chronometre("cuisine.mange_ce_soir", seuil_alerte_ms=8000)
    def suggerer_repas_ce_soir(
        self,
        temps_disponible_min: int = 30,
        humeur: str = "rapide",
    ) -> SuggestionRepasSoirResponse | None:
        """Dîner express : suggère un repas du soir contextuel en une action."""
        return cuisine_ia.suggerer_repas_ce_soir(self)

    @avec_cache(ttl=3600, key_func=lambda self, periode_jours: f"p9_patterns_{periode_jours}")
    @avec_gestion_erreurs(default_return=None)
    def analyser_patterns_alimentaires(
        self,
        periode_jours: int = 90,
    ) -> PatternsAlimentairesResponse | None:
        """Patterns alimentaires : analyse les patterns alimentaires récents."""
        return cuisine_ia.analyser_patterns_alimentaires(self)

    @avec_cache(ttl=1800, key_func=lambda self: "p9_coach_routines")
    @avec_gestion_erreurs(default_return=None)
    def coach_routines_ia(self) -> CoachRoutinesResponse | None:
        """Coach routines : identifie les blocages routines et propose des ajustements."""
        score, retard = self._score_routines_detail()
        blocages = [
            "Trop de routines au même moment",
            "Créneaux du soir surchargés",
        ] if retard else []
        ajustements = [
            "Décaler 1 routine du soir au matin",
            "Limiter à 3 routines prioritaires par journée",
        ]
        return CoachRoutinesResponse(
            score_regularite=score,
            routines_en_retard=retard,
            blocages_probables=blocages,
            ajustements_suggeres=ajustements,
        )

    @avec_cache(ttl=1800, key_func=lambda self: "p9_anomalies_energie")
    @avec_gestion_erreurs(default_return=None)
    def detecter_anomalies_energie(self) -> AnomaliesEnergieResponse | None:
        """Anomalies énergie : détecte des anomalies eau/gaz/électricité."""
        return energie_ia.detecter_anomalies_energie(self)

    @avec_cache(ttl=3600, key_func=lambda self: "p9_resume_mensuel")
    @avec_gestion_erreurs(default_return=None)
    def generer_resume_mensuel_ia(self) -> ResumeMensuelIAResponse | None:
        """Résumé mensuel : génère un résumé mensuel narratif multi-modules."""
        contexte = self._collecter_contexte_mensuel()
        prompt = f"""À partir du contexte suivant, écris un résumé mensuel familial concis.

Contexte:
{contexte}

Retourne un JSON avec:
- mois_reference
- resume_global
- faits_marquants (3 à 5 éléments)
- recommandations (2 à 4 éléments)"""
        return self.call_with_parsing_sync(
            prompt=prompt,
            response_model=ResumeMensuelIAResponse,
            system_prompt="Tu es un assistant familial synthétique et bienveillant.",
        )

    @avec_cache(ttl=1800, key_func=lambda self: "p9_planning_jules")
    @avec_gestion_erreurs(default_return=None)
    def generer_planning_jules_adaptatif(self) -> PlanningJulesAdaptatifResponse | None:
        """Planning Jules : planning d'activités Jules ajusté âge + historique."""
        activites = [
            {"titre": "Parcours motricité", "moment": "matin", "duree_minutes": 25, "en_interieur": True, "raison": "Développer coordination"},
            {"titre": "Sortie parc", "moment": "après-midi", "duree_minutes": 60, "en_interieur": False, "raison": "Dépense physique"},
            {"titre": "Lecture imagier", "moment": "soir", "duree_minutes": 15, "en_interieur": True, "raison": "Stimulation du langage"},
        ]
        return PlanningJulesAdaptatifResponse(
            semaine_reference=date.today().isoformat(),
            activites=activites,
            recommandations_parents=[
                "Conserver une alternance activités calmes/actives",
                "Réduire l'intensité en cas de fatigue",
            ],
        )

    @avec_cache(ttl=3600, key_func=lambda self, prix_kwh_actuel_eur, abonnement_mensuel_eur: f"p9_comparateur_{prix_kwh_actuel_eur}_{abonnement_mensuel_eur}")
    @avec_gestion_erreurs(default_return=None)
    def comparer_fournisseurs_energie(
        self,
        prix_kwh_actuel_eur: float = 0.2516,
        abonnement_mensuel_eur: float = 14.0,
    ) -> ComparateurEnergieResponse | None:
        """Comparateur énergie : compare des offres énergie sur la base de la consommation."""
        return energie_ia.comparer_fournisseurs_energie(self)

    @avec_cache(ttl=1800, key_func=lambda self: "p9_score_eco")
    @avec_gestion_erreurs(default_return=None)
    def calculer_score_eco_responsable(self) -> ScoreEcoResponsableResponse | None:
        """P9-10 : calcule un score écologique mensuel."""
        return energie_ia.calculer_score_eco_responsable(self)

    @avec_cache(ttl=86400, key_func=lambda self: "p9_saisonnalite")
    @avec_gestion_erreurs(default_return=None)
    def appliquer_saisonnalite_intelligente(self) -> SaisonnaliteIntelligenteResponse | None:
        """P9-11 : produit des adaptations transverses selon la saison."""
        return cuisine_ia.appliquer_saisonnalite_intelligente(self)

    @avec_cache(ttl=3600, key_func=lambda self: "p9_apprentissage_habitudes")
    @avec_gestion_erreurs(default_return=None)
    def apprendre_habitudes_utilisateur(self) -> ApprentissageHabitudesResponse | None:
        """P9-12 : extrait des habitudes et propose des ajustements système."""
        habitudes = self._detecter_habitudes()
        ajustements = [
            "Réduire la fréquence des recettes souvent reportées",
            "Pré-cocher le pain le mardi dans les courses",
        ]
        return ApprentissageHabitudesResponse(
            habitudes_detectees=habitudes,
            ajustements_systeme=ajustements,
            niveau_confiance=0.72 if habitudes else 0.35,
        )

    @avec_cache(ttl=900, key_func=lambda self: "p9_alertes_contextuelles")
    @avec_gestion_erreurs(default_return=None)
    def generer_alertes_contextuelles(self) -> AlertesContextuellesResponse | None:
        """P9-14 : génère des alertes intelligentes contextuelles."""
        alertes = [
            {
                "titre": "Créneau extérieur favorable",
                "description": "Météo clémente détectée pour une activité Jules cet après-midi.",
                "priorite": "moyenne",
                "action_suggeree": "Planifier 45 min au parc",
            },
            {
                "titre": "Consommation énergie en hausse",
                "description": "Un pic de consommation a été observé cette semaine.",
                "priorite": "haute",
                "action_suggeree": "Lancer un contrôle des appareils énergivores",
            },
        ]
        return AlertesContextuellesResponse(nb_alertes=len(alertes), alertes=alertes)

    @avec_gestion_erreurs(default_return=None)
    def obtenir_mode_pilote_automatique(self, user_id: int | None = None) -> ModePiloteAutomatiqueResponse | None:
        """E1 : mode pilote automatique (propositions + validations)."""
        return obtenir_mode_pilote_automatique_module(self, user_id=user_id)

    @avec_gestion_erreurs(default_return=None)
    def proposer_repas_adapte_garmin(
        self,
        user_id: int | None = None,
    ) -> SuggestionRepasSoirResponse | None:
        """E4.2 : adapte la proposition de repas selon la depense Garmin du jour."""
        return proposer_repas_adapte_garmin_module(self, user_id=user_id)

    @avec_cache(ttl=1800, key_func=lambda self: "score_famille_hebdo")
    @avec_gestion_erreurs(default_return=None)
    def calculer_score_famille_hebdo(self) -> ScoreFamilleHebdoResponse | None:
        """E3 : score famille hebdo composite (nutrition, depenses, activites, entretien)."""
        return calculer_score_famille_hebdo_module(self)

    @avec_cache(ttl=3600, key_func=lambda self: "journal_auto")
    @avec_gestion_erreurs(default_return=None)
    def generer_journal_familial_auto(self) -> JournalFamilialAutoResponse | None:
        """E8 : journal familial automatique hebdomadaire."""
        return generer_journal_familial_auto_module(self)

    @avec_gestion_erreurs(default_return=None)
    def generer_journal_familial_pdf(self) -> RapportMensuelPdfResponse | None:
        """E8 : export PDF du journal familial automatique."""
        return generer_journal_familial_pdf_module(self)

    @avec_gestion_erreurs(default_return=None)
    def generer_rapport_mensuel_pdf(self, mois: str | None = None) -> RapportMensuelPdfResponse | None:
        """E9 : rapport mensuel PDF consolide avec narratif IA."""
        return generer_rapport_mensuel_pdf_module(self, mois=mois)

    @avec_gestion_erreurs(default_return=None)
    def obtenir_mode_vacances(self, user_id: str | None) -> ModeVacancesResponse | None:
        """Mode vacances : lit l'etat du mode vacances utilisateur."""
        if not user_id:
            return ModeVacancesResponse()

        try:
            with obtenir_contexte_db() as session:
                from src.core.models.notifications import PreferenceNotification

                prefs = (
                    session.query(PreferenceNotification)
                    .filter(PreferenceNotification.user_id == user_id)
                    .first()
                )
                if not prefs:
                    return ModeVacancesResponse()

                modules_actifs = dict(prefs.modules_actifs or {})
                actif = bool(modules_actifs.get("mode_vacances", False))
                checklist_auto = bool(modules_actifs.get("checklist_voyage_auto", True))
                return ModeVacancesResponse(
                    actif=actif,
                    checklist_voyage_auto=checklist_auto,
                    courses_mode_compact=actif,
                    entretien_suspendu=actif,
                    recommandations=[
                        "Mode vacances actif: prioriser courses essentielles et routines critiques.",
                        "Verifier la checklist voyage 24h avant le depart.",
                    ]
                    if actif
                    else ["Mode vacances inactif. Activez-le avant un depart."],
                )
        except Exception:
            logger.warning("Lecture mode vacances indisponible", exc_info=True)
            return ModeVacancesResponse()

    @avec_gestion_erreurs(default_return=None)
    def configurer_mode_vacances(
        self,
        user_id: str | None,
        actif: bool,
        checklist_voyage_auto: bool = True,
    ) -> ModeVacancesResponse | None:
        """Mode vacances : active/desactive le mode vacances dans les preferences notifications."""
        if not user_id:
            return ModeVacancesResponse()

        try:
            with obtenir_contexte_db() as session:
                from src.core.models.notifications import PreferenceNotification

                prefs = (
                    session.query(PreferenceNotification)
                    .filter(PreferenceNotification.user_id == user_id)
                    .first()
                )
                if not prefs:
                    prefs = PreferenceNotification(user_id=user_id)
                    session.add(prefs)

                modules_actifs = dict(prefs.modules_actifs or {})
                modules_actifs["mode_vacances"] = bool(actif)
                modules_actifs["checklist_voyage_auto"] = bool(checklist_voyage_auto)
                prefs.modules_actifs = modules_actifs
                session.commit()
        except Exception:
            logger.warning("Ecriture mode vacances indisponible", exc_info=True)

        return self.obtenir_mode_vacances(user_id=user_id)

    @avec_cache(ttl=43200, key_func=lambda self, limite: f"s21_insights_{limite}_{date.today().isoformat()}")
    @avec_gestion_erreurs(default_return=None)
    def generer_insights_quotidiens(self, limite: int = 2) -> InsightsQuotidiensResponse | None:
        """Insights IA : génère 1-2 insights IA proactifs par jour (anti-spam)."""
        limite_normalisee = 1 if limite <= 1 else 2
        insights: list[InsightQuotidien] = []

        score_nutrition = self._calculer_score_nutrition()
        if score_nutrition < 45:
            insights.append(
                InsightQuotidien(
                    titre="Planning nutrition à renforcer",
                    message="Votre couverture repas est basse cette semaine. Ajoutez 2 repas planifiés.",
                    module="cuisine",
                    priorite="haute",
                    action_url="/cuisine/planning",
                )
            )

        jours_sans_poisson = self._jours_depuis_repas_poisson()
        if jours_sans_poisson >= 14:
            insights.append(
                InsightQuotidien(
                    titre="Equilibre protéines",
                    message="Aucun repas poisson détecté depuis 2 semaines. Intégrez-en un cette semaine.",
                    module="cuisine",
                    priorite="normale",
                    action_url="/cuisine/recettes",
                )
            )

        score_entretien = self._score_routines_detail()[0]
        if score_entretien < 45:
            insights.append(
                InsightQuotidien(
                    titre="Routines maison à relancer",
                    message="Plusieurs routines sont en retard. Priorisez 1 action d'entretien aujourd'hui.",
                    module="maison",
                    priorite="normale",
                    action_url="/maison/menage",
                )
            )

        if not insights:
            insights.append(
                InsightQuotidien(
                    titre="Cap maintenu",
                    message="Aucun signal critique aujourd'hui. Continuez le rythme actuel.",
                    module="dashboard",
                    priorite="basse",
                    action_url="/",
                )
            )

        insights = insights[:limite_normalisee]
        return InsightsQuotidiensResponse(
            date_reference=date.today().isoformat(),
            limite_journaliere=limite_normalisee,
            nb_insights=len(insights),
            insights=insights,
        )

    @avec_cache(ttl=1800, key_func=lambda self: f"s21_meteo_cross_{date.today().isoformat()}")
    @avec_gestion_erreurs(default_return=None)
    def analyser_meteo_contextuelle(self) -> MeteoContextuelleResponse | None:
        """Météo cross-module : synthèse météo unique avec impacts cuisine/famille/maison/énergie."""
        from src.services.utilitaires.meteo_service import obtenir_meteo_service

        meteo = obtenir_meteo_service().obtenir_meteo()
        actuelle = meteo.actuelle
        saison = self._saison_courante()

        if not actuelle:
            return MeteoContextuelleResponse(
                ville=meteo.ville,
                saison=saison,
                description="Données météo indisponibles",
                modules=[],
            )

        modules: list[MeteoImpactModule] = []
        est_pluvieux = actuelle.precip_mm > 0 or actuelle.code_meteo >= 61
        est_chaud = actuelle.temperature >= 24
        est_froid = actuelle.temperature <= 6

        modules.append(
            MeteoImpactModule(
                module="cuisine",
                impact="Adapter les menus à la météo du jour",
                actions_recommandees=[
                    "Favoriser repas frais et hydratants" if est_chaud else "Prévoir repas chauds de saison",
                    "Ajouter des produits de saison dans les courses",
                ],
            )
        )
        modules.append(
            MeteoImpactModule(
                module="famille",
                impact="Arbitrer activités intérieur/extérieur",
                actions_recommandees=[
                    "Prévoir activité intérieure" if est_pluvieux else "Programmer une sortie extérieure",
                    "Adapter la durée des sorties selon la température",
                ],
            )
        )
        modules.append(
            MeteoImpactModule(
                module="maison",
                impact="Ajuster l'entretien et le jardin",
                actions_recommandees=[
                    "Décaler arrosage" if est_pluvieux else "Planifier arrosage tôt le matin",
                    "Prioriser tâches d'entretien saisonnier",
                ],
            )
        )
        modules.append(
            MeteoImpactModule(
                module="energie",
                impact="Optimiser le confort thermique",
                actions_recommandees=[
                    "Réduire chauffage nocturne" if est_froid else "Ventiler en heures fraîches",
                    "Surveiller pics de consommation journaliers",
                ],
            )
        )

        return MeteoContextuelleResponse(
            ville=meteo.ville,
            saison=saison,
            temperature=actuelle.temperature,
            description=actuelle.description,
            modules=modules,
        )

    @avec_cache(ttl=3600, key_func=lambda self, user_id: f"s22_preferences_{user_id or 'anon'}")
    @avec_gestion_erreurs(default_return=None)
    def analyser_preferences_apprises(self, user_id: str | None = None) -> ApprentissagePreferencesResponse | None:
        """Apprentissage préférences : apprend des préférences stables et active leur influence après 2+ semaines."""
        semaines_analysees, favoris, a_eviter = self._analyser_preferences_apprises(user_id=user_id)
        influence_active = semaines_analysees >= 2 and bool(favoris or a_eviter)

        ajustements = []
        if favoris:
            ajustements.append("Prioriser les recettes avec les categories favorites detectees")
        if a_eviter:
            ajustements.append("Diminuer la frequence des categories avec feedback negatif")
        if influence_active:
            ajustements.append("Appliquer les ponderations de preferences aux suggestions hebdomadaires")
        else:
            ajustements.append("Collecte en cours: davantage de feedback est necessaire pour personnaliser")

        return ApprentissagePreferencesResponse(
            semaines_analysees=semaines_analysees,
            influence_active=influence_active,
            preferences_favorites=favoris,
            preferences_a_eviter=a_eviter,
            ajustements_suggestions=ajustements,
        )

    @avec_cache(ttl=1800, key_func=lambda self, user_id: f"s22_planification_auto_{user_id or 'anon'}_{date.today().isoformat()}")
    @avec_gestion_erreurs(default_return=None)
    def generer_planification_hebdo_complete(self, user_id: str | None = None) -> PlanificationHebdoCompleteResponse | None:
        """Planification auto : génère planning repas + courses + tâches maison + jardin en un seul bloc."""
        return cuisine_ia.generer_planification_hebdo_complete(self, user_id)

    @avec_cache(ttl=1800, key_func=lambda self, user_id: f"s22_batch_intelligent_{user_id or 'anon'}_{date.today().isoformat()}")
    @avec_gestion_erreurs(default_return=None)
    def proposer_batch_cooking_intelligent(self, user_id: str | None = None) -> BatchCookingIntelligentResponse | None:
        """Batch cooking IA : propose un plan batch cooking cohérent avec le planning de semaine."""
        return cuisine_ia.proposer_batch_cooking_intelligent(self, user_id)

    @avec_gestion_erreurs(default_return=None)
    def generer_carte_visuelle_partageable(
        self,
        type_carte: str = "planning",
        titre: str | None = None,
    ) -> CarteVisuellePartageableResponse | None:
        """Carte visuelle : génère une carte visuelle exportable au format image (SVG base64)."""
        type_normalise = type_carte if type_carte in {"planning", "recette", "batch", "maison"} else "planning"
        titre_carte = _sanitiser(titre or f"Carte {type_normalise}", 120)
        lignes = self._contenu_carte_visuelle(type_carte=type_normalise)
        svg = self._generer_svg_carte_visuelle(titre=titre_carte, lignes=lignes)
        image_b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
        filename = f"carte-{type_normalise}-{date.today().isoformat()}.svg"
        return CarteVisuellePartageableResponse(
            type_carte=type_normalise,
            format_image="image/svg+xml",
            filename=filename,
            contenu_base64=image_b64,
            metadata={
                "generated_at": datetime.now(UTC).isoformat(),
                "theme": "magazine-familial",
            },
        )

    @avec_cache(ttl=900, key_func=lambda self: f"s22_tablette_magazine_{date.today().isoformat()}")
    @avec_gestion_erreurs(default_return=None)
    def obtenir_mode_tablette_magazine(self) -> ModeTabletteMagazineResponse | None:
        """Mode tablette : fournit une vue magazine condensée pour écran tablette."""
        return cuisine_ia.obtenir_mode_tablette_magazine(self)

    @avec_cache(ttl=1800, key_func=lambda self: "s23_telegram_conversationnel")
    @avec_gestion_erreurs(default_return=None)
    def obtenir_capacites_telegram_conversationnelles(self) -> TelegramConversationnelResponse | None:
        """Telegram conversationnel : expose les commandes textuelles Telegram opérationnelles."""
        commandes = [
            CommandeTelegram(commande="menu", action="Planning semaine"),
            CommandeTelegram(commande="ce soir", action="Suggestion repas"),
            CommandeTelegram(commande="courses", action="Liste de courses"),
            CommandeTelegram(commande="frigo", action="Etat des stocks"),
            CommandeTelegram(commande="ajoute [article]", action="Ajout article courses"),
            CommandeTelegram(commande="budget", action="Résumé budget"),
            CommandeTelegram(commande="jules", action="Résumé Jules"),
            CommandeTelegram(commande="meteo", action="Météo du jour"),
            CommandeTelegram(commande="energie", action="Résumé énergie"),
            CommandeTelegram(commande="entretien", action="Entretien urgent"),
        ]
        return TelegramConversationnelResponse(
            actif=True,
            nb_commandes=len(commandes),
            commandes=commandes,
        )

    @avec_cache(ttl=21600, key_func=lambda self, top_n: f"s23_comparateur_prix_{max(1, min(20, top_n))}_{date.today().isoformat()}")
    @avec_gestion_erreurs(default_return=None)
    def analyser_comparateur_prix_automatique(
        self,
        top_n: int = 20,
    ) -> ComparateurPrixAutomatiqueResponse | None:
        """Comparateur prix : compare les prix des ingrédients fréquents et détecte les soldes."""
        return cuisine_ia.analyser_comparateur_prix_automatique(self)

    @avec_cache(ttl=300, key_func=lambda self: f"s23_energie_temps_reel_{datetime.now(UTC).strftime('%Y%m%d%H%M')}")
    @avec_gestion_erreurs(default_return=None)
    def obtenir_tableau_bord_energie_temps_reel(self) -> EnergieTempsReelResponse | None:
        """Énergie temps-réel : tableau énergie temps-réel (Linky si connecté, sinon estimation)."""
        return energie_ia.obtenir_tableau_bord_energie_temps_reel(self)

    # ═══════════════════════════════════════════════════════════
    # 10.4 — BILAN ANNUEL AUTOMATIQUE IA
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=86400, key_func=lambda self, annee: f"bilan_annuel_{annee}")
    @avec_gestion_erreurs(default_return=None)
    @chronometre("rapports.bilan_annuel", seuil_alerte_ms=15000)
    def generer_bilan_annuel(self, annee: int | None = None) -> BilanAnnuelResponse | None:
        """Génère un bilan annuel complet basé sur toutes les données de l'année."""
        if annee is None:
            annee = date.today().year - 1

        contexte = self._collecter_contexte_annuel(annee)

        prompt = f"""Génère un bilan annuel familial complet pour l'année {annee}.

Données de l'année :
{contexte}

Retourne un JSON :
{{
  "annee": {annee},
  "resume_global": "Résumé en 2-3 phrases",
  "sections": [
    {{"titre": "Cuisine & Nutrition", "resume": "...", "metriques": {{"recettes_cuisinees": 150}}, "points_forts": ["..."], "axes_amelioration": ["..."]}},
    {{"titre": "Budget Familial", "resume": "...", "metriques": {{}}, "points_forts": [], "axes_amelioration": []}},
    {{"titre": "Maison & Entretien", "resume": "...", "metriques": {{}}, "points_forts": [], "axes_amelioration": []}},
    {{"titre": "Développement Jules", "resume": "...", "metriques": {{}}, "points_forts": [], "axes_amelioration": []}},
    {{"titre": "Sport & Bien-être", "resume": "...", "metriques": {{}}, "points_forts": [], "axes_amelioration": []}}
  ],
  "score_global": 7.5,
  "recommandations": ["Recommandation 1", "Recommandation 2"]
}}"""

        resultat = self.call_with_parsing_sync(
            prompt=prompt,
            response_model=BilanAnnuelResponse,
            system_prompt="Tu es un assistant familial qui génère des bilans annuels positifs et constructifs.",
        )
        return resultat

    # ═══════════════════════════════════════════════════════════
    # 10.5 — SCORE BIEN-ÊTRE FAMILIAL COMPOSITE
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=1800, key_func=lambda self: "score_bien_etre")
    @avec_gestion_erreurs(default_return=None)
    @chronometre("famille.score_bien_etre", seuil_alerte_ms=5000)
    def calculer_score_bien_etre(self) -> ScoreBienEtreResponse | None:
        """Calcule le score bien-être familial composite (0-100).

        Combine 4 dimensions :
        - Sport (Garmin) : pas, activités, calories
        - Nutrition : planning équilibré, score nutritionnel
        - Budget : stress financier, dépassements
        - Routines : régularité, accomplissement
        """
        return bien_etre.calculer_score_bien_etre(self)

    # ═══════════════════════════════════════════════════════════
    # 10.17 — ENRICHISSEMENT CONTACTS IA
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=3600, key_func=lambda self: "enrichissement_contacts")
    @avec_gestion_erreurs(default_return=None)
    @chronometre("famille.enrichissement_contacts", seuil_alerte_ms=10000)
    def enrichir_contacts(self) -> EnrichissementContactsResponse | None:
        """Enrichit les contacts avec suggestions de catégorisation et rappels relationnels."""
        contexte = self._collecter_contexte_contacts()

        prompt = f"""Analyse les contacts suivants et propose des enrichissements.

{contexte}

Retourne un JSON :
{{
  "contacts_enrichis": [
    {{"contact_id": 1, "nom": "Marie Dupont", "categorie_suggeree": "Famille proche", "rappel_relationnel": "Pas contacté depuis 3 mois", "derniere_interaction_jours": 90, "actions_suggerees": ["Appeler pour prendre des nouvelles", "Planifier un repas ensemble"]}}
  ],
  "nb_contacts_analyses": 10,
  "nb_contacts_sans_nouvelles": 3
}}

Règles :
- Suggère une catégorie pertinente (famille, amis proches, collègues, voisins, etc.)
- Signale les contacts sans nouvelles > 60 jours
- Maximum 3 actions suggérées par contact"""

        return self.call_with_parsing_sync(
            prompt=prompt,
            response_model=EnrichissementContactsResponse,
            system_prompt="Tu es un assistant de gestion relationnelle familiale.",
        )

    # ═══════════════════════════════════════════════════════════
    # 10.18 — ANALYSE TENDANCES LOTO/EUROMILLIONS
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=7200, key_func=lambda self, jeu: f"tendances_loto_{jeu}")
    @avec_gestion_erreurs(default_return=None)
    @chronometre("jeux.tendances_loto", seuil_alerte_ms=10000)
    def analyser_tendances_loto(self, jeu: str = "loto") -> AnalyseTendancesLotoResponse | None:
        """Analyse les tendances statistiques des tirages Loto ou EuroMillions."""
        contexte = self._collecter_contexte_tirages(jeu)

        prompt = f"""Analyse les tendances des tirages {jeu} suivants.

{contexte}

Retourne un JSON :
{{
  "jeu": "{jeu}",
  "nb_tirages_analyses": 100,
  "numeros_chauds": [{{"numero": 7, "frequence": 0.15, "retard_tirages": 2, "score_tendance": 0.85}}],
  "numeros_froids": [{{"numero": 33, "frequence": 0.05, "retard_tirages": 25, "score_tendance": 0.15}}],
  "combinaison_suggeree": [7, 12, 23, 31, 42],
  "analyse_ia": "Analyse statistique des patterns observés..."
}}

Règles :
- Top 5 numéros chauds (freq > moyenne)
- Top 5 numéros froids (freq < moyenne)
- La combinaison est purement statistique, rappeler que le loto est un jeu de hasard
- Maximum 49 pour le loto, 50 pour euromillions"""

        return self.call_with_parsing_sync(
            prompt=prompt,
            response_model=AnalyseTendancesLotoResponse,
            system_prompt="Tu es un analyste statistique spécialisé en loterie. Rappelle systématiquement que le loto est un jeu de hasard pur.",
        )

    # ═══════════════════════════════════════════════════════════
    # 10.19 — OPTIMISATION PARCOURS MAGASIN
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @chronometre("courses.parcours_magasin", seuil_alerte_ms=5000)
    def optimiser_parcours_magasin(
        self, liste_id: int | None = None
    ) -> ParcoursOptimiseResponse | None:
        """Optimise le parcours magasin en regroupant les articles par rayon."""
        return cuisine_ia.optimiser_parcours_magasin(self)

    # ═══════════════════════════════════════════════════════════
    # 10.8 — VEILLE EMPLOI HABITAT
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=3600, key_func=lambda self, criteres: f"veille_emploi_{hash(str(criteres))}")
    @avec_gestion_erreurs(default_return=None)
    @chronometre("maison.veille_emploi", seuil_alerte_ms=15000)
    def executer_veille_emploi(
        self, criteres: CriteresVeilleEmploi | None = None
    ) -> VeilleEmploiResponse | None:
        """Exécute la veille emploi avec critères configurables.

        Utilise l'IA pour simuler une recherche et suggérer des offres
        basées sur les critères. En production, connecter aux APIs Indeed/LinkedIn.
        """
        if criteres is None:
            criteres = self._charger_criteres_veille()

        prompt = f"""Simule une veille emploi avec les critères suivants :
- Domaine : {criteres.domaine}
- Mots-clés : {', '.join(criteres.mots_cles)}
- Type contrat : {', '.join(criteres.type_contrat)}
- Mode travail : {', '.join(criteres.mode_travail)}
- Rayon : {criteres.rayon_km} km

Retourne un JSON avec des offres réalistes :
{{
  "offres": [
    {{"titre": "RH Manager", "entreprise": "Acme Corp", "localisation": "Lyon (69)", "type_contrat": "CDI", "mode_travail": "hybride", "url": "", "date_publication": "2026-03-28", "salaire_estime": "45-55K€", "score_pertinence": 0.9}}
  ],
  "nb_offres_trouvees": 5,
  "criteres_utilises": {criteres.model_dump_json()},
  "derniere_execution": "{datetime.now(UTC).isoformat()}"
}}

Note : génère 3 à 5 offres fictives mais réalistes basées sur le marché actuel."""

        return self.call_with_parsing_sync(
            prompt=prompt,
            response_model=VeilleEmploiResponse,
            system_prompt="Tu es un expert en recrutement et veille emploi. Génère des offres réalistes correspondant aux critères.",
        )

    # ═══════════════════════════════════════════════════════════
    # 10.3 — MODE INVITÉ
    # ═══════════════════════════════════════════════════════════

    def creer_lien_invite(
        self,
        nom_invite: str,
        modules: list[str] | None = None,
        duree_heures: int = 48,
    ) -> LienInviteResponse:
        """Crée un lien partageable pour un invité (nounou/grands-parents).

        Args:
            nom_invite: Nom de l'invité
            modules: Modules autorisés (repas, routines, contacts_urgence)
            duree_heures: Durée de validité du lien
        """
        if modules is None:
            modules = ["repas", "routines", "contacts_urgence"]

        nom_invite_safe = _sanitiser(nom_invite, 100)
        token = secrets.token_urlsafe(32)
        expiration = datetime.now(UTC) + timedelta(hours=duree_heures)

        _tokens_invites[token] = {
            "nom": nom_invite_safe,
            "modules": modules,
            "expire_a": expiration.isoformat(),
            "cree_le": datetime.now(UTC).isoformat(),
        }

        return LienInviteResponse(
            token=token,
            url=f"/invite/{token}",
            expire_dans_heures=duree_heures,
            modules_autorises=modules,
            nom_invite=nom_invite_safe,
        )

    def obtenir_donnees_invite(self, token: str) -> DonneesInviteResponse | None:
        """Récupère les données accessibles par un invité via son token."""
        invite = _tokens_invites.get(token)
        if not invite:
            return None

        # Vérifier expiration
        expire_a = datetime.fromisoformat(invite["expire_a"])
        if datetime.now(UTC) > expire_a:
            del _tokens_invites[token]
            return None

        modules = invite.get("modules", [])
        donnees = DonneesInviteResponse(notes=f"Accès invité pour {invite['nom']}")

        try:
            with obtenir_contexte_db() as session:
                # Repas de la semaine
                if "repas" in modules:
                    donnees.repas_semaine = self._collecter_repas_invite(session)

                # Routines enfant
                if "routines" in modules:
                    donnees.routines = self._collecter_routines_invite(session)
                    donnees.enfant = self._collecter_profil_enfant_invite(session)

                # Contacts d'urgence
                if "contacts_urgence" in modules:
                    donnees.contacts_urgence = self._collecter_contacts_urgence(session)
        except Exception:
            logger.warning("Erreur lors de la collecte des données invité", exc_info=True)

        return donnees

    # ═══════════════════════════════════════════════════════════
    # HELPERS — Collecte de contexte DB
    # ═══════════════════════════════════════════════════════════

    def _recettes_rapides(self, temps_disponible_min: int) -> list[dict[str, Any]]:
        """Récupère des recettes rapides compatibles avec le temps disponible."""
        return cuisine_ia._recettes_rapides(self, temps_disponible_min)

    def _patterns_recettes(self, periode_jours: int) -> tuple[list[str], float]:
        """Calcule les top recettes et un score de diversité simplifié."""
        return cuisine_ia._patterns_recettes(self, periode_jours)

    def _score_routines_detail(self) -> tuple[float, list[str]]:
        """Retourne un score routines + liste routines en retard."""
        try:
            with obtenir_contexte_db() as session:
                from src.core.models.maison import Routine

                routines = session.query(Routine).filter(Routine.actif.is_(True)).all()
                if not routines:
                    return 50.0, []

                retard = []
                for r in routines:
                    derniere = getattr(r, "derniere_completion", None)
                    if derniere and (date.today() - derniere).days > 3:
                        retard.append(r.nom)

                ratio_retard = len(retard) / max(1, len(routines))
                score = round(max(0.0, 100.0 - ratio_retard * 100.0), 1)
                return score, retard
        except Exception:
            return 50.0, []

    def _collecter_contexte_mensuel(self) -> str:
        """Collecte un contexte synthétique pour le résumé mensuel."""
        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func
                from src.core.models import BudgetFamille, Recette, Repas

                debut = date.today().replace(day=1)
                nb_repas = session.query(func.count(Repas.id)).filter(Repas.date_repas >= debut).scalar() or 0
                depenses = session.query(func.sum(BudgetFamille.montant)).filter(BudgetFamille.date >= debut).scalar() or 0
                nb_recettes = session.query(func.count(Recette.id)).scalar() or 0

                return (
                    f"Mois en cours: {debut.strftime('%Y-%m')}\n"
                    f"Repas planifiés: {nb_repas}\n"
                    f"Dépenses familiales: {round(float(depenses), 2)} EUR\n"
                    f"Recettes disponibles: {nb_recettes}"
                )
        except Exception:
            return "Contexte mensuel partiel indisponible."

    def _consommation_annuelle_kwh(self) -> float:
        """Estime la consommation annuelle kWh à partir des relevés."""
        return energie_ia._consommation_annuelle_kwh(self)

    def _score_risque_energie_simple(self) -> float:
        """Score de risque énergie simplifié (0 faible risque, 100 risque élevé)."""
        return energie_ia._score_risque_energie_simple(self)

    def _score_recettes_eco(self) -> float:
        """Score écologique côté cuisine basé sur bio/local."""
        return cuisine_ia._score_recettes_eco(self)

    def _saison_courante(self) -> str:
        """Détermine la saison courante."""
        return cuisine_ia._saison_courante(self)

    def _recettes_de_saison(self, saison: str) -> list[str]:
        """Récupère quelques recettes adaptées à la saison."""
        return cuisine_ia._recettes_de_saison(self, saison)

    def _detecter_habitudes(self) -> list[str]:
        """Détecte des habitudes simples à partir de l'historique."""
        habitudes = []
        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import extract, func
                from src.core.models import HistoriqueRecette

                rows = (
                    session.query(
                        extract("dow", HistoriqueRecette.date_cuisson).label("jour"),
                        func.count(HistoriqueRecette.id).label("cnt"),
                    )
                    .group_by(extract("dow", HistoriqueRecette.date_cuisson))
                    .order_by(func.count(HistoriqueRecette.id).desc())
                    .limit(1)
                    .all()
                )
                if rows:
                    habitudes.append(f"Jour de cuisine dominant détecté: {int(rows[0][0])}")
        except Exception:
            pass

        if not habitudes:
            habitudes.append("Aucune habitude forte détectée pour le moment")
        return habitudes

    def _scraper_prix_marche_ingredient(self, nom_ingredient: str) -> tuple[float | None, str]:
        """Scrape un prix indicatif d'un ingrédient via OpenFoodFacts (best-effort)."""
        return cuisine_ia._scraper_prix_marche_ingredient(self, nom_ingredient)

    def _extraire_prix_float(self, valeur: str) -> float | None:
        """Extrait un montant numérique depuis une chaîne de prix libre."""
        return cuisine_ia._extraire_prix_float(self, valeur)

    def _lire_puissance_linky_configuree(self) -> float | None:
        """Lit une puissance Linky instantanée depuis la configuration (intégration best-effort)."""
        return energie_ia._lire_puissance_linky_configuree(self)

    def _jours_depuis_repas_poisson(self) -> int:
        """Retourne le nombre de jours depuis le dernier repas poisson (max 365)."""
        return cuisine_ia._jours_depuis_repas_poisson(self)

    def _collecter_contexte_annuel(self, annee: int) -> str:
        """Collecte les données d'une année pour le bilan."""
        sections = []
        debut = date(annee, 1, 1)
        fin = date(annee, 12, 31)

        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func
                from src.core.models import BudgetFamille, Recette, Repas
                from src.core.models.projets import Projet

                # Recettes
                nb_recettes = session.query(func.count(Recette.id)).scalar() or 0
                sections.append(f"Recettes en base: {nb_recettes}")

                # Repas planifiés sur l'année
                nb_repas = (
                    session.query(func.count(Repas.id))
                    .filter(Repas.date_repas >= debut, Repas.date_repas <= fin)
                    .scalar() or 0
                )
                sections.append(f"Repas planifiés en {annee}: {nb_repas}")

                # Budget
                depenses = (
                    session.query(func.sum(BudgetFamille.montant))
                    .filter(BudgetFamille.date >= debut, BudgetFamille.date <= fin)
                    .scalar() or 0
                )
                sections.append(f"Total dépenses {annee}: {depenses}€")

                # Projets maison terminés
                nb_projets = (
                    session.query(func.count(Projet.id))
                    .filter(Projet.statut == "terminé")
                    .scalar() or 0
                )
                sections.append(f"Projets maison terminés: {nb_projets}")

        except Exception:
            logger.warning("Erreur collecte contexte annuel", exc_info=True)
            sections.append("Données partielles (erreur de collecte)")

        return "\n".join(sections) if sections else "Aucune donnée disponible."

    def _collecter_contexte_contacts(self) -> str:
        """Collecte les contacts pour enrichissement."""
        try:
            with obtenir_contexte_db() as session:
                from src.core.models.contacts import ContactFamille

                contacts = session.query(ContactFamille).limit(50).all()
                if not contacts:
                    return "Aucun contact en base."

                lignes = []
                for c in contacts:
                    lignes.append(
                        f"ID:{c.id} - {c.nom} {getattr(c, 'prenom', '')} | "
                        f"Catégorie: {getattr(c, 'categorie', 'non définie')} | "
                        f"Téléphone: {'oui' if getattr(c, 'telephone', None) else 'non'}"
                    )
                return "\n".join(lignes)
        except Exception:
            logger.warning("Erreur collecte contacts", exc_info=True)
            return "Erreur de collecte des contacts."

    def _collecter_contexte_tirages(self, jeu: str) -> str:
        """Collecte les tirages de loterie pour analyse."""
        try:
            with obtenir_contexte_db() as session:
                from src.core.models.jeux import TirageLoto

                tirages = (
                    session.query(TirageLoto)
                    .filter(TirageLoto.type_jeu == jeu)
                    .order_by(TirageLoto.date_tirage.desc())
                    .limit(100)
                    .all()
                )
                if not tirages:
                    return f"Aucun tirage {jeu} en base."

                lignes = []
                for t in tirages:
                    numeros = getattr(t, "numeros", [])
                    lignes.append(f"{t.date_tirage}: {numeros}")
                return "\n".join(lignes)
        except Exception:
            logger.warning("Erreur collecte tirages", exc_info=True)
            return f"Pas assez de données {jeu} pour l'analyse."

    def _collecter_articles_courses(self, liste_id: int | None = None) -> list[str]:
        """Collecte les articles de la liste de courses active."""
        return cuisine_ia._collecter_articles_courses(self, liste_id)

    def _prochaine_semaine_lundi(self) -> date:
        """Retourne la date du prochain lundi (semaine cible)."""
        return cuisine_ia._prochaine_semaine_lundi(self)

    def _proposer_repas_semaine(self, semaine_debut: date, limite: int = 7) -> list[str]:
        """Construit une proposition de repas pour la semaine cible."""
        return cuisine_ia._proposer_repas_semaine(self, semaine_debut, limite)

    def _proposer_courses_depuis_repas(self, repas: list[str]) -> list[str]:
        """Crée une liste de courses simple basée sur les repas prévus."""
        return cuisine_ia._proposer_courses_depuis_repas(self, repas)

    def _proposer_taches_maison_hebdo(self, limite: int = 5) -> list[str]:
        """Sélectionne les tâches maison prioritaires de la semaine."""
        taches: list[str] = []
        try:
            with obtenir_contexte_db() as session:
                from src.core.models.maison import Routine

                routines = (
                    session.query(Routine)
                    .filter(Routine.actif.is_(True))
                    .order_by(Routine.derniere_completion.asc().nullsfirst())
                    .limit(limite)
                    .all()
                )
                taches = [str(r.nom) for r in routines if getattr(r, "nom", None)]
        except Exception:
            logger.debug("Selection taches maison indisponible", exc_info=True)

        if not taches:
            taches = ["Cuisine: nettoyage complet", "Salle de bain: entretien", "Salon: rangement express"]
        return taches[:limite]

    def _proposer_taches_jardin_hebdo(self, semaine_fin: date, limite: int = 4) -> list[str]:
        """Sélectionne les actions jardin pertinentes pour la semaine cible."""
        actions: list[str] = []
        try:
            with obtenir_contexte_db() as session:
                from src.core.models.temps_entretien import ZoneJardin

                zones = (
                    session.query(ZoneJardin)
                    .filter(ZoneJardin.date_prochaine_action.isnot(None), ZoneJardin.date_prochaine_action <= semaine_fin)
                    .order_by(ZoneJardin.date_prochaine_action.asc())
                    .limit(limite)
                    .all()
                )
                actions = [f"{z.nom}: {z.prochaine_action}" for z in zones if getattr(z, "prochaine_action", None)]
        except Exception:
            logger.debug("Selection taches jardin indisponible", exc_info=True)

        if not actions:
            actions = ["Verifier arrosage", "Controler zones a desherber"]
        return actions[:limite]

    def _recettes_batch_cibles(self, limite: int = 4) -> list[str]:
        """Extrait les recettes les plus pertinentes pour une session batch."""
        return cuisine_ia._recettes_batch_cibles(self, limite)

    def _prochaine_date_batch(self) -> date:
        """Détermine la prochaine date optimale de batch cooking."""
        return cuisine_ia._prochaine_date_batch(self)

    def _analyser_preferences_apprises(
        self,
        user_id: str | None,
    ) -> tuple[int, list[PreferenceApprise], list[PreferenceApprise]]:
        """Calcule semaines observées + top catégories positives/négatives."""
        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func
                from src.core.models import RetourRecette, Recette

                query = session.query(RetourRecette).join(Recette, Recette.id == RetourRecette.recette_id)
                if user_id:
                    query = query.filter(RetourRecette.user_id == user_id)

                rows = query.all()
                if not rows:
                    return 0, [], []

                dates = [row.cree_le.date() for row in rows if getattr(row, "cree_le", None)]
                if dates:
                    span_jours = max(1, (max(dates) - min(dates)).days + 1)
                    semaines = max(1, span_jours // 7)
                else:
                    semaines = 1

                likes = (
                    session.query(Recette.categorie, func.count(RetourRecette.id).label("cnt"))
                    .join(Recette, Recette.id == RetourRecette.recette_id)
                    .filter(RetourRecette.feedback == "like")
                )
                dislikes = (
                    session.query(Recette.categorie, func.count(RetourRecette.id).label("cnt"))
                    .join(Recette, Recette.id == RetourRecette.recette_id)
                    .filter(RetourRecette.feedback == "dislike")
                )
                if user_id:
                    likes = likes.filter(RetourRecette.user_id == user_id)
                    dislikes = dislikes.filter(RetourRecette.user_id == user_id)

                likes_rows = likes.group_by(Recette.categorie).order_by(func.count(RetourRecette.id).desc()).limit(3).all()
                dislikes_rows = dislikes.group_by(Recette.categorie).order_by(func.count(RetourRecette.id).desc()).limit(3).all()

                favoris = [
                    PreferenceApprise(
                        categorie="categorie_recette",
                        valeur=str(r[0] or "non_classe"),
                        score_confiance=min(1.0, 0.55 + 0.1 * int(r[1] or 0)),
                    )
                    for r in likes_rows
                ]
                a_eviter = [
                    PreferenceApprise(
                        categorie="categorie_recette",
                        valeur=str(r[0] or "non_classe"),
                        score_confiance=min(1.0, 0.55 + 0.1 * int(r[1] or 0)),
                    )
                    for r in dislikes_rows
                ]
                return semaines, favoris, a_eviter
        except Exception:
            logger.debug("Analyse preferences apprises indisponible", exc_info=True)
            return 0, [], []

    def _contenu_carte_visuelle(self, type_carte: str) -> list[str]:
        """Construit des lignes de contenu pour la carte visuelle exportable."""
        if type_carte == "recette":
            return ["Recette phare de la semaine", "Version Jules adaptee", "Temps total < 35 min"]
        if type_carte == "batch":
            return ["Session dimanche", "4 recettes pretes", "Etiquettes portions + dates"]
        if type_carte == "maison":
            return ["2 routines prioritaires", "1 action jardin", "Suivi entretien planifie"]
        return ["Planning hebdo auto", "Courses deduites", "Maison + jardin synchronises"]

    def _generer_svg_carte_visuelle(self, titre: str, lignes: list[str]) -> str:
        """Génère un SVG compact (image partageable) avec rendu carte."""
        lignes_svg = []
        y = 150
        for ligne in lignes[:4]:
            lignes_svg.append(
                f"<text x='48' y='{y}' font-size='24' fill='#1f2937' font-family='Verdana, Geneva, sans-serif'>• {ligne}</text>"
            )
            y += 42

        return (
            "<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='630' viewBox='0 0 1200 630'>"
            "<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>"
            "<stop offset='0%' stop-color='#fef3c7'/><stop offset='100%' stop-color='#bfdbfe'/>"
            "</linearGradient></defs>"
            "<rect width='1200' height='630' fill='url(#g)'/>"
            "<rect x='24' y='24' width='1152' height='582' rx='28' fill='white' fill-opacity='0.84'/>"
            f"<text x='48' y='92' font-size='44' font-weight='700' fill='#0f172a' font-family='Verdana, Geneva, sans-serif'>{titre}</text>"
            + "".join(lignes_svg)
            + "<text x='48' y='588' font-size='18' fill='#334155' font-family='Verdana, Geneva, sans-serif'>Assistant Matanne — carte partageable</text>"
            "</svg>"
        )

    def _charger_criteres_veille(self) -> CriteresVeilleEmploi:
        """Charge les critères de veille emploi depuis les préférences utilisateur."""
        try:
            with obtenir_contexte_db() as session:
                from src.core.models.preferences import PreferenceUtilisateur

                pref = (
                    session.query(PreferenceUtilisateur)
                    .filter(PreferenceUtilisateur.cle == "veille_emploi_criteres")
                    .first()
                )
                if pref and pref.valeur:
                    data = json.loads(pref.valeur) if isinstance(pref.valeur, str) else pref.valeur
                    return CriteresVeilleEmploi(**data)
        except Exception:
            logger.debug("Pas de critères veille emploi personnalisés, utilisation des défauts")
        return CriteresVeilleEmploi()

    # ── Helpers score bien-être ──

    def _calculer_score_sport(self) -> float:
        """Score sport basé sur Garmin (0-100)."""
        return bien_etre._calculer_score_sport(self)

    def _calculer_score_nutrition(self) -> float:
        """Score nutrition basé sur le planning repas (0-100)."""
        return bien_etre._calculer_score_nutrition(self)

    def _calculer_score_budget(self) -> float:
        """Score budget basé sur les dépassements (0-100)."""
        return bien_etre._calculer_score_budget(self)

    def _calculer_score_routines(self) -> float:
        """Score routines basé sur l'accomplissement (0-100)."""
        return bien_etre._calculer_score_routines(self)

    def _detail_sport(self, score: float) -> str:
        return bien_etre._detail_sport(self, score)

    def _detail_nutrition(self, score: float) -> str:
        return bien_etre._detail_nutrition(self, score)

    def _detail_budget(self, score: float) -> str:
        return bien_etre._detail_budget(self, score)

    def _detail_routines(self, score: float) -> str:
        return bien_etre._detail_routines(self, score)

    def _evaluer_tendance(self, dimension: str) -> str:
        """Évalue la tendance d'une dimension (simplifié)."""
        return bien_etre._evaluer_tendance(self, dimension)

    def _evaluer_niveau(self, score: float) -> str:
        return bien_etre._evaluer_niveau(self, score)

    def _generer_conseils(self, dimensions: list[DimensionBienEtre]) -> list[str]:
        """Génère des conseils basés sur les dimensions les plus faibles."""
        return bien_etre._generer_conseils(self, dimensions)

    def _generer_conseils_score_famille(self, dimensions: list[DimensionScoreFamille]) -> list[str]:
        """Conseils ciblés pour le score famille hebdo."""
        return bien_etre._generer_conseils_score_famille(self, dimensions)

    def _generer_pdf_simple(self, titre: str, sections: list[tuple[str, list[str]]]) -> str:
        """Genere un PDF simple et retourne son contenu en base64."""
        import base64
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        y = 800
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(40, y, titre[:100])
        y -= 28
        pdf.setFont("Helvetica", 10)
        pdf.drawString(40, y, f"Genere le {datetime.now(UTC).strftime('%d/%m/%Y %H:%M')}")
        y -= 24

        for section_titre, lignes in sections:
            if y < 100:
                pdf.showPage()
                y = 800
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(40, y, section_titre[:90])
            y -= 16
            pdf.setFont("Helvetica", 10)
            for ligne in (lignes or ["-"]):
                if y < 80:
                    pdf.showPage()
                    y = 800
                    pdf.setFont("Helvetica", 10)
                pdf.drawString(52, y, f"- {str(ligne)[:130]}")
                y -= 14
            y -= 6

        pdf.save()
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("ascii")

    # ── Helpers mode invité ──

    def _collecter_repas_invite(self, session: Any) -> list[dict]:
        """Collecte les repas de la semaine pour un invité."""
        from src.core.models import Repas, Planning

        today = date.today()
        fin_semaine = today + timedelta(days=7)

        planning = session.query(Planning).order_by(Planning.cree_le.desc()).first()
        if not planning:
            return []

        repas = (
            session.query(Repas)
            .filter(
                Repas.planning_id == planning.id,
                Repas.date_repas >= today,
                Repas.date_repas <= fin_semaine,
            )
            .order_by(Repas.date_repas, Repas.type_repas)
            .all()
        )
        return [
            {
                "date": r.date_repas.isoformat(),
                "type": r.type_repas,
                "recette": getattr(getattr(r, "recette", None), "nom", "Repas libre"),
            }
            for r in repas
        ]

    def _collecter_routines_invite(self, session: Any) -> list[dict]:
        """Collecte les routines actives pour un invité."""
        from src.core.models.famille import Routine

        routines = session.query(Routine).filter(Routine.actif.is_(True)).all()
        return [
            {"nom": r.nom, "categorie": getattr(r, "categorie", "")}
            for r in routines
        ]

    def _collecter_profil_enfant_invite(self, session: Any) -> dict:
        """Collecte le profil enfant pour un invité."""
        from src.core.models import ProfilEnfant

        enfant = (
            session.query(ProfilEnfant)
            .filter(ProfilEnfant.actif.is_(True))
            .first()
        )
        if not enfant:
            return {}
        return {
            "prenom": enfant.name,
            "date_naissance": enfant.date_of_birth.isoformat() if enfant.date_of_birth else None,
        }

    def _collecter_contacts_urgence(self, session: Any) -> list[dict]:
        """Collecte les contacts d'urgence pour un invité."""
        try:
            from src.core.models.contacts import ContactFamille

            contacts = (
                session.query(ContactFamille)
                .filter(ContactFamille.categorie == "urgence")
                .all()
            )
            return [
                {
                    "nom": f"{c.nom} {getattr(c, 'prenom', '')}".strip(),
                    "telephone": getattr(c, "telephone", ""),
                    "relation": getattr(c, "relation", ""),
                }
                for c in contacts
            ]
        except Exception:
            return []


@service_factory("innovations", tags={"phase10", "ia"})
def get_innovations_service() -> InnovationsService:
    """Factory pour le service Innovations (singleton via registre)."""
    return InnovationsService()
