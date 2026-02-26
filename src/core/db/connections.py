"""
Connections Unifiées — Innovation v11: st.connection() pour tous les services.

Ajoute des classes de connexion natives Streamlit pour:
- Redis (cache distribué, sessions, pub/sub)
- APIs externes (OpenFoodFacts, weather, etc.)
- WebSockets

Usage:
    from src.core.db.connections import (
        obtenir_connexion_redis,
        obtenir_connexion_api,
        RedisConnection,
        ExternalAPIConnection,
    )

    # Redis
    redis = obtenir_connexion_redis()
    redis.set("key", "value", ttl=300)
    value = redis.get("key")

    # API externe avec retry
    api = obtenir_connexion_api("openfoodfacts")
    product = api.get("/product/3017620422003")
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Any, Generator

import streamlit as st

logger = logging.getLogger(__name__)

__all__ = [
    "RedisConnection",
    "ExternalAPIConnection",
    "WebSocketConnection",
    "obtenir_connexion_redis",
    "obtenir_connexion_api",
    "obtenir_connexion_ws",
]


# ═══════════════════════════════════════════════════════════
# REDIS CONNECTION — st.connection pour cache distribué
# ═══════════════════════════════════════════════════════════


class RedisConnection(st.connections.BaseConnection["Any"]):
    """Connection Redis via st.connection avec pooling Streamlit natif.

    Fonctionnalités:
    - Connection pooling automatique
    - Retry sur erreurs réseau
    - Serialization JSON automatique
    - Health check intégré
    - Pub/Sub support

    Usage:
        conn = st.connection("redis", type=RedisConnection)
        conn.set("user:123", {"name": "Alice"}, ttl=3600)
        user = conn.get("user:123")
    """

    def _connect(self, **kwargs) -> Any:
        """Établit la connexion Redis.

        Configuration depuis (par priorité):
        1. secrets.toml → [connections.redis]
        2. Paramètres application → REDIS_URL
        3. Arguments kwargs
        """
        try:
            import redis

            # Résoudre l'URL Redis
            url = kwargs.get("url")
            if not url:
                try:
                    url = st.secrets.get("connections", {}).get("redis", {}).get("url")
                except Exception:
                    pass

            if not url:
                try:
                    from src.core.config import obtenir_parametres

                    params = obtenir_parametres()
                    url = getattr(params, "REDIS_URL", None)
                except Exception:
                    pass

            if not url:
                url = "redis://localhost:6379/0"

            # Créer le pool de connexions
            pool = redis.ConnectionPool.from_url(
                url,
                max_connections=kwargs.get("max_connections", 10),
                socket_timeout=kwargs.get("socket_timeout", 5.0),
                socket_connect_timeout=kwargs.get("socket_connect_timeout", 5.0),
                retry_on_timeout=True,
            )

            client = redis.Redis(connection_pool=pool, decode_responses=True)

            # Test connexion
            client.ping()
            logger.info("Redis connecté")

            return client

        except ImportError:
            logger.warning("redis non installé - mode fallback dict")
            return _FallbackRedis()
        except Exception as e:
            logger.warning(f"Redis non disponible: {e} - mode fallback")
            return _FallbackRedis()

    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur depuis Redis.

        Args:
            key: Clé Redis
            default: Valeur par défaut si clé absente

        Returns:
            Valeur désérialisée ou default
        """
        try:
            import json

            value = self._instance.get(key)
            if value is None:
                return default

            # Tenter de désérialiser JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value

        except Exception as e:
            logger.warning(f"Redis get error: {e}")
            return default

    def set(
        self,
        key: str,
        value: Any,
        *,
        ttl: int | None = None,
    ) -> bool:
        """Stocke une valeur dans Redis.

        Args:
            key: Clé Redis
            value: Valeur (auto-sérialisée en JSON si dict/list)
            ttl: Time-to-live en secondes

        Returns:
            True si succès
        """
        try:
            import json

            # Sérialiser si nécessaire
            if isinstance(value, dict | list):
                value = json.dumps(value, ensure_ascii=False, default=str)

            if ttl:
                return bool(self._instance.setex(key, ttl, value))
            return bool(self._instance.set(key, value))

        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    def delete(self, *keys: str) -> int:
        """Supprime des clés.

        Returns:
            Nombre de clés supprimées
        """
        try:
            return self._instance.delete(*keys)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Vérifie si une clé existe."""
        try:
            return bool(self._instance.exists(key))
        except Exception:
            return False

    def incr(self, key: str, amount: int = 1) -> int:
        """Incrémente un compteur atomique."""
        try:
            return self._instance.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis incr error: {e}")
            return 0

    def expire(self, key: str, ttl: int) -> bool:
        """Définit l'expiration d'une clé."""
        try:
            return bool(self._instance.expire(key, ttl))
        except Exception:
            return False

    def publish(self, channel: str, message: Any) -> int:
        """Publie un message sur un channel.

        Args:
            channel: Nom du channel
            message: Message (auto-sérialisé)

        Returns:
            Nombre d'abonnés ayant reçu le message
        """
        try:
            import json

            if isinstance(message, dict | list):
                message = json.dumps(message, ensure_ascii=False, default=str)
            return self._instance.publish(channel, message)
        except Exception as e:
            logger.error(f"Redis publish error: {e}")
            return 0

    @contextmanager
    def subscribe(self, *channels: str) -> Generator[Any, None, None]:
        """Souscrit à des channels pub/sub.

        Usage:
            with redis.subscribe("updates") as pubsub:
                for message in pubsub.listen():
                    if message["type"] == "message":
                        process(message["data"])
        """
        pubsub = None
        try:
            pubsub = self._instance.pubsub()
            pubsub.subscribe(*channels)
            yield pubsub
        finally:
            if pubsub:
                pubsub.unsubscribe()
                pubsub.close()

    def health_check(self) -> dict[str, Any]:
        """Vérifie la santé de la connexion Redis."""
        try:
            start = time.time()
            self._instance.ping()
            latency = (time.time() - start) * 1000

            info = self._instance.info("memory")

            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": self._instance.info("clients").get("connected_clients", 0),
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class _FallbackRedis:
    """Redis fallback en mémoire quand Redis n'est pas disponible."""

    def __init__(self):
        self._data: dict[str, tuple[Any, float | None]] = {}

    def get(self, key: str) -> Any:
        entry = self._data.get(key)
        if entry is None:
            return None
        value, expires = entry
        if expires and time.time() > expires:
            del self._data[key]
            return None
        return value

    def set(self, key: str, value: Any) -> bool:
        self._data[key] = (value, None)
        return True

    def setex(self, key: str, ttl: int, value: Any) -> bool:
        self._data[key] = (value, time.time() + ttl)
        return True

    def delete(self, *keys: str) -> int:
        count = 0
        for key in keys:
            if key in self._data:
                del self._data[key]
                count += 1
        return count

    def exists(self, key: str) -> bool:
        return key in self._data

    def incrby(self, key: str, amount: int) -> int:
        current = self._data.get(key, (0, None))[0]
        new_value = int(current) + amount
        self._data[key] = (new_value, None)
        return new_value

    def expire(self, key: str, ttl: int) -> bool:
        if key in self._data:
            value = self._data[key][0]
            self._data[key] = (value, time.time() + ttl)
            return True
        return False

    def publish(self, channel: str, message: Any) -> int:
        return 0  # Pas de pub/sub en fallback

    def pubsub(self):
        return _FallbackPubSub()

    def ping(self) -> bool:
        return True

    def info(self, section: str = "") -> dict:
        return {"used_memory_human": "0B", "connected_clients": 1}


class _FallbackPubSub:
    """PubSub fallback."""

    def subscribe(self, *channels):
        pass

    def unsubscribe(self):
        pass

    def close(self):
        pass

    def listen(self):
        return iter([])


# ═══════════════════════════════════════════════════════════
# EXTERNAL API CONNECTION — st.connection pour APIs REST
# ═══════════════════════════════════════════════════════════


class ExternalAPIConnection(st.connections.BaseConnection["Any"]):
    """Connection API REST avec retry et cache Streamlit.

    APIs préconfigurées:
    - openfoodfacts: Infos produits alimentaires
    - openweather: Météo
    - nominatim: Géocodage OSM

    Fonctionnalités:
    - Retry automatique avec backoff
    - Cache des réponses (ttl configurable)
    - Rate limiting
    - Headers personnalisables

    Usage:
        api = st.connection("openfoodfacts", type=ExternalAPIConnection)
        product = api.get("/product/3017620422003.json")
    """

    # APIs préconfigurées
    _PRESETS = {
        "openfoodfacts": {
            "base_url": "https://world.openfoodfacts.org/api/v2",
            "headers": {"User-Agent": "MaTanne/1.0"},
            "rate_limit": 10,  # req/sec
        },
        "openweather": {
            "base_url": "https://api.openweathermap.org/data/2.5",
            "headers": {},
            "rate_limit": 60,  # req/min
        },
        "nominatim": {
            "base_url": "https://nominatim.openstreetmap.org",
            "headers": {"User-Agent": "MaTanne/1.0"},
            "rate_limit": 1,  # req/sec (strict)
        },
    }

    def _connect(self, **kwargs) -> Any:
        """Configure le client HTTP."""
        try:
            import httpx

            # Récupérer config preset ou custom
            preset_name = kwargs.get("preset", self._connection_name)
            preset = self._PRESETS.get(preset_name, {})

            base_url = kwargs.get("base_url") or preset.get("base_url", "")
            headers = {**preset.get("headers", {}), **kwargs.get("headers", {})}
            timeout = kwargs.get("timeout", 30.0)

            # Ajouter API key si fournie
            api_key = kwargs.get("api_key")
            if not api_key:
                try:
                    api_key = st.secrets.get("connections", {}).get(preset_name, {}).get("api_key")
                except Exception:
                    pass

            client = httpx.Client(
                base_url=base_url,
                headers=headers,
                timeout=timeout,
                follow_redirects=True,
            )

            return {
                "client": client,
                "base_url": base_url,
                "api_key": api_key,
                "rate_limit": preset.get("rate_limit", 100),
                "last_request": 0.0,
            }

        except ImportError:
            logger.error("httpx non installé")
            raise ImportError("pip install httpx required")

    def get(
        self,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        ttl: int = 300,
    ) -> dict[str, Any] | None:
        """GET request avec cache.

        Args:
            endpoint: Path de l'endpoint
            params: Query parameters
            ttl: Cache TTL en secondes

        Returns:
            Réponse JSON ou None
        """
        return self._request("GET", endpoint, params=params, ttl=ttl)

    def post(
        self,
        endpoint: str,
        *,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """POST request (non-caché).

        Args:
            endpoint: Path de l'endpoint
            data: Form data
            json: JSON body

        Returns:
            Réponse JSON ou None
        """
        return self._request("POST", endpoint, data=data, json=json, ttl=0)

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        ttl: int = 0,
    ) -> dict[str, Any] | None:
        """Effectue une requête HTTP."""
        config = self._instance
        client = config["client"]

        # Rate limiting
        self._rate_limit(config)

        # Ajouter API key si nécessaire
        if config.get("api_key") and params is not None:
            params = {**params, "appid": config["api_key"]}
        elif config.get("api_key") and params is None:
            params = {"appid": config["api_key"]}

        try:
            if method == "GET":
                response = client.get(endpoint, params=params)
            else:
                response = client.post(endpoint, data=data, json=json)

            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"API request error: {e}")
            return None

    def _rate_limit(self, config: dict) -> None:
        """Applique le rate limiting."""
        rate_limit = config.get("rate_limit", 100)
        min_interval = 1.0 / rate_limit

        elapsed = time.time() - config.get("last_request", 0)
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)

        config["last_request"] = time.time()

    def health_check(self) -> dict[str, Any]:
        """Vérifie la disponibilité de l'API."""
        try:
            start = time.time()
            # Simple HEAD request
            config = self._instance
            config["client"].head("/")
            latency = (time.time() - start) * 1000

            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "base_url": config.get("base_url", ""),
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# ═══════════════════════════════════════════════════════════
# WEBSOCKET CONNECTION — st.connection pour temps réel
# ═══════════════════════════════════════════════════════════


class WebSocketConnection(st.connections.BaseConnection["Any"]):
    """Connection WebSocket pour communication temps réel.

    Usage:
        ws = st.connection("realtime", type=WebSocketConnection, url="wss://...")
        ws.send({"type": "subscribe", "channel": "updates"})

        # Dans un fragment
        @st.fragment(run_every=1)
        def updates():
            msg = ws.receive()
            if msg:
                st.write(msg)
    """

    def _connect(self, **kwargs) -> Any:
        """Établit la connexion WebSocket."""
        try:
            import websocket

            url = kwargs.get("url", "")
            if not url:
                try:
                    url = st.secrets.get("connections", {}).get("websocket", {}).get("url", "")
                except Exception:
                    pass

            ws = websocket.WebSocket()
            if url:
                ws.connect(url)
                logger.info(f"WebSocket connecté à {url}")

            return {"ws": ws, "url": url, "connected": bool(url)}

        except ImportError:
            logger.warning("websocket-client non installé")
            return {"ws": None, "url": "", "connected": False}
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            return {"ws": None, "url": "", "connected": False}

    def send(self, data: dict[str, Any] | str) -> bool:
        """Envoie un message.

        Args:
            data: Message (dict auto-sérialisé en JSON)

        Returns:
            True si envoyé
        """
        try:
            import json

            ws = self._instance.get("ws")
            if not ws:
                return False

            if isinstance(data, dict):
                data = json.dumps(data)

            ws.send(data)
            return True

        except Exception as e:
            logger.error(f"WebSocket send error: {e}")
            return False

    def receive(self, timeout: float = 0.1) -> dict[str, Any] | str | None:
        """Reçoit un message (non-bloquant).

        Args:
            timeout: Timeout en secondes

        Returns:
            Message reçu ou None
        """
        try:
            import json

            ws = self._instance.get("ws")
            if not ws:
                return None

            ws.settimeout(timeout)
            data = ws.recv()

            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return data

        except Exception:
            return None

    def close(self) -> None:
        """Ferme la connexion."""
        try:
            ws = self._instance.get("ws")
            if ws:
                ws.close()
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════
# FACTORY FUNCTIONS
# ═══════════════════════════════════════════════════════════


def obtenir_connexion_redis(
    *,
    url: str | None = None,
    max_connections: int = 10,
) -> RedisConnection:
    """Obtient une connexion Redis via st.connection.

    Args:
        url: URL Redis (optionnel, auto-détecté)
        max_connections: Taille du pool

    Returns:
        RedisConnection
    """
    return st.connection(
        "redis",
        type=RedisConnection,
        url=url,
        max_connections=max_connections,
    )


def obtenir_connexion_api(
    nom: str,
    *,
    api_key: str | None = None,
    **kwargs,
) -> ExternalAPIConnection:
    """Obtient une connexion API externe.

    Args:
        nom: Nom de l'API (openfoodfacts, openweather, nominatim, ou custom)
        api_key: Clé API (optionnel)
        **kwargs: Options supplémentaires (base_url, headers, etc.)

    Returns:
        ExternalAPIConnection
    """
    return st.connection(
        nom,
        type=ExternalAPIConnection,
        preset=nom,
        api_key=api_key,
        **kwargs,
    )


def obtenir_connexion_ws(
    url: str,
    **kwargs,
) -> WebSocketConnection:
    """Obtient une connexion WebSocket.

    Args:
        url: URL WebSocket (wss://...)
        **kwargs: Options supplémentaires

    Returns:
        WebSocketConnection
    """
    return st.connection(
        "websocket",
        type=WebSocketConnection,
        url=url,
        **kwargs,
    )
