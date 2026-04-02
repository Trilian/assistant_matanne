'use client'

import { useState, useEffect, useMemo } from 'react'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ReferenceLine,
} from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import { Input } from '@/composants/ui/input'
import { Label } from '@/composants/ui/label'
import { Badge } from '@/composants/ui/badge'
import { Skeleton } from '@/composants/ui/skeleton'
import { Slider } from '@/composants/ui/slider'
import { utiliserRequete } from '@/crochets/utiliser-api'
import { TrendingUp, TrendingDown, AlertTriangle, DollarSign, Info } from 'lucide-react'
import { Tooltip as TooltipUI, TooltipContent, TooltipProvider, TooltipTrigger } from '@/composants/ui/tooltip'

interface SuggestionMise {
  mise_suggeree: number
  mise_kelly_complete: number
  fraction_utilisee: number
  edge: number
  pourcentage_bankroll: number
  confiance: 'faible' | 'moyenne' | 'haute'
  message: string
}

interface BankrollData {
  bankroll_actuelle: number
  bankroll_initiale: number
  variation_totale: number
  roi: number
  historique: Array<{
    date: string
    bankroll: number
    variation: number
  }>
}

interface BankrollWidgetProps {
  userId: number
  /** Cote pour calcul Kelly (optionnel) */
  cote?: number
  /** Edge/EV pour calcul Kelly (optionnel) */
  edge?: number
  /** Confiance IA pour calcul Kelly (optionnel) */
  confianceIA?: number
  /** Mode compact (sans graphique) */
  compact?: boolean
}

export function BankrollWidget({
  userId,
  cote,
  edge,
  confianceIA,
  compact = false
}: BankrollWidgetProps) {
  const [bankrollInitiale, setBankrollInitiale] = useState(1000)
  const [coteLocale, setCoteLocale] = useState(cote || 2.0)
  const [edgeLocal, setEdgeLocal] = useState(edge ? edge * 100 : 5) // En pourcentage

  // Récupérer données bankroll
  const { data: bankrollData, isLoading: loadingBankroll } = utiliserRequete<BankrollData>(
    ['bankroll', String(userId), String(bankrollInitiale)],
    async () => {
      const reponse = await fetch(`/api/v1/jeux/bankroll/${userId}?bankroll_initiale=${bankrollInitiale}`)
      if (!reponse.ok) throw new Error('Impossible de charger la bankroll')
      return reponse.json() as Promise<BankrollData>
    }
  )

  // Récupérer suggestion Kelly
  const { data: suggestion } = utiliserRequete<SuggestionMise>(
    [
      'suggestion-mise',
      String(userId),
      String(bankrollData?.bankroll_actuelle ?? ''),
      String(coteLocale),
      String(edgeLocal),
      String(confianceIA ?? 70),
    ],
    async () => {
      const reponse = await fetch(
        `/api/v1/jeux/bankroll/suggestion-mise?` +
          `bankroll=${bankrollData!.bankroll_actuelle}&` +
          `edge=${edgeLocal / 100}&` +
          `cote=${coteLocale}&` +
          `confiance_ia=${confianceIA || 70}`
      )
      if (!reponse.ok) throw new Error('Impossible de calculer la mise suggérée')
      return reponse.json() as Promise<SuggestionMise>
    },
    { enabled: !!bankrollData && coteLocale > 1 && edgeLocal > 0 }
  )

  // Synchroniser avec props si changement
  useEffect(() => {
    if (cote !== undefined) setCoteLocale(cote)
  }, [cote])

  useEffect(() => {
    if (edge !== undefined) setEdgeLocal(edge * 100)
  }, [edge])

  // Préparer données graphique
  const chartData = useMemo(() => {
    if (!bankrollData?.historique) return null

    return bankrollData.historique.map((h) => {
      const date = new Date(h.date)
      return {
        ...h,
        libelle: date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' }),
      }
    })
  }, [bankrollData])

  if (loadingBankroll) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-4 w-60" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-64 w-full" />
        </CardContent>
      </Card>
    )
  }

  const couleurConfiance = (conf: string) => {
    switch (conf) {
      case 'haute':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'moyenne':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'faible':
        return 'bg-red-100 text-red-800 border-red-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const iconeVariation = bankrollData && bankrollData.variation_totale >= 0 ? TrendingUp : TrendingDown
  const IconeVariation = iconeVariation

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              Gestion Bankroll
            </CardTitle>
            <CardDescription>
              Money management avec critère de Kelly (25%)
            </CardDescription>
          </div>
          
          {bankrollData && (
            <div className="text-right">
              <div className="text-2xl font-bold">
                {bankrollData.bankroll_actuelle.toFixed(2)}€
              </div>
              <div className={`flex items-center gap-1 text-sm ${
                bankrollData.variation_totale >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                <IconeVariation className="h-4 w-4" />
                {bankrollData.variation_totale >= 0 ? '+' : ''}
                {bankrollData.variation_totale.toFixed(2)}€ ({bankrollData.roi.toFixed(1)}%)
              </div>
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Configuration bankroll initiale */}
        <div className="space-y-2">
          <Label htmlFor="bankroll-initiale" className="flex items-center gap-2">
            Bankroll initiale
            <TooltipProvider>
              <TooltipUI>
                <TooltipTrigger>
                  <Info className="h-3 w-3 text-gray-400" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Montant de départ pour calculer la progression</p>
                </TooltipContent>
              </TooltipUI>
            </TooltipProvider>
          </Label>
          <Input
            id="bankroll-initiale"
            type="number"
            min="100"
            step="100"
            value={bankrollInitiale}
            onChange={(e) => setBankrollInitiale(Number(e.target.value))}
            className="max-w-xs"
          />
        </div>

        {/* Calculateur Kelly */}
        {!compact && (
          <div className="space-y-4 rounded-lg border p-4 bg-blue-50/50">
            <h3 className="font-semibold text-sm flex items-center gap-2">
              📊 Calculateur de mise Kelly
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="cote">Cote décimale</Label>
                <Input
                  id="cote"
                  type="number"
                  min="1.01"
                  step="0.1"
                  value={coteLocale}
                  onChange={(e) => setCoteLocale(Number(e.target.value))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="edge">Edge / EV (%)</Label>
                <div className="space-y-2">
                  <Slider
                    id="edge"
                    min={0}
                    max={20}
                    step={0.5}
                    value={[edgeLocal]}
                    onValueChange={(val) => setEdgeLocal(val[0])}
                  />
                  <div className="text-sm text-gray-600 text-right">
                    {edgeLocal.toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>

            {/* Suggestion */}
            {suggestion && (
              <div className="mt-4 p-4 rounded-lg bg-white border-2 border-blue-200">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="text-3xl font-bold text-blue-600">
                      {suggestion.mise_suggeree.toFixed(2)}€
                    </div>
                    <div className="text-sm text-gray-500">
                      Mise suggérée ({suggestion.pourcentage_bankroll.toFixed(2)}% bankroll)
                    </div>
                  </div>
                  
                  <Badge className={couleurConfiance(suggestion.confiance)}>
                    Confiance: {suggestion.confiance}
                  </Badge>
                </div>

                <p className="text-sm text-gray-700 mb-2">
                  {suggestion.message}
                </p>

                <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                  <div>
                    <span className="font-semibold">Kelly complet:</span> {suggestion.mise_kelly_complete.toFixed(2)}€
                  </div>
                  <div>
                    <span className="font-semibold">Fraction:</span> {(suggestion.fraction_utilisee * 100).toFixed(0)}%
                  </div>
                </div>

                {suggestion.pourcentage_bankroll > 3 && (
                  <div className="mt-3 flex items-start gap-2 p-2 rounded bg-orange-50 border border-orange-200">
                    <AlertTriangle className="h-4 w-4 text-orange-600 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-orange-800">
                      <strong>Attention:</strong> Cette mise représente plus de 3% de votre bankroll. 
                      Risque élevé de grosse perte.
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Graphique évolution */}
        {!compact && chartData && (
          <div className="space-y-2">
            <h3 className="font-semibold text-sm">Évolution bankroll (30 derniers jours)</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="libelle" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `${Number(v).toFixed(0)}€`} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--background))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                    }}
                    formatter={(value, name) => [`${Number(value).toFixed(2)}€`, String(name)]}
                  />
                  {!compact && <Legend />}
                  <ReferenceLine
                    y={bankrollData?.bankroll_initiale ?? 0}
                    stroke="hsl(215 16% 55%)"
                    strokeDasharray="5 5"
                    label={{ value: 'Initiale', position: 'insideTopRight', fontSize: 10 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="bankroll"
                    name="Bankroll"
                    stroke={bankrollData && bankrollData.variation_totale >= 0 ? 'hsl(var(--chart-2))' : 'hsl(var(--destructive))'}
                    strokeWidth={2}
                    dot={{ r: 2 }}
                    activeDot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Stats compactes */}
        {compact && bankrollData && (
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-500">Initiale</div>
              <div className="font-semibold">{bankrollData.bankroll_initiale.toFixed(2)}€</div>
            </div>
            <div>
              <div className="text-gray-500">ROI</div>
              <div className={`font-semibold ${bankrollData.roi >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {bankrollData.roi.toFixed(1)}%
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
