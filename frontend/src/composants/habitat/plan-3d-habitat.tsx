"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Text } from "@react-three/drei";
import { useEffect, useMemo, useRef, useState, type ChangeEvent } from "react";
import { z } from "zod";
import type {
  PieceHabitat,
  PlanHabitatConfiguration3D,
  PlanHabitatConfiguration3DServeur,
  PlanHabitatVariante3D,
} from "@/types/habitat";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";

interface Plan3DHabitatProps {
  pieces: PieceHabitat[];
  nomPlan?: string;
  planId?: number;
  piecesVariante?: PieceHabitat[];
  afficherComparaison?: boolean;
  configurationServeur?: PlanHabitatConfiguration3DServeur | null;
  sauvegardeServeurEnCours?: boolean;
  onSauvegarderConfigurationServeur?: (
    payload: Omit<PlanHabitatConfiguration3DServeur, "plan_id">
  ) => Promise<void> | void;
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
  typeSource: string;
}

type PaletteTypePiece = Record<string, string>;

type EtatDrag = {
  id: number;
  offsetX: number;
  offsetZ: number;
};

type PiecePersisted = Pick<PieceLayout, "id" | "x" | "z" | "width" | "depth">;

type Etat3DPersisted = {
  layoutEdition: PiecePersisted[];
  paletteParType: PaletteTypePiece;
};

type ModeImport = "remplacer" | "fusionner" | "palette";

type ConfigurationImportee = z.infer<typeof schemaConfigurationImport>;

const schemaPiecePersisted = z.object({
  id: z.number().int(),
  x: z.number().finite(),
  z: z.number().finite(),
  width: z.number().finite().min(1.8).max(12),
  depth: z.number().finite().min(1.8).max(12),
});

const schemaConfigurationImport = z.object({
  version: z.number().int().optional(),
  plan_id: z.number().int().nullable().optional(),
  nom_plan: z.string().nullable().optional(),
  exporte_le: z.string().optional(),
  layoutEdition: z.array(schemaPiecePersisted).optional(),
  paletteParType: z.record(z.string(), z.string().regex(/^#[0-9a-fA-F]{6}$/)).default({}).optional(),
  configuration_courante: z
    .object({
      layout_edition: z.array(schemaPiecePersisted),
      palette_par_type: z.record(z.string(), z.string().regex(/^#[0-9a-fA-F]{6}$/)).default({}),
    })
    .optional(),
  variantes: z
    .array(
      z.object({
        id: z.string().min(1),
        nom: z.string().min(1),
        source: z.string().min(1),
        configuration: z.object({
          layout_edition: z.array(schemaPiecePersisted),
          palette_par_type: z.record(z.string(), z.string().regex(/^#[0-9a-fA-F]{6}$/)).default({}),
        }),
      })
    )
    .default([]),
  variante_active_id: z.string().nullable().optional(),
}).refine((valeur) => Array.isArray(valeur.layoutEdition) || Boolean(valeur.configuration_courante), {
  message: "configuration absente",
});

type ImportNormalise = {
  planIdSource: number | null;
  nomPlanSource: string | null;
  configurationCourante: PlanHabitatConfiguration3D;
  variantes: PlanHabitatVariante3D[];
  varianteActiveId: string | null;
};

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
      typeSource: (piece.type_piece ?? piece.nom ?? "autre").toLowerCase(),
    };

    curseurX += width + espacement;
    profondeurRangee = Math.max(profondeurRangee, depth);
    return layout;
  });
}

function calculerBornes(layout: PieceLayout[]) {
  const maxX = Math.max(...layout.map((piece) => piece.x + piece.width / 2), 12);
  const maxZ = Math.max(...layout.map((piece) => piece.z + piece.depth / 2), 10);
  return {
    maxX,
    maxZ,
    centreX: maxX / 2,
    centreZ: maxZ / 2,
  };
}

function trouverCouleurPiece(piece: PieceLayout, palette: PaletteTypePiece): string {
  const type = piece.typeSource;
  if (palette[type]) {
    return palette[type];
  }
  return palettePiece(piece.type_piece || piece.nom);
}

function paletteParDefaut(layout: PieceLayout[]): PaletteTypePiece {
  const typesUniques = new Set(layout.map((piece) => piece.typeSource));
  const palette: PaletteTypePiece = {};
  typesUniques.forEach((type) => {
    palette[type] = palettePiece(type);
  });
  return palette;
}

function appliquerLayoutPersisted(layoutBase: PieceLayout[], persisted: PiecePersisted[]): PieceLayout[] {
  const parId = new Map<number, PiecePersisted>(persisted.map((item) => [item.id, item]));
  return layoutBase.map((piece) => {
    const sauvegarde = parId.get(piece.id);
    if (!sauvegarde) {
      return piece;
    }
    return {
      ...piece,
      x: sauvegarde.x,
      z: sauvegarde.z,
      width: sauvegarde.width,
      depth: sauvegarde.depth,
    };
  });
}

function calculerCompatibiliteImport(layoutBase: PieceLayout[], persisted: PiecePersisted[]) {
  const idsLocaux = new Set(layoutBase.map((piece) => piece.id));
  const idsImportes = new Set(persisted.map((piece) => piece.id));
  const idsCorrespondants = [...idsImportes].filter((id) => idsLocaux.has(id));

  return {
    totalImportees: idsImportes.size,
    appliquees: idsCorrespondants.length,
    ignorees: Math.max(0, idsImportes.size - idsCorrespondants.length),
  };
}

function construireConfigurationCourante(
  layoutEdition: PieceLayout[],
  paletteParType: PaletteTypePiece
): PlanHabitatConfiguration3D {
  return {
    layout_edition: layoutEdition.map((piece) => ({
      id: piece.id,
      x: piece.x,
      z: piece.z,
      width: piece.width,
      depth: piece.depth,
      nom: piece.nom,
      type_piece: piece.type_piece,
    })),
    palette_par_type: paletteParType,
  };
}

function appliquerConfiguration3D(
  layoutBase: PieceLayout[],
  configuration: PlanHabitatConfiguration3D,
  mode: ModeImport,
  layoutCourant?: PieceLayout[]
) {
  const base = mode === "fusionner" && layoutCourant ? layoutCourant : layoutBase;
  if (mode === "palette") {
    return layoutCourant ?? layoutBase;
  }
  return appliquerLayoutPersisted(base, configuration.layout_edition);
}

function normaliserConfigurationImportee(configuration: ConfigurationImportee): ImportNormalise {
  const configurationCourante = configuration.configuration_courante ?? {
    layout_edition: configuration.layoutEdition ?? [],
    palette_par_type: configuration.paletteParType ?? {},
  };

  return {
    planIdSource: configuration.plan_id ?? null,
    nomPlanSource: configuration.nom_plan ?? null,
    configurationCourante,
    variantes: configuration.variantes ?? [],
    varianteActiveId: configuration.variante_active_id ?? null,
  };
}

function fusionnerVariantes(
  variantesExistantes: PlanHabitatVariante3D[],
  variantesImportees: PlanHabitatVariante3D[]
): PlanHabitatVariante3D[] {
  const variantesParId = new Map<string, PlanHabitatVariante3D>();
  for (const variante of variantesExistantes) {
    variantesParId.set(variante.id, variante);
  }
  for (const variante of variantesImportees) {
    variantesParId.set(variante.id, variante);
  }
  return [...variantesParId.values()];
}

function genererIdVariante() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID().slice(0, 12);
  }
  return `var_${Date.now().toString(36)}`;
}

function arrondirSurGrille(valeur: number, pas = 0.25) {
  return Math.round(valeur / pas) * pas;
}

function detecterChevauchement(
  layout: PieceLayout[],
  pieceId: number,
  prochainX: number,
  prochainZ: number
) {
  const pieceActive = layout.find((piece) => piece.id === pieceId);
  if (!pieceActive) {
    return false;
  }

  return layout.some((piece) => {
    if (piece.id === pieceId) {
      return false;
    }

    const chevaucheEnX = Math.abs(prochainX - piece.x) < (pieceActive.width + piece.width) / 2;
    const chevaucheEnZ = Math.abs(prochainZ - piece.z) < (pieceActive.depth + piece.depth) / 2;
    return chevaucheEnX && chevaucheEnZ;
  });
}

function Piece3D({
  piece,
  couleur,
  estSelectionnee,
  editionActive,
  onPointerDown,
}: {
  piece: PieceLayout;
  couleur: string;
  estSelectionnee: boolean;
  editionActive: boolean;
  onPointerDown?: (piece: PieceLayout, pointX: number, pointZ: number) => void;
}) {
  const hauteur = 1.8;

  return (
    <group position={[piece.x, 0, piece.z]}>
      <mesh position={[0, 0.03, 0]} receiveShadow>
        <boxGeometry args={[piece.width * 0.97, 0.06, piece.depth * 0.97]} />
        <meshStandardMaterial color="#f8fafc" roughness={0.9} metalness={0.02} />
      </mesh>
      <mesh
        position={[0, hauteur / 2, 0]}
        castShadow
        receiveShadow
        onPointerDown={(event) => {
          event.stopPropagation();
          if (!editionActive || !onPointerDown) {
            return;
          }
          onPointerDown(piece, event.point.x, event.point.z);
        }}
      >
        <boxGeometry args={[piece.width, hauteur, piece.depth]} />
        <meshStandardMaterial
          color={couleur}
          transparent
          opacity={estSelectionnee ? 0.95 : 0.78}
          roughness={estSelectionnee ? 0.35 : 0.5}
          metalness={estSelectionnee ? 0.08 : 0.04}
          emissive={estSelectionnee ? "#1d4ed8" : "#000000"}
          emissiveIntensity={estSelectionnee ? 0.2 : 0}
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

function Vue3DPlan({
  titre,
  layout,
  palette,
  editionActive,
  pieceSelectionneeId,
  onPiecePointerDown,
  onGroundPointerMove,
  onGroundPointerUp,
}: {
  titre?: string;
  layout: PieceLayout[];
  palette: PaletteTypePiece;
  editionActive: boolean;
  pieceSelectionneeId?: number;
  onPiecePointerDown?: (piece: PieceLayout, pointX: number, pointZ: number) => void;
  onGroundPointerMove?: (pointX: number, pointZ: number) => void;
  onGroundPointerUp?: () => void;
}) {
  const { maxX, maxZ, centreX, centreZ } = useMemo(() => calculerBornes(layout), [layout]);

  return (
    <div className="space-y-2">
      {titre && <p className="text-xs text-muted-foreground">{titre}</p>}
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
          {editionActive && (
            <mesh
              rotation={[-Math.PI / 2, 0, 0]}
              position={[centreX, 0.02, centreZ]}
              onPointerMove={(event) => {
                event.stopPropagation();
                onGroundPointerMove?.(event.point.x, event.point.z);
              }}
              onPointerUp={(event) => {
                event.stopPropagation();
                onGroundPointerUp?.();
              }}
              onPointerLeave={() => onGroundPointerUp?.()}
            >
              <planeGeometry args={[maxX + 8, maxZ + 8]} />
              <meshBasicMaterial transparent opacity={0} />
            </mesh>
          )}
          {layout.map((piece) => (
            <Piece3D
              key={piece.id}
              piece={piece}
              couleur={trouverCouleurPiece(piece, palette)}
              estSelectionnee={pieceSelectionneeId === piece.id}
              editionActive={editionActive}
              onPointerDown={onPiecePointerDown}
            />
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

export default function Plan3DHabitat({
  pieces,
  nomPlan,
  planId,
  piecesVariante,
  afficherComparaison = false,
  configurationServeur,
  sauvegardeServeurEnCours = false,
  onSauvegarderConfigurationServeur,
}: Plan3DHabitatProps) {
  const layoutInitial = useMemo(() => construireLayout(pieces), [pieces]);
  const layoutVariante = useMemo(() => construireLayout(piecesVariante ?? []), [piecesVariante]);
  const [layoutEdition, setLayoutEdition] = useState<PieceLayout[]>(layoutInitial);
  const [editionActive, setEditionActive] = useState(false);
  const [pieceSelectionneeId, setPieceSelectionneeId] = useState<number | undefined>(undefined);
  const [paletteParType, setPaletteParType] = useState<PaletteTypePiece>({});
  const [variantes, setVariantes] = useState<PlanHabitatVariante3D[]>([]);
  const [varianteActiveId, setVarianteActiveId] = useState<string | null>(null);
  const [nomVariante, setNomVariante] = useState("");
  const [modeImport, setModeImport] = useState<ModeImport>("remplacer");
  const [grilleActive, setGrilleActive] = useState(true);
  const [eviterChevauchements, setEviterChevauchements] = useState(true);
  const [messageImportExport, setMessageImportExport] = useState<string | null>(null);
  const [importEnAttente, setImportEnAttente] = useState<ImportNormalise | null>(null);
  const [nomFichierImport, setNomFichierImport] = useState<string | null>(null);
  const [demanderConfirmationImport, setDemanderConfirmationImport] = useState(true);
  const dragRef = useRef<EtatDrag | null>(null);
  const inputImportRef = useRef<HTMLInputElement | null>(null);
  const cleStockage = useMemo(
    () => `vision-maison:plans:3d-edition:${String(planId ?? nomPlan ?? "defaut")}`,
    [planId, nomPlan]
  );
  const clePreferenceConfirmationImport = "vision-maison:plans:3d-import-confirmation";

  useEffect(() => {
    const paletteBase = paletteParDefaut(layoutInitial);
    let layoutCharge = layoutInitial;
    let paletteChargee = paletteBase;
    let variantesChargees: PlanHabitatVariante3D[] = configurationServeur?.variantes ?? [];
    let varianteServeurActive = configurationServeur?.variante_active_id ?? null;

    if (configurationServeur?.configuration_courante) {
      layoutCharge = appliquerLayoutPersisted(layoutInitial, configurationServeur.configuration_courante.layout_edition);
      paletteChargee = {
        ...paletteBase,
        ...configurationServeur.configuration_courante.palette_par_type,
      };
      setVariantes(variantesChargees);
      setVarianteActiveId(varianteServeurActive);
      setLayoutEdition(layoutCharge);
      setPaletteParType(paletteChargee);
      setPieceSelectionneeId(undefined);
      setEditionActive(false);
      return;
    }

    try {
      const raw = window.localStorage.getItem(cleStockage);
      if (raw) {
        const persisted = JSON.parse(raw) as Etat3DPersisted;
        if (Array.isArray(persisted.layoutEdition)) {
          layoutCharge = appliquerLayoutPersisted(layoutInitial, persisted.layoutEdition);
        }
        if (persisted.paletteParType && typeof persisted.paletteParType === "object") {
          paletteChargee = { ...paletteBase, ...persisted.paletteParType };
        }
      }
    } catch {
      layoutCharge = layoutInitial;
      paletteChargee = paletteBase;
    }

    setVariantes(variantesChargees);
    setVarianteActiveId(varianteServeurActive);
    setLayoutEdition(layoutCharge);
    setPaletteParType(paletteChargee);
    setPieceSelectionneeId(undefined);
    setEditionActive(false);
  }, [layoutInitial, cleStockage, configurationServeur]);

  useEffect(() => {
    if (layoutEdition.length === 0) {
      return;
    }

    const payload: Etat3DPersisted = {
      layoutEdition: layoutEdition.map((piece) => ({
        id: piece.id,
        x: piece.x,
        z: piece.z,
        width: piece.width,
        depth: piece.depth,
      })),
      paletteParType,
    };

    try {
      window.localStorage.setItem(cleStockage, JSON.stringify(payload));
    } catch {
      // Ignore storage quota errors; editing still works in-memory.
    }
  }, [layoutEdition, paletteParType, cleStockage]);

  useEffect(() => {
    try {
      const brute = window.localStorage.getItem(clePreferenceConfirmationImport);
      if (brute === "false") {
        setDemanderConfirmationImport(false);
      }
    } catch {
      setDemanderConfirmationImport(true);
    }
  }, []);

  useEffect(() => {
    try {
      window.localStorage.setItem(clePreferenceConfirmationImport, String(demanderConfirmationImport));
    } catch {
      // noop
    }
  }, [demanderConfirmationImport]);

  if (layoutEdition.length === 0) {
    return (
      <div className="flex h-[420px] items-center justify-center rounded-xl border border-dashed text-sm text-muted-foreground">
        Ajoutez des surfaces de pieces pour activer la visualisation 3D.
      </div>
    );
  }

  const pieceSelectionnee = layoutEdition.find((piece) => piece.id === pieceSelectionneeId);

  async function sauvegarderServeur(
    prochaineConfiguration = construireConfigurationCourante(layoutEdition, paletteParType),
    prochainesVariantes = variantes,
    prochaineVarianteActiveId = varianteActiveId
  ) {
    if (!planId || !onSauvegarderConfigurationServeur) {
      return;
    }

    try {
      await Promise.resolve(
        onSauvegarderConfigurationServeur({
          configuration_courante: prochaineConfiguration,
          variantes: prochainesVariantes,
          variante_active_id: prochaineVarianteActiveId,
        })
      );
      setMessageImportExport("Configuration 3D sauvegardee sur le serveur.");
    } catch {
      setMessageImportExport("Sauvegarde serveur impossible pour le moment.");
    }
  }

  function appliquerConfigurationLocale(configuration: PlanHabitatConfiguration3D, mode: ModeImport) {
    const prochainLayout = appliquerConfiguration3D(layoutInitial, configuration, mode, layoutEdition);
    const paletteBase = paletteParDefaut(layoutInitial);
    const prochainePalette =
      mode === "palette"
        ? { ...paletteParType, ...configuration.palette_par_type }
        : { ...paletteBase, ...paletteParType, ...configuration.palette_par_type };

    setLayoutEdition(prochainLayout);
    setPaletteParType(prochainePalette);
    setPieceSelectionneeId(undefined);
    setEditionActive(false);
    arreterDrag();

    return {
      prochainLayout,
      prochainePalette,
      prochaineConfiguration: construireConfigurationCourante(prochainLayout, prochainePalette),
    };
  }

  function lancerDrag(piece: PieceLayout, pointX: number, pointZ: number) {
    if (!editionActive) {
      return;
    }
    setPieceSelectionneeId(piece.id);
    dragRef.current = {
      id: piece.id,
      offsetX: piece.x - pointX,
      offsetZ: piece.z - pointZ,
    };
  }

  function deplacerPiece(pointX: number, pointZ: number) {
    const drag = dragRef.current;
    if (!drag || !editionActive) {
      return;
    }
    setLayoutEdition((precedent) =>
      precedent.map((piece) => {
        if (piece.id !== drag.id) {
          return piece;
        }

        let prochainX = Math.max(0.8, pointX + drag.offsetX);
        let prochainZ = Math.max(0.8, pointZ + drag.offsetZ);
        if (grilleActive) {
          prochainX = arrondirSurGrille(prochainX);
          prochainZ = arrondirSurGrille(prochainZ);
        }
        if (eviterChevauchements && detecterChevauchement(precedent, piece.id, prochainX, prochainZ)) {
          return piece;
        }

        return {
          ...piece,
          x: prochainX,
          z: prochainZ,
        };
      })
    );
  }

  function arreterDrag() {
    dragRef.current = null;
  }

  function ajusterDimension(cle: "width" | "depth", delta: number) {
    if (!pieceSelectionneeId) {
      return;
    }
    setLayoutEdition((precedent) =>
      precedent.map((piece) => {
        if (piece.id !== pieceSelectionneeId) {
          return piece;
        }
        return {
          ...piece,
          [cle]: Math.max(1.8, Math.min(12, piece[cle] + delta)),
        };
      })
    );
  }

  function exporterConfiguration() {
    const payload = {
      version: 1,
      plan_id: planId ?? null,
      nom_plan: nomPlan ?? null,
      exporte_le: new Date().toISOString(),
      configuration_courante: construireConfigurationCourante(layoutEdition, paletteParType),
      variantes,
      variante_active_id: varianteActiveId,
      layoutEdition: layoutEdition.map((piece) => ({
        id: piece.id,
        x: piece.x,
        z: piece.z,
        width: piece.width,
        depth: piece.depth,
      })),
      paletteParType,
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = window.URL.createObjectURL(blob);
    const lien = document.createElement("a");
    const suffixe = String(planId ?? nomPlan ?? "plan").replace(/[^a-zA-Z0-9_-]/g, "_");
    lien.href = url;
    lien.download = `plan_3d_${suffixe}.json`;
    document.body.appendChild(lien);
    lien.click();
    lien.remove();
    window.URL.revokeObjectURL(url);
    setMessageImportExport("Configuration exportee en JSON.");
  }

  async function appliquerConfigurationImportee(configurationImportee: ImportNormalise, mode = modeImport) {
    const { configurationCourante, variantes: variantesImportees, planIdSource, varianteActiveId: varianteImporteeActiveId } = configurationImportee;
    const compatibilite = calculerCompatibiliteImport(layoutInitial, configurationCourante.layout_edition);
    const { prochaineConfiguration } = appliquerConfigurationLocale(configurationCourante, mode);
    const prochainesVariantes = mode === "palette" ? variantes : fusionnerVariantes(variantes, variantesImportees);
    const prochaineVarianteActiveId =
      mode === "palette"
        ? varianteActiveId
        : prochaineConfiguration.layout_edition.length > 0
          ? varianteImporteeActiveId ?? varianteActiveId
          : varianteActiveId;

    setVariantes(prochainesVariantes);
    setVarianteActiveId(prochaineVarianteActiveId);

    const importAutrePlan = typeof planIdSource === "number" && typeof planId === "number" && planIdSource !== planId;
    const resumeCompat = ` (${compatibilite.appliquees}/${compatibilite.totalImportees} piece(s) appliquee(s))`;
    if (importAutrePlan) {
      setMessageImportExport(`Configuration importee depuis un autre plan: verifiez l'alignement des pieces.${resumeCompat}`);
    } else {
      if (compatibilite.ignorees > 0) {
        setMessageImportExport(`Configuration importee partiellement: ${compatibilite.appliquees}/${compatibilite.totalImportees} piece(s) appliquee(s).`);
      } else {
        setMessageImportExport(`Configuration importee.${resumeCompat}`);
      }
    }

    await sauvegarderServeur(prochaineConfiguration, prochainesVariantes, prochaineVarianteActiveId);
  }

  async function importerConfiguration(event: ChangeEvent<HTMLInputElement>) {
    const fichier = event.target.files?.[0];
    if (!fichier) {
      return;
    }

    try {
      const contenu = await fichier.text();
      const dataBrute = JSON.parse(contenu);
      const parsed = schemaConfigurationImport.safeParse(dataBrute);
      if (!parsed.success) {
        throw new Error("schema invalide");
      }
      const configurationNormalisee = normaliserConfigurationImportee(parsed.data);

      if (demanderConfirmationImport) {
        setImportEnAttente(configurationNormalisee);
        setNomFichierImport(fichier.name);
        setMessageImportExport("Configuration lue: confirmez l'import.");
      } else {
        await appliquerConfigurationImportee(configurationNormalisee);
        setImportEnAttente(null);
        setNomFichierImport(null);
      }
    } catch {
      setImportEnAttente(null);
      setNomFichierImport(null);
      setMessageImportExport("Import impossible: fichier JSON invalide.");
    } finally {
      event.target.value = "";
    }
  }

  const afficherVariante = afficherComparaison && layoutVariante.length > 0;
  const compatibiliteImport = importEnAttente
    ? calculerCompatibiliteImport(layoutInitial, importEnAttente.configurationCourante.layout_edition)
    : null;

  async function enregistrerVarianteCourante() {
    const nom = nomVariante.trim();
    if (!nom) {
      setMessageImportExport("Renseignez un nom de variante avant l'enregistrement.");
      return;
    }

    const nouvelleVariante: PlanHabitatVariante3D = {
      id: genererIdVariante(),
      nom,
      source: "manuel",
      configuration: construireConfigurationCourante(layoutEdition, paletteParType),
    };
    const prochainesVariantes = fusionnerVariantes(variantes, [nouvelleVariante]);
    setVariantes(prochainesVariantes);
    setVarianteActiveId(nouvelleVariante.id);
    setNomVariante("");
    setMessageImportExport(`Variante "${nom}" enregistree.`);
    await sauvegarderServeur(nouvelleVariante.configuration, prochainesVariantes, nouvelleVariante.id);
  }

  async function appliquerVarianteSelectionnee(id: string) {
    const variante = variantes.find((item) => item.id === id);
    if (!variante) {
      return;
    }
    const { prochaineConfiguration } = appliquerConfigurationLocale(variante.configuration, "remplacer");
    setVarianteActiveId(id);
    setMessageImportExport(`Variante "${variante.nom}" appliquee.`);
    await sauvegarderServeur(prochaineConfiguration, variantes, id);
  }

  async function supprimerVarianteSelectionnee(id: string) {
    const prochainesVariantes = variantes.filter((item) => item.id !== id);
    const prochaineVarianteActiveId = varianteActiveId === id ? null : varianteActiveId;
    setVariantes(prochainesVariantes);
    setVarianteActiveId(prochaineVarianteActiveId);
    setMessageImportExport("Variante supprimee.");
    await sauvegarderServeur(
      construireConfigurationCourante(layoutEdition, paletteParType),
      prochainesVariantes,
      prochaineVarianteActiveId
    );
  }

  return (
    <div className="space-y-3">
      {nomPlan && (
        <p className="text-xs text-muted-foreground">
          Plan actif: <span className="font-medium text-foreground">{nomPlan}</span>
        </p>
      )}

      <div className="rounded-xl border bg-white p-3">
        <div className="flex flex-wrap items-center gap-2">
          <Button
            type="button"
            size="sm"
            variant={editionActive ? "default" : "outline"}
            onClick={() => {
              setEditionActive((precedent) => !precedent);
              if (editionActive) {
                arreterDrag();
              }
            }}
          >
            {editionActive ? "Edition active" : "Activer edition"}
          </Button>
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => {
              setLayoutEdition(layoutInitial);
              setPieceSelectionneeId(undefined);
              arreterDrag();
            }}
          >
            Reinitialiser layout
          </Button>
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={exporterConfiguration}
          >
            Exporter JSON
          </Button>
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => inputImportRef.current?.click()}
          >
            Importer JSON
          </Button>
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => {
              const paletteBase = paletteParDefaut(layoutInitial);
              setLayoutEdition(layoutInitial);
              setPaletteParType(paletteBase);
              setPieceSelectionneeId(undefined);
              setEditionActive(false);
              setImportEnAttente(null);
              setNomFichierImport(null);
              arreterDrag();
              try {
                window.localStorage.removeItem(cleStockage);
              } catch {
                // noop
              }
            }}
          >
            Effacer sauvegarde
          </Button>
          <Button
            type="button"
            size="sm"
            variant="outline"
            disabled={!onSauvegarderConfigurationServeur || sauvegardeServeurEnCours}
            onClick={() => void sauvegarderServeur()}
          >
            {sauvegardeServeurEnCours ? "Sauvegarde..." : "Sauvegarder serveur"}
          </Button>
          <input
            ref={inputImportRef}
            type="file"
            accept="application/json"
            title="Importer une configuration 3D"
            aria-label="Importer une configuration 3D"
            className="hidden"
            onChange={importerConfiguration}
          />
          {pieceSelectionnee && (
            <>
              <span className="text-xs text-muted-foreground">Piece: {pieceSelectionnee.nom}</span>
              <Button type="button" size="sm" variant="outline" onClick={() => ajusterDimension("width", -0.25)}>
                Largeur -
              </Button>
              <Button type="button" size="sm" variant="outline" onClick={() => ajusterDimension("width", 0.25)}>
                Largeur +
              </Button>
              <Button type="button" size="sm" variant="outline" onClick={() => ajusterDimension("depth", -0.25)}>
                Profondeur -
              </Button>
              <Button type="button" size="sm" variant="outline" onClick={() => ajusterDimension("depth", 0.25)}>
                Profondeur +
              </Button>
            </>
          )}
        </div>

        <div className="mt-3 grid gap-3 rounded-lg border border-dashed p-3 md:grid-cols-[1fr_auto]">
          <div className="space-y-2">
            <p className="text-xs font-medium text-foreground">Variantes nommees</p>
            <div className="flex flex-wrap gap-2">
              <Input
                value={nomVariante}
                onChange={(event) => setNomVariante(event.target.value)}
                placeholder="Ex: Variante rangements"
                className="h-8 max-w-xs"
              />
              <Button type="button" size="sm" variant="outline" onClick={() => void enregistrerVarianteCourante()}>
                Enregistrer variante
              </Button>
            </div>
            {variantes.length > 0 ? (
              <div className="flex flex-wrap items-center gap-2">
                <select
                  aria-label="Selectionner une variante 3D"
                  title="Selectionner une variante 3D"
                  value={varianteActiveId ?? ""}
                  onChange={(event) => {
                    const id = event.target.value;
                    if (id) {
                      void appliquerVarianteSelectionnee(id);
                    }
                  }}
                  className="h-8 min-w-56 rounded-md border bg-background px-2 text-xs"
                >
                  <option value="">Selectionner une variante</option>
                  {variantes.map((variante) => (
                    <option key={variante.id} value={variante.id}>
                      {variante.nom} · {variante.source}
                    </option>
                  ))}
                </select>
                {varianteActiveId && (
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => void supprimerVarianteSelectionnee(varianteActiveId)}
                  >
                    Supprimer variante active
                  </Button>
                )}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">Aucune variante nommee enregistree pour ce plan.</p>
            )}
          </div>
          <div className="space-y-2 text-xs text-muted-foreground">
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={grilleActive} onChange={(event) => setGrilleActive(event.target.checked)} />
              Snap sur grille 25 cm
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={eviterChevauchements}
                onChange={(event) => setEviterChevauchements(event.target.checked)}
              />
              Bloquer les chevauchements simples
            </label>
          </div>
        </div>

        <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {Object.entries(paletteParType).map(([type, couleur]) => (
            <label key={type} className="flex items-center justify-between rounded-md border px-2 py-1.5 text-xs">
              <span className="truncate pr-2">{type}</span>
              <input
                type="color"
                value={couleur}
                onChange={(event) =>
                  setPaletteParType((precedente) => ({
                    ...precedente,
                    [type]: event.target.value,
                  }))
                }
                className="h-7 w-9 cursor-pointer rounded border"
              />
            </label>
          ))}
        </div>

        <label className="mt-3 inline-flex items-center gap-2 text-xs text-muted-foreground">
          <input
            type="checkbox"
            checked={demanderConfirmationImport}
            onChange={(event) => setDemanderConfirmationImport(event.target.checked)}
          />
          Toujours demander confirmation avant import JSON
        </label>
        {!demanderConfirmationImport && (
          <div className="mt-2">
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={() => {
                setDemanderConfirmationImport(true);
                setMessageImportExport("Confirmation avant import reactivee.");
              }}
            >
              Reactiver confirmation
            </Button>
          </div>
        )}
      </div>

      {importEnAttente && (
        <div className="rounded-xl border border-amber-300 bg-amber-50/70 p-3 text-xs">
          <p className="font-medium text-amber-900">Apercu import JSON</p>
          <p className="mt-1 text-amber-900/90">Fichier: {nomFichierImport ?? "(inconnu)"}</p>
          <p className="text-amber-900/90">Plan source: {importEnAttente.nomPlanSource ?? "(non renseigne)"}</p>
          <p className="text-amber-900/90">ID source: {String(importEnAttente.planIdSource ?? "-")}</p>
          <p className="text-amber-900/90">Pieces importees: {importEnAttente.configurationCourante.layout_edition.length}</p>
          <p className="text-amber-900/90">
            Compatibilite locale: {compatibiliteImport?.appliquees ?? 0}/{importEnAttente.configurationCourante.layout_edition.length} piece(s) correspondante(s)
          </p>
          <p className="text-amber-900/90">Palette types: {Object.keys(importEnAttente.configurationCourante.palette_par_type).length}</p>
          <p className="text-amber-900/90">Variantes incluses: {importEnAttente.variantes.length}</p>
          <div className="mt-2 flex flex-wrap gap-3 text-amber-900/90">
            <label className="flex items-center gap-1">
              <input
                type="radio"
                name="mode-import-3d"
                checked={modeImport === "remplacer"}
                onChange={() => setModeImport("remplacer")}
              />
              Remplacer
            </label>
            <label className="flex items-center gap-1">
              <input
                type="radio"
                name="mode-import-3d"
                checked={modeImport === "fusionner"}
                onChange={() => setModeImport("fusionner")}
              />
              Fusionner
            </label>
            <label className="flex items-center gap-1">
              <input
                type="radio"
                name="mode-import-3d"
                checked={modeImport === "palette"}
                onChange={() => setModeImport("palette")}
              />
              Palette seule
            </label>
          </div>
          <div className="mt-2 flex gap-2">
            <Button
              type="button"
              size="sm"
              onClick={() => {
                void appliquerConfigurationImportee(importEnAttente, modeImport);
                setImportEnAttente(null);
                setNomFichierImport(null);
              }}
            >
              Confirmer import
            </Button>
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={() => {
                setImportEnAttente(null);
                setNomFichierImport(null);
                setMessageImportExport("Import annule.");
              }}
            >
              Annuler
            </Button>
          </div>
        </div>
      )}

      {editionActive && (
        <p className="text-xs text-muted-foreground">
          Edition: cliquez une piece puis glissez-la sur le plan. Utilisez les boutons pour ajuster largeur/profondeur.
        </p>
      )}
      <p className="text-xs text-muted-foreground">Sauvegarde locale automatique active pour ce plan.</p>
      {messageImportExport && <p className="text-xs text-muted-foreground">{messageImportExport}</p>}

      {afficherVariante ? (
        <div className="grid gap-4 xl:grid-cols-2">
          <Vue3DPlan
            titre="Plan actuel"
            layout={layoutEdition}
            palette={paletteParType}
            editionActive={editionActive}
            pieceSelectionneeId={pieceSelectionneeId}
            onPiecePointerDown={lancerDrag}
            onGroundPointerMove={deplacerPiece}
            onGroundPointerUp={arreterDrag}
          />
          <Vue3DPlan
            titre="Variante IA"
            layout={layoutVariante}
            palette={paletteParType}
            editionActive={false}
          />
        </div>
      ) : (
        <Vue3DPlan
          layout={layoutEdition}
          palette={paletteParType}
          editionActive={editionActive}
          pieceSelectionneeId={pieceSelectionneeId}
          onPiecePointerDown={lancerDrag}
          onGroundPointerMove={deplacerPiece}
          onGroundPointerUp={arreterDrag}
        />
      )}
    </div>
  );
}
