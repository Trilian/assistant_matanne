"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Text } from "@react-three/drei";
import { useMemo } from "react";
import type { PieceHabitat } from "@/types/habitat";

interface Plan3DHabitatProps {
  pieces: PieceHabitat[];
  nomPlan?: string;
}

interface PieceLayout {
  id: number;
  nom: string;
  surface: number;
  type_piece: string;
  x: number;
  z: number;
  width: number;
  depth: number;
  color: string;
}

function palettePiece(typePiece?: string): string {
  const type = (typePiece ?? "").toLowerCase();
  if (type.includes("salon")) return "#f59e0b";
  if (type.includes("cuisine")) return "#f97316";
  if (type.includes("chambre")) return "#8b5cf6";
  if (type.includes("bain")) return "#0ea5e9";
  if (type.includes("bureau")) return "#22c55e";
  if (type.includes("entree") || type.includes("entrée")) return "#ec4899";
  return "#6366f1";
}

function construireLayout(pieces: PieceHabitat[]): PieceLayout[] {
  const avecSurface = pieces
    .filter((piece) => (piece.surface_m2 ?? 0) > 0)
    .map((piece) => ({
      ...piece,
      surface: Number(piece.surface_m2 ?? 10),
    }))
    .sort((a, b) => b.surface - a.surface);

  let curseurX = 0;
  let curseurZ = 0;
  let profondeurRangee = 0;
  const largeurMaxRangee = 16;
  const espacement = 0.6;

  return avecSurface.map((piece) => {
    const cote = Math.sqrt(piece.surface) * 0.85;
    const width = Math.max(2.4, Math.min(cote * 1.15, 7));
    const depth = Math.max(2.2, Math.min(cote * 0.9, 6));

    if (curseurX + width > largeurMaxRangee) {
      curseurX = 0;
      curseurZ += profondeurRangee + espacement;
      profondeurRangee = 0;
    }

    const layout: PieceLayout = {
      id: piece.id,
      nom: piece.nom,
      surface: piece.surface,
      type_piece: piece.type_piece ?? "autre",
      x: curseurX + width / 2,
      z: curseurZ + depth / 2,
      width,
      depth,
      color: palettePiece(piece.type_piece ?? piece.nom),
    };

    curseurX += width + espacement;
    profondeurRangee = Math.max(profondeurRangee, depth);
    return layout;
  });
}

function Piece3D({ piece }: { piece: PieceLayout }) {
  const hauteur = 1.8;

  return (
    <group position={[piece.x, 0, piece.z]}>
      <mesh position={[0, 0.03, 0]} receiveShadow>
        <boxGeometry args={[piece.width * 0.97, 0.06, piece.depth * 0.97]} />
        <meshStandardMaterial color="#f8fafc" roughness={0.9} metalness={0.02} />
      </mesh>
      <mesh position={[0, hauteur / 2, 0]} castShadow receiveShadow>
        <boxGeometry args={[piece.width, hauteur, piece.depth]} />
        <meshStandardMaterial
          color={piece.color}
          transparent
          opacity={0.78}
          roughness={0.5}
          metalness={0.04}
        />
      </mesh>
      <Text
        position={[0, hauteur + 0.22, 0]}
        fontSize={0.28}
        color="#0f172a"
        anchorX="center"
        anchorY="middle"
        maxWidth={piece.width}
      >
        {piece.nom}
      </Text>
      <Text
        position={[0, hauteur + 0.02, 0]}
        fontSize={0.18}
        color="#334155"
        anchorX="center"
        anchorY="middle"
      >
        {`${piece.surface.toFixed(0)} m2`}
      </Text>
    </group>
  );
}

export default function Plan3DHabitat({ pieces, nomPlan }: Plan3DHabitatProps) {
  const layout = useMemo(() => construireLayout(pieces), [pieces]);

  if (layout.length === 0) {
    return (
      <div className="flex h-[420px] items-center justify-center rounded-xl border border-dashed text-sm text-muted-foreground">
        Ajoutez des surfaces de pieces pour activer la visualisation 3D.
      </div>
    );
  }

  const maxX = Math.max(...layout.map((piece) => piece.x + piece.width / 2), 12);
  const maxZ = Math.max(...layout.map((piece) => piece.z + piece.depth / 2), 10);
  const centreX = maxX / 2;
  const centreZ = maxZ / 2;

  return (
    <div className="space-y-2">
      {nomPlan && (
        <p className="text-xs text-muted-foreground">
          Plan actif: <span className="font-medium text-foreground">{nomPlan}</span>
        </p>
      )}
      <div className="h-[460px] overflow-hidden rounded-xl border bg-slate-50">
        <Canvas shadows camera={{ position: [centreX + 8, 13, centreZ + 10], fov: 44 }}>
          <ambientLight intensity={0.55} />
          <directionalLight
            position={[8, 14, 10]}
            intensity={0.85}
            castShadow
            shadow-mapSize-width={1024}
            shadow-mapSize-height={1024}
          />
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[centreX, -0.01, centreZ]} receiveShadow>
            <planeGeometry args={[maxX + 8, maxZ + 8]} />
            <meshStandardMaterial color="#e2e8f0" roughness={0.95} />
          </mesh>
          {layout.map((piece) => (
            <Piece3D key={piece.id} piece={piece} />
          ))}
          <OrbitControls
            target={[centreX, 0, centreZ]}
            enablePan
            enableZoom
            enableRotate
            maxPolarAngle={Math.PI / 2.2}
          />
        </Canvas>
      </div>
    </div>
  );
}
