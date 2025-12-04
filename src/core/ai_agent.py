"""
Agent IA - Version Mistral AI pour Streamlit Cloud
"""
import httpx
import json
import streamlit as st
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AgentIA:
    """Agent IA central utilisant Mistral AI"""

    def __init__(self):
        """Initialise l'agent avec la clé API depuis les secrets"""
        try:
            self.api_key = st.secrets["mistral"]["api_key"]
            self.model = st.secrets.get("mistral", {}).get("model", "mistral-small")
            self.base_url = "https://api.mistral.ai/v1"
            self.timeout = 30
            logger.info("✅ Agent IA Mistral initialisé")
        except KeyError:
            error_msg = "Clé API Mistral manquante dans les secrets"
            logger.error(error_msg)
            raise ValueError(
                f"{error_msg}\n"
                "Ajoute dans les secrets Streamlit:\n"
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
        """Appel API Mistral avec gestion d'erreurs"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
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

                response = await client.post(
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
            return f"[IA indisponible] Erreur HTTP: {str(e)}"
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            return f"[IA indisponible] Erreur: {str(e)}"

    # ===================================
    # MÉTHODES MÉTIER
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
            "Tu es un chef cuisinier expert. "
            f"Suggère {nb_suggestions} recettes RÉALISABLES avec les ingrédients disponibles.\n"
            "Réponds UNIQUEMENT en JSON valide :\n"
            "[\n"
            '  {"nom": "Nom", "ingredients": ["ing1"], "faisabilite": 85, '
            '"raison": "Explication", "temps_preparation": 30}\n'
            "]"
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

        except json.JSONDecodeError:
            logger.error("Erreur parsing JSON suggestions")
            return [{
                "nom": "Erreur parsing",
                "ingredients": [],
                "faisabilite": 0,
                "raison": "Impossible de parser la réponse IA"
            }]

    async def detecter_gaspillage(self, inventaire: List[Dict]) -> Dict:
        """Détecte les items à risque de gaspillage"""
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

        prompt = f"Items à utiliser rapidement : {items_text}"
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

    async def optimiser_courses(
            self,
            inventaire: List[Dict],
            recettes_prevues: List[str]
    ) -> Dict:
        """Optimise la liste de courses"""
        inv_text = ", ".join([f"{i['nom']} ({i['quantite']} {i['unite']})" for i in inventaire])
        recettes_text = ", ".join(recettes_prevues)

        system_prompt = (
            "Tu es un expert en optimisation de courses. "
            'Format JSON: {"par_rayon": {"Fruits": ["pomme"]}, "budget_estime": 50}'
        )

        prompt = f"Inventaire: {inv_text}\nRecettes prévues: {recettes_text}\nOptimise les courses."
        response = await self._call_mistral(prompt, system_prompt)

        try:
            return json.loads(response.strip().replace("```json", "").replace("```", ""))
        except:
            return {
                "par_rayon": {"Courses": ["Articles nécessaires"]},
                "budget_estime": 0
            }

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
            f"Réponds de manière concise.{ctx_text}"
        )

        prompt = f"Historique:\n{hist_text}\n\nUtilisateur: {message}"

        return await self._call_mistral(prompt, system_prompt, temperature=0.7)