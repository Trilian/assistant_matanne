// ═══════════════════════════════════════════════════════════
// Finances — Charges · Dépenses · Énergie (fusionnés en tabs)
// Phase 2B
// ═══════════════════════════════════════════════════════════

"use client";

import { Suspense, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import {
  Receipt, Banknote, Zap, Plus, Trash2, Pencil,
  TrendingUp, TrendingDown, Droplets, Flame, Upload,
} from "lucide-react";
import {
  Card, CardContent, CardHeader, CardTitle, CardDescription,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Skeleton } from "@/composants/ui/skeleton";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Progress } from "@/composants/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/composants/ui/select";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { utiliserDialogCrud } from "@/crochets/utiliser-crud";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerCharges,
  listerDepensesMaison, creerDepenseMaison, modifierDepenseMaison, supprimerDepenseMaison, statsDepensesMaison,
  importerDepensesDepuisTicket,
  creerReleve, supprimerReleve, listerReleves, historiqueEnergie, obtenirPrevisionsEnergie,
} from "@/bibliotheque/api/maison";
import type { DepenseMaison } from "@/types/maison";
import { toast } from "sonner";
import { BandeauIA } from "@/composants/maison/bandeau-ia";

// Lazy-load Recharts pour éviter le SSR
const LineChart = dynamic(() => import("recharts").then(m => m.LineChart), { ssr: false });
const Line = dynamic(() => import("recharts").then(m => m.Line), { ssr: false });
const XAxis = dynamic(() => import("recharts").then(m => m.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then(m => m.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then(m => m.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then(m => m.Tooltip), { ssr: false });
const ResponsiveContainer = dynamic(() => import("recharts").then(m => m.ResponsiveContainer), { ssr: false });

// ─── Onglet Charges ───────────────────────────────────────────
function OngletCharges() {
  const anneeActuelle = new Date().getFullYear();
  const [annee, setAnnee] = useState(anneeActuelle);

  const { data: charges, isLoading } = utiliserRequete(
    ["maison", "charges", String(annee)],
    () => listerCharges(annee)
  );

  const total = charges?.reduce((s: number, c: { montant?: number; montant_annuel?: number }) => s + (c.montant_annuel ?? c.montant ?? 0), 0) ?? 0;

  const parType = charges?.reduce((acc: Record<string, number>, c: { type?: string; montant?: number; montant_annuel?: number }) => {
    const t = c.type ?? "Autre";
    acc[t] = (acc[t] ?? 0) + (c.montant_annuel ?? c.montant ?? 0);
    return acc;
  }, {} as Record<string, number>) ?? {};

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <Select value={String(annee)} onValueChange={(v) => setAnnee(Number(v))}>
          <SelectTrigger className="w-28"><SelectValue /></SelectTrigger>
          <SelectContent>
            {[anneeActuelle, anneeActuelle - 1, anneeActuelle - 2].map(a => (
              <SelectItem key={a} value={String(a)}>{a}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Card className="flex-1"><CardContent className="py-2 flex justify-between items-center"><p className="text-sm text-muted-foreground">Total {annee}</p><p className="text-xl font-bold">{total.toFixed(2)} €</p></CardContent></Card>
      </div>

      {isLoading ? (
        <div className="space-y-2">{[1,2,3].map(i => <Skeleton key={i} className="h-14" />)}</div>
      ) : !charges?.length ? (
        <Card><CardContent className="py-10 text-center text-muted-foreground"><Receipt className="h-8 w-8 mx-auto mb-2 opacity-50" />Aucune charge pour {annee}</CardContent></Card>
      ) : (
        <div className="space-y-3">
          {Object.entries(parType).map(([type, montant]) => (
            <Card key={type}>
              <CardContent className="py-3">
                <div className="flex items-center justify-between mb-1.5">
                  <p className="text-sm font-medium">{type}</p>
                  <p className="text-sm font-semibold">{(montant as number).toFixed(2)} €</p>
                </div>
                <Progress value={Math.min(100, ((montant as number) / Math.max(total, 1)) * 100)} className="h-1.5" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Onglet Dépenses ──────────────────────────────────────────
function OngletDepenses() {
  const formsVide = { libelle: "", montant: "", categorie: "", date: "", fournisseur: "", recurrence: "", notes: "" };
  const [form, setForm] = useState(formsVide);
  const [fichierTicket, setFichierTicket] = useState<File | null>(null);
  const [apercuTicket, setApercuTicket] = useState<DepenseMaison[] | null>(null);
  const [dialogImportOuvert, setDialogImportOuvert] = useState(false);
  const [metaImport, setMetaImport] = useState<{ magasin?: string; confiance_ocr?: number }>({});
  const queryClient = useQueryClient();
  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<DepenseMaison>({
      onOuvrirCreation: () => setForm(formsVide),
      onOuvrirEdition: (d) => setForm({ libelle: d.libelle, montant: String(d.montant), categorie: d.categorie ?? "", date: d.date ?? "", fournisseur: d.fournisseur ?? "", recurrence: d.recurrence ?? "", notes: d.notes ?? "" }),
    });

  const { data: depenses, isLoading } = utiliserRequete(["maison", "depenses"], () => listerDepensesMaison());
  const { data: stats } = utiliserRequete(["maison", "depenses", "stats"], () => statsDepensesMaison());
  const invalider = () => queryClient.invalidateQueries({ queryKey: ["maison", "depenses"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Record<string, unknown>) => creerDepenseMaison(data as Omit<DepenseMaison, "id">),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Dépense créée"); } }
  );
  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<DepenseMaison> }) => modifierDepenseMaison(id, data),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Dépense modifiée"); } }
  );
  const { mutate: supprimer } = utiliserMutation(supprimerDepenseMaison, { onSuccess: () => { invalider(); toast.success("Dépense supprimée"); } });

  const { mutate: analyserTicket, isPending: analyseEnCours } = utiliserMutation(
    (file: File) => importerDepensesDepuisTicket(file, false),
    {
      onSuccess: (result) => {
        setApercuTicket(result.depenses ?? []);
        setMetaImport({ magasin: result.magasin, confiance_ocr: result.confiance_ocr });
        setDialogImportOuvert(true);
      },
      onError: () => toast.error("Impossible d'analyser le ticket"),
    }
  );

  const { mutate: confirmerImport, isPending: importEnCours } = utiliserMutation(
    (file: File) => importerDepensesDepuisTicket(file, true),
    {
      onSuccess: (result) => {
        invalider();
        setDialogImportOuvert(false);
        setFichierTicket(null);
        setApercuTicket(null);
        toast.success(`${result.nb_importees ?? 0} dépenses importées`);
      },
      onError: () => toast.error("Échec de l'import des dépenses"),
    }
  );

  const soumettre = () => {
    const payload = { libelle: form.libelle, montant: Number(form.montant), categorie: form.categorie || undefined, date: form.date || undefined, fournisseur: form.fournisseur || undefined, recurrence: form.recurrence || undefined, notes: form.notes || undefined };
    if (enEdition) modifier({ id: enEdition.id, data: payload });
    else creer(payload as Record<string, unknown>);
  };

  const champs = [
    { id: "libelle", label: "Libellé", type: "text" as const, value: form.libelle, onChange: (v: string) => setForm(f => ({ ...f, libelle: v })), required: true },
    { id: "montant", label: "Montant (€)", type: "number" as const, value: form.montant, onChange: (v: string) => setForm(f => ({ ...f, montant: v })), required: true },
    { id: "categorie", label: "Catégorie", type: "text" as const, value: form.categorie, onChange: (v: string) => setForm(f => ({ ...f, categorie: v })) },
    { id: "date", label: "Date", type: "date" as const, value: form.date, onChange: (v: string) => setForm(f => ({ ...f, date: v })) },
    { id: "fournisseur", label: "Fournisseur", type: "text" as const, value: form.fournisseur, onChange: (v: string) => setForm(f => ({ ...f, fournisseur: v })) },
  ];

  return (
    <div className="space-y-4">
      {stats && (
        <div className="grid grid-cols-2 gap-3">
          <Card><CardContent className="py-3"><p className="text-xs text-muted-foreground">Ce mois</p><p className="text-xl font-bold">{(stats.total_mois_courant ?? 0).toFixed(0)} €</p></CardContent></Card>
          <Card><CardContent className="py-3"><p className="text-xs text-muted-foreground">Cette année</p><p className="text-xl font-bold">{(stats.total_annee_courante ?? 0).toFixed(0)} €</p></CardContent></Card>
        </div>
      )}

      <div className="flex justify-end">
        <div className="flex items-center gap-2">
          <label className="inline-flex">
            <input
              type="file"
              accept="image/png,image/jpeg,image/webp"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (!file) return;
                setFichierTicket(file);
                analyserTicket(file);
              }}
            />
            <Button size="sm" variant="outline" disabled={analyseEnCours} asChild>
              <span>
                <Upload className="mr-2 h-4 w-4" />
                {analyseEnCours ? "Analyse..." : "Importer depuis photo"}
              </span>
            </Button>
          </label>
          <Button size="sm" onClick={ouvrirCreation}><Plus className="mr-2 h-4 w-4" />Ajouter une dépense</Button>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-2">{[1,2,3].map(i => <Skeleton key={i} className="h-14" />)}</div>
      ) : !depenses?.length ? (
        <Card><CardContent className="py-10 text-center text-muted-foreground"><Banknote className="h-8 w-8 mx-auto mb-2 opacity-50" />Aucune dépense enregistrée</CardContent></Card>
      ) : (
        <div className="space-y-2">
          {depenses.map((d: DepenseMaison) => (
            <Card key={d.id}>
              <CardContent className="py-3 flex items-center gap-3">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium">{d.libelle}</p>
                  <p className="text-xs text-muted-foreground">{d.categorie ?? "—"}{d.date ? ` · ${new Date(d.date).toLocaleDateString("fr-FR")}` : ""}</p>
                </div>
                <p className="text-sm font-semibold shrink-0">{d.montant.toFixed(2)} €</p>
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => ouvrirEdition(d)}><Pencil className="h-3.5 w-3.5" /></Button>
                  <Button variant="ghost" size="icon" className="h-7 w-7 hover:text-destructive" onClick={() => supprimer(d.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <DialogueFormulaire
        ouvert={dialogOuvert}
        onChangerOuvert={setDialogOuvert}
        titre={enEdition ? "Modifier la dépense" : "Ajouter une dépense"}
        champs={champs}
        onSoumettre={soumettre}
        enChargement={enCreation || enModif}
      />

      {dialogImportOuvert && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl">
            <CardHeader>
              <CardTitle className="text-base">Aperçu import ticket</CardTitle>
              <CardDescription>
                {metaImport.magasin ? `Magasin: ${metaImport.magasin}` : "Magasin non détecté"}
                {metaImport.confiance_ocr != null && ` · Confiance OCR: ${(metaImport.confiance_ocr * 100).toFixed(0)}%`}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {!apercuTicket?.length ? (
                <p className="text-sm text-muted-foreground">Aucune dépense exploitable détectée.</p>
              ) : (
                <div className="max-h-72 overflow-y-auto space-y-2">
                  {apercuTicket.map((d, idx) => (
                    <div key={`import-${idx}`} className="rounded-md border p-2 flex items-center justify-between gap-3">
                      <div className="min-w-0">
                        <p className="text-sm font-medium truncate">{d.libelle}</p>
                        <p className="text-xs text-muted-foreground truncate">{d.categorie ?? "courses"}</p>
                      </div>
                      <p className="text-sm font-semibold whitespace-nowrap">{Number(d.montant ?? 0).toFixed(2)} €</p>
                    </div>
                  ))}
                </div>
              )}
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setDialogImportOuvert(false)}>Annuler</Button>
                <Button
                  disabled={!fichierTicket || !apercuTicket?.length || importEnCours}
                  onClick={() => {
                    if (fichierTicket) confirmerImport(fichierTicket);
                  }}
                >
                  {importEnCours ? "Import..." : `Importer ${apercuTicket?.length ?? 0} dépenses`}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

// ─── Onglet Énergie ───────────────────────────────────────────
function OngletEnergie() {
  const [compteur, setCompteur] = useState<"electricite" | "eau" | "gaz">("electricite");
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [valeur, setValeur] = useState(""); const [date, setDate] = useState("");
  const queryClient = useQueryClient();

  const { data: historique, isLoading: chargementHisto } = utiliserRequete(["maison", "energie", compteur], () => historiqueEnergie(compteur));
  const { data: previsions } = utiliserRequete(["maison", "energie", compteur, "previsions"], () => obtenirPrevisionsEnergie(compteur));
  const { data: releves } = utiliserRequete(["maison", "energie", compteur, "releves"], () => listerReleves());

  const invalider = () => queryClient.invalidateQueries({ queryKey: ["maison", "energie"] });

  const { mutate: ajouterReleve, isPending } = utiliserMutation(
    (data: { compteur: string; valeur: number; date: string }) =>
      creerReleve({
        type_compteur: data.compteur,
        valeur: data.valeur,
        date_releve: data.date,
      }),
    { onSuccess: () => { invalider(); setDialogOuvert(false); setValeur(""); setDate(""); toast.success("Relevé ajouté"); } }
  );
  const { mutate: supprimerR } = utiliserMutation(supprimerReleve, { onSuccess: () => { invalider(); toast.success("Relevé supprimé"); } });

  const iconeCompteur = compteur === "electricite" ? <Zap className="h-4 w-4" /> : compteur === "eau" ? <Droplets className="h-4 w-4" /> : <Flame className="h-4 w-4" />;
  const unites: Record<string, string> = { electricite: "kWh", eau: "m³", gaz: "m³" };
  const couleurs: Record<string, string> = { electricite: "#f59e0b", eau: "#3b82f6", gaz: "#f97316" };

  return (
    <div className="space-y-4">
      {/* Sélecteur compteur + ajout */}
      <div className="flex gap-2 flex-wrap">
        {(["electricite", "eau", "gaz"] as const).map((c) => (
          <Button key={c} variant={compteur === c ? "default" : "outline"} size="sm" className="capitalize" onClick={() => setCompteur(c)}>
            {c === "electricite" ? <Zap className="mr-1.5 h-3.5 w-3.5" /> : c === "eau" ? <Droplets className="mr-1.5 h-3.5 w-3.5" /> : <Flame className="mr-1.5 h-3.5 w-3.5" />}
            {c}
          </Button>
        ))}
        <Button size="sm" onClick={() => setDialogOuvert(true)} className="ml-auto"><Plus className="mr-2 h-4 w-4" />Relevé</Button>
      </div>

      {/* Prévisions */}
      {previsions && (
        <div className="grid grid-cols-2 gap-3">
          <Card><CardContent className="py-3">
            <p className="text-xs text-muted-foreground flex items-center gap-1">{iconeCompteur}Ce mois (prévu)</p>
            <p className="text-xl font-bold">{previsions.consommation_prevue?.toFixed(1) ?? "-"} {unites[compteur]}</p>
            {previsions.tendance === "hausse" ? <p className="text-xs text-destructive flex items-center gap-1"><TrendingUp className="h-3 w-3" />En hausse</p> : previsions.tendance === "baisse" ? <p className="text-xs text-green-600 flex items-center gap-1"><TrendingDown className="h-3 w-3" />En baisse</p> : null}
          </CardContent></Card>
          <Card><CardContent className="py-3">
            <p className="text-xs text-muted-foreground">Coût prévu</p>
            <p className="text-xl font-bold">{previsions.cout_prevu?.toFixed(2) ?? "-"} €</p>
          </CardContent></Card>
        </div>
      )}

      {/* Graphique */}
      {chargementHisto ? (
        <Skeleton className="h-48" />
      ) : historique?.length ? (
        <Card>
          <CardHeader className="pb-0"><CardTitle className="text-sm">Historique {new Date().getFullYear()}</CardTitle></CardHeader>
          <CardContent>
            <div className="h-40 w-full mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={historique}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="mois" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} unit={` ${unites[compteur]}`} />
                  <Tooltip formatter={(v) => [`${Number(v ?? 0)} ${unites[compteur]}`, "Consommation"]} />
                  <Line type="monotone" dataKey="consommation" stroke={couleurs[compteur]} strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card><CardContent className="py-10 text-center text-muted-foreground"><Zap className="h-8 w-8 mx-auto mb-2 opacity-50" />Aucun historique</CardContent></Card>
      )}

      {/* Derniers relevés */}
      {releves?.slice(0, 5).map((r) => (
        <Card key={r.id}>
          <CardContent className="py-2 flex items-center justify-between">
            <p className="text-sm">{r.valeur} {unites[compteur]} · {new Date(r.date_releve).toLocaleDateString("fr-FR")}</p>
            <Button variant="ghost" size="icon" className="h-7 w-7 hover:text-destructive" onClick={() => supprimerR(r.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
          </CardContent>
        </Card>
      ))}

      {/* Dialog ajout relevé */}
      {dialogOuvert && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-80">
            <CardHeader><CardTitle className="text-sm">Nouveau relevé {compteur}</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-1.5"><Label>Valeur ({unites[compteur]})</Label><Input type="number" value={valeur} onChange={(e) => setValeur(e.target.value)} /></div>
              <div className="space-y-1.5"><Label>Date</Label><Input type="date" value={date} onChange={(e) => setDate(e.target.value)} /></div>
              <div className="flex gap-2">
                <Button variant="outline" className="flex-1" onClick={() => setDialogOuvert(false)}>Annuler</Button>
                <Button className="flex-1" disabled={isPending} onClick={() => valeur && date && ajouterReleve({ compteur, valeur: Number(valeur), date })}>Ajouter</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

// ─── Page principale ──────────────────────────────────────────
function ContenuFinances() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const tab = searchParams.get("tab") ?? "charges";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">💰 Finances</h1>
        <p className="text-muted-foreground">Charges, dépenses et consommation d&apos;énergie</p>
      </div>

      <BandeauIA section="finances" />

      <Tabs value={tab} onValueChange={(val) => router.replace(`?tab=${val}`)}>
        <TabsList>
          <TabsTrigger value="charges"><Receipt className="h-4 w-4 mr-1.5" />Charges</TabsTrigger>
          <TabsTrigger value="depenses"><Banknote className="h-4 w-4 mr-1.5" />Dépenses</TabsTrigger>
          <TabsTrigger value="energie"><Zap className="h-4 w-4 mr-1.5" />Énergie</TabsTrigger>
        </TabsList>
        <TabsContent value="charges" className="mt-4"><OngletCharges /></TabsContent>
        <TabsContent value="depenses" className="mt-4"><OngletDepenses /></TabsContent>
        <TabsContent value="energie" className="mt-4"><OngletEnergie /></TabsContent>
      </Tabs>
    </div>
  );
}

export default function PageFinances() {
  return (
    <Suspense fallback={<div className="space-y-4"><Skeleton className="h-8 w-40" /><Skeleton className="h-10 w-64" /><Skeleton className="h-64" /></div>}>
      <ContenuFinances />
    </Suspense>
  );
}
