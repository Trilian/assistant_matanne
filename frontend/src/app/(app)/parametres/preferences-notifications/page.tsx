'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { Switch } from '@/composants/ui/switch'
import { Label } from '@/composants/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/composants/ui/select'
import { CheckCircle2, AlertCircle } from 'lucide-react'
import { clientApi } from '@/bibliotheque/api/client'
import { toast } from 'sonner'

/**
 * Page
 Preferences Notifications (E.4)
 * 
 * Configure:
 * - Canal prefere (push, email, ntfy, whatsapp)
 * - Canaux par categorie (rappels, alertes, resumes)
 * - Heures silencieuses
 * - Max notifs/heure
 */

interface PreferencesFormData {
  canal_prefere: string
  canaux_par_categorie: {
    rappels: string[]
    alertes: string[]
    resumes: string[]
  }
  quiet_hours: {
    debut: string
    fin: string
  }
}

type CategorieNotification = keyof PreferencesFormData['canaux_par_categorie']

const canaux = [
  { id: 'push', label: 'Push', description: 'Notifications navigateur' },
  { id: 'email', label: 'Email', description: 'Emails' },
  { id: 'ntfy', label: 'Ntfy', description: 'Notifications ntfy.sh' },
  { id: 'whatsapp', label: 'WhatsApp', description: 'Messages WhatsApp' },
]

const categories: Array<{ id: CategorieNotification; label: string; description: string }> = [
  { id: 'rappels', label: 'Rappels', description: 'Rappels activites, courses, etc.' },
  { id: 'alertes', label: 'Alertes', description: 'Alertes peremption, stock, etc.' },
  { id: 'resumes', label: 'Resumes', description: 'Resumes hebdo, digests, etc.' },
]

export default function PreferencesNotificationsPage() {
  const [isEditing, setIsEditing] = useState(false)

  // Recuperer les preferences actuelles
  const { data: currentPrefs, isLoading } = useQuery({
    queryKey: ['notification-preferences'],
    queryFn: async () => {
      const response = await clientApi.get('/api/v1/notifications/preferences')
      return response.data
    },
  })

  // Mutation pour sauvegarder
  const saveMutation = useMutation({
    mutationFn: async (data: PreferencesFormData) => {
      const response = await clientApi.put('/api/v1/notifications/preferences', data)
      return response.data
    },
    onSuccess: () => {
      toast.success('Preferences mises a jour', {
        description: 'Vos preferences de notifications ont ete sauvegardees.',
      })
      setIsEditing(false)
    },
    onError: () => {
      toast.error('Erreur', {
        description: 'Impossible de sauvegarder les preferences.',
      })
    },
  })

  const { register, watch, handleSubmit, reset } = useForm<PreferencesFormData>({
    defaultValues: currentPrefs || {
      canal_prefere: 'push',
      canaux_par_categorie: {
        rappels: ['push', 'ntfy'],
        alertes: ['push', 'ntfy', 'email'],
        resumes: ['email'],
      },
    },
  })

  const onSubmit = async (data: PreferencesFormData) => {
    await saveMutation.mutateAsync(data)
  }

  if (isLoading) {
    return <div className="p-6 text-center text-muted-foreground">Chargement...</div>
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Preferences Notifications</h1>
        <p className="text-muted-foreground mt-2">
          Configurez comment et ou recevoir vos notifications (E.4)
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Canal prefere */}
        <Card>
          <CardHeader>
            <CardTitle>Canal prefere</CardTitle>
            <CardDescription>Choisissez votre canal de notification par defaut</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {canaux.map((canal) => (
                <label
                  key={canal.id}
                  className="flex flex-col gap-2 p-4 border rounded-lg cursor-pointer hover:bg-muted transition"
                >
                  <input
                    type="radio"
                    value={canal.id}
                    {...register('canal_prefere')}
                    className="w-4 h-4"
                  />
                  <span className="font-semibold">{canal.label}</span>
                  <span className="text-xs text-muted-foreground">{canal.description}</span>
                </label>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Canaux par categorie */}
        <Card>
          <CardHeader>
            <CardTitle>Canaux par categorie</CardTitle>
            <CardDescription>Selectionnez les canaux pour chaque type de notification</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {categories.map((cat) => (
              <div key={cat.id}>
                <Label className="text-base font-semibold mb-3 block">{cat.label}</Label>
                <p className="text-sm text-muted-foreground mb-3">{cat.description}</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {canaux.map((canal) => (
                    <label key={canal.id} className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="checkbox"
                        value={canal.id}
                        {...register(`canaux_par_categorie.${cat.id}` as const)}
                        className="w-4 h-4"
                      />
                      <span className="text-sm">{canal.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Heures silencieuses */}
        <Card>
          <CardHeader>
            <CardTitle>Heures silencieuses</CardTitle>
            <CardDescription>
              Pas de notifications non urgentes pendant ces heures (generalement 22h a 7h)
            </CardDescription>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="quiet_debut">Debut</Label>
              <input
                id="quiet_debut"
                type="time"
                {...register('quiet_hours.debut')}
                className="mt-2 w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <Label htmlFor="quiet_fin">Fin</Label>
              <input
                id="quiet_fin"
                type="time"
                {...register('quiet_hours.fin')}
                className="mt-2 w-full px-3 py-2 border rounded-lg"
              />
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex gap-3">
          <Button
            type="submit"
            disabled={saveMutation.isPending}
            className="gap-2"
          >
            <CheckCircle2 className="w-4 h-4" />
            {saveMutation.isPending ? 'Sauvegarde...' : 'Sauvegarder'}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => reset()}
          >
            Annuler
          </Button>
        </div>
      </form>

      {/* Info */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex gap-3">
            <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0" />
            <div className="space-y-2 text-sm">
              <p className="font-semibold text-blue-900">Conseil</p>
              <ul className="space-y-1 text-blue-800 list-disc list-inside">
                <li>Les alertes critiques sont toujours envoyees en priorite</li>
                <li>Les canaux multiples creent une cascade de fallback</li>
                <li>WhatsApp pour les notifications temps reel (courses, Jules, resultats)</li>
                <li>Email pour les resumes et rapports importants</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
