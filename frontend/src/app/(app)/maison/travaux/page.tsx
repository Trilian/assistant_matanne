// ═══════════════════════════════════════════════════════════
// Travaux — Projets · Entretien · Artisans (fusionnés en tabs)
// Page travaux maison
// ═══════════════════════════════════════════════════════════

"use client";

import { Suspense, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  Hammer, SprayCan, Wrench, Plus, Trash2, Pencil,
  AlertTriangle, CheckCircle2, Activity,
  Phone, Mail, BotMessageSquare,
} from "lucide-react";
import {
  Card, CardContent, CardHeader, CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Skeleton } from "@/composants/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger,
} from "@/composants/ui/dialog";
import {
  Sheet, SheetContent, SheetHeader, SheetTitle,
} from "@/composants/ui/sheet";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/composants/ui/select";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { utiliserDialogCrud } from "@/crochets/utiliser-crud";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerProjets, creerProjet, supprimerProjet, estimerProjetIA,
  listerTachesEntretien, obtenirSanteAppareils, creerTacheEntretien, supprimerTacheEntretien,
  listerArtisans, creerArtisan, modifierArtisan, supprimerArtisan, statsArtisans,
} from "@/bibliotheque/api/maison";
import type { Artisan } from "@/types/maison";
import { toast } from "sonner";
import { BandeauIA } from "@/composants/maison/bandeau-ia";
import { BoutonAchat } from "@/composants/bouton-achat";
import { utiliserAutoCompletionMaison } from "@/crochets/utiliser-auto-completion-maison";

// ─── Couleurs ────────────────────────────────────────────────
const COULEURS_STATUT: Record<string, string> = {
  en_cours: "bg-blue-500/10 text-blue-600",
  a_faire: "bg-yellow-500/10 text-yellow-600",
  termine: "bg-green-500/10 text-green-600",
  annule: "bg-red-500/10 text-red-600",
};
const COULEURS_PRIORITE: Record<string, "default" | "secondary" | "destructive"> = {
  haute: "destructive",
  moyenne: "default",
  basse: "secondary",
};

// ─── Sheet Estimation IA ──────────────────────────────────────
function SheetEstimationIA({
  projetId,
  ouvert,
  onFermer,
}: {
  projetId: number | null;
  ouvert: boolean;
  onFermer: () => void;
}) {
  const { data: estimation, isLoading, error } = utiliserRequete(
    ["maison", "projets", String(projetId ?? ""), "estimation-ia"],
    () => estimerProjetIA(projetId!),
    { enabled: ouvert && projetId !== null, staleTime: 30 * 60 * 1000 }
  );

  return (
    <Sheet open={ouvert} onOpenChange={(o) => !o && onFermer()}>
      <SheetContent className="w-full sm:max-w-lg overflow-y-auto">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <BotMessageSquare className="h-5 w-5 text-primary" />
            Estimation IA
          </SheetTitle>
        </SheetHeader>

        {isLoading && (
          <div className="mt-6 space-y-3">
            <Skeleton className="h-16" />
            <Skeleton className="h-24" />
            <Skeleton className="h-32" />
          </div>
        )}

        {error && (
          <div className="mt-6 text-sm text-destructive">
            Impossible de générer l&apos;estimation. Vérifiez que le projet a une description.
          </div>
        )}

        {estimation && (
          <div className="mt-6 space-y-6">
            {/* Budget */}
            <div className="rounded-lg border bg-muted/30 p-4 space-y-1">
              <p className="text-xs font-semibold text-muted-foreground uppercase">Budget estimé</p>
              <p className="text-2xl font-bold">
                {estimation.budget_estime_min.toLocaleString("fr-FR")} €
                {" – "}
                {estimation.budget_estime_max.toLocaleString("fr-FR")} €
              </p>
              <p className="text-xs text-muted-foreground">
                Durée estimée : {estimation.duree_estimee_jours} jour{estimation.duree_estimee_jours > 1 ? "s" : ""}
              </p>
            </div>

            {/* Tâches */}
            {estimation.taches_suggerees.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase mb-2">Étapes suggérées</p>
                <ol className="space-y-2">
                  {estimation.taches_suggerees.map((t, i) => (
                    <li key={i} className="flex gap-2 text-sm">
                      <span className="font-bold text-primary shrink-0">{i + 1}.</span>
                      <span className="flex-1">{t.nom}
                        {t.duree_estimee_min && <span className="text-muted-foreground text-xs ml-1">({t.duree_estimee_min} min)</span>}
                      </span>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {/* Matériaux */}
            {estimation.materiels_necessaires.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase mb-2">Matériaux nécessaires</p>
                <div className="space-y-2">
                  {estimation.materiels_necessaires.map((m, i) => (
                    <div key={i} className="flex items-center justify-between gap-2 text-sm rounded-md border p-2">
                      <div className="min-w-0">
                        <p className="font-medium truncate">{m.nom} × {m.quantite}</p>
                        {m.magasin_suggere && <p className="text-xs text-muted-foreground">{m.magasin_suggere}</p>}
                        {m.alternatif_eco && <p className="text-xs text-green-600">💡 {m.alternatif_eco}</p>}
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        {m.prix_estime && <span className="text-xs font-semibold">{m.prix_estime} €</span>}
                        <BoutonAchat article={{ nom: m.nom }} taille="xs" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Risques */}
            {estimation.risques_identifies.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase mb-2">Points de vigilance</p>
                <ul className="space-y-1">
                  {estimation.risques_identifies.map((r, i) => (
                    <li key={i} className="flex gap-2 text-sm text-amber-700">
                      <AlertTriangle className="h-3.5 w-3.5 mt-0.5 shrink-0" />{r}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Conseils */}
            {estimation.conseils_ia.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase mb-2">Conseils</p>
                <ul className="space-y-1">
                  {estimation.conseils_ia.map((c, i) => (
                    <li key={i} className="flex gap-2 text-sm">
                      <CheckCircle2 className="h-3.5 w-3.5 mt-0.5 shrink-0 text-green-600" />{c}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}

// ─── Onglet Projets ───────────────────────────────────────────
function OngletProjets() {
  const [statut, setStatut] = useState("tous");
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [etapeCreation, setEtapeCreation] = useState(1);
  const [nomProjet, setNomProjet] = useState("");
  const [descProjet, setDescProjet] = useState("");
  const [prioriteProjet, setPrioriteProjet] = useState("moyenne");
  const [categorieProjet, setCategorieProjet] = useState("");
  const [budgetProjet, setBudgetProjet] = useState("");
  const [tachesSelectionnees, setTachesSelectionnees] = useState<string[]>([]);
  const [estimationProjetId, setEstimationProjetId] = useState<number | null>(null);
  const queryClient = useQueryClient();
  const { autoCompleter } = utiliserAutoCompletionMaison("travaux_projets");

  const suggestionsTaches = [
    "Definir le besoin et les contraintes",
    "Comparer 2 devis minimum",
    "Commander les materiaux",
    "Planifier les etapes",
  ];

  const reinitialiserWizard = () => {
    setEtapeCreation(1);
    setNomProjet("");
    setDescProjet("");
    setPrioriteProjet("moyenne");
    setCategorieProjet("");
    setBudgetProjet("");
    setTachesSelectionnees([]);
  };

  const { data: projets, isLoading } = utiliserRequete(
    ["maison", "projets", statut],
    () => listerProjets(statut === "tous" ? undefined : statut)
  );

  const { mutate: creer, isPending: enCreation } = utiliserMutation(creerProjet, {
    onSuccess: (nouveauProjet) => {
      queryClient.invalidateQueries({ queryKey: ["maison", "projets"] });
      setDialogOuvert(false);
      reinitialiserWizard();
      toast.success("Projet créé");
      toast("💡 Estimer ce projet avec l'IA ?", {
        action: {
          label: "Estimer",
          onClick: () => setEstimationProjetId(nouveauProjet.id),
        },
      });
    },
    onError: () => toast.error("Erreur lors de la création"),
  });

  const { mutate: supprimer } = utiliserMutation(supprimerProjet, {
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["maison", "projets"] }); toast.success("Projet supprimé"); },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <Select value={statut} onValueChange={setStatut}>
          <SelectTrigger className="w-36"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="tous">Tous</SelectItem>
            <SelectItem value="en_cours">En cours</SelectItem>
            <SelectItem value="a_faire">À faire</SelectItem>
            <SelectItem value="termine">Terminé</SelectItem>
          </SelectContent>
        </Select>
        <Dialog
          open={dialogOuvert}
          onOpenChange={(ouvert) => {
            setDialogOuvert(ouvert);
            if (!ouvert) reinitialiserWizard();
          }}
        >
          <DialogTrigger asChild>
            <Button size="sm"><Plus className="mr-2 h-4 w-4" />Nouveau projet</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Wizard projet maison (3 etapes)</DialogTitle>
            </DialogHeader>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (etapeCreation < 3) {
                  setEtapeCreation((v) => v + 1);
                  return;
                }
                const segments = [descProjet.trim()];
                if (categorieProjet.trim()) segments.push(`Type: ${categorieProjet.trim()}`);
                if (budgetProjet.trim()) segments.push(`Budget cible: ${budgetProjet.trim()} EUR`);
                if (tachesSelectionnees.length > 0) {
                  segments.push(`Taches suggerees: ${tachesSelectionnees.join(", ")}`);
                }

                creer({
                  nom: nomProjet,
                  description: segments.filter(Boolean).join(" | ") || undefined,
                  priorite: prioriteProjet,
                  statut: "planifié",
                });
              }}
              className="space-y-4"
            >
              <div className="text-xs text-muted-foreground">Etape {etapeCreation} / 3</div>

              {etapeCreation === 1 && (
                <div className="space-y-2">
                  <Label>Nom du projet</Label>
                  <Input
                    value={nomProjet}
                    onChange={(e) => setNomProjet(e.target.value)}
                    onBlur={(e) => autoCompleter("nom_projet", e.target.value, (v) => { if (!categorieProjet) setCategorieProjet(v); })}
                    required
                    placeholder="Ex: Refaire la salle de bain"
                  />
                  <Label>Description rapide</Label>
                  <Input
                    value={descProjet}
                    onChange={(e) => setDescProjet(e.target.value)}
                    placeholder="Contexte du projet"
                  />
                </div>
              )}

              {etapeCreation === 2 && (
                <div className="space-y-3">
                  <div className="space-y-2">
                    <Label>Type de projet</Label>
                    <Input
                      value={categorieProjet}
                      onChange={(e) => setCategorieProjet(e.target.value)}
                      placeholder="Renovation, energie, menage..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Budget cible (EUR)</Label>
                    <Input
                      type="number"
                      min="0"
                      value={budgetProjet}
                      onChange={(e) => setBudgetProjet(e.target.value)}
                      placeholder="1500"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Priorite</Label>
                    <Select value={prioriteProjet} onValueChange={setPrioriteProjet}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="haute">Haute</SelectItem>
                        <SelectItem value="moyenne">Moyenne</SelectItem>
                        <SelectItem value="basse">Basse</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}

              {etapeCreation === 3 && (
                <div className="space-y-2">
                  <Label>Taches suggerees (IA)</Label>
                  <div className="space-y-2">
                    {suggestionsTaches.map((tache) => {
                      const actif = tachesSelectionnees.includes(tache);
                      return (
                        <button
                          key={tache}
                          type="button"
                          className={`w-full text-left rounded-md border px-3 py-2 text-sm ${actif ? "bg-primary/10 border-primary" : ""}`}
                          onClick={() => {
                            setTachesSelectionnees((prev) =>
                              prev.includes(tache)
                                ? prev.filter((x) => x !== tache)
                                : [...prev, tache]
                            );
                          }}
                        >
                          {tache}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              <div className="flex items-center gap-2">
                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  disabled={etapeCreation === 1 || enCreation}
                  onClick={() => setEtapeCreation((v) => Math.max(1, v - 1))}
                >
                  Retour
                </Button>
                <Button type="submit" disabled={enCreation || !nomProjet.trim()} className="w-full">
                  {enCreation
                    ? "Creation..."
                    : etapeCreation < 3
                      ? "Continuer"
                      : "Creer le projet"}
                </Button>
              </div>

              <Button
                type="button"
                variant="ghost"
                className="w-full"
                onClick={() => {
                  setDialogOuvert(false);
                  reinitialiserWizard();
                }}
              >
                Annuler
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{[1,2,3].map(i => <Skeleton key={i} className="h-32" />)}</div>
      ) : !projets?.length ? (
        <Card><CardContent className="py-10 text-center text-muted-foreground"><Hammer className="h-8 w-8 mx-auto mb-2 opacity-50" />Aucun projet{statut !== "tous" ? " dans ce statut" : ""}</CardContent></Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {projets.map((p) => (
            <Card key={p.id}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-sm">{p.nom}</CardTitle>
                  <Button variant="ghost" size="icon" className="h-7 w-7 shrink-0 text-muted-foreground hover:text-destructive" onClick={() => supprimer(p.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
                </div>
                <div className="flex gap-1.5 flex-wrap">
                  <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${COULEURS_STATUT[p.statut] ?? ""}`}>{p.statut.replace("_", " ")}</span>
                  {p.priorite && <Badge variant={COULEURS_PRIORITE[p.priorite] ?? "outline"} className="text-xs">{p.priorite}</Badge>}
                </div>
              </CardHeader>
              {p.description && <CardContent className="pt-0 pb-2"><p className="text-xs text-muted-foreground line-clamp-2">{p.description}</p></CardContent>}
              <CardContent className="pt-0 pb-3">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full text-xs h-7 gap-1"
                  onClick={() => setEstimationProjetId(p.id)}
                >
                  <BotMessageSquare className="h-3.5 w-3.5" />
                  Estimer avec l&apos;IA
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <SheetEstimationIA
        projetId={estimationProjetId}
        ouvert={estimationProjetId !== null}
        onFermer={() => setEstimationProjetId(null)}
      />
    </div>
  );
}

// ─── Onglet Entretien ─────────────────────────────────────────
function OngletEntretien() {
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [nom, setNom] = useState(""); const [categorie, setCategorie] = useState(""); const [piece, setPiece] = useState(""); const [frequence, setFrequence] = useState("");
  const queryClient = useQueryClient();

  const { data: taches, isLoading: chargementTaches } = utiliserRequete(["maison", "entretien", "taches"], () => listerTachesEntretien());
  const { data: sante, isLoading: chargementSante } = utiliserRequete(["maison", "entretien", "sante"], obtenirSanteAppareils);

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: { nom: string; categorie?: string; piece?: string; frequence_jours?: number }) => creerTacheEntretien({ ...data, fait: false }),
    { onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["maison", "entretien"] }); setDialogOuvert(false); setNom(""); setCategorie(""); setPiece(""); setFrequence(""); toast.success("Tâche créée"); } }
  );

  const { mutate: supprimer } = utiliserMutation((id: number) => supprimerTacheEntretien(id), {
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["maison", "entretien"] }); toast.success("Tâche supprimée"); }
  });

  const tachesEnRetard = taches?.filter((t) => t.prochaine_fois && new Date(t.prochaine_fois) < new Date() && !t.fait) ?? [];
  const tachesNormales = taches?.filter((t) => !tachesEnRetard.includes(t)) ?? [];

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Dialog open={dialogOuvert} onOpenChange={setDialogOuvert}>
          <DialogTrigger asChild><Button size="sm"><Plus className="mr-2 h-4 w-4" />Nouvelle tâche</Button></DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Nouvelle tâche d&apos;entretien</DialogTitle></DialogHeader>
            <form onSubmit={(e) => { e.preventDefault(); creer({ nom, categorie: categorie || undefined, piece: piece || undefined, frequence_jours: frequence ? Number(frequence) : undefined }); }} className="space-y-4">
              <div className="space-y-2"><Label>Nom</Label><Input value={nom} onChange={(e) => setNom(e.target.value)} required /></div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2"><Label>Catégorie</Label><Input value={categorie} onChange={(e) => setCategorie(e.target.value)} /></div>
                <div className="space-y-2"><Label>Pièce</Label><Input value={piece} onChange={(e) => setPiece(e.target.value)} /></div>
              </div>
              <div className="space-y-2"><Label>Fréquence (jours)</Label><Input type="number" value={frequence} onChange={(e) => setFrequence(e.target.value)} /></div>
              <Button type="submit" disabled={enCreation} className="w-full">{enCreation ? "Création…" : "Créer"}</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Santé appareils */}
      {!chargementSante && sante && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2"><Activity className="h-4 w-4" />Santé des appareils<Badge variant={sante.score_global >= 80 ? "secondary" : sante.score_global >= 50 ? "default" : "destructive"} className="ml-auto">{sante.score_global}%</Badge></CardTitle>
          </CardHeader>
          {sante.actions_urgentes?.length > 0 && (
            <CardContent className="pt-0">
              {sante.actions_urgentes.slice(0, 3).map((a, i) => (
                <p key={i} className="text-xs text-muted-foreground flex items-center gap-1"><AlertTriangle className="h-3 w-3 text-amber-500 shrink-0" />{a.tache} ({a.zone})</p>
              ))}
            </CardContent>
          )}
        </Card>
      )}

      {/* Tâches en retard */}
      {tachesEnRetard.length > 0 && (
        <div>
          <p className="text-sm font-medium text-destructive mb-2 flex items-center gap-1.5"><AlertTriangle className="h-4 w-4" />{tachesEnRetard.length} tâche(s) en retard</p>
          <div className="space-y-2">
            {tachesEnRetard.map((t) => (
              <Card key={t.id} className="border-destructive/30">
                <CardContent className="py-3 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-destructive shrink-0" />
                  <div className="flex-1 min-w-0"><p className="text-sm font-medium">{t.nom}</p><p className="text-xs text-muted-foreground">{t.categorie}{t.piece ? ` · ${t.piece}` : ""}</p></div>
                  <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-destructive" onClick={() => supprimer(t.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Autres tâches */}
      {chargementTaches ? (
        <div className="space-y-2">{[1,2,3].map(i => <Skeleton key={i} className="h-14" />)}</div>
      ) : (
        <div className="space-y-2">
          {tachesNormales.map((t) => (
            <Card key={t.id}>
              <CardContent className="py-3 flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-muted-foreground shrink-0" />
                <div className="flex-1 min-w-0"><p className="text-sm">{t.nom}</p><p className="text-xs text-muted-foreground">{t.categorie}{t.piece ? ` · ${t.piece}` : ""}{t.frequence_jours ? ` · tous les ${t.frequence_jours}j` : ""}</p></div>
                <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-destructive" onClick={() => supprimer(t.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
              </CardContent>
            </Card>
          ))}
          {!tachesNormales.length && !tachesEnRetard.length && (
            <Card><CardContent className="py-10 text-center text-muted-foreground"><SprayCan className="h-8 w-8 mx-auto mb-2 opacity-50" />Aucune tâche d&apos;entretien</CardContent></Card>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Onglet Artisans ──────────────────────────────────────────
function OngletArtisans() {
  const [metier] = useState<string | undefined>();
  const formsVide = { nom: "", metier: "", telephone: "", email: "", adresse: "", note_satisfaction: "" };
  const [form, setForm] = useState(formsVide);
  const queryClient = useQueryClient();
  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<Artisan>({
      onOuvrirCreation: () => setForm(formsVide),
      onOuvrirEdition: (a) => setForm({ nom: a.nom, metier: a.metier, telephone: a.telephone ?? "", email: a.email ?? "", adresse: a.adresse ?? "", note_satisfaction: a.note_satisfaction != null ? String(a.note_satisfaction) : "" }),
    });

  const { data: artisans, isLoading } = utiliserRequete(["maison", "artisans", metier ?? "all"], () => listerArtisans(metier));
  const { data: stats } = utiliserRequete(["maison", "artisans", "stats"], statsArtisans);
  const invalider = () => queryClient.invalidateQueries({ queryKey: ["maison", "artisans"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Record<string, unknown>) => creerArtisan(data as Omit<Artisan, "id">),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Artisan ajouté"); } }
  );
  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<Artisan> }) => modifierArtisan(id, data),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Artisan modifié"); } }
  );
  const { mutate: supprimer } = utiliserMutation(supprimerArtisan, { onSuccess: () => { invalider(); toast.success("Artisan supprimé"); } });

  const soumettre = () => {
    const payload = { nom: form.nom, metier: form.metier, telephone: form.telephone || undefined, email: form.email || undefined, adresse: form.adresse || undefined, note_satisfaction: form.note_satisfaction ? Number(form.note_satisfaction) : undefined };
    if (enEdition) modifier({ id: enEdition.id, data: payload });
    else creer(payload as Record<string, unknown>);
  };

  const champsForme = [
    { id: "nom", label: "Nom", type: "text" as const, value: form.nom, onChange: (v: string) => setForm(f => ({ ...f, nom: v })), required: true },
    { id: "metier", label: "Métier", type: "text" as const, value: form.metier, onChange: (v: string) => setForm(f => ({ ...f, metier: v })), required: true },
    { id: "telephone", label: "Téléphone", type: "text" as const, value: form.telephone, onChange: (v: string) => setForm(f => ({ ...f, telephone: v })) },
    { id: "email", label: "Email", type: "email" as const, value: form.email, onChange: (v: string) => setForm(f => ({ ...f, email: v })) },
  ];

  return (
    <div className="space-y-4">
      {stats && (
        <div className="grid gap-3 grid-cols-3">
          <Card><CardContent className="py-3 text-center"><p className="text-xl font-bold">{stats.total_artisans ?? 0}</p><p className="text-xs text-muted-foreground">Artisans</p></CardContent></Card>
          <Card><CardContent className="py-3 text-center"><p className="text-xl font-bold">{stats.total_interventions ?? 0}</p><p className="text-xs text-muted-foreground">Interventions</p></CardContent></Card>
          <Card><CardContent className="py-3 text-center"><p className="text-xl font-bold">{(stats.total_depenses ?? 0).toFixed(0)} €</p><p className="text-xs text-muted-foreground">Dépenses</p></CardContent></Card>
        </div>
      )}

      <div className="flex justify-end">
        <Button size="sm" onClick={ouvrirCreation}><Plus className="mr-2 h-4 w-4" />Ajouter un artisan</Button>
      </div>

      {isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{[1,2,3].map(i => <Skeleton key={i} className="h-28" />)}</div>
      ) : !artisans?.length ? (
        <Card><CardContent className="py-10 text-center text-muted-foreground"><Wrench className="h-8 w-8 mx-auto mb-2 opacity-50" />Aucun artisan enregistré</CardContent></Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {artisans.map((a) => (
            <Card key={a.id}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-sm">{a.nom}</CardTitle>
                    <Badge variant="secondary" className="text-xs mt-1">{a.metier}</Badge>
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => ouvrirEdition(a)}><Pencil className="h-3.5 w-3.5" /></Button>
                    <Button variant="ghost" size="icon" className="h-7 w-7 hover:text-destructive" onClick={() => supprimer(a.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0 space-y-1">
                {a.telephone && <p className="text-xs flex items-center gap-1.5"><Phone className="h-3 w-3" />{a.telephone}</p>}
                {a.email && <p className="text-xs flex items-center gap-1.5"><Mail className="h-3 w-3" />{a.email}</p>}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <DialogueFormulaire
        ouvert={dialogOuvert}
        onChangerOuvert={setDialogOuvert}
        titre={enEdition ? "Modifier l'artisan" : "Ajouter un artisan"}
        champs={champsForme}
        onSoumettre={soumettre}
        enChargement={enCreation || enModif}
      />
    </div>
  );
}

// ─── Page principale ──────────────────────────────────────────
function ContenuTravaux() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const tab = searchParams.get("tab") ?? "projets";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🔧 Travaux</h1>
        <p className="text-muted-foreground">Projets, entretien et artisans</p>
      </div>

      <BandeauIA section="travaux" />

      <Tabs value={tab} onValueChange={(val) => router.replace(`?tab=${val}`)}>
        <TabsList>
          <TabsTrigger value="projets"><Hammer className="h-4 w-4 mr-1.5" />Projets</TabsTrigger>
          <TabsTrigger value="entretien"><SprayCan className="h-4 w-4 mr-1.5" />Entretien</TabsTrigger>
          <TabsTrigger value="artisans"><Wrench className="h-4 w-4 mr-1.5" />Artisans</TabsTrigger>
        </TabsList>
        <TabsContent value="projets" className="mt-4"><OngletProjets /></TabsContent>
        <TabsContent value="entretien" className="mt-4"><OngletEntretien /></TabsContent>
        <TabsContent value="artisans" className="mt-4"><OngletArtisans /></TabsContent>
      </Tabs>
    </div>
  );
}

export default function PageTravaux() {
  return (
    <Suspense fallback={<div className="space-y-4"><Skeleton className="h-8 w-48" /><Skeleton className="h-10 w-64" /><Skeleton className="h-64" /></div>}>
      <ContenuTravaux />
    </Suspense>
  );
}
