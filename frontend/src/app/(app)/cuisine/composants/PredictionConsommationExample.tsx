'use client'

import { useState } from 'react'
import { Button } from '@/src/composants/ui/button'
import { Card } from '@/src/composants/ui/card'
import { Input } from '@/src/composants/ui/input'
import { useNotifications } from '@/src/magasins/store-notifications'
import { utilisePredictionConsommation } from '@/src/crochets/utiliser-ia-modules'

/**
 * Example Component: Inventory Prediction
 * ─────────────────────────────────────────
 * Demonstrates the IA hook for predicting ingredient consumption
 * Located in: frontend/src/app/(app)/cuisine/composants/PredictionConsommationExample.tsx
 *
 * Usage:
 * - User inputs ingredient name, current stock, and purchase history
 * - Component calls mutation on form submit
 * - Results displayed dynamically
 * - Errors handled via Zustand notifications
 */

interface HistoriqueAchat {
  mois: number
  quantite_kg: number
}

export function PredictionConsommationExample() {
  const [ingredientNom, setIngredientNom] = useState('')
  const [stockActuel, setStockActuel] = useState('')
  const [historique, setHistorique] = useState<HistoriqueAchat[]>([])

  const { mutate: predireConsommation, isPending, data } = utilisePredictionConsommation()
  const { ajouter_notification } = useNotifications()

  const handleSubmit = () => {
    if (!ingredientNom || !stockActuel) {
      ajouter_notification('Veuillez remplir tous les champs', 'erreur')
      return
    }

    predireConsommation(
      {
        ingredient_nom: ingredientNom,
        stock_actuel_kg: parseFloat(stockActuel),
        historique_achat_mensuel: historique.map((h) => h.quantite_kg),
      },
      {
        onSuccess: (result) => {
          ajouter_notification(
            `Prochaine consommation estimée: ${result.prochaine_consommation_estimee_j} jours`,
            'succes'
          )
        },
        onError: () => {
          ajouter_notification(
            'Erreur lors de la prédiction de consommation',
            'erreur'
          )
        },
      }
    )
  }

  return (
    <Card className="p-6 max-w-md">
      <h2 className="text-xl font-bold mb-4">Prédiction Consommation</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            Ingrédient
          </label>
          <Input
            value={ingredientNom}
            onChange={(e) => setIngredientNom(e.target.value)}
            placeholder="Ex: Tomates"
            disabled={isPending}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Stock actuel (kg)
          </label>
          <Input
            value={stockActuel}
            onChange={(e) => setStockActuel(e.target.value)}
            placeholder="2.5"
            type="number"
            disabled={isPending}
          />
        </div>

        <Button
          onClick={handleSubmit}
          disabled={isPending}
          className="w-full"
        >
          {isPending ? 'Prédiction...' : 'Prédire'}
        </Button>

        {data && (
          <div className="mt-4 p-3 bg-blue-50 rounded">
            <p className="text-sm">
              <strong>Jours avant rupture:</strong> {data.prochaine_consommation_estimee_j}
            </p>
            <p className="text-sm">
              <strong>Confiance:</strong> {(data.confiance_prediction * 100).toFixed(0)}%
            </p>
          </div>
        )}
      </div>
    </Card>
  )
}
