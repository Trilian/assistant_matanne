// ═══════════════════════════════════════════════════════════
// Visualisation Plan Maison — Vue interactive des pièces
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  Home,
  Layers,
  Square,
  Info,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { listerPieces, listerEtages } from "@/bibliotheque/api/maison";
import type { PieceMaison } from "@/types/maison";

// Couleurs par défaut pour les pièces
const COULEURS_DEFAUT: Record<string, string> = {
  Salon: "#93c5fd",
  Cuisine: "#fcd34d",
  Chambre: "#c4b5fd",
  "Salle de bain": "#6ee7b7",
  Bureau: "#fdba74",
  Entrée: "#d1d5db",
  Couloir: "#e5e7eb",
  Garage: "#a1a1aa",
  Jardin: "#86efac",
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
