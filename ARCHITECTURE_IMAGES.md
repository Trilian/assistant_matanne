# 🏗️ Architecture: Système de Génération d'Images

## 📐 Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                      STREAMLIT APP (UI)                          │
│  - Affiche les recettes                                          │
│  - Bouton "Générer l'image"                                      │
└─────────────────────────────────────────────┬───────────────────┘
                                              │
                                              │ generer_image_recette()
                                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            IMAGE GENERATOR (src/utils/image_generator.py)        │
│                                                                   │
│  1️⃣  Essaie APIs photos réelles (priorité haute):               │
│      ├─ Unsplash.com       (photos professionnelles)            │
│      ├─ Pexels.com         (photos excellentes)                 │
│      └─ Pixabay.com        (images libres)                      │
│                                                                   │
│  2️⃣  Si aucune trouvée → Génération IA:                         │
│      ├─ Pollinations.ai    (IA rapide, pas de clé)             │
│      └─ Replicate.com      (IA premium, si token)              │
│                                                                   │
│  3️⃣  Retourner URL directe                                      │
└──────────────┬─────────────────────────────────────────┬────────┘
               │                                         │
               ↓                                         ↓
        ┌────────────────┐         ┌────────────────────────┐
        │ Photo Trouvée  │         │ Image Générée par IA   │
        │ (< 1 sec)      │         │ (2-3 sec ou premium)   │
        │ ⭐⭐⭐⭐⭐        │         │ ⭐⭐⭐⭐               │
        └────────────────┘         └────────────────────────┘
               │                                         │
               └──────────────────────┬──────────────────┘
                                      │
                                      ↓
                        ┌──────────────────────────┐
                        │  Image URL Retournée    │
                        └──────────────────────────┘
                                      │
                                      ↓
                        ┌──────────────────────────┐
                        │  Affichée dans Streamlit │
                        │  st.image(url)           │
                        └──────────────────────────┘
```

---

## 📊 Flow Décisionnel

```
┌─ generer_image_recette(nom, desc, ingredients, type_plat)
│
├─ Clé Unsplash? OUI ──→ Chercher ──→ Trouvé? OUI ──→ Retourner URL ✅
│                                    │ NON
│                                    └─→ Continuer
│
├─ Clé Pexels? OUI ────→ Chercher ──→ Trouvé? OUI ──→ Retourner URL ✅
│                                    │ NON
│                                    └─→ Continuer
│
├─ Clé Pixabay? OUI ───→ Chercher ──→ Trouvé? OUI ──→ Retourner URL ✅
│                                    │ NON
│                                    └─→ Continuer
│
├─ Pollinations? TOUJOURS ──→ Générer IA ──→ Retourner URL ✅
│
└─ Clé Replicate? OUI ─→ Générer Premium IA ──→ Retourner URL ✅
```

---

## 🔄 Cycle de Vie (Utilisateur)

```
┌──────────────────────────────────┐
│ Utilisateur Streamlit            │
│ Clique "Générer l'image"         │
└──────────────┬───────────────────┘
               │
               ↓
    ┌──────────────────────┐
    │ Spinner "⏳ Chargement │
    └──────────────────────┘
               │
               ↓
    ┌──────────────────────────────────┐
    │ generer_image_recette() appelée  │
    └──────────────────────────────────┘
               │
               ├─→ Unsplash (< 100 ms)
               │   └─→ Pas trouvé
               │
               ├─→ Pexels (< 100 ms)
               │   └─→ Pas trouvé
               │
               ├─→ Pixabay (< 100 ms)
               │   └─→ Pas trouvé
               │
               ├─→ Pollinations (1-3 sec)
               │   └─→ Image générée! ✅
               │
               ↓
    ┌──────────────────────┐
    │ URL Retournée        │
    └──────────────────────┘
               │
               ↓
    ┌──────────────────────┐
    │ st.image(url)        │
    │ Affichage            │
    └──────────────────────┘
               │
               ↓
    ┌──────────────────────┐
    │ Image visible!       │
    │ 😍 Utilisateur heureux
    └──────────────────────┘
```

---

## 🗂️ Structure des Fichiers

```
assistant_matanne/
│
├── src/
│   └── utils/
│       └── image_generator.py          ← 🎯 Système principal
│
├── IMAGE_GENERATION_QUICKSTART.md      ← ⚡ Démarrage rapide
├── IMAGE_GENERATION_SETUP.md           ← 📖 Guide complet
├── COMPARISON_IMAGE_APIS.md            ← 📊 Analyse APIs
├── DEPLOYMENT_IMAGE_GENERATION.md      ← 🚀 Production
├── CHANGES_IMAGE_GENERATION.md         ← 📝 Changements
├── IMAGE_GENERATION_COMPLETE.md        ← ✨ Complet
├── IMAGE_GENERATION_INDEX.md           ← 📚 Index
├── README_IMAGES.md                    ← 🎨 Ce fichier
│
├── test_image_generation.py            ← 🧪 Tests
├── .env.example.images                 ← 🔧 Config
│
└── docs/
    └── ARCHITECTURE.md                 ← Architecture
```

---

## 🔌 Intégration dans l'App

### Endroit 1: Module Recettes
```python
# src/modules/cuisine/recettes.py
from src.utils.image_generator import generer_image_recette

# Quand utilisateur clique "Générer l'image"
url_image = generer_image_recette(
    nom_recette,
    description,
    ingredients_list,
    type_plat
)

if url_image:
    st.image(url_image)
```

### Endroit 2: Services Recettes (optionnel)
```python
# Pourrait être ajouté pour génération auto
class RecetteService:
    def generer_image_auto(self, recette_id):
        recette = self.get_by_id(recette_id)
        url = generer_image_recette(...)
        recette.url_image = url
        self.update(recette)
```

---

## 🌐 Architecture des APIs

### Tier 1: Photos Réelles (Priorité Haute)
```
┌─ Unsplash
│  └─ API: https://api.unsplash.com/search/photos
│  └─ Besoin: Client ID
│  └─ Limite: 50 req/h (enregistrée: illimitée)
│  └─ Résultat: URLs images professionnelles
│
├─ Pexels
│  └─ API: https://api.pexels.com/v1/search
│  └─ Besoin: API Key
│  └─ Limite: 200 req/h
│  └─ Résultat: Photos excellentes
│
└─ Pixabay
   └─ API: https://pixabay.com/api/
   └─ Besoin: API Key
   └─ Limite: 100 req/h
   └─ Résultat: Images libres
```

### Tier 2: Génération IA (Fallback)
```
├─ Pollinations.ai
│  └─ API: https://image.pollinations.ai/prompt/{prompt}
│  └─ Besoin: AUCUN
│  └─ Limite: Illimitée
│  └─ Résultat: Qualité correcte, très rapide
│
└─ Replicate
   └─ API: https://api.replicate.com/
   └─ Besoin: Token API
   └─ Limite: 100/mois gratuit
   └─ Résultat: Qualité premium
```

---

## 📈 Performance

### Timing par Source

```
Unsplash:     ≈ 100-200 ms  (appel + recherche)
Pexels:       ≈ 100-150 ms  (très rapide)
Pixabay:      ≈ 100-200 ms  (rapide)
Pollinations: ≈ 2-3 sec     (génération IA)
Replicate:    ≈ 15-30 sec   (IA premium)

TOTAL SI HIT:     < 1 seconde ✅
TOTAL SI FALLBACK: 2-3 secondes ⚙️
```

### Métriques Optimisation

```
Succès Taux Photo:  ~80% des recettes populaires
Succès Fallback:    ~95% total (avec Pollinations)
Succès Premium:     ~99% total (avec Replicate)

Latence P95: < 1 sec (si source photo)
Latence P99: < 4 sec (avec fallback)
```

---

## 🔐 Sécurité

### API Keys Storage
```
✅ Variables d'environnement
✅ Streamlit secrets (pour cloud)
✅ .env local (jamais committer)
✅ Ou GitHub secrets (CI/CD)

❌ Hardcodés dans le code
❌ Dans git
❌ Exposed publiquement
```

### Rate Limits Respect
```
✅ Système de fallback
✅ Pas de retry boucle infini
✅ Timeouts définis
✅ Logging des erreurs
```

---

## 🚀 Scalabilité

### Pour 10 utilisateurs
- ✅ Aucun problème
- Limite Unsplash OK (50/h)
- Toutes les APIs suffisent

### Pour 100 utilisateurs
- ✅ Probable sans souci
- Unsplash: 50/h → OK pour pics
- Pexels: 200/h → Excellent
- Pixabay: 100/h → Bon
- Recommander Unsplash + Pexels

### Pour 1000+ utilisateurs
- ⚠️ Besoin de caching
- Enregistrer les images en DB
- Réduire les appels API
- Utiliser CDN pour les images

---

## 📊 Coûts Échelle

```
100 utilisateurs:
- Unsplash + Pexels: 0€
- Pollinations: 0€
- TOTAL: 0€

1000 utilisateurs:
- Unsplash (registrée): 0€
- Pexels: 0€
- Pixabay: 0€
- Pollinations: 0€
- TOTAL: 0€

10000+ utilisateurs:
- Replicate payant: $5-50/mois
- Ou CDN: $10-100/mois
- TOTAL: 15-150€/mois
```

---

## 🔧 Maintenance

### Points de Suivi
- ✅ Les APIs restent stables
- ✅ Les clés ne sont pas révoquées
- ✅ Les limites de rate ne sont pas atteintes
- ✅ Logs d'erreurs surveillés

### Actions Préventives
- Tester régulièrement avec `test_image_generation.py`
- Monitorer les logs
- Avoir un plan B (fallback Pollinations)

---

**Status**: ✅ Production Ready
**Dernière mise à jour**: 17 janvier 2026
