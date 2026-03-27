// ═══════════════════════════════════════════════════════════
// Visualisation Plan Maison — Vue 2D interactive des pièces
// Phase 7 — Positionnement CSS absolu + mode édition drag & drop
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import dynamic from "next/dynamic";
import {
  Home, Layers, Square, Info, ChevronLeft, ChevronRight, Pencil, Save, GripVertical, Box,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { listerPieces, listerEtages, sauvegarderPositions } from "@/bibliotheque/api/maison";
import type { PieceMaison } from "@/types/maison";
import { toast } from "sonner";

// Chargement dynamique côté client uniquement (WebGL)
const Plan3D = dynamic(() => import("@/composants/maison/plan-3d"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-[400px]">
      <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
    </div>
  ),
});

// Dimensions de la zone de plan
const PLAN_W = 800;
const PLAN_H = 560;
const PIECE_W_DEFAUT = 160;
const PIECE_H_DEFAUT = 120;

const COULEURS_DEFAUT: Record<string, string> = {
  salon: "#fbbf2440",
  cuisine: "#f97316 40",
  chambre: "#a78bfa40",
  "salle de bain": "#38bdf840",
  bureau: "#34d39940",
  entrée: "#f43f5e40",
  couloir: "#94a3b840",
  garage: "#78716c40",
  jardin: "#86efac40",
};

function couleurPiece(piece: PieceMaison): string {
  if (piece.couleur) return piece.couleur + "40";
  for (const [nom, couleur] of Object.entries(COULEURS_DEFAUT)) {
    if (piece.nom.toLowerCase().includes(nom)) return couleur;
  }
  return "#6366f140";
}

function couleurBord(piece: PieceMaison): string {
  if (piece.couleur) return piece.couleur;
  for (const [nom, couleur] of Object.entries(COULEURS_DEFAUT)) {
    if (piece.nom.toLowerCase().includes(nom)) return couleur.replace("40", "");
  }
  return "#6366f1";
}

// Vérifie si au moins une pièce a des positions
function aPosisions(pieces: PieceMaison[]): boolean {
  return pieces.some((p) => p.position_x != null && p.position_y != null);
}

export default function PageVisualisation() {
  const [etageActif, setEtageActif] = useState(0);
  const [pieceSelectionnee, setPieceSelectionnee] = useState<PieceMaison | null>(null);
  const [modeEdition, setModeEdition] = useState(false);
  const [mode3D, setMode3D] = useState(false);
  const [positions, setPositions] = useState<Record<number, { x: number; y: number }>>({});
  const [modifiees, setModifiees] = useState(false);
  const planRef = useRef<HTMLDivElement>(null);
  const dragOffset = useRef({ dx: 0, dy: 0 });
  const queryClient = useQueryClient();

  const { data: etages, isLoading: chargementEtages } = utiliserRequete(
    ["maison", "etages"],
    listerEtages
  );

  const { data: pieces, isLoading: chargementPieces } = utiliserRequete(
    ["maison", "pieces", String(etageActif)],
    () => listerPieces(etageActif)
  );

  // Sync positions from server data
  useEffect(() => {
    if (!pieces) return;
    const init: Record<number, { x: number; y: number }> = {};
    pieces.forEach((p) => {
      if (p.position_x != null && p.position_y != null) {
        init[p.id] = { x: p.position_x, y: p.position_y };
      }
    });
    setPositions(init);
    setModifiees(false);
  }, [pieces]);

  const sauvegarder = utiliserMutation(
    (payload: { id: number; position_x: number; position_y: number }[]) =>
      sauvegarderPositions(payload),
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["maison", "pieces"] });
        setModifiees(false);
        toast.success("Positions sauvegardées");
      },
    }
  );

  const handleSauvegarder = () => {
    const payload = Object.entries(positions).map(([id, pos]) => ({
      id: Number(id),
      position_x: Math.round(pos.x),
      position_y: Math.round(pos.y),
    }));
    sauvegarder.mutate(payload);
  };

  const etageMin = etages ? Math.min(...etages) : 0;
  const etageMax = etages ? Math.max(...etages) : 0;

  // Drag handlers
  const handleDragStart = useCallback(
    (e: React.DragEvent, piece: PieceMaison) => {
      if (!modeEdition) { e.preventDefault(); return; }
      const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
      dragOffset.current = {
        dx: e.clientX - rect.left,
        dy: e.clientY - rect.top,
      };
      e.dataTransfer.setData("pieceId", String(piece.id));
      e.dataTransfer.effectAllowed = "move";
    },
    [modeEdition]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const id = Number(e.dataTransfer.getData("pieceId"));
      if (!id || !planRef.current) return;
      const planRect = planRef.current.getBoundingClientRect();
      const piece = pieces?.find((p) => p.id === id);
      const w = piece?.largeur ?? PIECE_W_DEFAUT;
      const h = piece?.hauteur ?? PIECE_H_DEFAUT;
      const x = Math.max(0, Math.min(e.clientX - planRect.left - dragOffset.current.dx, PLAN_W - w));
      const y = Math.max(0, Math.min(e.clientY - planRect.top - dragOffset.current.dy, PLAN_H - h));
      setPositions((prev) => ({ ...prev, [id]: { x, y } }));
      setModifiees(true);
    },
    [pieces]
  );

  const positionPiece = (piece: PieceMaison) =>
    positions[piece.id] ?? (piece.position_x != null ? { x: piece.position_x, y: piece.position_y! } : null);

  const modesPositionnement = pieces && aPosisions(pieces);

  return (
    <div className="space-y-4">
      {/* En-tête */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Home className="h-6 w-6" />
            Plan de la maison
          </h1>
          <p className="text-muted-foreground text-sm">Vue interactive des pièces et de leur agencement</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={mode3D ? "default" : "outline"}
            size="sm"
            onClick={() => { setMode3D((v) => !v); setModeEdition(false); }}
            disabled={!modesPositionnement}
            title={!modesPositionnement ? "Définissez les positions 2D d'abord" : undefined}
          >
            <Box className="h-4 w-4 mr-1.5" />
            {mode3D ? "Vue 3D" : "Passer en 3D"}
          </Button>
          {!mode3D && (
            <Button
              variant={modeEdition ? "default" : "outline"}
              size="sm"
              onClick={() => { setModeEdition((v) => !v); }}
            >
              <Pencil className="h-4 w-4 mr-1.5" />
              {modeEdition ? "Édition active" : "Modifier positions"}
            </Button>
          )}
          {modeEdition && modifiees && (
            <Button size="sm" onClick={handleSauvegarder} disabled={sauvegarder.isPending}>
              <Save className="h-4 w-4 mr-1.5" />
              Sauvegarder
            </Button>
          )}
        </div>
      </div>

      {/* Sélecteur d'étage */}
      <div className="flex items-center gap-3">
        <Layers className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm font-medium">Étage :</span>
        <div className="flex items-center gap-1">
          <Button variant="outline" size="icon" className="h-8 w-8" disabled={etageActif <= etageMin} onClick={() => setEtageActif((e) => e - 1)} aria-label="Étage précédent">
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Badge variant="secondary" className="min-w-[60px] justify-center">
            {etageActif === 0 ? "RDC" : etageActif > 0 ? `+${etageActif}` : `${etageActif}`}
          </Badge>
          <Button variant="outline" size="icon" className="h-8 w-8" disabled={etageActif >= etageMax} onClick={() => setEtageActif((e) => e + 1)} aria-label="Étage suivant">
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
        {etages && <span className="text-xs text-muted-foreground ml-2">{etages.length} étage{etages.length > 1 ? "s" : ""}</span>}
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_300px]">
        {/* Zone plan */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              Plan {etageActif === 0 ? "rez-de-chaussée" : `étage ${etageActif}`}
              {modeEdition && <Badge variant="outline" className="text-[10px]">Glissez les pièces pour les repositionner</Badge>}
            </CardTitle>
          </CardHeader>
          <CardContent className="p-2">
            {(chargementPieces || chargementEtages) ? (
              <Skeleton className="h-[400px] w-full rounded-lg" />
            ) : mode3D && pieces && pieces.length > 0 ? (
              /* ── Vue 3D ── */
              <div className="rounded-lg overflow-hidden" style={{ height: 480 }}>
                <Plan3D
                  pieces={pieces}
                  pieceSelectionnee={pieceSelectionnee}
                  onSelectPiece={setPieceSelectionnee}
                />
              </div>
            ) : pieces && pieces.length > 0 ? (
              modesPositionnement ? (
                /* ── Mode 2D absolu ── */
                <div
                  ref={planRef}
                  className={`relative bg-muted/30 rounded-lg border-2 ${modeEdition ? "border-primary/40 border-dashed" : "border-dashed border-muted"} overflow-hidden`}
                  style={{ width: "100%", aspectRatio: `${PLAN_W}/${PLAN_H}`, maxWidth: PLAN_W }}
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                >
                  {/* Grille */}
                  <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-10" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                      <pattern id="grid2d" width="40" height="40" patternUnits="userSpaceOnUse">
                        <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="0.5" />
                      </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#grid2d)" />
                  </svg>

                  {pieces.map((piece) => {
                    const pos = positionPiece(piece);
                    if (!pos) return null;
                    const w = piece.largeur ?? PIECE_W_DEFAUT;
                    const h = piece.hauteur ?? PIECE_H_DEFAUT;
                    // Scale percentages relative to plan area
                    const left = `${(pos.x / PLAN_W) * 100}%`;
                    const top = `${(pos.y / PLAN_H) * 100}%`;
                    const width = `${(w / PLAN_W) * 100}%`;
                    const height = `${(h / PLAN_H) * 100}%`;

                    return (
                      <div
                        key={piece.id}
                        draggable={modeEdition}
                        onDragStart={(e) => handleDragStart(e, piece)}
                        onClick={() => setPieceSelectionnee(piece)}
                        className={`absolute rounded border-2 flex flex-col p-1.5 transition-shadow text-left
                          ${modeEdition ? "cursor-grab active:cursor-grabbing hover:shadow-lg hover:z-10" : "cursor-pointer hover:shadow-md hover:z-10"}
                          ${pieceSelectionnee?.id === piece.id ? "ring-2 ring-primary ring-offset-1 z-10" : ""}
                        `}
                        style={{
                          left, top, width, height,
                          backgroundColor: couleurPiece(piece),
                          borderColor: couleurBord(piece),
                        }}
                      >
                        {modeEdition && <GripVertical className="h-3 w-3 opacity-50 absolute top-1 right-1" />}
                        <p className="font-semibold text-[11px] leading-tight truncate">{piece.nom}</p>
                        {piece.surface_m2 && <p className="text-[10px] text-muted-foreground">{piece.surface_m2} m²</p>}
                        {piece.objets && piece.objets.length > 0 && (
                          <Badge variant="secondary" className="text-[9px] h-4 mt-auto self-start">{piece.objets.length} obj.</Badge>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                /* ── Mode grille fallback (pas de positions définies) ── */
                <div className="bg-muted/30 rounded-lg border-2 border-dashed border-muted p-4">
                  {modeEdition && (
                    <p className="text-xs text-muted-foreground text-center mb-4">
                      Activez le positionnement en sauvegardant les pièces avec des coordonnées définies dans le backend.
                    </p>
                  )}
                  <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 md:grid-cols-4">
                    {pieces.map((piece) => (
                      <button
                        key={piece.id}
                        className={`relative rounded-lg border-2 p-3 text-left transition-all cursor-pointer hover:shadow-md hover:scale-[1.02] ${pieceSelectionnee?.id === piece.id ? "border-primary ring-2 ring-primary/30 shadow-lg" : "border-border hover:border-primary/50"}`}
                        style={{ backgroundColor: couleurPiece(piece), borderColor: pieceSelectionnee?.id === piece.id ? undefined : couleurBord(piece) }}
                        onClick={() => setPieceSelectionnee(piece)}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <Square className="h-3 w-3" style={{ color: couleurBord(piece) }} fill={couleurBord(piece)} />
                          <span className="font-medium text-sm truncate">{piece.nom}</span>
                        </div>
                        {piece.surface_m2 && <span className="text-xs text-muted-foreground">{piece.surface_m2} m²</span>}
                        {piece.objets && piece.objets.length > 0 && <Badge variant="secondary" className="mt-1 text-[10px]">{piece.objets.length} objet{piece.objets.length > 1 ? "s" : ""}</Badge>}
                      </button>
                    ))}
                  </div>
                </div>
              )
            ) : (
              <div className="flex flex-col items-center justify-center h-[400px] text-muted-foreground">
                <Home className="h-12 w-12 mb-3 opacity-30" />
                <p>Aucune pièce définie pour cet étage</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Sidebar 300px */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Info className="h-4 w-4" />
                {pieceSelectionnee ? pieceSelectionnee.nom : "Détails"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {pieceSelectionnee ? (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <p className="text-muted-foreground text-xs">Étage</p>
                      <p className="font-medium">{pieceSelectionnee.etage === 0 ? "RDC" : pieceSelectionnee.etage}</p>
                    </div>
                    {pieceSelectionnee.surface_m2 && (
                      <div>
                        <p className="text-muted-foreground text-xs">Surface</p>
                        <p className="font-medium">{pieceSelectionnee.surface_m2} m²</p>
                      </div>
                    )}
                    {pieceSelectionnee.position_x != null && (
                      <div>
                        <p className="text-muted-foreground text-xs">Position</p>
                        <p className="font-medium text-xs">
                          ({positions[pieceSelectionnee.id]?.x ?? pieceSelectionnee.position_x}, {positions[pieceSelectionnee.id]?.y ?? pieceSelectionnee.position_y})
                        </p>
                      </div>
                    )}
                    {pieceSelectionnee.largeur && (
                      <div>
                        <p className="text-muted-foreground text-xs">Dimensions</p>
                        <p className="font-medium text-xs">{pieceSelectionnee.largeur} × {pieceSelectionnee.hauteur} px</p>
                      </div>
                    )}
                  </div>
                  {pieceSelectionnee.objets && pieceSelectionnee.objets.length > 0 && (
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">Objets ({pieceSelectionnee.objets.length})</p>
                      <ul className="space-y-1 max-h-40 overflow-y-auto">
                        {pieceSelectionnee.objets.map((obj) => (
                          <li key={obj.id} className="text-sm px-2 py-1 bg-muted rounded">
                            {obj.nom}
                            {obj.type && <span className="text-muted-foreground ml-1">• {obj.type}</span>}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Cliquez sur une pièce pour voir ses détails
                </p>
              )}
            </CardContent>
          </Card>

          {/* Légende */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Légende</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1 max-h-48 overflow-y-auto">
                {pieces?.map((piece) => (
                  <button
                    key={piece.id}
                    className={`flex items-center gap-2 text-xs w-full text-left rounded px-1 py-0.5 hover:bg-accent transition-colors ${pieceSelectionnee?.id === piece.id ? "bg-accent font-medium" : ""}`}
                    onClick={() => setPieceSelectionnee(piece)}
                  >
                    <div className="h-3 w-3 rounded-sm border shrink-0" style={{ backgroundColor: couleurPiece(piece), borderColor: couleurBord(piece) }} />
                    <span>{piece.nom}</span>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Résumé */}
          {pieces && pieces.length > 0 && (
            <Card>
              <CardContent className="pt-4">
                <div className="grid grid-cols-2 gap-3 text-center">
                  <div>
                    <p className="text-xl font-bold">{pieces.length}</p>
                    <p className="text-xs text-muted-foreground">Pièces</p>
                  </div>
                  <div>
                    <p className="text-xl font-bold">{pieces.reduce((a, p) => a + (p.surface_m2 ?? 0), 0)} m²</p>
                    <p className="text-xs text-muted-foreground">Surface</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { listerPieces, listerEtages } from "@/bibliotheque/api/maison";
import type { PieceMaison } from "@/types/maison";

// Couleurs par défaut pour les pièces (CSS custom properties)
const COULEURS_DEFAUT: Record<string, string> = {
  Salon: "var(--room-salon)",
  Cuisine: "var(--room-cuisine)",
  Chambre: "var(--room-chambre)",
  "Salle de bain": "var(--room-sdb)",
  Bureau: "var(--room-bureau)",
  Entrée: "var(--room-entree)",
  Couloir: "var(--room-couloir)",
  Garage: "var(--room-garage)",
  Jardin: "var(--room-jardin)",
};

function couleurPiece(piece: PieceMaison): string {
  if (piece.couleur) return piece.couleur;
  for (const [nom, couleur] of Object.entries(COULEURS_DEFAUT)) {
    if (piece.nom.toLowerCase().includes(nom.toLowerCase())) return couleur;
  }
  return "var(--color-primary)";
}

export default function PageVisualisation() {
  const [etageActif, setEtageActif] = useState(0);
  const [pieceSelectionnee, setPieceSelectionnee] = useState<PieceMaison | null>(null);

  const { data: etages, isLoading: chargementEtages } = utiliserRequete(
    ["maison", "etages"],
    listerEtages
  );

  const { data: pieces, isLoading: chargementPieces } = utiliserRequete(
    ["maison", "pieces", String(etageActif)],
    () => listerPieces(etageActif)
  );

  const etageMin = etages ? Math.min(...etages) : 0;
  const etageMax = etages ? Math.max(...etages) : 0;

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            <Home className="inline h-6 w-6 mr-2" />
            Plan de la maison
          </h1>
          <p className="text-muted-foreground">
            Vue interactive des pièces et de leur agencement
          </p>
        </div>
      </div>

      {/* Sélecteur d'étage */}
      <div className="flex items-center gap-3">
        <Layers className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm font-medium">Étage :</span>
        <div className="flex items-center gap-1">
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            disabled={etageActif <= etageMin}
            onClick={() => setEtageActif((e) => e - 1)}
            aria-label="Étage précédent"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Badge variant="secondary" className="min-w-[60px] justify-center">
            {etageActif === 0
              ? "RDC"
              : etageActif > 0
                ? `+${etageActif}`
                : `${etageActif}`}
          </Badge>
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            disabled={etageActif >= etageMax}
            onClick={() => setEtageActif((e) => e + 1)}
            aria-label="Étage suivant"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
        {etages && (
          <span className="text-xs text-muted-foreground ml-2">
            {etages.length} étage{etages.length > 1 ? "s" : ""}
          </span>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
        {/* Plan interactif */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              Plan {etageActif === 0 ? "rez-de-chaussée" : `étage ${etageActif}`}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {chargementPieces || chargementEtages ? (
              <Skeleton className="h-[400px] w-full rounded-lg" />
            ) : pieces && pieces.length > 0 ? (
              <div className="relative bg-muted/30 rounded-lg border-2 border-dashed border-muted min-h-[400px] p-4">
                {/* Grille SVG de fond */}
                <svg
                  className="absolute inset-0 w-full h-full pointer-events-none opacity-10"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <defs>
                    <pattern
                      id="grid"
                      width="40"
                      height="40"
                      patternUnits="userSpaceOnUse"
                    >
                      <path
                        d="M 40 0 L 0 0 0 40"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="0.5"
                      />
                    </pattern>
                  </defs>
                  <rect width="100%" height="100%" fill="url(#grid)" />
                </svg>

                {/* Pièces positionnées */}
                <div className="relative grid gap-3 grid-cols-2 sm:grid-cols-3 md:grid-cols-4">
                  {pieces.map((piece) => (
                    <button
                      key={piece.id}
                      className={`
                        relative rounded-lg border-2 p-3 text-left transition-all cursor-pointer
                        hover:shadow-md hover:scale-[1.02]
                        ${
                          pieceSelectionnee?.id === piece.id
                            ? "border-primary ring-2 ring-primary/30 shadow-lg"
                            : "border-border hover:border-primary/50"
                        }
                      `}
                      style={{
                        backgroundColor: couleurPiece(piece) + "33",
                        borderColor:
                          pieceSelectionnee?.id === piece.id
                            ? undefined
                            : couleurPiece(piece),
                      }}
                      onClick={() => setPieceSelectionnee(piece)}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <Square
                          className="h-3 w-3"
                          style={{ color: couleurPiece(piece) }}
                          fill={couleurPiece(piece)}
                        />
                        <span className="font-medium text-sm truncate">
                          {piece.nom}
                        </span>
                      </div>
                      {piece.surface_m2 && (
                        <span className="text-xs text-muted-foreground">
                          {piece.surface_m2} m²
                        </span>
                      )}
                      {piece.objets && piece.objets.length > 0 && (
                        <Badge variant="secondary" className="mt-1 text-[10px]">
                          {piece.objets.length} objet
                          {piece.objets.length > 1 ? "s" : ""}
                        </Badge>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-[400px] text-muted-foreground">
                <Home className="h-12 w-12 mb-3 opacity-30" />
                <p>Aucune pièce définie pour cet étage</p>
                <p className="text-sm mt-1">
                  Ajoutez des pièces via l'API pour les voir ici
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Panel détail */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Info className="h-4 w-4" />
                Détails
              </CardTitle>
            </CardHeader>
            <CardContent>
              {pieceSelectionnee ? (
                <div className="space-y-3">
                  <div>
                    <p className="text-sm font-medium">Nom</p>
                    <p className="text-lg font-bold">{pieceSelectionnee.nom}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <p className="text-muted-foreground">Étage</p>
                      <p className="font-medium">
                        {pieceSelectionnee.etage === 0
                          ? "RDC"
                          : pieceSelectionnee.etage}
                      </p>
                    </div>
                    {pieceSelectionnee.surface_m2 && (
                      <div>
                        <p className="text-muted-foreground">Surface</p>
                        <p className="font-medium">
                          {pieceSelectionnee.surface_m2} m²
                        </p>
                      </div>
                    )}
                  </div>
                  {pieceSelectionnee.objets &&
                    pieceSelectionnee.objets.length > 0 && (
                      <div>
                        <p className="text-sm text-muted-foreground mb-2">
                          Objets ({pieceSelectionnee.objets.length})
                        </p>
                        <ul className="space-y-1">
                          {pieceSelectionnee.objets.map((obj) => (
                            <li
                              key={obj.id}
                              className="text-sm px-2 py-1 bg-muted rounded"
                            >
                              {obj.nom}
                              {obj.type && (
                                <span className="text-muted-foreground ml-1">
                                  • {obj.type}
                                </span>
                              )}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Cliquez sur une pièce pour voir ses détails
                </p>
              )}
            </CardContent>
          </Card>

          {/* Légende */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Légende</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                {pieces?.map((piece) => (
                  <div key={piece.id} className="flex items-center gap-2 text-xs">
                    <div
                      className="h-3 w-3 rounded-sm border"
                      style={{ backgroundColor: couleurPiece(piece) }}
                    />
                    <span>{piece.nom}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Résumé étage */}
          {pieces && pieces.length > 0 && (
            <Card>
              <CardContent className="pt-4">
                <div className="grid grid-cols-2 gap-3 text-center">
                  <div>
                    <p className="text-xl font-bold">{pieces.length}</p>
                    <p className="text-xs text-muted-foreground">Pièces</p>
                  </div>
                  <div>
                    <p className="text-xl font-bold">
                      {pieces.reduce((a, p) => a + (p.surface_m2 ?? 0), 0)} m²
                    </p>
                    <p className="text-xs text-muted-foreground">Surface totale</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
