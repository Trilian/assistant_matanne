'use client'

import { useEffect, useMemo, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/composants/ui/select'
import { Badge } from '@/composants/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/composants/ui/table'
import { clientApi } from '@/bibliotheque/api/client'
import type { ReponsePaginee } from '@/types/api'
import type { Recette } from '@/types/recettes'
import { toast } from 'sonner'

type Metrique = {
  label: string
  unite: string
  getValeur: (recette: Recette) => number
  objectif: 'plus' | 'moins'
}

const METRIQUES: Metrique[] = [
  { label: 'Calories', unite: 'kcal', getValeur: (r) => r.calories ?? 0, objectif: 'moins' },
  { label: 'Proteines', unite: 'g', getValeur: (r) => r.proteines ?? 0, objectif: 'plus' },
  { label: 'Glucides', unite: 'g', getValeur: (r) => r.glucides ?? 0, objectif: 'moins' },
  { label: 'Lipides', unite: 'g', getValeur: (r) => r.lipides ?? 0, objectif: 'moins' },
]

function estRecetteNutriDisponible(recette: Recette): boolean {
  return (
    recette.calories !== undefined &&
    recette.proteines !== undefined &&
    recette.glucides !== undefined &&
    recette.lipides !== undefined
  )
}

export default function ComparateurRecettesPage() {
  const [chargement, setChargement] = useState(false)
  const [recettes, setRecettes] = useState<Recette[]>([])
  const [recetteAId, setRecetteAId] = useState<string>('')
  const [recetteBId, setRecetteBId] = useState<string>('')

  useEffect(() => {
    async function charger() {
      setChargement(true)
      try {
        const { data } = await clientApi.get<ReponsePaginee<Recette>>('/recettes', {
          params: { page: 1, page_size: 150 },
        })
        const items = data?.items ?? []
        const recipesNutri = items.filter(estRecetteNutriDisponible)
        setRecettes(recipesNutri)

        if (recipesNutri.length >= 2) {
          setRecetteAId(String(recipesNutri[0].id))
          setRecetteBId(String(recipesNutri[1].id))
        }
      } catch {
        toast.error('Impossible de charger les recettes nutritionnelles.')
      } finally {
        setChargement(false)
      }
    }

    void charger()
  }, [])

  const recetteA = useMemo(
    () => recettes.find((r) => String(r.id) === recetteAId) ?? null,
    [recetteAId, recettes]
  )
  const recetteB = useMemo(
    () => recettes.find((r) => String(r.id) === recetteBId) ?? null,
    [recetteBId, recettes]
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Comparateur recettes nutritionnel</h1>
        <p className="text-muted-foreground">
          Compare deux recettes enrichies pour visualiser les ecarts calories/macros en un coup d'oeil.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Selection des recettes</CardTitle>
          <CardDescription>
            Seules les recettes avec donnees nutritionnelles completes sont proposees.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          <Select value={recetteAId} onValueChange={setRecetteAId}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Choisir recette A" />
            </SelectTrigger>
            <SelectContent>
              {recettes.map((recette) => (
                <SelectItem key={`a-${recette.id}`} value={String(recette.id)}>
                  {recette.nom}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={recetteBId} onValueChange={setRecetteBId}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Choisir recette B" />
            </SelectTrigger>
            <SelectContent>
              {recettes.map((recette) => (
                <SelectItem key={`b-${recette.id}`} value={String(recette.id)}>
                  {recette.nom}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {chargement && (
        <Card>
          <CardContent className="pt-6 text-sm text-muted-foreground">Chargement des recettes...</CardContent>
        </Card>
      )}

      {!chargement && recettes.length < 2 && (
        <Card>
          <CardContent className="pt-6 text-sm text-muted-foreground">
            Il faut au moins 2 recettes enrichies nutritionnellement. Lance d'abord l'enrichissement nutrition depuis le module recettes.
          </CardContent>
        </Card>
      )}

      {recetteA && recetteB && (
        <Card>
          <CardHeader>
            <CardTitle>Comparaison visuelle</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-lg border p-3">
                <p className="text-xs text-muted-foreground">Recette A</p>
                <p className="font-semibold">{recetteA.nom}</p>
              </div>
              <div className="rounded-lg border p-3">
                <p className="text-xs text-muted-foreground">Recette B</p>
                <p className="font-semibold">{recetteB.nom}</p>
              </div>
            </div>

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Metrique</TableHead>
                  <TableHead>{recetteA.nom}</TableHead>
                  <TableHead>{recetteB.nom}</TableHead>
                  <TableHead>Ecart</TableHead>
                  <TableHead>Lecture rapide</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {METRIQUES.map((metrique) => {
                  const valeurA = metrique.getValeur(recetteA)
                  const valeurB = metrique.getValeur(recetteB)
                  const ecart = Number((valeurA - valeurB).toFixed(1))
                  const gagnant =
                    metrique.objectif === 'plus'
                      ? valeurA >= valeurB
                        ? 'A'
                        : 'B'
                      : valeurA <= valeurB
                        ? 'A'
                        : 'B'

                  return (
                    <TableRow key={metrique.label}>
                      <TableCell className="font-medium">{metrique.label}</TableCell>
                      <TableCell>{valeurA.toFixed(1)} {metrique.unite}</TableCell>
                      <TableCell>{valeurB.toFixed(1)} {metrique.unite}</TableCell>
                      <TableCell>{ecart > 0 ? '+' : ''}{ecart} {metrique.unite}</TableCell>
                      <TableCell>
                        <Badge variant={gagnant === 'A' ? 'secondary' : 'outline'}>
                          Avantage {gagnant}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
