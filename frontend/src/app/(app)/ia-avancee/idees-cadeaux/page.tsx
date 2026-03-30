'use client'

import { useState, type FormEvent } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { Input } from '@/composants/ui/input'
import { obtenirIdeesCadeaux, type SuggestionsIdeasResponse } from '@/bibliotheque/api/ia_avancee'
import { toast } from 'sonner'

export default function IdeesCadeauxPage() {
  const [nom, setNom] = useState('Jules')
  const [age, setAge] = useState('3')
  const [relation, setRelation] = useState('fils')
  const [budget, setBudget] = useState('50')
  const [occasion, setOccasion] = useState('anniversaire')
  const [chargement, setChargement] = useState(false)
  const [resultat, setResultat] = useState<SuggestionsIdeasResponse | null>(null)

  async function soumettre(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setChargement(true)
    try {
      const data = await obtenirIdeesCadeaux({ nom, age: Number(age), relation, budget_max: Number(budget), occasion })
      setResultat(data)
    } catch {
      toast.error('Impossible de générer des idées cadeaux.')
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold">Idées cadeaux</h1><p className="text-muted-foreground">Suggestions personnalisées selon l'âge, la relation et le budget.</p></div>
      <Card>
        <CardHeader><CardTitle>Destinataire</CardTitle><CardDescription>Complète le profil pour affiner les idées.</CardDescription></CardHeader>
        <CardContent>
          <form className="grid gap-3 md:grid-cols-2" onSubmit={soumettre}>
            <Input value={nom} onChange={(e) => setNom(e.target.value)} placeholder="Nom" />
            <Input value={age} onChange={(e) => setAge(e.target.value)} type="number" placeholder="Âge" />
            <Input value={relation} onChange={(e) => setRelation(e.target.value)} placeholder="Relation" />
            <Input value={budget} onChange={(e) => setBudget(e.target.value)} type="number" placeholder="Budget max" />
            <Input value={occasion} onChange={(e) => setOccasion(e.target.value)} placeholder="Occasion" className="md:col-span-2" />
            <Button type="submit" disabled={chargement} className="md:col-span-2">{chargement ? 'Génération...' : 'Générer des idées'}</Button>
          </form>
        </CardContent>
      </Card>
      {!resultat && !chargement && (
        <Card>
          <CardHeader><CardTitle>En attente d'idées</CardTitle></CardHeader>
          <CardContent><p className="text-sm text-muted-foreground">Remplis le profil et lance la génération pour obtenir des idées adaptées.</p></CardContent>
        </Card>
      )}
      {resultat && <div className="grid gap-4 md:grid-cols-2">{resultat.idees.map((idee, index) => <Card key={`${idee.titre}-${index}`}><CardHeader><CardTitle className="text-lg">{idee.titre}</CardTitle><CardDescription>{idee.fourchette_prix}</CardDescription></CardHeader><CardContent className="space-y-2"><p>{idee.description}</p><p className="text-sm text-muted-foreground">Pertinence : {idee.pertinence}</p>{idee.raison && <p className="text-sm text-muted-foreground">{idee.raison}</p>}{idee.ou_acheter && <p className="text-sm">Où acheter : {idee.ou_acheter}</p>}</CardContent></Card>)}</div>}
    </div>
  )
}
