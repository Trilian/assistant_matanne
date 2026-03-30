'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { Badge } from '@/composants/ui/badge'
import { obtenirSuggestionsProactives, type SuggestionsProactivesResponse } from '@/bibliotheque/api/ia_avancee'
import { toast } from 'sonner'

export default function SuggestionsProactivesPage() {
  const [chargement, setChargement] = useState(false)
  const [resultat, setResultat] = useState<SuggestionsProactivesResponse | null>(null)

  async function charger() {
    setChargement(true)
    try {
      setResultat(await obtenirSuggestionsProactives())
    } catch {
      toast.error('Suggestions proactives indisponibles.')
    } finally {
      setChargement(false)
    }
  }

  useEffect(() => { void charger() }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4"><div><h1 className="text-3xl font-bold">Suggestions proactives</h1><p className="text-muted-foreground">L'app te pousse les meilleures actions sans attendre une demande.</p></div><Button onClick={charger} disabled={chargement}>{chargement ? 'Actualisation...' : 'Actualiser'}</Button></div>
      {resultat && <div className="grid gap-4">{resultat.suggestions.map((item, index) => <Card key={`${item.titre}-${index}`}><CardHeader><CardTitle className="flex items-center gap-2">{item.titre}<Badge variant={item.priorite === 'haute' ? 'destructive' : item.priorite === 'basse' ? 'outline' : 'secondary'}>{item.priorite}</Badge></CardTitle></CardHeader><CardContent className="space-y-2"><p>{item.message}</p><p className="text-sm text-muted-foreground">Module : {item.module}</p>{item.contexte && <p className="text-sm text-muted-foreground">{item.contexte}</p>}{item.action_url && <Link href={item.action_url} className="text-sm font-medium text-primary underline underline-offset-4">Ouvrir l'action</Link>}</CardContent></Card>)}</div>}
    </div>
  )
}
