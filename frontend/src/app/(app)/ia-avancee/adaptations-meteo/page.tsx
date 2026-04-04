'use client'

import { useState, type FormEvent } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { Textarea } from '@/composants/ui/textarea'
import { obtenirAdaptationsMeteo, type AdaptationPlanningMeteoResponse } from '@/bibliotheque/api/ia-avancee'
import { toast } from 'sonner'

export default function AdaptationsMeteoPage() {
  const [meteoJson, setMeteoJson] = useState('{\n  "jour": "samedi",\n  "condition": "pluie",\n  "temperature": 8,\n  "vent": 25\n}')
  const [chargement, setChargement] = useState(false)
  const [resultat, setResultat] = useState<AdaptationPlanningMeteoResponse | null>(null)

  async function soumettre(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setChargement(true)
    try {
      const data = await obtenirAdaptationsMeteo(JSON.parse(meteoJson))
      setResultat(data)
    } catch {
      toast.error('Adaptations météo indisponibles.')
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold">Adaptations météo</h1><p className="text-muted-foreground">Transforme les prévisions météo en ajustements concrets du planning.</p></div>
      <Card><CardHeader><CardTitle>Prévisions météo</CardTitle><CardDescription>Colle un JSON météo simple pour obtenir des adaptations.</CardDescription></CardHeader><CardContent><form className="space-y-4" onSubmit={soumettre}><Textarea rows={8} value={meteoJson} onChange={(e) => setMeteoJson(e.target.value)} /><Button type="submit" disabled={chargement}>{chargement ? 'Analyse...' : 'Adapter le planning'}</Button></form></CardContent></Card>
      {!resultat && !chargement && (
        <Card>
          <CardHeader><CardTitle>En attente d'adaptation</CardTitle></CardHeader>
          <CardContent><p className="text-sm text-muted-foreground">Soumets des prévisions météo JSON pour obtenir des ajustements actionnables du planning.</p></CardContent>
        </Card>
      )}
      {resultat && <div className="grid gap-4 lg:grid-cols-2"><Card><CardHeader><CardTitle>Résumé météo</CardTitle></CardHeader><CardContent><pre className="text-xs whitespace-pre-wrap">{JSON.stringify(resultat.meteo_resume, null, 2)}</pre></CardContent></Card><Card><CardHeader><CardTitle>Adaptations</CardTitle></CardHeader><CardContent><ul className="space-y-2">{resultat.adaptations.map((item, index) => <li key={index}>• {item.type_adaptation} / {item.condition_meteo} : {item.recommandation} ({item.impact})</li>)}</ul></CardContent></Card></div>}
    </div>
  )
}
