"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Konva from "konva";
import { Circle, Group, Layer, Line, Rect, Stage, Text } from "react-konva";
import type { KonvaEventObject } from "konva/lib/Node";
import { Box, DoorOpen, Move, Save, Square, Trash2, Type, ZoomIn, ZoomOut } from "lucide-react";
import { chargerCanvasHabitat, sauvegarderCanvasHabitat } from "@/bibliotheque/api/habitat";
import { Button } from "@/composants/ui/button";
import { Card } from "@/composants/ui/card";
import { Input } from "@/composants/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/composants/ui/tooltip";
import type { Annotation, CanvasData, Fenetre, MeublePlan, Mur, Porte } from "@/types/maison";

interface EditeurPlan2DHabitatProps {
  planId: number;
  readOnly?: boolean;
  onSave?: (donnees: CanvasData) => void;
  onSynchroniser3D?: (donnees: CanvasData) => Promise<void> | void;
}

type OutilEdition = "select" | "mur" | "porte" | "fenetre" | "meuble" | "annotation";
type ElementEdition = "mur" | "porte" | "fenetre" | "meuble" | "annotation";

interface ElementSelectionne {
  type: ElementEdition;
  id: string;
}

interface MetaPlan {
  nom: string;
  version: number;
  type_plan: string;
  largeur_canvas: number;
  hauteur_canvas: number;
}

const ZOOM_FACTOR = 1.1;

function donneesInitiales(): CanvasData {
  return {
    murs: [],
    portes: [],
    fenetres: [],
    meubles: [],
    annotations: [],
  };
}

export function EditeurPlan2DHabitat({
  planId,
  readOnly = false,
  onSave,
  onSynchroniser3D,
}: EditeurPlan2DHabitatProps) {
  const stageRef = useRef<Konva.Stage | null>(null);
  const [meta, setMeta] = useState<MetaPlan | null>(null);
  const [donnees, setDonnees] = useState<CanvasData>(donneesInitiales);
  const [outil, setOutil] = useState<OutilEdition>("select");
  const [selection, setSelection] = useState<ElementSelectionne | null>(null);
  const [zoom, setZoom] = useState(1);
  const [dessinEnCours, setDessinEnCours] = useState(false);
  const [depart, setDepart] = useState<{ x: number; y: number } | null>(null);
  const [chargement, setChargement] = useState(true);
  const [sauvegardeOk, setSauvegardeOk] = useState(true);
  const [synchronisationEnCours, setSynchronisationEnCours] = useState(false);

  useEffect(() => {
    let annule = false;
    const charger = async () => {
      setChargement(true);
      try {
        const reponse = await chargerCanvasHabitat(planId);
        if (annule) {
          return;
        }
        setMeta({
          nom: reponse.nom,
          version: reponse.version,
          type_plan: reponse.type_plan,
          largeur_canvas: reponse.largeur_canvas,
          hauteur_canvas: reponse.hauteur_canvas,
        });
        setDonnees({ ...donneesInitiales(), ...(reponse.donnees_canvas ?? {}) });
      } catch (error) {
        console.error("Erreur de chargement du canvas Habitat", error);
      } finally {
        if (!annule) {
          setChargement(false);
        }
      }
    };
    void charger();
    return () => {
      annule = true;
    };
  }, [planId]);

  useEffect(() => {
    if (chargement || readOnly || !meta) {
      return;
    }

    const timer = window.setTimeout(async () => {
      try {
        await sauvegarderCanvasHabitat(planId, {
          donnees_canvas: donnees,
          largeur_canvas: meta.largeur_canvas,
          hauteur_canvas: meta.hauteur_canvas,
        });
        setSauvegardeOk(true);
        onSave?.(donnees);
      } catch (error) {
        console.error("Erreur de sauvegarde du canvas Habitat", error);
        setSauvegardeOk(false);
      }
    }, 1200);

    setSauvegardeOk(false);
    return () => window.clearTimeout(timer);
  }, [chargement, donnees, meta, onSave, planId, readOnly]);

  const ajouterMur = useCallback((x1: number, y1: number, x2: number, y2: number) => {
    const mur: Mur = {
      id: `mur-${Date.now()}`,
      x1,
      y1,
      x2,
      y2,
      epaisseur: 18,
      porteur: false,
      couleur: "#8b7355",
      label: "",
    };
    setDonnees((precedent) => ({ ...precedent, murs: [...(precedent.murs ?? []), mur] }));
  }, []);

  const ajouterPorte = useCallback((x: number, y: number) => {
    const porte: Porte = {
      id: `porte-${Date.now()}`,
      x,
      y,
      largeur: 90,
      hauteur: 24,
      cote: "gauche",
      label: "",
    };
    setDonnees((precedent) => ({ ...precedent, portes: [...(precedent.portes ?? []), porte] }));
  }, []);

  const ajouterFenetre = useCallback((x: number, y: number) => {
    const fenetre: Fenetre = {
      id: `fenetre-${Date.now()}`,
      x,
      y,
      largeur: 110,
      hauteur: 20,
      double_vitrage: true,
      label: "",
    };
    setDonnees((precedent) => ({
      ...precedent,
      fenetres: [...(precedent.fenetres ?? []), fenetre],
    }));
  }, []);

  const ajouterMeuble = useCallback((x: number, y: number) => {
    const meuble: MeublePlan = {
      id: `meuble-${Date.now()}`,
      nom: "Module",
      type: "module",
      x,
      y,
      largeur: 110,
      hauteur: 70,
      rotation: 0,
      couleur: "#d2b48c",
    };
    setDonnees((precedent) => ({ ...precedent, meubles: [...(precedent.meubles ?? []), meuble] }));
  }, []);

  const ajouterAnnotation = useCallback((x: number, y: number) => {
    const annotation: Annotation = {
      id: `annotation-${Date.now()}`,
      x,
      y,
      texte: "Repère technique",
      type: "warning",
      icone: "⚑",
    };
    setDonnees((precedent) => ({
      ...precedent,
      annotations: [...(precedent.annotations ?? []), annotation],
    }));
  }, []);

  const supprimerElement = useCallback(() => {
    if (!selection) {
      return;
    }
    setDonnees((precedent) => {
      if (selection.type === "mur") {
        return { ...precedent, murs: (precedent.murs ?? []).filter((item) => item.id !== selection.id) };
      }
      if (selection.type === "porte") {
        return { ...precedent, portes: (precedent.portes ?? []).filter((item) => item.id !== selection.id) };
      }
      if (selection.type === "fenetre") {
        return {
          ...precedent,
          fenetres: (precedent.fenetres ?? []).filter((item) => item.id !== selection.id),
        };
      }
      if (selection.type === "meuble") {
        return { ...precedent, meubles: (precedent.meubles ?? []).filter((item) => item.id !== selection.id) };
      }
      return {
        ...precedent,
        annotations: (precedent.annotations ?? []).filter((item) => item.id !== selection.id),
      };
    });
    setSelection(null);
  }, [selection]);

  const mettreAJourSelection = useCallback(
    (updates: Record<string, unknown>) => {
      if (!selection) {
        return;
      }
      setDonnees((precedent) => {
        if (selection.type === "mur") {
          return {
            ...precedent,
            murs: (precedent.murs ?? []).map((item) =>
              item.id === selection.id ? { ...item, ...updates } : item
            ),
          };
        }
        if (selection.type === "porte") {
          return {
            ...precedent,
            portes: (precedent.portes ?? []).map((item) =>
              item.id === selection.id ? { ...item, ...updates } : item
            ),
          };
        }
        if (selection.type === "fenetre") {
          return {
            ...precedent,
            fenetres: (precedent.fenetres ?? []).map((item) =>
              item.id === selection.id ? { ...item, ...updates } : item
            ),
          };
        }
        if (selection.type === "meuble") {
          return {
            ...precedent,
            meubles: (precedent.meubles ?? []).map((item) =>
              item.id === selection.id ? { ...item, ...updates } : item
            ),
          };
        }
        return {
          ...precedent,
          annotations: (precedent.annotations ?? []).map((item) =>
            item.id === selection.id ? { ...item, ...updates } : item
          ),
        };
      });
    },
    [selection]
  );

  const deplacerMur = useCallback((id: string, dx: number, dy: number) => {
    setDonnees((precedent) => ({
      ...precedent,
      murs: (precedent.murs ?? []).map((mur) =>
        mur.id === id
          ? { ...mur, x1: mur.x1 + dx, x2: mur.x2 + dx, y1: mur.y1 + dy, y2: mur.y2 + dy }
          : mur
      ),
    }));
  }, []);

  const deplacerElementPlan = useCallback(
    (type: Exclude<ElementEdition, "mur">, id: string, dx: number, dy: number) => {
      setDonnees((precedent) => {
        if (type === "porte") {
          return {
            ...precedent,
            portes: (precedent.portes ?? []).map((item) =>
              item.id === id ? { ...item, x: item.x + dx, y: item.y + dy } : item
            ),
          };
        }
        if (type === "fenetre") {
          return {
            ...precedent,
            fenetres: (precedent.fenetres ?? []).map((item) =>
              item.id === id ? { ...item, x: item.x + dx, y: item.y + dy } : item
            ),
          };
        }
        if (type === "meuble") {
          return {
            ...precedent,
            meubles: (precedent.meubles ?? []).map((item) =>
              item.id === id ? { ...item, x: item.x + dx, y: item.y + dy } : item
            ),
          };
        }
        return {
          ...precedent,
          annotations: (precedent.annotations ?? []).map((item) =>
            item.id === id ? { ...item, x: item.x + dx, y: item.y + dy } : item
          ),
        };
      });
    },
    []
  );

  const handleMouseDown = useCallback(
    (event: KonvaEventObject<MouseEvent>) => {
      const position = event.target.getStage()?.getPointerPosition() || { x: 0, y: 0 };
      if (outil === "mur") {
        setDessinEnCours(true);
        setDepart(position);
        return;
      }
      if (readOnly) {
        return;
      }
      if (outil === "porte") {
        ajouterPorte(position.x, position.y);
      } else if (outil === "fenetre") {
        ajouterFenetre(position.x, position.y);
      } else if (outil === "meuble") {
        ajouterMeuble(position.x, position.y);
      } else if (outil === "annotation") {
        ajouterAnnotation(position.x, position.y);
      }
    },
    [ajouterAnnotation, ajouterFenetre, ajouterMeuble, ajouterPorte, outil, readOnly]
  );

  const handleMouseUp = useCallback(
    (event: KonvaEventObject<MouseEvent>) => {
      if (outil === "mur" && dessinEnCours && depart) {
        const position = event.target.getStage()?.getPointerPosition() || { x: 0, y: 0 };
        ajouterMur(depart.x, depart.y, position.x, position.y);
      }
      setDessinEnCours(false);
      setDepart(null);
    },
    [ajouterMur, depart, dessinEnCours, outil]
  );

  const handleWheel = useCallback(
    (event: KonvaEventObject<WheelEvent>) => {
      event.evt.preventDefault();
      const stage = stageRef.current;
      if (!stage) {
        return;
      }
      const oldScale = zoom;
      const pointer = stage.getPointerPosition();
      if (!pointer) {
        return;
      }
      const pointReference = {
        x: (pointer.x - stage.x()) / oldScale,
        y: (pointer.y - stage.y()) / oldScale,
      };
      const newScale = event.evt.deltaY > 0 ? oldScale / ZOOM_FACTOR : oldScale * ZOOM_FACTOR;
      setZoom(newScale);
      stage.position({
        x: pointer.x - pointReference.x * newScale,
        y: pointer.y - pointReference.y * newScale,
      });
      stage.scale({ x: newScale, y: newScale });
    },
    [zoom]
  );

  const sauvegarderManuellement = useCallback(async () => {
    if (!meta) {
      return;
    }
    await sauvegarderCanvasHabitat(planId, {
      donnees_canvas: donnees,
      largeur_canvas: meta.largeur_canvas,
      hauteur_canvas: meta.hauteur_canvas,
    });
    setSauvegardeOk(true);
    onSave?.(donnees);
  }, [donnees, meta, onSave, planId]);

  const synchroniser3D = useCallback(async () => {
    if (!onSynchroniser3D) {
      return;
    }
    setSynchronisationEnCours(true);
    try {
      await onSynchroniser3D(donnees);
    } finally {
      setSynchronisationEnCours(false);
    }
  }, [donnees, onSynchroniser3D]);

  if (chargement) {
    return <div className="flex h-[520px] items-center justify-center rounded-xl border">Chargement du plan 2D...</div>;
  }

  const stats = [
    { label: "Murs", value: donnees.murs?.length ?? 0 },
    { label: "Porteurs", value: (donnees.murs ?? []).filter((mur) => mur.porteur).length },
    { label: "Ouvertures", value: (donnees.portes?.length ?? 0) + (donnees.fenetres?.length ?? 0) },
    { label: "Repères", value: donnees.annotations?.length ?? 0 },
  ];

  return (
    <div className="space-y-4">
      <Card className="p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="font-medium">{meta?.nom}</p>
            <p className="text-xs text-muted-foreground">
              {meta?.type_plan} · v{meta?.version} · {meta?.largeur_canvas}×{meta?.hauteur_canvas}px
            </p>
          </div>
          <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
            {stats.map((stat) => (
              <div key={stat.label} className="rounded-full border px-3 py-1">
                {stat.label}: {stat.value}
              </div>
            ))}
          </div>
        </div>
      </Card>

      <Card className="p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex gap-1 rounded border bg-muted/30 p-1">
            {[
              { id: "select", icon: <Move className="h-4 w-4" />, label: "Sélection" },
              { id: "mur", icon: <Square className="h-4 w-4" />, label: "Mur" },
              { id: "porte", icon: <DoorOpen className="h-4 w-4" />, label: "Porte" },
              { id: "fenetre", icon: <Square className="h-4 w-4" />, label: "Fenêtre" },
              { id: "meuble", icon: <Box className="h-4 w-4" />, label: "Module" },
              { id: "annotation", icon: <Type className="h-4 w-4" />, label: "Repère" },
            ].map((item) => (
              <Tooltip key={item.id}>
                <TooltipTrigger asChild>
                  <Button
                    size="sm"
                    variant={outil === item.id ? "default" : "ghost"}
                    onClick={() => setOutil(item.id as OutilEdition)}
                    disabled={readOnly && item.id !== "select"}
                  >
                    {item.icon}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>{item.label}</TooltipContent>
              </Tooltip>
            ))}
          </div>

          <div className="flex items-center gap-1 rounded border bg-muted/30 p-1">
            <Button size="sm" variant="ghost" onClick={() => setZoom((valeur) => valeur / ZOOM_FACTOR)}>
              <ZoomOut className="h-4 w-4" />
            </Button>
            <span className="w-14 text-center text-sm">{Math.round(zoom * 100)}%</span>
            <Button size="sm" variant="ghost" onClick={() => setZoom((valeur) => valeur * ZOOM_FACTOR)}>
              <ZoomIn className="h-4 w-4" />
            </Button>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {selection && !readOnly && (
              <Button size="sm" variant="destructive" onClick={supprimerElement}>
                <Trash2 className="mr-1 h-4 w-4" /> Supprimer
              </Button>
            )}
            {!readOnly && (
              <Button size="sm" variant="outline" onClick={() => void sauvegarderManuellement()}>
                <Save className="mr-1 h-4 w-4" /> Sauvegarder
              </Button>
            )}
            {onSynchroniser3D && (
              <Button size="sm" onClick={() => void synchroniser3D()} disabled={synchronisationEnCours}>
                {synchronisationEnCours ? "Projection..." : "Synchroniser vers 3D"}
              </Button>
            )}
            <span className="text-xs text-muted-foreground">
              {sauvegardeOk ? "✓ Canvas à jour" : "⏳ Sauvegarde..."}
            </span>
          </div>
        </div>
      </Card>

      <Card className="overflow-hidden">
        <div className="overflow-auto bg-slate-100 p-3">
          <Stage
            ref={stageRef}
            width={meta?.largeur_canvas ?? 1200}
            height={meta?.hauteur_canvas ?? 800}
            scale={{ x: zoom, y: zoom }}
            onMouseDown={handleMouseDown}
            onMouseUp={handleMouseUp}
            onWheel={handleWheel}
            className="border border-slate-300"
            style={{ backgroundColor: "#ffffff" }}
          >
            <Layer>
              {(donnees.murs ?? []).map((mur) => (
                <Group
                  key={mur.id}
                  draggable={!readOnly && outil === "select"}
                  onClick={() => setSelection({ type: "mur", id: mur.id })}
                  onDragEnd={(event) => {
                    deplacerMur(mur.id, event.target.x(), event.target.y());
                    event.target.position({ x: 0, y: 0 });
                  }}
                  opacity={selection?.id === mur.id ? 0.8 : 1}
                >
                  <Line
                    points={[mur.x1, mur.y1, mur.x2, mur.y2]}
                    stroke={mur.couleur ?? "#8b7355"}
                    strokeWidth={mur.epaisseur}
                    lineCap="round"
                    lineJoin="round"
                  />
                  {mur.label && (
                    <Text
                      x={(mur.x1 + mur.x2) / 2}
                      y={(mur.y1 + mur.y2) / 2}
                      text={mur.label}
                      fontSize={12}
                      fill="#0f172a"
                    />
                  )}
                </Group>
              ))}

              {(donnees.portes ?? []).map((porte) => (
                <Group
                  key={porte.id}
                  draggable={!readOnly && outil === "select"}
                  onClick={() => setSelection({ type: "porte", id: porte.id })}
                  onDragEnd={(event) => {
                    deplacerElementPlan("porte", porte.id, event.target.x(), event.target.y());
                    event.target.position({ x: 0, y: 0 });
                  }}
                  opacity={selection?.id === porte.id ? 0.8 : 1}
                >
                  <Rect x={porte.x} y={porte.y} width={porte.largeur} height={porte.hauteur} fill="#d4af37" stroke="#8b7500" strokeWidth={2} />
                </Group>
              ))}

              {(donnees.fenetres ?? []).map((fenetre) => (
                <Group
                  key={fenetre.id}
                  draggable={!readOnly && outil === "select"}
                  onClick={() => setSelection({ type: "fenetre", id: fenetre.id })}
                  onDragEnd={(event) => {
                    deplacerElementPlan("fenetre", fenetre.id, event.target.x(), event.target.y());
                    event.target.position({ x: 0, y: 0 });
                  }}
                  opacity={selection?.id === fenetre.id ? 0.8 : 1}
                >
                  <Rect x={fenetre.x} y={fenetre.y} width={fenetre.largeur} height={fenetre.hauteur} fill="#87ceeb" stroke="#4169e1" strokeWidth={2} />
                </Group>
              ))}

              {(donnees.meubles ?? []).map((meuble) => (
                <Group
                  key={meuble.id}
                  draggable={!readOnly && outil === "select"}
                  onClick={() => setSelection({ type: "meuble", id: meuble.id })}
                  onDragEnd={(event) => {
                    deplacerElementPlan("meuble", meuble.id, event.target.x(), event.target.y());
                    event.target.position({ x: 0, y: 0 });
                  }}
                  opacity={selection?.id === meuble.id ? 0.8 : 1}
                >
                  <Rect
                    x={meuble.x}
                    y={meuble.y}
                    width={meuble.largeur}
                    height={meuble.hauteur}
                    rotation={meuble.rotation}
                    fill={meuble.couleur ?? "#d2b48c"}
                    stroke="#334155"
                    strokeWidth={1}
                  />
                  <Text x={meuble.x + 6} y={meuble.y + meuble.hauteur / 2 - 6} text={meuble.nom} fontSize={10} fill="#0f172a" />
                </Group>
              ))}

              {(donnees.annotations ?? []).map((annotation) => (
                <Group
                  key={annotation.id}
                  draggable={!readOnly && outil === "select"}
                  onClick={() => setSelection({ type: "annotation", id: annotation.id })}
                  onDragEnd={(event) => {
                    deplacerElementPlan("annotation", annotation.id, event.target.x(), event.target.y());
                    event.target.position({ x: 0, y: 0 });
                  }}
                  opacity={selection?.id === annotation.id ? 0.8 : 1}
                >
                  <Circle x={annotation.x} y={annotation.y} radius={12} fill="#fde047" stroke="#f59e0b" strokeWidth={2} />
                  <Text x={annotation.x - 6} y={annotation.y - 8} text={annotation.icone ?? "⚑"} fontSize={14} />
                </Group>
              ))}
            </Layer>
          </Stage>
        </div>
      </Card>

      {selection && !readOnly && (
        <Card className="p-4">
          <h3 className="mb-4 font-semibold">Propriétés</h3>
          <Tabs defaultValue="general" className="w-full">
            <TabsList>
              <TabsTrigger value="general">Général</TabsTrigger>
              <TabsTrigger value="style">Style</TabsTrigger>
            </TabsList>
            <TabsContent value="general" className="space-y-4">
              {selection.type === "mur" && (
                <>
                  <div>
                    <label className="text-sm font-medium">Label</label>
                    <Input
                      defaultValue={(donnees.murs ?? []).find((item) => item.id === selection.id)?.label}
                      onChange={(event) => mettreAJourSelection({ label: event.target.value })}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Épaisseur</label>
                    <Input
                      type="number"
                      defaultValue={(donnees.murs ?? []).find((item) => item.id === selection.id)?.epaisseur ?? 18}
                      onChange={(event) => mettreAJourSelection({ epaisseur: Number(event.target.value) })}
                    />
                  </div>
                </>
              )}

              {selection.type === "porte" && (
                <>
                  <div>
                    <label className="text-sm font-medium">Label</label>
                    <Input
                      defaultValue={(donnees.portes ?? []).find((item) => item.id === selection.id)?.label}
                      onChange={(event) => mettreAJourSelection({ label: event.target.value })}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Ouverture</label>
                    <Select
                      defaultValue={(donnees.portes ?? []).find((item) => item.id === selection.id)?.cote ?? "gauche"}
                      onValueChange={(value) => mettreAJourSelection({ cote: value })}
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
                </>
              )}

              {selection.type === "fenetre" && (
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    defaultChecked={(donnees.fenetres ?? []).find((item) => item.id === selection.id)?.double_vitrage}
                    onChange={(event) => mettreAJourSelection({ double_vitrage: event.target.checked })}
                  />
                  Double vitrage
                </label>
              )}

              {selection.type === "meuble" && (
                <>
                  <div>
                    <label className="text-sm font-medium">Nom</label>
                    <Input
                      defaultValue={(donnees.meubles ?? []).find((item) => item.id === selection.id)?.nom}
                      onChange={(event) => mettreAJourSelection({ nom: event.target.value })}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Type</label>
                    <Input
                      defaultValue={(donnees.meubles ?? []).find((item) => item.id === selection.id)?.type}
                      onChange={(event) => mettreAJourSelection({ type: event.target.value })}
                    />
                  </div>
                </>
              )}

              {selection.type === "annotation" && (
                <>
                  <div>
                    <label className="text-sm font-medium">Texte</label>
                    <Input
                      defaultValue={(donnees.annotations ?? []).find((item) => item.id === selection.id)?.texte}
                      onChange={(event) => mettreAJourSelection({ texte: event.target.value })}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Type</label>
                    <Select
                      defaultValue={(donnees.annotations ?? []).find((item) => item.id === selection.id)?.type ?? "warning"}
                      onValueChange={(value) =>
                        mettreAJourSelection({ type: value, icone: value === "note" ? "📝" : value === "coffrage" ? "▣" : "⚑" })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="warning">Alerte</SelectItem>
                        <SelectItem value="coffrage">Coffrage</SelectItem>
                        <SelectItem value="imaison">Repère pièce</SelectItem>
                        <SelectItem value="note">Note</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </>
              )}
            </TabsContent>
            <TabsContent value="style" className="space-y-4">
              {(selection.type === "mur" || selection.type === "meuble") && (
                <div>
                  <label className="text-sm font-medium">Couleur</label>
                  <div className="mt-2 flex items-center gap-2">
                    <input
                      aria-label="Couleur de l'élément"
                      type="color"
                      onChange={(event) => mettreAJourSelection({ couleur: event.target.value })}
                    />
                  </div>
                </div>
              )}
              {selection.type === "mur" && (
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    defaultChecked={(donnees.murs ?? []).find((item) => item.id === selection.id)?.porteur}
                    onChange={(event) => mettreAJourSelection({ porteur: event.target.checked })}
                  />
                  Mur porteur
                </label>
              )}
            </TabsContent>
          </Tabs>
        </Card>
      )}
    </div>
  );
}

export default EditeurPlan2DHabitat;