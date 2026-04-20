"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import dynamic from "next/dynamic";
import { Box, Map, Sparkles, SquareDashedMousePointer } from "lucide-react";
import {
  analyserPlanHabitat,
  chargerCanvasHabitat,
  historiquePlanHabitat,
  listerZonesJardinHabitat,
  listerPiecesHabitat,
  listerPlansHabitat,
  obtenirResumeJardinHabitat,
  obtenirConfiguration3DHabitat,
  sauvegarderConfiguration3DHabitat,
} from "@/bibliotheque/api/habitat";
import { EntetePageHabitat } from "@/composants/habitat/entete-page-habitat";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { Textarea } from "@/composants/ui/textarea";
import { utiliserMutationAvecInvalidation, utiliserRequete } from "@/crochets/utiliser-api";
import type { CanvasData } from "@/types/maison";
import type { PieceHabitat, PlanHabitatConfiguration3D, PlanHabitatConfiguration3DServeur } from "@/types/habitat";

const Plan3DHabitat = dynamic(() => import("@/composants/habitat/plan-3d-habitat"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[420px] items-center justify-center rounded-xl border text-sm text-muted-foreground">
      Chargement de la vue 3D...
    </div>
  ),
});

const EditeurPlan2DHabitat = dynamic(() => import("@/composants/habitat/editeur-plan-2d-habitat"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[420px] items-center justify-center rounded-xl border text-sm text-muted-foreground">
      Chargement de l'éditeur 2D...
    </div>
  ),
});

function borne(valeur: number, minimum: number, maximum: number) {
  return Math.min(Math.max(valeur, minimum), maximum);
}

function extraireEmpreinteCanvas(canvas: CanvasData | null) {
  if (!canvas) {
    return null;
  }
  const points: Array<{ x: number; y: number }> = [];
  for (const mur of canvas.murs ?? []) {
    points.push({ x: mur.x1, y: mur.y1 }, { x: mur.x2, y: mur.y2 });
  }
  for (const porte of canvas.portes ?? []) {
    points.push({ x: porte.x, y: porte.y }, { x: porte.x + porte.largeur, y: porte.y + porte.hauteur });
  }
  for (const fenetre of canvas.fenetres ?? []) {
    points.push({ x: fenetre.x, y: fenetre.y }, { x: fenetre.x + fenetre.largeur, y: fenetre.y + fenetre.hauteur });
  }
  for (const meuble of canvas.meubles ?? []) {
    points.push({ x: meuble.x, y: meuble.y }, { x: meuble.x + meuble.largeur, y: meuble.y + meuble.hauteur });
  }
  for (const annotation of canvas.annotations ?? []) {
    points.push({ x: annotation.x, y: annotation.y });
  }
  if (points.length === 0) {
    return null;
  }
  const xs = points.map((point) => point.x);
  const ys = points.map((point) => point.y);
  return {
    minX: Math.min(...xs),
    maxX: Math.max(...xs),
    minY: Math.min(...ys),
    maxY: Math.max(...ys),
  };
}

function trouverReperePiece(piece: PieceHabitat, canvas: CanvasData) {
  const cible = `${piece.nom} ${piece.type_piece ?? ""}`.toLowerCase();
  const annotation = (canvas.annotations ?? []).find((item) => {
    const texte = (item.texte ?? "").toLowerCase();
    return texte.includes(piece.nom.toLowerCase()) || (piece.type_piece ? texte.includes(piece.type_piece.toLowerCase()) : false) || texte.includes(cible.trim());
  });
  if (annotation) {
    return { x: annotation.x, y: annotation.y };
  }
  const meuble = (canvas.meubles ?? []).find((item) => {
    const texte = `${item.nom} ${item.type}`.toLowerCase();
    return texte.includes(piece.nom.toLowerCase()) || (piece.type_piece ? texte.includes(piece.type_piece.toLowerCase()) : false);
  });
  if (meuble) {
    return { x: meuble.x + meuble.largeur / 2, y: meuble.y + meuble.hauteur / 2 };
  }
  return null;
}

function construireConfigurationDepuisCanvas(
  pieces: PieceHabitat[],
  canvas: CanvasData,
  configurationServeur: PlanHabitatConfiguration3DServeur | null | undefined
): PlanHabitatConfiguration3D {
  const empreinte = extraireEmpreinteCanvas(canvas);
  if (pieces.length === 0) {
    return configurationServeur?.configuration_courante ?? { layout_edition: [], palette_par_type: {} };
  }
  const largeurReference = Math.max((empreinte?.maxX ?? 1200) - (empreinte?.minX ?? 0), 1);
  const hauteurReference = Math.max((empreinte?.maxY ?? 800) - (empreinte?.minY ?? 0), 1);
  const largeurMetres = Math.max(8, largeurReference / 80);
  const profondeurMetres = Math.max(6, hauteurReference / 80);
  const configurationCourante = configurationServeur?.configuration_courante;
  const precedents = new Map((configurationCourante?.layout_edition ?? []).map((item) => [item.id, item]));

  const layout = pieces.map((piece, index) => {
    const surface = Number(piece.surface_m2 ?? 12);
    const largeur = borne(precedents.get(piece.id)?.width ?? Math.sqrt(surface) * 1.1, 2.4, Math.max(3.2, largeurMetres * 0.45));
    const depth = borne(precedents.get(piece.id)?.depth ?? surface / largeur, 2.2, Math.max(3, profondeurMetres * 0.45));
    const repere = trouverReperePiece(piece, canvas);
    const fallbackColonne = index % 3;
    const fallbackLigne = Math.floor(index / 3);
    const x = repere
      ? borne(((repere.x - (empreinte?.minX ?? 0)) / largeurReference) * largeurMetres, largeur / 2, largeurMetres - largeur / 2)
      : borne((fallbackColonne + 0.7) * (largeurMetres / 3), largeur / 2, largeurMetres - largeur / 2);
    const z = repere
      ? borne(((repere.y - (empreinte?.minY ?? 0)) / hauteurReference) * profondeurMetres, depth / 2, profondeurMetres - depth / 2)
      : borne((fallbackLigne + 0.8) * 2.8, depth / 2, profondeurMetres - depth / 2);
    return {
      id: piece.id,
      x,
      z,
      width: largeur,
      depth,
      nom: piece.nom,
      type_piece: piece.type_piece,
    };
  });

  return {
    layout_edition: layout,
    palette_par_type: configurationCourante?.palette_par_type ?? {},
  };
}

export default function PlansHabitatPage() {
  const [planSelectionne, setPlanSelectionne] = useState<number | null>(null);
  const [afficherComparaisonIA, setAfficherComparaisonIA] = useState(false);
  const [prompt, setPrompt] = useState("Optimiser la circulation, les rangements et le cout travaux.");
  const [canvasActif, setCanvasActif] = useState<CanvasData | null>(null);
  const { data: plans } = utiliserRequete(["habitat", "plans"], listerPlansHabitat);
  const planActif = (plans ?? []).find((plan) => plan.id === planSelectionne) ?? (plans ?? [])[0] ?? null;
  const { data: canvasPlan } = utiliserRequete(
    ["habitat", "plans", String(planActif?.id ?? "aucun"), "canvas"],
    () => chargerCanvasHabitat(planActif?.id ?? 0),
    { enabled: Boolean(planActif?.id) }
  );
  const { data: historique } = utiliserRequete(
    ["habitat", "plans", String(planActif?.id ?? "aucun"), "historique"],
    () => historiquePlanHabitat(planActif?.id ?? 0),
    { enabled: Boolean(planActif?.id) }
  );
  const { data: piecesPlanActif } = utiliserRequete(
    ["habitat", "plans", String(planActif?.id ?? "aucun"), "pieces"],
    () => listerPiecesHabitat(planActif?.id ?? 0),
    { enabled: Boolean(planActif?.id) }
  );
  const { data: configuration3D } = utiliserRequete(
    ["habitat", "plans", String(planActif?.id ?? "aucun"), "configuration-3d"],
    () => obtenirConfiguration3DHabitat(planActif?.id ?? 0),
    { enabled: Boolean(planActif?.id) }
  );
  const { data: zonesJardin } = utiliserRequete(
    ["habitat", "plans", String(planActif?.id ?? "aucun"), "zones-jardin"],
    () => listerZonesJardinHabitat(planActif?.id ?? 0),
    { enabled: Boolean(planActif?.id) }
  );
  const { data: resumeJardin } = utiliserRequete(
    ["habitat", "plans", String(planActif?.id ?? "aucun"), "resume-jardin"],
    () => obtenirResumeJardinHabitat(planActif?.id ?? 0),
    { enabled: Boolean(planActif?.id) }
  );

  const analyseMutation = utiliserMutationAvecInvalidation(
    ({ planId, generer_image }: { planId: number; generer_image: boolean }) =>
      analyserPlanHabitat(planId, { prompt_utilisateur: prompt, generer_image }),
    [["habitat", "plans"], ["habitat", "plans", String(planActif?.id ?? "aucun"), "historique"]]
  );
  const sauvegardeConfigurationMutation = utiliserMutationAvecInvalidation(
    ({ planId, payload }: { planId: number; payload: Omit<PlanHabitatConfiguration3DServeur, "plan_id"> }) =>
      sauvegarderConfiguration3DHabitat(planId, payload),
    [["habitat", "plans", String(planActif?.id ?? "aucun"), "configuration-3d"]]
  );

  const piecesVarianteIA = useMemo(
    () =>
      (analyseMutation.data?.analyse.suggestions_pieces ?? []).map((suggestion, index) => ({
        id: -(index + 1),
        plan_id: planActif?.id ?? 0,
        nom: suggestion.nom,
        type_piece: suggestion.type_piece,
        surface_m2: suggestion.surface_m2,
      })),
    [analyseMutation.data?.analyse.suggestions_pieces, planActif?.id]
  );
  const canvasTechnique = canvasActif ?? canvasPlan?.donnees_canvas ?? null;
  const syntheseCanvas = useMemo(() => {
    const canvas = canvasTechnique;
    if (!canvas) {
      return { murs: 0, porteurs: 0, ouvertures: 0, annotations: 0 };
    }
    return {
      murs: canvas.murs?.length ?? 0,
      porteurs: (canvas.murs ?? []).filter((mur) => mur.porteur).length,
      ouvertures: (canvas.portes?.length ?? 0) + (canvas.fenetres?.length ?? 0),
      annotations: canvas.annotations?.length ?? 0,
    };
  }, [canvasTechnique]);

  return (
    <div className="space-y-6">
      <EntetePageHabitat
        badge="H6 • Plans IA"
        titre="Plans"
        description="Analyse des plans, lecture des risques et memorisation des variantes pour converger vers un schema exploitable avant travaux ou amenagement." 
        stats={[
          { label: "Plans", valeur: `${plans?.length ?? 0}` },
          { label: "Historique", valeur: `${historique?.length ?? 0}` },
          { label: "Plan actif", valeur: planActif?.nom ?? "-" },
        ]}
      />

      <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Plans enregistres</CardTitle>
            <CardDescription>Sélectionne un plan puis déclenche une analyse.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {(plans ?? []).map((plan) => {
              const actif = planActif?.id === plan.id;
              return (
                <button
                  key={plan.id}
                  type="button"
                  onClick={() => setPlanSelectionne(plan.id)}
                  className={`w-full rounded-xl border p-3 text-left transition-colors ${actif ? "border-emerald-500 bg-emerald-50" : "hover:bg-accent/40"}`}
                >
                  <p className="font-medium">{plan.nom}</p>
                  <p className="text-xs text-muted-foreground">
                    {plan.type_plan} · v{plan.version} · {plan.surface_totale_m2 ?? "?"} m2
                  </p>
                  {plan.suggestions_ia && plan.suggestions_ia.length > 0 && (
                    <p className="mt-2 text-xs text-muted-foreground">
                      {plan.suggestions_ia.length} suggestion(s) IA déjà stockée(s)
                    </p>
                  )}
                </button>
              );
            })}
            {(plans ?? []).length === 0 && <p className="text-sm text-muted-foreground">Aucun plan disponible.</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Analyse IA</CardTitle>
            <CardDescription>Mistral pour le diagnostic + visualisation 3D instantanee du plan actif.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Tabs defaultValue="plan-2d" className="w-full">
              <TabsList variant="line" className="w-full justify-start">
                <TabsTrigger value="plan-2d" className="gap-1.5">
                  <SquareDashedMousePointer className="h-4 w-4" /> Vue 2D
                </TabsTrigger>
                <TabsTrigger value="analyse" className="gap-1.5">
                  <Sparkles className="h-4 w-4" /> Analyse IA
                </TabsTrigger>
                <TabsTrigger value="visualisation" className="gap-1.5">
                  <Box className="h-4 w-4" /> Vue 3D
                </TabsTrigger>
              </TabsList>

              <TabsContent value="plan-2d" className="space-y-4 pt-3">
                {!planActif ? (
                  <div className="flex h-[420px] items-center justify-center rounded-xl border border-dashed text-sm text-muted-foreground">
                    Selectionnez un plan pour ouvrir l'éditeur 2D.
                  </div>
                ) : (
                  <div className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
                    <EditeurPlan2DHabitat
                      planId={planActif.id}
                      onSave={(donnees) => setCanvasActif(donnees)}
                      onSynchroniser3D={async (donnees) => {
                        const configurationCourante = construireConfigurationDepuisCanvas(
                          piecesPlanActif ?? [],
                          donnees,
                          configuration3D
                        );
                        await sauvegardeConfigurationMutation.mutateAsync({
                          planId: planActif.id,
                          payload: {
                            configuration_courante: configurationCourante,
                            variantes: configuration3D?.variantes ?? [],
                            variante_active_id: configuration3D?.variante_active_id ?? null,
                          },
                        });
                      }}
                    />

                    <div className="space-y-4">
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base">Synthèse technique</CardTitle>
                          <CardDescription>Le canvas 2D alimente la faisabilité et prépare la projection 3D.</CardDescription>
                        </CardHeader>
                        <CardContent className="grid gap-3 sm:grid-cols-2">
                          <div className="rounded-xl border p-3">
                            <p className="text-xs uppercase tracking-wide text-muted-foreground">Murs</p>
                            <p className="mt-2 text-2xl font-semibold">{syntheseCanvas.murs}</p>
                          </div>
                          <div className="rounded-xl border p-3">
                            <p className="text-xs uppercase tracking-wide text-muted-foreground">Murs porteurs</p>
                            <p className="mt-2 text-2xl font-semibold">{syntheseCanvas.porteurs}</p>
                          </div>
                          <div className="rounded-xl border p-3">
                            <p className="text-xs uppercase tracking-wide text-muted-foreground">Ouvertures</p>
                            <p className="mt-2 text-2xl font-semibold">{syntheseCanvas.ouvertures}</p>
                          </div>
                          <div className="rounded-xl border p-3">
                            <p className="text-xs uppercase tracking-wide text-muted-foreground">Repères</p>
                            <p className="mt-2 text-2xl font-semibold">{syntheseCanvas.annotations}</p>
                          </div>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2 text-base">
                            <Map className="h-4 w-4" /> Terrain et jardin liés
                          </CardTitle>
                          <CardDescription>Phase 3 unifiée dans le même workspace Vision Maison.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-3">
                          <div className="grid gap-3 sm:grid-cols-2">
                            <div className="rounded-xl border p-3">
                              <p className="text-xs uppercase tracking-wide text-muted-foreground">Zones</p>
                              <p className="mt-2 text-2xl font-semibold">{zonesJardin?.length ?? 0}</p>
                            </div>
                            <div className="rounded-xl border p-3">
                              <p className="text-xs uppercase tracking-wide text-muted-foreground">Budget jardin</p>
                              <p className="mt-2 text-2xl font-semibold">{Math.round(resumeJardin?.budget_estime ?? 0)} €</p>
                            </div>
                          </div>
                          {(zonesJardin ?? []).length > 0 ? (
                            <div className="space-y-2">
                              {(zonesJardin ?? []).slice(0, 4).map((zone) => (
                                <div key={zone.id} className="rounded-lg border px-3 py-2 text-sm">
                                  <p className="font-medium">{zone.nom}</p>
                                  <p className="text-muted-foreground">{zone.type_zone ?? "Zone"} · {zone.surface_m2 ?? "?"} m2</p>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-sm text-muted-foreground">Aucune zone terrain liée à ce plan pour le moment.</p>
                          )}
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="analyse" className="space-y-4 pt-3">
                <Textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} rows={4} />
                <div className="flex gap-2">
                  <Button
                    disabled={!planActif || analyseMutation.isPending}
                    onClick={() => planActif && analyseMutation.mutate({ planId: planActif.id, generer_image: false })}
                  >
                    {analyseMutation.isPending ? "Analyse..." : "Analyser"}
                  </Button>
                  <Button
                    variant="outline"
                    disabled={!planActif || analyseMutation.isPending}
                    onClick={() => planActif && analyseMutation.mutate({ planId: planActif.id, generer_image: true })}
                  >
                    Analyse + image
                  </Button>
                </div>

                {analyseMutation.data && (
                  <div className="rounded-xl border p-4">
                    <p className="font-medium">{analyseMutation.data.analyse.resume}</p>
                    <div className="mt-3 grid gap-3 md:grid-cols-2">
                      <div>
                        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Points forts</p>
                        <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                          {analyseMutation.data.analyse.points_forts.map((item) => <li key={item}>• {item}</li>)}
                        </ul>
                      </div>
                      <div>
                        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Risques</p>
                        <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                          {analyseMutation.data.analyse.risques.map((item) => <li key={item}>• {item}</li>)}
                        </ul>
                      </div>
                    </div>
                    {analyseMutation.data.analyse.faisabilite && (
                      <div className="mt-4 space-y-4 rounded-xl border border-dashed p-4">
                        <div>
                          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Faisabilité par domaine</p>
                          <p className="mt-2 text-sm text-muted-foreground">{analyseMutation.data.analyse.faisabilite.synthese}</p>
                        </div>
                        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                          {Object.entries(analyseMutation.data.analyse.faisabilite.domaines).map(([nom, valeur]) => (
                            <div key={nom} className="rounded-xl border p-3">
                              <div className="flex items-start justify-between gap-2">
                                <p className="font-medium capitalize">{nom}</p>
                                <span className="rounded-full bg-muted px-2 py-0.5 text-xs">{valeur.score.toFixed(1)}/10</span>
                              </div>
                              <p className="mt-2 text-sm text-muted-foreground">{valeur.verdict}</p>
                              <p className="mt-3 text-xs uppercase tracking-wide text-muted-foreground">Points de vigilance</p>
                              <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                                {valeur.points_vigilance.map((item) => <li key={item}>• {item}</li>)}
                              </ul>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {analyseMutation.data.image?.image_base64 && (
                      <Image
                        src={analyseMutation.data.image.image_base64}
                        alt="Variante visuelle du plan"
                        width={1200}
                        height={800}
                        unoptimized
                        className="mt-4 rounded-xl border"
                      />
                    )}
                  </div>
                )}
              </TabsContent>

              <TabsContent value="visualisation" className="space-y-3 pt-3">
                {!planActif ? (
                  <div className="flex h-[420px] items-center justify-center rounded-xl border border-dashed text-sm text-muted-foreground">
                    Selectionnez un plan pour ouvrir la visualisation 3D.
                  </div>
                ) : (
                  <>
                    {piecesVarianteIA.length > 0 && (
                      <div className="flex items-center gap-2 rounded-lg border px-3 py-2 text-xs text-muted-foreground">
                        <span>{piecesVarianteIA.length} piece(s) proposee(s) par l'analyse IA.</span>
                        <Button
                          type="button"
                          size="sm"
                          variant={afficherComparaisonIA ? "default" : "outline"}
                          onClick={() => setAfficherComparaisonIA((precedent) => !precedent)}
                        >
                          {afficherComparaisonIA ? "Masquer comparaison" : "Comparer avec variante IA"}
                        </Button>
                      </div>
                    )}
                    <Plan3DHabitat
                      pieces={piecesPlanActif ?? []}
                      nomPlan={planActif.nom}
                      planId={planActif.id}
                      piecesVariante={piecesVarianteIA}
                      afficherComparaison={afficherComparaisonIA}
                      configurationServeur={configuration3D ?? null}
                      sauvegardeServeurEnCours={sauvegardeConfigurationMutation.isPending}
                      onSauvegarderConfigurationServeur={async (payload) => {
                        await sauvegardeConfigurationMutation.mutateAsync({
                          planId: planActif.id,
                          payload,
                        });
                      }}
                    />
                  </>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Historique des variantes</CardTitle>
          <CardDescription>Demandes IA et analyses précédentes pour le plan sélectionné.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {(historique ?? []).map((item) => (
            <div key={item.id} className="rounded-xl border p-4">
              <p className="font-medium">{item.prompt_utilisateur}</p>
              <p className="mt-1 text-sm text-muted-foreground">{item.analyse_ia.resume}</p>
            </div>
          ))}
          {(historique ?? []).length === 0 && <p className="text-sm text-muted-foreground">Aucun historique IA pour ce plan.</p>}
        </CardContent>
      </Card>
    </div>
  );
}