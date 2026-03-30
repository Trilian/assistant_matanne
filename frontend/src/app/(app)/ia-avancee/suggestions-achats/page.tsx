'use client'

import { useState, type FormEvent } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { Input } from '@/composants/ui/input'
import { Badge } from '@/composants/ui/badge'
import { obtenirSuggestionsAchats, type SuggestionsAchatsResponse } from '@/bibliotheque/api/ia_avancee'
import { toast } from 'sonner'

export default function SuggestionsAchatsPage() {
  const [jours, setJours] = useState(90)
  const [chargement, setChargement] = useState(false)
  const [resultat, setResultat] = useState<SuggestionsAchatsResponse | null>(null)

  async function soumettre(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setChargement(true)
    try {
      const data = await obtenirSuggestionsAchats(jours)
      setResultat(data)
    } catch {
      toast.error('Impossible de charger les suggestions d\'achats.')
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Suggestions d'achats</h1>
        <p className="text-muted-foreground">Détecte les articles à racheter selon l'historique.</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Analyser une période</CardTitle>
          <CardDescription>Choisis le nombre de jours à analyser.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="flex gap-3 max-w-md" onSubmit={soumettre}>
            <Input type="number" min={7} max={365} value={jours} onChange={(e) => setJours(Number(e.target.value))} />
            <Button type="submit" disabled={chargement}>{chargement ? 'Analyse...' : 'Analyser'}</Button>
          </form>
        </CardContent>
      </Card>
      {!resultat && !chargement && (
        <Card>
          <CardHeader><CardTitle>En attente d'analyse</CardTitle></CardHeader>
          <CardContent><p className="text-sm text-muted-foreground">Lance une analyse pour afficher les articles à racheter avec leur urgence.</p></CardContent>
        </Card>
      )}
      {resultat && (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <Card><CardContent className="pt-6"><div className="text-2xl font-bold">{resultat.suggestions.length}</div><p className="text-sm text-muted-foreground">Suggestions</p></CardContent></Card>
            <Card><CardContent className="pt-6"><div className="text-2xl font-bold">{resultat.nb_produits_analyses}</div><p className="text-sm text-muted-foreground">Produits analysés</p></CardContent></Card>
            <Card><CardContent className="pt-6"><div className="text-2xl font-bold">{resultat.periode_analyse_jours} j</div><p className="text-sm text-muted-foreground">Période</p></CardContent></Card>
          </div>
          <div className="grid gap-4">
            {resultat.suggestions.map((suggestion, index) => (
              <Card key={`${suggestion.nom}-${index}`}>
                <CardContent className="pt-6 flex items-start justify-between gap-4">
                  <div className="space-y-1">
                    <p className="font-medium">{suggestion.nom}</p>
                    <p className="text-sm text-muted-foreground">{suggestion.raison}</p>
                    {suggestion.quantite_suggeree && <p className="text-xs text-muted-foreground">Quantité suggérée : {suggestion.quantite_suggeree}</p>}
                  </div>
                  <Badge variant={suggestion.urgence === 'haute' ? 'destructive' : suggestion.urgence === 'basse' ? 'outline' : 'secondary'}>{suggestion.urgence}</Badge>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
