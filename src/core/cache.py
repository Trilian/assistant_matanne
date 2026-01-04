"""
Cache Simplifié - Version Production
"""
import streamlit as st
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Optional, Callable, Dict, List
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CACHE PRINCIPAL
# ═══════════════════════════════════════════════════════════

class Cache:
    """
    Cache simple et efficace

    Fonctionnalités :
    - Cache en mémoire (session Streamlit)
    - TTL automatique
    - Invalidations granulaires par tags
    - Stats temps réel
    - Auto-cleanup
    """

    @staticmethod
    def _initialiser():
        """Initialise state cache"""
        if "cache_donnees" not in st.session_state:
            st.session_state.cache_donnees = {}

        if "cache_timestamps" not in st.session_state:
            st.session_state.cache_timestamps = {}

        if "cache_dependances" not in st.session_state:
            st.session_state.cache_dependances = {}

        if "cache_statistiques" not in st.session_state:
            st.session_state.cache_statistiques = {
                "hits": 0,
                "misses": 0,
                "invalidations": 0,
                "taille_octets": 0
            }

    @staticmethod
    def obtenir(cle: str, ttl: int = 300) -> Optional[Any]:
        """
        Récupère valeur du cache

        Args:
            cle: Clé cache
            ttl: Durée de vie en secondes

        Returns:
            Valeur ou None si expiré/absent
        """
        Cache._initialiser()

        if cle not in st.session_state.cache_donnees:
            st.session_state.cache_statistiques["misses"] += 1
            return None

        # Vérifier TTL
        if cle in st.session_state.cache_timestamps:
            age = (datetime.now() - st.session_state.cache_timestamps[cle]).seconds
            if age > ttl:
                Cache._supprimer(cle)
                st.session_state.cache_statistiques["misses"] += 1
                return None

        st.session_state.cache_statistiques["hits"] += 1
        return st.session_state.cache_donnees[cle]

    @staticmethod
    def definir(
            cle: str,
            valeur: Any,
            ttl: int = 300,
            tags: Optional[List[str]] = None
    ):
        """
        Sauvegarde valeur dans cache

        Args:
            cle: Clé cache
            valeur: Valeur à cacher
            ttl: Durée de vie en secondes
            tags: Tags pour invalidations (ex: ["recettes", "recette_42"])
        """
        Cache._initialiser()

        st.session_state.cache_donnees[cle] = valeur
        st.session_state.cache_timestamps[cle] = datetime.now()

        # Enregistrer tags pour invalidations
        if tags:
            for tag in tags:
                if tag not in st.session_state.cache_dependances:
                    st.session_state.cache_dependances[tag] = []
                st.session_state.cache_dependances[tag].append(cle)

        Cache._mettre_a_jour_taille()

    @staticmethod
    def invalider(pattern: Optional[str] = None, tags: Optional[List[str]] = None):
        """
        Invalide cache

        Args:
            pattern: Pattern dans la clé (ex: "recettes")
            tags: Tags spécifiques (ex: ["recette_42"])
        """
        Cache._initialiser()

        cles_a_supprimer = set()

        # Par pattern
        if pattern:
            cles_a_supprimer.update([
                k for k in st.session_state.cache_donnees.keys()
                if pattern in k
            ])

        # Par tags
        if tags:
            for tag in tags:
                if tag in st.session_state.cache_dependances:
                    cles_a_supprimer.update(st.session_state.cache_dependances[tag])
                    del st.session_state.cache_dependances[tag]

        # Supprimer
        for cle in cles_a_supprimer:
            Cache._supprimer(cle)
            st.session_state.cache_statistiques["invalidations"] += 1

        if cles_a_supprimer:
            logger.info(f"Cache invalidé : {len(cles_a_supprimer)} clés")

    @staticmethod
    def nettoyer_expires(age_max_secondes: int = 3600):
        """
        Nettoie entrées expirées

        Args:
            age_max_secondes: Âge maximum en secondes
        """
        Cache._initialiser()

        maintenant = datetime.now()
        expirees = []

        for cle, timestamp in st.session_state.cache_timestamps.items():
            age = (maintenant - timestamp).seconds
            if age > age_max_secondes:
                expirees.append(cle)

        for cle in expirees:
            Cache._supprimer(cle)

        if expirees:
            logger.info(f"Cleanup : {len(expirees)} entrées supprimées")

    @staticmethod
    def vider():
        """Vide tout le cache"""
        Cache._initialiser()
        st.session_state.cache_donnees = {}
        st.session_state.cache_timestamps = {}
        st.session_state.cache_dependances = {}
        st.session_state.cache_statistiques["invalidations"] += 1
        logger.info("Cache complètement vidé")

    @staticmethod
    def obtenir_statistiques() -> Dict:
        """Retourne statistiques cache"""
        Cache._initialiser()
        Cache._mettre_a_jour_taille()

        stats = st.session_state.cache_statistiques.copy()
        stats.update({
            "entrees": len(st.session_state.cache_donnees),
            "dependances": len(st.session_state.cache_dependances),
            "taille_mo": stats["taille_octets"] / (1024 * 1024),
        })

        # Taux de hit
        total = stats["hits"] + stats["misses"]
        stats["taux_hit"] = (stats["hits"] / total * 100) if total > 0 else 0

        return stats

    @staticmethod
    def _supprimer(cle: str):
        """Supprime une clé"""
        if cle in st.session_state.cache_donnees:
            del st.session_state.cache_donnees[cle]
        if cle in st.session_state.cache_timestamps:
            del st.session_state.cache_timestamps[cle]

    @staticmethod
    def _mettre_a_jour_taille():
        """Calcule taille cache"""
        try:
            import sys
            taille = sum(
                sys.getsizeof(v)
                for v in st.session_state.cache_donnees.values()
            )
            st.session_state.cache_statistiques["taille_octets"] = taille
        except:
            pass


# ═══════════════════════════════════════════════════════════
# CACHE IA (MD5 Simple)
# ═══════════════════════════════════════════════════════════

class CacheIA:
    """Cache spécialisé pour réponses IA (MD5 simple)"""

    @staticmethod
    def generer_cle(prompt: str, systeme: str = "", temperature: float = 0.7) -> str:
        """
        Génère clé MD5 pour cache IA

        Args:
            prompt: Prompt utilisateur
            systeme: Prompt système
            temperature: Température

        Returns:
            Clé MD5
        """
        donnees_cache = {
            "prompt": prompt.strip(),
            "systeme": systeme.strip(),
            "temperature": temperature
        }
        chaine_cache = json.dumps(donnees_cache, sort_keys=True)
        return f"ia_{hashlib.md5(chaine_cache.encode()).hexdigest()}"

    @staticmethod
    def obtenir(cle: str, ttl: int = 1800) -> Optional[str]:
        """Récupère réponse IA cachée"""
        return Cache.obtenir(cle, ttl)

    @staticmethod
    def definir(cle: str, valeur: str, ttl: int = 1800):
        """Sauvegarde réponse IA"""
        Cache.definir(cle, valeur, ttl, tags=["ia"])


# ═══════════════════════════════════════════════════════════
# RATE LIMIT
# ═══════════════════════════════════════════════════════════

class LimiteDebit:
    """Rate limiting pour API IA"""

    LIMITE_JOURNALIERE = 100
    LIMITE_HORAIRE = 30

    @staticmethod
    def _initialiser():
        """Initialise state rate limit"""
        if "limite_debit" not in st.session_state:
            st.session_state.limite_debit = {
                "appels_jour": 0,
                "appels_heure": 0,
                "dernier_reset": datetime.now().date(),
                "dernier_reset_heure": datetime.now().replace(
                    minute=0, second=0, microsecond=0
                )
            }

    @staticmethod
    def peut_appeler() -> tuple[bool, str]:
        """
        Vérifie si appel API autorisé

        Returns:
            (autorise, message_erreur)
        """
        LimiteDebit._initialiser()

        aujourd_hui = datetime.now().date()
        if st.session_state.limite_debit["dernier_reset"] != aujourd_hui:
            st.session_state.limite_debit["appels_jour"] = 0
            st.session_state.limite_debit["dernier_reset"] = aujourd_hui

        heure_actuelle = datetime.now().replace(minute=0, second=0, microsecond=0)
        if st.session_state.limite_debit["dernier_reset_heure"] != heure_actuelle:
            st.session_state.limite_debit["appels_heure"] = 0
            st.session_state.limite_debit["dernier_reset_heure"] = heure_actuelle

        if st.session_state.limite_debit["appels_jour"] >= LimiteDebit.LIMITE_JOURNALIERE:
            return False, "⏳ Limite quotidienne atteinte"

        if st.session_state.limite_debit["appels_heure"] >= LimiteDebit.LIMITE_HORAIRE:
            return False, "⏳ Limite horaire atteinte"

        return True, ""

    @staticmethod
    def enregistrer_appel():
        """Enregistre un appel API"""
        LimiteDebit._initialiser()
        st.session_state.limite_debit["appels_jour"] += 1
        st.session_state.limite_debit["appels_heure"] += 1


# ═══════════════════════════════════════════════════════════
# DECORATEUR CACHE
# ═══════════════════════════════════════════════════════════

def cache(ttl: int = 300, cle: Optional[str] = None, tags: Optional[List[str]] = None):
    """
    Décorateur pour cacher résultats de fonction

    Args:
        ttl: Durée de vie en secondes
        cle: Clé custom (sinon auto-générée)
        tags: Tags pour invalidations

    Usage:
        @cache(ttl=600, tags=["recettes"])
        def obtenir_recettes():
            return recette_service.get_all()
    """
    def decorateur(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Générer clé cache
            if cle:
                cle_cache = cle
            else:
                cle_data = {
                    "fonction": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
                cle_cache = hashlib.md5(
                    json.dumps(cle_data, sort_keys=True).encode()
                ).hexdigest()

            # Vérifier cache
            resultat = Cache.obtenir(cle_cache, ttl)
            if resultat is not None:
                logger.debug(f"Cache HIT : {func.__name__}")
                return resultat

            # Exécuter fonction
            resultat = func(*args, **kwargs)

            # Cacher résultat
            Cache.definir(cle_cache, resultat, ttl, tags)
            logger.debug(f"Cache SET : {func.__name__}")

            return resultat

        return wrapper
    return decorateur


# ═══════════════════════════════════════════════════════════
# UI COMPONENT (Stats)
# ═══════════════════════════════════════════════════════════

def afficher_statistiques_cache(prefixe_cle: str = "cache"):
    """
    Widget stats cache pour sidebar

    Args:
        prefixe_cle: Préfixe pour clés Streamlit
    """
    import streamlit as st

    stats = Cache.obtenir_statistiques()

    with st.expander("💾 Cache Stats"):
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Entrées",
                stats["entrees"],
                help="Nombre d'entrées en cache"
            )
            st.metric(
                "Taux Hit",
                f"{stats['taux_hit']:.1f}%",
                help="Taux de succès cache"
            )

        with col2:
            st.metric(
                "Taille",
                f"{stats['taille_mo']:.2f} MB",
                help="Taille totale du cache"
            )
            st.metric(
                "Invalidations",
                stats["invalidations"],
                help="Nombre d'invalidations"
            )

        # Actions
        col3, col4 = st.columns(2)

        with col3:
            if st.button("🧹 Nettoyer", key=f"{prefixe_cle}_nettoyer", use_container_width=True):
                Cache.nettoyer_expires()
                st.success("Nettoyage effectué !")
                st.rerun()

        with col4:
            if st.button("🗑️ Vider", key=f"{prefixe_cle}_vider", use_container_width=True):
                Cache.vider()
                st.success("Cache vidé !")
                st.rerun()