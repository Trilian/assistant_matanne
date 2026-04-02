# Sprint 13 — IA & Backend Integration Guide

## Vue d'ensemble

Sprint 13 ajoute **6 services IA avancés** avec endpoints FastAPI correspondants. Ce guide explique:
- ✅ Comment les services IA fonctionnent (backend)
- ✅ Comment les hooks React utilisent l'API (frontend)
- ✅ Comment intégrer les composants d'exemple dans vos pages
- ✅ Patterns de validation, erreurs, et notifications

---

## Architecture Backend

### 6 Services IA (BaseAIService)

Tous les services héritent de `BaseAIService` avec:
- ✅ Limitation de débit intégrée
- ✅ Cache sémantique d'appels IA
- ✅ Parsing JSON automatique
- ✅ Résilience intégrée (retry, timeout, fallback)

#### 1. **InventaireAIService** (`src/services/inventaire/ia_service.py`)

```python
class InventaireAIService(BaseAIService):
    def predire_consommation(
        self, ingredient_nom: str, stock_kg: float, historique: list[float]
    ) -> dict:
        """Prédit les jours avant rupture de stock"""
        return {
            "ingredient_nom": ingredient_nom,
            "prochaine_consommation_estimee_j": 5,
            "confiance_prediction": 0.87,
            "recommandations": ["Acheter cette semaine"]
        }
```

**Endpoint**: `POST /api/v1/ia/sprint13/inventaire/prediction-consommation`

---

#### 2. **PlanningAIService** (`src/services/planning/ia_service.py`)

```python
class PlanningAIService(BaseAIService):
    def analyser_variete_semaine(self, planning: list[dict]) -> dict:
        """Analyse la variété nutritionnelle d'une semaine"""
        return {
            "variete_score": 78,  # 0-100
            "equilibre_nutritionnel": "Bon équilibre",
            "categories_presentes": ["Protéines", "Légumes", "Féculents"],
            "recommendations": ["Plus de fruits", "Varier les poissons"]
        }
```

**Endpoint**: `POST /api/v1/ia/sprint13/planning/analyse-variete`

---

#### 3. **MeteoImpactAIService** (`src/services/integrations/meteo_impact_ai.py`)

```python
class MeteoImpactAIService(BaseAIService):
    def analyser_impacts_meteo(
        self, previsions: list[dict], saison: str
    ) -> list[dict]:
        """Suggère des activités selon la météo"""
        return [
            {
                "date": "2026-04-02",
                "meteo": "Ensoleillé",
                "activites_suggerees": ["Pique-nique", "Parc", "Vélo"]
            }
        ]
```

**Endpoint**: `POST /api/v1/ia/sprint13/meteo/impacts`

---

#### 4. **HabitudesAIService** (`src/services/integrations/habitudes_ia.py`)

```python
class HabitudesAIService(BaseAIService):
    def analyser_habitude(
        self, habitude_nom: str, historique_7j: list[int], contexte: str
    ) -> dict:
        """Analyse la compliance & tendance d'une habitude"""
        return {
            "compliance_rate": 0.71,  # 71%
            "tendance": "croissante",  # "croissante" | "stable" | "décroissante"
            "score_tendance": 0.15,
            "recommendation": "Continuer, la tendance s'améliore!"
        }
```

**Endpoint**: `POST /api/v1/ia/sprint13/habitudes/analyse`

---

#### 5. **ProjetsMaisonAIService** (`src/services/maison/projets_ia_service.py`)

```python
class ProjetsMaisonAIService(BaseAIService):
    def estimer_projet(
        self, description: str, surface_m2: float, type_maison: str, 
        contraintes: list[str] = None
    ) -> dict:
        """Estime coûts et durée d'un projet maison"""
        return {
            "cout_estime_min": 800,  # €
            "cout_estime_max": 1200,
            "duree_estimee_j": 3,
            "professionnel_recommande": False,
            "complexite_estimee": "Faible",
            "etapes": ["Préparation", "Application", "Finition"]
        }
```

**Endpoint**: `POST /api/v1/ia/sprint13/maison/projets/estimation`

---

#### 6. **NutritionFamilleAIService** (`src/services/cuisine/nutrition_famille_ia.py`)

```python
class NutritionFamilleAIService(BaseAIService):
    def analyser_nutrition_personne(
        self, personne_nom: str, age: int, sexe: str, 
        activite_niveau: str, recettes_semaine: list[str],
        objectif_sante: str
    ) -> dict:
        """Analyse besoins nutritionnels (parfait pour Jules!)"""
        return {
            "calories_journalieres_recommandees": 1400,
            "proteines_g_j": 42,
            "glucides_g_j": 210,
            "lipides_g_j": 39,
            "notes_personnalisees": "Jules: adapter sans sel, mixer si nécessaire",
            "avertissements": []
        }
```

**Endpoint**: `POST /api/v1/ia/sprint13/nutrition/personne`

---

## Architecture Frontend

### Hooks React — TanStack Query

Tous les hooks utilisent **TanStack Query v5** avec:
- ✅ `useMutation()` pour les opérations
- ✅ Invalidation automatique des queries
- ✅ Notification Zustand des erreurs
- ✅ States: `isPending`, `isSuccess`, `isError`

#### Hook #1: `utilisePredictionConsommation()`
```typescript
const { mutate, isPending, data, error } = utilisePredictionConsommation()

mutate(
  {
    ingredient_nom: "Tomates",
    stock_actuel_kg: 2.5,
    historique_achat_mensuel: [2.5, 2.8, 2.2]
  },
  {
    onSuccess: (result) => console.log("Prochaine rupture:", result.prochaine_consommation_estimee_j),
    onError: () => ajouter_notification("Erreur", "error")
  }
)
```

#### Hook #2: `utiliseAnalyseVarietePlanning()`
```typescript
const { mutate, data } = utiliseAnalyseVarietePlanning()

mutate({
  planning_repas: [
    {
      date: "2026-04-02",
      petit_dejeuner: "Oeufs", 
      dejeuner: "Salade",
      diner: "Pâtes"
    }
  ]
})
```

#### Hook #3: `utiliseAnalyseImpactsMeteo()`
```typescript
const { mutate, data } = utiliseAnalyseImpactsMeteo()

mutate({
  previsions_7j: [...],
  saison: "printemps"
})
```

#### Hook #4: `utiliseAnalyseHabitudes()`
```typescript
const { mutate, data } = utiliseAnalyseHabitudes()

mutate({
  habitude_nom: "Sport matin",
  historique_7j: [1, 1, 0, 1, 1, 0, 1],
  description_contexte: "Morning exercise"
})
```

#### Hook #5: `utiliseEstimationProjet()`
```typescript
const { mutate, data } = utiliseEstimationProjet()

mutate({
  projet_description: "Repeindre la cuisine",
  surface_m2: 15,
  type_maison: "Maison ancienne",
  contraintes: ["Budget limité"]
})
```

#### Hook #6: `utiliseAnalyseNutrition()`
```typescript
const { mutate, data } = utiliseAnalyseNutrition()

mutate({
  personne_nom: "Jules",
  age_ans: 4,
  sexe: "M",
  activite_niveau: "intense",
  recettes_semaine: ["Pâtes", "Poulet"],
  objectif_sante: "Croissance saine"
})
```

---

## Intégration dans vos pages

### Exemple Cuisine (Prédiction Inventaire)

**Fichier**: `frontend/src/app/(app)/cuisine/page.tsx`

```typescript
'use client'

import { PredictionConsommationExample } from './composants/PredictionConsommationExample'

export default function CuisinePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Cuisine</h1>
      
      <section>
        <h2 className="text-lg font-semibold mb-4">Prédiction Stock</h2>
        <PredictionConsommationExample />
      </section>
    </div>
  )
}
```

### Exemple Planning (Variété Repas)

**Fichier**: `frontend/src/app/(app)/planning/page.tsx`

```typescript
'use client'

import { AnalyseVarieteExample } from './composants/AnalyseVarieteExample'

export default function PlanningPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Planning</h1>
      
      <section>
        <h2 className="text-lg font-semibold mb-4">Variété Semaine</h2>
        <AnalyseVarieteExample />
      </section>
    </div>
  )
}
```

### Pattern réutilisable

```typescript
'use client'

import { Card } from '@/src/composants/ui/card'
import { Button } from '@/src/composants/ui/button'
import { useNotifications } from '@/src/magasins/store-notifications'
import { utiliserXXXXX } from '@/src/crochets/utiliser-sprint13-ia'

export function MonComposant() {
  const { mutate, isPending, data } = utiliserXXXXX()
  const { ajouter_notification } = useNotifications()

  const handleAction = () => {
    mutate(
      { /* payload */ },
      {
        onSuccess: (result) => {
          ajouter_notification("Succès!", "success")
          // Traiter result
        },
        onError: () => {
          ajouter_notification("Erreur", "error")
        }
      }
    )
  }

  return (
    <Card className="p-6">
      {/* Form inputs */}
      <Button onClick={handleAction} disabled={isPending}>
        {isPending ? 'Chargement...' : 'Analyser'}
      </Button>
      
      {data && <div>{/* Display results */}</div>}
    </Card>
  )
}
```

---

## Validation & Erreurs

### Validation Backend (Pydantic)

Tous les schémas de requête valident les données:

```python
# src/api/schemas/ia_sprint13.py
class PredictionConsommationRequest(BaseModel):
    ingredient_nom: str = Field(..., min_length=1, max_length=100)
    stock_actuel_kg: float = Field(..., gt=0, le=1000)  # > 0
    historique_achat_mensuel: list[float] = Field(..., min_items=1, max_items=12)
```

### Erreurs FrontEnd

```typescript
const { mutate, isError, error } = utiliserXXXXX()

mutate(payload, {
  onError: (err: any) => {
    const message = err.response?.data?.detail || "Erreur inconnue"
    ajouter_notification(message, "error")
  }
})
```

### Erreurs Backend

Les erreurs sont catchées et retournées:

```python
# 400 Bad Request (validation échouée)
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "stock_actuel_kg"],
      "msg": "ensure this value is greater than 0"
    }
  ]
}

# 401 Unauthorized
{
  "detail": "Credentials not provided"
}

# 429 Too Many Requests (Rate limit IA)
{
  "detail": "IA rate limit exceeded"
}

# 500 Internal Server Error
{
  "detail": "Unexpected error during prediction"
}
```

---

## Flux complet d'exemple

**Scenario**: Analyser nutrition pour Jules

1. **Frontend**: Utilisateur ouvre `/cuisine`
2. **Frontend**: Saisit Jules (4 ans, M, modéré, recettes, croissance)
3. **Frontend**: Clique "Analyser"
4. **Frontend**: Hook `utiliseAnalyseNutrition()` déclenche `mutate()`
5. **Hook**: Ajoute bearer token JWT automatiquement (intercepteur Axios)
6. **Hook**: Envoie POST `/api/v1/ia/sprint13/nutrition/personne`
7. **Backend**: Route reçoit + valide requête (Pydantic)
8. **Backend**: Vérifie rate limit IA
9. **Backend**: Appelle `NutritionFamilleAIService.analyser_nutrition_personne()`
10. **Service**: Limite de débit + cache vérifiés
11. **Service**: Appel IA Mistral avec prompt système
12. **Service**: Parse réponse JSON en dict Python
13. **Backend**: Retourne 200 + dict résultat
14. **Frontend**: Hook re-render composant avec `data`
15. **Frontend**: Affiche calories/protéines/glucides/lipides + notes
16. **Frontend**: Notification "Succès!" affichée

---

## Tests

### Tests Backend

```bash
# Tous les tests Sprint 13 (23 tests)
python -m pytest tests/services/test_sprint13_simple.py tests/api/test_routes_ia_sprint13.py -v

# Tests E2E intégration
python -m pytest tests/e2e/test_sprint13_integration.py -v

# Résultats: 23 unit tests + 11 E2E tests = 34 tests totaux
```

### Tests Frontend (futur)

```bash
# Tests composants React
cd frontend && npm test -- Prediction

# Tests E2E Playwright
npx playwright test --grep "sprint13"
```

---

## Fichiers créés

### Backend
- ✅ `src/services/inventaire/ia_service.py`
- ✅ `src/services/planning/ia_service.py`
- ✅ `src/services/integrations/meteo_impact_ai.py`
- ✅ `src/services/integrations/habitudes_ia.py`
- ✅ `src/services/maison/projets_ia_service.py`
- ✅ `src/services/cuisine/nutrition_famille_ia.py`
- ✅ `src/api/routes/ia_sprint13.py` (6 endpoints)
- ✅ `src/api/schemas/ia_sprint13.py` (6 request/response schemas)
- ✅ `tests/services/test_sprint13_simple.py` (15 tests)
- ✅ `tests/api/test_routes_ia_sprint13.py` (8 tests)
- ✅ `tests/e2e/test_sprint13_integration.py` (11 tests)

### Frontend
- ✅ `frontend/src/bibliotheque/api/ia-sprint13.ts` (6 clients API)
- ✅ `frontend/src/crochets/utiliser-sprint13-ia.ts` (6 hooks TanStack Query)
- ✅ `frontend/src/app/(app)/cuisine/composants/PredictionConsommationExample.tsx`
- ✅ `frontend/src/app/(app)/planning/composants/AnalyseVarieteExample.tsx`
- ✅ `frontend/src/app/(app)/outils/composants/AnalyseMeteoExample.tsx`
- ✅ `frontend/src/app/(app)/famille/composants/AnalyseHabitesExample.tsx`
- ✅ `frontend/src/app/(app)/maison/composants/EstimationProjetExample.tsx`
- ✅ `frontend/src/app/(app)/cuisine/composants/AnalyseNutritionExample.tsx`

### Documentation
- ✅ Cette guide (`docs/SPRINT13_INTEGRATION_GUIDE.md`)

---

## Next Steps

1. **Intégrer les exemples** dans les pages de chaque module
2. **Tester les composants** avec Playwright E2E
3. **Customiser les appels API** selon les besoins métier
4. **Ajouter des validations** côté frontend supplémentaires
5. **Monitorer les appels IA** via Prometheus/Grafana

---

## Support

- Questions backend? → Voir `src/core/ai/` et `BaseAIService`
- Questions frontend? → Voir `frontend/src/crochets/utiliser-sprint13-ia.ts`
- Questions API? → Documentation OpenAPI: `http://localhost:8000/docs`
- Questions validation? → Voir `src/api/schemas/ia_sprint13.py`
