"""
Routeur IA Multi-Modèle — Innovation 2.3.

Pipeline intelligent qui route les requêtes IA vers le meilleur modèle
en fonction de la complexité, du budget tokens et de la disponibilité.

Modèles supportés:
- Mistral (cloud) — modèle principal via ClientIA existant
- Ollama (local) — modèle local pour requêtes simples/hors-ligne
- OpenAI GPT-4 (cloud) — fallback premium pour requêtes complexes

Usage:
    from src.core.ai.router import RouteurIA, obtenir_routeur_ia

    routeur = obtenir_routeur_ia()

    # Routage automatique
    reponse = await routeur.appeler("Suggère une recette rapide")

    # Forcer un fournisseur
    reponse = await routeur.appeler("Analyse nutritionnelle détaillée",
                                     fournisseur="openai")

    # Streaming
    async for chunk in routeur.appeler_streaming("Raconte une histoire"):
        print(chunk, end="")
"""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum, StrEnum
from typing import Any, AsyncGenerator

import httpx

logger = logging.getLogger(__name__)

__all__ = [
    "Fournisseur",
    "ConfigFournisseur",
    "RouteurIA",
    "obtenir_routeur_ia",
]


# ═══════════════════════════════════════════════════════════
# FOURNISSEURS
# ═══════════════════════════════════════════════════════════


class Fournisseur(StrEnum):
    """Fournisseurs IA disponibles."""

    MISTRAL = "mistral"
    OLLAMA = "ollama"
    OPENAI = "openai"


@dataclass
class ConfigFournisseur:
    """Configuration d'un fournisseur IA."""

    nom: Fournisseur
    url_base: str
    cle_api: str | None = None
    modele: str = ""
    timeout: float = 30.0
    max_tokens_defaut: int = 1000
    cout_par_1k_tokens: float = 0.0  # $ par 1k tokens
    priorite: int = 1  # 1 = plus prioritaire
    actif: bool = True
    # Capacités
    supporte_streaming: bool = True
    supporte_vision: bool = False
    supporte_json_mode: bool = False
    max_context_tokens: int = 32000


@dataclass
class _HealthStatus:
    """Statut de santé d'un fournisseur."""

    disponible: bool = True
    derniere_verification: float = 0.0
    erreurs_consecutives: int = 0
    latence_moyenne_ms: float = 0.0
    _latences: list[float] = field(default_factory=list)

    def enregistrer_succes(self, latence_ms: float) -> None:
        """Enregistre un appel réussi."""
        self.disponible = True
        self.erreurs_consecutives = 0
        self._latences.append(latence_ms)
        if len(self._latences) > 20:
            self._latences = self._latences[-20:]
        self.latence_moyenne_ms = sum(self._latences) / len(self._latences)
        self.derniere_verification = time.time()

    def enregistrer_erreur(self) -> None:
        """Enregistre un échec."""
        self.erreurs_consecutives += 1
        if self.erreurs_consecutives >= 3:
            self.disponible = False
        self.derniere_verification = time.time()

    def doit_retester(self, cooldown_s: float = 60.0) -> bool:
        """Vérifie si on doit retester un fournisseur indisponible."""
        if self.disponible:
            return True
        return (time.time() - self.derniere_verification) > cooldown_s


# ═══════════════════════════════════════════════════════════
# CLASSIFIEUR DE COMPLEXITÉ
# ═══════════════════════════════════════════════════════════


class _ClassifieurComplexite:
    """Classifie la complexité d'une requête pour le routage."""

    # Mots-clés indiquant une requête complexe
    MOTS_COMPLEXE = {
        "analyse",
        "compare",
        "explique en détail",
        "nutritionnel",
        "planning semaine",
        "batch cooking",
        "optimise",
        "stratégie",
        "budget détaillé",
        "recommandation personnalisée",
        "évalue",
    }

    # Mots-clés indiquant une requête simple
    MOTS_SIMPLE = {
        "liste",
        "rapide",
        "simple",
        "oui",
        "non",
        "combien",
        "quel",
        "quelle",
        "quand",
        "où",
        "c'est quoi",
    }

    @classmethod
    def evaluer(cls, prompt: str, max_tokens: int = 1000) -> str:
        """Évalue la complexité d'une requête.

        Args:
            prompt: Texte du prompt
            max_tokens: Tokens demandés

        Returns:
            "simple", "moyen" ou "complexe"
        """
        prompt_lower = prompt.lower()
        score = 0

        # Longueur du prompt
        if len(prompt) > 500:
            score += 2
        elif len(prompt) > 200:
            score += 1

        # Tokens demandés
        if max_tokens > 2000:
            score += 2
        elif max_tokens > 1000:
            score += 1

        # Mots-clés complexes
        for mot in cls.MOTS_COMPLEXE:
            if mot in prompt_lower:
                score += 2

        # Mots-clés simples
        for mot in cls.MOTS_SIMPLE:
            if mot in prompt_lower:
                score -= 1

        if score >= 4:
            return "complexe"
        elif score >= 1:
            return "moyen"
        return "simple"


# ═══════════════════════════════════════════════════════════
# ROUTEUR IA
# ═══════════════════════════════════════════════════════════


class RouteurIA:
    """Routeur intelligent multi-modèle.

    Route les requêtes vers le meilleur fournisseur en fonction de:
    - Complexité de la requête
    - Disponibilité des fournisseurs
    - Budget tokens
    - Latence
    """

    def __init__(self):
        self._fournisseurs: dict[Fournisseur, ConfigFournisseur] = {}
        self._health: dict[Fournisseur, _HealthStatus] = {}
        self._configurer_defauts()

    def _configurer_defauts(self) -> None:
        """Configure les fournisseurs par défaut depuis la config."""
        try:
            from ..config import obtenir_parametres

            params = obtenir_parametres()

            # Mistral — fournisseur principal
            if params.MISTRAL_API_KEY:
                self.enregistrer_fournisseur(
                    ConfigFournisseur(
                        nom=Fournisseur.MISTRAL,
                        url_base=params.MISTRAL_BASE_URL,
                        cle_api=params.MISTRAL_API_KEY,
                        modele=params.MISTRAL_MODEL,
                        timeout=params.MISTRAL_TIMEOUT,
                        max_tokens_defaut=1000,
                        cout_par_1k_tokens=0.002,
                        priorite=1,
                        supporte_streaming=True,
                        supporte_vision=True,
                        supporte_json_mode=True,
                        max_context_tokens=32000,
                    )
                )
        except Exception:
            logger.debug("Config Mistral non disponible pour le routeur")

        # Ollama — fournisseur local (si disponible)
        self.enregistrer_fournisseur(
            ConfigFournisseur(
                nom=Fournisseur.OLLAMA,
                url_base="http://localhost:11434/v1",
                modele="mistral:7b",
                timeout=60.0,
                max_tokens_defaut=1000,
                cout_par_1k_tokens=0.0,
                priorite=3,  # Fallback économique
                supporte_streaming=True,
                supporte_vision=False,
                supporte_json_mode=False,
                max_context_tokens=8000,
                actif=False,  # Désactivé par défaut, activer si Ollama disponible
            )
        )

        # OpenAI — fournisseur premium fallback
        import os

        openai_key = os.getenv("OPENAI_API_KEY", "")
        if openai_key:
            self.enregistrer_fournisseur(
                ConfigFournisseur(
                    nom=Fournisseur.OPENAI,
                    url_base="https://api.openai.com/v1",
                    cle_api=openai_key,
                    modele="gpt-4o-mini",
                    timeout=30.0,
                    max_tokens_defaut=1000,
                    cout_par_1k_tokens=0.01,
                    priorite=2,
                    supporte_streaming=True,
                    supporte_vision=True,
                    supporte_json_mode=True,
                    max_context_tokens=128000,
                )
            )

    def enregistrer_fournisseur(self, config: ConfigFournisseur) -> None:
        """Enregistre un fournisseur IA.

        Args:
            config: Configuration du fournisseur
        """
        self._fournisseurs[config.nom] = config
        if config.nom not in self._health:
            self._health[config.nom] = _HealthStatus()
        logger.debug(f"Fournisseur enregistré: {config.nom.value} (priorité {config.priorite})")

    def activer_ollama(
        self, modele: str = "mistral:7b", url: str = "http://localhost:11434/v1"
    ) -> None:
        """Active le fournisseur Ollama local.

        Args:
            modele: Nom du modèle Ollama
            url: URL de l'API Ollama
        """
        if Fournisseur.OLLAMA in self._fournisseurs:
            self._fournisseurs[Fournisseur.OLLAMA].actif = True
            self._fournisseurs[Fournisseur.OLLAMA].modele = modele
            self._fournisseurs[Fournisseur.OLLAMA].url_base = url
            logger.info(f"Ollama activé: {modele} @ {url}")

    # ───────────────────────────────────────────────────
    # ROUTAGE
    # ───────────────────────────────────────────────────

    def choisir_fournisseur(
        self,
        prompt: str,
        *,
        fournisseur_force: str | Fournisseur | None = None,
        max_tokens: int = 1000,
        besoin_vision: bool = False,
        besoin_json: bool = False,
    ) -> ConfigFournisseur | None:
        """Choisit le meilleur fournisseur pour une requête.

        Args:
            prompt: Texte du prompt
            fournisseur_force: Forcer un fournisseur spécifique
            max_tokens: Tokens demandés
            besoin_vision: Requiert capacité vision
            besoin_json: Requiert mode JSON

        Returns:
            ConfigFournisseur ou None si aucun disponible
        """
        # Fournisseur forcé
        if fournisseur_force:
            if isinstance(fournisseur_force, str):
                try:
                    fournisseur_force = Fournisseur(fournisseur_force)
                except ValueError:
                    logger.warning(f"Fournisseur inconnu: {fournisseur_force}")
                    fournisseur_force = None

            if fournisseur_force and fournisseur_force in self._fournisseurs:
                config = self._fournisseurs[fournisseur_force]
                if config.actif:
                    return config

        # Filtrer les fournisseurs actifs et disponibles
        candidats: list[ConfigFournisseur] = []
        for f, config in self._fournisseurs.items():
            if not config.actif:
                continue

            health = self._health.get(f, _HealthStatus())
            if not health.disponible and not health.doit_retester():
                continue

            # Vérifier capacités requises
            if besoin_vision and not config.supporte_vision:
                continue
            if besoin_json and not config.supporte_json_mode:
                continue
            if max_tokens > config.max_context_tokens:
                continue

            candidats.append(config)

        if not candidats:
            logger.error("Aucun fournisseur IA disponible!")
            return None

        # Complexité
        complexite = _ClassifieurComplexite.evaluer(prompt, max_tokens)

        # Trier les candidats
        def score_candidat(c: ConfigFournisseur) -> tuple[int, float]:
            """Score de tri: (priorité ajustée, latence)."""
            priorite = c.priorite
            latence = self._health.get(c.nom, _HealthStatus()).latence_moyenne_ms

            # Ajuster priorité selon complexité
            if complexite == "simple" and c.cout_par_1k_tokens == 0:
                # Préférer modèle gratuit/local pour requêtes simples
                priorite -= 1
            elif complexite == "complexe" and c.max_context_tokens >= 32000:
                # Préférer modèle puissant pour requêtes complexes
                priorite -= 1

            return (priorite, latence)

        candidats.sort(key=score_candidat)
        choix = candidats[0]
        logger.debug(
            f"Routage → {choix.nom.value} (complexité: {complexite}, modèle: {choix.modele})"
        )
        return choix

    # ───────────────────────────────────────────────────
    # APPEL API
    # ───────────────────────────────────────────────────

    async def appeler(
        self,
        prompt: str,
        prompt_systeme: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        fournisseur: str | Fournisseur | None = None,
        besoin_vision: bool = False,
        besoin_json: bool = False,
        max_fallbacks: int = 2,
    ) -> str:
        """Appel IA avec routage intelligent et fallback automatique.

        Args:
            prompt: Prompt utilisateur
            prompt_systeme: Instructions système
            temperature: Température (0-2)
            max_tokens: Tokens max
            fournisseur: Forcer un fournisseur (optionnel)
            besoin_vision: Besoin de capacité vision
            besoin_json: Besoin de mode JSON
            max_fallbacks: Nombre max de tentatives alternatives

        Returns:
            Réponse texte

        Raises:
            RuntimeError: Si aucun fournisseur disponible
        """
        tentative = 0
        dernieres_erreurs: list[str] = []
        fournisseur_exclu: set[Fournisseur] = set()

        while tentative <= max_fallbacks:
            # Choisir le fournisseur
            config = self.choisir_fournisseur(
                prompt,
                fournisseur_force=fournisseur if tentative == 0 else None,
                max_tokens=max_tokens,
                besoin_vision=besoin_vision,
                besoin_json=besoin_json,
            )

            if config is None or config.nom in fournisseur_exclu:
                break

            try:
                debut = time.time()
                reponse = await self._appeler_fournisseur(
                    config, prompt, prompt_systeme, temperature, max_tokens
                )
                latence = (time.time() - debut) * 1000
                self._health[config.nom].enregistrer_succes(latence)
                return reponse

            except Exception as e:
                self._health[config.nom].enregistrer_erreur()
                fournisseur_exclu.add(config.nom)
                dernieres_erreurs.append(f"{config.nom.value}: {e}")
                logger.warning(
                    f"Échec {config.nom.value}: {e} — tentative fallback {tentative + 1}"
                )
                tentative += 1

        erreur_msg = " | ".join(dernieres_erreurs) if dernieres_erreurs else "Aucun fournisseur"
        raise RuntimeError(f"Tous les fournisseurs IA ont échoué: {erreur_msg}")

    async def _appeler_fournisseur(
        self,
        config: ConfigFournisseur,
        prompt: str,
        prompt_systeme: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Appel API pour un fournisseur spécifique.

        Compatible OpenAI API format (Mistral, Ollama, OpenAI).
        """
        messages = []
        if prompt_systeme:
            messages.append({"role": "system", "content": prompt_systeme})
        messages.append({"role": "user", "content": prompt})

        headers = {"Content-Type": "application/json"}
        if config.cle_api:
            headers["Authorization"] = f"Bearer {config.cle_api}"

        payload: dict[str, Any] = {
            "model": config.modele,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=config.timeout) as client:
            response = await client.post(
                f"{config.url_base}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            result = response.json()

            choices = result.get("choices", [])
            if not choices:
                raise ValueError("Réponse vide du fournisseur")

            return choices[0]["message"]["content"]

    async def appeler_streaming(
        self,
        prompt: str,
        prompt_systeme: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        fournisseur: str | Fournisseur | None = None,
    ) -> AsyncGenerator[str, None]:
        """Appel streaming avec routage intelligent.

        Args:
            prompt: Prompt utilisateur
            prompt_systeme: Instructions système
            temperature: Température
            max_tokens: Tokens max
            fournisseur: Forcer un fournisseur

        Yields:
            Chunks de texte
        """
        config = self.choisir_fournisseur(
            prompt,
            fournisseur_force=fournisseur,
            max_tokens=max_tokens,
        )

        if not config:
            yield "Aucun fournisseur IA disponible."
            return

        if not config.supporte_streaming:
            # Fallback: appel normal puis yield unique
            result = await self._appeler_fournisseur(
                config, prompt, prompt_systeme, temperature, max_tokens
            )
            yield result
            return

        messages = []
        if prompt_systeme:
            messages.append({"role": "system", "content": prompt_systeme})
        messages.append({"role": "user", "content": prompt})

        headers = {"Content-Type": "application/json"}
        if config.cle_api:
            headers["Authorization"] = f"Bearer {config.cle_api}"

        debut = time.time()

        async with httpx.AsyncClient(timeout=config.timeout) as client:
            async with client.stream(
                "POST",
                f"{config.url_base}/chat/completions",
                headers=headers,
                json={
                    "model": config.modele,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        import json

                        chunk = json.loads(data)
                        choices = chunk.get("choices", [])
                        if choices:
                            content = choices[0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                    except Exception:
                        continue

        latence = (time.time() - debut) * 1000
        self._health[config.nom].enregistrer_succes(latence)

    # ───────────────────────────────────────────────────
    # APPELS SYNCHRONES
    # ───────────────────────────────────────────────────

    def appeler_sync(
        self,
        prompt: str,
        prompt_systeme: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        fournisseur: str | None = None,
    ) -> str:
        """Appel synchrone avec routage.

        Wrapper pour les contextes non-async (Streamlit UI).
        """
        from src.core.async_utils import executer_async

        return executer_async(
            self.appeler(
                prompt=prompt,
                prompt_systeme=prompt_systeme,
                temperature=temperature,
                max_tokens=max_tokens,
                fournisseur=fournisseur,
            )
        )

    # ───────────────────────────────────────────────────
    # STATUT & DIAGNOSTICS
    # ───────────────────────────────────────────────────

    def statut(self) -> dict[str, Any]:
        """Retourne le statut de tous les fournisseurs.

        Returns:
            Dict avec info par fournisseur
        """
        result = {}
        for f, config in self._fournisseurs.items():
            health = self._health.get(f, _HealthStatus())
            result[config.nom.value] = {
                "modele": config.modele,
                "actif": config.actif,
                "disponible": health.disponible,
                "latence_ms": round(health.latence_moyenne_ms, 1),
                "erreurs_consecutives": health.erreurs_consecutives,
                "cout_1k_tokens": config.cout_par_1k_tokens,
                "priorite": config.priorite,
            }
        return result

    @property
    def fournisseurs_actifs(self) -> list[str]:
        """Liste les noms des fournisseurs actifs."""
        return [f.nom.value for f in self._fournisseurs.values() if f.actif]

    async def verifier_disponibilite(self) -> dict[str, bool]:
        """Vérifie la disponibilité de chaque fournisseur.

        Returns:
            Dict {nom: disponible}
        """
        resultats = {}
        for f, config in self._fournisseurs.items():
            if not config.actif:
                resultats[config.nom.value] = False
                continue
            try:
                await asyncio.wait_for(
                    self._appeler_fournisseur(config, "Ping", "", 0.1, 10),
                    timeout=5.0,
                )
                resultats[config.nom.value] = True
                self._health[f].enregistrer_succes(0)
            except Exception:
                resultats[config.nom.value] = False
                self._health[f].enregistrer_erreur()

        return resultats


# ═══════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════

_routeur: RouteurIA | None = None
_routeur_lock = threading.Lock()


def obtenir_routeur_ia() -> RouteurIA:
    """Obtient le routeur IA singleton (thread-safe).

    Returns:
        Instance RouteurIA
    """
    global _routeur
    if _routeur is None:
        with _routeur_lock:
            if _routeur is None:
                _routeur = RouteurIA()
    return _routeur
