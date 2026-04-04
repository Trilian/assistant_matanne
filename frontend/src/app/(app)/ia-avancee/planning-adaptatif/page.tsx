'use client'

import { useState, type FormEvent } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { Input } from '@/composants/ui/input'
import { Textarea } from '@/composants/ui/textarea'
import { genererPlanningAdaptatif, type PlanningAdaptatifResponse } from '@/bibliotheque/api/ia-avancee'
import { toast } from 'sonner'

export default function PlanningAdaptatifPage() {
  const [budget, setBudget] = useState('450')
  const [meteoJson, setMeteoJson] = useState('{\n  "condition": "pluie",\n  "temperature": 11,\n  "weekend": true\n}')
  const [chargement, setChargement] = useState(false)
  const [resultat, setResultat] = useState<PlanningAdaptatifResponse | null>(null)

  async function soumettre(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setChargement(true)
    try {
      const meteo = meteoJson.trim() ? JSON.parse(meteoJson) : null
      const data = await genererPlanningAdaptatif({
        budget_restant: budget ? Number(budget) : null,
        meteo,
      })
      setResultat(data)
    } catch {
      toast.error('Impossible de générer le planning adaptatif.')
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Planning adaptatif</h1>
        <p className="text-muted-foreground">Ajuste repas et activités selon météo et budget.</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Contexte</CardTitle>
          <CardDescription>Décris la météo prévue et le budget disponible.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={soumettre}>
            <Input value={budget} onChange={(e) => setBudget(e.target.value)} placeholder="Budget restant" type="number" />
            <Textarea rows={8} value={meteoJson} onChange={(e) => setMeteoJson(e.target.value)} />
            <Button type="submit" disabled={chargement}>{chargement ? 'Génération...' : 'Générer'}</Button>
          </form>
        </CardContent>
      </Card>
      {!resultat && !chargement && (
        <Card>
          <CardHeader><CardTitle>En attente de génération</CardTitle></CardHeader>
          <CardContent><p className="text-sm text-muted-foreground">Renseigne le contexte puis génère pour obtenir des recommandations, repas et activités adaptés.</p></CardContent>
        </Card>
      )}
      {resultat && (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader><CardTitle>Score d'adaptation</CardTitle></CardHeader>
            <CardContent><div className="text-4xl font-bold">{resultat.score_adaptation}/100</div></CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Recommandations</CardTitle></CardHeader>
            <CardContent><ul className="space-y-2">{resultat.recommandations.map((item, index) => <li key={index}>• {item}</li>)}</ul></CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Repas suggérés</CardTitle></CardHeader>
            <CardContent><pre className="text-xs whitespace-pre-wrap">{JSON.stringify(resultat.repas_suggerees, null, 2)}</pre></CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Activités suggérées</CardTitle></CardHeader>
            <CardContent><pre className="text-xs whitespace-pre-wrap">{JSON.stringify(resultat.activites_suggerees, null, 2)}</pre></CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
