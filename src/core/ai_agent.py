"""
Agent IA central - Version Mistral AI pour Streamlit Cloud
"""
import httpx
import json
import streamlit as st
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class AIRequest(BaseModel):
    """Requête vers l'agent IA"""
    prompt: str
    context: Optional[Dict[str, Any]] = None
    max_tokens: int = Field(default=500, gt=0, le=2000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    system_prompt: Optional[str] = None

class AIResponse(BaseModel):
    """Réponse de l'agent IA"""
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

class AgentIA:
    """
    Agent IA central utilisant Mistral AI
    Compatible Streamlit Cloud
    """

    def __init__(self):
        # Récupération de la clé API depuis les secrets
        try:
            self.api_key = st.secrets["mistral"]["api_key"]
            self.model = "mistral-small"  # Modèle économique et performant
            self.base_url = "https://api.mistral.ai/v1"
            self.client = httpx.AsyncClient(timeout=30.0)
            logger.info("✅ Agent IA Mistral initialisé")
        except KeyError:
            logger.error("❌ Clé API Mistral manquante dans les secrets")
            raise ValueError(
                "Clé API Mistral manquante.\n"
                "Ajoute dans les secrets Streamlit :\n"
                "[mistral]\n"
                'api_key = "ta_cle_api"'
            )

    async def _call_mistral(
            self,
            prompt: str,
            system_prompt: str = "",
            temperature: float = 0.7,
            max_tokens: int = 500
    ) -> str:
        """Appel API Mistral"""
        try:
            messages = []

            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            messages.append({
                "role": "user",
                "content": prompt
            })

            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )

            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

        except httpx.HTTPError as e:
            logger.error(f"Erreur Mistral API: {e}")
            return f"[IA indisponible] Erreur : {str(e)}"
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            return "[IA indisponible] Erreur interne"

    # ===================================
    # 🍲 CUISINE - Suggestions recettes
    # ===================================

    async def suggerer_recettes(
            self,
            inventaire: List[Dict],
            preferences: Optional[List[str]] = None,
            nb_suggestions: int = 3
    ) -> List[Dict]:
        """Suggère des recettes basées sur l'inventaire"""
        items_text = "\n".join([
            f"- {item['nom']}: {item['quantite']} {item['unite']}"
            for item in inventaire
        ])

        pref_text = f"\nPréférences: {', '.join(preferences)}" if preferences else ""

        system_prompt = (
            f"Tu es un chef cuisinier expert. "
            f"Suggère {nb_suggestions} recettes RÉALISABLES avec les ingrédients disponibles.\n"
            f"Réponds UNIQUEMENT en JSON valide (sans markdown) :\n"
            f"[\n"
            f'  {{"nom": "Nom", "ingredients": ["ing1"], "faisabilite": 85, '
            f'"raison": "Explication", "temps_preparation": 30}}\n'
            f"]"
        )

        prompt = f"Inventaire :\n{items_text}{pref_text}\n\nSuggère {nb_suggestions} recettes."

        response = await self._call_mistral(prompt, system_prompt, temperature=0.8)

        try:
            # Nettoyer la réponse
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            suggestions = json.loads(cleaned.strip())
            return suggestions[:nb_suggestions]

        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON : {e}")
            return [{
                "nom": "Erreur parsing",
                "ingredients": [item["nom"] for item in inventaire[:3]],
                "faisabilite": 0,
                "raison": "Impossible de parser la réponse IA",
                "temps_preparation": 0
            }]

    async def detecter_gaspillage(self, inventaire: List[Dict]) -> Dict:
        """Détecte les items à risque"""
        items_faibles = [i for i in inventaire if i.get("quantite", 0) < 2]

        if not items_faibles:
            return {
                "statut": "OK",
                "message": "Aucun risque détecté",
                "suggestions": []
            }

        items_text = ", ".join([item["nom"] for item in items_faibles])

        system_prompt = (
            "Tu es un expert anti-gaspillage. "
            "Suggère des recettes RAPIDES. "
            'Format JSON: {"recettes_urgentes": ["recette1"], "conseil": "conseil"}'
        )

        prompt = f"Items à utiliser : {items_text}"
        response = await self._call_mistral(prompt, system_prompt)

        try:
            result = json.loads(response.strip().replace("```json", "").replace("```", ""))
            result["statut"] = "ATTENTION"
            result["items"] = items_text
            return result
        except:
            return {
                "statut": "ATTENTION",
                "items": items_text,
                "recettes_urgentes": [f"Utiliser {items_text} rapidement"],
                "conseil": "À consommer rapidement"
            }

    # ===================================
    # 👶 FAMILLE - Conseils
    # ===================================

    async def conseiller_developpement(
            self,
            age_mois: int,
            contexte: Optional[Dict] = None
    ) -> Dict:
        """Conseils développement selon l'âge"""
        system_prompt = (
            f"Tu es un pédiatre expert. "
            f"Donne des conseils pour un bébé de {age_mois} mois. "
            'Format JSON: {"conseils": ["c1"], "activites": ["a1"], "alertes": []}'
        )

        ctx_text = f"\nContexte: {json.dumps(contexte)}" if contexte else ""
        prompt = f"Bébé de {age_mois} mois.{ctx_text}\nConseils ?"

        response = await self._call_mistral(prompt, system_prompt, temperature=0.5)

        try:
            return json.loads(response.strip().replace("```json", "").replace("```", ""))
        except:
            return {
                "conseils": ["Consulter un pédiatre"],
                "activites": ["Adaptées à l'âge"],
                "alertes": []
            }

    # ===================================
    # 💬 CHAT - Interface conversationnelle
    # ===================================

    async def chat(
            self,
            message: str,
            historique: List[Dict],
            contexte: Optional[Dict] = None
    ) -> str:
        """Interface conversationnelle"""
        hist_text = "\n".join([
            f"{h['role']}: {h['content']}"
            for h in historique[-5:]
        ])

        ctx_text = f"\n\nContexte:\n{json.dumps(contexte, indent=2)}" if contexte else ""

        system_prompt = (
            "Tu es l'assistant familial MaTanne. "
            "Tu aides avec : Cuisine, Famille, Maison, Planning. "
            f"Réponds de manière concise et actionnable.{ctx_text}"
        )

        prompt = f"Historique:\n{hist_text}\n\nUtilisateur: {message}"

        return await self._call_mistral(prompt, system_prompt, temperature=0.7)