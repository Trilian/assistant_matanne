"""Fonctions cuisine/repas extraites du service innovations."""

from __future__ import annotations

import logging
import re
from datetime import UTC, date, datetime, timedelta
from typing import Any

from src.core.db import obtenir_contexte_db
from src.core.decorators import avec_cache, avec_gestion_erreurs

from .types import (
    BatchCookingIntelligentResponse,
    BlocPlanificationAuto,
    CarteMagazineTablette,
    ComparateurPrixAutomatiqueResponse,
    EtapeBatchIntelligente,
    ModeTabletteMagazineResponse,
    ParcoursOptimiseResponse,
    PatternsAlimentairesResponse,
    PlanificationHebdoCompleteResponse,
    PrixIngredientCompare,
    SaisonnaliteIntelligenteResponse,
    SuggestionRepasSoirResponse,
)

logger = logging.getLogger(__name__)


def suggerer_repas_ce_soir(
    self,
    temps_disponible_min: int = 30,
    humeur: str = "rapide",
) -> SuggestionRepasSoirResponse | None:
    """P9-01 : suggère un repas du soir contextuel en une action."""
    humeur_safe = _sanitiser(humeur, 50)
    candidates = service._recettes_rapides(temps_disponible_min)
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

def analyser_patterns_alimentaires(
    self,
    periode_jours: int = 90,
) -> PatternsAlimentairesResponse | None:
    """P9-02 : analyse les patterns alimentaires récents."""
    top_recettes, score_diversite = service._patterns_recettes(periode_jours)
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

def appliquer_saisonnalite_intelligente(service) -> SaisonnaliteIntelligenteResponse | None:
    """P9-11 : produit des adaptations transverses selon la saison."""
    saison = service._saison_courante()
    recettes = service._recettes_de_saison(saison)
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

def generer_planification_hebdo_complete(service, user_id: str | None = None) -> PlanificationHebdoCompleteResponse | None:
    """S22 IN9 : génère planning repas + courses + tâches maison + jardin en un seul bloc."""
    semaine_debut = service._prochaine_semaine_lundi()
    semaine_fin = semaine_debut + timedelta(days=6)

    repas = service._proposer_repas_semaine(semaine_debut=semaine_debut, limite=7)
    courses = service._proposer_courses_depuis_repas(repas)
    taches_maison = service._proposer_taches_maison_hebdo(limite=5)
    taches_jardin = service._proposer_taches_jardin_hebdo(semaine_fin=semaine_fin, limite=4)

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

def proposer_batch_cooking_intelligent(service, user_id: str | None = None) -> BatchCookingIntelligentResponse | None:
    """S22 IN13 : propose un plan batch cooking cohérent avec le planning de semaine."""
    recettes = service._recettes_batch_cibles(limite=4)
    if not recettes:
        recettes = [
            "Base legumes rotis", "Poulet effiloche", "Riz complet", "Compote sans sucre ajoute",
        ]

    date_session = service._prochaine_date_batch()
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

def obtenir_mode_tablette_magazine(service) -> ModeTabletteMagazineResponse | None:
    """S22 IN7 : fournit une vue magazine condensée pour écran tablette."""
    score_bien_etre = service.calculer_score_bien_etre() or ScoreBienEtreResponse(score_global=0.0)
    insights = service.generer_insights_quotidiens(limite=2) or InsightsQuotidiensResponse()
    meteo = service.analyser_meteo_contextuelle() or MeteoContextuelleResponse()

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

def analyser_comparateur_prix_automatique(
    self,
    top_n: int = 20,
) -> ComparateurPrixAutomatiqueResponse | None:
    """S23 IN15 : compare les prix des ingrédients fréquents et détecte les soldes."""
    limite = max(1, min(20, top_n))

    from sqlalchemy import func

    with obtenir_contexte_db() as session:
        from src.core.models.courses import ArticleCourses
        from src.core.models.inventaire import ArticleInventaire
        from src.core.models.recettes import Ingredient

        top_ingredients = (
            session.query(
                Ingredient.nom,
                func.count(ArticleCourses.id).label("frequence"),
            )
            .join(ArticleCourses, ArticleCourses.ingredient_id == Ingredient.id)
            .group_by(Ingredient.nom)
            .order_by(func.count(ArticleCourses.id).desc())
            .limit(limite)
            .all()
        )

        prix_historiques_rows = (
            session.query(
                Ingredient.nom,
                func.avg(ArticleInventaire.prix_unitaire).label("prix_moyen"),
            )
            .join(ArticleInventaire, ArticleInventaire.ingredient_id == Ingredient.id)
            .filter(ArticleInventaire.prix_unitaire.isnot(None))
            .group_by(Ingredient.nom)
            .all()
        )

    prix_historiques = {
        str(row[0]).lower(): float(row[1])
        for row in prix_historiques_rows
        if row and row[0] and row[1] is not None
    }

    ingredients: list[PrixIngredientCompare] = []
    alertes: list[str] = []

    for nom, frequence in top_ingredients:
        nom_clean = str(nom)
        prix_historique = prix_historiques.get(nom_clean.lower())
        prix_marche, source = service._scraper_prix_marche_ingredient(nom_clean)

        variation_pct: float | None = None
        alerte_soldes = False
        if prix_historique and prix_marche and prix_historique > 0:
            variation_pct = round(((prix_marche - prix_historique) / prix_historique) * 100.0, 1)
            alerte_soldes = variation_pct <= -10.0
            if alerte_soldes:
                alertes.append(
                    f"{nom_clean}: baisse détectée ({abs(variation_pct):.1f}% vs historique)"
                )

        ingredients.append(
            PrixIngredientCompare(
                ingredient=nom_clean,
                frequence_utilisation=int(frequence or 0),
                prix_historique_moyen_eur=round(prix_historique, 2) if prix_historique else None,
                prix_marche_eur=round(prix_marche, 2) if prix_marche else None,
                source_prix=source,
                variation_pct=variation_pct,
                alerte_soldes=alerte_soldes,
            )
        )

    return ComparateurPrixAutomatiqueResponse(
        date_reference=date.today().isoformat(),
        nb_ingredients_analyses=len(ingredients),
        ingredients=ingredients,
        nb_alertes=len(alertes),
        alertes=alertes,
    )

    def optimiser_parcours_magasin(
        self, liste_id: int | None = None
    ) -> ParcoursOptimiseResponse | None:
        """Optimise le parcours magasin en regroupant les articles par rayon."""
        articles = service._collecter_articles_courses(liste_id)
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

        return service.call_with_parsing_sync(
            prompt=prompt,
            response_model=ParcoursOptimiseResponse,
            system_prompt="Tu es un expert en optimisation de parcours en supermarché.",
        )

def _recettes_rapides(service, temps_disponible_min: int) -> list[dict[str, Any]]:
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

def _patterns_recettes(service, periode_jours: int) -> tuple[list[str], float]:
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

def _score_recettes_eco(service) -> float:
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

def _saison_courante(service) -> str:
    """Détermine la saison courante."""
    mois = date.today().month
    if mois in (12, 1, 2):
        return "hiver"
    if mois in (3, 4, 5):
        return "printemps"
    if mois in (6, 7, 8):
        return "été"
    return "automne"

def _recettes_de_saison(service, saison: str) -> list[str]:
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

def _jours_depuis_repas_poisson(service) -> int:
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

def _collecter_articles_courses(service, liste_id: int | None = None) -> list[str]:
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

def _prochaine_semaine_lundi(service) -> date:
    """Retourne la date du prochain lundi (semaine cible)."""
    today = date.today()
    delta = (7 - today.weekday()) % 7
    if delta == 0:
        delta = 7
    return today + timedelta(days=delta)

def _proposer_repas_semaine(service, semaine_debut: date, limite: int = 7) -> list[str]:
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

def _proposer_courses_depuis_repas(service, repas: list[str]) -> list[str]:
    """Crée une liste de courses simple basée sur les repas prévus."""
    base = ["fruits de saison", "legumes frais", "yaourts nature", "oeufs", "riz", "huile d'olive"]
    if any("poisson" in r.lower() for r in repas):
        base.append("poisson frais")
    if any("curry" in r.lower() for r in repas):
        base.append("lait de coco")
    return base[:10]

def _recettes_batch_cibles(service, limite: int = 4) -> list[str]:
    """Extrait les recettes les plus pertinentes pour une session batch."""
    try:
        with obtenir_contexte_db() as session:
            from src.core.models import Repas, Recette

            start = service._prochaine_semaine_lundi()
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

def _prochaine_date_batch(service) -> date:
    """Détermine la prochaine date optimale de batch cooking."""
    fallback = service._prochaine_semaine_lundi() - timedelta(days=1)
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

def _scraper_prix_marche_ingredient(service, nom_ingredient: str) -> tuple[float | None, str]:
    """Scrape un prix indicatif d'un ingrédient via OpenFoodFacts (best-effort)."""
    try:
        import httpx

        with httpx.Client(timeout=1.2) as client:
            response = client.get(
                "https://world.openfoodfacts.org/cgi/search.pl",
                params={
                    "action": "process",
                    "search_terms": nom_ingredient,
                    "json": 1,
                    "page_size": 6,
                    "fields": "product_name,price",
                },
            )
            response.raise_for_status()
            payload = response.json()

        prix_detectes: list[float] = []
        for produit in payload.get("products", []):
            prix_brut = str(produit.get("price") or "").strip()
            prix = service._extraire_prix_float(prix_brut)
            if prix is not None and prix > 0:
                prix_detectes.append(prix)

        if prix_detectes:
            prix_detectes.sort()
            mediane = prix_detectes[len(prix_detectes) // 2]
            return float(mediane), "openfoodfacts"
    except Exception:
        logger.debug("Scraping prix indisponible pour %s", nom_ingredient, exc_info=True)

    return None, "historique"

def _extraire_prix_float(service, valeur: str) -> float | None:
    """Extrait un montant numérique depuis une chaîne de prix libre."""
    if not valeur:
        return None
    normalisee = valeur.replace(",", ".")
    match = re.search(r"(\d+(?:\.\d{1,2})?)", normalisee)
    if not match:
        return None
    try:
        return float(match.group(1))
    except (TypeError, ValueError):
        return None
