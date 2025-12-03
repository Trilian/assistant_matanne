from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class AIRecetteService:
    def __init__(self):
        mistral_api_key = os.getenv("MISTRAL_API_KEY")
        if not mistral_api_key:
            raise ValueError("MISTRAL_API_KEY non trouvée. Vérifie ton fichier .env.")
        self.client = MistralClient(api_key=mistral_api_key)
        self.model = "mistral-small"

    def générer_recettes(
            self,
            nombre: int = 3,
            type_plat: Optional[str] = None,
            saison: Optional[str] = None,
            ingrédients: Optional[List[str]] = None,
            version: str = "classique",
            temps_max: Optional[int] = None,
            équilibré: bool = False
    ) -> List[Dict]:
        """Génère des recettes avec Mistral en évitant les erreurs de format."""

        # Préparation des ingrédients pour le prompt
        ingrédients_str = ", ".join(ingrédients) if ingrédients else "aucun ingrédient spécifique"

        # Adaptation du prompt selon la version
        version_prompt = ""
        if version == "bébé":
            version_prompt = """
            - Ajoute une section 'adaptation_bébé' avec :
              1. Les étapes spécifiques pour bébé (ex: "À l'étape 3, prélever 100g et mixer finement")
              2. Les quantités adaptées pour un bébé
              3. Les précautions à prendre (ex: pas de sel, pas de miel avant 1 an)
            """
        elif version == "batch_cooking":
            version_prompt = """
            - Organise les étapes pour le batch cooking :
              1. Identifie les étapes parallélisables
              2. Estime le temps total optimisé
              3. Propose des quantités pour 4 portions
            """

        # Construction du prompt principal
        prompt = f"""
        Tu es un chef cuisinier expert. Génère {nombre} recettes de {type_plat or "plat principal"}
        {f"pour la saison {saison}" if saison else ""}
        {f"avec ces ingrédients : {ingrédients_str}" if ingrédients_str != "aucun ingrédient spécifique" else ""}
        {f"en moins de {temps_max} minutes" if temps_max else ""}
        {"équilibrées" if équilibré else ""}.

        {version_prompt}

        **Format de réponse strict (JSON valide uniquement) :**
        {{
            "recettes": [
                {{
                    "nom": "Nom de la recette",
                    "description": "Description courte et appétissante",
                    "type": "{type_plat or 'plat'}",
                    "saison": "{saison or 'toutes'}",
                    "temps_preparation": 15,
                    "temps_cuisson": 30,
                    "difficulté": "facile/moyenne/difficile",
                    "portions": 4,
                    "ingrédients": [
                        {{"nom": "carotte", "quantité": 200, "unité": "g"}}
                    ],
                    "étapes": [
                        "1. Éplucher et couper les carottes en rondelles",
                        "2. Faire revenir dans une poêle avec de l'huile d'olive"
                    ],
                    "tags": {{
                        "rapide": {str(équilibré).lower()},
                        "équilibré": {str(équilibré).lower()},
                        "végétarien": false
                    }},
                    "adaptation_bébé": {{
                        "étapes": ["Mixez 100g de la préparation pour bébé"],
                        "précautions": ["Pas de sel pour les bébés"]
                    }},
                    "batch_info": {{
                        "étapes_parallèles": ["Éplucher les légumes", "Préchauffer le four"],
                        "temps_optimisé": 45
                    }}
                }}
            ]
        }}
        """

        try:
            # Appel à l'API Mistral
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un chef cuisinier expert. Réponds EXCLUSIVEMENT en JSON valide sans commentaires."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"}  # Force le format JSON
            )

            # Parsing sécurisé de la réponse
            try:
                data = json.loads(response.choices[0].message.content)
                return data["recettes"]
            except json.JSONDecodeError as e:
                print(f"Erreur de parsing JSON: {e}")
                print(f"Réponse brute: {response.choices[0].message.content}")
                raise ValueError("La réponse de Mistral n'est pas un JSON valide")

        except Exception as e:
            print(f"Erreur avec l'API Mistral: {e}")
            raise ValueError(f"Erreur lors de la génération des recettes: {str(e)}")
