// ═══════════════════════════════════════════════════════════
// Recettes — Marmiton-style cards + kitchen appliance filters
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import {
  Plus,
  Search,
  Clock,
  ChefHat,
  Filter,
  Heart,
  CalendarDays,
  Users,
  UtensilsCrossed,
  Flame,
  Wind,
  Star,
  Leaf,
  Copy,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Card, CardContent } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { EtatVide } from "@/composants/ui/etat-vide";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { utiliserRequete, utiliserMutationAvecInvalidation } from "@/crochets/utiliser-api";
import { utiliserDelai } from "@/crochets/utiliser-delai";
import {
  listerRecettes,
  listerRecettesSemaine,
  listerRecettesSaisonnieres,
  planifierRecetteSemaine,
  deplanifierRecetteSemaine,
  obtenirDoublonsRecettes,
} from "@/bibliotheque/api/recettes";
import { DialogueImportRecette } from "@/composants/cuisine/dialogue-import-recette";
import { SwipeableItem } from "@/composants/swipeable-item";
import { PanneauFiltres, SectionFiltre, BoutonFiltre } from "@/composants/panneau-filtres";
import type { Recette } from "@/types/recettes";

const CATEGORIES = [
  "Toutes",
  "Entrée",
  "Plat",
  "Dessert",
  "Accompagnement",
  "Boisson",
  "Petit-déjeuner",
  "Goûter",
  "Snack",
];

const APPAREILS = [
  { cle: "cookeo" as const, label: "Cookeo", icone: Flame },
  { cle: "monsieur_cuisine" as const, label: "Mr Cuisine", icone: UtensilsCrossed },
  { cle: "airfryer" as const, label: "Air Fryer", icone: Wind },
] as const;

type CleAppareil = (typeof APPAREILS)[number]["cle"];

function tempsTotal(r: Recette): number {
  return (r.temps_preparation ?? 0) + (r.temps_cuisson ?? 0);
}

function ApplianceBadges({ recette }: { recette: Recette }) {
  const appareils = [];
  if (recette.compatible_cookeo) appareils.push({ label: "Cookeo", icone: Flame });
  if (recette.compatible_monsieur_cuisine) appareils.push({ label: "Mr Cuisine", icone: UtensilsCrossed });
  if (recette.compatible_airfryer) appareils.push({ label: "Air Fryer", icone: Wind });
  if (appareils.length === 0) return null;
  return (
    <div className="flex gap-1 mt-1">
      {appareils.map((a) => {
        const Ic = a.icone;
        return (
          <Badge key={a.label} variant="outline" className="text-[10px] gap-0.5 px-1 py-0">
            <Ic className="h-2.5 w-2.5" />
            {a.label}
          </Badge>
        );
      })}
    </div>
  );
}

export default function PageRecettes() {
  const [recherche, setRecherche] = useState("");
  const [categorie, setCategorie] = useState("Toutes");
  const [page, setPage] = useState(1);
  const [filtresAppareils, setFiltresAppareils] = useState<Set<CleAppareil>>(new Set());
    const [filtresFavoris, setFiltresFavoris] = useState(false);
    const [filtreTempsMax, setFiltreTempsMax] = useState<number | null>(null);
    const [filtreSaison, setFiltreSaison] = useState(false);
  const rechercheDelayee = utiliserDelai(recherche, 300);

  const { data, isLoading } = utiliserRequete(
    ["recettes", String(page), rechercheDelayee, categorie],
    () => listerRecettes(page, 20, rechercheDelayee || undefined)
  );

  // IDs des recettes de saison (pour badge)
  const { data: dataSaison } = utiliserRequete(
    ["recettes", "saisonnieres"],
    () => listerRecettesSaisonnieres(1, 0),
    { staleTime: 10 * 60 * 1000 }
  );
  const idsSaison = useMemo(
    () => new Set((dataSaison?.items ?? []).map((r) => r.id)),
    [dataSaison]
  );

  const { data: planifiees } = utiliserRequete(
    ["recettes", "semaine"],
    listerRecettesSemaine
  );
  const { data: doublonsRecettes } = utiliserRequete(
    ["recettes", "doublons"],
    () => obtenirDoublonsRecettes(0.75),
    { staleTime: 30 * 60 * 1000 }
  );
  const idsPlanifies = useMemo(
    () => new Set((planifiees ?? []).map((r) => r.id)),
    [planifiees]
  );

  const mutationPlanifier = utiliserMutationAvecInvalidation(
    (id: number) => planifierRecetteSemaine(id),
    [["recettes", "semaine"]],
    { onSuccess: () => toast.success("Recette ajoutée au menu de la semaine") }
  );

  const mutationDeplanifier = utiliserMutationAvecInvalidation(
    (id: number) => deplanifierRecetteSemaine(id),
    [["recettes", "semaine"]],
    { onSuccess: () => toast.success("Recette retirée du menu de la semaine") }
  );

  const recettes = useMemo(() => data?.items ?? [], [data]);
  const totalPages = data?.pages_totales ?? 1;

  // Filtrage client par appareil
  // Filtrage client (appareils + favoris + temps)
  const recettesFiltrees = useMemo(() => {
    return recettes.filter((r) => {
      if (filtresAppareils.size > 0) {
        for (const f of filtresAppareils) {
          if (f === "cookeo" && !r.compatible_cookeo) return false;
          if (f === "monsieur_cuisine" && !r.compatible_monsieur_cuisine) return false;
          if (f === "airfryer" && !r.compatible_airfryer) return false;
        }
      }
      if (filtresFavoris && !r.est_favori) return false;
      if (filtreTempsMax !== null && tempsTotal(r) > filtreTempsMax) return false;
      if (filtreSaison && !idsSaison.has(r.id)) return false;
      return true;
    });
  }, [recettes, filtresAppareils, filtresFavoris, filtreTempsMax, filtreSaison, idsSaison]);

  const toggleAppareil = (cle: CleAppareil) => {
    setFiltresAppareils((prev) => {
      const next = new Set(prev);
      if (next.has(cle)) next.delete(cle);
      else next.add(cle);
      return next;
    });
  };

  const nombreFiltresActifs =
    (filtresFavoris ? 1 : 0) +
    (filtreTempsMax !== null ? 1 : 0) +
    (filtreSaison ? 1 : 0) +
    filtresAppareils.size;

  const reinitialiserFiltres = () => {
    setFiltresFavoris(false);
    setFiltreTempsMax(null);
    setFiltreSaison(false);
    setFiltresAppareils(new Set());
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">📖 Recettes</h1>
          <p className="text-muted-foreground">
            {data?.total ?? 0} recettes dans votre collection
          </p>
        </div>
        <div className="flex gap-2">
          <DialogueImportRecette />
          <Button asChild>
            <Link href="/cuisine/recettes/nouveau">
              <Plus className="mr-2 h-4 w-4" />
              Nouvelle recette
            </Link>
          </Button>
        </div>
      </div>

      {/* Barre de recherche + filtres */}
      <div className="flex flex-col sm:flex-row gap-3 items-start">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Rechercher une recette..."
            value={recherche}
            onChange={(e) => {
              setRecherche(e.target.value);
              setPage(1);
            }}
            className="pl-10"
          />
        </div>
        <Select
          value={categorie}
          onValueChange={(val) => {
            setCategorie(val);
            setPage(1);
          }}
        >
          <SelectTrigger className="w-full sm:w-[180px]">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {CATEGORIES.map((cat) => (
              <SelectItem key={cat} value={cat}>
                {cat}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <PanneauFiltres
          nombreFiltresActifs={nombreFiltresActifs}
          onReinitialiser={reinitialiserFiltres}
          labelBouton="Filtres"
        >
          <SectionFiltre titre="Préférences">
            <div className="flex flex-wrap gap-2">
              <BoutonFiltre actif={filtresFavoris} onClick={() => setFiltresFavoris((v) => !v)} className="gap-1.5">
                <Star className="h-3 w-3" />Favoris uniquement
              </BoutonFiltre>
              <BoutonFiltre actif={filtreSaison} onClick={() => setFiltreSaison((v) => !v)} className="gap-1.5">
                <Leaf className="h-3 w-3" />De saison
              </BoutonFiltre>
            </div>
          </SectionFiltre>
          <SectionFiltre titre="Temps total (prépa + cuisson)">
            <div className="flex flex-wrap gap-2">
              {([null, 15, 30, 60] as const).map((t) => (
                <BoutonFiltre
                  key={t ?? "tous"}
                  actif={filtreTempsMax === t}
                  onClick={() => setFiltreTempsMax(t === filtreTempsMax ? null : t)}
                >
                  {t === null ? "Tous" : `≤ ${t}min`}
                </BoutonFiltre>
              ))}
            </div>
          </SectionFiltre>
          <SectionFiltre titre="Appareils">
            <div className="flex flex-wrap gap-2">
              {APPAREILS.map((ap) => {
                const Ic = ap.icone;
                return (
                  <BoutonFiltre key={ap.cle} actif={filtresAppareils.has(ap.cle)} onClick={() => toggleAppareil(ap.cle)} className="gap-1.5">
                    <Ic className="h-3 w-3" />{ap.label}
                  </BoutonFiltre>
                );
              })}
            </div>
          </SectionFiltre>
        </PanneauFiltres>
      </div>


      {doublonsRecettes?.items?.length ? (
        <Card className="border-amber-200 bg-amber-50/60 dark:border-amber-900 dark:bg-amber-950/20">
          <CardContent className="py-4 space-y-3">
            <div className="flex items-start gap-3">
              <div className="rounded-full bg-amber-100 p-2 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300">
                <Copy className="h-4 w-4" />
              </div>
              <div className="space-y-1">
                <p className="font-medium">Doublons potentiels</p>
                <p className="text-sm text-muted-foreground">
                  Quelques recettes se ressemblent assez pour mériter une fusion ou une clarification.
                </p>
              </div>
            </div>
            <div className="grid gap-2 md:grid-cols-2">
              {doublonsRecettes.items.slice(0, 4).map((doublon) => (
                <div key={`${doublon.recette_source.id}-${doublon.recette_proche.id}`} className="rounded-lg border bg-background/80 p-3">
                  <p className="text-sm font-medium">
                    {doublon.recette_source.nom} ↔ {doublon.recette_proche.nom}
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Similarité {(doublon.score_similarite * 100).toFixed(0)}%
                  </p>
                  {doublon.raisons?.length ? (
                    <ul className="mt-2 space-y-1 text-xs text-muted-foreground">
                      {doublon.raisons.slice(0, 2).map((raison) => (
                        <li key={raison}>• {raison}</li>
                      ))}
                    </ul>
                  ) : null}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}

      {/* Grille de recettes */}
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <Skeleton className="h-40 w-full rounded-t-xl" />
              <CardContent className="pt-3 space-y-2">
                <Skeleton className="h-5 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : recettesFiltrees.length === 0 ? (
        <EtatVide
          Icone={ChefHat}
          titre="Aucune recette trouvée"
          description={
            recherche
              ? "Essayez avec d'autres termes de recherche."
              : "Commencez par ajouter votre première recette."
          }
          action={
            !recherche ? (
              <Button asChild>
                <Link href="/cuisine/recettes/nouveau">
                  <Plus className="mr-2 h-4 w-4" />
                  Créer une recette
                </Link>
              </Button>
            ) : undefined
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {recettesFiltrees.map((recette) => (
            <SwipeableItem
              key={recette.id}
              desactiverGauche={idsPlanifies.has(recette.id)}
              desactiverDroit={!idsPlanifies.has(recette.id)}
              labelGauche="Planifier"
              labelDroit="Déplanifier"
              onSwipeLeft={() => mutationPlanifier.mutate(recette.id)}
              onSwipeRight={() => mutationDeplanifier.mutate(recette.id)}
            >
              <div className="relative group">
                <Link href={`/cuisine/recettes/${recette.id}`}>
                  <Card className="overflow-hidden hover:shadow-lg transition-shadow h-full">
                  {/* Photo placeholder */}
                  <div className="relative h-40 bg-gradient-to-br from-orange-100 to-amber-50 dark:from-orange-950 dark:to-amber-950 flex items-center justify-center">
                    {recette.image_url ? (
                      <img
                        src={recette.image_url}
                        alt={recette.nom}
                        className="object-cover w-full h-full"
                      />
                    ) : (
                      <ChefHat className="h-12 w-12 text-orange-300 dark:text-orange-700" />
                    )}
                    {/* Actions overlay */}
                    <div className="absolute top-2 right-2 flex gap-1">
                      {recette.est_favori && (
                        <div className="rounded-full bg-white/80 dark:bg-black/50 p-1">
                          <Heart className="h-4 w-4 text-red-500 fill-red-500" />
                        </div>
                      )}
                      <button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          if (idsPlanifies.has(recette.id)) {
                            mutationDeplanifier.mutate(recette.id);
                          } else {
                            mutationPlanifier.mutate(recette.id);
                          }
                        }}
                        title={
                          idsPlanifies.has(recette.id)
                            ? "Retirer du menu de la semaine"
                            : "Ajouter au menu de la semaine"
                        }
                        className="rounded-full bg-white/80 dark:bg-black/50 p-1 hover:bg-white dark:hover:bg-black/70 transition-colors"
                      >
                        <CalendarDays
                          className={`h-4 w-4 ${
                            idsPlanifies.has(recette.id)
                              ? "text-blue-500"
                              : "text-muted-foreground"
                          }`}
                        />
                      </button>
                    </div>
                    {/* Catégorie badge */}
                    {recette.categorie && (
                      <Badge className="absolute bottom-2 left-2 bg-white/90 text-foreground dark:bg-black/70 dark:text-white text-xs">
                        {recette.categorie}
                      </Badge>
                    )}
                  </div>

                  <CardContent className="pt-3 pb-3 space-y-2">
                    <h3 className="font-semibold text-sm line-clamp-1">
                      {recette.nom}
                    </h3>
                    {recette.description && (
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {recette.description}
                      </p>
                    )}

                    {recette.jours_depuis_derniere_cuisson != null && (
                      <div>
                        <Badge variant="outline" className="text-[10px]">
                          Dernière fois il y a {recette.jours_depuis_derniere_cuisson}j
                        </Badge>
                      </div>
                    )}

                    {/* Métadonnées */}
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      {tempsTotal(recette) > 0 && (
                        <span className="flex items-center gap-0.5">
                          <Clock className="h-3 w-3" />
                          {tempsTotal(recette)} min
                        </span>
                      )}
                      {recette.portions && (
                        <span className="flex items-center gap-0.5">
                          <Users className="h-3 w-3" />
                          {recette.portions}
                        </span>
                      )}

                      {recette.difficulte && (
                        <Badge
                          variant={
                            recette.difficulte === "facile"
                              ? "outline"
                              : recette.difficulte === "moyen"
                                ? "secondary"
                                : "destructive"
                          }
                          className="text-[10px] px-1 py-0"
                        >
                          {recette.difficulte}
                        </Badge>
                      )}
                    </div>

                    {/* Appareils compatibles */}
                    <ApplianceBadges recette={recette} />

                    {/* Badge saisonnalité */}
                    {idsSaison.has(recette.id) && (
                      <Badge variant="outline" className="text-[10px] gap-0.5 px-1 py-0 text-green-600 border-green-300">
                        <Leaf className="h-2.5 w-2.5" />
                        De saison
                      </Badge>
                    )}
                  </CardContent>
                  </Card>
                </Link>
              </div>
            </SwipeableItem>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            Précédent
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} / {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            Suivant
          </Button>
        </div>
      )}
    </div>
  );
}
