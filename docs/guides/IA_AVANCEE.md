# Guide â€” Module IA AvancÃ©e

> **Routes** : `GET|POST /api/v1/ia-avancee/*`  
> **Rate limiting** : 10 req/min (plafonnÃ© par `verifier_limite_debit_ia`)  
> **ModÃ¨le** : Mistral AI (configurÃ© dans `.env.local`)  
> **Service** : `src/services/ia_avancee/service.py`

---

## Vue d'ensemble â€” Les 14 outils IA

| # | Endpoint | MÃ©thode | Description | Multimodal |
| --- | ---------- | --------- | ------------- | ----------- |
| 1 | `/suggestions-achats` | GET | Suggestions achats basÃ©es sur l'historique de courses | Non |
| 2 | `/planning-adaptatif` | POST | Planning repas adaptÃ© (mÃ©tÃ©o + budget + prÃ©fÃ©rences) | Non |
| 3 | `/diagnostic-plante` | POST | Diagnostic plante par photo (maladie, soin recommandÃ©) | âœ… Image |
| 4 | `/prevision-depenses` | GET | PrÃ©vision dÃ©penses de fin de mois | Non |
| 5 | `/idees-cadeaux` | POST | IdÃ©es cadeaux personnalisÃ©es pour anniversaire | Non |
| 6 | `/analyse-photo` | POST | Analyse photo multi-usage (contexte auto-dÃ©tectÃ©) | âœ… Image |
| 7 | `/optimisation-routines` | GET | Suggestions d'optimisation des routines mÃ©nagÃ¨res | Non |
| 8 | `/analyse-document` | POST | Analyse document par photo (OCR + extraction donnÃ©es) | âœ… Image |
| 9 | `/estimation-travaux` | POST | Estimation coÃ»t travaux par photo | âœ… Image |
| 10 | `/planning-voyage` | POST | Planning voyage complet (itinÃ©raire, budget, checklist) | Non |
| 11 | `/recommandations-energie` | GET | Ã‰conomies d'Ã©nergie basÃ©es sur consommation rÃ©elle | Non |
| 12 | `/prediction-pannes` | GET | PrÃ©diction pannes Ã©quipements (historique entretien) | Non |
| 13 | `/suggestions-proactives` | GET | Suggestions proactives multi-modules contextuelles | Non |
| 14 | `/adaptations-meteo` | POST | Adaptations planning selon mÃ©tÃ©o (repas, activitÃ©s) | Non |

---

## DÃ©tail de chaque outil

### 1. Suggestions achats â€” GET `/suggestions-achats`

Analyse l'historique de courses et l'inventaire pour suggÃ©rer ce qu'il faut racheter.

**Auth** : Bearer token requis  
**Rate limit** : 10 req/min IA  
**RÃ©ponse** : `SuggestionsAchatsResponse`

```python
# Exemple de rÃ©ponse
{
  "suggestions": [
    {"nom": "PÃ¢tes", "raison": "Stock bas (2 paquets restants)", "priorite": "haute"},
    {"nom": "Lait", "raison": "ConsommÃ© chaque semaine", "priorite": "normale"}
  ],
  "contexte": "BasÃ© sur 8 semaines d'historique"
}
```

---

### 2. Planning adaptatif â€” POST `/planning-adaptatif`

GÃ©nÃ¨re un planning repas adaptÃ© aux conditions actuelles (mÃ©tÃ©o, budget restant, prÃ©fÃ©rences).

**Body** : `PlanningAdaptatifRequest`
```json
{
  "semaine_debut": "2026-04-07",
  "budget_restant": 120.50,
  "contraintes": ["sans_gluten"],
  "incorporer_meteo": true
}
```

**RÃ©ponse** : `PlanningAdaptatif` (7 jours de repas avec justifications)

---

### 3. Diagnostic plante â€” POST `/diagnostic-plante`

Analyse une photo de plante pour diagnostiquer maladies et suggÃ©rer soins.

**Body** : `multipart/form-data` avec champ `image` (JPG/PNG, max 5MB)  
**RÃ©ponse** : `DiagnosticPlante`
```json
{
  "diagnostic": "OÃ¯dium (champignon)",
  "confiance": 0.85,
  "soins_recommandes": ["Traiter avec fongicide", "RÃ©duire arrosage"],
  "urgence": "modÃ©rÃ©e"
}
```

---

### 4. PrÃ©vision dÃ©penses â€” GET `/prevision-depenses`

PrÃ©dit les dÃ©penses restantes du mois en cours.

**RÃ©ponse** : `PrevisionDepenses`
```json
{
  "prevu_fin_mois": 340.00,
  "budget_restant": 215.50,
  "tendance": "normale",
  "alertes": []
}
```

---

### 5. IdÃ©es cadeaux â€” POST `/idees-cadeaux`

GÃ©nÃ¨re des idÃ©es cadeaux personnalisÃ©es en fonction du profil et budget.

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

### 6. Analyse photo multi-usage â€” POST `/analyse-photo`

Analyse une photo et en extrait des informations selon le contexte (produit, plante, document, Ã©tat).

**Body** : `UploadFile` (JPG/PNG) + champ `contexte` optionnel  
**RÃ©ponse** : `AnalysePhotoMultiUsage`

---

### 7. Optimisation routines â€” GET `/optimisation-routines`

Analyse les routines existantes et suggÃ¨re des optimisations (temps, frÃ©quence, ordonnancement).

**RÃ©ponse** : `OptimisationRoutinesResponse`
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

### 8. Analyse document â€” POST `/analyse-document`

OCR + extraction structurÃ©e depuis photo d'un document (facture, contrat, ordonnance).

**Body** : `UploadFile` (JPG/PNG, max 10MB)  
**RÃ©ponse** : `DocumentAnalyse`
```json
{
  "type_document": "facture",
  "donnÃ©es_extraites": {
    "montant": 127.50,
    "date": "2026-03-15",
    "fournisseur": "EDF"
  },
  "texte_brut": "..."
}
```

---

### 9. Estimation travaux â€” POST `/estimation-travaux`

Estime le coÃ»t de travaux Ã  partir d'une photo.

**Body** : `EstimationTravauxRequest` + `UploadFile`  
**RÃ©ponse** : `EstimationTravauxPhoto`
```json
{
  "type_travaux": "Remplacement revÃªtement sol",
  "estimation_basse": 800,
  "estimation_haute": 1500,
  "facteurs": ["surface ~20mÂ²", "pose comprise", "matÃ©riaux standard"],
  "recommandations": ["Demander 3 devis"]
}
```

---

### 10. Planning voyage â€” POST `/planning-voyage`

GÃ©nÃ¨re un planning voyage dÃ©taillÃ© avec itinÃ©raire, budget et checklist.

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

**RÃ©ponse** : `PlanningVoyage` (itinÃ©raire jour par jour + checklist + budget estimÃ©)

---

### 11. Recommandations Ã©nergie â€” GET `/recommandations-energie`

Analyse la consommation Ã©nergÃ©tique et recommande des Ã©conomies.

**RÃ©ponse** : `RecommandationsEnergieResponse`
```json
{
  "economies_estimees_euros": 42.0,
  "recommandations": [
    {"action": "DÃ©caler lave-linge en heures creuses", "economie_mois": 8.50}
  ]
}
```

---

### 12. PrÃ©diction pannes â€” GET `/prediction-pannes`

PrÃ©dit les Ã©quipements susceptibles de tomber en panne basÃ© sur l'historique d'entretien.

**RÃ©ponse** : `PredictionsPannesResponse`

---

### 13. Suggestions proactives â€” GET `/suggestions-proactives`

Point d'entrÃ©e multi-modules â€” retourne des suggestions contextuelles depuis tous les domaines.

**RÃ©ponse** : `SuggestionsProactivesResponse`
```json
{
  "suggestions": [
    {"module": "cuisine", "message": "3 recettes Ã  utiliser avant pÃ©remption", "priorite": 1},
    {"module": "maison", "message": "Vidange voiture Ã  programmer (12 000 km)", "priorite": 2}
  ]
}
```

---

### 14. Adaptations mÃ©tÃ©o â€” POST `/adaptations-meteo`

Adapte les activitÃ©s et repas planifiÃ©s selon la mÃ©tÃ©o prÃ©vue.

**Body** : `AdaptationsMeteoRequest`  
**RÃ©ponse** : `AdaptationsMeteoResponse`

---

## Architecture technique

### Rate limiting IA

Tous les endpoints IA utilisent la dÃ©pendance `verifier_limite_debit_ia` (10 req/min vs 60 req/min standard).

```python
@router.post("/diagnostic-plante")
@gerer_exception_api
async def diagnostic_plante(
    image: UploadFile = File(...),
    _: None = Depends(verifier_limite_debit_ia),    # â† rate limit IA
    user: dict = Depends(require_auth),
) -> dict:
    ...
```

### Cache IA (cache sÃ©mantique)

Le `CacheIA` dans `src/core/ai/cache.py` stocke les rÃ©ponses d'appels IA identiques/similaires.
TTL par dÃ©faut : 1 heure. Les appels multimodaux (images) ne sont **pas** mis en cache.

### Client Mistral

```python
from src.core.ai import ClientIA, AnalyseurIA

client = ClientIA()
# Appel synchrone (dans un thread via executer_async)
reponse = client.appeler_sync(prompt, system_prompt=..., modele="mistral-large-latest")
```

### Circuit Breaker

Si Mistral AI est indisponible, le `CircuitBreaker` (`src/core/ai/circuit_breaker.py`) ouvre le circuit aprÃ¨s 5 Ã©checs consÃ©cutifs et retourne des rÃ©ponses de fallback.

---

## Limites et quotas

| ParamÃ¨tre | Valeur | Source config |
| ----------- | -------- | --------------- |
| Limite journaliÃ¨re globale | `AI_RATE_LIMIT_DAILY` | `src/core/constants.py` |
| Limite horaire | `AI_RATE_LIMIT_HOURLY` | `src/core/constants.py` |
| Rate limit HTTP IA | 10 req/min | `src/api/rate_limiting/` |
| Taille max image | 5 MB (10 MB pour documents) | Validation route |
| Formats image acceptÃ©s | JPG, PNG, WEBP | `UploadFile` validator |

---

## DÃ©pannage

| Erreur | Cause probable | Solution |
| -------- | --------------- | --------- |
| `429 Too Many Requests` | Rate limit IA atteint | Attendre 60s puis rÃ©essayer |
| `503 Service Unavailable` | Circuit breaker ouvert (Mistral down) | Attendre et rÃ©essayer (auto-reset aprÃ¨s 60s) |
| `422 Unprocessable Entity` | Body mal formÃ© | VÃ©rifier le schÃ©ma dans `/docs` (Swagger) |
| `500 Internal Server Error` | Erreur parsing rÃ©ponse Mistral | VÃ©rifier les logs `uvicorn` |

Pour tester manuellement : `http://localhost:8000/docs#/IA%20AvancÃ©e`
