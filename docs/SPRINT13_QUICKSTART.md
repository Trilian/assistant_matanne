# Sprint 13 Quick Start — 5 min Integration

Want to use the 6 new AI features? Here's the fastest path:

---

## 1. Copy the hook you need (2 min)

Choose one from 6 available hooked:

```typescript
// In your component:
import { utilisePredictionConsommation } from '@/src/crochets/utiliser-sprint13-ia'
// OR:
import { utiliseAnalyseVarietePlanning } from '@/src/crochets/utiliser-sprint13-ia'
// OR:
import { utiliseAnalyseImpactsMeteo } from '@/src/crochets/utiliser-sprint13-ia'
// OR:
import { utiliseAnalyseHabitudes } from '@/src/crochets/utiliser-sprint13-ia'
// OR:
import { utiliseEstimationProjet } from '@/src/crochets/utiliser-sprint13-ia'
// OR:
import { utiliseAnalyseNutrition } from '@/src/crochets/utiliser-sprint13-ia'
```

---

## 2. Use the hook in your component (2 min)

```typescript
'use client'

import { useState } from 'react'
import { useNotifications } from '@/src/magasins/store-notifications'
import { utilisePredictionConsommation } from '@/src/crochets/utiliser-sprint13-ia'

export function MaComposant() {
  const [input, setInput] = useState('')
  const { mutate, isPending, data } = utilisePredictionConsommation()
  const { ajouter_notification } = useNotifications()

  const handleSubmit = () => {
    mutate(
      {
        ingredient_nom: input,
        stock_actuel_kg: 2.5,
        historique_achat_mensuel: [2.5, 2.8, 2.2]
      },
      {
        onSuccess: (result) => {
          ajouter_notification(`${result.prochaine_consommation_estimee_j} jours`, 'success')
        },
        onError: () => {
          ajouter_notification('Erreur', 'error')
        }
      }
    )
  }

  return (
    <div>
      <input value={input} onChange={(e) => setInput(e.target.value)} />
      <button onClick={handleSubmit} disabled={isPending}>
        {isPending ? 'Chargement...' : 'Analyser'}
      </button>
      {data && <div>Résultat: {JSON.stringify(data)}</div>}
    </div>
  )
}
```

---

## 3. See the example (1 min)

Want a full working example? Copy from one of these:

- **Inventory**: `frontend/src/app/(app)/cuisine/composants/PredictionConsommationExample.tsx`
- **Meals**: `frontend/src/app/(app)/planning/composants/AnalyseVarieteExample.tsx`
- **Weather**: `frontend/src/app/(app)/outils/composants/AnalyseMeteoExample.tsx`
- **Habits**: `frontend/src/app/(app)/famille/composants/AnalyseHabitesExample.tsx`
- **Projects**: `frontend/src/app/(app)/maison/composants/EstimationProjetExample.tsx`
- **Nutrition**: `frontend/src/app/(app)/cuisine/composants/AnalyseNutritionExample.tsx`

---

## API Reference

### 1. Prediction Consommation (Inventory)
```typescript
utilisePredictionConsommation().mutate({
  ingredient_nom: "Tomates",
  stock_actuel_kg: 2.5,
  historique_achat_mensuel: [2.5, 2.8, 2.2, 3.0]
})

// Response:
{
  ingredient_nom: "Tomates",
  prochaine_consommation_estimee_j: 5,
  confiance_prediction: 0.87,
  recommandations: ["Acheter cette semaine"]
}
```

### 2. Analyse Variete Planning (Meals)
```typescript
utiliseAnalyseVarietePlanning().mutate({
  planning_repas: [
    {
      date: "2026-04-02",
      petit_dejeuner: "Oeufs",
      dejeuner: "Salade",
      diner: "Pâtes"
    }
  ]
})

// Response:
{
  variete_score: 78,
  equilibre_nutritionnel: "Bon équilibre",
  categories_presentes: ["Protéines", "Légumes"],
  recommandations: ["Varier les poissons"]
}
```

### 3. Analyse Impacts Meteo (Weather)
```typescript
utiliseAnalyseImpactsMeteo().mutate({
  previsions_7j: [{
    date: "2026-04-02",
    meteo: "Ensoleillé",
    temperature_min: 10,
    temperature_max: 18,
    precipitation_mm: 0
  }],
  saison: "printemps"
})

// Response:
[{
  date: "2026-04-02",
  meteo: "Ensoleillé",
  activites_suggerees: ["Pique-nique", "Parc", "Vélo"]
}]
```

### 4. Analyse Habitudes (Habits)
```typescript
utiliseAnalyseHabitudes().mutate({
  habitude_nom: "Sport matin",
  historique_7j: [1, 1, 0, 1, 1, 0, 1],
  description_contexte: "Morning exercise"
})

// Response:
{
  compliance_rate: 0.71,
  tendance: "croissante",
  score_tendance: 0.15,
  recommendation: "Continuer, bravo!"
}
```

### 5. Estimation Projet (Projects)
```typescript
utiliseEstimationProjet().mutate({
  projet_description: "Repeindre la cuisine",
  surface_m2: 15,
  type_maison: "Maison ancienne",
  contraintes: ["Budget limité"]
})

// Response:
{
  cout_estime_min: 800,
  cout_estime_max: 1200,
  duree_estimee_j: 3,
  professionnel_recommande: false,
  complexite_estimee: "Faible",
  etapes: ["Préparation", "Application"]
}
```

### 6. Analyse Nutrition (Jules!)
```typescript
utiliseAnalyseNutrition().mutate({
  personne_nom: "Jules",
  age_ans: 4,
  sexe: "M",
  activite_niveau: "intense",
  recettes_semaine: ["Pâtes", "Poulet"],
  objectif_sante: "Croissance saine"
})

// Response:
{
  calories_journalieres_recommandees: 1400,
  proteines_g_j: 42,
  glucides_g_j: 210,
  lipides_g_j: 39,
  notes_personnalisees: "Jules: pas de sel, mixer si needed",
  avertissements: []
}
```

---

## Error Handling

All hooks automatically handle errors + show notifications:

```typescript
const { mutate, isError, error } = utiliseXXXXX()

mutate(payload, {
  onError: (err: any) => {
    // Notification automatically shown via Zustand
    console.error(err.response?.data?.detail)
  }
})
```

Possible errors:
- `400`: Bad validation (check payload format)
- `401`: Auth failed (check token)
- `429`: Rate limit (wait & retry)
- `500`: Server error (check backend logs)

---

## Testing Your Integration

Test the endpoint directly:

```bash
# Terminal 1: Start backend
python manage.py run

# Terminal 2: Make a test request
curl -X POST http://localhost:8000/api/v1/ia/sprint13/inventaire/prediction-consommation \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredient_nom": "Tomates",
    "stock_actuel_kg": 2.5,
    "historique_achat_mensuel": [2.5, 2.8]
  }'

# Expected response: 200 OK with prediction data
```

Or test in Swagger UI: http://localhost:8000/docs

---

## Common Patterns

### Pattern: Form -> Mutation -> Display

```typescript
export function MonAnalyse() {
  const [formData, setFormData] = useState({})
  const { mutate, data, isPending } = utiliserXXXX()

  return (
    <form onSubmit={(e) => {
      e.preventDefault()
      mutate(formData)
    }}>
      {/* Form fields */}
      <button disabled={isPending}>Analyser</button>
      {data && <Results data={data} />}
    </form>
  )
}
```

### Pattern: List -> Select -> Analyze

```typescript
export function SelectionAnalyse() {
  const [selected, setSelected] = useState<Item>()
  const { mutate } = utiliserXXXX()

  const handleSelect = (item: Item) => {
    setSelected(item)
    mutate({...item})
  }

  return (
    <div>
      {items.map(item => 
        <button onClick={() => handleSelect(item)}>
          {item.name}
        </button>
      )}
    </div>
  )
}
```

### Pattern: Real-time Update

```typescript
export function RealtimeAnalyse() {
  const [input, setInput] = useState('')
  const { mutate } = utiliserXXXX()

  useEffect(() => {
    const timer = setTimeout(() => {
      if (input) mutate({keyword: input})
    }, 500) // Debounce

    return () => clearTimeout(timer)
  }, [input])

  return <input value={input} onChange={(e) => setInput(e.target.value)} />
}
```

---

## FAQ

**Q: My hook returns 401?** 
A: Check your JWT token is valid. Auth is required for all endpoints.

**Q: Getting 429 rate limit error?**
A: IA endpoints limited to 10 req/min per user. Wait 1 min & retry.

**Q: Component not showing results?**
A: Check:
1. Wrapped in `<QueryClientProvider>` ? (see `src/fournisseurs/`)
2. Response is JSON? (check Network tab)
3. `data` state is set? (check `isPending` = false)

**Q: Want full documentation?**
A: See `docs/SPRINT13_INTEGRATION_GUIDE.md`

**Q: Tests failing?**
A: Run: `python -m pytest tests/e2e/test_sprint13_integration.py -v`

---

## Deploy

1. Backend: Deployed automatically (railway.app)
2. Frontend: Deployed automatically (vercel.com)
3. Test in production: Just use the hooks!

---

**That's it! You're ready to use Sprint 13 IA features! 🚀**

Questions? Check `docs/SPRINT13_INTEGRATION_GUIDE.md` or the component examples.
