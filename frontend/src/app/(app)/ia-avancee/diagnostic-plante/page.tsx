'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { Badge } from '@/composants/ui/badge'
import { diagnostiquerPlante, type DiagnosticPlantResponse } from '@/bibliotheque/api/ia_avancee'
import { toast } from 'sonner'

export default function DiagnosticPlantePage() {
  const [file, setFile] = useState<File | null>(null)
  const [chargement, setChargement] = useState(false)
  const [resultat, setResultat] = useState<DiagnosticPlantResponse | null>(null)

  async function analyser() {
    if (!file) return
    setChargement(true)
    try {
      setResultat(await diagnostiquerPlante(file))
    } catch {
      toast.error('Diagnostic plante indisponible.')
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Diagnostic plante</h1>
        <p className="text-muted-foreground">Analyse une photo et identifie les problèmes de santé.</p>
      </div>
      <Card>
        <CardHeader><CardTitle>Photo de la plante</CardTitle><CardDescription>Charge une image JPG ou PNG.</CardDescription></CardHeader>
        <CardContent className="space-y-4">
          <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          <Button onClick={analyser} disabled={!file || chargement}>{chargement ? 'Analyse...' : 'Analyser'}</Button>
        </CardContent>
      </Card>
      {resultat && (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card><CardHeader><CardTitle>{resultat.nom_plante}</CardTitle></CardHeader><CardContent className="space-y-2"><Badge>{resultat.etat_general}</Badge><p>Confiance : {Math.round(resultat.confiance * 100)}%</p><p>{resultat.arrosage_conseil}</p><p>{resultat.exposition_conseil}</p></CardContent></Card>
          <Card><CardHeader><CardTitle>Traitements</CardTitle></CardHeader><CardContent><ul className="space-y-2">{resultat.traitements_recommandes.map((item, index) => <li key={index}>• {item}</li>)}</ul></CardContent></Card>
          <Card><CardHeader><CardTitle>Problèmes détectés</CardTitle></CardHeader><CardContent><ul className="space-y-2">{resultat.problemes_detectes.map((item, index) => <li key={index}>• {item}</li>)}</ul></CardContent></Card>
          <Card><CardHeader><CardTitle>Causes probables</CardTitle></CardHeader><CardContent><ul className="space-y-2">{resultat.causes_probables.map((item, index) => <li key={index}>• {item}</li>)}</ul></CardContent></Card>
        </div>
      )}
    </div>
  )
}
