// ═══════════════════════════════════════════════════════════
// Meubles — Wishlist & Suivi achats mobilier
// ═══════════════════════════════════════════════════════════

"use client";

import { Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  Sofa, Plus, Trash2, Pencil, ExternalLink, ShoppingCart,
  Euro, Package, CheckCircle2, Truck, Star, type LucideIcon,
} from "lucide-react";
import {
  Card, CardContent, CardHeader, CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Skeleton } from "@/composants/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { utiliserDialogCrud } from "@/crochets/utiliser-crud";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerMeubles, creerMeuble, modifierMeuble, supprimerMeuble,
  obtenirBudgetMeubles,
} from "@/bibliotheque/api/maison";
import type { Meuble } from "@/types/maison";
import type { ObjetDonnees } from "@/types/commun";
import { toast } from "sonner";
import { BoutonAchat } from "@/composants/maison/bouton-achat";

// ─── Constantes ──────────────────────────────────────────────

const STATUTS = ["tous", "souhaité", "commandé", "reçu", "installé"] as const;

const COULEUR_STATUT: Record<string, string> = {
  "souhaité": "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
  "commandé": "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300",
  "reçu": "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300",
  "installé": "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
};

const COULEUR_PRIORITE: Record<string, string> = {
  haute: "bg-red-100 text-red-700",
  moyenne: "bg-orange-100 text-orange-700",
  basse: "bg-gray-100 text-gray-600",
};

const ICONE_STATUT: Record<string, LucideIcon> = {
  "souhaité": Star,
  "commandé": ShoppingCart,
  "reçu": Package,
  "installé": CheckCircle2,
};

const TRANSITION_STATUT: Record<string, { label: string; suivant: string }> = {
  "souhaité": { label: "→ Commandé", suivant: "commandé" },
  "commandé": { label: "→ Reçu", suivant: "reçu" },
  "reçu": { label: "→ Installé", suivant: "installé" },
};

const CATEGORIES = [
  "Salon", "Chambre", "Cuisine", "Salle de bain", "Bureau",
  "Entrée", "Jardin", "Rangement", "Autre",
];

const PIECES = [
  "Salon", "Chambre principale", "Chambre enfant", "Cuisine",
  "Salle de bain", "Bureau", "Entrée", "Garage", "Jardin", "Autre",
];

// ─── Prochaines soldes (statique) ────────────────────────────

const PROCHAINES_SOLDES = [
  { label: "Soldes d'hiver", debut: "12 jan 2026", fin: "11 fév 2026" },
  { label: "Soldes d'été", debut: "25 juin 2026", fin: "22 juil 2026" },
];

// ─── Composant carte meuble ───────────────────────────────────

function CarteMeuble({
  meuble,
  onModifier,
  onSupprimer,
  onAvancer,
}: {
  meuble: Meuble;
  onModifier: (m: Meuble) => void;
  onSupprimer: (id: number) => void;
  onAvancer: (id: number, statut: string) => void;
}) {
  const statut = meuble.statut ?? "souhaité";
  const IconeStatut = ICONE_STATUT[statut] ?? Star;
  const transition = TRANSITION_STATUT[statut];

  return (
    <Card className="group relative flex flex-col gap-2 p-4 hover:shadow-md transition-shadow">
      {/* En-tête */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-sm truncate">{meuble.nom}</p>
          {meuble.piece && (
            <p className="text-xs text-muted-foreground mt-0.5">{meuble.piece}</p>
          )}
        </div>
        <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${COULEUR_STATUT[statut] ?? "bg-gray-100 text-gray-600"}`}>
          <IconeStatut className="h-3 w-3" />
          {statut}
        </span>
      </div>

      {/* Badges */}
      <div className="flex flex-wrap gap-1">
        {meuble.categorie && (
          <Badge variant="outline" className="text-xs">{meuble.categorie}</Badge>
        )}
        {meuble.priorite && (
          <span className={`rounded px-1.5 py-0.5 text-xs font-medium ${COULEUR_PRIORITE[meuble.priorite] ?? "bg-gray-100 text-gray-600"}`}>
            {meuble.priorite}
          </span>
        )}
        {meuble.prix_estime != null && (
          <span className="inline-flex items-center gap-0.5 rounded bg-muted px-1.5 py-0.5 text-xs font-medium">
            <Euro className="h-3 w-3" />
            {meuble.prix_estime.toFixed(0)}
          </span>
        )}
      </div>

      {/* Notes */}
      {meuble.notes && (
        <p className="text-xs text-muted-foreground line-clamp-2">{meuble.notes}</p>
      )}

      {/* Actions */}
      <div className="mt-auto flex flex-col gap-1.5 pt-2 border-t">
        {/* Bouton avancement workflow */}
        {transition && (
          <Button
            size="sm"
            variant="secondary"
            className="w-full text-xs h-7"
            onClick={() => onAvancer(meuble.id, transition.suivant)}
          >
            <Truck className="h-3 w-3 mr-1" />
            {transition.label}
          </Button>
        )}

        {/* Bouton achat + lien externe */}
        <div className="flex gap-1">
          {meuble.url_reference && (
            <BoutonAchat
              url={meuble.url_reference}
              label="Voir"
              size="sm"
              className="flex-1 h-7 text-xs"
            />
          )}
          {meuble.url_reference && (
            <Button
              size="sm"
              variant="ghost"
              className="h-7 w-7 p-0"
              asChild
            >
              <a href={meuble.url_reference} target="_blank" rel="noopener noreferrer" title="Voir la référence"  aria-label="Voir la référence">
                <ExternalLink className="h-3 w-3" />
              </a>
            </Button>
          )}
        </div>

        {/* Modifier / Supprimer */}
        <div className="flex gap-1">
          <Button
            size="sm"
            variant="ghost"
            className="flex-1 h-7 text-xs"
            onClick={() => onModifier(meuble)}
          >
            <Pencil className="h-3 w-3 mr-1" />
            Modifier
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="h-7 w-7 p-0 text-destructive hover:text-destructive"
            onClick={() => onSupprimer(meuble.id)}
          >
            <Trash2 className="h-3 w-3" />
          </Button>
        </div>
      </div>
    </Card>
  );
}

// ─── Sidebar budget ───────────────────────────────────────────

function SidebarBudget() {
  const { data: budget, isLoading } = utiliserRequete(
    ["maison", "meubles", "budget"],
    obtenirBudgetMeubles,
    { staleTime: 5 * 60 * 1000 }
  );

  return (
    <aside className="space-y-4">
      {/* Budget */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Euro className="h-4 w-4 text-green-600" />
            Budget estimé
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </div>
          ) : budget ? (
            <>
              <div className="rounded-lg bg-muted p-3 text-center">
                <p className="text-2xl font-bold text-green-600">
                  {budget.total_estime.toFixed(0)} €
                </p>
                <p className="text-xs text-muted-foreground">Total estimé</p>
              </div>
              {budget.prix_max > 0 && (
                <p className="text-xs text-muted-foreground text-center">
                  Jusqu&apos;à {budget.prix_max.toFixed(0)} €
                </p>
              )}
              <p className="text-xs text-muted-foreground">
                {budget.nb_meubles} article{budget.nb_meubles !== 1 ? "s" : ""}
              </p>
              {Object.entries(budget.par_piece).length > 0 && (
                <div className="space-y-1">
                  <p className="text-xs font-medium text-muted-foreground">Par pièce</p>
                  {Object.entries(budget.par_piece).map(([piece, montant]) => (
                    <div key={piece} className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">{piece}</span>
                      <span className="font-medium">{(montant as number).toFixed(0)} €</span>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <p className="text-xs text-muted-foreground text-center py-2">Aucune donnée</p>
          )}
        </CardContent>
      </Card>

      {/* Prochaines soldes */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <ShoppingCart className="h-4 w-4 text-amber-600" />
            Prochaines soldes
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {PROCHAINES_SOLDES.map((s) => (
            <div key={s.label} className="rounded-lg border p-2 space-y-1">
              <p className="text-xs font-semibold">{s.label}</p>
              <p className="text-xs text-muted-foreground">
                Du {s.debut} au {s.fin}
              </p>
            </div>
          ))}
          <p className="text-xs text-muted-foreground mt-1">
            💡 Préparez votre wishlist à l&apos;avance pour profiter des réductions !
          </p>
        </CardContent>
      </Card>

      {/* Légende statuts */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Légende</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1.5">
          {Object.entries(COULEUR_STATUT).map(([statut, classe]) => {
            const Icone = ICONE_STATUT[statut] ?? Star;
            return (
              <div key={statut} className="flex items-center gap-2">
                <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${classe}`}>
                  <Icone className="h-3 w-3" />
                  {statut}
                </span>
              </div>
            );
          })}
        </CardContent>
      </Card>
    </aside>
  );
}

// ─── Composant principal ──────────────────────────────────────

function ContenuMeubles() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const queryClient = useQueryClient();

  const tabActif = searchParams.get("statut") ?? "tous";
  const setTabActif = (val: string) => {
    router.replace(`?statut=${val}`, { scroll: false });
  };

  const { donnees: meubles, chargement } = utiliserRequete(
    ["maison", "meubles", tabActif],
    () => listerMeubles(tabActif === "tous" ? undefined : tabActif),
    { staleTime: 60_000 }
  );

  const invalidate = () => {
    STATUTS.forEach((s) => queryClient.invalidateQueries({ queryKey: ["maison", "meubles", s] }));
    queryClient.invalidateQueries({ queryKey: ["maison", "meubles", "budget"] });
  };

  const mutCreer = utiliserMutation(
    (data: Omit<Meuble, "id">) => creerMeuble(data),
    { onSuccess: () => { invalidate(); toast.success("Meuble ajouté"); } }
  );
  const mutModifier = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<Meuble> }) => modifierMeuble(id, data),
    { onSuccess: () => { invalidate(); toast.success("Meuble modifié"); } }
  );
  const mutSupprimer = utiliserMutation(
    (id: number) => supprimerMeuble(id),
    { onSuccess: () => { invalidate(); toast.success("Meuble supprimé"); } }
  );

  const {
    ouvert, mode, elementEnCours, ouvrir, fermer,
  } = utiliserDialogCrud<Meuble>();

  const onSoumettre = (donnees: ObjetDonnees) => {
    const payload = {
      nom: donnees.nom as string,
      piece: donnees.piece as string | undefined,
      categorie: donnees.categorie as string | undefined,
      prix_estime: donnees.prix_estime ? Number(donnees.prix_estime) : undefined,
      url_reference: donnees.url_reference as string | undefined,
      priorite: donnees.priorite as string | undefined,
      statut: (donnees.statut as string | undefined) ?? "souhaité",
      notes: donnees.notes as string | undefined,
    };
    if (mode === "creation") {
      mutCreer.mutate(payload);
    } else if (elementEnCours) {
      mutModifier.mutate({ id: elementEnCours.id, data: payload });
    }
    fermer();
  };

  const onAvancer = (id: number, suivant: string) => {
    mutModifier.mutate(
      { id, data: { statut: suivant } },
      { onSuccess: () => toast.success(`Statut mis à jour : ${suivant}`) }
    );
  };

  const champsFormulaire = [
    { nom: "nom", label: "Nom", type: "text" as const, requis: true, defaut: elementEnCours?.nom ?? "" },
    {
      nom: "piece", label: "Pièce", type: "select" as const,
      options: PIECES.map((p) => ({ valeur: p, label: p })),
      defaut: elementEnCours?.piece ?? "",
    },
    {
      nom: "categorie", label: "Catégorie", type: "select" as const,
      options: CATEGORIES.map((c) => ({ valeur: c, label: c })),
      defaut: elementEnCours?.categorie ?? "",
    },
    { nom: "prix_estime", label: "Prix estimé (€)", type: "number" as const, defaut: elementEnCours?.prix_estime ?? "" },
    { nom: "url_reference", label: "URL de référence", type: "text" as const, defaut: elementEnCours?.url_reference ?? "" },
    {
      nom: "priorite", label: "Priorité", type: "select" as const,
      options: [
        { valeur: "haute", label: "Haute" },
        { valeur: "moyenne", label: "Moyenne" },
        { valeur: "basse", label: "Basse" },
      ],
      defaut: elementEnCours?.priorite ?? "moyenne",
    },
    {
      nom: "statut", label: "Statut", type: "select" as const,
      options: [
        { valeur: "souhaité", label: "Souhaité" },
        { valeur: "commandé", label: "Commandé" },
        { valeur: "reçu", label: "Reçu" },
        { valeur: "installé", label: "Installé" },
      ],
      defaut: elementEnCours?.statut ?? "souhaité",
    },
    { nom: "notes", label: "Notes", type: "textarea" as const, defaut: elementEnCours?.notes ?? "" },
  ];

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-amber-500/10 p-2">
            <Sofa className="h-5 w-5 text-amber-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Meubles & Wishlist</h1>
            <p className="text-sm text-muted-foreground">Suivi de vos achats mobilier</p>
          </div>
        </div>
        <Button size="sm" onClick={() => ouvrir("creation")}>
          <Plus className="h-4 w-4 mr-1" />
          Ajouter
        </Button>
      </div>

      {/* Layout deux colonnes */}
      <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
        {/* Colonne principale */}
        <div className="space-y-4">
          <Tabs value={tabActif} onValueChange={setTabActif}>
            <TabsList className="grid w-full grid-cols-5 h-auto">
              {STATUTS.map((s) => (
                <TabsTrigger key={s} value={s} className="text-xs capitalize py-1.5">
                  {s === "tous" ? "Tous" : s}
                </TabsTrigger>
              ))}
            </TabsList>

            {STATUTS.map((s) => (
              <TabsContent key={s} value={s} className="mt-4">
                {chargement ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                    {Array.from({ length: 6 }).map((_, i) => (
                      <Skeleton key={i} className="h-48 w-full rounded-lg" />
                    ))}
                  </div>
                ) : !meubles || meubles.length === 0 ? (
                  <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-12 text-center gap-3">
                    <Sofa className="h-10 w-10 text-muted-foreground/50" />
                    <div>
                      <p className="font-medium text-muted-foreground">Aucun meuble</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {s === "tous"
                          ? "Commencez par ajouter un meuble à votre wishlist"
                          : `Aucun meuble avec le statut "${s}"`}
                      </p>
                    </div>
                    {s === "tous" && (
                      <Button size="sm" variant="outline" onClick={() => ouvrir("creation")}>
                        <Plus className="h-4 w-4 mr-1" />
                        Ajouter un meuble
                      </Button>
                    )}
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                    {meubles.map((meuble) => (
                      <CarteMeuble
                        key={meuble.id}
                        meuble={meuble}
                        onModifier={(m) => ouvrir(m)}
                        onSupprimer={(id) => {
                          if (confirm("Supprimer ce meuble ?")) mutSupprimer.mutate(id);
                        }}
                        onAvancer={onAvancer}
                      />
                    ))}
                  </div>
                )}
              </TabsContent>
            ))}
          </Tabs>
        </div>

        {/* Sidebar */}
        <SidebarBudget />
      </div>

      {/* Dialogue CRUD */}
      <DialogueFormulaire
        titre={mode === "creation" ? "Ajouter un meuble" : "Modifier le meuble"}
        description={mode === "creation" ? "Ajoutez un meuble à votre wishlist" : "Modifiez les informations du meuble"}
        ouvert={ouvert}
        onFermer={fermer}
        champs={champsFormulaire}
        onSoumettre={onSoumettre}
        chargement={mutCreer.isPending || mutModifier.isPending}
      />
    </div>
  );
}

// ─── Export ───────────────────────────────────────────────────

export default function MeublesPage() {
  return (
    <Suspense fallback={
      <div className="space-y-6">
        <Skeleton className="h-10 w-48" />
        <div className="grid grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-48 w-full rounded-lg" />
          ))}
        </div>
      </div>
    }>
      <ContenuMeubles />
    </Suspense>
  );
}
