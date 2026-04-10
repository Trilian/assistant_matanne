"""
Client IA Unifié - Mistral AI

Fonctionnalités core: appels API, cache, rate limiting, retry.
Vision/OCR et streaming sont délégués aux mixins dédiés.
"""

__all__ = ["ClientIA", "CacheIA", "RateLimitIA", "obtenir_client_ia"]

import asyncio
import logging
import threading
from typing import Any

import httpx

from ..config import obtenir_parametres
from ..exceptions import ErreurLimiteDebit, ErreurServiceIA
from .streaming import StreamingMixin
from .vision import VisionMixin

logger = logging.getLogger(__name__)


def __getattr__(name: str):
    """Expose les utilitaires IA de facon lazy pour compatibilite des imports/tests."""
    if name == "CacheIA":
        from .cache import CacheIA

        return CacheIA
    if name == "RateLimitIA":
        from .rate_limit import RateLimitIA

        return RateLimitIA
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


class ClientIA(VisionMixin, StreamingMixin):
    """
    Client IA unifié pour Mistral

    Fonctionnalités:
    - Appels API avec retry automatique
    - Cache intelligent
    - Rate limiting
    - Gestion d'erreurs robuste
    - Vision/OCR (via VisionMixin)
    - Streaming SSE (via StreamingMixin)
    """

    def __init__(self):
        """Initialise le client - lazy loading de la config."""
        self._config_loaded = False
        self.cle_api = None
        self.modele = None
        self.url_base = None
        self.timeout = None

    def _ensure_config_loaded(self):
        """Charge la config au moment du premier accès (lazy loading)."""
        if self._config_loaded:
            return

        try:
            parametres = obtenir_parametres()
            self.cle_api = parametres.MISTRAL_API_KEY
            self.modele = parametres.MISTRAL_MODEL
            self.url_base = parametres.MISTRAL_BASE_URL
            self.timeout = parametres.MISTRAL_TIMEOUT
            self._config_loaded = True

            logger.info(f"[OK] ClientIA initialisé (modèle: {self.modele})")

        except ValueError:
            logger.error("[ERROR] Configuration IA manquante: Clé API Mistral non configurée")
            self.cle_api = None
            self.modele = None
            self.url_base = None
            self.timeout = None
            raise

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
        response_format: dict | None = None,
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

        # Lazy imports pour réduire la mémoire au démarrage.
        from .cache import CacheIA
        from .rate_limit import RateLimitIA

        # Vérifier rate limit
        peut_appeler, message_erreur = RateLimitIA.peut_appeler()
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
                    response_format=response_format,
                )

                # Enregistrer appel
                RateLimitIA.enregistrer_appel(service="mistral")

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

            except httpx.HTTPStatusError as e:
                status = e.response.status_code if e.response is not None else 0
                # 429: quota Mistral dépassé — respecter Retry-After si présent
                if status == 429:
                    retry_after = 0
                    if e.response is not None:
                        try:
                            retry_after = int(e.response.headers.get("Retry-After", 0))
                        except (ValueError, TypeError):
                            retry_after = 0
                    # Limite de 1 req/s sur Free Tier : attente courte + 1 seul retry.
                    # Retry-After est rarement envoyé ; on attend 2 s (suffisant pour
                    # que la fenêtre RPS se réinitialise) sauf si Retry-After > 10 s.
                    delai_effectif = retry_after if 0 < retry_after <= 10 else 2
                    logger.warning(
                        "[RATE LIMIT] Quota Mistral 429 — attente %ss avant retry (tentative %s/%s)",
                        delai_effectif,
                        tentative + 1,
                        max_tentatives,
                    )
                    if tentative < max_tentatives - 1:
                        await asyncio.sleep(delai_effectif)
                        continue
                    raise ErreurLimiteDebit(
                        f"Erreur API Mistral: {str(e)}",
                        message_utilisateur=(
                            "Limite de requêtes Mistral atteinte. "
                            + (
                                f"Réessayez dans {retry_after}s."
                                if retry_after
                                else "Réessayez dans quelques secondes."
                            )
                        ),
                    ) from e
                if tentative == max_tentatives - 1:
                    logger.error(f"[ERROR] Erreur API après {max_tentatives} tentatives: {e}")
                    raise ErreurServiceIA(
                        f"Erreur API Mistral: {str(e)}",
                        message_utilisateur="L'IA est temporairement indisponible",
                    ) from e
                # Attente exponentielle pour les autres erreurs HTTP
                temps_attente = 2**tentative
                logger.warning(f"Tentative {tentative + 1}/{max_tentatives} après {temps_attente}s")
                await asyncio.sleep(temps_attente)

            except httpx.HTTPError as e:
                if tentative == max_tentatives - 1:
                    logger.error(f"[ERROR] Erreur réseau après {max_tentatives} tentatives: {e}")
                    raise ErreurServiceIA(
                        f"Erreur réseau Mistral: {str(e)}",
                        message_utilisateur="L'IA est temporairement indisponible",
                    ) from e
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
        self,
        prompt: str,
        prompt_systeme: str,
        temperature: float,
        max_tokens: int,
        response_format: dict | None = None,
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
                    **({"response_format": response_format} if response_format else {}),
                },
            )

            reponse.raise_for_status()
            resultat = reponse.json()

            # Vérifier que la réponse contient au moins un choix
            if not resultat.get("choices") or len(resultat["choices"]) == 0:
                raise ErreurServiceIA(
                    "Réponse IA invalide: pas de contenu",
                    message_utilisateur="Service IA retourné une réponse vide",
                )

            contenu = resultat["choices"][0]["message"]["content"]
            logger.info(f"[OK] Réponse reçue ({len(contenu)} caractères)")

            return contenu

    # ═══════════════════════════════════════════════════════════
    # HELPERS SYNCHRONES
    # ═══════════════════════════════════════════════════════════

    def obtenir_suggestions(
        self,
        prompt: str,
        prompt_systeme: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        utiliser_cache: bool = True,
    ) -> str:
        """Retourne des suggestions textuelles via un wrapper synchrone de compatibilité."""
        from src.core.async_utils import executer_async

        try:
            reponse = executer_async(
                self.appeler(
                    prompt=prompt,
                    prompt_systeme=prompt_systeme,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    utiliser_cache=utiliser_cache,
                )
            )
            return reponse or "Suggestions indisponibles pour le moment."
        except Exception as exc:
            logger.warning("Fallback obtenir_suggestions activé: %s", exc)
            return "Suggestions indisponibles pour le moment."

    def generer_json(
        self,
        prompt: str,
        system_prompt: str = "Réponds UNIQUEMENT en JSON valide.",
        temperature: float = 0.3,
        max_tokens: int = 2000,
        utiliser_cache: bool = True,
    ) -> dict | str | None:
        """
        Génère une réponse JSON de manière synchrone.

        Wrapper sync autour de appeler() pour les contextes UI.
        Utilise ``executer_async`` centralisé pour éviter les conflits de boucle.

        Args:
            prompt: Prompt utilisateur
            system_prompt: Instructions système (défaut: JSON uniquement)
            temperature: Température (défaut: 0.3 pour plus de précision)
            max_tokens: Tokens max
            utiliser_cache: Utiliser le cache (défaut: True)

        Returns:
            Dictionnaire parsé, string JSON brut, ou None si erreur
        """
        import json

        from src.core.async_utils import executer_async

        try:
            response = executer_async(
                self.appeler(
                    prompt=prompt,
                    prompt_systeme=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    utiliser_cache=utiliser_cache,
                    response_format={"type": "json_object"},
                )
            )

            if not response:
                return None

            try:
                # Nettoyer et parser JSON
                import re

                cleaned = response.strip()

                # Tentative 1: Extraire bloc de code JSON via regex
                # Capture tout ce qu'il y a entre ```json et ``` ou entre ``` et ```
                code_block_match = re.search(
                    r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE
                )
                if code_block_match:
                    cleaned = code_block_match.group(1).strip()
                else:
                    # Fallback manuel si regex échoue (ex: pas de bloc de code complet)
                    if cleaned.startswith("```json"):
                        cleaned = cleaned[7:]
                    elif cleaned.startswith("```"):
                        cleaned = cleaned[3:]

                    if cleaned.endswith("```"):
                        cleaned = cleaned[:-3]

                    cleaned = cleaned.strip()

                # Tentative 1.1: Utiliser AnalyseurIA._reparer_intelligemment si possible
                try:
                    from .parser import AnalyseurIA

                    cleaned = AnalyseurIA._reparer_intelligemment(cleaned)
                except ImportError:
                    # Nettoyage préventif manuel si AnalyseurIA indisponible
                    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

                return json.loads(cleaned)

            except json.JSONDecodeError as e:
                logger.warning(f"Erreur JSON decode (tentative 1): {e}")

                # Tentative 2: Chercher le premier objet/tableau JSON valide via AnalyseurIA
                try:
                    from .parser import AnalyseurIA

                    extracted = AnalyseurIA._extraire_objet_json(cleaned)
                    extracted = AnalyseurIA._reparer_intelligemment(extracted)
                    return json.loads(extracted)
                except Exception as e:
                    logger.debug(f"AnalyseurIA extraction JSON échouée: {e}")
                    # Fallback regex simple si AnalyseurIA échoue
                    try:
                        match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
                        if match:
                            potential_json = match.group(0)
                            # Nettoyage préventif sur le fragment extrait aussi
                            potential_json = re.sub(r",\s*([}\]])", r"\1", potential_json)
                            return json.loads(potential_json)
                    except Exception as e2:
                        logger.warning(f"Erreur JSON decode (tentative 2): {e2}")

                # Retourner la réponse brute si pas du JSON valide
                logger.warning(f"Réponse non-JSON, retour brut (début): {cleaned[:100]}...")
                return response  # type: ignore[possibly-undefined]

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
_client_lock = threading.Lock()


def obtenir_client_ia() -> ClientIA:
    """
    Récupère l'instance ClientIA (singleton lazy, thread-safe).

    Returns:
        Instance ClientIA (toujours valide — la config est chargée en lazy
        au moment du premier appel API, pas à la création)
    """
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = ClientIA()
                logger.debug("[OK] ClientIA créé (config chargée en lazy)")
    return _client
