"""
Client IA Unifié - Mistral AI
"""

import asyncio
import logging
from typing import Any, Optional

import httpx

from ..config import obtenir_parametres
from ..errors import ErreurLimiteDebit, ErreurServiceIA
from .cache import CacheIA

logger = logging.getLogger(__name__)


class ClientIA:
    """
    Client IA unifié pour Mistral

    Fonctionnalités:
    - Appels API avec retry automatique
    - Cache intelligent
    - Rate limiting
    - Gestion d'erreurs robuste
    """

    def __init__(self):
        """Initialise le client - lazy loading de la config"""
        # Ne pas charger la config ici - elle sera chargée lors du premier appel
        # Cela permet à Streamlit Cloud de charger st.secrets correctement
        self._config_loaded = False
        self.cle_api = None
        self.modele = None
        self.url_base = None
        self.timeout = None

    def _ensure_config_loaded(self):
        """Charge la config au moment du premier accès (lazy loading)
        
        En Streamlit Cloud, on retente à chaque appel car st.secrets n'est
        disponible que lors des interactions utilisateur.
        """
        # Déterminer si on est en Streamlit Cloud
        import os
        is_cloud = os.getenv("SF_PARTNER") == "streamlit"
        
        # En Cloud, toujours retenter. Localement, charger une fois
        if self._config_loaded and not is_cloud:
            return
        
        # Si on a déjà une config valide et pas en cloud, la conserver
        if self._config_loaded and self.cle_api:
            return

        try:
            # Force reload de la config pour Streamlit Cloud
            parametres = obtenir_parametres()
            self.cle_api = parametres.MISTRAL_API_KEY
            self.modele = parametres.MISTRAL_MODEL
            self.url_base = parametres.MISTRAL_BASE_URL
            self.timeout = parametres.MISTRAL_TIMEOUT
            self._config_loaded = True

            logger.info(f"[OK] ClientIA initialisé (modèle: {self.modele})")

        except ValueError as e:
            logger.error(f"[ERROR] Configuration IA manquante: Clé API Mistral non configurée")
            # NE PAS marquer comme loaded en cas d'erreur
            # Cela permet une tentative lors du prochain appel (quand st.secrets sera prêt)
            self.cle_api = None
            self.modele = None
            self.url_base = None
            self.timeout = None
            raise  # Re-raise pour que l'erreur remonte

    # ═══════════════════════════════════════════════════════════
    # APPEL API PRINCIPAL
    # ═══════════════════════════════════════════════════════════

    async def appeler(
        self,
        prompt: str,
        prompt_systeme: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        utiliser_cache: bool = True,
        max_tentatives: int = 3,
    ) -> str:
        """
        Appel API avec cache et retry

        Args:
            prompt: Prompt utilisateur
            prompt_systeme: Instructions système
            temperature: Température (0-2)
            max_tokens: Tokens max
            utiliser_cache: Utiliser le cache
            max_tentatives: Nombre de tentatives

        Returns:
            Réponse de l'IA

        Raises:
            ErreurServiceIA: Si erreur API
            ErreurLimiteDebit: Si rate limit dépassé
        """
        # Charger la config au moment du premier appel (lazy loading)
        self._ensure_config_loaded()

        # Vérifier rate limit
        from ..cache import LimiteDebit

        peut_appeler, message_erreur = LimiteDebit.peut_appeler()
        if not peut_appeler:
            raise ErreurLimiteDebit(message_erreur, message_utilisateur=message_erreur)

        # Vérifier cache
        if utiliser_cache:
            cache = CacheIA.obtenir(
                prompt=prompt, systeme=prompt_systeme, temperature=temperature, modele=self.modele
            )

            if cache:
                logger.debug(f"Cache HIT: {prompt[:50]}...")
                return cache

        # Appel API avec retry
        for tentative in range(max_tentatives):
            try:
                reponse = await self._effectuer_appel(
                    prompt=prompt,
                    prompt_systeme=prompt_systeme,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                # Enregistrer appel
                LimiteDebit.enregistrer_appel()

                # Cacher résultat
                if utiliser_cache:
                    CacheIA.definir(
                        prompt=prompt,
                        reponse=reponse,
                        systeme=prompt_systeme,
                        temperature=temperature,
                        modele=self.modele,
                    )

                return reponse

            except httpx.HTTPError as e:
                if tentative == max_tentatives - 1:
                    logger.error(f"[ERROR] Erreur API après {max_tentatives} tentatives: {e}")
                    raise ErreurServiceIA(
                        f"Erreur API Mistral: {str(e)}",
                        message_utilisateur="L'IA est temporairement indisponible",
                    ) from e

                # Attente exponentielle
                temps_attente = 2**tentative
                logger.warning(f"Tentative {tentative + 1}/{max_tentatives} après {temps_attente}s")
                await asyncio.sleep(temps_attente)

            except Exception as e:
                logger.error(f"[ERROR] Erreur inattendue: {e}")
                raise ErreurServiceIA(
                    f"Erreur inattendue: {str(e)}", message_utilisateur="Erreur lors de l'appel IA"
                ) from e

        # Ne devrait jamais arriver ici
        raise ErreurServiceIA("Échec après toutes les tentatives")

    async def _effectuer_appel(
        self, prompt: str, prompt_systeme: str, temperature: float, max_tokens: int
    ) -> str:
        """Effectue l'appel API réel"""
        # S'assurer que la config est chargée
        self._ensure_config_loaded()

        # Vérifier que la configuration minimale est présente
        if not self.cle_api:
            raise ErreurServiceIA(
                "Clé API Mistral non configurée",
                message_utilisateur="La clé API Mistral n'est pas configurée. Veuillez ajouter MISTRAL_API_KEY.",
            )

        if not self.url_base:
            raise ErreurServiceIA(
                "URL de base API Mistral non configurée",
                message_utilisateur="La configuration Mistral est incomplète.",
            )

        messages = []

        if prompt_systeme:
            messages.append({"role": "system", "content": prompt_systeme})

        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            reponse = await client.post(
                f"{self.url_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.cle_api}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.modele,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )

            reponse.raise_for_status()
            resultat = reponse.json()

            # Vérifier que la réponse contient au moins un choix
            if not resultat.get("choices") or len(resultat["choices"]) == 0:
                raise ErreurServiceIA(
                    "Réponse IA invalide: pas de contenu", 
                    message_utilisateur="Service IA retourné une réponse vide"
                )

            contenu = resultat["choices"][0]["message"]["content"]
            logger.info(f"[OK] Réponse reçue ({len(contenu)} caractères)")

            return contenu

    # ═══════════════════════════════════════════════════════════
    # APPEL VISION (OCR)
    # ═══════════════════════════════════════════════════════════

    async def chat_with_vision(
        self,
        prompt: str,
        image_base64: str,
        max_tokens: int = 1000,
        temperature: float = 0.3,
    ) -> str:
        """
        Appel API avec image (Vision) pour OCR.
        
        Args:
            prompt: Instructions pour l'analyse
            image_base64: Image encodée en base64
            max_tokens: Tokens max pour la réponse
            temperature: Température (recommandé: 0.3 pour OCR)
            
        Returns:
            Texte extrait de l'image
        """
        # Charger la config
        self._ensure_config_loaded()
        
        if not self.cle_api:
            raise ErreurServiceIA(
                "Clé API Mistral non configurée",
                message_utilisateur="La clé API Mistral n'est pas configurée.",
            )
        
        # Modèle vision (pixtral)
        vision_model = "pixtral-12b-2409"
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.url_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.cle_api}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": vision_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            
            response.raise_for_status()
            result = response.json()
            
            if not result.get("choices"):
                raise ErreurServiceIA(
                    "Réponse vision vide",
                    message_utilisateur="L'analyse de l'image a échoué"
                )
            
            content = result["choices"][0]["message"]["content"]
            logger.info(f"[OK] Vision: {len(content)} caractères extraits")
            
            return content

    # ═══════════════════════════════════════════════════════════
    # MÉTHODES MÉTIER (LEGACY)
    # ═══════════════════════════════════════════════════════════

    async def discuter(
        self, message: str, historique: Optional[list[dict]] = None, contexte: dict | None = None
    ) -> str:
        """
        Interface conversationnelle (legacy)

        Maintenu pour compatibilité avec l'ancien code
        """
        texte_historique = ""
        if historique:
            texte_historique = "\n".join([f"{h['role']}: {h['content']}" for h in historique[-5:]])

        texte_contexte = ""
        if contexte:
            import json

            texte_contexte = f"\n\nContexte:\n{json.dumps(contexte, indent=2)}"

        prompt_systeme = (
            "Tu es l'assistant familial MaTanne. "
            "Tu aides avec: Cuisine, Famille, Maison, Planning."
            f"{texte_contexte}"
        )

        prompt = f"Historique:\n{texte_historique}\n\nUtilisateur: {message}"

        return await self.appeler(
            prompt=prompt, prompt_systeme=prompt_systeme, temperature=0.7, max_tokens=500
        )

    # ═══════════════════════════════════════════════════════════
    # HELPERS SYNCHRONES
    # ═══════════════════════════════════════════════════════════

    def generer_json(
        self,
        prompt: str,
        system_prompt: str = "Réponds UNIQUEMENT en JSON valide.",
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> dict | str | None:
        """
        Génère une réponse JSON de manière synchrone.
        
        Wrapper sync autour de appeler() pour les contextes UI.
        
        Args:
            prompt: Prompt utilisateur
            system_prompt: Instructions système (défaut: JSON uniquement)
            temperature: Température (défaut: 0.3 pour plus de précision)
            max_tokens: Tokens max
            
        Returns:
            Dictionnaire parsé, string JSON brut, ou None si erreur
        """
        import concurrent.futures
        import json
        
        # Exécuter async dans un thread pour éviter les conflits de boucle
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        
        async def _call():
            return await self.appeler(
                prompt=prompt,
                prompt_systeme=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                utiliser_cache=True,
            )
        
        try:
            if loop is not None:
                # Boucle d'événements active - utiliser un thread
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, _call())
                    response = future.result(timeout=60)
            else:
                # Pas de boucle - exécuter directement
                response = asyncio.run(_call())
            
            if not response:
                return None
            
            # Nettoyer et parser JSON
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
            
        except json.JSONDecodeError:
            # Retourner la réponse brute si pas du JSON valide
            logger.warning("Réponse non-JSON, retour brut")
            return response if 'response' in dir() else None
            
        except Exception as e:
            logger.error(f"Erreur generer_json: {e}")
            return None

    def obtenir_infos_modele(self) -> dict[str, Any]:
        """Retourne infos sur le modèle"""
        # S'assurer que la config est chargée
        self._ensure_config_loaded()
        return {"modele": self.modele, "url_base": self.url_base, "timeout": self.timeout}


# ═══════════════════════════════════════════════════════════
# INSTANCE GLOBALE (LAZY)
# ═══════════════════════════════════════════════════════════

_client: ClientIA | None = None


def obtenir_client_ia() -> ClientIA | None:
    """
    Récupère l'instance ClientIA (singleton lazy)

    Returns:
        Instance ClientIA ou None si non disponible
    """
    global _client
    if _client is None:
        _client = ClientIA()
        # NE PAS vérifier cle_api ici - la config est chargée en lazy
        # Elle sera validée au moment du premier appel
        logger.debug("[OK] ClientIA créé (config chargée en lazy)")
    return _client
