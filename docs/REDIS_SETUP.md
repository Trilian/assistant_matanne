# Redis — Activation & Configuration en Production

## Prérequis

- Redis 7.x+ installé ou un service managé (Upstash, Railway, Redis Cloud)
- Package Python `redis>=5.0.0` (déjà dans `requirements.txt`)

## Configuration

### 1. Variable d'environnement

Ajouter `REDIS_URL` dans `.env.local` ou les secrets Streamlit :

```bash
# .env.local
REDIS_URL=redis://localhost:6379/0

# Avec authentification (production)
REDIS_URL=redis://:password@redis-host:6379/0

# Avec TLS (Upstash, Redis Cloud)
REDIS_URL=rediss://:password@redis-host:6380/0
```

### 2. Ou via `st.secrets` (Streamlit Cloud)

```toml
# .streamlit/secrets.toml
REDIS_URL = "redis://:password@redis-host:6379/0"
```

### 3. Ou via la config Pydantic

Le paramètre `REDIS_URL` est déclaré dans `Parametres` (src/core/config/settings.py).

## Validation

```python
from src.core.caching.redis import is_redis_available, obtenir_cache_redis

# Vérifier la disponibilité
print(is_redis_available())  # True si connexion OK

# Obtenir l'instance
cache = obtenir_cache_redis()
print(cache.get_stats())
```

## Architecture multi-niveaux

L'orchestrateur `CacheMultiNiveau` détecte automatiquement Redis :

```
Lecture:  L1 (mémoire) → Redis → L2 (session) → L3 (fichier) → miss
Écriture: L1 + Redis + L2 (L3 si persistent=True)
```

- **Sans Redis** : L1 → L2 → L3 (comportement actuel)
- **Avec Redis** : Redis s'insère entre L1 et L2 pour le partage inter-instances

## Monitoring

```python
from src.core.caching import obtenir_cache

cache = obtenir_cache()
stats = cache.obtenir_statistiques()

print(f"Redis hits: {stats.redis_hits}")
print(f"Redis disponible: {stats.redis_available}")
```

## Fournisseurs recommandés

| Fournisseur | Plan gratuit | Latence | Notes |
|-------------|-------------|---------|-------|
| **Upstash** | 10K req/jour | ~5ms | Serverless, TLS natif |
| **Railway** | $5 crédit | ~1ms (même région) | Simple à déployer |
| **Redis Cloud** | 30MB | ~2ms | Redis officiel |

## Dépannage

- **`is_redis_available()` retourne False** : Vérifier que `REDIS_URL` est défini et que le serveur est joignable.
- **Timeout** : Augmenter le timeout de connexion dans les paramètres Redis.
- **Erreur TLS** : Utiliser `rediss://` (double s) pour les connexions sécurisées.
