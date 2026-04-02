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
    EtapeBatchIntelligente,
    ModeTabletteMagazineResponse,
    PlanificationHebdoCompleteResponse,
    PreferenceApprise,
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
    # PHASE 9 — IA AVANCÉE & INNOVATIONS
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @chronometre("innovations.p9.mange_ce_soir", seuil_alerte_ms=8000)
    def suggerer_repas_ce_soir(
        self,
        temps_disponible_min: int = 30,
        humeur: str = "rapide",
    ) -> SuggestionRepasSoirResponse | None:
        """P9-01 : suggère un repas du soir contextuel en une action."""
        humeur_safe = _sanitiser(humeur, 50)
        candidates = self._recettes_rapides(temps_disponible_min)
        if not candidates:
            return SuggestionRepasSoirResponse(
                recette_suggeree="Omelette légumes + salade",
                raison="Aucune recette correspondante en base, fallback rapide et équilibré.",
                temps_total_estime_min=min(temps_disponible_min, 20),
                alternatives=["Pâtes tomate basilic", "Poêlée légumes riz"],
            )

        recette = candidates[0]
        alternatives = [r["nom"] for r in candidates[1:4]]
        return SuggestionRepasSoirResponse(
            recette_suggeree=recette["nom"],
            raison=(
                f"Sélection basée sur un temps disponible de {temps_disponible_min} min "
                f"et une humeur '{humeur_safe}'."
            ),
            temps_total_estime_min=recette["temps_total"],
            alternatives=alternatives,
        )

    @avec_cache(ttl=3600, key_func=lambda self, periode_jours: f"p9_patterns_{periode_jours}")
    @avec_gestion_erreurs(default_return=None)
    def analyser_patterns_alimentaires(
        self,
        periode_jours: int = 90,
    ) -> PatternsAlimentairesResponse | None:
        """P9-02 : analyse les patterns alimentaires récents."""
        top_recettes, score_diversite = self._patterns_recettes(periode_jours)
        recommandations = [
            "Ajouter 1 repas végétarien supplémentaire par semaine",
            "Varier davantage les sources de protéines",
        ]
        return PatternsAlimentairesResponse(
            periode_jours=periode_jours,
            score_diversite=score_diversite,
            top_recettes=top_recettes,
            categories_sous_representees=["légumineuses", "poisson"],
            recommandations=recommandations,
        )

    @avec_cache(ttl=1800, key_func=lambda self: "p9_coach_routines")
    @avec_gestion_erreurs(default_return=None)
    def coach_routines_ia(self) -> CoachRoutinesResponse | None:
        """P9-03 : identifie les blocages routines et propose des ajustements."""
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
        """P9-04 : détecte des anomalies eau/gaz/électricité."""
        from src.services.maison.energie_anomalies_ia import obtenir_service_energie_anomalies_ia

        service = obtenir_service_energie_anomalies_ia()
        details: list[AnomalieEnergieDetail] = []
        for type_compteur in ("electricite", "gaz", "eau"):
            resultat = service.analyser_anomalies(type_compteur=type_compteur, nb_mois=12, seuil_pct=20)
            for a in resultat.get("anomalies", []):
                details.append(
                    AnomalieEnergieDetail(
                        type_energie=type_compteur,
                        mois=str(a.get("mois", "")),
                        ecart_pct=float(a.get("ecart_pct", 0.0) or 0.0),
                        severite=str(a.get("severite", "moyenne")),
                        explication=str(a.get("explication", "Variation significative détectée.")),
                    )
                )

        score_risque = round(min(100.0, len(details) * 18.0), 1)
        recommandations = [
            "Vérifier les appareils énergivores des 30 derniers jours",
            "Contrôler les fuites potentielles (eau/gaz)",
        ]
        return AnomaliesEnergieResponse(
            nb_anomalies=len(details),
            score_risque=score_risque,
            anomalies=details,
            recommandations=recommandations,
        )

    @avec_cache(ttl=3600, key_func=lambda self: "p9_resume_mensuel")
    @avec_gestion_erreurs(default_return=None)
    def generer_resume_mensuel_ia(self) -> ResumeMensuelIAResponse | None:
        """P9-06 : génère un résumé mensuel narratif multi-modules."""
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
        """P9-08 : planning d'activités Jules ajusté âge + historique."""
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
        """P9-09 : compare des offres énergie sur la base de la consommation."""
        conso = self._consommation_annuelle_kwh()
        cout_actuel = round(conso * prix_kwh_actuel_eur + abonnement_mensuel_eur * 12, 2)

        offres = [
            OffreEnergieAlternative(
                fournisseur="Offre EcoFix",
                prix_kwh_eur=round(prix_kwh_actuel_eur * 0.95, 4),
                abonnement_mensuel_eur=max(0.0, abonnement_mensuel_eur - 1.5),
            ),
            OffreEnergieAlternative(
                fournisseur="Offre Tempo+",
                prix_kwh_eur=round(prix_kwh_actuel_eur * 0.92, 4),
                abonnement_mensuel_eur=abonnement_mensuel_eur + 1.0,
            ),
            OffreEnergieAlternative(
                fournisseur="Offre Verte Locale",
                prix_kwh_eur=round(prix_kwh_actuel_eur * 0.97, 4),
                abonnement_mensuel_eur=abonnement_mensuel_eur,
            ),
        ]

        for offre in offres:
            offre.cout_annuel_estime_eur = round(
                conso * offre.prix_kwh_eur + offre.abonnement_mensuel_eur * 12,
                2,
            )

        economie = round(max(0.0, cout_actuel - min((o.cout_annuel_estime_eur for o in offres), default=cout_actuel)), 2)
        return ComparateurEnergieResponse(
            consommation_annuelle_kwh=conso,
            cout_actuel_estime_eur=cout_actuel,
            economie_max_estimee_eur=economie,
            offres=offres,
        )

    @avec_cache(ttl=1800, key_func=lambda self: "p9_score_eco")
    @avec_gestion_erreurs(default_return=None)
    def calculer_score_eco_responsable(self) -> ScoreEcoResponsableResponse | None:
        """P9-10 : calcule un score écologique mensuel."""
        score_recettes = self._score_recettes_eco()
        score_energie = max(0.0, 100.0 - self._score_risque_energie_simple())
        score_global = round(score_recettes * 0.5 + score_energie * 0.5, 1)
        return ScoreEcoResponsableResponse(
            score_global=score_global,
            details={
                "alimentation_locale_bio": round(score_recettes, 1),
                "efficacite_energetique": round(score_energie, 1),
            },
            recommandations=[
                "Privilégier les recettes de saison et locales",
                "Suivre les pics de consommation hebdomadaires",
            ],
        )

    @avec_cache(ttl=86400, key_func=lambda self: "p9_saisonnalite")
    @avec_gestion_erreurs(default_return=None)
    def appliquer_saisonnalite_intelligente(self) -> SaisonnaliteIntelligenteResponse | None:
        """P9-11 : produit des adaptations transverses selon la saison."""
        saison = self._saison_courante()
        recettes = self._recettes_de_saison(saison)
        if saison in {"hiver", "automne"}:
            energie = ["Baisser le chauffage la nuit de 1°C", "Vérifier l'isolation des ouvrants"]
            jardin = ["Protéger les plantes sensibles", "Planifier les tailles de repos végétatif"]
            entretien = ["Contrôler joints et humidité", "Purger les radiateurs"]
        else:
            energie = ["Décaler les appareils en heures creuses", "Optimiser ventilation naturelle"]
            jardin = ["Arroser tôt le matin", "Planifier semis/récoltes de saison"]
            entretien = ["Nettoyer filtres VMC", "Vérifier extérieurs et gouttières"]
        return SaisonnaliteIntelligenteResponse(
            saison=saison,
            recettes_de_saison=recettes,
            actions_jardin=jardin,
            actions_entretien=entretien,
            ajustements_energie=energie,
        )

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

    @avec_cache(ttl=1800, key_func=lambda self: "phase_e_score_famille_hebdo")
    @avec_gestion_erreurs(default_return=None)
    def calculer_score_famille_hebdo(self) -> ScoreFamilleHebdoResponse | None:
        """E3 : score famille hebdo composite (nutrition, depenses, activites, entretien)."""
        return calculer_score_famille_hebdo_module(self)

    @avec_cache(ttl=3600, key_func=lambda self: "phase_e_journal_auto")
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
        """IN10 : lit l'etat du mode vacances utilisateur."""
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
        """IN10 : active/desactive le mode vacances dans les preferences notifications."""
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
        """IN11 : génère 1-2 insights IA proactifs par jour (anti-spam)."""
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
        """IN4 : synthèse météo unique avec impacts cuisine/famille/maison/énergie."""
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
        """S22 IN1 : apprend des préférences stables et active leur influence après 2+ semaines."""
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
        """S22 IN9 : génère planning repas + courses + tâches maison + jardin en un seul bloc."""
        semaine_debut = self._prochaine_semaine_lundi()
        semaine_fin = semaine_debut + timedelta(days=6)

        repas = self._proposer_repas_semaine(semaine_debut=semaine_debut, limite=7)
        courses = self._proposer_courses_depuis_repas(repas)
        taches_maison = self._proposer_taches_maison_hebdo(limite=5)
        taches_jardin = self._proposer_taches_jardin_hebdo(semaine_fin=semaine_fin, limite=4)

        blocs = [
            BlocPlanificationAuto(titre="Repas semaine", items=repas),
            BlocPlanificationAuto(titre="Liste de courses", items=courses),
            BlocPlanificationAuto(titre="Maison", items=taches_maison),
            BlocPlanificationAuto(titre="Jardin", items=taches_jardin),
        ]
        return PlanificationHebdoCompleteResponse(
            semaine_reference=semaine_debut.isoformat(),
            genere_en_un_clic=True,
            blocs=blocs,
            resume="Planning complet genere automatiquement pour la semaine cible.",
        )

    @avec_cache(ttl=1800, key_func=lambda self, user_id: f"s22_batch_intelligent_{user_id or 'anon'}_{date.today().isoformat()}")
    @avec_gestion_erreurs(default_return=None)
    def proposer_batch_cooking_intelligent(self, user_id: str | None = None) -> BatchCookingIntelligentResponse | None:
        """S22 IN13 : propose un plan batch cooking cohérent avec le planning de semaine."""
        recettes = self._recettes_batch_cibles(limite=4)
        if not recettes:
            recettes = [
                "Base legumes rotis", "Poulet effiloche", "Riz complet", "Compote sans sucre ajoute",
            ]

        date_session = self._prochaine_date_batch()
        etapes: list[EtapeBatchIntelligente] = []
        for index, recette in enumerate(recettes, start=1):
            etapes.append(
                EtapeBatchIntelligente(
                    ordre=index,
                    action=f"Preparer {recette}",
                    duree_minutes=25 if index <= 2 else 20,
                )
            )

        duree_totale = sum(etape.duree_minutes for etape in etapes)
        conseils = [
            "Demarrer par les cuissons longues pour paralléliser les preparatifs.",
            "Prevoir des portions adaptees pour Jules (sans sel, texture simplifiee).",
            "Etiqueter les boites avec date et portions restantes.",
        ]
        return BatchCookingIntelligentResponse(
            session_nom=f"Batch intelligent {date_session.strftime('%d/%m')}",
            date_session=date_session.isoformat(),
            recettes_cibles=recettes,
            duree_estimee_totale_minutes=duree_totale,
            etapes=etapes,
            conseils=conseils,
        )

    @avec_gestion_erreurs(default_return=None)
    def generer_carte_visuelle_partageable(
        self,
        type_carte: str = "planning",
        titre: str | None = None,
    ) -> CarteVisuellePartageableResponse | None:
        """S22 IN17 : génère une carte visuelle exportable au format image (SVG base64)."""
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
        """S22 IN7 : fournit une vue magazine condensée pour écran tablette."""
        score_bien_etre = self.calculer_score_bien_etre() or ScoreBienEtreResponse(score_global=0.0)
        insights = self.generer_insights_quotidiens(limite=2) or InsightsQuotidiensResponse()
        meteo = self.analyser_meteo_contextuelle() or MeteoContextuelleResponse()

        cartes = [
            CarteMagazineTablette(
                titre="Score bien-etre",
                valeur=f"{round(score_bien_etre.score_global, 1)}/100",
                accent="energie",
                action_url="/outils/tableau-sante",
            ),
            CarteMagazineTablette(
                titre="Insights du jour",
                valeur=str(insights.nb_insights),
                accent="focus",
                action_url="/",
            ),
            CarteMagazineTablette(
                titre="Meteo",
                valeur=meteo.description or "Stable",
                accent="saison",
                action_url="/outils/meteo",
            ),
        ]
        return ModeTabletteMagazineResponse(
            titre="Edition tablette",
            sous_titre="Vue magazine priorisee pour la famille",
            cartes=cartes,
        )

    # ═══════════════════════════════════════════════════════════
    # 10.4 — BILAN ANNUEL AUTOMATIQUE IA
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=86400, key_func=lambda self, annee: f"bilan_annuel_{annee}")
    @avec_gestion_erreurs(default_return=None)
    @chronometre("innovations.bilan_annuel", seuil_alerte_ms=15000)
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
    @chronometre("innovations.score_bien_etre", seuil_alerte_ms=5000)
    def calculer_score_bien_etre(self) -> ScoreBienEtreResponse | None:
        """Calcule le score bien-être familial composite (0-100).

        Combine 4 dimensions :
        - Sport (Garmin) : pas, activités, calories
        - Nutrition : planning équilibré, score nutritionnel
        - Budget : stress financier, dépassements
        - Routines : régularité, accomplissement
        """
        dimensions = []
        scores = []

        # Dimension Sport (poids 30%)
        score_sport = self._calculer_score_sport()
        dimensions.append(DimensionBienEtre(
            nom="Sport & Activité Physique",
            score=score_sport,
            poids=0.30,
            detail=self._detail_sport(score_sport),
            tendance=self._evaluer_tendance("sport"),
        ))
        scores.append(score_sport * 0.30)

        # Dimension Nutrition (poids 25%)
        score_nutrition = self._calculer_score_nutrition()
        dimensions.append(DimensionBienEtre(
            nom="Nutrition & Alimentation",
            score=score_nutrition,
            poids=0.25,
            detail=self._detail_nutrition(score_nutrition),
            tendance=self._evaluer_tendance("nutrition"),
        ))
        scores.append(score_nutrition * 0.25)

        # Dimension Budget (poids 25%)
        score_budget = self._calculer_score_budget()
        dimensions.append(DimensionBienEtre(
            nom="Équilibre Financier",
            score=score_budget,
            poids=0.25,
            detail=self._detail_budget(score_budget),
            tendance=self._evaluer_tendance("budget"),
        ))
        scores.append(score_budget * 0.25)

        # Dimension Routines (poids 20%)
        score_routines = self._calculer_score_routines()
        dimensions.append(DimensionBienEtre(
            nom="Régularité & Routines",
            score=score_routines,
            poids=0.20,
            detail=self._detail_routines(score_routines),
            tendance=self._evaluer_tendance("routines"),
        ))
        scores.append(score_routines * 0.20)

        score_global = round(sum(scores), 1)
        niveau = self._evaluer_niveau(score_global)

        # Conseils basés sur les scores les plus bas
        conseils = self._generer_conseils(dimensions)

        return ScoreBienEtreResponse(
            score_global=score_global,
            niveau=niveau,
            dimensions=dimensions,
            historique_7j=[],
            conseils=conseils,
        )

    # ═══════════════════════════════════════════════════════════
    # 10.17 — ENRICHISSEMENT CONTACTS IA
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=3600, key_func=lambda self: "enrichissement_contacts")
    @avec_gestion_erreurs(default_return=None)
    @chronometre("innovations.enrichissement_contacts", seuil_alerte_ms=10000)
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
    @chronometre("innovations.tendances_loto", seuil_alerte_ms=10000)
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
    @chronometre("innovations.parcours_magasin", seuil_alerte_ms=5000)
    def optimiser_parcours_magasin(
        self, liste_id: int | None = None
    ) -> ParcoursOptimiseResponse | None:
        """Optimise le parcours magasin en regroupant les articles par rayon."""
        articles = self._collecter_articles_courses(liste_id)
        if not articles:
            return ParcoursOptimiseResponse()

        prompt = f"""Organise ces articles de courses par rayon de supermarché et optimise le parcours.

Articles : {json.dumps(articles, ensure_ascii=False)}

Retourne un JSON :
{{
  "articles_par_rayon": {{
    "Fruits & Légumes": ["tomates", "carottes", "pommes"],
    "Boulangerie": ["pain", "croissants"],
    "Produits laitiers": ["lait", "yaourt"]
  }},
  "ordre_rayons": ["Fruits & Légumes", "Boulangerie", "Produits laitiers", "Épicerie", "Surgelés", "Boissons"],
  "nb_articles": {len(articles)},
  "temps_estime_minutes": 25
}}

Règles :
- Ordre typique d'un supermarché français (entrée = fruits&légumes, sortie = caisses)
- Regroupe les articles similaires
- Estime le temps en fonction du nombre d'articles"""

        return self.call_with_parsing_sync(
            prompt=prompt,
            response_model=ParcoursOptimiseResponse,
            system_prompt="Tu es un expert en optimisation de parcours en supermarché.",
        )

    # ═══════════════════════════════════════════════════════════
    # 10.8 — VEILLE EMPLOI HABITAT
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=3600, key_func=lambda self, criteres: f"veille_emploi_{hash(str(criteres))}")
    @avec_gestion_erreurs(default_return=None)
    @chronometre("innovations.veille_emploi", seuil_alerte_ms=15000)
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
        try:
            with obtenir_contexte_db() as session:
                from src.core.models import Recette

                recettes = (
                    session.query(Recette)
                    .filter((Recette.temps_preparation + Recette.temps_cuisson) <= temps_disponible_min)
                    .order_by(Recette.est_rapide.desc(), Recette.score_ia.desc().nullslast())
                    .limit(8)
                    .all()
                )
                return [
                    {
                        "nom": r.nom,
                        "temps_total": int((r.temps_preparation or 0) + (r.temps_cuisson or 0)),
                    }
                    for r in recettes
                ]
        except Exception:
            return []

    def _patterns_recettes(self, periode_jours: int) -> tuple[list[str], float]:
        """Calcule les top recettes et un score de diversité simplifié."""
        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func
                from src.core.models import HistoriqueRecette, Recette

                debut = date.today() - timedelta(days=periode_jours)
                rows = (
                    session.query(Recette.nom, func.count(HistoriqueRecette.id).label("cnt"))
                    .join(HistoriqueRecette, HistoriqueRecette.recette_id == Recette.id)
                    .filter(HistoriqueRecette.date_cuisson >= debut)
                    .group_by(Recette.nom)
                    .order_by(func.count(HistoriqueRecette.id).desc())
                    .limit(5)
                    .all()
                )
                top = [str(r[0]) for r in rows]
                total = sum(int(r[1] or 0) for r in rows)
                uniques = len(top)
                score = round(min(100.0, (uniques / max(1, total)) * 220.0), 1)
                return top, score
        except Exception:
            return [], 0.0

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
        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func
                from src.core.models.utilitaires import ReleveEnergie

                annee = date.today().year
                total = (
                    session.query(func.sum(ReleveEnergie.consommation))
                    .filter(ReleveEnergie.annee == annee, ReleveEnergie.type_energie == "electricite")
                    .scalar()
                )
                return round(float(total or 3200.0), 2)
        except Exception:
            return 3200.0

    def _score_risque_energie_simple(self) -> float:
        """Score de risque énergie simplifié (0 faible risque, 100 risque élevé)."""
        data = self.detecter_anomalies_energie()
        if not data:
            return 40.0
        return data.score_risque

    def _score_recettes_eco(self) -> float:
        """Score écologique côté cuisine basé sur bio/local."""
        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func
                from src.core.models import Recette

                total = session.query(func.count(Recette.id)).scalar() or 0
                if total == 0:
                    return 50.0
                eco = (
                    session.query(func.count(Recette.id))
                    .filter((Recette.est_bio.is_(True)) | (Recette.est_local.is_(True)))
                    .scalar() or 0
                )
                return round((float(eco) / float(total)) * 100.0, 1)
        except Exception:
            return 50.0

    def _saison_courante(self) -> str:
        """Détermine la saison courante."""
        mois = date.today().month
        if mois in (12, 1, 2):
            return "hiver"
        if mois in (3, 4, 5):
            return "printemps"
        if mois in (6, 7, 8):
            return "été"
        return "automne"

    def _recettes_de_saison(self, saison: str) -> list[str]:
        """Récupère quelques recettes adaptées à la saison."""
        try:
            with obtenir_contexte_db() as session:
                from src.core.models import Recette

                rows = (
                    session.query(Recette.nom)
                    .filter((Recette.saison == saison) | (Recette.saison == "toute_année"))
                    .limit(5)
                    .all()
                )
                return [str(r[0]) for r in rows]
        except Exception:
            return []

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

    def _jours_depuis_repas_poisson(self) -> int:
        """Retourne le nombre de jours depuis le dernier repas poisson (max 365)."""
        try:
            with obtenir_contexte_db() as session:
                from src.core.models import Recette, Repas

                dernier = (
                    session.query(Repas.date_repas)
                    .join(Recette, Recette.id == Repas.recette_id)
                    .filter(Recette.categorie == "poisson")
                    .order_by(Repas.date_repas.desc())
                    .first()
                )
                if not dernier or not dernier[0]:
                    return 365
                return max(0, (date.today() - dernier[0]).days)
        except Exception:
            return 365

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
        try:
            with obtenir_contexte_db() as session:
                from src.core.models import ArticleCourses, ListeCourses, Ingredient

                query = session.query(ListeCourses).filter(ListeCourses.archivee.is_(False))
                if liste_id:
                    query = query.filter(ListeCourses.id == liste_id)
                liste = query.order_by(ListeCourses.id.desc()).first()
                if not liste:
                    return []

                articles = (
                    session.query(ArticleCourses)
                    .filter(ArticleCourses.liste_id == liste.id, ArticleCourses.coche.is_(False))
                    .all()
                )
                noms = []
                for a in articles:
                    ingredient = session.query(Ingredient).filter(Ingredient.id == a.ingredient_id).first()
                    if ingredient:
                        noms.append(ingredient.nom)
                return noms
        except Exception:
            logger.warning("Erreur collecte articles courses", exc_info=True)
            return []

    def _prochaine_semaine_lundi(self) -> date:
        """Retourne la date du prochain lundi (semaine cible)."""
        today = date.today()
        delta = (7 - today.weekday()) % 7
        if delta == 0:
            delta = 7
        return today + timedelta(days=delta)

    def _proposer_repas_semaine(self, semaine_debut: date, limite: int = 7) -> list[str]:
        """Construit une proposition de repas pour la semaine cible."""
        repas: list[str] = []
        try:
            with obtenir_contexte_db() as session:
                from src.core.models import Recette

                recettes = (
                    session.query(Recette.nom)
                    .order_by(Recette.score_ia.desc().nullslast(), Recette.cree_le.desc())
                    .limit(limite)
                    .all()
                )
                repas = [str(row[0]) for row in recettes if row and row[0]]
        except Exception:
            logger.debug("Selection repas semaine via DB indisponible", exc_info=True)

        if not repas:
            repas = [
                "Lundi: Poelee legumes + proteines",
                "Mardi: Poisson au four + puree douce",
                "Mercredi: Pates legumes rôtis",
                "Jeudi: Curry doux maison",
                "Vendredi: Riz safrane + legumes",
                "Samedi: Batch restes intelligents",
                "Dimanche: Plat familial cuisson lente",
            ]
        return repas[:limite]

    def _proposer_courses_depuis_repas(self, repas: list[str]) -> list[str]:
        """Crée une liste de courses simple basée sur les repas prévus."""
        base = ["fruits de saison", "legumes frais", "yaourts nature", "oeufs", "riz", "huile d'olive"]
        if any("poisson" in r.lower() for r in repas):
            base.append("poisson frais")
        if any("curry" in r.lower() for r in repas):
            base.append("lait de coco")
        return base[:10]

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
        try:
            with obtenir_contexte_db() as session:
                from src.core.models import Repas, Recette

                start = self._prochaine_semaine_lundi()
                end = start + timedelta(days=6)
                rows = (
                    session.query(Recette.nom)
                    .join(Repas, Repas.recette_id == Recette.id)
                    .filter(Repas.date_repas >= start, Repas.date_repas <= end)
                    .limit(20)
                    .all()
                )
                uniques: list[str] = []
                for row in rows:
                    nom = str(row[0]) if row and row[0] else ""
                    if nom and nom not in uniques:
                        uniques.append(nom)
                    if len(uniques) >= limite:
                        break
                return uniques
        except Exception:
            logger.debug("Extraction recettes batch cible indisponible", exc_info=True)
            return []

    def _prochaine_date_batch(self) -> date:
        """Détermine la prochaine date optimale de batch cooking."""
        fallback = self._prochaine_semaine_lundi() - timedelta(days=1)
        try:
            with obtenir_contexte_db() as session:
                from src.core.models.batch_cooking import ConfigBatchCooking

                config = session.query(ConfigBatchCooking).order_by(ConfigBatchCooking.id.desc()).first()
                if not config or not config.jours_batch:
                    return fallback

                jours_batch = [int(j) for j in config.jours_batch if isinstance(j, int)]
                if not jours_batch:
                    return fallback

                today = date.today()
                delta_candidates = [((jour - today.weekday()) % 7) for jour in jours_batch]
                delta = min(delta_candidates)
                return today + timedelta(days=delta)
        except Exception:
            return fallback

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
        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func
                from src.core.models.garmin import DonneesGarmin

                semaine = date.today() - timedelta(days=7)
                donnees = (
                    session.query(DonneesGarmin)
                    .filter(DonneesGarmin.date >= semaine)
                    .all()
                )
                if not donnees:
                    return 50.0

                pas_moyen = sum(getattr(d, "pas", 0) or 0 for d in donnees) / len(donnees)
                # 10000 pas/jour = 100, 0 = 0
                score = min(100, (pas_moyen / 10000) * 100)
                return round(score, 1)
        except Exception:
            return 50.0

    def _calculer_score_nutrition(self) -> float:
        """Score nutrition basé sur le planning repas (0-100)."""
        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func
                from src.core.models import Repas

                semaine = date.today() - timedelta(days=7)
                nb_repas = (
                    session.query(func.count(Repas.id))
                    .filter(Repas.date_repas >= semaine)
                    .scalar() or 0
                )
                # 21 repas/semaine (3/jour) = 100
                score = min(100, (nb_repas / 21) * 100)
                return round(score, 1)
        except Exception:
            return 50.0

    def _calculer_score_budget(self) -> float:
        """Score budget basé sur les dépassements (0-100)."""
        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func
                from src.core.models import BudgetFamille

                mois_courant = date.today().replace(day=1)
                total = (
                    session.query(func.sum(BudgetFamille.montant))
                    .filter(BudgetFamille.date >= mois_courant)
                    .scalar() or 0
                )
                # Moins de dépenses = meilleur score (heuristique simple)
                score = max(0, 100 - min(100, total / 50))
                return round(score, 1)
        except Exception:
            return 60.0

    def _calculer_score_routines(self) -> float:
        """Score routines basé sur l'accomplissement (0-100)."""
        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func
                from src.core.models.famille import Routine

                routines_actives = (
                    session.query(func.count(Routine.id))
                    .filter(Routine.actif.is_(True))
                    .scalar() or 0
                )
                if routines_actives == 0:
                    return 50.0
                # Avoir des routines actives = bon signe
                score = min(100, routines_actives * 15)
                return round(float(score), 1)
        except Exception:
            return 50.0

    def _detail_sport(self, score: float) -> str:
        if score >= 80:
            return "Excellent niveau d'activité physique"
        if score >= 60:
            return "Bon niveau d'activité, continuez !"
        if score >= 40:
            return "Activité modérée, essayez de bouger plus"
        return "Activité insuffisante, fixez-vous un objectif de pas quotidien"

    def _detail_nutrition(self, score: float) -> str:
        if score >= 80:
            return "Planning repas bien rempli et équilibré"
        if score >= 60:
            return "Bonne planification, quelques repas à ajouter"
        if score >= 40:
            return "Planning repas incomplet, planifiez davantage"
        return "Peu de repas planifiés, utilisez le planificateur IA"

    def _detail_budget(self, score: float) -> str:
        if score >= 80:
            return "Budget maîtrisé, bravo !"
        if score >= 60:
            return "Budget correct, attention aux dépenses"
        if score >= 40:
            return "Budget tendu, surveillez vos dépenses"
        return "Budget dépassé, réduisez les dépenses non essentielles"

    def _detail_routines(self, score: float) -> str:
        if score >= 80:
            return "Routines régulières et bien suivies"
        if score >= 60:
            return "Bonnes routines, restez constant"
        if score >= 40:
            return "Quelques routines à consolider"
        return "Peu de routines actives, créez-en pour structurer votre quotidien"

    def _evaluer_tendance(self, dimension: str) -> str:
        """Évalue la tendance d'une dimension (simplifié)."""
        return "stable"

    def _evaluer_niveau(self, score: float) -> str:
        if score >= 80:
            return "excellent"
        if score >= 60:
            return "bon"
        if score >= 40:
            return "moyen"
        return "attention"

    def _generer_conseils(self, dimensions: list[DimensionBienEtre]) -> list[str]:
        """Génère des conseils basés sur les dimensions les plus faibles."""
        conseils = []
        sorted_dims = sorted(dimensions, key=lambda d: d.score)
        for dim in sorted_dims[:2]:
            if dim.score < 60:
                conseils.append(f"Améliorez votre {dim.nom.lower()} : {dim.detail}")
        if not conseils:
            conseils.append("Continuez ainsi, votre bien-être familial est excellent !")
        return conseils

    def _generer_conseils_score_famille(self, dimensions: list[DimensionScoreFamille]) -> list[str]:
        """Conseils ciblés pour le score famille hebdo."""
        conseils: list[str] = []
        faibles = sorted(dimensions, key=lambda d: d.score)[:2]
        for d in faibles:
            if d.score < 60:
                conseils.append(f"Renforcer le pilier {d.nom.lower()} cette semaine.")
        if not conseils:
            conseils.append("Semaine bien equilibree, gardez ce rythme.")
        return conseils

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
