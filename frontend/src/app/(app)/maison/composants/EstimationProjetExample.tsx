'use client'

import { useState } from 'react'
import { Button } from '@/src/composants/ui/button'
import { Card } from '@/src/composants/ui/card'
import { Input } from '@/src/composants/ui/input'
import { Checkbox } from '@/src/composants/ui/checkbox'
import { useNotifications } from '@/src/magasins/store-notifications'
import { utiliseEstimationProjet } from '@/src/crochets/utiliser-ia-modules'

/**
 * Example Component: Home Project Estimation
 * ────────────────────────────────────────────
 * Demonstrates the Sprint 13 IA hook for estimating home project costs & duration
 * Located in: frontend/src/app/(app)/maison/composants/EstimationProjetExample.tsx
 *
 * Usage:
 * - User describes project + surface + type of house
 * - Component optionally accepts constraints (budget, time)
 * - Mutation returns cost/duration estimates
 * - Great for project planning & budget tracking
 */

const CONTRAINTES_PREDEFINIES = [
  'Budget limité',
  'Peu de temps',
  'DIY préféré',
  'Professionnel requis',
  'Urgent',
  'Écologique',
]

export function EstimationProjetExample() {
  const [description, setDescription] = useState('')
  const [surfaceM2, setSurfaceM2] = useState('')
  const [typeHabit, setTypeHabit] = useState('Maison moderne')
  const [contraintes, setContraintes] = useState<string[]>([])

  const { mutate: estimerProjet, isPending, data } = utiliseEstimationProjet()
  const { ajouter_notification } = useNotifications()

  const handleEstimate = () => {
    if (!description || !surfaceM2) {
      ajouter_notification('Veuillez remplir description et surface', 'erreur')
      return
    }

    estimerProjet(
      {
        projet_description: description,
        surface_m2: parseFloat(surfaceM2),
        type_maison: typeHabit,
        contraintes: contraintes.length > 0 ? contraintes : undefined,
      },
      {
        onSuccess: (result) => {
          ajouter_notification(
            `Budget: €${result.cout_estime_min}-${result.cout_estime_max}`,
            'succes'
          )
        },
        onError: () => {
          ajouter_notification('Erreur lors de l\'estimation', 'erreur')
        },
      }
    )
  }

  const toggleContrainte = (c: string) => {
    setContraintes((prev) =>
      prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c]
    )
  }

  return (
    <Card className="p-6">
      <h2 className="text-xl font-bold mb-4">Estimation Projet Maison</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            Description du projet
          </label>
          <Input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Ex: Repeindre la cuisine"
            disabled={isPending}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Surface (m²)</label>
            <Input
              value={surfaceM2}
              onChange={(e) => setSurfaceM2(e.target.value)}
              placeholder="15"
              type="number"
              disabled={isPending}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Type habitation</label>
            <Input
              value={typeHabit}
              onChange={(e) => setTypeHabit(e.target.value)}
              placeholder="Maison moderne"
              disabled={isPending}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Contraintes</label>
          <div className="grid grid-cols-2 gap-2">
            {CONTRAINTES_PREDEFINIES.map((c) => (
              <div key={c} className="flex items-center gap-2">
                <Checkbox
                  id={c}
                  checked={contraintes.includes(c)}
                  onCheckedChange={() => toggleContrainte(c)}
                  disabled={isPending}
                />
                <label
                  htmlFor={c}
                  className="text-sm cursor-pointer"
                >
                  {c}
                </label>
              </div>
            ))}
          </div>
        </div>

        <Button
          onClick={handleEstimate}
          disabled={isPending}
          className="w-full"
        >
          {isPending ? 'Estimation...' : 'Estimer'}
        </Button>

        {data && (
          <div className="mt-4 p-3 bg-yellow-50 rounded space-y-2">
            <div className="text-sm">
              <strong>Budget estimé:</strong> €
              {Math.round(data.cout_estime_min)} - €
              {Math.round(data.cout_estime_max)}
            </div>
            <div className="text-sm">
              <strong>Durée:</strong> {data.duree_estimee_j} jours
            </div>
            {data.professionnel_recommande && (
              <div className="text-sm text-orange-700">
                ⚠️ Professionnel recommandé
              </div>
            )}
            {data.complexite_estimee && (
              <div className="text-sm">
                <strong>Complexité:</strong> {data.complexite_estimee}
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  )
}
