# Redis â€” Activation & Configuration en Production

> âš ï¸ **Redis est optionnel.** Le MVP fonctionne avec le cache L1 mÃ©moire + L3 fichier. Redis n'est nÃ©cessaire que pour le scaling en production (cache L2 partagÃ© entre workers).

## PrÃ©requis

- Redis 7.x+ installÃ© ou un service managÃ© (Upstash, Railway, Redis Cloud)
- Package Python `redis>=5.0.0` (dÃ©jÃ  dans `requirements.txt`)

## Configuration

### 1. Variable d'environnement

Ajouter `REDIS_URL` dans `.env.local` :

```bash
# .env.local
REDIS_URL=redis://localhost:6379/0

# Avec authentification (production)
REDIS_URL=redis://:password@redis-host:6379/0

# Avec TLS (Upstash, Redis Cloud)
REDIS_URL=rediss://:password@redis-host:6380/0
```

### 2. Via la config Pydantic

Le paramÃ¨tre `REDIS_URL` est dÃ©clarÃ© dans `Parametres` (src/core/config/settings.py).

## Validation

```python
from src.core.caching.redis import is_redis_available, obtenir_cache_redis

# VÃ©rifier la disponibilitÃ©
print(is_redis_available())  # True si connexion OK

# Obtenir l'instance
cache = obtenir_cache_redis()
print(cache.get_stats())
```

## Architecture multi-niveaux

L'orchestrateur `CacheMultiNiveau` dÃ©tecte automatiquement Redis :

```
Lecture:  L1 (mÃ©moire) â†’ Redis â†’ L2 (session) â†’ L3 (fichier) â†’ miss
Ã‰criture: L1 + Redis + L2 (L3 si persistent=True)
```

- **Sans Redis** : L1 â†’ L2 â†’ L3 (comportement actuel)
- **Avec Redis** : Redis s'insÃ¨re entre L1 et L2 pour le partage inter-instances

## Monitoring

```python
from src.core.caching import obtenir_cache

cache = obtenir_cache()
stats = cache.obtenir_statistiques()

print(f"Redis hits: {stats.redis_hits}")
print(f"Redis disponible: {stats.redis_available}")
```

## Fournisseurs recommandÃ©s

| Fournisseur | Plan gratuit | Latence | Notes |
| ------------- | ------------- | --------- | ------- |
| **Upstash** | 10K req/jour | ~5ms | Serverless, TLS natif |
| **Railway** | $5 crÃ©dit | ~1ms (mÃªme rÃ©gion) | Simple Ã  dÃ©ployer |
| **Redis Cloud** | 30MB | ~2ms | Redis officiel |

## DÃ©pannage

- **`is_redis_available()` retourne False** : VÃ©rifier que `REDIS_URL` est dÃ©fini et que le serveur est joignable.
- **Timeout** : Augmenter le timeout de connexion dans les paramÃ¨tres Redis.
- **Erreur TLS** : Utiliser `rediss://` (double s) pour les connexions sÃ©curisÃ©es.
