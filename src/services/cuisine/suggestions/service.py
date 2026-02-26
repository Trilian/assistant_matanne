"""
Service de suggestions IA avec historique.

Améliore les suggestions en utilisant:
- Historique des recettes consultées/préparées
- Préférences détectées automatiquement
- Saisons et disponibilité des ingrédients
- Retours utilisateur (likes/dislikes)
"""

import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from sqlalchemy.orm import Session, selectinload

from src.core.ai import AnalyseurIA, obtenir_client_ia
from src.core.decorators import avec_session_db
from src.core.exceptions import ErreurLimiteDebit
from src.core.models import (
    ArticleInventaire,
    HistoriqueRecette,
    Recette,
    RecetteIngredient,
)
from src.services.core.base import BaseAIService

from .types import ContexteSuggestion, ProfilCulinaire, SuggestionRecette

logger = logging.getLogger(__name__)


class ServiceSuggestions(BaseAIService):
    """
    Service de suggestions intelligentes basées sur l'historique.

    Hérite de BaseAIService pour bénéficier automatiquement de:
    - Rate limiting avec retry intelligent
    - Cache sémantique automatique
    - Circuit breaker (protection service externe)
    - Parsing JSON robuste
    - Gestion d'erreurs unifiée

    Analyse l'historique pour:
    - Détecter les préférences
    - Éviter la répétition
    - Suggérer selon la saison
    - Proposer des découvertes
    """

    def __init__(self, client=None):
        if client is None:
            client = obtenir_client_ia()
        super().__init__(
            client=client,
            cache_prefix="suggestions",
            default_temperature=0.7,
            service_name="suggestions",
        )

    # ═══════════════════════════════════════════════════════════
    # ANALYSE DU PROFIL
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def analyser_profil_culinaire(
        self, jours_historique: int = 90, session: Session = None
    ) -> ProfilCulinaire:
        """
        Analyse l'historique pour construire un profil culinaire.

        Args:
            jours_historique: Nombre de jours à analyser
            session: Session DB

        Returns:
            Profil culinaire déduit
        """
        profil = ProfilCulinaire()
        date_limite = datetime.now() - timedelta(days=jours_historique)

        # Analyser l'historique des recettes (eager load recette + ingredients)
        historique = (
            session.query(HistoriqueRecette)
            .options(
                selectinload(HistoriqueRecette.recette)
                .selectinload(Recette.ingredients)
                .selectinload(RecetteIngredient.ingredient)
            )
            .filter(HistoriqueRecette.date_cuisson >= date_limite)
            .all()
        )

        if not historique:
            return profil

        # Compteurs
        categories_count = Counter()
        ingredients_count = Counter()
        difficultes = []
        temps_list = []
        portions_list = []
        recettes_consultees = defaultdict(int)

        for h in historique:
            recette = h.recette
            if not recette:
                continue

            recettes_consultees[recette.id] += 1

            if recette.categorie:
                categories_count[recette.categorie] += 1

            if recette.difficulte:
                difficultes.append(recette.difficulte)

            if recette.temps_preparation:
                temps_list.append(recette.temps_preparation)

            if recette.portions:
                portions_list.append(recette.portions)

            # Compter les ingrédients
            for ri in recette.ingredients:
                if ri.ingredient:
                    ingredients_count[ri.ingredient.nom] += 1

        # Construire le profil
        profil.categories_preferees = [cat for cat, _ in categories_count.most_common(5)]

        profil.ingredients_frequents = [ing for ing, _ in ingredients_count.most_common(10)]

        if difficultes:
            profil.difficulte_moyenne = Counter(difficultes).most_common(1)[0][0]

        if temps_list:
            profil.temps_moyen_minutes = int(sum(temps_list) / len(temps_list))

        if portions_list:
            profil.nb_portions_habituel = int(sum(portions_list) / len(portions_list))

        # Recettes favorites (consultées 3+ fois)
        profil.recettes_favorites = [
            rid for rid, count in recettes_consultees.items() if count >= 3
        ]

        # Jours depuis dernière utilisation de chaque recette
        for rid in recettes_consultees.keys():
            dernier = (
                session.query(HistoriqueRecette)
                .filter_by(recette_id=rid)
                .order_by(HistoriqueRecette.date_cuisson.desc())
                .first()
            )
            if dernier:
                jours = (datetime.now().date() - dernier.date_cuisson).days
                profil.jours_depuis_derniere_recette[rid] = jours

        logger.info(
            f"Profil culinaire analysé: {len(profil.categories_preferees)} catégories préférées"
        )
        return profil

    # ═══════════════════════════════════════════════════════════
    # CONTEXTE INTELLIGENT
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def construire_contexte(
        self,
        type_repas: str = "dîner",
        nb_personnes: int = 4,
        temps_minutes: int = 60,
        session: Session = None,
    ) -> ContexteSuggestion:
        """
        Construit un contexte intelligent pour les suggestions.

        Inclut automatiquement:
        - Ingrédients disponibles en stock
        - Ingrédients à consommer en priorité (péremption proche)
        - Saison actuelle

        Args:
            type_repas: Type de repas
            nb_personnes: Nombre de personnes
            temps_minutes: Temps disponible
            session: Session DB

        Returns:
            Contexte enrichi
        """
        contexte = ContexteSuggestion(
            type_repas=type_repas,
            nb_personnes=nb_personnes,
            temps_disponible_minutes=temps_minutes,
        )

        # Déterminer la saison
        mois = datetime.now().month
        if mois in [3, 4, 5]:
            contexte.saison = "printemps"
        elif mois in [6, 7, 8]:
            contexte.saison = "été"
        elif mois in [9, 10, 11]:
            contexte.saison = "automne"
        else:
            contexte.saison = "hiver"

        # Récupérer le stock
        articles = session.query(ArticleInventaire).filter(ArticleInventaire.quantite > 0).all()

        maintenant = datetime.now()
        dans_5_jours = maintenant + timedelta(days=5)

        for article in articles:
            contexte.ingredients_disponibles.append(article.nom)

            # Ingrédients à utiliser en priorité (péremption dans 5 jours)
            if article.date_peremption and article.date_peremption <= dans_5_jours:
                contexte.ingredients_a_utiliser.append(article.nom)

        logger.debug(
            f"Contexte: {len(contexte.ingredients_disponibles)} ingrédients disponibles, "
            f"{len(contexte.ingredients_a_utiliser)} à utiliser en priorité"
        )

        return contexte

    # ═══════════════════════════════════════════════════════════
    # GÉNÉRATION DE SUGGESTIONS
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def suggerer_recettes(
        self,
        contexte: ContexteSuggestion | None = None,
        nb_suggestions: int = 5,
        inclure_decouvertes: bool = True,
        session: Session = None,
    ) -> list[SuggestionRecette]:
        """
        Génère des suggestions de recettes personnalisées.

        Args:
            contexte: Contexte de suggestion (auto-construit si None)
            nb_suggestions: Nombre de suggestions
            inclure_decouvertes: Inclure des recettes jamais préparées
            session: Session DB

        Returns:
            Liste de suggestions scorées
        """
        from sqlalchemy.orm import selectinload

        if contexte is None:
            contexte = self.construire_contexte(session=session)

        profil = self.analyser_profil_culinaire(session=session)

        # Récupérer toutes les recettes avec eager loading
        recettes = (
            session.query(Recette)
            .options(selectinload(Recette.ingredients).selectinload(RecetteIngredient.ingredient))
            .all()
        )

        if not recettes:
            return []

        suggestions = []

        for recette in recettes:
            score, raisons, tags = self._calculer_score_recette(recette, contexte, profil)

            if score > 0:
                # Déterminer ingrédients manquants
                manquants = self._trouver_ingredients_manquants(
                    recette, contexte.ingredients_disponibles
                )

                est_nouvelle = recette.id not in profil.jours_depuis_derniere_recette

                suggestions.append(
                    SuggestionRecette(
                        recette_id=recette.id,
                        nom=recette.nom,
                        raison="; ".join(raisons[:2]),
                        score=score,
                        tags=tags,
                        temps_preparation=recette.temps_preparation or 0,
                        difficulte=recette.difficulte or "moyen",
                        ingredients_manquants=manquants[:3],
                        est_nouvelle=est_nouvelle,
                    )
                )

        # Trier par score décroissant
        suggestions.sort(key=lambda x: x.score, reverse=True)

        # Assurer un mix de favoris et découvertes
        if inclure_decouvertes:
            suggestions = self._mixer_suggestions(suggestions, nb_suggestions)
        else:
            suggestions = suggestions[:nb_suggestions]

        logger.info(f"Généré {len(suggestions)} suggestions de recettes")
        return suggestions

    def _calculer_score_recette(
        self, recette: Recette, contexte: ContexteSuggestion, profil: ProfilCulinaire
    ) -> tuple[float, list[str], list[str]]:
        """
        Calcule le score d'une recette selon le contexte et le profil.

        Délègue au scoring unifié (scoring.py) puis ajoute les bonus
        contextuels spécifiques aux objets ORM.

        Returns:
            (score, raisons, tags)
        """
        from .scoring import calculate_recipe_score, generate_suggestion_reason

        # Convertir l'objet ORM en dict pour le scoring unifié
        ingredients_recette = []
        if hasattr(recette, "ingredients"):
            ingredients_recette = [ri.ingredient.nom for ri in recette.ingredients if ri.ingredient]

        recette_dict = {
            "id": recette.id,
            "nom": recette.nom,
            "categorie": recette.categorie,
            "temps_preparation": recette.temps_preparation or 0,
            "temps_cuisson": getattr(recette, "temps_cuisson", 0) or 0,
            "difficulte": recette.difficulte or "moyen",
            "ingredients": ingredients_recette,
            "est_vegetarien": getattr(recette, "est_vegetarien", False),
            "contient_gluten": getattr(recette, "contient_gluten", False),
        }

        contexte_dict = {
            "ingredients_disponibles": contexte.ingredients_disponibles,
            "ingredients_a_utiliser": contexte.ingredients_a_utiliser,
            "temps_disponible_minutes": contexte.temps_disponible_minutes,
            "contraintes": contexte.contraintes,
            "saison": contexte.saison,
        }

        profil_dict = {
            "categories_preferees": profil.categories_preferees,
            "difficulte_moyenne": profil.difficulte_moyenne,
            "temps_moyen_minutes": profil.temps_moyen_minutes,
        }

        historique_list = [
            {"recette_id": rid, "date": str(date)}
            for rid, date in profil.jours_depuis_derniere_recette.items()
        ]

        # Score unifié (0-100) via scoring.py
        score_base = calculate_recipe_score(
            recette_dict, contexte_dict, profil_dict, historique_list
        )

        # Bonus contextuels ORM (non disponibles dans le scoring dict-based)
        raisons = []
        tags = []

        # Raison générée par le scoring unifié
        raison_base = generate_suggestion_reason(recette_dict, contexte_dict)
        if raison_base:
            raisons.append(raison_base)

        # Bonus ingrédients en stock (ratio)
        ingredients_lower = [i.lower() for i in ingredients_recette]
        ingredients_disponibles_utilises = sum(
            1 for ing in contexte.ingredients_disponibles if ing.lower() in ingredients_lower
        )
        ratio_disponible = (
            ingredients_disponibles_utilises / len(ingredients_recette)
            if ingredients_recette
            else 0
        )
        if ratio_disponible > 0.7:
            score_base += 10
            raisons.append("Majorité des ingrédients en stock")
            tags.append("stock-ok")

        # Tags contextuels
        if recette.categorie in profil.categories_preferees:
            tags.append("favori")
        if (
            recette.temps_preparation
            and recette.temps_preparation <= contexte.temps_disponible_minutes
        ):
            tags.append("rapide")
        if any(
            ing.lower() in [i.lower() for i in contexte.ingredients_a_utiliser]
            for ing in ingredients_recette
        ):
            tags.append("anti-gaspi")
        if recette.id not in profil.jours_depuis_derniere_recette:
            tags.append("découverte")
        if recette.id in profil.recettes_favorites:
            tags.append("classique")

        # Bonus saison (tag)
        from .saisons import get_current_season, is_ingredient_in_season

        saison = contexte.saison or get_current_season()
        for ing in ingredients_recette:
            if is_ingredient_in_season(ing, saison):
                tags.append("de-saison")
                break

        return max(0, min(100, score_base)), raisons, list(set(tags))

    def _trouver_ingredients_manquants(
        self, recette: Recette, ingredients_disponibles: list[str]
    ) -> list[str]:
        """Trouve les ingrédients manquants pour une recette."""
        manquants = []

        if not hasattr(recette, "ingredients"):
            return manquants

        disponibles_lower = [i.lower() for i in ingredients_disponibles]

        for ri in recette.ingredients:
            if ri.ingredient:
                nom = ri.ingredient.nom
                if nom.lower() not in disponibles_lower:
                    manquants.append(nom)

        return manquants

    def _mixer_suggestions(
        self, suggestions: list[SuggestionRecette], nb_total: int
    ) -> list[SuggestionRecette]:
        """
        Mixe les suggestions pour inclure découvertes et favoris.

        Ratio: 60% favoris/adaptés, 40% découvertes
        """
        favoris = [s for s in suggestions if not s.est_nouvelle]
        decouvertes = [s for s in suggestions if s.est_nouvelle]

        nb_favoris = int(nb_total * 0.6)
        nb_decouvertes = nb_total - nb_favoris

        resultat = favoris[:nb_favoris] + decouvertes[:nb_decouvertes]

        # Compléter si pas assez
        if len(resultat) < nb_total:
            reste = [s for s in suggestions if s not in resultat]
            resultat.extend(reste[: nb_total - len(resultat)])

        return resultat[:nb_total]

    # ═══════════════════════════════════════════════════════════
    # SUGGESTIONS IA AVANCÉES
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def suggerer_avec_ia(
        self,
        requete_utilisateur: str,
        contexte: ContexteSuggestion | None = None,
        session: Session = None,
    ) -> list[dict]:
        """
        Utilise l'IA pour des suggestions plus créatives.

        Args:
            requete_utilisateur: Demande en langage naturel
            contexte: Contexte de suggestion
            session: Session DB

        Returns:
            Liste de suggestions IA
        """
        if contexte is None:
            contexte = self.construire_contexte(session=session)

        profil = self.analyser_profil_culinaire(session=session)

        # Construire le prompt
        prompt = f"""Tu es un assistant culinaire expert. Suggère des recettes adaptées.

DEMANDE UTILISATEUR: {requete_utilisateur}

CONTEXTE:
- Type de repas: {contexte.type_repas}
- Nombre de personnes: {contexte.nb_personnes}
- Temps disponible: {contexte.temps_disponible_minutes} minutes
- Saison: {contexte.saison}

INGRÉDIENTS DISPONIBLES:
{", ".join(contexte.ingredients_disponibles[:20]) if contexte.ingredients_disponibles else "Non spécifié"}

INGRÉDIENTS À UTILISER EN PRIORITÉ (péremption proche):
{", ".join(contexte.ingredients_a_utiliser) if contexte.ingredients_a_utiliser else "Aucun"}

PRÉFÉRENCES DÉTECTÉES:
- Catégories préférées: {", ".join(profil.categories_preferees[:3]) if profil.categories_preferees else "Non déterminé"}
- Difficulté habituelle: {profil.difficulte_moyenne}
- Temps moyen: {profil.temps_moyen_minutes} minutes

Réponds avec 3 suggestions au format JSON:
[
  {{"nom": "...", "description": "...", "temps_minutes": X, "pourquoi": "..."}},
  ...
]
"""

        try:
            # ✅ Rate limiting, cache & circuit breaker automatiques via BaseAIService
            reponse = self.call_with_cache_sync(
                prompt=prompt,
                system_prompt="Tu es un chef cuisinier créatif qui fait des suggestions personnalisées.",
                temperature=0.7,
                category="suggestions_ia",
            )

            if not reponse:
                return []

            suggestions = AnalyseurIA().extraire_json(reponse)

            if isinstance(suggestions, list):
                return suggestions

        except ErreurLimiteDebit:
            logger.warning("⏳ Quota IA atteint pour suggestions")
            return []
        except Exception as e:
            logger.error(f"Erreur suggestion IA: {e}")

        return []


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


from src.services.core.registry import service_factory


@service_factory("suggestions", tags={"cuisine", "ia"})
def obtenir_service_suggestions() -> ServiceSuggestions:
    """Factory pour le service de suggestions IA (thread-safe via registre)."""
    return ServiceSuggestions()


def get_suggestions_service() -> ServiceSuggestions:
    """Factory for suggestions service (English alias)."""
    return obtenir_service_suggestions()


__all__ = [
    "ServiceSuggestions",
    "obtenir_service_suggestions",
    "get_suggestions_service",
]
