"""
Agent IA - Wrapper hautement intégré pour interactions IA
Fournit une interface simplifiée pour les modules
"""

import logging
from typing import Any, Optional

from .ai.client import ClientIA

logger = logging.getLogger(__name__)


class AgentIA:
    """
    Agent IA - Interface simplifiée pour interactions avec l'IA
    Permet aux modules de dialoguer avec Mistral sans gérer ClientIA directement
    """

    def __init__(self):
        """Initialise l'agent avec un client IA"""
        try:
            self.client = ClientIA()
            self.contexte = {}
            logger.info("[OK] AgentIA initialisé")
        except Exception as e:
            logger.error(f"[ERROR] Erreur lors de l'initialisation d'AgentIA: {e}")
            self.client = None
            self.contexte = {}

    async def analyser(
        self,
        prompt: str,
        contexte: Optional[dict] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Analyse un prompt avec l'IA
        
        Args:
            prompt: Le prompt/question à analyser
            contexte: Contexte supplémentaire (données utilisateur, etc.)
            temperature: Température de réponse (0-1)
            
        Returns:
            Réponse texte de l'IA
        """
        if not self.client:
            logger.warning("[ERROR] ClientIA non disponible, retournant réponse par défaut")
            return "L'IA n'est pas disponible pour le moment."

        try:
            # Enrichir le prompt avec le contexte
            if contexte:
                prompt_enrichi = f"{prompt}\n\nContexte: {contexte}"
            else:
                prompt_enrichi = prompt

            # Appeler l'IA
            reponse = await self.client.appeler(
                prompt=prompt_enrichi,
                temperature=temperature,
            )

            return reponse

        except Exception as e:
            logger.error(f"[ERROR] Erreur lors de l'appel IA: {e}")
            return f"Erreur lors du traitement: {str(e)}"

    async def generer_analyse(
        self,
        donnees: dict,
        type_analyse: str,
    ) -> str:
        """
        Génère une analyse spécifique d'un type de données
        
        Args:
            donnees: Données à analyser
            type_analyse: Type d'analyse ('bien_etre', 'cuisine', 'budget', etc.)
            
        Returns:
            Analyse texte générée
        """
        prompts = {
            "bien_etre": f"Analyse le bien-être familial: {donnees}. Fournis des conseils pratiques.",
            "cuisine": f"Analyse ces recettes et repas: {donnees}. Suggère des améliorations.",
            "budget": f"Analyse cet historique de dépenses: {donnees}. Identifie les tendances.",
            "jardin": f"Analyse cet entretien du jardin: {donnees}. Suggère des améliorations.",
            "routines": f"Analyse ces routines familiales: {donnees}. Suggère des optimisations.",
        }

        prompt = prompts.get(type_analyse, f"Analyse ceci: {donnees}")
        return await self.analyser(prompt)

    def ajouter_contexte(self, cle: str, valeur: Any) -> None:
        """Ajoute une information au contexte de l'agent"""
        self.contexte[cle] = valeur

    def obtenir_contexte(self, cle: str) -> Any:
        """Récupère une information du contexte"""
        return self.contexte.get(cle)

    def effacer_contexte(self) -> None:
        """Efface tout le contexte"""
        self.contexte = {}
