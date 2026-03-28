/**
 * Composant Stats Personnelles - Affiche ROI, win rate, patterns et évolution
 * 
 * Fonctionnalités:
 * - 4 cartes métriques (ROI, Win Rate, Bénéfice, Nombre)
 * - Graphique évolution mensuelle (Chart.js)
 * - Tableau patterns gagnants
 * - Recommandations personnalisées
 */

'use client'

import { useMemo, useState } from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import { Badge } from '@/composants/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/composants/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/composants/ui/select'
import { utiliserRequete } from '@/crochets/utiliser-api'
import { TrendingUp, TrendingDown, Target, Trophy, AlertCircle } from 'lucide-react'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface StatsData {
  roi: {
    roi: number
    gains_totaux: number
    mises_totales: number
    benefice_net: number
    nb_paris: number
    nb_grilles: number
    periode_jours: number
  }
  win_rate: {
    win_rate_global: number
    win_rate_paris: number
    win_rate_loto: number
    win_rate_euromillions: number
    nb_gagnants: number
    nb_total: number
    periode_jours: number
  }
  patterns: {
    meilleur_type_pari: string | null
    meilleure_strategie_loto: string | null
    meilleure_strategie_euro: string | null
    roi_par_type: Record<string, { roi: number; nb: number }>
    recommandations: string[]
    periode_jours: number
  }
  evolution: Array<{
    mois: string
    roi: number
    benefice: number
    gains: number
    mises: number
  }>
}

interface StatsPersonnellesProps {
  userId: string | number
}

export function StatsPersonnelles({ userId }: StatsPersonnellesProps) {
  const [periode, setPeriode] = useState<number>(30)

  // Fetch stats data
  const { data, isLoading, error } = utiliserRequete<StatsData>(
    ['jeux', 'stats-personnelles', userId, periode],
    async () => {
      const response = await fetch(`/api/v1/jeux/stats/personnelles/${userId}?periode=${periode}`)
      if (!response.ok) throw new Error('Erreur chargement stats')
      return response.json()
    },
    {
      enabled: !!userId,
      staleTime: 5 * 60 * 1000 // 5 minutes
    }
  )

  // Chart data
  const chartData = useMemo(() => {
    if (!data?.evolution) return null

    return {
      labels: data.evolution.map(e => e.mois),
      datasets: [
        {
          label: 'Bénéfice (€)',
          data: data.evolution.map(e => e.benefice),
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          fill: true,
          tension: 0.3
        },
        {
          label: 'ROI (%)',
          data: data.evolution.map(e => e.roi),
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true,
          tension: 0.3,
          yAxisID: 'y1'
        }
      ]
    }
  }, [data?.evolution])

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false
    },
    plugins: {
      legend: {
        position: 'top' as const
      },
      title: {
        display: false
      }
    },
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Bénéfice (€)'
        }
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'ROI (%)'
        },
        grid: {
          drawOnChartArea: false
        }
      }
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <span className="ml-2">Chargement statistiques...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !data) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center text-destructive">
            <AlertCircle className="mr-2 h-5 w-5" />
            <span>Erreur chargement statistiques</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  const { roi, win_rate, patterns } = data

  return (
    <div className="space-y-6">
      {/* Sélecteur période */}
      <div className="flex items-center gap-2">
        <label className="text-sm font-medium">Période:</label>
        <Select value={periode.toString()} onValueChange={v => setPeriode(parseInt(v))}>
          <SelectTrigger className="w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7">7 jours</SelectItem>
            <SelectItem value="30">30 jours</SelectItem>
            <SelectItem value="90">90 jours</SelectItem>
            <SelectItem value="180">6 mois</SelectItem>
            <SelectItem value="365">1 an</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Cartes métriques */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* ROI Global */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>ROI Global</CardDescription>
            <CardTitle className="text-3xl flex items-center gap-2">
              {roi.roi >= 0 ? (
                <TrendingUp className="h-6 w-6 text-green-600" />
              ) : (
                <TrendingDown className="h-6 w-6 text-red-600" />
              )}
              <span className={roi.roi >= 0 ? 'text-green-600' : 'text-red-600'}>
                {roi.roi.toFixed(1)}%
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              {roi.mises_totales.toFixed(2)}€ misés
            </p>
          </CardContent>
        </Card>

        {/* Win Rate */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Win Rate</CardDescription>
            <CardTitle className="text-3xl flex items-center gap-2">
              <Target className="h-6 w-6 text-blue-600" />
              <span className="text-blue-600">{win_rate.win_rate_global.toFixed(1)}%</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              {win_rate.nb_gagnants} / {win_rate.nb_total} paris
            </p>
          </CardContent>
        </Card>

        {/* Bénéfice Net */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Bénéfice Net</CardDescription>
            <CardTitle className="text-3xl flex items-center gap-2">
              <Trophy className="h-6 w-6 text-yellow-600" />
              <span className={roi.benefice_net >= 0 ? 'text-green-600' : 'text-red-600'}>
                {roi.benefice_net.toFixed(2)}€
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              {roi.gains_totaux.toFixed(2)}€ gagnés
            </p>
          </CardContent>
        </Card>

        {/* Nombre de paris */}
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Activité</CardDescription>
            <CardTitle className="text-3xl">{roi.nb_paris + roi.nb_grilles}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              {roi.nb_paris} paris • {roi.nb_grilles} grilles
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs: Évolution / Patterns / Détails */}
      <Tabs defaultValue="evolution">
        <TabsList>
          <TabsTrigger value="evolution">📈 Évolution</TabsTrigger>
          <TabsTrigger value="patterns">🎯 Patterns</TabsTrigger>
          <TabsTrigger value="details">📊 Détails</TabsTrigger>
        </TabsList>

        {/* Tab Évolution */}
        <TabsContent value="evolution" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Évolution sur 6 mois</CardTitle>
              <CardDescription>Bénéfice et ROI mensuels</CardDescription>
            </CardHeader>
            <CardContent>
              {chartData && (
                <div style={{ height: '300px' }}>
                  <Line data={chartData} options={chartOptions} />
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab Patterns */}
        <TabsContent value="patterns" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Patterns Gagnants</CardTitle>
              <CardDescription>Vos stratégies les plus rentables</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Recommandations */}
              {patterns.recommandations.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-semibold text-sm">💡 Recommandations</h4>
                  <ul className="space-y-1">
                    {patterns.recommandations.map((rec, idx) => (
                      <li key={idx} className="text-sm flex items-start gap-2">
                        <Badge variant="outline" className="mt-0.5">
                          {idx + 1}
                        </Badge>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* ROI par type de pari */}
              {Object.keys(patterns.roi_par_type).length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-semibold text-sm">📊 ROI par type de pari</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    {Object.entries(patterns.roi_par_type).map(([type, data]) => (
                      <Card key={type} className="p-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium">{type}</span>
                          <Badge variant={data.roi >= 0 ? 'default' : 'destructive'}>
                            {data.roi.toFixed(1)}%
                          </Badge>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">{data.nb} paris</p>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* Meilleures stratégies */}
              <div className="space-y-2">
                <h4 className="font-semibold text-sm">🏆 Meilleures stratégies</h4>
                <div className="grid gap-2">
                  {patterns.meilleur_type_pari && (
                    <div className="flex items-center gap-2 text-sm">
                      <Badge>Paris</Badge>
                      <span>{patterns.meilleur_type_pari}</span>
                    </div>
                  )}
                  {patterns.meilleure_strategie_loto && (
                    <div className="flex items-center gap-2 text-sm">
                      <Badge>Loto</Badge>
                      <span>{patterns.meilleure_strategie_loto}</span>
                    </div>
                  )}
                  {patterns.meilleure_strategie_euro && (
                    <div className="flex items-center gap-2 text-sm">
                      <Badge>Euromillions</Badge>
                      <span>{patterns.meilleure_strategie_euro}</span>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab Détails */}
        <TabsContent value="details" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Win Rate par jeu */}
            <Card>
              <CardHeader>
                <CardTitle>Win Rate par jeu</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Paris Sportifs</span>
                  <Badge variant={win_rate.win_rate_paris >= 50 ? 'default' : 'secondary'}>
                    {win_rate.win_rate_paris.toFixed(1)}%
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Loto</span>
                  <Badge variant={win_rate.win_rate_loto >= 5 ? 'default' : 'secondary'}>
                    {win_rate.win_rate_loto.toFixed(1)}%
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Euromillions</span>
                  <Badge variant={win_rate.win_rate_euromillions >= 5 ? 'default' : 'secondary'}>
                    {win_rate.win_rate_euromillions.toFixed(1)}%
                  </Badge>
                </div>
              </CardContent>
            </Card>

            {/* Résumé financier */}
            <Card>
              <CardHeader>
                <CardTitle>Résumé Financier</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Gains Totaux</span>
                  <span className="font-semibold text-green-600">
                    {roi.gains_totaux.toFixed(2)}€
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Mises Totales</span>
                  <span className="font-semibold text-red-600">
                    -{roi.mises_totales.toFixed(2)}€
                  </span>
                </div>
                <div className="h-px bg-border"></div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-bold">Bénéfice Net</span>
                  <span
                    className={`font-bold ${
                      roi.benefice_net >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {roi.benefice_net >= 0 ? '+' : ''}
                    {roi.benefice_net.toFixed(2)}€
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
