'use client'

import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import {
  obtenirSimulation,
  listerScenarios,
  comparerScenarios,
  modifierSimulation,
} from '@/bibliotheque/api/maison'
import { ComparateurScenarios } from '@/composants/maison/comparateur-scenarios'
import { Button } from '@/composants/ui/button'
import { Card } from '@/composants/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/composants/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/composants/ui/select'
import { ArrowLeft, Download } from 'lucide-react'

type StatutSimulation = 'brouillon' | 'en_cours' | 'termine' | 'archive'

/**
 * Page détail d'une simulation
 * Affiche le comparateur de scénarios et permet de sélectionner celui à éditer
 */
export default function SimulationDetailPage() {
  const params = useParams()
  const simulationId = parseInt(params.id as string)
  const queryClient = useQueryClient()
  const [scenarioSelectionne, setScenarioSelectionne] = useState<number | null>(null)

  // Récupérer la simulation
  const { data: simulation, isLoading, error } = useQuery({
    queryKey: ['simulation', simulationId],
    queryFn: () => obtenirSimulation(simulationId),
    staleTime: 1000 * 60 * 5,
  })

  // Récupérer les scénarios
  const { data: scenarios = [], isLoading: isLoadingScenarios } = useQuery({
    queryKey: ['scenarios', simulationId],
    queryFn: () => listerScenarios(simulationId),
    enabled: !!simulation,
    staleTime: 1000 * 60 * 5,
  })

  // Récupérer la comparaison
  const { data: comparaison } = useQuery({
    queryKey: ['comparaison', simulationId],
    queryFn: () => comparerScenarios(simulationId),
    enabled: scenarios.length > 0,
  })

  // Mettre à jour le statut
  const { mutate: updateStatut } = useMutation({
    mutationFn: (newStatut: StatutSimulation) =>
      modifierSimulation(simulationId, { statut: newStatut }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['simulation', simulationId] })
    },
  })

  if (isLoading) {
    return <div className="p-8 text-center">Chargement...</div>
  }

  if (error || !simulation) {
    return (
      <div className="p-8 space-y-4">
        <div className="text-red-600 font-semibold">Erreur lors du chargement</div>
        <Link href="/maison/simulation">
          <Button variant="outline">
            <ArrowLeft size={16} className="mr-2" />
            Retour
          </Button>
        </Link>
      </div>
    )
  }

  const getStatutBadgeColor = (statut: string) => {
    const colors: Record<string, string> = {
      brouillon: 'bg-gray-100 text-gray-800',
      en_cours: 'bg-blue-100 text-blue-800',
      termine: 'bg-green-100 text-green-800',
      archive: 'bg-gray-400 text-white',
    }
    return colors[statut] || 'bg-gray-100'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/maison/simulation">
            <Button variant="ghost" size="icon">
              <ArrowLeft size={20} />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">{simulation.nom}</h1>
            <p className="text-gray-600">{simulation.type_projet}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className={`text-xs px-3 py-1 rounded-full font-medium ${getStatutBadgeColor(simulation.statut)}`}>
            {simulation.statut.replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="scenar" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="scenar">Scénarios</TabsTrigger>
          <TabsTrigger value="plans">Plans</TabsTrigger>
          <TabsTrigger value="params">Paramètres</TabsTrigger>
        </TabsList>

        {/* ─── ONGLET SCÉNARIOS ─────────────────────────────────── */}
        <TabsContent value="scenar" className="space-y-4">
          {isLoadingScenarios ? (
            <Card className="p-8 text-center text-gray-500">Chargement des scénarios...</Card>
          ) : scenarios.length === 0 ? (
            <Card className="p-8 text-center">
              <p className="text-gray-600 mb-4">Aucun scénario créé pour cette simulation</p>
              <Link href={`/maison/simulation/${simulationId}/new-scenario`}>
                <Button>Créer le premier scénario</Button>
              </Link>
            </Card>
          ) : (
            <ComparateurScenarios
              scenarios={scenarios}
              comparaison={comparaison}
                scenarioSelectionnéId={scenarioSelectionne ?? undefined}
              onSelectScenario={(id) => {
                setScenarioSelectionne(id)
                // Rediriger vers l'édition du plan du scénario
                const scenario = scenarios.find((s) => s.id === id)
                if (scenario?.plan_apres_id) {
                  // TODO: Ouvrir l'éditeur pour ce plan
                }
              }}
            />
          )}

          {/* Bouton créer scénario */}
          <div className="flex justify-center">
            <Link href={`/maison/simulation/${simulationId}/new-scenario`}>
              <Button size="lg" variant="default">
                ➕ Ajouter un scénario
              </Button>
            </Link>
          </div>
        </TabsContent>

        {/* ─── ONGLET PLANS ────────────────────────────────────── */}
        <TabsContent value="plans" className="space-y-4">
          <Card className="p-8 text-center text-gray-500">
            <p>Plans associés à cette simulation</p>
            {scenarios.length > 0 && (
              <div className="mt-4 text-sm">
                <p className="mb-2">Cliquez sur un scénario pour éditer ses plans</p>
                <p className="text-xs text-gray-400">
                  Chaque scénario dispose d'un plan "avant" et d'un plan "après" rénovation
                </p>
              </div>
            )}
          </Card>
        </TabsContent>

        {/* ─── ONGLET PARAMÈTRES ───────────────────────────────── */}
        <TabsContent value="params" className="space-y-4">
          <Card className="p-6">
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Statut</label>
                <Select
                  value={simulation.statut}
                  onValueChange={(val) => updateStatut(val as StatutSimulation)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="brouillon">Brouillon</SelectItem>
                    <SelectItem value="en_cours">En cours</SelectItem>
                    <SelectItem value="termine">Terminé</SelectItem>
                    <SelectItem value="archive">Archivé</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium">Pièces concernées</label>
                <div className="text-sm text-gray-600 mt-2">
                  {Array.isArray(simulation.pieces_concernees)
                    ? simulation.pieces_concernees.join(', ')
                    : simulation.pieces_concernees || 'À définir'}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Données</label>
                <div className="space-y-2 text-sm text-gray-600">
                  <div>
                    Créée le{' '}
                    {simulation.created_at
                      ? new Date(simulation.created_at).toLocaleDateString('fr-FR')
                      : 'N/A'}
                  </div>
                  <div>
                    Modifiée le{' '}
                    {simulation.updated_at
                      ? new Date(simulation.updated_at).toLocaleDateString('fr-FR')
                      : 'N/A'}
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Actions en bas */}
      <div className="flex gap-3 justify-between">
        <Link href="/maison/simulation">
          <Button variant="outline">Retour</Button>
        </Link>
        <div className="flex gap-3">
          <Button variant="outline">
            <Download size={16} className="mr-2" />
            Exporter
          </Button>
        </div>
      </div>
    </div>
  )
}
