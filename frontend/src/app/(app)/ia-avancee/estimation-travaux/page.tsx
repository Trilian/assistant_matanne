'use client'

import { useEffect, useState, type FormEvent } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { Input } from '@/composants/ui/input'
import { estimerTravaux, type EstimationTravauxResponse } from '@/bibliotheque/api/ia_avancee'
import { toast } from 'sonner'

export default function EstimationTravauxPage() {
  const [file, setFile] = useState<File | null>(null)
  const [description, setDescription] = useState('Fuite légère sous évier')
  const [chargement, setChargement] = useState(false)
  const [resultat, setResultat] = useState<EstimationTravauxResponse | null>(null)
  const [apercu, setApercu] = useState<string | null>(null)

  useEffect(() => {
    if (!file) {
      setApercu(null)
      return
    }
    const url = URL.createObjectURL(file)
    setApercu(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  async function soumettre(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!file) return
    setChargement(true)
    try {
      setResultat(await estimerTravaux(file, description))
    } catch {
      toast.error('Estimation travaux indisponible.')
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold">Estimation travaux</h1><p className="text-muted-foreground">Photo + contexte libre pour estimer budget, difficulté et matériel.</p></div>
      <Card><CardHeader><CardTitle>Décrire le chantier</CardTitle><CardDescription>Ajoute une photo et quelques mots de contexte.</CardDescription></CardHeader><CardContent><form className="space-y-4" onSubmit={soumettre}><input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />{file && <div className="space-y-2 rounded-md border p-3"><p className="text-sm text-muted-foreground">Fichier sélectionné: {file.name}</p>{apercu && <img src={apercu} alt="Aperçu travaux" className="max-h-64 w-full rounded-md object-cover" />}</div>}<Input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description" /><Button type="submit" disabled={!file || chargement}>{chargement ? 'Analyse...' : 'Estimer les travaux'}</Button></form></CardContent></Card>
      {!resultat && !chargement && (
        <Card>
          <CardHeader><CardTitle>En attente d'estimation</CardTitle></CardHeader>
          <CardContent><p className="text-sm text-muted-foreground">L'IA estimera le budget, la difficulté, les matériaux et le recours éventuel à un artisan.</p></CardContent>
        </Card>
      )}
      {resultat && <div className="grid gap-4 lg:grid-cols-2"><Card><CardHeader><CardTitle>{resultat.type_travaux}</CardTitle></CardHeader><CardContent className="space-y-2"><p>{resultat.description}</p><p>Budget : {resultat.budget_min} € - {resultat.budget_max} €</p><p>Difficulté : {resultat.difficulte}</p><p>DIY possible : {resultat.diy_possible ? 'Oui' : 'Non'}</p>{resultat.duree_estimee && <p>Durée : {resultat.duree_estimee}</p>}</CardContent></Card><Card><CardHeader><CardTitle>Artisans recommandés</CardTitle></CardHeader><CardContent><ul className="space-y-2">{resultat.artisans_recommandes.map((item, index) => <li key={index}>• {item}</li>)}</ul></CardContent></Card><Card className="lg:col-span-2"><CardHeader><CardTitle>Matériaux nécessaires</CardTitle></CardHeader><CardContent><ul className="space-y-2">{resultat.materiaux_necessaires.map((materiau, index) => <li key={index}>• {typeof materiau === 'object' && materiau !== null ? JSON.stringify(materiau) : String(materiau)}</li>)}</ul></CardContent></Card></div>}
    </div>
  )
}
