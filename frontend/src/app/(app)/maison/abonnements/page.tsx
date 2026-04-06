// Page Abonnements — Comparateur d'abonnements maison

"use client";

import { Suspense, useMemo, useState } from "react";
import {
  BarChart3,
  CalendarClock,
  Pencil,
  Plus,
  Receipt,
  ShieldAlert,
  TrendingDown,
  Trash2,
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
import { Progress } from "@/composants/ui/progress";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/composants/ui/table";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { utiliserSuppressionAnnulable } from "@/crochets/utiliser-suppression-annulable";
import { SwipeableItem } from "@/composants/swipeable-item";
import { useQueryClient } from "@tanstack/react-query";
import { utiliserDialogCrud } from "@/crochets/utiliser-crud";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerAbonnements,
  creerAbonnement,
  modifierAbonnement,
  supprimerAbonnement,
  resumeAbonnements,
  comparerAbonnementsIA,
} from "@/bibliotheque/api/maison";
import type { Abonnement } from "@/types/maison";
import { toast } from "sonner";
import { BandeauIA } from "@/composants/maison/bandeau-ia";
import { SectionReveal } from "@/composants/ui/motion-utils";
import { EtatVide } from "@/composants/ui/etat-vide";
import { ZoneTableauResponsive } from "@/composants/ui/zone-tableau-responsive";
import { BoutonExportCsv } from "@/composants/ui/bouton-export-csv";
import { SkeletonPage } from "@/composants/ui/skeleton-page";

const TYPES_ABONNEMENT = [
  { valeur: "eau", label: "Eau" },
  { valeur: "electricite", label: "Électricité" },
  { valeur: "gaz", label: "Gaz" },
  { valeur: "assurance_habitation", label: "Assurance habitation" },
  { valeur: "assurance_auto", label: "Assurance auto" },
  { valeur: "chaudiere", label: "Chaudière" },
  { valeur: "telephone", label: "Téléphone" },
  { valeur: "internet", label: "Internet" },
];

function formaterEuros(valeur?: number | null): string {
  if (typeof valeur !== "number") {
    return "—";
  }
  return `${valeur.toFixed(2)} €`;
}

function calculerJoursRestants(dateFin?: string): number | null {
  if (!dateFin) {
    return null;
  }

  const fin = new Date(dateFin);
  const diff = fin.getTime() - Date.now();
  return Math.ceil(diff / 86400000);
}

function ContenuAbonnements() {
  const formsVide = {
    type_abonnement: "",
    fournisseur: "",
    prix_mensuel: "",
    date_debut: "",
    date_fin_engagement: "",
    notes: "",
  };
  const [form, setForm] = useState(formsVide);
  const queryClient = useQueryClient();

  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<Abonnement>({
      onOuvrirCreation: () => setForm(formsVide),
      onOuvrirEdition: (a) =>
        setForm({
          type_abonnement: a.type_abonnement,
          fournisseur: a.fournisseur,
          prix_mensuel: a.prix_mensuel?.toString() ?? "",
          date_debut: a.date_debut ?? "",
          date_fin_engagement: a.date_fin_engagement ?? "",
          notes: a.notes ?? "",
        }),
    });

  const { data: abonnements, isLoading } = utiliserRequete(["maison", "abonnements"], listerAbonnements);
  const { data: resume } = utiliserRequete(["maison", "abonnements", "resume"], resumeAbonnements);

  // Comparaison IA (triggered manually, cache 1h)
  const { data: analyseia, isFetching: chargAnalyseIA, refetch: lancerAnalyseIA } = utiliserRequete(
    ["maison", "abonnements", "ia-comparaison"],
    comparerAbonnementsIA,
    { enabled: false, staleTime: 60 * 60 * 1000 }
  );

  const invalider = () => queryClient.invalidateQueries({ queryKey: ["maison", "abonnements"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Parameters<typeof creerAbonnement>[0]) => creerAbonnement(data),
    {
      onSuccess: () => {
        invalider();
        fermerDialog();
        toast.success("Abonnement ajouté");
      },
    }
  );
  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<Abonnement> }) => modifierAbonnement(id, data),
    {
      onSuccess: () => {
        invalider();
        fermerDialog();
        toast.success("Abonnement modifié");
      },
    }
  );
  const { mutate: supprimer } = utiliserMutation(supprimerAbonnement, {
    onSuccess: () => {
      invalider();
      toast.success("Abonnement supprimé");
    },
  });
  const { planifierSuppression } = utiliserSuppressionAnnulable();

  const abonnementsTries = useMemo(
    () => [...(abonnements ?? [])].sort((a, b) => (b.prix_mensuel ?? 0) - (a.prix_mensuel ?? 0)),
    [abonnements]
  );
  const economiePotentielle = useMemo(
    () =>
      abonnementsTries.reduce((total, abo) => {
        if (
          typeof abo.prix_mensuel === "number" &&
          typeof abo.meilleur_prix_trouve === "number" &&
          abo.meilleur_prix_trouve < abo.prix_mensuel
        ) {
          return total + (abo.prix_mensuel - abo.meilleur_prix_trouve);
        }
        return total;
      }, 0),
    [abonnementsTries]
  );
  const engagementsProches = useMemo(
    () => abonnementsTries.filter((abo) => {
      const jours = calculerJoursRestants(abo.date_fin_engagement);
      return jours !== null && jours >= 0 && jours <= 60;
    }),
    [abonnementsTries]
  );
  const maxMensuel = useMemo(
    () => Math.max(1, ...abonnementsTries.map((abo) => abo.prix_mensuel ?? 0)),
    [abonnementsTries]
  );
  const donneesExport = useMemo(
    () => abonnementsTries.map((abo) => ({
      type: TYPES_ABONNEMENT.find((item) => item.valeur === abo.type_abonnement)?.label ?? abo.type_abonnement,
      fournisseur: abo.fournisseur,
      prix_mensuel: abo.prix_mensuel ?? "",
      prix_annuel: typeof abo.prix_mensuel === "number" ? (abo.prix_mensuel * 12).toFixed(2) : "",
      fin_engagement: abo.date_fin_engagement ?? "",
      fournisseur_alternatif: abo.fournisseur_alternatif ?? "",
      meilleur_prix: abo.meilleur_prix_trouve ?? "",
      notes: abo.notes ?? "",
    })),
    [abonnementsTries]
  );
  const repartitionTypes = useMemo(
    () =>
      Object.entries(resume?.par_type ?? {}).sort(([, montantA], [, montantB]) => Number(montantB) - Number(montantA)),
    [resume]
  );

  const supprimerAvecUndo = (a: Abonnement) => {
    planifierSuppression(`abo-${a.id}`, {
      libelle: `${a.fournisseur} (${a.type_abonnement})`,
      onConfirmer: () => supprimer(a.id),
      onErreur: () => toast.error("Erreur lors de la suppression"),
    });
  };

  const soumettre = () => {
    const payload: Parameters<typeof creerAbonnement>[0] = {
      type_abonnement: form.type_abonnement,
      fournisseur: form.fournisseur,
      prix_mensuel: form.prix_mensuel ? parseFloat(form.prix_mensuel) : undefined,
      date_debut: form.date_debut || undefined,
      date_fin_engagement: form.date_fin_engagement || undefined,
      notes: form.notes || undefined,
    };
    if (enEdition) {
      modifier({ id: enEdition.id, data: payload });
    } else {
      creer(payload);
    }
  };

  const CHAMPS = [
    {
      id: "type_abonnement",
      label: "Type",
      type: "select" as const,
      value: form.type_abonnement,
      onChange: (v: string) => setForm((f) => ({ ...f, type_abonnement: v })),
      required: true,
      options: TYPES_ABONNEMENT,
    },
    {
      id: "fournisseur",
      label: "Fournisseur",
      type: "text" as const,
      value: form.fournisseur,
      onChange: (v: string) => setForm((f) => ({ ...f, fournisseur: v })),
      required: true,
    },
    {
      id: "prix_mensuel",
      label: "Prix mensuel (€)",
      type: "number" as const,
      value: form.prix_mensuel,
      onChange: (v: string) => setForm((f) => ({ ...f, prix_mensuel: v })),
    },
    {
      id: "date_debut",
      label: "Date de début",
      type: "date" as const,
      value: form.date_debut,
      onChange: (v: string) => setForm((f) => ({ ...f, date_debut: v })),
    },
    {
      id: "date_fin_engagement",
      label: "Fin d'engagement",
      type: "date" as const,
      value: form.date_fin_engagement,
      onChange: (v: string) => setForm((f) => ({ ...f, date_fin_engagement: v })),
    },
    {
      id: "notes",
      label: "Notes",
      type: "textarea" as const,
      value: form.notes,
      onChange: (v: string) => setForm((f) => ({ ...f, notes: v })),
    },
  ];

  return (
    <div className="space-y-6">
      <SectionReveal className="space-y-2">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">📋 Abonnements</h1>
          <p className="text-muted-foreground">Comparateur visuel d&apos;abonnements maison et suivi des contrats.</p>
        </div>
      </SectionReveal>

      <SectionReveal delay={0.03}>
        <BandeauIA section="abonnements" />
      </SectionReveal>

      {/* G6 — Analyse IA des abonnements */}
      <SectionReveal delay={0.04}>
        <Card className="border-purple-200 dark:border-purple-800">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                🧠 Comparateur IA
              </CardTitle>
              <Button
                size="sm"
                variant="outline"
                onClick={() => void lancerAnalyseIA()}
                disabled={chargAnalyseIA}
                className="gap-1.5"
              >
                <TrendingDown className={`h-3.5 w-3.5 ${chargAnalyseIA ? "animate-pulse" : ""}`} />
                {chargAnalyseIA ? "Analyse…" : "Analyser mes contrats"}
              </Button>
            </div>
            {analyseia && (
              <CardDescription>{analyseia.resume}</CardDescription>
            )}
          </CardHeader>
          {analyseia && analyseia.conseils.length > 0 && (
            <CardContent className="space-y-2 pt-0">
              {analyseia.conseils.map((c, i) => (
                <div key={i} className="rounded-lg border p-3 space-y-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="text-sm font-semibold">{c.titre}</p>
                    <Badge variant={c.priorite === "haute" ? "destructive" : c.priorite === "moyenne" ? "secondary" : "outline"} className="text-xs">
                      {c.priorite}
                    </Badge>
                    {c.economies_estimees_eur != null && c.economies_estimees_eur > 0 && (
                      <span className="ml-auto text-xs font-medium text-green-600 dark:text-green-400">
                        −{c.economies_estimees_eur.toFixed(0)} €/mois
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">{c.detail}</p>
                </div>
              ))}
              <p className="text-xs text-muted-foreground text-right">
                Économies potentielles&nbsp;: <strong>{analyseia.economies_potentielles_eur.toFixed(0)} €/mois</strong>
              </p>
            </CardContent>
          )}
        </Card>
      </SectionReveal>

      {resume ? (
        <SectionReveal delay={0.05} className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <Card>
            <CardContent className="py-3 text-center">
              <p className="text-xs text-muted-foreground">Coût mensuel</p>
              <p className="text-lg font-bold">{formaterEuros(resume.total_mensuel)}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="py-3 text-center">
              <p className="text-xs text-muted-foreground">Coût annuel</p>
              <p className="text-lg font-bold">{formaterEuros(resume.total_annuel)}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="py-3 text-center">
              <p className="text-xs text-muted-foreground">Économie potentielle</p>
              <p className="text-lg font-bold text-emerald-600">{formaterEuros(economiePotentielle)}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="py-3 text-center">
              <p className="text-xs text-muted-foreground">Engagements proches</p>
              <p className="text-lg font-bold">{engagementsProches.length}</p>
            </CardContent>
          </Card>
        </SectionReveal>
      ) : null}

      <SectionReveal delay={0.07} className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <BoutonExportCsv
            data={donneesExport}
            filename={`abonnements-maison-${new Date().toISOString().slice(0, 10)}.csv`}
            label="Exporter CSV"
          />
        </div>
        <Button size="sm" onClick={ouvrirCreation}>
          <Plus className="mr-2 h-4 w-4" />Ajouter
        </Button>
      </SectionReveal>

      {isLoading ? (
        <SkeletonPage
          ariaLabel="Chargement des abonnements"
          lignes={["h-8 w-44", "h-24 w-full", "h-64 w-full", "h-20 w-full"]}
        />
      ) : !abonnementsTries.length ? (
        <EtatVide
          Icone={Receipt}
          titre="Aucun abonnement enregistré"
          description="Ajoutez vos contrats pour comparer les coûts, suivre les engagements et repérer les alternatives intéressantes."
          action={
            <Button size="sm" onClick={ouvrirCreation}>
              <Plus className="mr-2 h-4 w-4" />Ajouter mon premier abonnement
            </Button>
          }
        />
      ) : (
        <>
          <SectionReveal delay={0.09} className="grid gap-4 xl:grid-cols-[1.4fr_0.8fr]">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <BarChart3 className="h-4 w-4" />Comparateur visuel
                </CardTitle>
                <CardDescription>
                  Lecture rapide des postes les plus coûteux, des fins d&apos;engagement et des alternatives détectées.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ZoneTableauResponsive containerClassName="rounded-lg border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Contrat</TableHead>
                        <TableHead>Coût</TableHead>
                        <TableHead>Engagement</TableHead>
                        <TableHead>Alternative</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {abonnementsTries.map((abo) => {
                        const joursRestants = calculerJoursRestants(abo.date_fin_engagement);
                        const largeurBarre = abo.prix_mensuel
                          ? Math.max(12, (abo.prix_mensuel / maxMensuel) * 100)
                          : 12;
                        return (
                          <TableRow key={`comparatif-${abo.id}`}>
                            <TableCell>
                              <div className="space-y-1">
                                <p className="font-medium">{abo.fournisseur}</p>
                                <p className="text-xs text-muted-foreground">
                                  {TYPES_ABONNEMENT.find((item) => item.valeur === abo.type_abonnement)?.label ?? abo.type_abonnement}
                                </p>
                              </div>
                            </TableCell>
                            <TableCell>
                              <div className="flex min-w-[170px] items-center gap-2">
                                <Progress value={largeurBarre} className="h-2 flex-1" />
                                <span className="text-xs font-medium">{formaterEuros(abo.prix_mensuel)}</span>
                              </div>
                              <p className="mt-1 text-[11px] text-muted-foreground">{formaterEuros((abo.prix_mensuel ?? 0) * 12)} / an</p>
                            </TableCell>
                            <TableCell>
                              {joursRestants === null ? (
                                <span className="text-xs text-muted-foreground">Libre</span>
                              ) : joursRestants < 0 ? (
                                <Badge variant="outline">Échu</Badge>
                              ) : joursRestants <= 60 ? (
                                <Badge className="bg-amber-100 text-amber-800 hover:bg-amber-100">{joursRestants} j</Badge>
                              ) : (
                                <span className="text-xs text-muted-foreground">{joursRestants} j</span>
                              )}
                            </TableCell>
                            <TableCell>
                              {typeof abo.meilleur_prix_trouve === "number" &&
                              typeof abo.prix_mensuel === "number" &&
                              abo.meilleur_prix_trouve < abo.prix_mensuel ? (
                                <div className="text-xs text-emerald-700">
                                  <p className="font-medium">{abo.fournisseur_alternatif ?? "Alternative"}</p>
                                  <p>−{(abo.prix_mensuel - abo.meilleur_prix_trouve).toFixed(2)} € / mois</p>
                                </div>
                              ) : (
                                <span className="text-xs text-muted-foreground">RAS</span>
                              )}
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </ZoneTableauResponsive>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <ShieldAlert className="h-4 w-4" />Points d&apos;attention
                </CardTitle>
                <CardDescription>Priorités à regarder cette semaine.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {engagementsProches.length ? (
                  engagementsProches.slice(0, 4).map((abo) => {
                    const joursRestants = calculerJoursRestants(abo.date_fin_engagement);
                    return (
                      <div key={`alerte-${abo.id}`} className="rounded-lg border p-3">
                        <p className="text-sm font-medium">{abo.fournisseur}</p>
                        <p className="text-xs text-muted-foreground">
                          {TYPES_ABONNEMENT.find((item) => item.valeur === abo.type_abonnement)?.label ?? abo.type_abonnement}
                        </p>
                        <p className="mt-1 text-xs text-amber-700">
                          Fin d&apos;engagement dans {joursRestants} jour(s)
                        </p>
                      </div>
                    );
                  })
                ) : (
                  <EtatVide
                    Icone={CalendarClock}
                    titre="Aucune échéance proche"
                    description="Les contrats en cours n’ont pas de fin d’engagement imminente."
                    className="p-5"
                  />
                )}

                {repartitionTypes.length ? (
                  <div className="space-y-2 rounded-lg border p-3">
                    <p className="text-sm font-medium">Répartition mensuelle</p>
                    {repartitionTypes.map(([type, montant]) => {
                      const largeur = resume?.total_mensuel ? Math.max(10, (Number(montant) / resume.total_mensuel) * 100) : 10;
                      return (
                        <div key={type} className="space-y-1">
                          <div className="flex items-center justify-between text-xs">
                            <span>{TYPES_ABONNEMENT.find((item) => item.valeur === type)?.label ?? type}</span>
                            <span>{formaterEuros(Number(montant))}</span>
                          </div>
                          <Progress value={largeur} className="h-1.5" />
                        </div>
                      );
                    })}
                  </div>
                ) : null}
              </CardContent>
            </Card>
          </SectionReveal>

          <SectionReveal delay={0.12} className="space-y-2">
            {abonnementsTries.map((abo) => {
              const finEngagement = abo.date_fin_engagement ? new Date(abo.date_fin_engagement) : null;
              const soonExpiring =
                finEngagement &&
                finEngagement.getTime() - Date.now() < 30 * 86400000 &&
                finEngagement.getTime() > Date.now();

              return (
                <SwipeableItem
                  key={abo.id}
                  labelGauche="Supprimer"
                  labelDroit="Modifier"
                  onSwipeLeft={() => supprimerAvecUndo(abo)}
                  onSwipeRight={() => ouvrirEdition(abo)}
                >
                  <Card className={soonExpiring ? "border-amber-300" : ""}>
                    <CardContent className="flex items-center gap-2 py-3">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-medium">{abo.fournisseur}</p>
                          <Badge variant="secondary" className="text-[10px]">
                            {TYPES_ABONNEMENT.find((t) => t.valeur === abo.type_abonnement)?.label ?? abo.type_abonnement}
                          </Badge>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {typeof abo.prix_mensuel === "number" ? `${abo.prix_mensuel.toFixed(2)} €/mois` : "—"}
                          {finEngagement && ` · engagement jusqu'au ${finEngagement.toLocaleDateString("fr-FR")}`}
                        </p>
                        {abo.meilleur_prix_trouve &&
                          abo.prix_mensuel &&
                          abo.meilleur_prix_trouve < abo.prix_mensuel && (
                            <p className="mt-0.5 flex items-center gap-1 text-xs text-green-600">
                              <TrendingDown className="h-3 w-3" />
                              {abo.fournisseur_alternatif}: {abo.meilleur_prix_trouve.toFixed(2)} €/mois
                              (−{(abo.prix_mensuel - abo.meilleur_prix_trouve).toFixed(2)} €)
                            </p>
                          )}
                      </div>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => ouvrirEdition(abo)}>
                          <Pencil className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 hover:text-destructive"
                          onClick={() => supprimerAvecUndo(abo)}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </SwipeableItem>
              );
            })}
          </SectionReveal>
        </>
      )}

      <DialogueFormulaire
        ouvert={dialogOuvert}
        onChangerOuvert={setDialogOuvert}
        titre={enEdition ? "Modifier l'abonnement" : "Ajouter un abonnement"}
        champs={CHAMPS}
        onSoumettre={soumettre}
        enChargement={enCreation || enModif}
      />
    </div>
  );
}

export default function PageAbonnements() {
  return (
    <Suspense
      fallback={
        <SkeletonPage
          ariaLabel="Chargement du comparateur d'abonnements"
          lignes={["h-8 w-48", "h-24 w-full", "h-64 w-full", "h-40 w-full"]}
        />
      }
    >
      <ContenuAbonnements />
    </Suspense>
  );
}
