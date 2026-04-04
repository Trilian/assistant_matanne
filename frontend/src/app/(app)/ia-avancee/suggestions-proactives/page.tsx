'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Volume2, VolumeX } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { Badge } from '@/composants/ui/badge'
import { obtenirSuggestionsProactives, type SuggestionsProactivesResponse } from '@/bibliotheque/api/ia-avancee'
import { utiliserSyntheseVocale } from '@/crochets/utiliser-synthese-vocale'
import { toast } from 'sonner'

export default function SuggestionsProactivesPage() {
  const [chargement, setChargement] = useState(false)
  const [resultat, setResultat] = useState<SuggestionsProactivesResponse | null>(null)
  const { estSupporte, enLecture, lire, arreter } = utiliserSyntheseVocale()

  function construireResumeVocal(data: SuggestionsProactivesResponse): string {
    if (!data.suggestions.length) {
      return 'Aucune suggestion proactive disponible pour le moment.'
    }

    const top = data.suggestions.slice(0, 3)
    const lignes = top.map((item, index) => `${index + 1}. ${item.titre}. ${item.message}`)
    return `Tu as ${data.suggestions.length} suggestions proactives. ${lignes.join(' ')}`
  }

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
      {resultat && estSupporte && (
        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={() => lire(construireResumeVocal(resultat))}
            disabled={!resultat.suggestions.length}
          >
            <Volume2 className="mr-2 h-4 w-4" />
            Lire le resume vocal
          </Button>
          {enLecture && (
            <Button type="button" variant="ghost" onClick={arreter}>
              <VolumeX className="mr-2 h-4 w-4" />
              Arreter
            </Button>
          )}
        </div>
      )}
      {!resultat && !chargement && (
        <Card>
          <CardHeader><CardTitle>Chargement initial terminé</CardTitle></CardHeader>
          <CardContent><p className="text-sm text-muted-foreground">Aucune suggestion proactive disponible actuellement. Réessaie dans quelques instants.</p></CardContent>
        </Card>
      )}
      {resultat && <div className="grid gap-4">{resultat.suggestions.map((item, index) => <Card key={`${item.titre}-${index}`}><CardHeader><CardTitle className="flex items-center gap-2">{item.titre}<Badge variant={item.priorite === 'haute' ? 'destructive' : item.priorite === 'basse' ? 'outline' : 'secondary'}>{item.priorite}</Badge></CardTitle></CardHeader><CardContent className="space-y-2"><p>{item.message}</p><p className="text-sm text-muted-foreground">Module : {item.module}</p>{item.contexte && <p className="text-sm text-muted-foreground">{item.contexte}</p>}{item.action_url && <Link href={item.action_url} className="text-sm font-medium text-primary underline underline-offset-4">Ouvrir l'action</Link>}</CardContent></Card>)}</div>}
    </div>
  )
}
