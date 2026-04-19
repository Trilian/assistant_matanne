'use client'

import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import {
  listerZonesTerrain,
  creerZoneTerrain,
  modifierZoneTerrain,
  supprimerZoneTerrain,
} from '@/bibliotheque/api/maison'
import { ZoneTerrain as ZoneTerrainType } from '@/types/maison'
import { Button } from '@/composants/ui/button'
import { Card } from '@/composants/ui/card'
import { Input } from '@/composants/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/composants/ui/select'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/composants/ui/dialog'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogTitle,
} from '@/composants/ui/alert-dialog'
import { Plus, Edit, Trash2, ArrowLeft, Map } from 'lucide-react'
import Link from 'next/link'

/**
 * Page de gestion du terrain et ses zones
 * Permet de définir les zones du terrain (potager, bassin, terrasse, etc.)
 */
export default function TerrainPage() {
  const params = useParams()
  const simulationId = parseInt(params.id as string)
  const queryClient = useQueryClient()
  
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [zoneAEditer, setZoneAEditer] = useState<ZoneTerrainType | null>(null)
  const [zoneASupprimer, setZoneASupprimer] = useState<number | null>(null)
  
  // Form state
  const [nom, setNom] = useState('')
  const [type, setType] = useState('autre')
  const [surface, setSurface] = useState('')
  const [altitude, setAltitude] = useState('')
  const [pente, setPente] = useState('')
  const [exposition, setExposition] = useState('aucune')
  const [etat, setEtat] = useState('bon')
  const [liaisJardin, setLiaisJardin] = useState(false)

  // Charger les zones
  const { data: zones = [], isLoading } = useQuery({
    queryKey: ['zones-terrain', simulationId],
    queryFn: () => listerZonesTerrain(1),
    staleTime: 1000 * 60 * 5,
  })

  const zonesListe = Array.isArray(zones) ? zones : zones.items ?? []

  // Créer une zone
  const { mutate: creer, isPending: isCreating } = useMutation({
    mutationFn: (data: any) => creerZoneTerrain(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['zones-terrain'] })
      resetForm()
      setIsDialogOpen(false)
    },
  })

  // Modifier une zone
  const { mutate: modifier, isPending: isModifying } = useMutation({
    mutationFn: (data: any) => modifierZoneTerrain(zoneAEditer!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['zones-terrain'] })
      resetForm()
      setIsDialogOpen(false)
    },
  })

  // Supprimer une zone
  const { mutate: supprimer } = useMutation({
    mutationFn: (id: number) => supprimerZoneTerrain(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['zones-terrain'] })
      setZoneASupprimer(null)
    },
  })

  const resetForm = () => {
    setNom('')
    setType('autre')
    setSurface('')
    setAltitude('')
    setPente('')
    setExposition('aucune')
    setEtat('bon')
    setLiaisJardin(false)
    setZoneAEditer(null)
  }

  const handleSave = () => {
    if (!nom.trim()) return

    const data = {
      nom,
      type_zone: type,
      surface_m2: surface ? parseFloat(surface) : 0,
      altitude_min: altitude ? parseInt(altitude.split('-')[0]) : 0,
      altitude_max: altitude ? parseInt(altitude.split('-')[1]) : 0,
      pente_pct: pente ? parseFloat(pente) : 0,
      exposition,
      etat,
      lien_jardin: liaisJardin,
      geometrie: [],
    }

    if (zoneAEditer) {
      modifier(data)
    } else {
      creer(data)
    }
  }

  const handleEditer = (zone: ZoneTerrainType) => {
    setZoneAEditer(zone)
    setNom(zone.nom)
    setType(zone.type_zone)
    setSurface(zone.surface_m2?.toString() || '')
    setAltitude(`${zone.altitude_min || 0}-${zone.altitude_max || 0}`)
    setPente(zone.pente_pct?.toString() || '')
    setExposition(zone.exposition || 'aucune')
    setEtat(zone.etat || 'bon')
    setLiaisJardin(zone.lien_jardin || false)
    setIsDialogOpen(true)
  }

  const getTypeEmoji = (type: string) => {
    const emojis: Record<string, string> = {
      'potager': '🌱',
      'jardin': '🌳',
      'terrasse': '🏘️',
      'pelouse': '🟢',
      'bassin': '💧',
      'allee': '🛤️',
      'parking': '🅿️',
      'autre': '⚪',
    }
    return emojis[type] || '⚪'
  }

  const getEtatColor = (etat: string) => {
    const colors: Record<string, string> = {
      'bon': 'bg-green-100 text-green-800',
      'moyen': 'bg-yellow-100 text-yellow-800',
      'mauvais': 'bg-red-100 text-red-800',
    }
    return colors[etat] || 'bg-gray-100'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href={`/maison/simulation/${simulationId}`}>
            <Button variant="ghost" size="icon">
              <ArrowLeft size={20} />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Map size={28} />
              Terrain & Zones
            </h1>
            <p className="text-gray-600">Définissez les zones de votre terrain</p>
          </div>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button size="lg" onClick={() => resetForm()}>
              <Plus size={16} className="mr-2" />
              Nouvelle zone
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>
                {zoneAEditer ? 'Modifier la zone' : 'Créer une zone'}
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              {/* Nom */}
              <div>
                <label className="text-sm font-medium">Nom de la zone</label>
                <Input
                  placeholder="Ex: Potager principal"
                  value={nom}
                  onChange={(e) => setNom(e.target.value)}
                />
              </div>

              {/* Type */}
              <div>
                <label className="text-sm font-medium">Type</label>
                <Select value={type} onValueChange={setType}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="potager">🌱 Potager</SelectItem>
                    <SelectItem value="jardin">🌳 Jardin ornemental</SelectItem>
                    <SelectItem value="terrasse">🏘️ Terrasse</SelectItem>
                    <SelectItem value="pelouse">🟢 Pelouse</SelectItem>
                    <SelectItem value="bassin">💧 Bassin / Fontaine</SelectItem>
                    <SelectItem value="allee">🛤️ Allée</SelectItem>
                    <SelectItem value="parking">🅿️ Parking</SelectItem>
                    <SelectItem value="autre">⚪ Autre</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Surface */}
              <div>
                <label className="text-sm font-medium">Surface (m²)</label>
                <Input
                  type="number"
                  min={0}
                  step={1}
                  placeholder="0"
                  value={surface}
                  onChange={(e) => setSurface(e.target.value)}
                />
              </div>

              {/* Altitude */}
              <div>
                <label className="text-sm font-medium">Altitude (m) - Min/Max</label>
                <Input
                  placeholder="Ex: 150-155"
                  value={altitude}
                  onChange={(e) => setAltitude(e.target.value)}
                />
              </div>

              {/* Pente */}
              <div>
                <label className="text-sm font-medium">Pente (%)</label>
                <Input
                  type="number"
                  min={0}
                  max={100}
                  step={0.1}
                  placeholder="0"
                  value={pente}
                  onChange={(e) => setPente(e.target.value)}
                />
              </div>

              {/* Exposition */}
              <div>
                <label className="text-sm font-medium">Exposition</label>
                <Select value={exposition} onValueChange={setExposition}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="aucune">Aucune</SelectItem>
                    <SelectItem value="nord">Nord</SelectItem>
                    <SelectItem value="sud">Sud</SelectItem>
                    <SelectItem value="est">Est</SelectItem>
                    <SelectItem value="ouest">Ouest</SelectItem>
                    <SelectItem value="plein_soleil">Plein soleil</SelectItem>
                    <SelectItem value="ombre">Ombragée</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* État */}
              <div>
                <label className="text-sm font-medium">État</label>
                <Select value={etat} onValueChange={setEtat}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="bon">Bon</SelectItem>
                    <SelectItem value="moyen">Moyen</SelectItem>
                    <SelectItem value="mauvais">Mauvais</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Lien jardin */}
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={liaisJardin}
                  onChange={(e) => setLiaisJardin(e.target.checked)}
                />
                <span className="text-sm">Zone de liaison avec le jardin</span>
              </label>

              <Button
                onClick={handleSave}
                disabled={isCreating || isModifying || !nom.trim()}
                className="w-full"
              >
                {zoneAEditer ? 'Modifier' : 'Créer'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Liste des zones */}
      {isLoading ? (
        <Card className="p-8 text-center text-gray-500">Chargement...</Card>
      ) : zonesListe.length === 0 ? (
        <Card className="p-12 text-center">
          <div className="text-gray-400 mb-4 text-6xl">🌍</div>
          <h3 className="font-semibold text-gray-700 mb-2">Aucune zone définie</h3>
          <p className="text-gray-500 mb-4">Créez la première zone de votre terrain</p>
          <Button onClick={() => {
            resetForm()
            setIsDialogOpen(true)
          }}>
            <Plus size={16} className="mr-2" />
            Créer une zone
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {zonesListe.map((zone) => (
            <Card key={zone.id} className="p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{getTypeEmoji(zone.type_zone)}</span>
                  <div>
                    <h3 className="font-semibold">{zone.nom}</h3>
                    <p className="text-xs text-gray-600">{zone.type_zone}</p>
                  </div>
                </div>
                <span className={`text-xs px-2 py-1 rounded font-medium ${getEtatColor(zone.etat)}`}>
                  {zone.etat}
                </span>
              </div>

              <div className="space-y-2 text-sm mb-4">
                {zone.surface_m2 && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Surface</span>
                    <span className="font-medium">{zone.surface_m2} m²</span>
                  </div>
                )}
                {zone.pente_pct && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Pente</span>
                    <span className="font-medium">{zone.pente_pct}%</span>
                  </div>
                )}
                {zone.exposition && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Exposition</span>
                    <span className="font-medium">{zone.exposition}</span>
                  </div>
                )}
                {zone.lien_jardin && (
                  <div className="text-blue-600 text-xs">
                    ✓ Liaison jardin
                  </div>
                )}
              </div>

              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleEditer(zone)}
                  className="flex-1"
                >
                  <Edit size={14} className="mr-1" />
                  Éditer
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setZoneASupprimer(zone.id)}
                >
                  <Trash2 size={14} className="text-red-500" />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Dialog suppression */}
      <AlertDialog open={!!zoneASupprimer} onOpenChange={(open) => !open && setZoneASupprimer(null)}>
        <AlertDialogContent>
          <AlertDialogTitle>Supprimer cette zone ?</AlertDialogTitle>
          <AlertDialogDescription>
            Cette action est irréversible.
          </AlertDialogDescription>
          <div className="flex gap-3 justify-end">
            <AlertDialogCancel>Annuler</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => zoneASupprimer && supprimer(zoneASupprimer)}
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
