// Page Équipements — Inventaire | Domotique

"use client";

import { Suspense, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  Boxes, Wifi, ChevronDown,
  AlertTriangle, Link2, FileText, ExternalLink,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Skeleton } from "@/composants/ui/skeleton";
import { SkeletonPage } from "@/composants/ui/skeleton-page";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/composants/ui/collapsible";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/composants/ui/select";
import { BandeauIA } from "@/composants/maison/bandeau-ia";
import { BoutonAchat } from "@/composants/bouton-achat";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  obtenirAstucesDomotique,
  obtenirPiecesAvecObjets, obtenirSuggestionsRenouvellement,
  listerToutesLesTachesRoutines, associerRoutineObjet,
} from "@/bibliotheque/api/maison";
import {
  lierDocumentGarantie,
  listerDocuments,
  obtenirDocumentsGarantieObjet,
} from "@/bibliotheque/api/documents";

function ResumeDocumentsGarantie({
  objetId,
  nomObjet,
  sousGarantie,
}: {
  objetId: number;
  nomObjet: string;
  sousGarantie?: boolean;
}) {
  const [selectionVisible, setSelectionVisible] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading } = utiliserRequete(
    ["documents", "garantie", String(objetId)],
    () => obtenirDocumentsGarantieObjet(objetId),
    { enabled: objetId > 0 }
  );
  const { data: documentsDisponibles, isLoading: chargementDisponibles } = utiliserRequete(
    ["documents", "liste", String(objetId)],
    () => listerDocuments(),
    { enabled: selectionVisible }
  );

  const { mutate: lierDocumentExistant, isPending: liaisonEnCours } = utiliserMutation(
    ({ documentId, objetId }: { documentId: number; objetId: number }) =>
      lierDocumentGarantie(documentId, objetId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["documents", "garantie", String(objetId)] });
        toast.success("Document de garantie lié");
        setSelectionVisible(false);
      },
    }
  );

  const documents = data?.documents ?? [];
  const documentsCandidats = (documentsDisponibles?.items ?? []).filter(
    (doc) => !(doc.tags ?? []).includes(`equipement:${objetId}`)
  );

  if (isLoading && sousGarantie) {
    return <p className="mt-1 text-xs text-muted-foreground">Vérification des justificatifs…</p>;
  }

  const actionLiaison = (
    <div className="mt-2 space-y-2">
      <Button
        type="button"
        variant="outline"
        size="sm"
        className="h-7 text-xs"
        onClick={() => setSelectionVisible((value) => !value)}
      >
        <Link2 className="h-3 w-3 mr-1" />
        {selectionVisible ? "Masquer la sélection" : "Lier un document existant"}
      </Button>

      {selectionVisible && (
        <div className="rounded-md border bg-muted/30 p-2 space-y-2">
          {chargementDisponibles ? (
            <p className="text-xs text-muted-foreground">Chargement des documents…</p>
          ) : documentsCandidats.length ? (
            <div className="flex flex-wrap gap-2">
              {documentsCandidats.slice(0, 5).map((doc) => (
                <Button
                  key={doc.id}
                  type="button"
                  variant="secondary"
                  size="sm"
                  className="h-7 max-w-full text-xs"
                  disabled={liaisonEnCours}
                  onClick={() => lierDocumentExistant({ documentId: doc.id, objetId })}
                >
                  <FileText className="h-3 w-3 mr-1" />
                  <span className="truncate">{doc.titre}</span>
                </Button>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground">
              Aucun document récent trouvé pour liaison directe.
            </p>
          )}
          <a
            href={`/famille/documents?search=${encodeURIComponent(nomObjet)}`}
            className="inline-flex items-center gap-1 text-xs text-primary underline underline-offset-2"
          >
            Voir tous les documents
            <ExternalLink className="h-3 w-3" />
          </a>
        </div>
      )}
    </div>
  );

  if (!documents.length) {
    if (!sousGarantie) return null;

    return (
      <div className="mt-1">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="outline" className="text-[10px] border-amber-300 text-amber-700">
            <AlertTriangle className="h-3 w-3 mr-1" />
            Aucun justificatif lié
          </Badge>
          <a
            href={`/famille/documents?search=${encodeURIComponent(nomObjet)}`}
            className="text-xs text-primary underline underline-offset-2"
          >
            Lier une facture
          </a>
        </div>
        {actionLiaison}
      </div>
    );
  }

  return (
    <div className="mt-1">
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant="outline" className="text-[10px]">
          <FileText className="h-3 w-3 mr-1" />
          {data?.nb_documents ?? documents.length} document{(data?.nb_documents ?? documents.length) > 1 ? "s" : ""} lié{(data?.nb_documents ?? documents.length) > 1 ? "s" : ""}
        </Badge>
        {documents.slice(0, 2).map((doc) => {
          const href = doc.fichier_url || `/famille/documents?search=${encodeURIComponent(doc.titre)}`;
          const estExterne = Boolean(doc.fichier_url);

          return (
            <a
              key={doc.id}
              href={href}
              target={estExterne ? "_blank" : undefined}
              rel={estExterne ? "noreferrer" : undefined}
              className="inline-flex items-center gap-1 text-xs text-primary underline underline-offset-2"
            >
              {doc.titre}
              <ExternalLink className="h-3 w-3" />
            </a>
          );
        })}
      </div>
      {actionLiaison}
    </div>
  );
}

// ─── Onglet Inventaire ───────────────────────────────────────
function OngletInventaire() {
  const [pieceFiltree] = useState<string | undefined>(undefined);
  const { data: inventaire, isLoading } = utiliserRequete(
    ["maison", "inventaire", pieceFiltree ?? ""],
    () => obtenirPiecesAvecObjets(pieceFiltree)
  );
  const { data: suggestions } = utiliserRequete(
    ["maison", "renouvellement"],
    obtenirSuggestionsRenouvellement
  );
  const { data: tachesRoutines } = utiliserRequete(["maison", "routines", "taches"], listerToutesLesTachesRoutines);
  const queryClient = useQueryClient();

  const { mutate: associer } = utiliserMutation(
    ({ objetId, tacheId }: { objetId: number; tacheId: number | null }) => associerRoutineObjet(objetId, tacheId),
    { onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["maison", "inventaire"] }); toast.success("Routine associée"); } }
  );

  if (isLoading) return <Skeleton className="h-48" />;

  const pieces = inventaire?.pieces ?? [];
  const suggCount = suggestions?.total ?? 0;

  return (
    <div className="space-y-4">
      {suggCount > 0 && (
        <Card className="border-amber-300">
          <CardContent className="py-3">
            <p className="text-sm font-medium text-amber-700 flex items-center gap-1.5">
              <AlertTriangle className="h-4 w-4" />
              {suggCount} objet{suggCount > 1 ? "s" : ""} à remplacer ou surveiller
            </p>
            {suggestions?.suggestions.slice(0, 3).map(s => (
              <div key={s.id} className="flex items-center gap-2 mt-1">
                <span className="text-xs text-muted-foreground">• {s.nom}</span>
                <Badge variant={s.statut === "hors_service" ? "destructive" : "secondary"} className="text-[10px]">{s.statut}</Badge>
                {s.categorie && <BoutonAchat article={{ nom: s.nom }} taille="xs" />}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {!pieces.length ? (
        <Card><CardContent className="py-10 text-center text-muted-foreground">
          <Boxes className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p className="font-medium">Aucun équipement inventorié</p>
          <p className="text-xs mt-1">Ajoutez vos équipements depuis la visualisation ou via l'API</p>
        </CardContent></Card>
      ) : (
        <div className="space-y-4">
          {pieces.map(({ piece, objets }) => (
            <Card key={piece}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Boxes className="h-4 w-4" />{piece}
                  <Badge variant="secondary" className="text-xs">{objets.length}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0 space-y-2">
                {objets.map((obj) => (
                  <div key={obj.id} className="flex items-start gap-2 py-1.5 border-b last:border-0">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{obj.nom}</p>
                      <p className="text-xs text-muted-foreground">
                        {obj.marque}{obj.modele ? ` ${obj.modele}` : ""}{obj.categorie ? ` · ${obj.categorie}` : ""}
                      </p>
                      <ResumeDocumentsGarantie
                        objetId={obj.id}
                        nomObjet={obj.nom}
                        sousGarantie={obj.sous_garantie ?? undefined}
                      />
                    </div>
                    <div className="flex items-center justify-end gap-2 flex-wrap shrink-0">
                      {obj.statut && (
                        <Badge variant={obj.statut === "hors_service" ? "destructive" : obj.statut === "a_remplacer" ? "secondary" : "outline"} className="text-[10px]">
                          {obj.statut.replace(/_/g, " ")}
                        </Badge>
                      )}
                      {obj.sous_garantie !== undefined && obj.sous_garantie !== null && (
                        <Badge variant={obj.sous_garantie ? "default" : "secondary"} className="text-[10px]">
                          {obj.sous_garantie ? "✅ Sous garantie" : "❌ Hors garantie"}
                        </Badge>
                      )}
                      {tachesRoutines && tachesRoutines.length > 0 && (
                        <Select onValueChange={(v) => associer({ objetId: obj.id, tacheId: v ? Number(v) : null })}>
                          <SelectTrigger className="h-7 w-32 text-xs">
                            <Link2 className="h-3 w-3 mr-1" />
                            <SelectValue placeholder="Routine" />
                          </SelectTrigger>
                          <SelectContent>
                            {tachesRoutines.map(t => (
                              <SelectItem key={t.id} value={String(t.id)} className="text-xs">
                                {t.routine_nom ? `${t.routine_nom} → ` : ""}{t.nom}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      )}
                      {(obj.statut === "hors_service" || obj.statut === "a_remplacer") && (
                        <BoutonAchat article={{ nom: obj.nom }} taille="xs" />
                      )}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Onglet Domotique ────────────────────────────────────────
function OngletDomotique() {
  const { data: catalogue, isLoading } = utiliserRequete(["maison", "domotique"], () => obtenirAstucesDomotique());
  const [expanded, setExpanded] = useState<string | null>(null);

  if (isLoading) return <Skeleton className="h-48" />;

  const categories = catalogue?.categories ?? [];

  return (
    <div className="space-y-3">
      {!categories.length ? (
        <Card><CardContent className="py-10 text-center text-muted-foreground"><Wifi className="h-8 w-8 mx-auto mb-2 opacity-50" />Aucune astuce domotique</CardContent></Card>
      ) : (
        categories.map((cat) => (
          <Collapsible key={cat.id} open={expanded === cat.id} onOpenChange={(o) => setExpanded(o ? cat.id : null)}>
            <Card>
              <CollapsibleTrigger asChild>
                <CardHeader className="pb-2 cursor-pointer hover:bg-muted/30 transition-colors rounded-t-lg">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm flex items-center gap-1.5">
                      <Wifi className="h-4 w-4 text-blue-500" />{cat.nom}
                      {cat.appareils?.length > 0 && <Badge variant="secondary" className="text-xs">{cat.appareils.length}</Badge>}
                    </CardTitle>
                    <ChevronDown className={`h-4 w-4 text-muted-foreground transition-transform ${expanded === cat.id ? "rotate-180" : ""}`} />
                  </div>
                </CardHeader>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <CardContent className="pt-0 pb-3 space-y-2">
                  {cat.appareils?.map((a) => (
                    <div key={a.id} className="flex items-center gap-2 py-1.5 border-b last:border-0">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium">{a.nom}</p>
                        <div className="flex gap-1.5 flex-wrap mt-0.5">
                          {a.prix_estime > 0 && <span className="text-xs text-muted-foreground">~{a.prix_estime} €</span>}
                          {a.difficulte_installation && <Badge variant="outline" className="text-[10px]">{a.difficulte_installation}</Badge>}
                        </div>
                      </div>
                      <BoutonAchat article={{ nom: a.nom }} taille="xs" />
                    </div>
                  ))}
                  {catalogue?.conseils_generaux?.slice(0, 2).map((c, i) => (
                    <p key={i} className="text-xs text-muted-foreground pt-1">💡 {c.titre}</p>
                  ))}
                </CardContent>
              </CollapsibleContent>
            </Card>
          </Collapsible>
        ))
      )}
    </div>
  );
}

function ContenuEquipements() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const tab = searchParams.get("tab") ?? "inventaire";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">📦 Équipements</h1>
        <p className="text-muted-foreground">Inventaire et domotique</p>
      </div>

      <BandeauIA section="equipements" />

      <Tabs value={tab} onValueChange={(val) => router.replace(`?tab=${val}`)}>
        <TabsList>
          <TabsTrigger value="inventaire"><Boxes className="h-4 w-4 mr-1.5" />Inventaire</TabsTrigger>
          <TabsTrigger value="domotique"><Wifi className="h-4 w-4 mr-1.5" />Domotique</TabsTrigger>
        </TabsList>
        <TabsContent value="inventaire" className="mt-4"><OngletInventaire /></TabsContent>
        <TabsContent value="domotique" className="mt-4"><OngletDomotique /></TabsContent>
      </Tabs>
    </div>
  );
}

export default function PageEquipements() {
  return (
    <Suspense fallback={<SkeletonPage ariaLabel="Chargement des équipements" lignes={["h-8 w-40", "h-10 w-64", "h-48 w-full"]} />}>
      <ContenuEquipements />
    </Suspense>
  );
}
