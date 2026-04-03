'use client'

import { useState } from 'react'
import { Button } from '@/src/composants/ui/button'
import { Card } from '@/src/composants/ui/card'
import { Input } from '@/src/composants/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/src/composants/ui/select'
import { useNotifications } from '@/src/magasins/store-notifications'
import { utiliseAnalyseNutrition } from '@/src/crochets/utiliser-ia-modules'

/**
 * Example Component: Family Nutrition Analysis
 * ──────────────────────────────────────────────
 * Demonstrates the Sprint 13 IA hook for analyzing nutritional requirements
 * Located in: frontend/src/app/(app)/cuisine/composants/AnalyseNutritionExample.tsx
 *
 * Usage:
 * - User inputs family member info (age, sex, activity level)
 * - Component enters weekly recipes
 * - Mutation returns daily macro/calorie recommendations
 * - Great for Jules (adapting meals) & family health
 */

const NIVEAUX_ACTIVITE = ['sedentaire', 'modere', 'actif', 'intense']
const OBJECTIFS_SANTE = [
  'Croissance saine',
  'Maintien poids',
  'Perte poids',
  'Gain musculaire',
  'Performance sport',
]

export function AnalyseNutritionExample() {
  const [nomPersonne, setNomPersonne] = useState('Jules')
  const [age, setAge] = useState('4')
  const [sexe, setSexe] = useState('M')
  const [niveauActivite, setNiveauActivite] = useState('modere')
  const [objectif, setObjectif] = useState('Croissance saine')
  const [recettes, setRecettes] = useState<string[]>(['Pâtes', 'Poulet', 'Légumes'])
  const [nouvelleRecette, setNouvelleRecette] = useState('')

  const { mutate: analyserNutrition, isPending, data } = utiliseAnalyseNutrition()
  const { ajouter_notification } = useNotifications()

  const handleAddRecette = () => {
    if (nouvelleRecette.trim()) {
      setRecettes([...recettes, nouvelleRecette])
      setNouvelleRecette('')
      ajouter_notification('Recette ajoutée', 'succes')
    }
  }

  const handleRemoveRecette = (index: number) => {
    setRecettes(recettes.filter((_, i) => i !== index))
  }

  const handleAnalyze = () => {
    if (!nomPersonne || !age || !sexe || recettes.length === 0) {
      ajouter_notification(
        'Veuillez remplir tous les champs et ajouter au moins une recette',
        'erreur'
      )
      return
    }

    analyserNutrition(
      {
        personne_nom: nomPersonne,
        age_ans: parseInt(age),
        sexe: sexe as 'M' | 'F',
        activite_niveau: niveauActivite,
        recettes_semaine: recettes,
        objectif_sante: objectif,
      },
      {
        onSuccess: (result) => {
          ajouter_notification(
            `${result.calories_journalieres_recommandees} kcal/jour`,
            'succes'
          )
        },
        onError: () => {
          ajouter_notification(
            'Erreur lors de l\'analyse nutritionnelle',
            'erreur'
          )
        },
      }
    )
  }

  return (
    <Card className="p-6">
      <h2 className="text-xl font-bold mb-4">Analyse Nutrition</h2>

      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Nom</label>
            <Input
              value={nomPersonne}
              onChange={(e) => setNomPersonne(e.target.value)}
              placeholder="Jules"
              disabled={isPending}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Âge (ans)</label>
            <Input
              value={age}
              onChange={(e) => setAge(e.target.value)}
              placeholder="4"
              type="number"
              disabled={isPending}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Sexe</label>
            <Select value={sexe} onValueChange={setSexe}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="M">Garçon</SelectItem>
                <SelectItem value="F">Fille</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Activité</label>
            <Select value={niveauActivite} onValueChange={setNiveauActivite}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {NIVEAUX_ACTIVITE.map((n) => (
                  <SelectItem key={n} value={n}>
                    {n.charAt(0).toUpperCase() + n.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Objectif de santé</label>
          <Select value={objectif} onValueChange={setObjectif}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {OBJECTIFS_SANTE.map((o) => (
                <SelectItem key={o} value={o}>
                  {o}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Recettes de la semaine</label>
          <div className="flex gap-2 mb-2">
            <Input
              value={nouvelleRecette}
              onChange={(e) => setNouvelleRecette(e.target.value)}
              placeholder="Ajouter une recette"
              disabled={isPending}
            />
            <Button
              onClick={handleAddRecette}
              disabled={isPending}
              className="whitespace-nowrap"
            >
              Ajouter
            </Button>
          </div>

          <div className="flex flex-wrap gap-1">
            {recettes.map((r, idx) => (
              <div
                key={idx}
                className="bg-blue-100 px-3 py-1 rounded text-sm flex items-center gap-2"
              >
                {r}
                <button
                  onClick={() => handleRemoveRecette(idx)}
                  className="text-red-500 hover:text-red-700"
                  disabled={isPending}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>

        <Button
          onClick={handleAnalyze}
          disabled={isPending}
          className="w-full"
        >
          {isPending ? 'Analyse...' : 'Analyser'}
        </Button>

        {data && (
          <div className="mt-4 grid grid-cols-2 gap-2 p-3 bg-green-50 rounded">
            <div className="text-sm">
              <strong>Calories:</strong>{' '}
              {Math.round(data.calories_journalieres_recommandees)} kcal/j
            </div>
            <div className="text-sm">
              <strong>Protéines:</strong> {Math.round(data.proteines_g_j)}g
            </div>
            <div className="text-sm">
              <strong>Glucides:</strong> {Math.round(data.glucides_g_j)}g
            </div>
            <div className="text-sm">
              <strong>Lipides:</strong> {Math.round(data.lipides_g_j)}g
            </div>
            {data.notes_personnalisees && (
              <div className="col-span-2 text-xs mt-2 p-2 bg-white rounded">
                <strong>Notes:</strong> {data.notes_personnalisees}
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  )
}
