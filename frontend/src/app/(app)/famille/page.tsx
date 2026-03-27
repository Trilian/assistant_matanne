// ═══════════════════════════════════════════════════════════
// Hub Famille Intelligent — Phase Refonte
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Baby,
  Wallet,
  ListChecks,
  Camera,
  BookUser,
  FileText,
  Sparkles,
  Bell,
  AlertTriangle,
  Info,
  Calendar,
  ShoppingBag,
  Settings,
  CheckCircle2,
  TrendingUp,
  TrendingDown,
  Minus,
  Clock,
  MapPin,
  Loader2,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/composants/ui/dialog";
import { BandeauMeteo } from "@/composants/famille/bandeau-meteo";
import { CarteAnniversaire } from "@/composants/famille/carte-anniversaire";
import { CarteDocumentExpire } from "@/composants/famille/carte-document-expire";
import { CarteJourSpecial } from "@/composants/famille/carte-jour-special";
import { CarteSuggestionIA } from "@/composants/famille/carte-suggestion-ia";
import { utiliserRequete } from "@/crochets/utiliser-api";
import {
  obtenirContexteFamilial,
  evaluerRappelsFamille,
  listerAchats,
  obtenirResumeBudgetMois,
  completerRoutine,
  obtenirSuggestionsWeekend,
  joursSansCReche,
  obtenirSuggestionsAchatsEnrichies,
} from "@/bibliotheque/api/famille";
import { toast } from "sonner";
import { GrilleWidgets } from "@/composants/disposition/grille-widgets";
import type { ContexteFamilial, RappelFamille } from "@/types/famille";

const MODULES = [
  { id: "jules", titre: "Jules", chemin: "/famille/jules", Icone: Baby },
  { id: "budget", titre: "Budget", chemin: "/famille/budget", Icone: Wallet },
  { id: "routines", titre: "Routines", chemin: "/famille/routines", Icone: ListChecks },
  { id: "achats", titre: "Achats", chemin: "/famille/achats", Icone: ShoppingBag },
  { id: "contacts", titre: "Contacts", chemin: "/famille/contacts", Icone: BookUser },
  { id: "documents", titre: "Documents", chemin: "/famille/documents", Icone: FileText },
  { id: "calendriers", titre: "Calendriers", chemin: "/famille/calendriers", Icone: Calendar },
  { id: "config", titre: "Config", chemin: "/famille/config", Icone: Settings },
];

// Mapping module id → mots-clés de types de rappels
const MODULES_RAPPELS_MAPPING: Record<string, string[]> = {
  documents: ["document"],
  budget: ["budget"],
  jules: ["jalon", "sante"],
  achats: ["achat", "anniversaire"],
};

const LABELS_POUR_QUI: Record<string, string> = {
  jules: "👶 Jules",
  anne: "👩 Anne",
  mathieu: "🧔 Mathieu",
  famille: "🏠 Famille",
};

export default function PageFamille() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: contexte, isLoading } = utiliserRequete<ContexteFamilial>(
    ["famille", "contexte"],
    obtenirContexteFamilial,
    { staleTime: 5 * 60 * 1000 }
  );

  const { data: rappelsData } = utiliserRequete<{ rappels: RappelFamille[]; total: number }>(
    ["famille", "rappels", "evaluer"],
    evaluerRappelsFamille,
    { staleTime: 5 * 60 * 1000 }
  );

  const { data: achatsRecents } = utiliserRequete(
    ["famille", "achats", "hub"],
    () => listerAchats({ achete: false }),
    { staleTime: 3 * 60 * 1000 }
  );

  const { data: resumeBudget } = utiliserRequete(
    ["famille", "budget", "resume-mois"],
    obtenirResumeBudgetMois,
    { staleTime: 10 * 60 * 1000 }
  );

  const mutationCompleterRoutine = useMutation({
    mutationFn: completerRoutine,
    onSuccess: (data) => {
      toast.success(`✅ ${data.nom} — routine complétée !`);
      queryClient.invalidateQueries({ queryKey: ["famille", "contexte"] });
    },
    onError: () => toast.error("Impossible de marquer la routine."),
  });

  // Jours sans crèche ce mois (Task 4)
  const { data: joursSansCreche } = utiliserRequete(
    ["famille", "planning", "jours-sans-creche"],
    () => joursSansCReche(),
    { staleTime: 60 * 60 * 1000 }
  );

  // État dialog suggestions weekend (Task 3)
  const [dialogWeekendOuvert, setDialogWeekendOuvert] = useState(false);
  const [suggestionsWeekend, setSuggestionsWeekend] = useState<string | null>(null);

  const mutationSuggestionsWeekend = useMutation({
    mutationFn: () => obtenirSuggestionsWeekend({ nb_suggestions: 5 }),
    onSuccess: (data) => {
      setSuggestionsWeekend(data.suggestions);
      setDialogWeekendOuvert(true);
    },
    onError: () => toast.error("Impossible de charger les suggestions weekend."),
  });

  const rappelsUrgents =
    rappelsData?.rappels?.filter((r) => r.priorite === "danger" || r.priorite === "warning") ?? [];

  const [hasShownToast, setHasShownToast] = useState(false);
  const [suggestionsIAHub, setSuggestionsIAHub] = useState<Array<{ titre: string; description: string; source?: string }>>([]);

  const mutationSuggestionsAchatsHub = useMutation({
    mutationFn: () => obtenirSuggestionsAchatsEnrichies({ triggers: ["hub_rapide"] }),
    onSuccess: (data) => setSuggestionsIAHub((data.items ?? []).slice(0, 2)),
    onError: () => toast.error("Impossible de charger les suggestions IA."),
  });

  useEffect(() => {
    if (!hasShownToast && contexte) {
      const urgences: string[] = [];
      contexte.anniversaires_proches?.forEach((a) => {
        if (a.jours_restants !== undefined && a.jours_restants <= 2) {
          urgences.push(`🎂 Anniversaire ${a.nom_personne} dans ${a.jours_restants} jour(s)`);
        }
      });
      contexte.documents_expirants?.forEach((d) => {
        if (d.jours_restants !== undefined && d.jours_restants <= 2) {
          urgences.push(`⚠️ ${d.titre} expire dans ${d.jours_restants} jour(s)`);
        }
      });
      if (urgences.length > 0) {
        urgences.forEach((msg) => toast.warning(msg));
      }
      setHasShownToast(true);
    }
  }, [contexte, hasShownToast]);

  // Détection des contextes IA
  const dayOfWeek = new Date().getDay(); // 0=dim, 4=jeu, 5=ven, 6=sam
  const isWeekendApproaching = dayOfWeek === 4 || dayOfWeek === 5;
  const isSoireeContext = dayOfWeek === 5 || dayOfWeek === 6;

  // Achats top 3 par personne (priorité urgents non achetés)
  const achatsPourQui = ["jules", "anne", "mathieu", "famille"].reduce(
    (acc, qui) => {
      const items = (achatsRecents ?? [])
        .filter((a) => a.pour_qui === qui && !a.achete)
        .slice(0, 2);
      if (items.length > 0) acc[qui] = items;
      return acc;
    },
    {} as Record<string, typeof achatsRecents>
  );

  const itemsAVenir = [
    ...(contexte?.anniversaires_proches?.map((a) => ({
      type: "anniversaire" as const,
      data: a,
      jours: a.jours_restants ?? 999,
    })) ?? []),
    ...(contexte?.documents_expirants?.map((d) => ({
      type: "document" as const,
      data: d,
      jours: d.jours_restants ?? 999,
    })) ?? []),
    ...(contexte?.jours_speciaux?.map((j) => ({
      type: "jour_special" as const,
      data: j,
      jours: j.jours_restants ?? 999,
    })) ?? []),
  ].sort((a, b) => a.jours - b.jours);

  // Variation budget: icone + couleur
  const variationBudget = resumeBudget?.variation_pct;
  const VariationIcon =
    variationBudget == null ? Minus : variationBudget > 0 ? TrendingUp : TrendingDown;
  const variationColor =
    variationBudget == null
      ? "text-muted-foreground"
      : variationBudget > 10
        ? "text-red-500"
        : variationBudget < -5
          ? "text-green-600"
          : "text-muted-foreground";

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">👨‍👩‍👦 Famille</h1>
          <p className="text-muted-foreground">Chargement du contexte...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* En-tête */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">👨‍👩‍👦 Famille</h1>
        <p className="text-muted-foreground">Votre contexte familial en un coup d'œil</p>
      </div>

      {/* Section 0: Rappels urgents */}
      {rappelsUrgents.length > 0 && (
        <section>
          <Card className="border-orange-200 bg-orange-50/50 dark:border-orange-800 dark:bg-orange-950/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Bell className="h-4 w-4 text-orange-500" />
                Rappels du moment
                <Badge variant="secondary" className="ml-auto">
                  {rappelsUrgents.length}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1.5">
                {rappelsUrgents.map((r, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    {r.priorite === "danger" ? (
                      <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 shrink-0" />
                    ) : (
                      <Info className="h-4 w-4 text-orange-400 mt-0.5 shrink-0" />
                    )}
                    <span className={r.priorite === "danger" ? "font-medium" : ""}>{r.message}</span>
                    {r.jours_restants !== undefined && (
                      <Badge
                        variant={r.priorite === "danger" ? "destructive" : "outline"}
                        className="ml-auto shrink-0 text-xs"
                      >
                        J-{r.jours_restants}
                      </Badge>
                    )}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </section>
      )}

      {/* Section Météo */}
      {contexte?.meteo && <BandeauMeteo meteo={contexte.meteo} />}

      {/* Section 1: Grille 2×2 widgets clés */}
      <section>
        <h2 className="text-lg font-semibold mb-3">Vue d'ensemble</h2>
        <div className="grid grid-cols-2 gap-3">
          {/* Widget Jules */}
          <Card className="col-span-1">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-1.5">
                <Baby className="h-4 w-4 text-blue-500" />
                Jules
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-1.5">
              {contexte?.jules ? (
                <>
                  <p className="text-xs text-muted-foreground">{contexte.jules.age_mois} mois</p>
                  {contexte.jules.prochains_jalons?.[0] && (
                    <p className="text-xs">🎯 {contexte.jules.prochains_jalons[0]}</p>
                  )}
                </>
              ) : (
                <p className="text-xs text-muted-foreground">—</p>
              )}
              <Link href="/famille/jules" className="block">
                <Button variant="ghost" size="sm" className="w-full h-7 text-xs mt-1">
                  Détails →
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Widget Activités */}
          <Card className="col-span-1">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-1.5">
                <Calendar className="h-4 w-4 text-green-500" />
                Activités
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-1">
              {contexte?.activites_a_venir?.slice(0, 2).map((a) => (
                <div key={a.id} className="text-xs flex items-center gap-1.5">
                  {(a as { heure_debut?: string }).heure_debut && (
                    <Clock className="h-3 w-3 text-muted-foreground shrink-0" />
                  )}
                  <span className="truncate">{a.titre}</span>
                </div>
              ))}
              {!contexte?.activites_a_venir?.length && (
                <p className="text-xs text-muted-foreground">Aucune activité</p>
              )}
              <Link href="/famille/activites" className="block">
                <Button variant="ghost" size="sm" className="w-full h-7 text-xs mt-1">
                  Voir tout →
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Widget Budget */}
          <Card className="col-span-1">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-1.5">
                <Wallet className="h-4 w-4 text-purple-500" />
                Budget
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-1.5">
              {resumeBudget ? (
                <>
                  <p className="text-base font-bold">{resumeBudget.total_courant.toFixed(0)} €</p>
                  <div className={`flex items-center gap-1 text-xs ${variationColor}`}>
                    <VariationIcon className="h-3 w-3" />
                    {variationBudget != null
                      ? `${variationBudget > 0 ? "+" : ""}${variationBudget}% vs mois préc.`
                      : "Mois en cours"}
                  </div>
                </>
              ) : (
                <p className="text-xs text-muted-foreground">—</p>
              )}
              <Link href="/famille/budget" className="block">
                <Button variant="ghost" size="sm" className="w-full h-7 text-xs mt-1">
                  Détails →
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Widget Achats par personne */}
          <Card className="col-span-1">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-1.5">
                <ShoppingBag className="h-4 w-4 text-orange-500" />
                Achats
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-1">
              {Object.entries(achatsPourQui).slice(0, 2).map(([qui, items]) => (
                <div key={qui} className="text-xs flex items-center gap-1.5">
                  <span className="shrink-0">{LABELS_POUR_QUI[qui] ?? qui}</span>
                  <Badge variant="secondary" className="text-xs">
                    {(items as { id: number }[]).length}
                  </Badge>
                </div>
              ))}
              {Object.keys(achatsPourQui).length === 0 && (
                <p className="text-xs text-muted-foreground">Liste vide 🎉</p>
              )}
              <Button
                variant="ghost"
                size="sm"
                className="w-full h-7 text-xs mt-1 text-purple-600"
                onClick={() => mutationSuggestionsAchatsHub.mutate()}
                disabled={mutationSuggestionsAchatsHub.isPending}
              >
                {mutationSuggestionsAchatsHub.isPending ? (
                  <Loader2 className="h-3 w-3 animate-spin mr-1" />
                ) : (
                  <Sparkles className="h-3 w-3 mr-1" />
                )}
                Suggestions IA
              </Button>
              {suggestionsIAHub.length > 0 && (
                <div className="space-y-1 mt-1">
                  {suggestionsIAHub.map((s, i) => (
                    <div key={i} className="flex items-center justify-between gap-1 text-xs">
                      <span className="truncate flex-1">{s.titre}</span>
                      <Badge variant="outline" className="text-[9px] shrink-0">
                        {s.source ?? "ia"}
                      </Badge>
                      <Link href="/famille/achats">
                        <Button variant="ghost" size="sm" className="h-5 text-[9px] px-1">
                          +
                        </Button>
                      </Link>
                    </div>
                  ))}
                </div>
              )}
              <Link href="/famille/achats" className="block">
                <Button variant="ghost" size="sm" className="w-full h-7 text-xs mt-1">
                  Voir tout →
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Section 2: Routines du moment (quick-complete) */}
      {contexte?.routines_du_moment && contexte.routines_du_moment.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-lg font-semibold">Routines du moment</h2>
          <div className="space-y-2">
            {contexte.routines_du_moment.map((r) => (
              <div key={r.id} className="flex items-center gap-3">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 px-2"
                  onClick={() => mutationCompleterRoutine.mutate(r.id)}
                  disabled={mutationCompleterRoutine.isPending}
                  title="Marquer comme complétée"
                >
                  <CheckCircle2 className="h-4 w-4 text-muted-foreground hover:text-green-500" />
                </Button>
                <span className="text-sm">{r.nom}</span>
                {r.categorie && (
                  <Badge variant="outline" className="text-xs ml-auto">
                    {r.categorie}
                  </Badge>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Section 3: À venir */}
      {itemsAVenir.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-lg font-semibold">À venir</h2>
          <div className="space-y-2">
            {itemsAVenir.slice(0, 5).map((item, idx) => {
              if (item.type === "anniversaire") {
                return <CarteAnniversaire key={`anniv-${idx}`} anniversaire={item.data} />;
              }
              if (item.type === "document") {
                return <CarteDocumentExpire key={`doc-${idx}`} document={item.data} />;
              }
              if (item.type === "jour_special") {
                return <CarteJourSpecial key={`js-${idx}`} jour={item.data} />;
              }
              return null;
            })}
          </div>
        </section>
      )}

      {/* Section 4: L'IA suggère (contextuel) */}
      <section className="space-y-3">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-purple-500" />
          L'IA suggère
        </h2>
        <div className="space-y-2">
          {/* Weekend (jeudi/vendredi) */}
          {isWeekendApproaching && (
            <CarteSuggestionIA
              titre="Idées pour le weekend"
              description="Activités adaptées à Jules, avec la météo du weekend"
              source="weekend"
              actionLabel={mutationSuggestionsWeekend.isPending ? "Chargement…" : "Suggestions weekend IA"}
              onAction={() => mutationSuggestionsWeekend.mutate()}
            />
          )}

          {/* Soirée (vendredi/samedi) */}
          {isSoireeContext && (
            <CarteSuggestionIA
              titre="Idées soirée"
              description="Activités ou films pour ce soir en famille ou en duo"
              source="weekend"
              actionLabel="Voir les idées"
              onAction={() => router.push("/famille/weekend")}
            />
          )}

          {/* Crèche fermée dans les 7 prochains jours (données API jours-sans-crèche) */}
          {(joursSansCreche?.total ?? 0) > 0 && (
            <CarteSuggestionIA
              titre="Jules sans crèche ce mois"
              description={`${joursSansCreche!.total} jour(s) sans crèche en ${joursSansCreche!.mois} — planifiez des activités`}
              source="achats"
              actionLabel="Planifier les activités"
              onAction={() => router.push("/famille/activites")}
            />
          )}

          {/* Vacances dans les 30 jours */}
          {contexte?.jours_speciaux?.some(
            (j) =>
              j.jours_restants !== undefined &&
              j.jours_restants <= 30 &&
              (j.label ?? "").toLowerCase().includes("vacanc")
          ) && (
            <CarteSuggestionIA
              titre="Vacances approchent"
              description="Préparez vos activités et vos achats pour le séjour"
              source="weekend"
              actionLabel="Suggestions séjour"
              onAction={() => router.push("/famille/weekend")}
            />
          )}

          {/* Anniversaire proche */}
          {contexte?.anniversaires_proches && contexte.anniversaires_proches.length > 0 && (
            <CarteSuggestionIA
              titre="Idées cadeaux"
              description={`Pour ${contexte.anniversaires_proches[0].nom_personne} (${contexte.anniversaires_proches[0].jours_restants}j)`}
              source="achats"
              actionLabel="Voir les idées"
              onAction={() => router.push("/famille/anniversaires")}
            />
          )}

          {/* Achats urgents */}
          {contexte?.achats_urgents && contexte.achats_urgents.length > 0 && (
            <CarteSuggestionIA
              titre="Achats à anticiper"
              description={`${contexte.achats_urgents.length} achat(s) urgent(s) identifié(s) pour la famille`}
              source="achats"
              actionLabel="Ouvrir les achats"
              onAction={() => router.push("/famille/achats")}
            />
          )}

          {/* Fallback */}
          {!isWeekendApproaching &&
            !isSoireeContext &&
            !contexte?.anniversaires_proches?.length &&
            !contexte?.achats_urgents?.length && (
              <p className="text-sm text-muted-foreground text-center py-4">
                Aucune suggestion pour le moment. Revenez jeudi pour les idées weekend !
              </p>
            )}
        </div>
      </section>

      {/* Section 5: Modules (grille compacte) */}
      <GrilleWidgets
        stockageCle="widgets:hub:famille"
        titre="Modules"
        items={MODULES}
        classeGrille="grid gap-3 grid-cols-2 sm:grid-cols-4"
        renderItem={({ id, titre, chemin, Icone }) => {
          const types = MODULES_RAPPELS_MAPPING[id as string] ?? [];
          const nbUrgences = types.length > 0
            ? rappelsUrgents.filter((r) => types.some((t) => r.type?.includes(t))).length
            : 0;
          return (
            <Link key={chemin} href={chemin}>
              <div className="relative h-full">
                {nbUrgences > 0 && (
                  <Badge
                    variant="destructive"
                    className="absolute -top-1 -right-1 h-4 w-4 p-0 text-[10px] flex items-center justify-center z-10"
                  >
                    {nbUrgences}
                  </Badge>
                )}
                <Card className="hover:bg-accent/50 transition-colors h-full">
                  <CardContent className="pt-5 pb-4">
                    <div className="flex flex-col items-center gap-2 text-center">
                      <div className="rounded-lg bg-primary/10 p-2.5">
                        <Icone className="h-5 w-5 text-primary" />
                      </div>
                      <p className="text-sm font-medium">{titre}</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </Link>
          );
        }}
      />

      {/* Dialog Suggestions Weekend IA */}
      <Dialog open={dialogWeekendOuvert} onOpenChange={setDialogWeekendOuvert}>
        <DialogContent className="max-w-lg max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-500" />
              Suggestions weekend IA
            </DialogTitle>
            <DialogDescription>
              Idées d'activités pour le weekend, adaptées à Jules et à la météo
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4 text-sm whitespace-pre-wrap leading-relaxed">
            {suggestionsWeekend ?? "Chargement…"}
          </div>
          <div className="mt-4 flex justify-end">
            <Button variant="outline" size="sm" onClick={() => router.push("/famille/weekend")}>
              Voir plus sur la page Weekend
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
