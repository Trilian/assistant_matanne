"""Routes API pour les services IA modulaires."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import median
from typing import Any

from fastapi import APIRouter, Depends

from src.api.dependencies import require_auth
from src.api.rate_limiting import verifier_limite_debit_ia
from src.api.schemas.errors import REPONSES_IA
from src.api.schemas.ia_modules import (
    AnalyseHabitudeRequest,
    AnalyseImpactsMeteoRequest,
    AnalyseNutritionPersonneRequest,
    AnalyseVarietePlanningRequest,
    BilanMensuelNarratifResponse,
    CalendrierSemisPersonnaliseResponse,
    DiagnosticPlanteJardinRequest,
    DiagnosticPlanteJardinResponse,
    EstimationComparaisonDevisResponse,
    EstimationProjetMaisonRequest,
    EstimationRoiHabitatResponse,
    OptimisationNutritionPlanningRequest,
    PredictionEnergieResponse,
    PredictionConsommationRequest,
    SuggestionSimplificationPlanningRequest,
)
from src.api.utils import gerer_exception_api
from src.core.models.abonnements import Artisan
from src.core.models.maison_extensions import DevisComparatif
from src.services.cuisine.nutrition_famille_ia import DonneesNutritionnelles
from src.services.habitat.dvf_service import obtenir_service_dvf_habitat
from src.services.integrations.habitudes_ia import AnalyseHabitude
from src.services.integrations.meteo_impact_ai import MeteoContexte
from src.services.inventaire.ia_service import PredictionConsommation
from src.services.maison.ia.projets_ia_service import EstimationProjet
from src.services.planning.ia_service import AnalyseVariete, OptimisationNutrition, SimplificationSemaine
from src.services.utilitaires.meteo_service import MeteoService

router = APIRouter(prefix="/api/v1/ia/modules", tags=["IA"])


def _get_inventaire_ai_service():
    from src.services.inventaire.ia_service import get_inventaire_ai_service

    return get_inventaire_ai_service()


def _get_planning_ai_service():
    from src.services.planning.ia_service import get_planning_ai_service

    return get_planning_ai_service()


def _get_meteo_impact_ai_service():
    from src.services.integrations.meteo_impact_ai import get_meteo_impact_ai_service

    return get_meteo_impact_ai_service()


def _get_habitudes_ai_service():
    from src.services.integrations.habitudes_ia import get_habitudes_ai_service

    return get_habitudes_ai_service()


def _get_projets_maison_ai_service():
    from src.services.maison.ia.projets_ia_service import get_projets_maison_ai_service

    return get_projets_maison_ai_service()


def _get_nutrition_famille_ai_service():
    from src.services.cuisine.nutrition_famille_ia import get_nutrition_famille_ai_service

    return get_nutrition_famille_ai_service()


def _charger_catalogue_plantes() -> list[dict[str, Any]]:
    catalogue_path = Path("data/reference/plantes_catalogue.json")
    if not catalogue_path.exists():
        return []
    with open(catalogue_path, encoding="utf-8") as f:
        contenu = json.load(f)
    if isinstance(contenu, list):
        return [item for item in contenu if isinstance(item, dict)]
    return [item for item in contenu.get("plantes", []) if isinstance(item, dict)]


def _charger_devis_avec_artisans(projet_id: int) -> list[tuple[DevisComparatif, Artisan | None]]:
    from src.api.utils import executer_avec_session

    with executer_avec_session() as session:
        return (
            session.query(DevisComparatif, Artisan)
            .outerjoin(Artisan, DevisComparatif.artisan_id == Artisan.id)
            .filter(DevisComparatif.projet_id == projet_id)
            .all()
        )


@router.post(
    "/inventaire/prediction-consommation",
    response_model=PredictionConsommation,
    responses=REPONSES_IA,
    summary="Prédire la consommation d'un article d'inventaire",
)
@gerer_exception_api
async def predire_consommation_inventaire(
    body: PredictionConsommationRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> PredictionConsommation:
    service = _get_inventaire_ai_service()
    return service.predire_consommation(
        ingredient_nom=body.ingredient_nom,
        stock_actuel_kg=body.stock_actuel_kg,
        historique_achat_mensuel=body.historique_achat_mensuel,
    )


@router.post(
    "/planning/analyse-variete",
    response_model=AnalyseVariete,
    responses=REPONSES_IA,
    summary="Analyser la variété d'un planning de repas",
)
@gerer_exception_api
async def analyser_variete_planning(
    body: AnalyseVarietePlanningRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> AnalyseVariete:
    service = _get_planning_ai_service()
    return await service.analyser_variete_semaine(body.planning_repas)


@router.post(
    "/planning/optimisation-nutrition",
    response_model=OptimisationNutrition,
    responses=REPONSES_IA,
    summary="Optimiser l'équilibre nutritionnel d'un planning de repas",
)
@gerer_exception_api
async def optimiser_nutrition_planning(
    body: OptimisationNutritionPlanningRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> OptimisationNutrition:
    service = _get_planning_ai_service()
    return service.optimiser_nutrition_semaine(
        body.planning_repas,
        restrictions=body.restrictions or None,
    )


@router.post(
    "/planning/suggestions-simplification",
    response_model=SimplificationSemaine,
    responses=REPONSES_IA,
    summary="Suggérer une simplification du planning pour une semaine chargée",
)
@gerer_exception_api
async def suggerer_simplification_planning(
    body: SuggestionSimplificationPlanningRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> SimplificationSemaine:
    service = _get_planning_ai_service()
    return service.suggerer_simplification(
        body.planning_repas,
        nb_heures_cuisine_max=body.nb_heures_cuisine_max,
    )


@router.post(
    "/meteo/impacts",
    response_model=list[MeteoContexte],
    responses=REPONSES_IA,
    summary="Analyser les impacts météo cross-modules",
)
@gerer_exception_api
async def analyser_impacts_meteo(
    body: AnalyseImpactsMeteoRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> list[MeteoContexte]:
    service = _get_meteo_impact_ai_service()
    return await service.analyser_impacts(
        previsions_7j=body.previsions_7j,
        saison=body.saison,
    )


@router.post(
    "/habitudes/analyse",
    response_model=AnalyseHabitude,
    responses=REPONSES_IA,
    summary="Analyser une routine familiale",
)
@gerer_exception_api
async def analyser_habitude(
    body: AnalyseHabitudeRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> AnalyseHabitude:
    service = _get_habitudes_ai_service()
    return await service.analyser_habitude(
        habitude_nom=body.habitude_nom,
        historique_7j=body.historique_7j,
        description_contexte=body.description_contexte,
    )


@router.post(
    "/maison/projets/estimation",
    response_model=EstimationProjet,
    responses=REPONSES_IA,
    summary="Estimer un projet maison",
)
@gerer_exception_api
async def estimer_projet_maison(
    body: EstimationProjetMaisonRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> EstimationProjet:
    service = _get_projets_maison_ai_service()
    return await service.estimer_projet(
        projet_description=body.projet_description,
        surface_m2=body.surface_m2,
        type_maison=body.type_maison,
        contraintes=body.contraintes,
    )


@router.post(
    "/nutrition/personne",
    response_model=DonneesNutritionnelles,
    responses=REPONSES_IA,
    summary="Analyser la nutrition d'une personne",
)
@gerer_exception_api
async def analyser_nutrition_personne(
    body: AnalyseNutritionPersonneRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> DonneesNutritionnelles:
    service = _get_nutrition_famille_ai_service()
    return await service.analyser_nutrition_personne(
        personne_nom=body.personne_nom,
        age_ans=body.age_ans,
        sexe=body.sexe,
        activite_niveau=body.activite_niveau,
        donnees_garmin_semaine=body.donnees_garmin_semaine,
        recettes_semaine=body.recettes_semaine,
        objectif_sante=body.objectif_sante,
    )


@router.post(
    "/jardin/diagnostic-plante",
    response_model=DiagnosticPlanteJardinResponse,
    responses=REPONSES_IA,
    summary="Diagnostiquer une plante à partir d'une photo",
)
@gerer_exception_api
async def diagnostiquer_plante_jardin(
    body: DiagnosticPlanteJardinRequest,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> DiagnosticPlanteJardinResponse:
    from src.services.maison.jardin_service import obtenir_jardin_service

    service = obtenir_jardin_service()
    diagnostic = await service.diagnostiquer_plante(
        image_base64=body.image_base64,
        description=body.description,
    )
    return DiagnosticPlanteJardinResponse(
        plante_identifiee=diagnostic.plante_identifiee,
        etat=diagnostic.etat.value if hasattr(diagnostic.etat, "value") else str(diagnostic.etat),
        problemes_detectes=list(diagnostic.problemes_detectes or []),
        traitements_suggeres=list(diagnostic.traitements_suggeres or []),
        confiance=float(diagnostic.confiance or 0.0),
    )


@router.get(
    "/rapports/bilan-mensuel",
    response_model=BilanMensuelNarratifResponse,
    responses=REPONSES_IA,
    summary="Générer le bilan mensuel narratif multi-modules",
)
@gerer_exception_api
async def generer_bilan_mensuel_narratif(
    mois: str | None = None,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> BilanMensuelNarratifResponse:
    from src.services.rapports.bilan_mensuel import obtenir_bilan_mensuel_service

    service = obtenir_bilan_mensuel_service()
    bilan = await service.generer_bilan(mois=mois)
    return BilanMensuelNarratifResponse(**bilan)


@router.get(
    "/energie/prediction-consommation",
    response_model=PredictionEnergieResponse,
    responses=REPONSES_IA,
    summary="Prédire la consommation énergie et proposer des conseils",
)
@gerer_exception_api
async def predire_consommation_energie(
    nb_mois: int = 12,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> PredictionEnergieResponse:
    from datetime import date

    from src.services.maison.ia.energie_anomalies_ia import obtenir_service_energie_anomalies_ia

    service = obtenir_service_energie_anomalies_ia()
    types_compteurs = ("electricite", "gaz", "eau")
    predictions: dict[str, dict[str, object]] = {}
    total_anomalies = 0
    scores: list[float] = []

    for type_compteur in types_compteurs:
        analyse = service.analyser_anomalies(
            type_compteur=type_compteur,
            nb_mois=max(3, min(24, nb_mois)),
            seuil_pct=20.0,
        )
        points = list(analyse.get("points", []))
        moyenne = float(analyse.get("moyenne", 0.0) or 0.0)
        score = float(analyse.get("score_anormalite_global", 0.0) or 0.0)
        scores.append(score)

        derniere_conso = float(points[-1].get("conso", 0.0) or 0.0) if points else 0.0
        avant_derniere = float(points[-2].get("conso", 0.0) or 0.0) if len(points) > 1 else derniere_conso

        if avant_derniere > 0 and derniere_conso > avant_derniere * 1.08:
            tendance = "hausse"
        elif avant_derniere > 0 and derniere_conso < avant_derniere * 0.92:
            tendance = "baisse"
        else:
            tendance = "stable"

        predictions[type_compteur] = {
            "consommation_dernier_mois": round(derniere_conso, 2),
            "consommation_moyenne": round(moyenne, 2),
            "prediction_mois_suivant": round((derniere_conso * 0.6) + (moyenne * 0.4), 2),
            "tendance": tendance,
            "score_risque": round(score, 1),
            "nb_anomalies": int(analyse.get("nb_anomalies", 0) or 0),
        }
        total_anomalies += int(analyse.get("nb_anomalies", 0) or 0)

    conseils: list[str] = []
    if predictions.get("electricite", {}).get("tendance") == "hausse":
        conseils.append("Programmer les appareils énergivores sur les heures creuses.")
    if predictions.get("eau", {}).get("nb_anomalies", 0):
        conseils.append("Vérifier les fuites potentielles et les usages anormaux en eau.")
    if predictions.get("gaz", {}).get("tendance") == "hausse":
        conseils.append("Contrôler la régulation chauffage et l'isolation des pièces principales.")
    if not conseils:
        conseils.append("Consommation globalement stable: poursuivre le suivi mensuel.")

    return PredictionEnergieResponse(
        mois_reference=date.today().strftime("%Y-%m"),
        predictions=predictions,
        nb_anomalies=total_anomalies,
        score_risque_global=round(sum(scores) / max(1, len(scores)), 1),
        conseils=conseils,
    )


@router.get(
    "/jardin/calendrier-personnalise",
    response_model=CalendrierSemisPersonnaliseResponse,
    responses=REPONSES_IA,
    summary="IA-2: calendrier semis/récolte personnalisé (région + météo)",
)
@gerer_exception_api
async def obtenir_calendrier_semis_personnalise(
    region: str = "Maison",
    mois: int = 0,
    latitude: float = 48.8566,
    longitude: float = 2.3522,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> CalendrierSemisPersonnaliseResponse:
    from datetime import date

    mois_courant = mois if 1 <= mois <= 12 else date.today().month
    plantes = _charger_catalogue_plantes()

    meteo = MeteoService(lat=latitude, lon=longitude, ville=region).obtenir_meteo()
    previsions = list(meteo.previsions or [])
    temp_moy_max = round(sum(p.temp_max for p in previsions[:7]) / max(1, min(7, len(previsions))), 1)
    temp_moy_min = round(sum(p.temp_min for p in previsions[:7]) / max(1, min(7, len(previsions))), 1)
    pluie_7j = round(sum(float(p.precip_mm or 0.0) for p in previsions[:7]), 1)

    a_semer: list[dict[str, Any]] = []
    a_planter: list[dict[str, Any]] = []
    a_recolter: list[dict[str, Any]] = []

    for plante in plantes:
        nom = str(plante.get("nom", "")).strip()
        if not nom:
            continue
        semis = plante.get("mois_semis", plante.get("semis", [])) or []
        plantation = plante.get("mois_plantation", plante.get("plantation", [])) or []
        recolte = plante.get("mois_recolte", plante.get("recolte", [])) or []

        if mois_courant in semis:
            a_semer.append({"nom": nom, "type": plante.get("type", "")})
        if mois_courant in plantation:
            a_planter.append({"nom": nom, "type": plante.get("type", "")})
        if mois_courant in recolte:
            a_recolter.append({"nom": nom, "type": plante.get("type", "")})

    conseils: list[str] = []
    if temp_moy_min < 5:
        conseils.append("Risque de nuits froides: privilégier les semis sous abri cette semaine.")
    if pluie_7j < 5:
        conseils.append("Semaine sèche: prévoir un arrosage de démarrage pour les jeunes semis.")
    if pluie_7j > 30:
        conseils.append("Pluviométrie élevée: améliorer le drainage et espacer les arrosages.")
    if temp_moy_max >= 26:
        conseils.append("Températures hautes: pailler les zones fraîchement plantées.")
    if not conseils:
        conseils.append("Conditions globalement favorables pour le programme de semis/récolte.")

    return CalendrierSemisPersonnaliseResponse(
        mois=mois_courant,
        region=region,
        meteo_resume={
            "temp_moy_max": temp_moy_max,
            "temp_moy_min": temp_moy_min,
            "pluie_7j_mm": pluie_7j,
            "suggestions_meteo": list(meteo.suggestions or []),
        },
        a_semer=a_semer,
        a_planter=a_planter,
        a_recolter=a_recolter,
        conseils_personnalises=conseils,
    )


@router.get(
    "/habitat/estimation-roi",
    response_model=EstimationRoiHabitatResponse,
    responses=REPONSES_IA,
    summary="IA-4: estimation prix bien + ROI rénovation",
)
@gerer_exception_api
async def estimer_roi_habitat(
    surface_m2: float,
    code_postal: str | None = None,
    commune: str | None = None,
    budget_travaux: float = 0.0,
    type_local: str = "Maison",
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> EstimationRoiHabitatResponse:
    dvf = obtenir_service_dvf_habitat().obtenir_historique_marche(
        code_postal=code_postal,
        commune=commune,
        type_local=type_local,
        limite=180,
    )
    prix_m2 = float((dvf.get("resume") or {}).get("prix_m2_median") or 0.0)
    valeur_bien = round(max(0.0, surface_m2) * prix_m2, 2)

    estimation_service = _get_projets_maison_ai_service()
    estimation = await estimation_service.estimer_projet(
        projet_description=f"Rénovation {type_local} {surface_m2}m2 à {commune or code_postal or 'zone locale'}",
        surface_m2=surface_m2,
        type_maison="maison_2020",
        contraintes=["analyse ROI"],
    )

    budget_ia = float(getattr(estimation, "budget_total_max", 0.0) or 0.0)
    budget_reference = max(float(budget_travaux or 0.0), budget_ia)
    if budget_reference <= 0:
        budget_reference = round(surface_m2 * 180.0, 2)

    plus_value_estimee = round(min(budget_reference * 1.35, valeur_bien * 0.18), 2)
    roi = round(((plus_value_estimee - budget_reference) / max(budget_reference, 1.0)) * 100.0, 1)

    if roi >= 15:
        verdict = "favorable"
    elif roi >= 0:
        verdict = "equilibre"
    else:
        verdict = "defavorable"

    recommandations = [
        f"Prioriser les travaux à forte valeur perçue (cuisine, salle d'eau) pour un bien {type_local.lower()}.",
        "Comparer au moins 3 devis avant engagement pour sécuriser la marge de ROI.",
    ]
    if roi < 0:
        recommandations.append("Réduire le périmètre des travaux ou phaser le projet pour améliorer le ROI.")

    return EstimationRoiHabitatResponse(
        prix_m2_reference=round(prix_m2, 2),
        valeur_estimee_bien=valeur_bien,
        budget_travaux=round(budget_reference, 2),
        plus_value_estimee=plus_value_estimee,
        roi_pct=roi,
        verdict=verdict,
        recommandations=recommandations,
    )


@router.get(
    "/artisans/comparaison-devis",
    response_model=EstimationComparaisonDevisResponse,
    responses=REPONSES_IA,
    summary="IA-7: estimation devis + comparaison artisans",
)
@gerer_exception_api
async def comparer_devis_artisans(
    projet_id: int,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> EstimationComparaisonDevisResponse:
    tuples = _charger_devis_avec_artisans(projet_id)
    devis_lus: list[dict[str, Any]] = []

    montants = [float(d.montant_ttc or 0.0) for d, _ in tuples if d and d.montant_ttc is not None]
    mediane_montant = float(median(montants)) if montants else 0.0
    min_montant = min(montants) if montants else 0.0
    max_montant = max(montants) if montants else 0.0

    for devis, artisan in tuples:
        montant = float(getattr(devis, "montant_ttc", 0.0) or 0.0)
        note_artisan = float(getattr(artisan, "note", 3) or 3)
        delai = int(getattr(devis, "delai_travaux_jours", 30) or 30)
        ratio_prix = (mediane_montant / montant) if montant > 0 else 0.0
        score = round((ratio_prix * 50.0) + (note_artisan * 8.0) + max(0.0, 20.0 - (delai / 3.0)), 1)
        devis_lus.append(
            {
                "devis_id": devis.id,
                "artisan": {
                    "id": getattr(artisan, "id", None),
                    "nom": getattr(artisan, "nom", "Inconnu"),
                    "metier": getattr(artisan, "metier", None),
                    "note": note_artisan,
                },
                "montant_ttc": round(montant, 2),
                "delai_jours": delai,
                "statut": getattr(devis, "statut", "demande"),
                "score_ia": score,
            }
        )

    devis_tries = sorted(devis_lus, key=lambda d: d.get("score_ia", 0.0), reverse=True)
    meilleur = devis_tries[0] if devis_tries else {}

    return EstimationComparaisonDevisResponse(
        projet_id=projet_id,
        estimation_reference={
            "nb_devis": len(devis_lus),
            "montant_min": round(min_montant, 2),
            "montant_mediane": round(mediane_montant, 2),
            "montant_max": round(max_montant, 2),
        },
        devis_analyses=devis_tries,
        recommandation={
            "devis_recommande": meilleur,
            "strategie": "Comparer prix, délai et qualité artisan avant validation finale.",
        },
    )


# ═══════════════════════════════════════════════════════════
# P6 — SCORE ÉCOLOGIQUE RECETTE & ANOMALIES JARDIN
# ═══════════════════════════════════════════════════════════


@router.post(
    "/recette/score-ecologique",
    responses=REPONSES_IA,
    summary="Score écologique d'une recette (empreinte carbone, saisonnalité)",
)
@gerer_exception_api
async def score_ecologique_recette(
    body: dict,
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> dict:
    """Calcule le score écologique d'une recette basé sur saisonnalité et provenance."""
    from src.services.ia_avancee.service import get_ia_avancee_service

    service = get_ia_avancee_service()
    result = service.calculer_score_eco_responsable()
    if result is None:
        return {"score_global": None, "details": {}, "recommandations": []}
    return result.model_dump() if hasattr(result, "model_dump") else result


@router.get(
    "/jardin/anomalies",
    responses=REPONSES_IA,
    summary="Détection d'anomalies au jardin via IA",
)
@gerer_exception_api
async def detecter_anomalies_jardin(
    user: dict = Depends(require_auth),
    _rate: dict = Depends(verifier_limite_debit_ia),
) -> dict:
    """Analyse l'état du jardin et détecte les anomalies potentielles."""
    from src.services.maison.ia.jardin_anomalies_ia import get_jardin_anomalies_ia_service

    def _query():
        from src.core.models.jardin import Plante

        with executer_avec_session() as session:
            plantes_db = session.query(Plante).filter(Plante.actif.is_(True)).all()
            plantes = [
                {
                    "nom": p.nom,
                    "date_plantation": str(getattr(p, "date_plantation", "")),
                    "etat": getattr(p, "etat", "normal"),
                    "frequence_arrosage": getattr(p, "frequence_arrosage", ""),
                }
                for p in plantes_db
            ]

        service = get_jardin_anomalies_ia_service()
        from datetime import date as date_type
        mois_saisons = {1: "hiver", 2: "hiver", 3: "printemps", 4: "printemps",
                        5: "printemps", 6: "ete", 7: "ete", 8: "ete",
                        9: "automne", 10: "automne", 11: "automne", 12: "hiver"}
        saison = mois_saisons.get(date_type.today().month, "")
        result = service.detecter_anomalies(plantes=plantes, saison=saison)
        return result.model_dump()

    from src.api.utils import executer_async
    return await executer_async(_query)
