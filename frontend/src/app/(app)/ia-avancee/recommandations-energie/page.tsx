'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { obtenirRecommandationsEnergie, type EconomiesEnergieResponse } from '@/bibliotheque/api/ia_avancee'
import { toast } from 'sonner'

export default function RecommandationsEnergiePage() {
  const [chargement, setChargement] = useState(false)
  const [resultat, setResultat] = useState<EconomiesEnergieResponse | null>(null)

  async function charger() {
    setChargement(true)
    try {
      setResultat(await obtenirRecommandationsEnergie())
    } catch {
      toast.error('Recommandations énergie indisponibles.')
    } finally {
      setChargement(false)
    }
  }

  useEffect(() => { void charger() }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4"><div><h1 className="text-3xl font-bold">Recommandations énergie</h1><p className="text-muted-foreground">Actions prioritaires pour réduire la consommation.</p></div><Button onClick={charger} disabled={chargement}>{chargement ? 'Actualisation...' : 'Actualiser'}</Button></div>
      {!resultat && !chargement && (
        <Card>
          <CardHeader><CardTitle>Chargement initial terminé</CardTitle></CardHeader>
          <CardContent><p className="text-sm text-muted-foreground">Aucune recommandation disponible actuellement. Réessaie via Actualiser.</p></CardContent>
        </Card>
      )}
      {resultat && <div className="space-y-4"><Card><CardHeader><CardTitle>Potentiel global</CardTitle></CardHeader><CardContent className="space-y-2"><p>{resultat.consommation_actuelle_resume}</p><p className="font-medium">{resultat.potentiel_economie_global}</p></CardContent></Card><div className="grid gap-4 md:grid-cols-2">{resultat.recommandations.map((item, index) => <Card key={`${item.titre}-${index}`}><CardHeader><CardTitle>{item.titre}</CardTitle></CardHeader><CardContent className="space-y-2"><p>{item.description}</p><p className="text-sm text-muted-foreground">Catégorie : {item.categorie} • Difficulté : {item.difficulte}</p>{item.economie_estimee && <p className="text-sm">Économie estimée : {item.economie_estimee}</p>}{item.cout_mise_en_oeuvre && <p className="text-sm">Coût : {item.cout_mise_en_oeuvre}</p>}</CardContent></Card>)}</div></div>}
    </div>
  )
}
