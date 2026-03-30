'use client'

import { useState, type FormEvent } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { Input } from '@/composants/ui/input'
import { genererPlanningVoyage, type PlanningVoyageResponse } from '@/bibliotheque/api/ia_avancee'
import { toast } from 'sonner'

export default function PlanningVoyagePage() {
  const [destination, setDestination] = useState('Bruges')
  const [duree, setDuree] = useState('3')
  const [budget, setBudget] = useState('500')
  const [avecEnfant, setAvecEnfant] = useState(true)
  const [chargement, setChargement] = useState(false)
  const [resultat, setResultat] = useState<PlanningVoyageResponse | null>(null)

  async function soumettre(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setChargement(true)
    try {
      setResultat(await genererPlanningVoyage({ destination, duree_jours: Number(duree), budget_total: Number(budget), avec_enfant: avecEnfant }))
    } catch {
      toast.error('Planning voyage indisponible.')
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold">Planning voyage</h1><p className="text-muted-foreground">Itinéraire, checklist et adaptation enfant.</p></div>
      <Card><CardHeader><CardTitle>Préparer le voyage</CardTitle><CardDescription>Décris destination, durée et budget total.</CardDescription></CardHeader><CardContent><form className="grid gap-3 md:grid-cols-2" onSubmit={soumettre}><Input value={destination} onChange={(e) => setDestination(e.target.value)} placeholder="Destination" /><Input type="number" value={duree} onChange={(e) => setDuree(e.target.value)} placeholder="Durée" /><Input type="number" value={budget} onChange={(e) => setBudget(e.target.value)} placeholder="Budget total" /><label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={avecEnfant} onChange={(e) => setAvecEnfant(e.target.checked)} /> Avec enfant</label><Button type="submit" disabled={chargement} className="md:col-span-2">{chargement ? 'Génération...' : 'Générer le planning'}</Button></form></CardContent></Card>
      {!resultat && !chargement && (
        <Card>
          <CardHeader><CardTitle>En attente de planning</CardTitle></CardHeader>
          <CardContent><p className="text-sm text-muted-foreground">Renseigne les paramètres du voyage pour générer un itinéraire complet jour par jour.</p></CardContent>
        </Card>
      )}
      {resultat && <div className="space-y-4"><Card><CardHeader><CardTitle>{resultat.destination}</CardTitle><CardDescription>{resultat.duree_jours} jours • budget estimé {resultat.budget_total_estime} €</CardDescription></CardHeader><CardContent><ul className="space-y-2">{resultat.conseils_generaux.map((item, index) => <li key={index}>• {item}</li>)}</ul></CardContent></Card><div className="grid gap-4 md:grid-cols-2">{resultat.jours.map((jour) => <Card key={jour.jour}><CardHeader><CardTitle>Jour {jour.jour}</CardTitle></CardHeader><CardContent className="space-y-3"><ul className="space-y-1">{jour.activites.map((item, index) => <li key={index}>• {item}</li>)}</ul><ul className="space-y-1 text-sm text-muted-foreground">{jour.conseils.map((item, index) => <li key={index}>→ {item}</li>)}</ul></CardContent></Card>)}</div></div>}
    </div>
  )
}
