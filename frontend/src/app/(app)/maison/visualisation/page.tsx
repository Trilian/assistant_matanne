// ═══════════════════════════════════════════════════════════
// Visualisation Plan Maison — Vue 2D interactive des pièces
// Positionnement CSS absolu + mode édition drag & drop
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useRef, useCallback, useEffect, useMemo } from "react";
import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import {
  Home, Layers, Square, Info, ChevronLeft, ChevronRight, Pencil, Save, GripVertical, Box,
  ChevronDown, Loader2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/composants/ui/sheet";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/composants/ui/collapsible";
import { BoutonAchat } from "@/composants/bouton-achat";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import {
  listerPieces, listerEtages, sauvegarderPositions,
  creerTacheEntretien, obtenirDetailPiece, listerTachesEntretien,
} from "@/bibliotheque/api/maison";
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

// Tâches ménage rapide par type de pièce
const TACHES_MENAGE: Record<string, string[]> = {
  salon: ["Passer l'aspirateur", "Dépoussiérer", "Laver le sol"],
  chambre: ["Passer l'aspirateur", "Dépoussiérer", "Laver le sol"],
  cuisine: ["Dégraisser hotte", "Nettoyer four", "Laver le sol"],
  salle_de_bain: ["Récurer douche", "Laver le sol", "Nettoyer joints"],
  exterieur: ["Tondre pelouse", "Désherber", "Arroser"],
};
const TACHES_MENAGE_DEFAUT = ["Nettoyer", "Ranger", "Dépoussiérer"];

function obtenirTachesMenage(piece: PieceMaison): string[] {
  const ref = (piece.type_piece ?? piece.nom).toLowerCase().replace(/ /g, "_");
  for (const [cle, taches] of Object.entries(TACHES_MENAGE)) {
    if (ref.includes(cle)) return taches;
  }
  return TACHES_MENAGE_DEFAUT;
}

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
  const router = useRouter();
  const [etageActif, setEtageActif] = useState(0);
  const [pieceSelectionnee, setPieceSelectionnee] = useState<PieceMaison | null>(null);
  const [sheetPieceOuverte, setSheetPieceOuverte] = useState(false);
  const [menageOuvert, setMenageOuvert] = useState(false);
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

  const { data: tachesEntretien = [] } = utiliserRequete(
    ["maison", "entretien", "visualisation", String(etageActif)],
    () => listerTachesEntretien(),
    { refetchInterval: 30000 }
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

  // Détail pièce (objets avec statuts)
  const { data: detailPiece, isLoading: chargementDetail } = utiliserRequete(
    ["maison", "pieces", String(pieceSelectionnee?.id ?? ""), "detail"],
    () => obtenirDetailPiece(pieceSelectionnee!.id),
    { enabled: !!pieceSelectionnee && sheetPieceOuverte }
  );

  // Mutation planification tâche ménage rapide
  const { mutate: planifierTache, isPending: planifEnCours } = utiliserMutation(
    ({ nom, pieceNom }: { nom: string; pieceNom: string | undefined }) =>
      creerTacheEntretien({ nom, piece: pieceNom, fait: false }),
    { onSuccess: () => toast.success("Tâche planifiée") }
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

  const donneesParPiece = useMemo(() => {
    const aujourdHui = new Date();
    const normaliser = (valeur?: string | null) => (valeur ?? "").trim().toLowerCase();

    const map: Record<number, { piece_id: number; taches_en_retard: number; taches_total: number; alertes: string[] }> = {};

    for (const piece of pieces ?? []) {
      const pieceNom = normaliser(piece.nom);
      const tachesPiece = tachesEntretien.filter((t) => {
        const cible = normaliser(t.piece);
        return cible.length > 0 && (cible.includes(pieceNom) || pieceNom.includes(cible));
      });

      const tachesEnRetard = tachesPiece.filter((t) => {
        if (t.fait || !t.prochaine_fois) return false;
        const date = new Date(t.prochaine_fois);
        return !Number.isNaN(date.getTime()) && date < aujourdHui;
      }).length;

      const alertes: string[] = [];
      const objetsProblemes = (piece.objets ?? []).filter(
        (o) => o.statut === "hors_service" || o.statut === "a_reparer" || o.statut === "a_remplacer"
      ).length;
      if (objetsProblemes > 0) {
        alertes.push(`${objetsProblemes} objet(s) à traiter`);
      }
      if (tachesEnRetard > 0) {
        alertes.push(`${tachesEnRetard} tâche(s) en retard`);
      }

      map[piece.id] = {
        piece_id: piece.id,
        taches_total: tachesPiece.length,
        taches_en_retard: tachesEnRetard,
        alertes,
      };
    }

    return map;
  }, [pieces, tachesEntretien]);

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
                  onSelectPiece={(piece) => {
                    setPieceSelectionnee(piece);
                    setSheetPieceOuverte(true);
                    setMenageOuvert(false);
                  }}
                  donneesParPiece={donneesParPiece}
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
                        onClick={() => { setPieceSelectionnee(piece); setSheetPieceOuverte(true); setMenageOuvert(false); }}
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
                        onClick={() => { setPieceSelectionnee(piece); setSheetPieceOuverte(true); setMenageOuvert(false); }}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <Square className="h-3 w-3" style={{ color: couleurBord(piece) }} fill={couleurBord(piece)} /> {/* calculated color */}
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
                    onClick={() => { setPieceSelectionnee(piece); setSheetPieceOuverte(true); setMenageOuvert(false); }}
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

      {/* ── Sheet pièce — sidebar slide-in ── */}
      <Sheet open={sheetPieceOuverte} onOpenChange={(o) => { setSheetPieceOuverte(o); if (!o) setMenageOuvert(false); }}>
        <SheetContent side="right" className="w-[320px] sm:w-[360px] overflow-y-auto flex flex-col gap-4">
          {pieceSelectionnee && (
            <>
              <SheetHeader>
                <SheetTitle className="flex items-center gap-2">
                  <Square className="h-4 w-4" style={{ color: couleurBord(pieceSelectionnee) }} fill={couleurBord(pieceSelectionnee)} />
                  {pieceSelectionnee.nom}
                </SheetTitle>
                <div className="flex gap-3 text-xs text-muted-foreground">
                  <span>Étage : {pieceSelectionnee.etage === 0 ? "RDC" : pieceSelectionnee.etage}</span>
                  {pieceSelectionnee.surface_m2 && <span>{pieceSelectionnee.surface_m2} m²</span>}
                </div>
              </SheetHeader>

              {/* Section objets */}
              <div>
                <p className="text-xs font-semibold uppercase text-muted-foreground mb-2">Objets</p>
                {chargementDetail ? (
                  <div className="space-y-2">{[1, 2, 3].map(i => <Skeleton key={i} className="h-10" />)}</div>
                ) : detailPiece?.objets.length ? (
                  <ul className="space-y-2">
                    {detailPiece.objets.map((obj) => (
                      <li key={obj.id} className="flex items-center gap-2 text-sm border rounded px-2 py-1.5">
                        <span className="flex-1 truncate">{obj.nom}</span>
                        {obj.statut === "a_reparer" && (
                          <Badge variant="secondary" className="text-[10px] shrink-0">SAV</Badge>
                        )}
                        {obj.statut && (
                          <Badge
                            variant={obj.statut === "hors_service" ? "destructive" : obj.statut === "a_remplacer" ? "secondary" : "outline"}
                            className="text-[10px] shrink-0"
                          >
                            {obj.statut.replace(/_/g, " ")}
                          </Badge>
                        )}
                        {obj.statut === "hors_service" && (
                          <BoutonAchat article={{ nom: obj.nom }} taille="xs" />
                        )}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-muted-foreground">Aucun objet dans cette pièce</p>
                )}
              </div>

              {/* Section ménage rapide (collapsible) */}
              <Collapsible open={menageOuvert} onOpenChange={setMenageOuvert}>
                <CollapsibleTrigger asChild>
                  <button className="flex items-center justify-between w-full text-xs font-semibold uppercase text-muted-foreground hover:text-foreground transition-colors">
                    <span>Ménage rapide</span>
                    <ChevronDown className={`h-3.5 w-3.5 transition-transform ${menageOuvert ? "rotate-180" : ""}`} />
                  </button>
                </CollapsibleTrigger>
                <CollapsibleContent className="mt-2 space-y-1.5">
                  {obtenirTachesMenage(pieceSelectionnee).map((tache) => (
                    <div key={tache} className="flex items-center justify-between gap-2 text-sm border rounded px-2 py-1.5">
                      <span className="flex-1 truncate">{tache}</span>
                      <Button
                        size="sm"
                        variant="outline"
                        className="h-6 text-[10px] px-2 shrink-0"
                        disabled={planifEnCours}
                        onClick={() => planifierTache({ nom: tache, pieceNom: pieceSelectionnee?.nom })}
                      >
                        {planifEnCours ? <Loader2 className="h-3 w-3 animate-spin" /> : "+ Planifier"}
                      </Button>
                    </div>
                  ))}
                </CollapsibleContent>
              </Collapsible>

              {/* Footer boutons */}
              <div className="mt-auto pt-4 border-t flex flex-col gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => {
                    setSheetPieceOuverte(false);
                    router.push("/maison/travaux?tab=entretien");
                  }}
                >
                  📝 Entretien rapide
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => {
                    setSheetPieceOuverte(false);
                    router.push("/maison/travaux?tab=projets");
                  }}
                >
                  🔨 Projet travaux
                </Button>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}

