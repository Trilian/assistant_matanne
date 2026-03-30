'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { analyserDocument, type AnalyseDocumentPhotoResponse } from '@/bibliotheque/api/ia_avancee'
import { toast } from 'sonner'

export default function AnalyseDocumentPage() {
  const [file, setFile] = useState<File | null>(null)
  const [chargement, setChargement] = useState(false)
  const [resultat, setResultat] = useState<AnalyseDocumentPhotoResponse | null>(null)

  async function analyser() {
    if (!file) return
    setChargement(true)
    try {
      setResultat(await analyserDocument(file))
    } catch {
      toast.error('Analyse document indisponible.')
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold">Analyse document</h1><p className="text-muted-foreground">OCR et classement automatique d’un document photographié.</p></div>
      <Card><CardHeader><CardTitle>Importer un document</CardTitle><CardDescription>Facture, contrat, document administratif ou ordonnance.</CardDescription></CardHeader><CardContent className="space-y-4"><input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} /><Button onClick={analyser} disabled={!file || chargement}>{chargement ? 'Analyse...' : 'Analyser le document'}</Button></CardContent></Card>
      {resultat && <div className="grid gap-4 lg:grid-cols-2"><Card><CardHeader><CardTitle>{resultat.titre}</CardTitle></CardHeader><CardContent className="space-y-2"><p>Type : {resultat.type_document}</p>{resultat.emetteur && <p>Émetteur : {resultat.emetteur}</p>}{resultat.date_document && <p>Date : {resultat.date_document}</p>}{typeof resultat.montant === 'number' && <p>Montant : {resultat.montant} €</p>}</CardContent></Card><Card><CardHeader><CardTitle>Actions suggérées</CardTitle></CardHeader><CardContent><ul className="space-y-2">{resultat.actions_suggerees.map((item, index) => <li key={index}>• {item}</li>)}</ul></CardContent></Card><Card className="lg:col-span-2"><CardHeader><CardTitle>Informations clés</CardTitle></CardHeader><CardContent><ul className="space-y-2">{resultat.informations_cles.map((item, index) => <li key={index}>• {item}</li>)}</ul></CardContent></Card></div>}
    </div>
  )
}
