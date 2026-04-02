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
import { utiliseAnalyseImpactsMeteo } from '@/src/crochets/utiliser-sprint13-ia'

/**
 * Example Component: Weather Impact Analysis
 * ────────────────────────────────────────────
 * Demonstrates the Sprint 13 IA hook for suggesting activities based on weather
 * Located in: frontend/src/app/(app)/outils/composants/AnalyseMeteoExample.tsx
 *
 * Usage:
 * - User inputs 7-day forecast + current season
 * - Component analyzes weather patterns
 * - Returns suggested activities for each day
 * - Great for outdoor planning & family activities
 */

interface Prevision {
  date: string
  meteo: string
  temperature_min: number
  temperature_max: number
  precipitation_mm: number
}

const SAISONS = ['printemps', 'ete', 'automne', 'hiver']

export function AnalyseMeteoExample() {
  const [saison, setSaison] = useState('printemps')
  const [previsions, setPrevisions] = useState<Prevision[]>([
    {
      date: '2026-04-02',
      meteo: 'Ensoleillé',
      temperature_min: 10,
      temperature_max: 18,
      precipitation_mm: 0,
    },
  ])

  const { mutate: analyserMeteo, isPending, data } = utiliseAnalyseImpactsMeteo()
  const { ajouter_notification } = useNotifications()

  const handleAnalyze = () => {
    if (previsions.some((p) => !p.meteo)) {
      ajouter_notification('Veuillez remplir la météo', 'error')
      return
    }

    analyserMeteo(
      { previsions_7j: previsions, saison },
      {
        onSuccess: (results) => {
          ajouter_notification(
            `${results.length} activités suggérées!`,
            'success'
          )
        },
        onError: () => {
          ajouter_notification('Erreur lors de l\'analyse météo', 'error')
        },
      }
    )
  }

  const updatePrevision = (
    index: number,
    field: keyof Prevision,
    value: string | number
  ) => {
    const newPrevisions = [...previsions]
    newPrevisions[index][field] = value as never
    setPrevisions(newPrevisions)
  }

  return (
    <Card className="p-6">
      <h2 className="text-xl font-bold mb-4">Analyse Météo & Activités</h2>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Saison</label>
        <Select value={saison} onValueChange={setSaison}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {SAISONS.map((s) => (
              <SelectItem key={s} value={s}>
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {previsions.map((prev, idx) => (
          <div key={idx} className="p-3 border rounded">
            <p className="text-sm font-medium mb-2">{prev.date}</p>
            <div className="grid grid-cols-2 gap-2">
              <Input
                value={prev.meteo}
                onChange={(e) =>
                  updatePrevision(idx, 'meteo', e.target.value)
                }
                placeholder="Ex: Ensoleillé, Pluvieux"
                size={25}
              />
              <Input
                value={prev.temperature_min}
                onChange={(e) =>
                  updatePrevision(idx, 'temperature_min', parseInt(e.target.value))
                }
                placeholder="T° min"
                type="number"
              />
              <Input
                value={prev.temperature_max}
                onChange={(e) =>
                  updatePrevision(idx, 'temperature_max', parseInt(e.target.value))
                }
                placeholder="T° max"
                type="number"
              />
              <Input
                value={prev.precipitation_mm}
                onChange={(e) =>
                  updatePrevision(idx, 'precipitation_mm', parseFloat(e.target.value))
                }
                placeholder="Pluie (mm)"
                type="number"
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
        <div className="mt-4 space-y-2">
          {data.map((day: any, idx: number) => (
            <div key={idx} className="p-3 bg-blue-50 rounded">
              <p className="text-sm font-semibold">{day.date}</p>
              <p className="text-sm">
                Activités: {day.activites_suggerees.join(', ')}
              </p>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}
