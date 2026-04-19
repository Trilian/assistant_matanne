'use client'

import React, { useState } from 'react'
import { ScenarioSimulation, ComparaisonScenarios } from '@/types/maison'
import { Card } from '@/composants/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/composants/ui/table'
import { Badge } from '@/composants/ui/badge'
import { Button } from '@/composants/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/composants/ui/dialog'
import { Check, TrendingUp, Clock, CreditCard, AlertCircle, Target } from 'lucide-react'

interface ComparatorScenariosProps {
  scenarios: ScenarioSimulation[]
  comparaison?: ComparaisonScenarios
  scenarioSelectionnéId?: number
  onSelectScenario?: (scenarioId: number) => void
  readOnly?: boolean
}

// Utilitaires
const formatBudget = (min?: number, max?: number) => {
  if (typeof min !== 'number' || typeof max !== 'number') {
    return 'N/A'
  }
  return `${(min / 1000).toFixed(1)}k - ${(max / 1000).toFixed(1)}k €`
}

const formatDuree = (jours?: number) => {
  if (typeof jours !== 'number') return 'N/A'
  if (jours < 1) return `${Math.round(jours * 24)}h`
  if (jours < 30) return `${Math.round(jours)}j`
  const mois = Math.round(jours / 30)
  return `${mois}m`
}

const getColorFaisabilite = (score?: number) => {
  if (typeof score !== 'number') return 'bg-gray-100 text-gray-800'
  if (score >= 80) return 'bg-green-100 text-green-800'
  if (score >= 50) return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
}

const getColorDPE = (impact: string | undefined) => {
  if (!impact) return 'bg-gray-100 text-gray-800'
  const lower = impact.toLowerCase()
  if (lower.includes('meilleur') || lower.includes('améliore')) return 'bg-green-100 text-green-800'
  if (lower.includes('maintien')) return 'bg-blue-100 text-blue-800'
  return 'bg-gray-100 text-gray-800'
}

/**
 * Comparateur de scénarios
 * Affiche un tableau comparant tous les scénarios d'une simulation
 * Permet de voir en un coup d'œil budget, durée, faisabilité, impact DPE
 */
export function ComparateurScenarios({
  scenarios,
  comparaison,
  scenarioSelectionnéId,
  onSelectScenario,
  readOnly = false,
}: ComparatorScenariosProps) {
  const [_scenarioDetailId, setScenarioDetailId] = useState<number | null>(null)
  
  if (!scenarios || scenarios.length === 0) {
    return (
      <Card className="p-8 text-center text-gray-400">
        <AlertCircle className="mx-auto mb-2" size={32} />
        Aucun scénario pour cette simulation
      </Card>
    )
  }

  // Identifier les meilleurs scénarios
  const meilleurBudget = comparaison?.meilleur_budget ?? scenarios[0]?.id
  const meilleurFaisabilite = comparaison?.meilleur_faisabilite ?? scenarios[0]?.id
  const meilleurRapport = comparaison?.meilleur_rapport ?? scenarios[0]?.id

  return (
    <div className="space-y-6">
      {/* Résumé statistique */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Scénario moins cher */}
        {scenarios
          .filter((s) => s.id === meilleurBudget)
          .map((s) => (
            <Card key={s.id} className="p-4 bg-green-50 border-green-200">
              <div className="flex items-center gap-3">
                <CreditCard className="text-green-600" size={24} />
                <div>
                  <div className="text-xs font-semibold text-green-600">MOINS CHER</div>
                  <div className="font-semibold">{s.nom}</div>
                  <div className="text-xs text-gray-600">
                    {formatBudget(s.budget_estime_min, s.budget_estime_max)}
                  </div>
                </div>
              </div>
            </Card>
          ))}

        {/* Plus faisable */}
        {scenarios
          .filter((s) => s.id === meilleurFaisabilite)
          .map((s) => (
            <Card key={s.id} className="p-4 bg-blue-50 border-blue-200">
              <div className="flex items-center gap-3">
                <Target className="text-blue-600" size={24} />
                <div>
                  <div className="text-xs font-semibold text-blue-600">PLUS FAISABLE</div>
                  <div className="font-semibold">{s.nom}</div>
                  <div className="text-xs text-gray-600">{s.score_faisabilite}% réalisable</div>
                </div>
              </div>
            </Card>
          ))}

        {/* Meilleur rapport qualité/prix */}
        {scenarios
          .filter((s) => s.id === meilleurRapport)
          .map((s) => (
            <Card key={s.id} className="p-4 bg-purple-50 border-purple-200">
              <div className="flex items-center gap-3">
                <TrendingUp className="text-purple-600" size={24} />
                <div>
                  <div className="text-xs font-semibold text-purple-600">MEILLEUR RAPPORT</div>
                  <div className="font-semibold">{s.nom}</div>
                  <div className="text-xs text-gray-600">
                    {typeof s.score_faisabilite === 'number'
                      ? `${((100 - s.score_faisabilite) / 1000).toFixed(2)}€ par %`
                      : 'N/A'}
                  </div>
                </div>
              </div>
            </Card>
          ))}

        {/* Scénario sélectionné */}
        {scenarioSelectionnéId && (
          <Card className="p-4 bg-orange-50 border-orange-200">
            <div className="flex items-center gap-3">
              <Check className="text-orange-600" size={24} />
              <div>
                <div className="text-xs font-semibold text-orange-600">SÉLECTIONNÉ</div>
                <div className="font-semibold">
                  {scenarios.find((s) => s.id === scenarioSelectionnéId)?.nom || 'N/A'}
                </div>
                <div className="text-xs text-gray-600">Prêt à éditer</div>
              </div>
            </div>
          </Card>
        )}
      </div>

      {/* Tableau comparatif */}
      <Card className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="bg-gray-50">
              <TableHead className="w-[180px] font-semibold">Scénario</TableHead>
              <TableHead className="text-right">Budget estimé</TableHead>
              <TableHead className="text-right">Durée</TableHead>
              <TableHead className="text-center">Faisabilité</TableHead>
              <TableHead className="text-center">Impact DPE</TableHead>
              <TableHead className="text-center">Actions</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {scenarios.map((scenario) => (
              <TableRow
                key={scenario.id}
                className={`transition-colors ${
                  scenarioSelectionnéId === scenario.id
                    ? 'bg-orange-50 hover:bg-orange-100'
                    : 'hover:bg-gray-50'
                }`}
              >
                {/* Nom du scénario */}
                <TableCell className="font-semibold">{scenario.nom}</TableCell>

                {/* Budget */}
                <TableCell className="text-right">
                  <div className="font-medium">
                    {formatBudget(scenario.budget_estime_min, scenario.budget_estime_max)}
                  </div>
                  <div className={`text-xs ${meilleurBudget === scenario.id ? 'text-green-600 font-semibold' : 'text-gray-500'}`}>
                    {meilleurBudget === scenario.id && '✓ Moins cher'}
                  </div>
                </TableCell>

                {/* Durée */}
                <TableCell className="text-right">
                  <div className="font-medium flex items-center justify-end gap-1">
                    <Clock size={14} className="text-gray-400" />
                    {formatDuree(scenario.duree_estimee_jours)}
                  </div>
                  <div className="text-xs text-gray-500">
                    {typeof scenario.duree_estimee_jours === 'number'
                      ? `~${Math.round(scenario.duree_estimee_jours)} jours`
                      : 'Durée non définie'}
                  </div>
                </TableCell>

                {/* Faisabilité */}
                <TableCell className="text-center">
                  <Badge
                    variant="outline"
                    className={`${getColorFaisabilite(scenario.score_faisabilite)}`}
                  >
                    {scenario.score_faisabilite}%
                  </Badge>
                  <div
                    className={`text-xs mt-1 ${
                      meilleurFaisabilite === scenario.id ? 'text-blue-600 font-semibold' : 'text-gray-500'
                    }`}
                  >
                    {meilleurFaisabilite === scenario.id && '✓ Plus faisable'}
                  </div>
                </TableCell>

                {/* Impact DPE */}
                <TableCell className="text-center">
                  <Badge
                    variant="outline"
                    className={getColorDPE(scenario.impact_dpe)}
                  >
                    {scenario.impact_dpe || 'N/A'}
                  </Badge>
                </TableCell>

                {/* Actions */}
                <TableCell className="text-center space-x-2">
                  {/* Détail pop-up */}
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setScenarioDetailId(scenario.id)}
                      >
                        Détail
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl">
                      <DialogHeader>
                        <DialogTitle>{scenario.nom}</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4">
                        {/* Données principales */}
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <label className="text-sm font-medium">Budget min.</label>
                            <div className="text-lg font-semibold">
                              {typeof scenario.budget_estime_min === 'number'
                                ? `${(scenario.budget_estime_min / 1000).toFixed(1)}k €`
                                : 'N/A'}
                            </div>
                          </div>
                          <div>
                            <label className="text-sm font-medium">Budget max.</label>
                            <div className="text-lg font-semibold">
                              {typeof scenario.budget_estime_max === 'number'
                                ? `${(scenario.budget_estime_max / 1000).toFixed(1)}k €`
                                : 'N/A'}
                            </div>
                          </div>
                          <div>
                            <label className="text-sm font-medium">Durée estimée</label>
                            <div className="text-lg font-semibold">{formatDuree(scenario.duree_estimee_jours)}</div>
                          </div>
                          <div>
                            <label className="text-sm font-medium">Faisabilité</label>
                            <div className="text-lg font-semibold">{scenario.score_faisabilite}%</div>
                          </div>
                        </div>

                        {/* Postes de travaux */}
                        {scenario.postes_travaux && scenario.postes_travaux.length > 0 && (
                          <div>
                            <label className="text-sm font-medium mb-2 block">Postes de travaux</label>
                            <div className="space-y-2">
                              {(scenario.postes_travaux as Array<{ poste?: string; budget_min?: number; budget_max?: number; duree_semaines?: number; priorite?: string; diy?: boolean }>).map((poste, idx) => (
                                <div key={idx} className="p-2 bg-gray-50 rounded text-sm">
                                  <div className="font-medium">{poste.poste}</div>
                                  <div className="text-xs text-gray-600">
                                    {poste.budget_min && poste.budget_max && (
                                      <>
                                        Budget : {(poste.budget_min / 1000).toFixed(1)}k -{' '}
                                        {(poste.budget_max / 1000).toFixed(1)}k €
                                      </>
                                    )}
                                  </div>
                                  {poste.diy && (
                                    <div className="text-xs text-blue-600 mt-1">
                                      💡 Possible en DIY
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Impact DPE */}
                        {scenario.impact_dpe && (
                          <div>
                            <label className="text-sm font-medium">Impact DPE</label>
                            <div className={`p-2 rounded ${getColorDPE(scenario.impact_dpe)}`}>
                              {scenario.impact_dpe}
                            </div>
                          </div>
                        )}

                        {/* Sélectionner ce scénario */}
                        {!readOnly && (
                          <Button
                            className="w-full"
                            onClick={() => {
                              onSelectScenario?.(scenario.id)
                            }}
                          >
                            Sélectionner ce scénario
                          </Button>
                        )}
                      </div>
                    </DialogContent>
                  </Dialog>

                  {/* Bouton sélectionner */}
                  {!readOnly && scenarioSelectionnéId !== scenario.id && (
                    <Button
                      size="sm"
                      onClick={() => onSelectScenario?.(scenario.id)}
                    >
                      Choisir
                    </Button>
                  )}

                  {scenarioSelectionnéId === scenario.id && (
                    <Badge className="bg-orange-100 text-orange-800">
                      ✓ Actif
                    </Badge>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {/* Résumé en bas */}
      <Card className="p-4 bg-blue-50 border-blue-200">
        <div className="text-sm space-y-2">
          <div className="font-semibold text-blue-900">💡 Conseils de décision</div>
          <ul className="text-xs text-blue-800 space-y-1">
            {meilleurBudget && scenarios.find((s) => s.id === meilleurBudget) && (
              <li>
                ✓ Pour réduire les dépenses : <strong>{scenarios.find((s) => s.id === meilleurBudget)?.nom}</strong>
              </li>
            )}
            {meilleurFaisabilite && scenarios.find((s) => s.id === meilleurFaisabilite) && (
              <li>
                ✓ Pour un projet réaliste : <strong>{scenarios.find((s) => s.id === meilleurFaisabilite)?.nom}</strong>
              </li>
            )}
            {meilleurRapport && scenarios.find((s) => s.id === meilleurRapport) && (
              <li>
                ✓ Meilleur équilibre : <strong>{scenarios.find((s) => s.id === meilleurRapport)?.nom}</strong>
              </li>
            )}
          </ul>
        </div>
      </Card>
    </div>
  )
}
