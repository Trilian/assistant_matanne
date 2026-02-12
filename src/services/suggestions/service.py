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
from typing import Any

from sqlalchemy.orm import Session

from src.core.ai import ClientIA, AnalyseurIA
from src.core.cache_multi import cached, obtenir_cache
from src.core.database import obtenir_contexte_db
from src.core.decorators import avec_session_db
from src.core.models import (
    Recette,
    HistoriqueRecette,
    ArticleInventaire,
    Planning,
    Repas,
    RecetteIngredient,
)

from .types import ProfilCulinaire, ContexteSuggestion, SuggestionRecette

logger = logging.getLogger(__name__)


class ServiceSuggestions:
    """
    Service de suggestions intelligentes basées sur l'historique.
    
    Analyse l'historique pour:
    - Détecter les préférences
    - Éviter la répétition
    - Suggérer selon la saison
    - Proposer des découvertes
    """
    
    def __init__(self):
        self.client_ia = ClientIA()
        self.analyseur = AnalyseurIA()
        self.cache = obtenir_cache()
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ANALYSE DU PROFIL
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    @avec_session_db
    def analyser_profil_culinaire(
        self,
        jours_historique: int = 90,
        session: Session = None
    ) -> ProfilCulinaire:
        """
        Analyse l'historique pour construire un profil culinaire.
        
        Args:
            jours_historique: Nombre de jours Ã  analyser
            session: Session DB
            
        Returns:
            Profil culinaire déduit
        """
        profil = ProfilCulinaire()
        date_limite = datetime.now() - timedelta(days=jours_historique)
        
        # Analyser l'historique des recettes
        historique = (
            session.query(HistoriqueRecette)
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
            recette = session.query(Recette).filter_by(id=h.recette_id).first()
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
            if hasattr(recette, 'ingredients'):
                for ri in recette.ingredients:
                    if ri.ingredient:
                        ingredients_count[ri.ingredient.nom] += 1
        
        # Construire le profil
        profil.categories_preferees = [
            cat for cat, _ in categories_count.most_common(5)
        ]
        
        profil.ingredients_frequents = [
            ing for ing, _ in ingredients_count.most_common(10)
        ]
        
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
        
        logger.info(f"Profil culinaire analysé: {len(profil.categories_preferees)} catégories préférées")
        return profil
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # CONTEXTE INTELLIGENT
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    @avec_session_db
    def construire_contexte(
        self,
        type_repas: str = "dîner",
        nb_personnes: int = 4,
        temps_minutes: int = 60,
        session: Session = None
    ) -> ContexteSuggestion:
        """
        Construit un contexte intelligent pour les suggestions.
        
        Inclut automatiquement:
        - Ingrédients disponibles en stock
        - Ingrédients Ã  consommer en priorité (péremption proche)
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
        articles = session.query(ArticleInventaire).filter(
            ArticleInventaire.quantite > 0
        ).all()
        
        maintenant = datetime.now()
        dans_5_jours = maintenant + timedelta(days=5)
        
        for article in articles:
            contexte.ingredients_disponibles.append(article.nom)
            
            # Ingrédients Ã  utiliser en priorité (péremption dans 5 jours)
            if article.date_peremption and article.date_peremption <= dans_5_jours:
                contexte.ingredients_a_utiliser.append(article.nom)
        
        logger.debug(f"Contexte: {len(contexte.ingredients_disponibles)} ingrédients disponibles, "
                    f"{len(contexte.ingredients_a_utiliser)} Ã  utiliser en priorité")
        
        return contexte
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # GÉNÉRATION DE SUGGESTIONS
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    @avec_session_db
    def suggerer_recettes(
        self,
        contexte: ContexteSuggestion | None = None,
        nb_suggestions: int = 5,
        inclure_decouvertes: bool = True,
        session: Session = None
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
            .options(
                selectinload(Recette.ingredients).selectinload(RecetteIngredient.ingredient)
            )
            .all()
        )
        
        if not recettes:
            return []
        
        suggestions = []
        
        for recette in recettes:
            score, raisons, tags = self._calculer_score_recette(
                recette, contexte, profil
            )
            
            if score > 0:
                # Déterminer ingrédients manquants
                manquants = self._trouver_ingredients_manquants(
                    recette, contexte.ingredients_disponibles
                )
                
                est_nouvelle = recette.id not in profil.jours_depuis_derniere_recette
                
                suggestions.append(SuggestionRecette(
                    recette_id=recette.id,
                    nom=recette.nom,
                    raison="; ".join(raisons[:2]),
                    score=score,
                    tags=tags,
                    temps_preparation=recette.temps_preparation or 0,
                    difficulte=recette.difficulte or "moyen",
                    ingredients_manquants=manquants[:3],
                    est_nouvelle=est_nouvelle,
                ))
        
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
        self,
        recette: Recette,
        contexte: ContexteSuggestion,
        profil: ProfilCulinaire
    ) -> tuple[float, list[str], list[str]]:
        """
        Calcule le score d'une recette selon le contexte et le profil.
        
        Returns:
            (score, raisons, tags)
        """
        score = 50.0  # Score de base
        raisons = []
        tags = []
        
        # Bonus catégorie préférée
        if recette.categorie in profil.categories_preferees:
            idx = profil.categories_preferees.index(recette.categorie)
            bonus = 20 - (idx * 3)
            score += bonus
            raisons.append(f"Catégorie préférée: {recette.categorie}")
            tags.append("favori")
        
        # Bonus temps adapté
        if recette.temps_preparation:
            if recette.temps_preparation <= contexte.temps_disponible_minutes:
                score += 15
                raisons.append("Temps adapté")
                tags.append("rapide")
            elif recette.temps_preparation > contexte.temps_disponible_minutes + 30:
                score -= 20  # Trop long
        
        # Bonus utilisation ingrédients Ã  consommer
        ingredients_recette = []
        if hasattr(recette, 'ingredients'):
            ingredients_recette = [
                ri.ingredient.nom.lower() 
                for ri in recette.ingredients 
                if ri.ingredient
            ]
        
        ingredients_prioritaires_utilises = sum(
            1 for ing in contexte.ingredients_a_utiliser
            if ing.lower() in [i.lower() for i in ingredients_recette]
        )
        if ingredients_prioritaires_utilises > 0:
            score += ingredients_prioritaires_utilises * 15
            raisons.append(f"Utilise {ingredients_prioritaires_utilises} ingrédient(s) Ã  consommer")
            tags.append("anti-gaspi")
        
        # Bonus ingrédients disponibles
        ingredients_disponibles_utilises = sum(
            1 for ing in contexte.ingredients_disponibles
            if ing.lower() in [i.lower() for i in ingredients_recette]
        )
        ratio_disponible = (
            ingredients_disponibles_utilises / len(ingredients_recette)
            if ingredients_recette else 0
        )
        if ratio_disponible > 0.7:
            score += 20
            raisons.append("Majorité des ingrédients en stock")
            tags.append("stock-ok")
        
        # Malus répétition récente
        if recette.id in profil.jours_depuis_derniere_recette:
            jours = profil.jours_depuis_derniere_recette[recette.id]
            if jours < 7:
                score -= 30
                raisons.append("Préparé récemment")
            elif jours < 14:
                score -= 15
        
        # Bonus découverte
        if recette.id not in profil.jours_depuis_derniere_recette:
            score += 10
            tags.append("découverte")
        
        # Bonus saison
        saison_tags = {
            "printemps": ["légumes verts", "asperge", "petit pois"],
            "été": ["tomate", "courgette", "aubergine", "salade"],
            "automne": ["champignon", "courge", "potiron"],
            "hiver": ["chou", "poireau", "carotte", "navet"],
        }
        if contexte.saison in saison_tags:
            for ing in ingredients_recette:
                if any(s in ing.lower() for s in saison_tags[contexte.saison]):
                    score += 10
                    tags.append("de-saison")
                    raisons.append("Ingrédients de saison")
                    break
        
        # Recette favorite
        if recette.id in profil.recettes_favorites:
            score += 5
            tags.append("classique")
        
        return max(0, score), raisons, list(set(tags))
    
    def _trouver_ingredients_manquants(
        self,
        recette: Recette,
        ingredients_disponibles: list[str]
    ) -> list[str]:
        """Trouve les ingrédients manquants pour une recette."""
        manquants = []
        
        if not hasattr(recette, 'ingredients'):
            return manquants
        
        disponibles_lower = [i.lower() for i in ingredients_disponibles]
        
        for ri in recette.ingredients:
            if ri.ingredient:
                nom = ri.ingredient.nom
                if nom.lower() not in disponibles_lower:
                    manquants.append(nom)
        
        return manquants
    
    def _mixer_suggestions(
        self,
        suggestions: list[SuggestionRecette],
        nb_total: int
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
            resultat.extend(reste[:nb_total - len(resultat)])
        
        return resultat[:nb_total]
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # SUGGESTIONS IA AVANCÉES
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    @avec_session_db
    def suggerer_avec_ia(
        self,
        requete_utilisateur: str,
        contexte: ContexteSuggestion | None = None,
        session: Session = None
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
{', '.join(contexte.ingredients_disponibles[:20]) if contexte.ingredients_disponibles else 'Non spécifié'}

INGRÉDIENTS Ã€ UTILISER EN PRIORITÉ (péremption proche):
{', '.join(contexte.ingredients_a_utiliser) if contexte.ingredients_a_utiliser else 'Aucun'}

PRÉFÉRENCES DÉTECTÉES:
- Catégories préférées: {', '.join(profil.categories_preferees[:3]) if profil.categories_preferees else 'Non déterminé'}
- Difficulté habituelle: {profil.difficulte_moyenne}
- Temps moyen: {profil.temps_moyen_minutes} minutes

Réponds avec 3 suggestions au format JSON:
[
  {{"nom": "...", "description": "...", "temps_minutes": X, "pourquoi": "..."}},
  ...
]
"""
        
        try:
            reponse = self.client_ia.generer(
                prompt=prompt,
                system="Tu es un chef cuisinier créatif qui fait des suggestions personnalisées.",
                temperature=0.7,
            )
            
            suggestions = self.analyseur.extraire_json(reponse)
            
            if isinstance(suggestions, list):
                return suggestions
            
        except Exception as e:
            logger.error(f"Erreur suggestion IA: {e}")
        
        return []


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FACTORY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


_suggestions_service: ServiceSuggestions | None = None


def obtenir_service_suggestions() -> ServiceSuggestions:
    """Factory pour le service de suggestions IA."""
    global _suggestions_service
    if _suggestions_service is None:
        _suggestions_service = ServiceSuggestions()
    return _suggestions_service


# Alias pour compatibilité
SuggestionsIAService = ServiceSuggestions
get_suggestions_ia_service = obtenir_service_suggestions


__all__ = [
    "ServiceSuggestions",
    "obtenir_service_suggestions",
    # Alias de compatibilité
    "SuggestionsIAService",
    "get_suggestions_ia_service",
]
