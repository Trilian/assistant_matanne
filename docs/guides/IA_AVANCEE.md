# Guide — Module IA Avancée

> **Routes** : `GET|POST /api/v1/ia-avancee/*`  
> **Rate limiting** : 10 req/min (plafonné par `verifier_limite_debit_ia`)  
> **Modèle** : Mistral AI (configuré dans `.env.local`)  
> **Service** : `src/services/ia_avancee/service.py`

---

## Vue d'ensemble — Les 14 outils IA

| # | Endpoint | Méthode | Description | Multimodal |
|---|----------|---------|-------------|-----------|
| 1 | `/suggestions-achats` | GET | Suggestions achats basées sur l'historique de courses | Non |
| 2 | `/planning-adaptatif` | POST | Planning repas adapté (météo + budget + préférences) | Non |
| 3 | `/diagnostic-plante` | POST | Diagnostic plante par photo (maladie, soin recommandé) | ✅ Image |
| 4 | `/prevision-depenses` | GET | Prévision dépenses de fin de mois | Non |
| 5 | `/idees-cadeaux` | POST | Idées cadeaux personnalisées pour anniversaire | Non |
| 6 | `/analyse-photo` | POST | Analyse photo multi-usage (contexte auto-détecté) | ✅ Image |
| 7 | `/optimisation-routines` | GET | Suggestions d'optimisation des routines ménagères | Non |
| 8 | `/analyse-document` | POST | Analyse document par photo (OCR + extraction données) | ✅ Image |
| 9 | `/estimation-travaux` | POST | Estimation coût travaux par photo | ✅ Image |
| 10 | `/planning-voyage` | POST | Planning voyage complet (itinéraire, budget, checklist) | Non |
| 11 | `/recommandations-energie` | GET | Économies d'énergie basées sur consommation réelle | Non |
| 12 | `/prediction-pannes` | GET | Prédiction pannes équipements (historique entretien) | Non |
| 13 | `/suggestions-proactives` | GET | Suggestions proactives multi-modules contextuelles | Non |
| 14 | `/adaptations-meteo` | POST | Adaptations planning selon météo (repas, activités) | Non |

---

## Détail de chaque outil

### 1. Suggestions achats — GET `/suggestions-achats`

Analyse l'historique de courses et l'inventaire pour suggérer ce qu'il faut racheter.

**Auth** : Bearer token requis  
**Rate limit** : 10 req/min IA  
**Réponse** : `SuggestionsAchatsResponse`

```python
# Exemple de réponse
{
  "suggestions": [
    {"nom": "Pâtes", "raison": "Stock bas (2 paquets restants)", "priorite": "haute"},
    {"nom": "Lait", "raison": "Consommé chaque semaine", "priorite": "normale"}
  ],
  "contexte": "Basé sur 8 semaines d'historique"
}
```

---

### 2. Planning adaptatif — POST `/planning-adaptatif`

Génère un planning repas adapté aux conditions actuelles (météo, budget restant, préférences).

**Body** : `PlanningAdaptatifRequest`
```json
{
  "semaine_debut": "2026-04-07",
  "budget_restant": 120.50,
  "contraintes": ["sans_gluten"],
  "incorporer_meteo": true
}
```

**Réponse** : `PlanningAdaptatif` (7 jours de repas avec justifications)

---

### 3. Diagnostic plante — POST `/diagnostic-plante`

Analyse une photo de plante pour diagnostiquer maladies et suggérer soins.

**Body** : `multipart/form-data` avec champ `image` (JPG/PNG, max 5MB)  
**Réponse** : `DiagnosticPlante`
```json
{
  "diagnostic": "Oïdium (champignon)",
  "confiance": 0.85,
  "soins_recommandes": ["Traiter avec fongicide", "Réduire arrosage"],
  "urgence": "modérée"
}
```

---

### 4. Prévision dépenses — GET `/prevision-depenses`

Prédit les dépenses restantes du mois en cours.

**Réponse** : `PrevisionDepenses`
```json
{
  "prevu_fin_mois": 340.00,
  "budget_restant": 215.50,
  "tendance": "normale",
  "alertes": []
}
```

---

### 5. Idées cadeaux — POST `/idees-cadeaux`

Génère des idées cadeaux personnalisées en fonction du profil et budget.

**Body** : `IdeesCadeauxRequest`
```json
{
  "beneficiaire": "Jules",
  "age_ans": 2,
  "budget_max": 50,
  "interets": ["dinosaures", "construction"],
  "occasion": "anniversaire"
}
```

---

### 6. Analyse photo multi-usage — POST `/analyse-photo`

Analyse une photo et en extrait des informations selon le contexte (produit, plante, document, état).

**Body** : `UploadFile` (JPG/PNG) + champ `contexte` optionnel  
**Réponse** : `AnalysePhotoMultiUsage`

---

### 7. Optimisation routines — GET `/optimisation-routines`

Analyse les routines existantes et suggère des optimisations (temps, fréquence, ordonnancement).

**Réponse** : `OptimisationRoutinesResponse`
```json
{
  "optimisations": [
    {"routine": "Aspirateur", "suggestion": "Passer le mardi matin avant les courses"},
    {"routine": "Lessive", "suggestion": "Grouper 2 machines le dimanche"}
  ],
  "gain_estime_minutes": 45
}
```

---

### 8. Analyse document — POST `/analyse-document`

OCR + extraction structurée depuis photo d'un document (facture, contrat, ordonnance).

**Body** : `UploadFile` (JPG/PNG, max 10MB)  
**Réponse** : `DocumentAnalyse`
```json
{
  "type_document": "facture",
  "données_extraites": {
    "montant": 127.50,
    "date": "2026-03-15",
    "fournisseur": "EDF"
  },
  "texte_brut": "..."
}
```

---

### 9. Estimation travaux — POST `/estimation-travaux`

Estime le coût de travaux à partir d'une photo.

**Body** : `EstimationTravauxRequest` + `UploadFile`  
**Réponse** : `EstimationTravauxPhoto`
```json
{
  "type_travaux": "Remplacement revêtement sol",
  "estimation_basse": 800,
  "estimation_haute": 1500,
  "facteurs": ["surface ~20m²", "pose comprise", "matériaux standard"],
  "recommandations": ["Demander 3 devis"]
}
```

---

### 10. Planning voyage — POST `/planning-voyage`

Génère un planning voyage détaillé avec itinéraire, budget et checklist.

**Body** : `PlanningVoyageRequest`
```json
{
  "destination": "Bretagne",
  "duree_jours": 5,
  "budget_total": 800,
  "enfants": true,
  "interets": ["plage", "gastronomie"]
}
```

**Réponse** : `PlanningVoyage` (itinéraire jour par jour + checklist + budget estimé)

---

### 11. Recommandations énergie — GET `/recommandations-energie`

Analyse la consommation énergétique et recommande des économies.

**Réponse** : `RecommandationsEnergieResponse`
```json
{
  "economies_estimees_euros": 42.0,
  "recommandations": [
    {"action": "Décaler lave-linge en heures creuses", "economie_mois": 8.50}
  ]
}
```

---

### 12. Prédiction pannes — GET `/prediction-pannes`

Prédit les équipements susceptibles de tomber en panne basé sur l'historique d'entretien.

**Réponse** : `PredictionsPannesResponse`

---

### 13. Suggestions proactives — GET `/suggestions-proactives`

Point d'entrée multi-modules — retourne des suggestions contextuelles depuis tous les domaines.

**Réponse** : `SuggestionsProactivesResponse`
```json
{
  "suggestions": [
    {"module": "cuisine", "message": "3 recettes à utiliser avant péremption", "priorite": 1},
    {"module": "maison", "message": "Vidange voiture à programmer (12 000 km)", "priorite": 2}
  ]
}
```

---

### 14. Adaptations météo — POST `/adaptations-meteo`

Adapte les activités et repas planifiés selon la météo prévue.

**Body** : `AdaptationsMeteoRequest`  
**Réponse** : `AdaptationsMeteoResponse`

---

## Architecture technique

### Rate limiting IA

Tous les endpoints IA utilisent la dépendance `verifier_limite_debit_ia` (10 req/min vs 60 req/min standard).

```python
@router.post("/diagnostic-plante")
@gerer_exception_api
async def diagnostic_plante(
    image: UploadFile = File(...),
    _: None = Depends(verifier_limite_debit_ia),    # ← rate limit IA
    user: dict = Depends(require_auth),
) -> dict:
    ...
```

### Cache IA (cache sémantique)

Le `CacheIA` dans `src/core/ai/cache.py` stocke les réponses d'appels IA identiques/similaires.
TTL par défaut : 1 heure. Les appels multimodaux (images) ne sont **pas** mis en cache.

### Client Mistral

```python
from src.core.ai import ClientIA, AnalyseurIA

client = ClientIA()
# Appel synchrone (dans un thread via executer_async)
reponse = client.appeler_sync(prompt, system_prompt=..., modele="mistral-large-latest")
```

### Circuit Breaker

Si Mistral AI est indisponible, le `CircuitBreaker` (`src/core/ai/circuit_breaker.py`) ouvre le circuit après 5 échecs consécutifs et retourne des réponses de fallback.

---

## Limites et quotas

| Paramètre | Valeur | Source config |
|-----------|--------|---------------|
| Limite journalière globale | `AI_RATE_LIMIT_DAILY` | `src/core/constants.py` |
| Limite horaire | `AI_RATE_LIMIT_HOURLY` | `src/core/constants.py` |
| Rate limit HTTP IA | 10 req/min | `src/api/rate_limiting/` |
| Taille max image | 5 MB (10 MB pour documents) | Validation route |
| Formats image acceptés | JPG, PNG, WEBP | `UploadFile` validator |

---

## Dépannage

| Erreur | Cause probable | Solution |
|--------|---------------|---------|
| `429 Too Many Requests` | Rate limit IA atteint | Attendre 60s puis réessayer |
| `503 Service Unavailable` | Circuit breaker ouvert (Mistral down) | Attendre et réessayer (auto-reset après 60s) |
| `422 Unprocessable Entity` | Body mal formé | Vérifier le schéma dans `/docs` (Swagger) |
| `500 Internal Server Error` | Erreur parsing réponse Mistral | Vérifier les logs `uvicorn` |

Pour tester manuellement : `http://localhost:8000/docs#/IA%20Avancée`
