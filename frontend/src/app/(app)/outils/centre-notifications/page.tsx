'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { Badge } from '@/composants/ui/badge'
import { Bell, Check } from 'lucide-react'
import { clientApi } from '@/bibliotheque/api/client'
import { toast } from 'sonner'

/**
 * Page Centre de notifications (E.5)
 * 
 * Affiche l'historique des notifications avec:
 * - Pagination
 * - Filtres (non-lu seulement)
 * - Actions (marquer comme lu, supprimer)
 * - Stats (nombre non-lu, par canal, par categorie)
 */

interface Notification {
  id: number
  canal: string
  titre: string
  message: string
  type_evenement?: string
  categorie: string
  lu: boolean
  timestamp: string
}

export default function CentreNotificationsPage() {
  const [page, setPage] = useState(1)
  const [nonLuSeulement, setNonLuSeulement] = useState(false)
  const [selectedNotif, setSelectedNotif] = useState<number | null>(null)

  // Recuperer l'historique
  const { data: historique, isLoading, refetch } = useQuery({
    queryKey: ['notifications', page, nonLuSeulement],
    queryFn: async () => {
      const response = await clientApi.get('/api/v1/notifications/historique', {
        params: {
          page: page,
          page_size: 20,
          non_lu_seulement: nonLuSeulement,
        },
      })
      return response.data
    },
  })

  // Recuperer les stats
  const { data: stats } = useQuery({
    queryKey: ['notifications-stats'],
    queryFn: async () => {
      const response = await clientApi.get('/api/v1/notifications/historique/stats')
      return response.data
    },
  })

  // Marquer comme lu
  const handleMarkAsRead = async (notifId: number) => {
    try {
      await clientApi.post(`/api/v1/notifications/historique/${notifId}/marquer-lu`)
      refetch()
    } catch (error) {
      toast.error('Erreur lors du marquage de la notification')
    }
  }

  // Marquer tous comme lu
  const handleMarkAllAsRead = async () => {
    try {
      await clientApi.post('/api/v1/notifications/historique/marquer-tous-lus')
      refetch()
    } catch (error) {
      toast.error('Erreur lors du marquage des notifications')
    }
  }

  const canalColors: Record<string, string> = {
    push: 'bg-blue-100 text-blue-800',
    email: 'bg-purple-100 text-purple-800',
    ntfy: 'bg-green-100 text-green-800',
    telegram: 'bg-cyan-100 text-cyan-800',
    whatsapp: 'bg-cyan-100 text-cyan-800',
  }

  const categorieIcons: Record<string, string> = {
    rappels: 'R',
    alertes: '!',
    resumes: 'S',
    autres: 'i',
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Centre de Notifications</h1>
          <p className="text-muted-foreground mt-2">
            Historique centralise de toutes vos notifications (E.5)
          </p>
        </div>
        {stats && (
          <div className="text-right">
            <div className="text-3xl font-bold text-red-600">{stats.non_lu || 0}</div>
            <p className="text-sm text-muted-foreground">non-lues</p>
          </div>
        )}
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Total notifications</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Par canal</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1 text-sm">
              {Object.entries(stats.par_canal || {}).map(([canal, count]) => (
                <div key={canal} className="flex justify-between">
                  <span className="capitalize">{canal}</span>
                  <span className="font-semibold">{String(count)}</span>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Par categorie</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1 text-sm">
              {Object.entries(stats.par_categorie || {}).map(([cat, count]) => (
                <div key={cat} className="flex justify-between">
                  <span className="capitalize">{cat}</span>
                  <span className="font-semibold">{String(count)}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Controles */}
      <div className="flex items-center gap-4">
        <div className="flex gap-2">
          <Button
            variant={nonLuSeulement ? 'default' : 'outline'}
            onClick={() => {
              setNonLuSeulement(!nonLuSeulement)
              setPage(1)
            }}
          >
            {nonLuSeulement ? 'Toutes' : 'Non-lues uniquement'}
          </Button>
          {stats && stats.non_lu > 0 && (
            <Button variant="ghost" onClick={handleMarkAllAsRead}>
              <Check className="w-4 h-4 mr-2" />
              Marquer tous comme lus
            </Button>
          )}
        </div>
      </div>

      {/* Liste Notifications */}
      <div className="space-y-2">
        {isLoading ? (
          <div className="text-center py-8 text-muted-foreground">Chargement...</div>
        ) : historique?.data?.length === 0 ? (
          <Card className="text-center py-8">
            <Bell className="w-12 h-12 mx-auto text-muted-foreground/50 mb-4" />
            <p className="text-muted-foreground">Aucune notification trouvee</p>
          </Card>
        ) : (
          historique?.data?.map((notif: Notification) => (
            <Card
              key={notif.id}
              className={`cursor-pointer transition ${notif.lu ? 'opacity-60' : 'border-blue-200 bg-blue-50/20'}`}
              onClick={() => setSelectedNotif(notif.id)}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-lg">{categorieIcons[notif.categorie] || 'i'}</span>
                      <h3 className="font-semibold">{notif.titre}</h3>
                      <Badge
                        variant="outline"
                        className={canalColors[notif.canal] || 'bg-gray-100'}
                      >
                        {notif.canal}
                      </Badge>
                      {!notif.lu && (
                        <Badge variant="default" className="bg-blue-600">
                          Non-lu
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{notif.message}</p>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>{new Date(notif.timestamp).toLocaleString('fr-FR')}</span>
                      {notif.type_evenement && <span>{notif.type_evenement}</span>}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 ml-4">
                    {!notif.lu && (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleMarkAsRead(notif.id)
                        }}
                      >
                        <Check className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Pagination */}
      {historique && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            Page {page} - {historique.data?.length} notification(s)
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
            >
              Precedent
            </Button>
            <Button
              variant="outline"
              onClick={() => setPage(page + 1)}
              disabled={!historique.data || historique.data.length < 20}
            >
              Suivant
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
