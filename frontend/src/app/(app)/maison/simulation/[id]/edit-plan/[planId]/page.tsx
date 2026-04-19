'use client'

import React, { useState, useCallback, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import { obtenirPlan, modifierPlan } from '@/bibliotheque/api/maison'
import { EditeurPlan2D } from '@/composants/maison/editeur-plan-2d'
import { CatalogueMeubles } from '@/composants/maison/catalogue-meubles'
import { Button, Card, Dialog, DialogContent, DialogHeader, DialogTitle, Input } from '@/composants/ui'
import { ArrowLeft, Save, RotateCcw, ZoomIn, ZoomOut } from 'lucide-react'
import Link from 'next/link'

/**
 * Page d'édition d'un plan 2D
 * Layout: Catalogue meubles à gauche | Éditeur 2D au centre
 */
export default function EditPlanPage() {
  const params = useParams()
  const router = useRouter()
  const planId = parseInt(params.planId as string)
  const simulationId = parseInt(params.id as string)
  const queryClient = useQueryClient()
  
  const [isPropsOpen, setIsPropsOpen] = useState(false)
  const [planName, setPlanName] = useState('')

  // Charger le plan
  const { data: plan, isLoading, error } = useQuery({
    queryKey: ['plan', planId],
    queryFn: () => obtenirPlan(planId),
    enabled: !!planId,
  })

  // Sauvegarder les modifications du plan
  const { mutate: savePlan } = useMutation({
    mutationFn: (data: any) => modifierPlan(planId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plan', planId] })
    },
  })

  useEffect(() => {
    if (plan) {
      setPlanName(plan.nom)
    }
  }, [plan])

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen">Chargement du plan...</div>
  }

  if (error || !plan) {
    return (
      <div className="p-8 space-y-4">
        <div className="text-red-600 font-semibold">Erreur lors du chargement du plan</div>
        <Link href={`/maison/simulation/${simulationId}`}>
          <Button>Retour</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      {/* Header */}
      <div className="bg-white border-b p-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href={`/maison/simulation/${simulationId}`}>
            <Button variant="ghost" size="icon">
              <ArrowLeft size={20} />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">{plan.nom}</h1>
            <p className="text-sm text-gray-600">Version {plan.version}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsPropsOpen(true)}
          >
            📋 Propriétés du plan
          </Button>
          <Button size="sm" disabled className="text-xs">
            {plan.largeur_canvas}×{plan.hauteur_canvas}px
          </Button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Catalogue meubles - Sidebar gauche */}
        <div className="w-72 border-r bg-white overflow-hidden flex flex-col">
          <CatalogueMeubles readOnly={false} />
        </div>

        {/* Éditeur 2D - Centre */}
        <div className="flex-1 overflow-auto">
          <div className="p-6">
            <EditeurPlan2D
              planId={planId}
              readOnly={false}
              onSave={(donnees) => {
                console.log('Plan sauvegardé:', donnees)
              }}
            />
          </div>
        </div>
      </div>

      {/* Dialog Propriétés */}
      <Dialog open={isPropsOpen} onOpenChange={setIsPropsOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Propriétés du plan</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Nom du plan</label>
              <Input
                value={planName}
                onChange={(e) => setPlanName(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Largeur (px)</label>
                <div className="p-2 bg-gray-50 rounded text-sm">{plan.largeur_canvas}</div>
              </div>
              <div>
                <label className="text-sm font-medium">Hauteur (px)</label>
                <div className="p-2 bg-gray-50 rounded text-sm">{plan.hauteur_canvas}</div>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium">Échelle</label>
              <div className="p-2 bg-gray-50 rounded text-sm">
                {plan.echelle_px_par_m} px = 1m
              </div>
            </div>
            <div>
              <label className="text-sm font-medium">Type de plan</label>
              <div className="p-2 bg-gray-50 rounded text-sm">{plan.type_plan}</div>
            </div>
            <Button
              onClick={() => {
                savePlan({ nom: planName })
                setIsPropsOpen(false)
              }}
              className="w-full"
            >
              <Save size={16} className="mr-2" />
              Sauvegarder
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
