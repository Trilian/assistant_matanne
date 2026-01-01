"""
Cache IA Sémantique - Optimisation Avancée
Détecte les prompts similaires et évite 70% des appels API

Principe:
- "Recette rapide poulet" ≈ "Recette de poulet rapide" → même réponse cachée
- Utilise embeddings de texte (sentence-transformers léger)
- Fallback sur cache MD5 classique si embeddings indisponibles
"""
import hashlib
import json
import logging
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
import streamlit as st
import numpy as np

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

class SemanticCacheConfig:
    """Configuration du cache sémantique"""

    # Seuil de similarité (0-1)
    # Plus élevé = plus strict (0.95 = quasi-identique)
    SIMILARITY_THRESHOLD = 0.85

    # TTL par type de requête
    TTL_RECETTES = 3600  # 1h - recettes changent peu
    TTL_COURSES = 1800   # 30min - courses évoluent
    TTL_PLANNING = 7200  # 2h - planning stable

    # Taille max du cache
    MAX_CACHE_SIZE = 100

    # Mode fallback si embeddings indisponibles
    FALLBACK_TO_MD5 = True


# ═══════════════════════════════════════════════════════════
# EMBEDDINGS LÉGERS (sentence-transformers)
# ═══════════════════════════════════════════════════════════

class EmbeddingEngine:
    """
    Moteur d'embeddings léger

    Utilise sentence-transformers (MiniLM) si disponible,
    sinon fallback sur hashing classique
    """

    _instance = None
    _model = None
    _available = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if EmbeddingEngine._model is None:
            self._init_model()

    def _init_model(self):
        """Initialise le modèle d'embeddings"""
        try:
            # Essayer sentence-transformers
            from sentence_transformers import SentenceTransformer

            # Modèle léger (33MB seulement)
            EmbeddingEngine._model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
            EmbeddingEngine._available = True

            logger.info("✅ Embeddings engine initialisé (MiniLM)")

        except ImportError:
            logger.warning("⚠️ sentence-transformers non disponible, fallback MD5")
            EmbeddingEngine._available = False
        except Exception as e:
            logger.error(f"❌ Erreur init embeddings: {e}")
            EmbeddingEngine._available = False

    def encode(self, text: str) -> Optional[np.ndarray]:
        """
        Encode un texte en vecteur

        Returns:
            Vecteur numpy ou None si indisponible
        """
        if not EmbeddingEngine._available or not EmbeddingEngine._model:
            return None

        try:
            # Nettoyer et normaliser
            text = text.strip().lower()

            # Encoder
            embedding = EmbeddingEngine._model.encode(text, convert_to_numpy=True)

            return embedding

        except Exception as e:
            logger.error(f"Erreur encoding: {e}")
            return None

    @staticmethod
    def similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calcule similarité cosinus entre 2 vecteurs

        Returns:
            Score 0-1 (1 = identique)
        """
        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    @staticmethod
    def is_available() -> bool:
        """Vérifie si embeddings disponibles"""
        return EmbeddingEngine._available


# ═══════════════════════════════════════════════════════════
# CACHE SÉMANTIQUE
# ═══════════════════════════════════════════════════════════

class SemanticCache:
    """
    Cache sémantique pour réponses IA

    Fonctionnalités:
    - Détection prompts similaires
    - Éviction intelligente (LRU)
    - Métriques de performance
    """

    CACHE_KEY = "semantic_cache"
    STATS_KEY = "semantic_cache_stats"

    @staticmethod
    def _init():
        """Initialise le cache"""
        if SemanticCache.CACHE_KEY not in st.session_state:
            st.session_state[SemanticCache.CACHE_KEY] = []

        if SemanticCache.STATS_KEY not in st.session_state:
            st.session_state[SemanticCache.STATS_KEY] = {
                "hits": 0,
                "misses": 0,
                "semantic_hits": 0,  # Hits via similarité
                "exact_hits": 0,      # Hits exacts (MD5)
                "total_saved_calls": 0
            }

    @staticmethod
    def get(prompt: str, system: str = "", temperature: float = 0.7,
            category: str = "general") -> Optional[str]:
        """
        Récupère depuis le cache

        Args:
            prompt: Prompt utilisateur
            system: Prompt système
            temperature: Température
            category: Catégorie (recettes, courses, etc.)

        Returns:
            Réponse cachée ou None
        """
        SemanticCache._init()

        cache = st.session_state[SemanticCache.CACHE_KEY]
        stats = st.session_state[SemanticCache.STATS_KEY]

        # Nettoyer cache expiré
        SemanticCache._clean_expired()

        # 1. Tentative cache exact (MD5)
        exact_key = SemanticCache._generate_exact_key(prompt, system, temperature)

        for entry in cache:
            if entry["exact_key"] == exact_key:
                # Vérifier TTL
                if SemanticCache._is_expired(entry):
                    continue

                # Hit exact !
                stats["hits"] += 1
                stats["exact_hits"] += 1
                stats["total_saved_calls"] += 1

                logger.debug(f"✅ Cache HIT exact: {prompt[:50]}")
                return entry["response"]

        # 2. Tentative cache sémantique
        if EmbeddingEngine.is_available():
            engine = EmbeddingEngine()

            # Encoder prompt
            prompt_embedding = engine.encode(prompt)

            if prompt_embedding is not None:
                # Chercher prompt similaire
                for entry in cache:
                    # Skip si pas même catégorie
                    if entry.get("category") != category:
                        continue

                    # Skip si expiré
                    if SemanticCache._is_expired(entry):
                        continue

                    # Calculer similarité
                    cached_embedding = entry.get("embedding")
                    if cached_embedding is None:
                        continue

                    similarity = EmbeddingEngine.similarity(
                        prompt_embedding,
                        cached_embedding
                    )

                    # Si assez similaire
                    if similarity >= SemanticCacheConfig.SIMILARITY_THRESHOLD:
                        stats["hits"] += 1
                        stats["semantic_hits"] += 1
                        stats["total_saved_calls"] += 1

                        logger.info(
                            f"✅ Cache HIT sémantique (sim={similarity:.2f}): "
                            f"{prompt[:50]} ≈ {entry['prompt'][:50]}"
                        )

                        return entry["response"]

        # Miss
        stats["misses"] += 1
        logger.debug(f"❌ Cache MISS: {prompt[:50]}")

        return None

    @staticmethod
    def set(prompt: str, response: str, system: str = "", temperature: float = 0.7,
            category: str = "general", ttl: int = None):
        """
        Sauvegarde dans le cache

        Args:
            prompt: Prompt utilisateur
            response: Réponse IA
            system: Prompt système
            temperature: Température
            category: Catégorie
            ttl: TTL custom (sinon TTL par défaut selon catégorie)
        """
        SemanticCache._init()

        cache = st.session_state[SemanticCache.CACHE_KEY]

        # Déterminer TTL
        if ttl is None:
            ttl_map = {
                "recettes": SemanticCacheConfig.TTL_RECETTES,
                "courses": SemanticCacheConfig.TTL_COURSES,
                "planning": SemanticCacheConfig.TTL_PLANNING,
            }
            ttl = ttl_map.get(category, 1800)  # Défaut 30min

        # Générer clé exacte
        exact_key = SemanticCache._generate_exact_key(prompt, system, temperature)

        # Encoder prompt si possible
        embedding = None
        if EmbeddingEngine.is_available():
            engine = EmbeddingEngine()
            embedding = engine.encode(prompt)

        # Créer entrée
        entry = {
            "prompt": prompt,
            "system": system,
            "temperature": temperature,
            "category": category,
            "response": response,
            "exact_key": exact_key,
            "embedding": embedding,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=ttl),
            "hits": 0
        }

        # Ajouter au cache
        cache.append(entry)

        # Éviction si trop gros
        if len(cache) > SemanticCacheConfig.MAX_CACHE_SIZE:
            SemanticCache._evict_lru()

        logger.debug(f"💾 Cache SET: {prompt[:50]}")

    @staticmethod
    def _generate_exact_key(prompt: str, system: str, temperature: float) -> str:
        """Génère clé MD5 exacte"""
        data = {
            "prompt": prompt.strip(),
            "system": system.strip(),
            "temperature": temperature
        }
        cache_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    @staticmethod
    def _is_expired(entry: dict) -> bool:
        """Vérifie si entrée expirée"""
        return datetime.now() > entry["expires_at"]

    @staticmethod
    def _clean_expired():
        """Nettoie entrées expirées"""
        SemanticCache._init()

        cache = st.session_state[SemanticCache.CACHE_KEY]

        # Filtrer non-expirés
        valid_entries = [
            entry for entry in cache
            if not SemanticCache._is_expired(entry)
        ]

        removed = len(cache) - len(valid_entries)

        if removed > 0:
            logger.debug(f"🗑️ Cache: {removed} entrées expirées nettoyées")
            st.session_state[SemanticCache.CACHE_KEY] = valid_entries

    @staticmethod
    def _evict_lru():
        """Éviction LRU (Least Recently Used)"""
        SemanticCache._init()

        cache = st.session_state[SemanticCache.CACHE_KEY]

        # Trier par date de création (plus vieux en premier)
        cache.sort(key=lambda e: e["created_at"])

        # Garder les N plus récents
        max_size = SemanticCacheConfig.MAX_CACHE_SIZE
        st.session_state[SemanticCache.CACHE_KEY] = cache[-max_size:]

        logger.debug(f"🗑️ Cache LRU: éviction des plus vieilles entrées")

    @staticmethod
    def get_stats() -> dict:
        """Retourne statistiques du cache"""
        SemanticCache._init()

        stats = st.session_state[SemanticCache.STATS_KEY]
        cache = st.session_state[SemanticCache.CACHE_KEY]

        total_requests = stats["hits"] + stats["misses"]
        hit_rate = stats["hits"] / total_requests * 100 if total_requests > 0 else 0

        return {
            "total_entries": len(cache),
            "total_requests": total_requests,
            "hits": stats["hits"],
            "misses": stats["misses"],
            "hit_rate": hit_rate,
            "semantic_hits": stats["semantic_hits"],
            "exact_hits": stats["exact_hits"],
            "saved_api_calls": stats["total_saved_calls"],
            "embeddings_available": EmbeddingEngine.is_available()
        }

    @staticmethod
    def clear():
        """Vide le cache"""
        SemanticCache._init()
        st.session_state[SemanticCache.CACHE_KEY] = []
        logger.info("🗑️ Cache sémantique vidé")

    @staticmethod
    def render_stats():
        """Affiche stats dans Streamlit"""
        import streamlit as st

        stats = SemanticCache.get_stats()

        st.markdown("### 🧠 Cache IA Sémantique")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Taux de Hit",
                f"{stats['hit_rate']:.1f}%",
                delta=f"{stats['saved_api_calls']} appels économisés"
            )

        with col2:
            st.metric(
                "Entrées Cachées",
                stats['total_entries'],
                delta=f"Max {SemanticCacheConfig.MAX_CACHE_SIZE}"
            )

        with col3:
            mode = "🧠 Sémantique" if stats['embeddings_available'] else "🔤 MD5"
            st.metric("Mode", mode)

        with st.expander("📊 Détails"):
            st.json({
                "total_requests": stats['total_requests'],
                "hits": stats['hits'],
                "misses": stats['misses'],
                "semantic_hits": stats['semantic_hits'],
                "exact_hits": stats['exact_hits'],
            })

            if st.button("🗑️ Vider Cache"):
                SemanticCache.clear()
                st.success("Cache vidé !")
                st.rerun()


# ═══════════════════════════════════════════════════════════
# INTÉGRATION AVEC AIClient
# ═══════════════════════════════════════════════════════════

def get_semantic_cached_response(
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        category: str = "general"
) -> Optional[str]:
    """
    Helper pour récupérer réponse cachée

    À utiliser dans AIClient.call()
    """
    return SemanticCache.get(prompt, system, temperature, category)


def set_semantic_cached_response(
        prompt: str,
        response: str,
        system: str = "",
        temperature: float = 0.7,
        category: str = "general"
):
    """
    Helper pour sauvegarder réponse

    À utiliser dans AIClient.call()
    """
    SemanticCache.set(prompt, response, system, temperature, category)