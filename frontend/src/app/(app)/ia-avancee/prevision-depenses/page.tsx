'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { obtenirPrevisionDepenses, type PrevisionsDepensesResponse } from '@/bibliotheque/api/ia_avancee'
import { toast } from 'sonner'

export default function PrevisionDepensesPage() {
  const [chargement, setChargement] = useState(false)
  const [resultat, setResultat] = useState<PrevisionsDepensesResponse | null>(null)

  async function charger() {
    setChargement(true)
    try {
      setResultat(await obtenirPrevisionDepenses())
    } catch {
      toast.error('Prévision des dépenses indisponible.')
    } finally {
      setChargement(false)
    }
  }

  useEffect(() => { void charger() }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Prévision des dépenses</h1>
          <p className="text-muted-foreground">Projection jusqu'à la fin du mois.</p>
        </div>
        <Button onClick={charger} disabled={chargement}>{chargement ? 'Actualisation...' : 'Actualiser'}</Button>
      </div>
      {resultat && (
        <>
          <div className="grid gap-4 md:grid-cols-4">
            <Card><CardContent className="pt-6"><div className="text-2xl font-bold">{resultat.depenses_actuelles.toFixed(0)} €</div><p className="text-sm text-muted-foreground">Dépensé</p></CardContent></Card>
            <Card><CardContent className="pt-6"><div className="text-2xl font-bold">{resultat.prevision_fin_mois.toFixed(0)} €</div><p className="text-sm text-muted-foreground">Prévision</p></CardContent></Card>
            <Card><CardContent className="pt-6"><div className="text-2xl font-bold">{resultat.budget_mensuel.toFixed(0)} €</div><p className="text-sm text-muted-foreground">Budget</p></CardContent></Card>
            <Card><CardContent className="pt-6"><div className="text-2xl font-bold">{resultat.ecart_prevu.toFixed(0)} €</div><p className="text-sm text-muted-foreground">Écart prévu</p></CardContent></Card>
          </div>
          <Card><CardHeader><CardTitle>Conseils économies</CardTitle></CardHeader><CardContent><ul className="space-y-2">{resultat.conseils_economies.map((item, index) => <li key={index}>• {item}</li>)}</ul></CardContent></Card>
        </>
      )}
    </div>
  )
}
