'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { obtenirPredictionPannes, type PredictionPannesResponse } from '@/bibliotheque/api/ia_avancee'
import { toast } from 'sonner'

export default function PredictionPannesPage() {
  const [chargement, setChargement] = useState(false)
  const [resultat, setResultat] = useState<PredictionPannesResponse | null>(null)

  async function charger() {
    setChargement(true)
    try {
      setResultat(await obtenirPredictionPannes())
    } catch {
      toast.error('Prédiction pannes indisponible.')
    } finally {
      setChargement(false)
    }
  }

  useEffect(() => { void charger() }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4"><div><h1 className="text-3xl font-bold">Prédiction pannes</h1><p className="text-muted-foreground">Risque de panne et maintenance préventive sur les équipements.</p></div><Button onClick={charger} disabled={chargement}>{chargement ? 'Actualisation...' : 'Actualiser'}</Button></div>
      {resultat && <div className="space-y-4"><div className="grid gap-4 md:grid-cols-2"><Card><CardContent className="pt-6"><div className="text-3xl font-bold">{resultat.nb_equipements_analyses}</div><p className="text-sm text-muted-foreground">Équipements analysés</p></CardContent></Card><Card><CardContent className="pt-6"><div className="text-3xl font-bold">{resultat.score_sante_global}/100</div><p className="text-sm text-muted-foreground">Score de santé global</p></CardContent></Card></div><div className="grid gap-4">{resultat.predictions.map((item, index) => <Card key={`${item.equipement}-${index}`}><CardHeader><CardTitle>{item.equipement}</CardTitle></CardHeader><CardContent className="space-y-2"><p>Risque : {item.risque} ({item.probabilite_pct}%)</p>{item.delai_estime && <p>Délai estimé : {item.delai_estime}</p>}<ul className="space-y-1 text-sm">{item.signes_alerte.map((entry, i) => <li key={i}>• {entry}</li>)}</ul><ul className="space-y-1 text-sm text-muted-foreground">{item.maintenance_preventive.map((entry, i) => <li key={i}>→ {entry}</li>)}</ul></CardContent></Card>)}</div></div>}
    </div>
  )
}
