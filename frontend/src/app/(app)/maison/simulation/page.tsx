'use client'

import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Link from 'next/link'
import {
  listerSimulations,
  creerSimulation,
  supprimerSimulation,
  dupliquerSimulation,
} from '@/bibliotheque/api/maison'
import { SimulationRenovation } from '@/types/maison'
import {
  Button,
  Card,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogTitle,
} from '@/composants/ui'
import { Plus, Edit, Copy, Trash2, Eye, ChevronRight, Filter } from 'lucide-react'

/**
 * Page liste des simulations de rénovation
 * Affiche toutes les simulations avec possibilité de créer, dupliquer, supprimer
 */
export default function SimulationListPage() {
  const queryClient = useQueryClient()
  const [filtre, setFiltre] = useState<string>('')
  const [statut, setStatut] = useState<string>('')
  const [page, setPage] = useState(1)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [nomNouvelle, setNomNouvelle] = useState('')
  const [typeProjet, setTypeProjet] = useState('libre')
  const [simulationASupprimer, setSimulationASupprimer] = useState<number | null>(null)

  // Récupérer les simulations
  const { data, isLoading, error } = useQuery({
    queryKey: ['simulations', page, statut],
    queryFn: () => listerSimulations(page, statut || undefined),
    staleTime: 1000 * 60 * 5, // 5 minutes
  })

  // Créer une simulation
  const { mutate: creer, isPending: isCreating } = useMutation({
    mutationFn: (data: any) => creerSimulation(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['simulations'] })
      setIsDialogOpen(false)
      setNomNouvelle('')
      setTypeProjet('libre')
    },
  })

  // Dupliquer une simulation
  const { mutate: dupliquer } = useMutation({
    mutationFn: (id: number) => dupliquerSimulation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['simulations'] })
    },
  })

  // Supprimer une simulation
  const { mutate: supprimer } = useMutation({
    mutationFn: (id: number) => supprimerSimulation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['simulations'] })
      setSimulationASupprimer(null)
    },
  })

  const handleCreer = () => {
    if (!nomNouvelle.trim()) return
    creer({
      nom: nomNouvelle,
      type_projet: typeProjet,
      pieces_concernees: [],
    })
  }

  const getStatutBadge = (statut: string) => {
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
        <div>
          <h1 className="text-3xl font-bold">Simulations Rénovation</h1>
          <p className="text-gray-600 mt-1">Créez et gérez vos projets de rénovation</p>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button size="lg">
              <Plus size={16} className="mr-2" />
              Nouvelle simulation
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Créer une simulation</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Nom du projet</label>
                <Input
                  placeholder="Ex: Rénovation cuisine"
                  value={nomNouvelle}
                  onChange={(e) => setNomNouvelle(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium">Type de projet</label>
                <Select value={typeProjet} onValueChange={setTypeProjet}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="libre">Libre</SelectItem>
                    <SelectItem value="cuisine">Cuisine</SelectItem>
                    <SelectItem value="salle_bain">Salle de bain</SelectItem>
                    <SelectItem value="chambre">Chambre</SelectItem>
                    <SelectItem value="sejour">Séjour</SelectItem>
                    <SelectItem value="etage">Étage complet</SelectItem>
                    <SelectItem value="maison">Maison entière</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={handleCreer}
                disabled={isCreating || !nomNouvelle.trim()}
                className="w-full"
              >
                {isCreating ? 'Création...' : 'Créer'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filtres */}
      <Card className="p-4">
        <div className="flex items-center gap-4">
          <Filter size={16} className="text-gray-400" />
          <div className="flex-1">
            <Input
              placeholder="Chercher une simulation..."
              value={filtre}
              onChange={(e) => setFiltre(e.target.value)}
            />
          </div>
          <Select value={statut} onValueChange={setStatut}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Tous les statuts" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">Tous les statuts</SelectItem>
              <SelectItem value="brouillon">Brouillon</SelectItem>
              <SelectItem value="en_cours">En cours</SelectItem>
              <SelectItem value="termine">Terminé</SelectItem>
              <SelectItem value="archive">Archivé</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </Card>

      {/* Liste */}
      {isLoading ? (
        <Card className="p-8 text-center text-gray-500">Chargement...</Card>
      ) : error ? (
        <Card className="p-8 text-center text-red-600">Erreur lors du chargement</Card>
      ) : !data?.items || data.items.length === 0 ? (
        <Card className="p-12 text-center">
          <div className="text-gray-400 mb-4 text-6xl">🏗️</div>
          <h3 className="font-semibold text-gray-700 mb-2">Aucune simulation</h3>
          <p className="text-gray-500 mb-4">Créez votre premier projet de rénovation</p>
          <Button onClick={() => setIsDialogOpen(true)}>
            <Plus size={16} className="mr-2" />
            Créer une simulation
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.items
            .filter((sim) =>
              nomNouvelle.trim() === ''
                ? true
                : sim.nom.toLowerCase().includes(nomNouvelle.toLowerCase())
            )
            .map((simulation) => (
              <Card
                key={simulation.id}
                className="p-6 hover:shadow-lg transition-shadow flex flex-col justify-between"
              >
                {/* Header */}
                <div className="mb-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-lg">{simulation.nom}</h3>
                    <span className={`text-xs px-2 py-1 rounded font-medium ${getStatutBadge(simulation.statut)}`}>
                      {simulation.statut.replace('_', ' ')}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{simulation.type_projet}</p>
                </div>

                {/* Body */}
                <div className="space-y-2 text-sm mb-4">
                  {simulation.scenarios_count !== undefined && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Scénarios</span>
                      <span className="font-semibold">{simulation.scenarios_count}</span>
                    </div>
                  )}
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Créée le</span>
                    <span className="text-xs">
                      {new Date(simulation.cree_le).toLocaleDateString('fr-FR')}
                    </span>
                  </div>
                </div>

                {/* Footer Actions */}
                <div className="flex gap-2">
                  <Link href={`/maison/simulation/${simulation.id}`} className="flex-1">
                    <Button variant="default" size="sm" className="w-full">
                      <Eye size={14} className="mr-1" />
                      Voir
                    </Button>
                  </Link>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => dupliquer(simulation.id)}
                    title="Dupliquer cette simulation"
                  >
                    <Copy size={14} />
                  </Button>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSimulationASupprimer(simulation.id)}
                    title="Supprimer"
                  >
                    <Trash2 size={14} className="text-red-500" />
                  </Button>
                </div>
              </Card>
            ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.total > 20 && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">
            {data.items.length} sur {data.total}
          </span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              disabled={page === 1}
              onClick={() => setPage(Math.max(1, page - 1))}
            >
              Précédent
            </Button>
            <Button
              variant="outline"
              disabled={!data.items || data.items.length < 20}
              onClick={() => setPage(page + 1)}
            >
              Suivant
            </Button>
          </div>
        </div>
      )}

      {/* Dialog suppression */}
      <AlertDialog open={!!simulationASupprimer} onOpenChange={(open) => !open && setSimulationASupprimer(null)}>
        <AlertDialogContent>
          <AlertDialogTitle>Supprimer la simulation ?</AlertDialogTitle>
          <AlertDialogDescription>
            Cette action est irréversible. Toutes les données de cette simulation seront supprimées.
          </AlertDialogDescription>
          <div className="flex gap-3 justify-end">
            <AlertDialogCancel>Annuler</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => simulationASupprimer && supprimer(simulationASupprimer)}
              className="bg-red-600 hover:bg-red-700"
            >
              Supprimer
            </AlertDialogAction>
          </div>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
