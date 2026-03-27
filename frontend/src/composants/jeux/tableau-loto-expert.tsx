'use client'

import { useState, useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import { Input } from '@/composants/ui/input'
import { Label } from '@/composants/ui/label'
import { Button } from '@/composants/ui/button'
import { Badge } from '@/composants/ui/badge'
import { Skeleton } from '@/composants/ui/skeleton'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/composants/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/composants/ui/table'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/composants/ui/dropdown-menu'
import { utiliserRequete } from '@/crochets/utiliser-api'
import { MoreVertical, Download, TrendingUp, Flame, Snowflake, Clock } from 'lucide-react'
import { CSVLink } from 'react-csv'

interface Filtres {
  strategie: 'toutes' | 'equilibree' | 'frequences' | 'retards' | 'ia_creative'
  qualite_min: number
  date_min: string
  date_max: string
  search: string
}

interface GrilleLoto {
  id: number
  numeros: number[]
  numero_chance: number
  date_tirage: string
  strategie: string
  qualite: number
  distribution: {
    nb_pairs: number
    nb_impairs: number
    somme: number
    nb_hauts: number
    nb_bas: number
  }
  backtest?: {
    rang: number
    nb_bons: number
    gain: number
  }
  statut: 'en_attente' | 'joue' | 'gagnant' | 'perdant'
}

interface TableauLotoExpertProps {
  onCreerGrille?: (grille: GrilleLoto) => void
  onVoirDetails?: (grille: GrilleLoto) => void
}

const STRATEGIES = [
  { value: 'toutes', label: 'Toutes stratégies' },
  { value: 'equilibree', label: '⚖️ Équilibrée' },
  { value: 'frequences', label: '🔥 Fréquences' },
  { value: 'retards', label: '⏰ Retards' },
  { value: 'ia_creative', label: '🤖 IA Créative' }
]

export function TableauLotoExpert({
  onCreerGrille,
  onVoirDetails
}: TableauLotoExpertProps) {
  const [filtres, setFiltres] = useState<Filtres>({
    strategie: 'toutes',
    qualite_min: 60,
    date_min: '',
    date_max: '',
    search: ''
  })

  // Récupérer grilles avec filtres
  const queryParams = useMemo(() => {
    const params = new URLSearchParams()
    if (filtres.strategie !== 'toutes') params.set('strategie', filtres.strategie)
    if (filtres.qualite_min > 0) params.set('qualite_min', filtres.qualite_min.toString())
    if (filtres.date_min) params.set('date_min', filtres.date_min)
    if (filtres.date_max) params.set('date_max', filtres.date_max)
    if (filtres.search) params.set('search', filtres.search)
    return params.toString()
  }, [filtres])

  const { data: grilles = [], isLoading } = utiliserRequete<GrilleLoto[]>(
    ['loto-expert', queryParams],
    `/api/v1/jeux/loto/grilles-expert?${queryParams}`
  )

  // Export CSV
  const csvData = useMemo(() => {
    return grilles.map(g => ({
      Date: g.date_tirage,
      Numeros: g.numeros.join('-'),
      Chance: g.numero_chance,
      Strategie: g.strategie,
      Qualite: g.qualite,
      Pairs: g.distribution.nb_pairs,
      Impairs: g.distribution.nb_impairs,
      Somme: g.distribution.somme,
      Statut: g.statut,
      Gain: g.backtest?.gain || 0
    }))
  }, [grilles])

  const couleurQualite = (qualite: number) => {
    if (qualite >= 80) return 'text-green-600'
    if (qualite >= 60) return 'text-yellow-600'
    return 'text-orange-600'
  }

  const couleurStrategie = (strategie: string) => {
    switch (strategie) {
      case 'équilibrée': return 'bg-blue-100 text-blue-800'
      case 'fréquences': return 'bg-orange-100 text-orange-800'
      case 'retards': return 'bg-purple-100 text-purple-800'
      case 'IA créative': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-60" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-96 w-full" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              🎰 Tableau Expert Loto
              <Badge variant="secondary">{grilles.length} grilles</Badge>
            </CardTitle>
            <CardDescription>
              Analyse avancée des grilles avec backtest et statistiques
            </CardDescription>
          </div>

          <CSVLink
            data={csvData}
            filename={`loto_expert_${new Date().toISOString().split('T')[0]}.csv`}
            className="inline-flex"
          >
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
          </CSVLink>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Filtres */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-lg border bg-gray-50">
          <div className="space-y-2">
            <Label>Stratégie</Label>
            <Select
              value={filtres.strategie}
              onValueChange={(val) => setFiltres({ ...filtres, strategie: val as any })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {STRATEGIES.map(s => (
                  <SelectItem key={s.value} value={s.value}>
                    {s.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Qualité min (%)</Label>
            <Input
              type="number"
              min="0"
              max="100"
              value={filtres.qualite_min}
              onChange={(e) => setFiltres({ ...filtres, qualite_min: Number(e.target.value) })}
            />
          </div>

          <div className="space-y-2">
            <Label>Recherche</Label>
            <Input
              placeholder="Numéros, date..."
              value={filtres.search}
              onChange={(e) => setFiltres({ ...filtres, search: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label>Date min</Label>
            <Input
              type="date"
              value={filtres.date_min}
              onChange={(e) => setFiltres({ ...filtres, date_min: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label>Date max</Label>
            <Input
              type="date"
              value={filtres.date_max}
              onChange={(e) => setFiltres({ ...filtres, date_max: e.target.value })}
            />
          </div>

          <div className="flex items-end">
            <Button
              variant="outline"
              onClick={() => setFiltres({
                strategie: 'toutes',
                qualite_min: 60,
                date_min: '',
                date_max: '',
                search: ''
              })}
              className="w-full"
            >
              Réinitialiser
            </Button>
          </div>
        </div>

        {/* Tableau */}
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Numéros</TableHead>
                <TableHead>Chance</TableHead>
                <TableHead>Stratégie</TableHead>
                <TableHead>Qualité</TableHead>
                <TableHead>Distribution</TableHead>
                <TableHead>Backtest</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {grilles.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} className="text-center text-gray-500 py-8">
                    Aucune grille trouvée avec ces filtres
                  </TableCell>
                </TableRow>
              ) : (
                grilles.map((grille) => (
                  <TableRow key={grille.id} className="hover:bg-gray-50">
                    <TableCell className="font-mono text-sm">
                      {new Date(grille.date_tirage).toLocaleDateString('fr-FR')}
                    </TableCell>

                    <TableCell>
                      <div className="flex gap-1">
                        {grille.numeros.map((num, i) => (
                          <span
                            key={i}
                            className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-900"
                          >
                            {num}
                          </span>
                        ))}
                      </div>
                    </TableCell>

                    <TableCell>
                      <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-yellow-100 text-xs font-bold text-yellow-900">
                        {grille.numero_chance}
                      </span>
                    </TableCell>

                    <TableCell>
                      <Badge className={couleurStrategie(grille.strategie)}>
                        {grille.strategie}
                      </Badge>
                    </TableCell>

                    <TableCell>
                      <span className={`font-semibold ${couleurQualite(grille.qualite)}`}>
                        {grille.qualite}%
                      </span>
                    </TableCell>

                    <TableCell className="text-xs text-gray-600">
                      <div>{grille.distribution.nb_pairs}P / {grille.distribution.nb_impairs}I</div>
                      <div>{grille.distribution.nb_hauts}H / {grille.distribution.nb_bas}B</div>
                      <div>Σ={grille.distribution.somme}</div>
                    </TableCell>

                    <TableCell>
                      {grille.backtest ? (
                        <div className="text-sm">
                          <div className="font-semibold">Rang {grille.backtest.rang}</div>
                          <div className="text-xs text-gray-600">
                            {grille.backtest.nb_bons} bons / {grille.backtest.gain}€
                          </div>
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400">-</span>
                      )}
                    </TableCell>

                    <TableCell>
                      <Badge variant={
                        grille.statut === 'gagnant' ? 'default' :
                        grille.statut === 'perdant' ? 'destructive' : 'secondary'
                      }>
                        {grille.statut}
                      </Badge>
                    </TableCell>

                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => onVoirDetails?.(grille)}>
                            Voir détails
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => onCreerGrille?.(grille)}>
                            Dupliquer grille
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
