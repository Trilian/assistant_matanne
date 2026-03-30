'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { obtenirOptimisationRoutines, type OptimisationRoutinesResponse } from '@/bibliotheque/api/ia_avancee'
import { toast } from 'sonner'

export default function OptimisationRoutinesPage() {
  const [chargement, setChargement] = useState(false)
  const [resultat, setResultat] = useState<OptimisationRoutinesResponse | null>(null)

  async function charger() {
    setChargement(true)
    try {
      setResultat(await obtenirOptimisationRoutines())
    } catch {
      toast.error('Optimisation des routines indisponible.')
    } finally {
      setChargement(false)
    }
  }

  useEffect(() => { void charger() }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4"><div><h1 className="text-3xl font-bold">Optimisation des routines</h1><p className="text-muted-foreground">Identifie les frictions et les gains de temps possibles.</p></div><Button onClick={charger} disabled={chargement}>{chargement ? 'Analyse...' : 'Relancer l’analyse'}</Button></div>
      {!resultat && !chargement && (
        <Card>
          <CardHeader><CardTitle>Chargement initial terminé</CardTitle></CardHeader>
          <CardContent><p className="text-sm text-muted-foreground">Aucune optimisation disponible pour l’instant. Relance l’analyse pour réessayer.</p></CardContent>
        </Card>
      )}
      {resultat && (
        <>
          <div className="grid gap-4 md:grid-cols-2">
            <Card><CardContent className="pt-6"><div className="text-3xl font-bold">{resultat.score_efficacite_actuel}</div><p className="text-sm text-muted-foreground">Score actuel</p></CardContent></Card>
            <Card><CardContent className="pt-6"><div className="text-3xl font-bold">{resultat.score_efficacite_projete}</div><p className="text-sm text-muted-foreground">Score projeté</p></CardContent></Card>
          </div>
          <div className="grid gap-4">{resultat.optimisations.map((item, index) => <Card key={`${item.routine_concernee}-${index}`}><CardHeader><CardTitle>{item.routine_concernee}</CardTitle></CardHeader><CardContent className="space-y-2"><p className="text-sm text-muted-foreground">{item.probleme_identifie}</p><p>{item.suggestion}</p>{item.gain_estime && <p className="text-sm">Gain estimé : {item.gain_estime}</p>}</CardContent></Card>)}</div>
        </>
      )}
    </div>
  )
}
