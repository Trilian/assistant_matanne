'use client'

import { useState } from 'react'
import { Button } from '@/src/composants/ui/button'
import { Card } from '@/src/composants/ui/card'
import { Input } from '@/src/composants/ui/input'
import { useNotifications } from '@/src/magasins/store-notifications'
import { utiliseAnalyseVarietePlanning } from '@/src/crochets/utiliser-ia-modules'

/**
 * Example Component: Meal Variety Analysis
 * ──────────────────────────────────────────
 * Demonstrates the IA hook for analyzing meal variety over a week
 * Located in: frontend/src/app/(app)/planning/composants/AnalyseVarieteExample.tsx
 *
 * Usage:
 * - User inputs meal planning for 1-7 days
 * - Component calls mutation to analyze variety score
 * - Results show nutritional balance + categories
 * - Used for quick meal plan validation before shopping
 */

interface MealDay {
  date: string
  petit_dejeuner: string
  dejeuner: string
  diner: string
}

export function AnalyseVarieteExample() {
  const [jours, setJours] = useState<MealDay[]>([
    {
      date: '2026-04-02',
      petit_dejeuner: '',
      dejeuner: '',
      diner: '',
    },
  ])

  const { mutate: analyserVariete, isPending, data } = utiliseAnalyseVarietePlanning()
  const { ajouter_notification } = useNotifications()

  const handleAnalyze = () => {
    if (jours.some((j) => !j.petit_dejeuner || !j.dejeuner || !j.diner)) {
      ajouter_notification('Veuillez remplir tous les repas', 'erreur')
      return
    }

    analyserVariete(
      { planning_repas: jours },
      {
        onSuccess: (result) => {
          ajouter_notification(
            `Variété: ${result.variete_score}/100 - ${result.equilibre_nutritionnel}`,
            'succes'
          )
        },
        onError: () => {
          ajouter_notification('Erreur lors de l\'analyse', 'erreur')
        },
      }
    )
  }

  const updateMeal = (
    index: number,
    field: 'petit_dejeuner' | 'dejeuner' | 'diner',
    value: string
  ) => {
    const newJours = [...jours]
    newJours[index][field] = value
    setJours(newJours)
  }

  return (
    <Card className="p-6">
      <h2 className="text-xl font-bold mb-4">Analyse Variété Semaine</h2>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {jours.map((jour, idx) => (
          <div key={idx} className="p-3 border rounded">
            <p className="text-sm font-medium mb-2">{jour.date}</p>
            <div className="grid grid-cols-3 gap-2">
              <Input
                value={jour.petit_dejeuner}
                onChange={(e) =>
                  updateMeal(idx, 'petit_dejeuner', e.target.value)
                }
                placeholder="Petit déj"
                size={25}
              />
              <Input
                value={jour.dejeuner}
                onChange={(e) =>
                  updateMeal(idx, 'dejeuner', e.target.value)
                }
                placeholder="Déjeuner"
                size={25}
              />
              <Input
                value={jour.diner}
                onChange={(e) =>
                  updateMeal(idx, 'diner', e.target.value)
                }
                placeholder="Dîner"
                size={25}
              />
            </div>
          </div>
        ))}
      </div>

      <Button
        onClick={handleAnalyze}
        disabled={isPending}
        className="w-full mt-4"
      >
        {isPending ? 'Analyse...' : 'Analyser'}
      </Button>

      {data && (
        <div className="mt-4 p-3 bg-green-50 rounded">
          <p className="text-sm font-semibold">
            Score Variété: {data.variete_score}/100
          </p>
          <p className="text-sm">
            Équilibre: {data.equilibre_nutritionnel}
          </p>
          <p className="text-sm">
            Catégories: {data.categories_presentes.join(', ')}
          </p>
        </div>
      )}
    </Card>
  )
}
