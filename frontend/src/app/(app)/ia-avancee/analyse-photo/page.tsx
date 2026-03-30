'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { analyserPhotoMultiUsage, type AnalysePhotoMultiResponse } from '@/bibliotheque/api/ia_avancee'
import { toast } from 'sonner'

export default function AnalysePhotoPage() {
  const [file, setFile] = useState<File | null>(null)
  const [chargement, setChargement] = useState(false)
  const [resultat, setResultat] = useState<AnalysePhotoMultiResponse | null>(null)

  async function analyser() {
    if (!file) return
    setChargement(true)
    try {
      setResultat(await analyserPhotoMultiUsage(file))
    } catch {
      toast.error('Analyse photo indisponible.')
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold">Analyse photo multi-usage</h1><p className="text-muted-foreground">Détecte automatiquement le contexte et propose des actions.</p></div>
      <Card>
        <CardHeader><CardTitle>Photo à analyser</CardTitle><CardDescription>Une seule photo, plusieurs interprétations possibles.</CardDescription></CardHeader>
        <CardContent className="space-y-4"><input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} /><Button onClick={analyser} disabled={!file || chargement}>{chargement ? 'Analyse...' : 'Analyser la photo'}</Button></CardContent>
      </Card>
      {resultat && (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card><CardHeader><CardTitle>Résumé</CardTitle></CardHeader><CardContent className="space-y-2"><p>Contexte : {resultat.contexte_detecte}</p><p>{resultat.resume}</p><p>Confiance : {Math.round(resultat.confiance * 100)}%</p></CardContent></Card>
          <Card><CardHeader><CardTitle>Actions suggérées</CardTitle></CardHeader><CardContent><ul className="space-y-2">{resultat.actions_suggerees.map((item, index) => <li key={index}>• {item}</li>)}</ul></CardContent></Card>
          <Card className="lg:col-span-2"><CardHeader><CardTitle>Détails détectés</CardTitle></CardHeader><CardContent><pre className="text-xs whitespace-pre-wrap">{JSON.stringify(resultat.details, null, 2)}</pre></CardContent></Card>
        </div>
      )}
    </div>
  )
}
