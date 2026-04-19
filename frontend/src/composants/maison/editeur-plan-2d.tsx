'use client'

import React, { useState, useRef, useCallback, useEffect } from 'react'
import { Stage, Layer, Rect, Circle, Text, Group, Line } from 'react-konva'
import { KonvaEventObject } from 'konva/lib/Node'
import { CanvasData, Mur, Porte, Fenetre, MeublePlan, Annotation, PlanMaison } from '@/types/maison'
import { chargerCanvas, sauvegarderCanvas } from '@/bibliotheque/api/maison'
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/composants/ui/tabs'
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/composants/ui/tooltip'
import { Trash2, Move, Square, DoorOpen, Type, Save, ZoomIn, ZoomOut } from 'lucide-react'

interface EditeurPlan2DProps {
  planId: number
  readOnly?: boolean
  onSave?: (donnees: CanvasData) => void
}

type ToolType = 'select' | 'mur' | 'porte' | 'fenetre' | 'meuble' | 'annotation'
type ElementType = 'mur' | 'porte' | 'fenetre' | 'meuble' | 'annotation'

interface ElementSelectionne {
  type: ElementType
  id: string
}

const ZOOM_FACTOR = 1.1

/**
 * Éditeur 2D pour les plans de maison (react-konva)
 * Permet de dessiner/modifier murs, portes, fenêtres, meubles, annotations
 */
export function EditeurPlan2D({
  planId,
  readOnly = false,
  onSave,
}: EditeurPlan2DProps) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const stageRef = useRef<any>(null)
  const [plan, setPlan] = useState<PlanMaison | null>(null)
  const [donnees, setDonnees] = useState<CanvasData>({
    murs: [],
    portes: [],
    fenetres: [],
    meubles: [],
    annotations: [],
  })
  const [toolActuel, setToolActuel] = useState<ToolType>('select')
  const [elementSelectionne, setElementSelectionne] = useState<ElementSelectionne | null>(null)
  const [zoom, setZoom] = useState(1)
  const [isDrawing, setIsDrawing] = useState(false)
  const [startPos, setStartPos] = useState<{ x: number; y: number } | null>(null)
  const [estEnChargement, setEstEnChargement] = useState(true)
  const [estSauvegarde, setEstSauvegarde] = useState(true)

  // ─── Charger le plan au montage ─────────────────────────────────────
  useEffect(() => {
    const charger = async () => {
      try {
        const data = await chargerCanvas(planId)
        setPlan(data)
        if (data.donnees_canvas) {
          setDonnees(data.donnees_canvas)
        }
      } catch (err) {
        console.error('Erreur lors du chargement du plan:', err)
      } finally {
        setEstEnChargement(false)
      }
    }
    charger()
  }, [planId])

  // ─── Sauvegarde automatique (débounce 2s) ────────────────────────────
  useEffect(() => {
    if (estEnChargement || readOnly) return

    const timer = setTimeout(async () => {
      try {
        await sauvegarderCanvas(planId, donnees)
        setEstSauvegarde(true)
        onSave?.(donnees)
      } catch (err) {
        console.error('Erreur lors de la sauvegarde:', err)
        setEstSauvegarde(false)
      }
    }, 2000)

    setEstSauvegarde(false)
    return () => clearTimeout(timer)
  }, [donnees, planId, readOnly, estEnChargement, onSave])

  // ─── Helpers pour gérer les objets ─────────────────────────────────
  const ajouterMur = useCallback(
    (x1: number, y1: number, x2: number, y2: number) => {
      const nouveauMur: Mur = {
        id: `mur-${Date.now()}`,
        x1,
        y1,
        x2,
        y2,
        epaisseur: 20,
        porteur: false,
        couleur: '#8B7355',
        label: '',
      }
      setDonnees((prev) => ({
        ...prev,
        murs: [...(prev.murs ?? []), nouveauMur],
      }))
    },
    []
  )

  const ajouterPorte = useCallback(
    (x: number, y: number) => {
      const nouvellePorte: Porte = {
        id: `porte-${Date.now()}`,
        x,
        y,
        largeur: 80,
        hauteur: 160,
        cote: 'gauche',
        label: '',
      }
      setDonnees((prev) => ({
        ...prev,
        portes: [...(prev.portes ?? []), nouvellePorte],
      }))
    },
    []
  )

  const ajouterFenetre = useCallback(
    (x: number, y: number) => {
      const nouvelleFenetre: Fenetre = {
        id: `fenetre-${Date.now()}`,
        x,
        y,
        largeur: 100,
        hauteur: 100,
        double_vitrage: false,
      }
      setDonnees((prev) => ({
        ...prev,
        fenetres: [...(prev.fenetres ?? []), nouvelleFenetre],
      }))
    },
    []
  )

  const ajouterMeuble = useCallback(
    (nom: string, type: string, x: number, y: number) => {
      const nouveauMeuble: MeublePlan = {
        id: `meuble-${Date.now()}`,
        nom,
        type,
        x,
        y,
        largeur: 100,
        hauteur: 100,
        rotation: 0,
        couleur: '#D2B48C',
      }
      setDonnees((prev) => ({
        ...prev,
        meubles: [...(prev.meubles ?? []), nouveauMeuble],
      }))
    },
    []
  )

  const ajouterAnnotation = useCallback(
    (x: number, y: number, texte: string) => {
      const nouvelleAnnotation: Annotation = {
        id: `annotation-${Date.now()}`,
        x,
        y,
        texte,
        type: 'note',
        icone: '📝',
      }
      setDonnees((prev) => ({
        ...prev,
        annotations: [...(prev.annotations ?? []), nouvelleAnnotation],
      }))
    },
    []
  )

  const supprimerElement = useCallback(() => {
    if (!elementSelectionne) return

    const { type, id } = elementSelectionne
    setDonnees((prev) => {
      const key = (type + 's') as keyof CanvasData
      type WithId = { id: string }
      return {
        ...prev,
        [key]: ((prev[key] ?? []) as WithId[]).filter((el) => el.id !== id),
      }
    })
    setElementSelectionne(null)
  }, [elementSelectionne])

  const mettreAJourElement = useCallback(
    (updates: Record<string, unknown>) => {
      if (!elementSelectionne) return

      const { type, id } = elementSelectionne
      const key = (type + 's') as keyof CanvasData

      setDonnees((prev) => {
        type WithId = { id: string }
        return {
          ...prev,
          [key]: ((prev[key] ?? []) as WithId[]).map((el) =>
            el.id === id ? { ...el, ...updates } : el
          ),
        }
      })
    },
    [elementSelectionne]
  )

  // ─── Gestion des événements canvas ────────────────────────────────
  const handleMouseDown = useCallback(
    (e: KonvaEventObject<MouseEvent>) => {
      const pos = e.target.getStage()?.getPointerPosition() || { x: 0, y: 0 }

      if (toolActuel === 'mur') {
        setIsDrawing(true)
        setStartPos(pos)
      } else if (toolActuel === 'porte') {
        ajouterPorte(pos.x, pos.y)
      } else if (toolActuel === 'fenetre') {
        ajouterFenetre(pos.x, pos.y)
      } else if (toolActuel === 'annotation') {
        ajouterAnnotation(pos.x, pos.y, 'Annotation')
      }
    },
    [toolActuel, ajouterPorte, ajouterFenetre, ajouterAnnotation]
  )

  const handleMouseMove = useCallback((_e: KonvaEventObject<MouseEvent>) => {
    // Déplacement en zoom: tenir la molette ou espace + drag
  }, [])

  const handleMouseUp = useCallback(
    (e: KonvaEventObject<MouseEvent>) => {
      if (toolActuel === 'mur' && isDrawing && startPos) {
        const pos = e.target.getStage()?.getPointerPosition() || { x: 0, y: 0 }
        ajouterMur(startPos.x, startPos.y, pos.x, pos.y)
      }
      setIsDrawing(false)
      setStartPos(null)
    },
    [toolActuel, isDrawing, startPos, ajouterMur]
  )

  const handleWheel = useCallback(
    (e: KonvaEventObject<WheelEvent>) => {
      e.evt.preventDefault()
      const stage = stageRef.current
      if (!stage) return

      const oldScale = zoom
      const pointer = stage.getPointerPosition()

      const mousePointTo = {
        x: (pointer.x - stage.x()) / oldScale,
        y: (pointer.y - stage.y()) / oldScale,
      }

      const newScale = e.evt.deltaY > 0 ? oldScale / ZOOM_FACTOR : oldScale * ZOOM_FACTOR
      setZoom(newScale)

      const newPos = {
        x: pointer.x - mousePointTo.x * newScale,
        y: pointer.y - mousePointTo.y * newScale,
      }

      stage.position(newPos)
      stage.scale({ x: newScale, y: newScale })
    },
    [zoom]
  )

  if (estEnChargement) {
    return <div className="flex items-center justify-center h-96">Chargement du plan...</div>
  }

  return (
    <div className="space-y-4">
      {/* ─── TOOLBAR ─────────────────────────────────────────────── */}
      <Card className="p-4">
        <div className="flex flex-wrap gap-2 items-center justify-between">
          {/* Outils de dessin */}
          <div className="flex gap-1 border rounded p-1 bg-gray-50">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  size="sm"
                  variant={toolActuel === 'select' ? 'default' : 'ghost'}
                  onClick={() => setToolActuel('select')}
                >
                  <Move size={16} />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Sélectionner</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  size="sm"
                  variant={toolActuel === 'mur' ? 'default' : 'ghost'}
                  onClick={() => setToolActuel('mur')}
                  disabled={readOnly}
                >
                  <Square size={16} />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Mur (drag)</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  size="sm"
                  variant={toolActuel === 'porte' ? 'default' : 'ghost'}
                  onClick={() => setToolActuel('porte')}
                  disabled={readOnly}
                >
                  <DoorOpen size={16} />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Porte</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  size="sm"
                  variant={toolActuel === 'fenetre' ? 'default' : 'ghost'}
                  onClick={() => setToolActuel('fenetre')}
                  disabled={readOnly}
                >
                  <Square size={16} />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Fenêtre</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  size="sm"
                  variant={toolActuel === 'annotation' ? 'default' : 'ghost'}
                  onClick={() => setToolActuel('annotation')}
                  disabled={readOnly}
                >
                  <Type size={16} />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Annotation</TooltipContent>
            </Tooltip>
          </div>

          {/* Zoom */}
          <div className="flex gap-1 border rounded p-1 bg-gray-50">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => {
                const stage = stageRef.current
                if (stage) {
                  const newScale = zoom / ZOOM_FACTOR
                  stage.scale({ x: newScale, y: newScale })
                  setZoom(newScale)
                }
              }}
            >
              <ZoomOut size={16} />
            </Button>
            <span className="w-12 text-center text-sm leading-8">{Math.round(zoom * 100)}%</span>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => {
                const stage = stageRef.current
                if (stage) {
                  const newScale = zoom * ZOOM_FACTOR
                  stage.scale({ x: newScale, y: newScale })
                  setZoom(newScale)
                }
              }}
            >
              <ZoomIn size={16} />
            </Button>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            {elementSelectionne && !readOnly && (
              <Button
                size="sm"
                variant="destructive"
                onClick={supprimerElement}
              >
                <Trash2 size={16} className="mr-1" />
                Supprimer
              </Button>
            )}

            {!readOnly && (
              <Button
                size="sm"
                variant="default"
                onClick={() => {
                  sauvegarderCanvas(planId, donnees)
                  setEstSauvegarde(true)
                }}
              >
                <Save size={16} className="mr-1" />
                Sauvegarder
              </Button>
            )}

            <span className="text-xs text-gray-500 leading-9">
              {estSauvegarde ? '✓ Sauvegardé' : '⏳ Sauvegarde...'}
            </span>
          </div>
        </div>
      </Card>

      {/* ─── CANVAS PRINCIPAL ─────────────────────────────────────── */}
      <Card className="overflow-hidden">
        <div className="bg-gray-100 h-[600px] relative">
          <Stage
            ref={stageRef}
            width={plan?.largeur_canvas || 1000}
            height={plan?.hauteur_canvas || 800}
            scale={{ x: zoom, y: zoom }}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onWheel={handleWheel}
            className="border border-gray-300"
            style={{ backgroundColor: '#FFF' }}
          >
            <Layer>
              {/* Murs */}
              {(donnees.murs ?? []).map((mur) => (
                <Group key={mur.id}>
                  <Line
                    points={[mur.x1, mur.y1, mur.x2, mur.y2]}
                    stroke={mur.couleur}
                    strokeWidth={mur.epaisseur}
                    lineCap="round"
                    lineJoin="round"
                    onClick={() =>
                      setElementSelectionne({ type: 'mur', id: mur.id })
                    }
                    opacity={
                      elementSelectionne?.id === mur.id ? 0.8 : 1
                    }
                  />
                  {mur.label && (
                    <Text
                      x={mur.x1 + (mur.x2 - mur.x1) / 2}
                      y={mur.y1 + (mur.y2 - mur.y1) / 2}
                      text={mur.label}
                      fontSize={12}
                      fill="#000"
                      align="center"
                    />
                  )}
                </Group>
              ))}

              {/* Portes */}
              {(donnees.portes ?? []).map((porte) => (
                <Group
                  key={porte.id}
                  onClick={() =>
                    setElementSelectionne({ type: 'porte', id: porte.id })
                  }
                  opacity={
                    elementSelectionne?.id === porte.id ? 0.8 : 1
                  }
                >
                  <Rect
                    x={porte.x}
                    y={porte.y}
                    width={porte.largeur}
                    height={porte.hauteur}
                    fill="#D4AF37"
                    stroke="#8B7500"
                    strokeWidth={2}
                  />
                  {porte.label && (
                    <Text
                      x={porte.x + porte.largeur / 2}
                      y={porte.y + porte.hauteur / 2}
                      text={porte.label}
                      fontSize={10}
                      fill="#000"
                      align="center"
                    />
                  )}
                </Group>
              ))}

              {/* Fenêtres */}
              {(donnees.fenetres ?? []).map((fenetre) => (
                <Group
                  key={fenetre.id}
                  onClick={() =>
                    setElementSelectionne({ type: 'fenetre', id: fenetre.id })
                  }
                  opacity={
                    elementSelectionne?.id === fenetre.id ? 0.8 : 1
                  }
                >
                  <Rect
                    x={fenetre.x}
                    y={fenetre.y}
                    width={fenetre.largeur}
                    height={fenetre.hauteur}
                    fill="#87CEEB"
                    stroke="#4169E1"
                    strokeWidth={2}
                  />
                  {fenetre.double_vitrage && (
                    <Line
                      points={[
                        fenetre.x + fenetre.largeur / 2,
                        fenetre.y,
                        fenetre.x + fenetre.largeur / 2,
                        fenetre.y + fenetre.hauteur,
                      ]}
                      stroke="#4169E1"
                      strokeWidth={1}
                      opacity={0.5}
                    />
                  )}
                </Group>
              ))}

              {/* Meubles */}
              {(donnees.meubles ?? []).map((meuble) => (
                <Group
                  key={meuble.id}
                  onClick={() =>
                    setElementSelectionne({ type: 'meuble', id: meuble.id })
                  }
                  opacity={
                    elementSelectionne?.id === meuble.id ? 0.8 : 1
                  }
                >
                  <Rect
                    x={meuble.x}
                    y={meuble.y}
                    width={meuble.largeur}
                    height={meuble.hauteur}
                    fill={meuble.couleur}
                    stroke="#333"
                    strokeWidth={1}
                    rotation={meuble.rotation}
                  />
                  <Text
                    x={meuble.x}
                    y={meuble.y + meuble.hauteur / 2 - 6}
                    text={meuble.nom}
                    fontSize={10}
                    fill="#000"
                  />
                </Group>
              ))}

              {/* Annotations */}
              {(donnees.annotations ?? []).map((annotation) => (
                <Group
                  key={annotation.id}
                  onClick={() =>
                    setElementSelectionne({
                      type: 'annotation',
                      id: annotation.id,
                    })
                  }
                  opacity={
                    elementSelectionne?.id === annotation.id ? 0.8 : 1
                  }
                >
                  <Circle
                    x={annotation.x}
                    y={annotation.y}
                    radius={12}
                    fill="#FFD700"
                    stroke="#FF8C00"
                    strokeWidth={2}
                  />
                  <Text
                    x={annotation.x - 6}
                    y={annotation.y - 8}
                    text={annotation.icone}
                    fontSize={14}
                  />
                </Group>
              ))}
            </Layer>
          </Stage>
        </div>
      </Card>

      {/* ─── PANNEAU PROPRIÉTÉS ───────────────────────────────────── */}
      {elementSelectionne && !readOnly && (
        <Card className="p-4">
          <h3 className="font-semibold mb-4">Propriétés de l'élément</h3>
          <Tabs defaultValue="general" className="w-full">
            <TabsList>
              <TabsTrigger value="general">Général</TabsTrigger>
              <TabsTrigger value="style">Style</TabsTrigger>
            </TabsList>

            <TabsContent value="general" className="space-y-4">
              {elementSelectionne.type === 'mur' && (
                <>
                  <div>
                    <label className="text-sm font-medium">Épaisseur (px)</label>
                    <Input
                      type="number"
                      min={1}
                      max={100}
                      defaultValue={
                        (donnees.murs ?? []).find((m) => m.id === elementSelectionne.id)
                          ?.epaisseur
                      }
                      onChange={(e) =>
                        mettreAJourElement({
                          epaisseur: parseInt(e.target.value),
                        })
                      }
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Label</label>
                    <Input
                      defaultValue={
                        (donnees.murs ?? []).find((m) => m.id === elementSelectionne.id)
                          ?.label
                      }
                      onChange={(e) =>
                        mettreAJourElement({ label: e.target.value })
                      }
                    />
                  </div>
                </>
              )}

              {elementSelectionne.type === 'porte' && (
                <>
                  <div>
                    <label className="text-sm font-medium">Côté</label>
                    <Select
                      defaultValue={
                        (donnees.portes ?? []).find((p) => p.id === elementSelectionne.id)
                          ?.cote || 'gauche'
                      }
                      onValueChange={(val) =>
                        mettreAJourElement({ cote: val })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="gauche">Gauche</SelectItem>
                        <SelectItem value="droite">Droite</SelectItem>
                        <SelectItem value="double">Double</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Label</label>
                    <Input
                      defaultValue={
                        (donnees.portes ?? []).find((p) => p.id === elementSelectionne.id)
                          ?.label
                      }
                      onChange={(e) =>
                        mettreAJourElement({ label: e.target.value })
                      }
                    />
                  </div>
                </>
              )}

              {elementSelectionne.type === 'fenetre' && (
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    defaultChecked={
                      (donnees.fenetres ?? []).find((f) => f.id === elementSelectionne.id)
                        ?.double_vitrage
                    }
                    onChange={(e) =>
                      mettreAJourElement({
                        double_vitrage: e.target.checked,
                      })
                    }
                  />
                  <span className="text-sm">Double vitrage</span>
                </label>
              )}

              {elementSelectionne.type === 'meuble' && (
                <>
                  <div>
                    <label className="text-sm font-medium">Nom</label>
                    <Input
                      defaultValue={
                        (donnees.meubles ?? []).find((m) => m.id === elementSelectionne.id)
                          ?.nom
                      }
                      onChange={(e) =>
                        mettreAJourElement({ nom: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Type</label>
                    <Input
                      defaultValue={
                        (donnees.meubles ?? []).find((m) => m.id === elementSelectionne.id)
                          ?.type
                      }
                      onChange={(e) =>
                        mettreAJourElement({ type: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Rotation (°)</label>
                    <Input
                      type="number"
                      min={0}
                      max={360}
                      defaultValue={
                        (donnees.meubles ?? []).find((m) => m.id === elementSelectionne.id)
                          ?.rotation || 0
                      }
                      onChange={(e) =>
                        mettreAJourElement({
                          rotation: parseInt(e.target.value),
                        })
                      }
                    />
                  </div>
                </>
              )}

              {elementSelectionne.type === 'annotation' && (
                <div>
                  <label className="text-sm font-medium">Texte</label>
                  <Input
                    defaultValue={
                      (donnees.annotations ?? []).find(
                        (a) => a.id === elementSelectionne.id
                      )?.texte
                    }
                    onChange={(e) =>
                      mettreAJourElement({ texte: e.target.value })
                    }
                  />
                </div>
              )}
            </TabsContent>

            <TabsContent value="style" className="space-y-4">
              {(elementSelectionne.type === 'mur' ||
                elementSelectionne.type === 'meuble') && (
                <div>
                  <label className="text-sm font-medium">Couleur</label>
                  <div className="flex gap-2 items-center">
                    <input
                      type="color"
                      aria-label="Couleur"
                      defaultValue={
                        elementSelectionne.type === 'mur'
                          ? (donnees.murs ?? []).find((m) => m.id === elementSelectionne.id)
                              ?.couleur || '#8B7355'
                          : (donnees.meubles ?? []).find(
                              (m) => m.id === elementSelectionne.id
                            )?.couleur || '#D2B48C'
                      }
                      onChange={(e) =>
                        mettreAJourElement({ couleur: e.target.value })
                      }
                    />
                    <span className="text-sm text-gray-500">
                      {elementSelectionne.type === 'mur'
                        ? (donnees.murs ?? []).find((m) => m.id === elementSelectionne.id)
                            ?.couleur
                        : (donnees.meubles ?? []).find(
                            (m) => m.id === elementSelectionne.id
                          )?.couleur}
                    </span>
                  </div>
                </div>
              )}

              {elementSelectionne.type === 'mur' && (
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    defaultChecked={
                      (donnees.murs ?? []).find((m) => m.id === elementSelectionne.id)
                        ?.porteur
                    }
                    onChange={(e) =>
                      mettreAJourElement({ porteur: e.target.checked })
                    }
                  />
                  <span className="text-sm">Mur porteur</span>
                </label>
              )}
            </TabsContent>
          </Tabs>
        </Card>
      )}
    </div>
  )
}

