// ═══════════════════════════════════════════════════════════
// Plan 3D — Vue isométrique des pièces de la maison
// Chargé dynamiquement (ssr: false) depuis la page visualisation
// ═══════════════════════════════════════════════════════════

"use client";

import { useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Text } from "@react-three/drei";
import type { PieceMaison } from "@/types/maison";

// Dimensions du plan en unités 3D (1 unit = 40px du plan 2D)
const SCALE = 1 / 40;
const WALL_HEIGHT = 2;
const PLAN_W = 800;
const PLAN_H = 560;

function couleurHex(piece: PieceMaison): string {
  if (piece.couleur) return piece.couleur;
  const nom = piece.nom.toLowerCase();
  if (nom.includes("salon")) return "#fbbf24";
  if (nom.includes("cuisine")) return "#f97316";
  if (nom.includes("chambre")) return "#a78bfa";
  if (nom.includes("salle de bain")) return "#38bdf8";
  if (nom.includes("bureau")) return "#34d399";
  if (nom.includes("entrée")) return "#f43f5e";
  if (nom.includes("garage")) return "#78716c";
  if (nom.includes("jardin")) return "#86efac";
  return "#6366f1";
}

function PieceBox({ piece, selectionne, onClick }: {
  piece: PieceMaison;
  selectionne: boolean;
  onClick: () => void;
}) {
  const [hovered, setHovered] = useState(false);

  const px = piece.position_x ?? 0;
  const py = piece.position_y ?? 0;
  const w = (piece.largeur ?? 160) * SCALE;
  const d = (piece.hauteur ?? 120) * SCALE;
  const h = WALL_HEIGHT;

  // Centre en 3D (plan x/z, hauteur y)
  const cx = (px + (piece.largeur ?? 160) / 2) * SCALE - PLAN_W * SCALE / 2;
  const cy = h / 2;
  const cz = (py + (piece.hauteur ?? 120) / 2) * SCALE - PLAN_H * SCALE / 2;

  const color = couleurHex(piece);
  const opacity = hovered ? 0.9 : selectionne ? 0.95 : 0.75;

  return (
    <group position={[cx, cy, cz]} onClick={(e) => { e.stopPropagation(); onClick(); }}>
      <mesh
        onPointerEnter={() => setHovered(true)}
        onPointerLeave={() => setHovered(false)}
        castShadow
        receiveShadow
      >
        <boxGeometry args={[w, h, d]} />
        <meshStandardMaterial
          color={color}
          transparent
          opacity={opacity}
          wireframe={false}
        />
      </mesh>
      {/* Bordure si sélectionnée */}
      {selectionne && (
        <mesh>
          <boxGeometry args={[w + 0.02, h + 0.02, d + 0.02]} />
          <meshStandardMaterial color="#6366f1" wireframe opacity={0.8} transparent />
        </mesh>
      )}
      {/* Label */}
      <Text
        position={[0, h / 2 + 0.15, 0]}
        fontSize={0.25}
        color="#1e293b"
        anchorX="center"
        anchorY="middle"
        maxWidth={w}
      >
        {piece.nom}
      </Text>
    </group>
  );
}

function Sol({ pieces }: { pieces: PieceMaison[] }) {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
      <planeGeometry args={[PLAN_W * SCALE + 2, PLAN_H * SCALE + 2]} />
      <meshStandardMaterial color="#f8fafc" />
    </mesh>
  );
}

interface Plan3DProps {
  pieces: PieceMaison[];
  pieceSelectionnee: PieceMaison | null;
  onSelectPiece: (piece: PieceMaison) => void;
}

export default function Plan3D({ pieces, pieceSelectionnee, onSelectPiece }: Plan3DProps) {
  const piecesAvecPos = pieces.filter((p) => p.position_x != null && p.position_y != null);

  if (piecesAvecPos.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
        <p>Définissez les positions 2D d&apos;abord pour activer la vue 3D</p>
      </div>
    );
  }

  return (
    <Canvas
      shadows
      camera={{ position: [8, 10, 8], fov: 50 }}
      style={{ background: "#f1f5f9", borderRadius: "0.5rem" }}
    >
      <ambientLight intensity={0.6} />
      <directionalLight
        position={[10, 15, 10]}
        intensity={0.8}
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />
      <OrbitControls
        enablePan
        enableZoom
        enableRotate
        minPolarAngle={0}
        maxPolarAngle={Math.PI / 2.2}
      />
      <Sol pieces={piecesAvecPos} />
      {piecesAvecPos.map((piece) => (
        <PieceBox
          key={piece.id}
          piece={piece}
          selectionne={pieceSelectionnee?.id === piece.id}
          onClick={() => onSelectPiece(piece)}
        />
      ))}
    </Canvas>
  );
}
