# Guide ? Module IA Avanc?e

> **Routes** : `GET|POST /api/v1/ia-avancee/*`  
> **Rate limiting** : 10 req/min (plafonn? par `verifier_limite_debit_ia`)  
> **Mod?le** : Mistral AI (configur? dans `.env.local`)  
> **Service** : `src/services/ia_avancee/service.py`

---

## Vue d'ensemble ? Les 14 outils IA

| # | Endpoint | M?thode | Description | Multimodal |
| --- | ---------- | --------- | ------------- | ----------- |
| 1 | `/suggestions-achats` | GET | Suggestions achats bas?es sur l'historique de courses | Non |
| 2 | `/planning-adaptatif` | POST | Planning repas adapt? (m?t?o + budget + pr?f?rences) | Non |
| 3 | `/diagnostic-plante` | POST | Diagnostic plante par photo (maladie, soin recommand?) | ? Image |
| 4 | `/prevision-depenses` | GET | Pr?vision d?penses de fin de mois | Non |
| 5 | `/idees-cadeaux` | POST | Id?es cadeaux personnalis?es pour anniversaire | Non |
| 6 | `/analyse-photo` | POST | Analyse photo multi-usage (contexte auto-d?tect?) | ? Image |
| 7 | `/optimisation-routines` | GET | Suggestions d'optimisation des routines m?nag?res | Non |
| 8 | `/analyse-document` | POST | Analyse document par photo (OCR + extraction donn?es) | ? Image |
| 9 | `/estimation-travaux` | POST | Estimation co?t travaux par photo | ? Image |
| 10 | `/planning-voyage` | POST | Planning voyage complet (itin?raire, budget, checklist) | Non |
| 11 | `/recommandations-energie` | GET | ?conomies d'?nergie bas?es sur consommation r?elle | Non |
| 12 | `/prediction-pannes` | GET | Pr?diction pannes ?quipements (historique entretien) | Non |
| 13 | `/suggestions-proactives` | GET | Suggestions proactives multi-modules contextuelles | Non |
| 14 | `/adaptations-meteo` | POST | Adaptations planning selon m?t?o (repas, activit?s) | Non |

---

## D?tail de chaque outil

### 1. Suggestions achats ? GET `/suggestions-achats`

Analyse l'historique de courses et l'inventaire pour sugg?rer ce qu'il faut racheter.

**Auth** : Bearer token requis  
**Rate limit** : 10 req/min IA  
**R?ponse** : `SuggestionsAchatsResponse`

```python
# Exemple de r?ponse
{
  "suggestions": [
    {"nom": "P?tes", "raison": "Stock bas (2 paquets restants)", "priorite": "haute"},
    {"nom": "Lait", "raison": "Consomm? chaque semaine", "priorite": "normale"}
  ],
  "contexte": "Bas? sur 8 semaines d'historique"
}
```

---

### 2. Planning adaptatif ? POST `/planning-adaptatif`

G?n?re un planning repas adapt? aux conditions actuelles (m?t?o, budget restant, pr?f?rences).

**Body** : `PlanningAdaptatifRequest`
```json
{
  "semaine_debut": "2026-04-07",
  "budget_restant": 120.50,
  "contraintes": ["sans_gluten"],
  "incorporer_meteo": true
}
```

**R?ponse** : `PlanningAdaptatif` (7 jours de repas avec justifications)

---

### 3. Diagnostic plante ? POST `/diagnostic-plante`

Analyse une photo de plante pour diagnostiquer maladies et sugg?rer soins.

**Body** : `multipart/form-data` avec champ `image` (JPG/PNG, max 5MB)  
**R?ponse** : `DiagnosticPlante`
```json
{
  "diagnostic": "O?dium (champignon)",
  "confiance": 0.85,
  "soins_recommandes": ["Traiter avec fongicide", "R?duire arrosage"],
  "urgence": "mod?r?e"
}
```

---

### 4. Pr?vision d?penses ? GET `/prevision-depenses`

Pr?dit les d?penses restantes du mois en cours.

**R?ponse** : `PrevisionDepenses`
```json
{
  "prevu_fin_mois": 340.00,
  "budget_restant": 215.50,
  "tendance": "normale",
  "alertes": []
}
```

---

### 5. Id?es cadeaux ? POST `/idees-cadeaux`

G?n?re des id?es cadeaux personnalis?es en fonction du profil et budget.

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

### 6. Analyse photo multi-usage ? POST `/analyse-photo`

Analyse une photo et en extrait des informations selon le contexte (produit, plante, document, ?tat).

**Body** : `UploadFile` (JPG/PNG) + champ `contexte` optionnel  
**R?ponse** : `AnalysePhotoMultiUsage`

---

### 7. Optimisation routines ? GET `/optimisation-routines`

Analyse les routines existantes et sugg?re des optimisations (temps, fr?quence, ordonnancement).

**R?ponse** : `OptimisationRoutinesResponse`
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

### 8. Analyse document ? POST `/analyse-document`

OCR + extraction structur?e depuis photo d'un document (facture, contrat, ordonnance).

**Body** : `UploadFile` (JPG/PNG, max 10MB)  
**R?ponse** : `DocumentAnalyse`
```json
{
  "type_document": "facture",
  "donn?es_extraites": {
    "montant": 127.50,
    "date": "2026-03-15",
    "fournisseur": "EDF"
  },
  "texte_brut": "..."
}
```

---

### 9. Estimation travaux ? POST `/estimation-travaux`

Estime le co?t de travaux ? partir d'une photo.

**Body** : `EstimationTravauxRequest` + `UploadFile`  
**R?ponse** : `EstimationTravauxPhoto`
```json
{
  "type_travaux": "Remplacement rev?tement sol",
  "estimation_basse": 800,
  "estimation_haute": 1500,
  "facteurs": ["surface ~20m?", "pose comprise", "mat?riaux standard"],
  "recommandations": ["Demander 3 devis"]
}
```

---

### 10. Planning voyage ? POST `/planning-voyage`

G?n?re un planning voyage d?taill? avec itin?raire, budget et checklist.

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

**R?ponse** : `PlanningVoyage` (itin?raire jour par jour + checklist + budget estim?)

---

### 11. Recommandations ?nergie ? GET `/recommandations-energie`

Analyse la consommation ?nerg?tique et recommande des ?conomies.

**R?ponse** : `RecommandationsEnergieResponse`
```json
{
  "economies_estimees_euros": 42.0,
  "recommandations": [
    {"action": "D?caler lave-linge en heures creuses", "economie_mois": 8.50}
  ]
}
```

---

### 12. Pr?diction pannes ? GET `/prediction-pannes`

Pr?dit les ?quipements susceptibles de tomber en panne bas? sur l'historique d'entretien.

**R?ponse** : `PredictionsPannesResponse`

---

### 13. Suggestions proactives ? GET `/suggestions-proactives`

Point d'entr?e multi-modules ? retourne des suggestions contextuelles depuis tous les domaines.

**R?ponse** : `SuggestionsProactivesResponse`
```json
{
  "suggestions": [
    {"module": "cuisine", "message": "3 recettes ? utiliser avant p?remption", "priorite": 1},
    {"module": "maison", "message": "Vidange voiture ? programmer (12 000 km)", "priorite": 2}
  ]
}
```

---

### 14. Adaptations m?t?o ? POST `/adaptations-meteo`

Adapte les activit?s et repas planifi?s selon la m?t?o pr?vue.

**Body** : `AdaptationsMeteoRequest`  
**R?ponse** : `AdaptationsMeteoResponse`

---

## Architecture technique

### Rate limiting IA

Tous les endpoints IA utilisent la d?pendance `verifier_limite_debit_ia` (10 req/min vs 60 req/min standard).

```python
@router.post("/diagnostic-plante")
@gerer_exception_api
async def diagnostic_plante(
    image: UploadFile = File(...),
    _: None = Depends(verifier_limite_debit_ia),    # ? rate limit IA
    user: dict = Depends(require_auth),
) -> dict:
    ...
```

### Cache IA (cache s?mantique)

Le `CacheIA` dans `src/core/ai/cache.py` stocke les r?ponses d'appels IA identiques/similaires.
TTL par d?faut : 1 heure. Les appels multimodaux (images) ne sont **pas** mis en cache.

### Client Mistral

```python
from src.core.ai import ClientIA, AnalyseurIA

client = ClientIA()
# Appel synchrone (dans un thread via executer_async)
reponse = client.appeler_sync(prompt, system_prompt=..., modele="mistral-large-latest")
```

### Circuit Breaker

Si Mistral AI est indisponible, le `CircuitBreaker` (`src/core/ai/circuit_breaker.py`) ouvre le circuit apr?s 5 ?checs cons?cutifs et retourne des r?ponses de fallback.

---

## Limites et quotas

| Param?tre | Valeur | Source config |
| ----------- | -------- | --------------- |
| Limite journali?re globale | `AI_RATE_LIMIT_DAILY` | `src/core/constants.py` |
| Limite horaire | `AI_RATE_LIMIT_HOURLY` | `src/core/constants.py` |
| Rate limit HTTP IA | 10 req/min | `src/api/rate_limiting/` |
| Taille max image | 5 MB (10 MB pour documents) | Validation route |
| Formats image accept?s | JPG, PNG, WEBP | `UploadFile` validator |

---

## D?pannage

| Erreur | Cause probable | Solution |
| -------- | --------------- | --------- |
| `429 Too Many Requests` | Rate limit IA atteint | Attendre 60s puis r?essayer |
| `503 Service Unavailable` | Circuit breaker ouvert (Mistral down) | Attendre et r?essayer (auto-reset apr?s 60s) |
| `422 Unprocessable Entity` | Body mal form? | V?rifier le sch?ma dans `/docs` (Swagger) |
| `500 Internal Server Error` | Erreur parsing r?ponse Mistral | V?rifier les logs `uvicorn` |

Pour tester manuellement : `http://localhost:8000/docs#/IA%20Avanc?e`
