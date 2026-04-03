'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/composants/ui/card'
import { AlertCircle, Cloud, CloudRain, Sun, Utensils, Clock } from 'lucide-react'
import { utiliserRequete } from '@/crochets/utiliser-api'
import { obtenirPlanningAujourdhui, obtenirMeteo } from '@/bibliotheque/api/planning'
import { obtenirTachesJourMaison } from '@/bibliotheque/api/maison'

interface RepasTablette {
  id: number | string
  type: string
  nom: string
  heure?: string
}

interface TacheTablette {
  fait?: boolean
  titre: string
  categorie?: string
  priorite?: string
}

/**
 * E2 — Widget Tablette Google
 * Page optimisée pour affichage tablette (zoom large, touches grandes)
 * Affiche: repas du jour + tâche prioritaire + météo + minuteur
 */

export default function PageTablette() {
  const [heureActuelle, setHeureActuelle] = useState(new Date())
  const [minuteurActif, setMinuteurActif] = useState(false)
  const [secondesRestantes, setSecondesRestantes] = useState(0)

  // Requêtes parallèles
  const { data: planning, isLoading: loadingPlanning } = utiliserRequete(
    ['planning', 'aujourd-hui'],
    () => obtenirPlanningAujourdhui(),
    { staleTime: 5 * 60 * 1000 } // 5 min cache
  )

  const { data: meteo, isLoading: loadingMeteo } = utiliserRequete(
    ['meteo'],
    () => obtenirMeteo(),
    { staleTime: 30 * 60 * 1000 } // 30 min cache
  )

  const { data: taches, isLoading: loadingTaches } = utiliserRequete(
    ['taches', 'aujourd-hui'],
    () => obtenirTachesJourMaison(),
    { staleTime: 5 * 60 * 1000 }
  )

  // Mettre à jour l'heure chaque seconde
  useEffect(() => {
    const timer = setInterval(() => setHeureActuelle(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  // Gestion du minuteur
  useEffect(() => {
    if (!minuteurActif || secondesRestantes <= 0) return
    const countdown = setTimeout(() => setSecondesRestantes(s => s - 1), 1000)
    return () => clearTimeout(countdown)
  }, [minuteurActif, secondesRestantes])

  const formatterHeure = (date: Date) => date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
  const formatterMinuteur = (s: number) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`

  const iconeMeteo = () => {
    if (!meteo) return null
    const condition = meteo.condition?.toLowerCase()
    if (condition?.includes('pluie') || condition === 'rainy') return <CloudRain className="h-12 w-12 text-blue-500" />
    if (condition?.includes('nuage') || condition === 'cloudy') return <Cloud className="h-12 w-12 text-gray-500" />
    return <Sun className="h-12 w-12 text-yellow-500" />
  }

  const dateAujourdhui = new Date().toISOString().split('T')[0]
  const repasAujourdhui: RepasTablette[] = (planning?.repas as unknown as Record<string, RepasTablette[]> | undefined)?.[dateAujourdhui] || []
  const tachePrioritaire = (taches as TacheTablette[] | undefined)?.filter((t) => !t.fait)?.[0]

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted/50 p-4 md:p-6 lg:p-8 flex flex-col gap-4">
      {/* Heure actuelle — Grande affichage */}
      <div className="text-center py-4 md:py-6">
        <p className="text-6xl font-bold text-primary md:text-7xl">
          {formatterHeure(heureActuelle)}
        </p>
        <p className="text-xl text-muted-foreground mt-2 md:text-2xl">
          {heureActuelle.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })}
        </p>
      </div>

      {/* Grille optimisée tablette */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1 auto-rows-fr">
        {/* Repas du jour */}
        <Card className="h-full border-2 shadow-lg md:row-span-2">
          <CardHeader className="pb-2 sm:pb-3">
            <CardTitle className="flex items-center gap-3 text-xl sm:text-2xl">
              <Utensils className="h-8 w-8 sm:h-10 sm:w-10" />
              Repas
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {loadingPlanning ? (
              <p className="text-lg text-muted-foreground">Chargement...</p>
            ) : repasAujourdhui.length > 0 ? (
              repasAujourdhui.map((repas) => (
                <div key={repas.id} className="p-4 rounded-lg bg-primary/10 border border-primary/20">
                  <p className="text-sm font-semibold text-muted-foreground">{repas.type}</p>
                  <p className="text-xl sm:text-2xl font-bold mt-1">{repas.nom}</p>
                  {repas.heure && (
                    <p className="text-sm text-muted-foreground mt-1">{repas.heure}</p>
                  )}
                </div>
              ))
            ) : (
              <p className="text-lg text-muted-foreground text-center py-6">Aucun repas planifié</p>
            )}
          </CardContent>
        </Card>

        {/* Tâche prioritaire */}
        <Card className="h-full border-2 shadow-lg">
          <CardHeader className="pb-2 sm:pb-3">
            <CardTitle className="text-xl sm:text-2xl flex items-center gap-2">
              <AlertCircle className="h-8 w-8 sm:h-10 sm:w-10" />
              À faire
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col justify-center">
            {loadingTaches ? (
              <p className="text-lg text-muted-foreground">Chargement...</p>
            ) : tachePrioritaire ? (
              <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/20">
                <p className="text-xl sm:text-2xl font-bold text-destructive">
                  {tachePrioritaire.titre}
                </p>
                {tachePrioritaire.categorie && (
                  <p className="text-sm text-muted-foreground mt-2">{tachePrioritaire.categorie}</p>
                )}
                {tachePrioritaire.priorite && (
                  <div className="mt-3 inline-block px-3 py-1 rounded-full bg-destructive/20 text-sm font-semibold">
                    Priorité: {tachePrioritaire.priorite}
                  </div>
                )}
              </div>
            ) : (
              <p className="text-lg text-muted-foreground text-center py-6">✓ Tout est fait!</p>
            )}
          </CardContent>
        </Card>

        {/* Météo */}
        <Card className="h-full border-2 shadow-lg">
          <CardHeader className="pb-2 sm:pb-3">
            <CardTitle className="text-xl sm:text-2xl">Météo</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center">
            {loadingMeteo ? (
              <p className="text-lg text-muted-foreground">Chargement...</p>
            ) : meteo ? (
              <div className="text-center space-y-3">
                <div>{iconeMeteo()}</div>
                <p className="text-3xl sm:text-4xl font-bold">{meteo.temperature}°C</p>
                <p className="text-lg text-muted-foreground">{meteo.condition}</p>
                {meteo.humidity && <p className="text-sm text-muted-foreground">Humidité: {meteo.humidity}%</p>}
              </div>
            ) : (
              <p className="text-lg text-muted-foreground">Données non disponibles</p>
            )}
          </CardContent>
        </Card>

        {/* Minuteur */}
        <Card className="h-full border-2 shadow-lg md:row-span-2">
          <CardHeader className="pb-2 sm:pb-3">
            <CardTitle className="text-xl sm:text-2xl flex items-center gap-3">
              <Clock className="h-8 w-8 sm:h-10 sm:w-10" />
              Minuteur
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center space-y-4">
            <input
              type="number"
              min="1"
              max="3600"
              value={secondesRestantes === 0 ? '' : Math.floor(secondesRestantes / 60)}
              onChange={(e) => setSecondesRestantes(parseInt(e.target.value || '0') * 60)}
              disabled={minuteurActif}
              placeholder="Minutes"
              className="w-full text-center text-2xl sm:text-3xl rounded-lg border-2 border-primary p-4 font-bold min-h-14"
            />
            <p className="text-4xl sm:text-5xl font-bold text-primary">
              {formatterMinuteur(secondesRestantes)}
            </p>
            <button
              onClick={() => setMinuteurActif(!minuteurActif)}
              className={`w-full px-6 py-4 rounded-lg text-lg font-bold transition min-h-14 ${
                minuteurActif
                  ? 'bg-destructive text-white hover:bg-destructive/90'
                  : 'bg-primary text-white hover:bg-primary/90'
              }`}
            >
              {minuteurActif ? 'Pause' : 'Démarrer'}
            </button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
