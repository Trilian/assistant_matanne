"""
Client IA Unifié - Mistral AI
"""
import httpx
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..config import obtenir_parametres
from ..errors import ErreurServiceIA, ErreurLimiteDebit
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
        """Initialise le client avec la config"""
        parametres = obtenir_parametres()

        try:
            self.cle_api = parametres.MISTRAL_API_KEY
            self.modele = parametres.MISTRAL_MODEL
            self.url_base = parametres.MISTRAL_BASE_URL
            self.timeout = parametres.MISTRAL_TIMEOUT

            logger.info(f"✅ ClientIA initialisé (modèle: {self.modele})")

        except ValueError as e:
            logger.error(f"❌ Configuration IA manquante: {e}")
            raise ErreurServiceIA(
                str(e),
                message_utilisateur="Configuration IA manquante"
            )

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
            max_tentatives: int = 3
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
        # Vérifier rate limit
        from .cache import LimiteDebit
        peut_appeler, message_erreur = LimiteDebit.peut_appeler()
        if not peut_appeler:
            raise ErreurLimiteDebit(message_erreur, message_utilisateur=message_erreur)

        # Vérifier cache
        if utiliser_cache:
            cache = CacheIA.obtenir(
                prompt=prompt,
                systeme=prompt_systeme,
                temperature=temperature,
                modele=self.modele
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
                    max_tokens=max_tokens
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
                        modele=self.modele
                    )

                return reponse

            except httpx.HTTPError as e:
                if tentative == max_tentatives - 1:
                    logger.error(f"❌ Erreur API après {max_tentatives} tentatives: {e}")
                    raise ErreurServiceIA(
                        f"Erreur API Mistral: {str(e)}",
                        message_utilisateur="L'IA est temporairement indisponible"
                    )

                # Attente exponentielle
                temps_attente = 2 ** tentative
                logger.warning(f"Tentative {tentative + 1}/{max_tentatives} après {temps_attente}s")
                await asyncio.sleep(temps_attente)

            except Exception as e:
                logger.error(f"❌ Erreur inattendue: {e}")
                raise ErreurServiceIA(
                    f"Erreur inattendue: {str(e)}",
                    message_utilisateur="Erreur lors de l'appel IA"
                )

        # Ne devrait jamais arriver ici
        raise ErreurServiceIA("Échec après toutes les tentatives")

    async def _effectuer_appel(
            self,
            prompt: str,
            prompt_systeme: str,
            temperature: float,
            max_tokens: int
    ) -> str:
        """Effectue l'appel API réel"""
        messages = []

        if prompt_systeme:
            messages.append({
                "role": "system",
                "content": prompt_systeme
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

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
                }
            )

            reponse.raise_for_status()
            resultat = reponse.json()

            contenu = resultat["choices"][0]["message"]["content"]
            logger.info(f"✅ Réponse reçue ({len(contenu)} caractères)")

            return contenu

    # ═══════════════════════════════════════════════════════════
    # MÉTHODES MÉTIER (LEGACY)
    # ═══════════════════════════════════════════════════════════

    async def discuter(
            self,
            message: str,
            historique: List[Dict] = None,
            contexte: Optional[Dict] = None
    ) -> str:
        """
        Interface conversationnelle (legacy)

        Maintenu pour compatibilité avec l'ancien code
        """
        texte_historique = ""
        if historique:
            texte_historique = "\n".join([
                f"{h['role']}: {h['content']}"
                for h in historique[-5:]
            ])

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
            prompt=prompt,
            prompt_systeme=prompt_systeme,
            temperature=0.7,
            max_tokens=500
        )

    # ═══════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════

    def obtenir_infos_modele(self) -> Dict[str, Any]:
        """Retourne infos sur le modèle"""
        return {
            "modele": self.modele,
            "url_base": self.url_base,
            "timeout": self.timeout
        }


# ═══════════════════════════════════════════════════════════
# INSTANCE GLOBALE (LAZY)
# ═══════════════════════════════════════════════════════════

_client: Optional[ClientIA] = None


def obtenir_client_ia() -> ClientIA:
    """
    Récupère l'instance ClientIA (singleton lazy)

    Returns:
        Instance ClientIA
    """
    global _client
    if _client is None:
        _client = ClientIA()
    return _client