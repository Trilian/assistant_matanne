'use client'

import { useState } from 'react'
import { Button } from '@/src/composants/ui/button'
import { Card } from '@/src/composants/ui/card'
import { Input } from '@/src/composants/ui/input'
import { useNotifications } from '@/src/magasins/store-notifications'
import { utiliseAnalyseHabitudes } from '@/src/crochets/utiliser-ia-modules'

/**
 * Example Component: Family Habit Analysis
 * ──────────────────────────────────────────
 * Demonstrates the Sprint 13 IA hook for tracking & analyzing family habits
 * Located in: frontend/src/app/(app)/famille/composants/AnalyseHabitesExample.tsx
 *
 * Usage:
 * - User inputs habit name + 7-day compliance history (0 or 1)
 * - Component calls mutation to analyze trends
 * - Results show compliance rate + trend direction
 * - Useful for tracking routines, exercise, chores, etc.
 */

export function AnalyseHabitesExample() {
  const [habitNom, setHabitNom] = useState('')
  const [contexte, setContexte] = useState('')
  const [historique, setHistorique] = useState<number[]>([1, 1, 0, 1, 1, 0, 1])

  const { mutate: analyserHabitude, isPending, data } = utiliseAnalyseHabitudes()
  const { ajouter_notification } = useNotifications()

  const handleAnalyze = () => {
    if (!habitNom) {
      ajouter_notification('Veuillez entrer le nom de l\'habitude', 'erreur')
      return
    }

    analyserHabitude(
      {
        habitude_nom: habitNom,
        historique_7j: historique,
        description_contexte: contexte,
      },
      {
        onSuccess: (result) => {
          ajouter_notification(
            `Compliance: ${(result.compliance_rate * 100).toFixed(0)}% - Tendance: ${result.tendance}`,
            'succes'
          )
        },
        onError: () => {
          ajouter_notification('Erreur lors de l\'analyse', 'erreur')
        },
      }
    )
  }

  const toggleDay = (index: number) => {
    const newHistorique = [...historique]
    newHistorique[index] = newHistorique[index] === 1 ? 0 : 1
    setHistorique(newHistorique)
  }

  return (
    <Card className="p-6 max-w-md">
      <h2 className="text-xl font-bold mb-4">Analyse Habitude</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            Habitude (Ex: Sport matin)
          </label>
          <Input
            value={habitNom}
            onChange={(e) => setHabitNom(e.target.value)}
            placeholder="Sport, Lecture, Méditation..."
            disabled={isPending}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Contexte (optionnel)
          </label>
          <Input
            value={contexte}
            onChange={(e) => setContexte(e.target.value)}
            placeholder="Détails contextuels..."
            disabled={isPending}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            7 derniers jours (clic pour toggle)
          </label>
          <div className="flex gap-2">
            {historique.map((jour, idx) => (
              <button
                key={idx}
                onClick={() => toggleDay(idx)}
                className={`flex-1 h-10 rounded text-xs font-medium transition-colors ${
                  jour === 1
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-200 text-gray-700'
                }`}
                disabled={isPending}
              >
                J{idx + 1}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {historique.filter((h) => h === 1).length}/7 jours complétés
          </p>
        </div>

        <Button
          onClick={handleAnalyze}
          disabled={isPending}
          className="w-full"
        >
          {isPending ? 'Analyse...' : 'Analyser'}
        </Button>

        {data && (
          <div className="mt-4 p-3 bg-purple-50 rounded">
            <p className="text-sm">
              <strong>Compliance:</strong>{' '}
              {(data.compliance_rate * 100).toFixed(0)}%
            </p>
            <p className="text-sm">
              <strong>Tendance:</strong>{' '}
              {data.tendance === 'croissante'
                ? '📈 Croissante'
                : data.tendance === 'décroissante'
                  ? '📉 Décroissante'
                  : '➡️ Stable'}
            </p>
            <p className="text-sm">
              <strong>Score:</strong> {data.score_tendance.toFixed(2)}
            </p>
          </div>
        )}
      </div>
    </Card>
  )
}
