// ═══════════════════════════════════════════════════════════
// Hub Famille Intelligent — Phase N
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
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
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { BandeauMeteo } from "@/composants/famille/bandeau-meteo";
import { CarteAnniversaire } from "@/composants/famille/carte-anniversaire";
import { CarteDocumentExpire } from "@/composants/famille/carte-document-expire";
import { CarteJourSpecial } from "@/composants/famille/carte-jour-special";
import { CarteSuggestionIA } from "@/composants/famille/carte-suggestion-ia";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirContexteFamilial, evaluerRappelsFamille } from "@/bibliotheque/api/famille";
import { toast } from "sonner";
import { GrilleWidgets } from "@/composants/disposition/grille-widgets";
import type { ContexteFamilial, RappelFamille } from "@/types/famille";

const MODULES = [
  { id: "jules", titre: "Jules", chemin: "/famille/jules", Icone: Baby },
  { id: "budget", titre: "Budget", chemin: "/famille/budget", Icone: Wallet },
  { id: "routines", titre: "Routines", chemin: "/famille/routines", Icone: ListChecks },
  { id: "album", titre: "Album", chemin: "/famille/album", Icone: Camera },
  { id: "contacts", titre: "Contacts", chemin: "/famille/contacts", Icone: BookUser },
  { id: "documents", titre: "Documents", chemin: "/famille/documents", Icone: FileText },
  { id: "calendriers", titre: "Calendriers", chemin: "/famille/calendriers", Icone: Calendar },
];

export default function PageFamille() {
  const router = useRouter();
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
  const rappelsUrgents = rappelsData?.rappels?.filter((r) => r.priorite === "danger" || r.priorite === "warning") ?? [];

  const [hasShownToast, setHasShownToast] = useState(false);

  // Afficher toast pour rappels urgents (J-1, J-2) à l'ouverture
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

  // Détection weekend approchant (jeudi/vendredi)
  const isWeekendApproaching = new Date().getDay() >= 4;

  // Items à venir triés par proximité
  const itemsAVenir = [
    ...(contexte?.anniversaires_proches?.map((a) => ({ type: "anniversaire" as const, data: a, jours: a.jours_restants ?? 999 })) ?? []),
    ...(contexte?.documents_expirants?.map((d) => ({ type: "document" as const, data: d, jours: d.jours_restants ?? 999 })) ?? []),
    ...(contexte?.jours_speciaux?.map((j) => ({ type: "jour_special" as const, data: j, jours: j.jours_restants ?? 999 })) ?? []),
  ].sort((a, b) => a.jours - b.jours);

  const hasItemsAVenir = itemsAVenir.length > 0;

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
        <p className="text-muted-foreground">
          Votre contexte familial en un coup d'œil
        </p>
      </div>

      {/* Section 0: Rappels urgents */}
      {rappelsUrgents.length > 0 && (
        <section>
          <Card className="border-orange-200 bg-orange-50/50 dark:border-orange-800 dark:bg-orange-950/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Bell className="h-4 w-4 text-orange-500" />
                Rappels du moment
                <Badge variant="secondary" className="ml-auto">{rappelsUrgents.length}</Badge>
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
      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Aujourd'hui</h2>

        {/* Météo */}
        {contexte?.meteo && <BandeauMeteo meteo={contexte.meteo} />}

        {/* Routines du moment */}
        {contexte?.routines_du_moment && contexte.routines_du_moment.length > 0 && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Routines du moment</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {contexte.routines_du_moment.map((r) => (
                <div key={r.id} className="flex items-center gap-2 text-sm">
                  <Badge variant="outline">{r.categorie ?? "routine"}</Badge>
                  <span>{r.nom}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Activités aujourd'hui */}
        {contexte?.activites_a_venir && contexte.activites_a_venir.length > 0 && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Activités prévues</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {contexte.activites_a_venir.slice(0, 3).map((a) => (
                <div key={a.id} className="flex items-center gap-2 text-sm">
                  <span className="text-muted-foreground">
                    {a.date ? new Date(a.date).toLocaleDateString("fr-FR", { weekday: "short", day: "numeric" }) : ""}
                  </span>
                  <span>{a.titre}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        )}
      </section>

      {/* Section 2: À venir */}
      {hasItemsAVenir && (
        <section className="space-y-3">
          <h2 className="text-lg font-semibold">À venir</h2>
          <div className="space-y-2">
            {itemsAVenir.slice(0, 5).map((item, idx) => {
              if (item.type === "anniversaire") {
                return (
                  <CarteAnniversaire
                    key={`anniv-${idx}`}
                    anniversaire={item.data}
                  />
                );
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

      {/* Section 3: L'IA suggère */}
      <section className="space-y-3">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-purple-500" />
          L'IA suggère
        </h2>
        <div className="space-y-2">
          {/* Suggestions weekend si jeudi/vendredi */}
          {isWeekendApproaching && (
            <CarteSuggestionIA
              titre="Idées pour le weekend"
              description="Activités adaptées à Jules, avec la météo du weekend"
              source="weekend"
              actionLabel="Voir les suggestions"
              onAction={() => router.push("/famille/weekend")}
            />
          )}

          {/* Si anniversaire proche, suggestion cadeaux */}
          {contexte?.anniversaires_proches && contexte.anniversaires_proches.length > 0 && (
            <CarteSuggestionIA
              titre="Idées cadeaux"
              description={`Pour ${contexte.anniversaires_proches[0].nom_personne} (${contexte.anniversaires_proches[0].jours_restants}j)`}
              source="achats"
              actionLabel="Voir les idées"
              onAction={() => router.push("/famille/anniversaires")}
            />
          )}

          {contexte?.achats_urgents && contexte.achats_urgents.length > 0 && (
            <CarteSuggestionIA
              titre="Achats à anticiper"
              description={`${contexte.achats_urgents.length} achat(s) urgent(s) identifié(s) pour la famille`}
              source="achats"
              actionLabel="Ouvrir les achats"
              onAction={() => router.push("/famille/achats")}
            />
          )}

          {/* Fallback si aucune suggestion */}
          {!isWeekendApproaching && !contexte?.anniversaires_proches?.length && (
            <p className="text-sm text-muted-foreground text-center py-4">
              Aucune suggestion pour le moment. Revenez jeudi pour les idées weekend !
            </p>
          )}
        </div>
      </section>

      {/* Section 4: Modules (grille compacte) */}
      <GrilleWidgets
        stockageCle="widgets:hub:famille"
        titre="Modules"
        items={MODULES}
        classeGrille="grid gap-3 grid-cols-2 sm:grid-cols-3"
        renderItem={({ titre, chemin, Icone }) => (
          <Link key={chemin} href={chemin}>
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
          </Link>
        )}
      />

      {/* Jules context rapide */}
      {contexte?.jules && (
        <Card className="bg-gradient-to-br from-blue-50/50 to-cyan-50/50 dark:from-blue-950/20 dark:to-cyan-950/20">
          <CardContent className="pt-5 pb-4">
            <div className="flex items-center gap-3">
              <Baby className="h-8 w-8 text-blue-500" />
              <div className="flex-1">
                <p className="font-semibold text-sm">Jules — {contexte.jules.age_mois} mois</p>
                {contexte.jules.prochains_jalons && contexte.jules.prochains_jalons.length > 0 && (
                  <p className="text-xs text-muted-foreground">
                    Prochain jalon OMS : {contexte.jules.prochains_jalons[0]}
                  </p>
                )}
              </div>
              <Link href="/famille/jules">
                <Badge variant="outline" className="cursor-pointer hover:bg-accent">
                  Détails →
                </Badge>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
