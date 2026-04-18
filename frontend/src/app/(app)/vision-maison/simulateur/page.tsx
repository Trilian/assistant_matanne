"use client";

import { useMemo, useState } from "react";
import {
  AlertTriangle,
  Calculator,
  CheckCircle2,
  Hammer,
  Home,
  Info,
  TrendingUp,
  XCircle,
} from "lucide-react";
import { EntetePageHabitat } from "@/composants/habitat/entete-page-habitat";
import { Badge } from "@/composants/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Slider } from "@/composants/ui/slider";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { cn } from "@/bibliotheque/utils";

// ═══════════════════════════════════════════════════════════
// Situation actuelle — données issues du dossier (fixes)
// ═══════════════════════════════════════════════════════════
const SITUATION = {
  valeurEstimee: 390_000,
  creditRestant: 235_458,
  mensualiteActuelle: 1_101.32,
  interetsMensuels: 233.83,
  assuranceMensuelle: 51.15,
  echeancesRestantes: 254,
  tauxDebiteur: 0.012,
  tauxAssurance: 0.0026,
} as const;

// Apport disponible si vente aujourd'hui
// Frais d'agence à la charge de l'acheteur → vendeur reçoit le prix net plein
const IRA = Math.min(SITUATION.interetsMensuels * 6, SITUATION.creditRestant * 0.03);
const APPORT_DISPONIBLE = SITUATION.valeurEstimee - IRA - SITUATION.creditRestant; // ≈ 153 139 €

// Coûts par défaut des features manquantes (modifiables inline)
const COUTS_DEFAUT = {
  chambres: 40_000,
  terrain: 22_000,
  piscine: 35_000,
  abri: 5_000,
  garage: 10_000,
  bureau: 10_000,
} as const;

// ═══════════════════════════════════════════════════════════
// Utilitaires
// ═══════════════════════════════════════════════════════════
function pmt(montant: number, tauxAnnuel: number, dureeAns: number): number {
  if (montant <= 0) return 0;
  const r = tauxAnnuel / 12;
  const n = dureeAns * 12;
  if (r === 0) return montant / n;
  return (montant * r) / (1 - Math.pow(1 + r, -n));
}

function eur(valeur: number, dec = 0): string {
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: dec,
    maximumFractionDigits: dec,
  }).format(valeur);
}

function pct(valeur: number): string {
  return new Intl.NumberFormat("fr-FR", {
    style: "percent",
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(valeur);
}

// ═══════════════════════════════════════════════════════════
// Composants UI internes
// ═══════════════════════════════════════════════════════════
type CouleurCarte = "neutre" | "vert" | "rouge" | "orange";

interface CarteProps {
  libelle: string;
  valeur: string;
  sousTitre?: string;
  couleur?: CouleurCarte;
}

function Carte({ libelle, valeur, sousTitre, couleur = "neutre" }: CarteProps) {
  const bg: Record<CouleurCarte, string> = {
    neutre: "bg-muted/40 border-border",
    vert: "bg-green-50 border-green-200 dark:bg-green-950/30 dark:border-green-800",
    rouge: "bg-red-50 border-red-200 dark:bg-red-950/30 dark:border-red-800",
    orange: "bg-amber-50 border-amber-200 dark:bg-amber-950/30 dark:border-amber-800",
  };
  const text: Record<CouleurCarte, string> = {
    neutre: "text-foreground",
    vert: "text-green-700 dark:text-green-300",
    rouge: "text-red-700 dark:text-red-300",
    orange: "text-amber-700 dark:text-amber-300",
  };
  return (
    <div className={cn("rounded-xl border p-4", bg[couleur])}>
      <p className="text-xs uppercase tracking-widest text-muted-foreground">{libelle}</p>
      <p className={cn("mt-1 text-2xl font-semibold", text[couleur])}>{valeur}</p>
      {sousTitre && <p className="mt-0.5 text-xs text-muted-foreground">{sousTitre}</p>}
    </div>
  );
}

interface VerdictProps {
  ok: boolean;
  texte: string;
}

function Verdict({ ok, texte }: VerdictProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium",
        ok
          ? "bg-green-100 text-green-800 dark:bg-green-950/40 dark:text-green-200"
          : "bg-red-100 text-red-800 dark:bg-red-950/40 dark:text-red-200"
      )}
    >
      {ok ? (
        <CheckCircle2 className="h-4 w-4 shrink-0" />
      ) : (
        <XCircle className="h-4 w-4 shrink-0" />
      )}
      {texte}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Tab 1 — Déménager
// ═══════════════════════════════════════════════════════════
const LABEL_FEATURES: Record<string, string> = {
  chambres: "4 chambres",
  terrain: "Terrain plat",
  piscine: "Piscine",
  abri: "Abri de jardin",
  garage: "Garage / carport",
  bureau: "Bureau",
};

function TabDemenager() {
  const [prixMaison, setPrixMaison] = useState(450_000);
  const [tauxCredit, setTauxCredit] = useState(3.5);
  const [duree, setDuree] = useState(25);
  const [revenus, setRevenus] = useState(0);
  const [couts, setCouts] = useState<Record<string, number>>({ ...COUTS_DEFAUT });
  const [features, setFeatures] = useState<Record<string, boolean>>({
    chambres: true,
    terrain: true,
    piscine: true,
    abri: true,
    garage: true,
    bureau: true,
  });

  const r = useMemo(() => {
    const featuresManquantes = Object.entries(features)
      .filter(([, present]) => !present)
      .reduce((acc, [key]) => acc + (couts[key] ?? 0), 0);
    const coutReel = prixMaison + featuresManquantes;
    const fraisNotaire = coutReel * 0.075;
    const totalAcquisition = coutReel + fraisNotaire;
    const nouveauPret = Math.max(0, totalAcquisition - APPORT_DISPONIBLE);
    const mensualiteHorsAss = pmt(nouveauPret, tauxCredit / 100, duree);
    const assurance = (nouveauPret * SITUATION.tauxAssurance) / 12;
    const mensualiteTotal = mensualiteHorsAss + assurance;
    const deltaMensuel = mensualiteTotal - SITUATION.mensualiteActuelle;
    const tauxEndettement = revenus > 0 ? mensualiteTotal / revenus : null;
    const totalInterets = mensualiteTotal * duree * 12 - nouveauPret;
    const interetsActuels = SITUATION.interetsMensuels * SITUATION.echeancesRestantes;
    return {
      featuresManquantes,
      coutReel,
      fraisNotaire,
      totalAcquisition,
      nouveauPret,
      mensualiteTotal,
      deltaMensuel,
      tauxEndettement,
      totalInterets,
      surcout: totalInterets - interetsActuels,
    };
  }, [prixMaison, tauxCredit, duree, revenus, features, couts]);

  const endettementOk = r.tauxEndettement === null || r.tauxEndettement <= 0.35;

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* ── Colonne inputs ── */}
      <div className="space-y-6">
        {/* Rappel apport */}
        <Card className="border-blue-200 bg-blue-50/50 dark:border-blue-900 dark:bg-blue-950/20">
          <CardContent className="flex items-start gap-2 pt-4 text-sm text-blue-700 dark:text-blue-300">
            <Info className="mt-0.5 h-4 w-4 shrink-0" />
            <span>
              Apport disponible si vente :{" "}
              <strong>{eur(APPORT_DISPONIBLE)}</strong> — frais d'agence à la
              charge de l'acheteur, déduction IRA ({eur(IRA, 0)}) +
              remboursement crédit ({eur(SITUATION.creditRestant)})
            </span>
          </CardContent>
        </Card>

        {/* Slider prix */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Prix de la maison cible</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="mb-2 flex justify-between text-sm">
                <span className="text-muted-foreground">Prix affiché</span>
                <span className="font-semibold">{eur(prixMaison)}</span>
              </div>
              <Slider
                value={[prixMaison]}
                onValueChange={([v]) => setPrixMaison(v)}
                min={200_000}
                max={700_000}
                step={5_000}
              />
              <div className="mt-1 flex justify-between text-xs text-muted-foreground">
                <span>200 k</span>
                <span>700 k</span>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <Label className="text-xs text-muted-foreground">
                  Taux crédit (%)
                </Label>
                <Input
                  type="number"
                  value={tauxCredit}
                  onChange={(e) => setTauxCredit(Number(e.target.value))}
                  step={0.05}
                  min={0.5}
                  max={8}
                  className="mt-1"
                />
              </div>
              <div>
                <Label className="text-xs text-muted-foreground">
                  Durée (ans)
                </Label>
                <Input
                  type="number"
                  value={duree}
                  onChange={(e) => setDuree(Number(e.target.value))}
                  min={10}
                  max={30}
                  className="mt-1"
                />
              </div>
              <div>
                <Label className="text-xs text-muted-foreground">
                  Revenus nets/mois
                </Label>
                <Input
                  type="number"
                  value={revenus || ""}
                  onChange={(e) => setRevenus(Number(e.target.value))}
                  placeholder="ex : 5 000"
                  className="mt-1"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Critères / features */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">
              Équipements présents dans la maison ?
            </CardTitle>
            <p className="text-xs text-muted-foreground">
              Décocher = coût de travaux ajouté au prix réel
            </p>
          </CardHeader>
          <CardContent className="space-y-3">
            {Object.entries(features).map(([key, present]) => (
              <div key={key} className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id={`f-${key}`}
                    checked={present}
                    onChange={(e) =>
                      setFeatures((prev) => ({
                        ...prev,
                        [key]: e.target.checked,
                      }))
                    }
                    className="h-4 w-4 cursor-pointer rounded"
                  />
                  <label
                    htmlFor={`f-${key}`}
                    className="cursor-pointer select-none text-sm"
                  >
                    {LABEL_FEATURES[key]}
                  </label>
                </div>
                <div className="flex items-center gap-1">
                  {!present ? (
                    <>
                      <Input
                        type="number"
                        value={couts[key] ?? 0}
                        onChange={(e) =>
                          setCouts((prev) => ({
                            ...prev,
                            [key]: Number(e.target.value),
                          }))
                        }
                        step={1_000}
                        className="h-7 w-28 text-right text-xs"
                      />
                      <span className="text-xs text-red-500">€</span>
                    </>
                  ) : (
                    <Badge variant="secondary" className="text-xs">
                      ✓ inclus
                    </Badge>
                  )}
                </div>
              </div>
            ))}
            {r.featuresManquantes > 0 && (
              <div className="mt-2 rounded-lg bg-red-50 px-3 py-2 text-sm dark:bg-red-950/20">
                <span className="text-muted-foreground">
                  Travaux complémentaires :{" "}
                </span>
                <span className="font-semibold text-red-600 dark:text-red-400">
                  {eur(r.featuresManquantes)}
                </span>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* ── Colonne résultats ── */}
      <div className="space-y-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Coût total d'acquisition</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-2">
            <Carte libelle="Prix affiché" valeur={eur(prixMaison)} />
            <Carte
              libelle="+ Travaux manquants"
              valeur={eur(r.featuresManquantes)}
              couleur={r.featuresManquantes > 0 ? "rouge" : "neutre"}
            />
            <Carte libelle="Coût réel maison" valeur={eur(r.coutReel)} />
            <Carte
              libelle="+ Frais notaire (7,5 %)"
              valeur={eur(r.fraisNotaire)}
            />
            <Carte
              libelle="Total acquisition"
              valeur={eur(r.totalAcquisition)}
            />
            <Carte
              libelle="− Apport disponible"
              valeur={`− ${eur(APPORT_DISPONIBLE)}`}
              couleur="vert"
            />
            <Carte
              libelle="Nouveau prêt"
              valeur={eur(r.nouveauPret)}
              couleur="orange"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Mensualité & endettement</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid gap-3 sm:grid-cols-2">
              <Carte
                libelle="Nouvelle mensualité"
                valeur={eur(r.mensualiteTotal, 2)}
                couleur="orange"
              />
              <Carte
                libelle="Delta / mois"
                valeur={`${r.deltaMensuel > 0 ? "+" : ""}${eur(r.deltaMensuel, 2)}`}
                sousTitre={`vs ${eur(SITUATION.mensualiteActuelle, 2)} actuels`}
                couleur={
                  r.deltaMensuel > 600
                    ? "rouge"
                    : r.deltaMensuel > 0
                      ? "orange"
                      : "vert"
                }
              />
            </div>

            {r.tauxEndettement !== null && (
              <Verdict
                ok={endettementOk}
                texte={`Taux endettement : ${pct(r.tauxEndettement)} ${endettementOk ? "(≤ 35 % ✓)" : "(> 35 % — refus probable)"}`}
              />
            )}

            <div className="space-y-1 rounded-lg bg-muted/40 p-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">
                  Total intérêts nouveau prêt
                </span>
                <span className="font-medium">{eur(r.totalInterets)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">
                  Surcoût vs intérêts restants actuels
                </span>
                <span
                  className={cn(
                    "font-semibold",
                    r.surcout > 0
                      ? "text-red-600 dark:text-red-400"
                      : "text-green-600 dark:text-green-400"
                  )}
                >
                  {r.surcout > 0 ? "+" : ""}
                  {eur(r.surcout)}
                </span>
              </div>
            </div>

            <Verdict
              ok={r.deltaMensuel < 600 && endettementOk}
              texte={
                !endettementOk
                  ? "Taux endettement trop élevé — réduire le prix cible"
                  : r.deltaMensuel > 600
                    ? `Surcoût mensuel élevé (+${eur(r.deltaMensuel, 0)}/mois) — voir Comparaison`
                    : `Faisable — voir l'onglet Comparaison`
              }
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Tab 2 — Rénover
// ═══════════════════════════════════════════════════════════
type ModeFinancement = "epargne" | "credit" | "mix";

function TabRenover() {
  const [budgetTravaux, setBudgetTravaux] = useState(125_000);
  const [modeFinancement, setModeFinancement] =
    useState<ModeFinancement>("mix");
  const [montantCredit, setMontantCredit] = useState(75_000);
  const [tauxCredit, setTauxCredit] = useState(3.8);
  const [dureeCredit, setDureeCredit] = useState(10);
  const [revenus, setRevenus] = useState(0);

  const r = useMemo(() => {
    const montantEmprunte =
      modeFinancement === "epargne"
        ? 0
        : modeFinancement === "credit"
          ? budgetTravaux
          : Math.min(montantCredit, budgetTravaux);
    const epargneMobilisee = budgetTravaux - montantEmprunte;
    const mensualiteCredit = pmt(montantEmprunte, tauxCredit / 100, dureeCredit);
    const mensualiteTotal = SITUATION.mensualiteActuelle + mensualiteCredit;
    const tauxEndettement = revenus > 0 ? mensualiteTotal / revenus : null;
    const totalInteretsCredit =
      mensualiteCredit * dureeCredit * 12 - montantEmprunte;
    const valeurPostTravaux = SITUATION.valeurEstimee + budgetTravaux * 0.7;
    const equityPost = valeurPostTravaux - SITUATION.creditRestant;
    const roi = (valeurPostTravaux - SITUATION.valeurEstimee) / budgetTravaux;
    return {
      montantEmprunte,
      epargneMobilisee,
      mensualiteCredit,
      mensualiteTotal,
      deltaMensuel: mensualiteCredit,
      tauxEndettement,
      totalInteretsCredit,
      valeurPostTravaux,
      equityPost,
      roi,
    };
  }, [budgetTravaux, modeFinancement, montantCredit, tauxCredit, dureeCredit, revenus]);

  const endettementOk = r.tauxEndettement === null || r.tauxEndettement <= 0.35;

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* ── Colonne inputs ── */}
      <div className="space-y-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Budget travaux estimé</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="mb-2 flex justify-between text-sm">
                <span className="text-muted-foreground">Budget total</span>
                <span className="font-semibold">{eur(budgetTravaux)}</span>
              </div>
              <Slider
                value={[budgetTravaux]}
                onValueChange={([v]) => setBudgetTravaux(v)}
                min={80_000}
                max={200_000}
                step={5_000}
              />
              <div className="mt-1 flex justify-between text-xs text-muted-foreground">
                <span>80 k</span>
                <span>200 k</span>
              </div>
            </div>
            <p className="text-xs text-muted-foreground">
              Fourchette estimée : 100 k – 150 k (4 chambres + terrassement +
              piscine)
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Mode de financement</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-2">
              {(
                [
                  ["epargne", "Épargne seule"],
                  ["credit", "Crédit total"],
                  ["mix", "Mix"],
                ] as const
              ).map(([mode, label]) => (
                <button
                  key={mode}
                  onClick={() => setModeFinancement(mode)}
                  className={cn(
                    "rounded-lg border px-3 py-2 text-sm font-medium transition-colors",
                    modeFinancement === mode
                      ? "border-primary bg-primary text-primary-foreground"
                      : "border-border hover:bg-accent"
                  )}
                >
                  {label}
                </button>
              ))}
            </div>

            {modeFinancement !== "epargne" && (
              <div className="space-y-3">
                {modeFinancement === "mix" && (
                  <div>
                    <Label className="text-xs text-muted-foreground">
                      Montant à emprunter (€)
                    </Label>
                    <Input
                      type="number"
                      value={montantCredit}
                      onChange={(e) =>
                        setMontantCredit(Number(e.target.value))
                      }
                      step={5_000}
                      className="mt-1"
                    />
                    <p className="mt-1 text-xs text-muted-foreground">
                      Épargne mobilisée :{" "}
                      {eur(Math.max(0, budgetTravaux - montantCredit))}
                    </p>
                  </div>
                )}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label className="text-xs text-muted-foreground">
                      Taux crédit travaux (%)
                    </Label>
                    <Input
                      type="number"
                      value={tauxCredit}
                      onChange={(e) => setTauxCredit(Number(e.target.value))}
                      step={0.05}
                      min={1}
                      max={8}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">
                      Durée (ans)
                    </Label>
                    <Input
                      type="number"
                      value={dureeCredit}
                      onChange={(e) =>
                        setDureeCredit(Number(e.target.value))
                      }
                      min={3}
                      max={25}
                      className="mt-1"
                    />
                  </div>
                </div>
              </div>
            )}

            <div>
              <Label className="text-xs text-muted-foreground">
                Revenus nets foyer / mois (€)
              </Label>
              <Input
                type="number"
                value={revenus || ""}
                onChange={(e) => setRevenus(Number(e.target.value))}
                placeholder="ex : 5 000"
                className="mt-1"
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ── Colonne résultats ── */}
      <div className="space-y-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Mensualités</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-2">
            <Carte
              libelle="Mensualité immo actuelle"
              valeur={eur(SITUATION.mensualiteActuelle, 2)}
            />
            <Carte
              libelle="+ Crédit travaux / mois"
              valeur={
                r.mensualiteCredit > 0 ? `+ ${eur(r.mensualiteCredit, 2)}` : "0 €"
              }
              couleur={r.mensualiteCredit > 0 ? "orange" : "neutre"}
            />
            <Carte
              libelle="Mensualité totale"
              valeur={eur(r.mensualiteTotal, 2)}
              sousTitre={`+ ${eur(r.deltaMensuel, 0)} / mois vs aujourd'hui`}
              couleur={
                r.deltaMensuel > 400
                  ? "rouge"
                  : r.deltaMensuel > 0
                    ? "orange"
                    : "vert"
              }
            />
            <Carte
              libelle="Épargne mobilisée"
              valeur={eur(r.epargneMobilisee)}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">
              Valeur & patrimoine post-travaux
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid gap-3 sm:grid-cols-2">
              <Carte
                libelle="Valeur estimée post-travaux"
                valeur={eur(r.valeurPostTravaux)}
                sousTitre="70 % des travaux valorisés"
                couleur="vert"
              />
              <Carte
                libelle="Equity nette"
                valeur={eur(r.equityPost)}
                couleur="vert"
              />
            </div>
            <div className="space-y-1 rounded-lg bg-muted/40 p-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">ROI travaux</span>
                <span className="font-semibold">
                  {pct(r.roi)} de la valeur récupérée
                </span>
              </div>
              {r.totalInteretsCredit > 0 && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">
                    Total intérêts crédit travaux
                  </span>
                  <span className="font-medium">
                    {eur(r.totalInteretsCredit)}
                  </span>
                </div>
              )}
            </div>

            {r.tauxEndettement !== null && (
              <Verdict
                ok={endettementOk}
                texte={`Taux endettement total : ${pct(r.tauxEndettement)} ${endettementOk ? "(≤ 35 % ✓)" : "(> 35 % — réduire montant emprunté)"}`}
              />
            )}

            <Verdict
              ok={endettementOk && r.deltaMensuel < 500}
              texte={
                !endettementOk
                  ? "Endettement trop élevé — réduire le montant à emprunter"
                  : r.deltaMensuel === 0
                    ? "Financement sur épargne — aucun impact mensuel"
                    : `Faisable — ${eur(r.mensualiteTotal, 0)} / mois au total`
              }
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Tab 3 — Comparaison
// ═══════════════════════════════════════════════════════════
function TabComparaison() {
  const [prixDemenager, setPrixDemenager] = useState(450_000);
  const [tauxDemenager, setTauxDemenager] = useState(3.5);
  const [dureeDemenager, setDureeDemenager] = useState(25);
  const [budgetRenover, setBudgetRenover] = useState(125_000);
  const [montantCreditRenover, setMontantCreditRenover] = useState(75_000);
  const [tauxRenover, setTauxRenover] = useState(3.8);
  const [dureeRenover, setDureeRenover] = useState(10);
  const [revenus, setRevenus] = useState(0);

  const { ren, dem } = useMemo(() => {
    // ── Déménager
    const fraisNotaire = prixDemenager * 0.075;
    const nouveauPret = Math.max(0, prixDemenager + fraisNotaire - APPORT_DISPONIBLE);
    const mensualiteDem =
      pmt(nouveauPret, tauxDemenager / 100, dureeDemenager) +
      (nouveauPret * SITUATION.tauxAssurance) / 12;
    const totalInteretsDem = mensualiteDem * dureeDemenager * 12 - nouveauPret;

    // ── Rénover
    const mensualiteCreditRen = pmt(montantCreditRenover, tauxRenover / 100, dureeRenover);
    const mensualiteRen = SITUATION.mensualiteActuelle + mensualiteCreditRen;
    const totalInteretsRen =
      SITUATION.interetsMensuels * SITUATION.echeancesRestantes +
      (mensualiteCreditRen * dureeRenover * 12 - montantCreditRenover);
    const valeurPostTravaux = SITUATION.valeurEstimee + budgetRenover * 0.7;

    // Break-even : nb mois pour que les frais de notaire soient compensés par économies mensuelles
    const deltaRen = mensualiteDem - mensualiteRen; // >0 = déménager coûte plus cher / mois
    const breakEvenMois = deltaRen > 0 ? Math.ceil(fraisNotaire / deltaRen) : null;

    return {
      ren: {
        mensualite: mensualiteRen,
        deltaMensuel: mensualiteCreditRen,
        tauxEndettement: revenus > 0 ? mensualiteRen / revenus : null,
        coutCumule20ans: mensualiteRen * 240,
        totalInterets: totalInteretsRen,
        valeur: valeurPostTravaux,
        equity: valeurPostTravaux - SITUATION.creditRestant,
      },
      dem: {
        mensualite: mensualiteDem,
        deltaMensuel: mensualiteDem - SITUATION.mensualiteActuelle,
        tauxEndettement: revenus > 0 ? mensualiteDem / revenus : null,
        coutCumule20ans: mensualiteDem * 240,
        totalInterets: totalInteretsDem,
        valeur: prixDemenager * 1.1,
        equity: prixDemenager * 1.1 - nouveauPret,
        fraisNotaire,
        breakEvenMois,
      },
    };
  }, [prixDemenager, tauxDemenager, dureeDemenager, budgetRenover, montantCreditRenover, tauxRenover, dureeRenover, revenus]);

  const renoverGagne = ren.mensualite < dem.mensualite;

  const lignes = [
    {
      label: "Mensualité totale",
      r: eur(ren.mensualite, 2),
      d: eur(dem.mensualite, 2),
      ok: ren.mensualite <= dem.mensualite,
    },
    {
      label: "Delta vs aujourd'hui / mois",
      r: `+ ${eur(ren.deltaMensuel, 0)}`,
      d: `+ ${eur(dem.deltaMensuel, 0)}`,
      ok: ren.deltaMensuel <= dem.deltaMensuel,
    },
    {
      label: "Taux d'endettement",
      r: ren.tauxEndettement ? pct(ren.tauxEndettement) : "—",
      d: dem.tauxEndettement ? pct(dem.tauxEndettement) : "—",
      ok: (ren.tauxEndettement ?? 0) <= (dem.tauxEndettement ?? 0),
    },
    {
      label: "Coût cumulé sur 20 ans",
      r: eur(ren.coutCumule20ans),
      d: eur(dem.coutCumule20ans),
      ok: ren.coutCumule20ans <= dem.coutCumule20ans,
    },
    {
      label: "Total intérêts sur durée",
      r: eur(ren.totalInterets),
      d: eur(dem.totalInterets),
      ok: ren.totalInterets <= dem.totalInterets,
    },
    {
      label: "Valeur patrimoine estimée",
      r: eur(ren.valeur),
      d: eur(dem.valeur),
      ok: ren.valeur >= dem.valeur,
    },
    {
      label: "Equity nette estimée",
      r: eur(ren.equity),
      d: eur(dem.equity),
      ok: ren.equity >= dem.equity,
    },
    {
      label: "Disruption",
      r: "Chantier 6–12 mois sur place",
      d: "Déménagement + nouveaux frais",
      ok: true,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Paramètres */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">
            Paramètres de la comparaison
          </CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <Label className="text-xs text-muted-foreground">
              Prix maison cible (€)
            </Label>
            <Input
              type="number"
              value={prixDemenager}
              onChange={(e) => setPrixDemenager(Number(e.target.value))}
              step={5_000}
              className="mt-1"
            />
          </div>
          <div>
            <Label className="text-xs text-muted-foreground">
              Taux nouveau crédit (%)
            </Label>
            <Input
              type="number"
              value={tauxDemenager}
              onChange={(e) => setTauxDemenager(Number(e.target.value))}
              step={0.05}
              className="mt-1"
            />
          </div>
          <div>
            <Label className="text-xs text-muted-foreground">
              Budget rénovation (€)
            </Label>
            <Input
              type="number"
              value={budgetRenover}
              onChange={(e) => setBudgetRenover(Number(e.target.value))}
              step={5_000}
              className="mt-1"
            />
          </div>
          <div>
            <Label className="text-xs text-muted-foreground">
              Revenus foyer / mois (€)
            </Label>
            <Input
              type="number"
              value={revenus || ""}
              onChange={(e) => setRevenus(Number(e.target.value))}
              placeholder="ex : 5 000"
              className="mt-1"
            />
          </div>
          <div>
            <Label className="text-xs text-muted-foreground">
              Montant crédit travaux (€)
            </Label>
            <Input
              type="number"
              value={montantCreditRenover}
              onChange={(e) =>
                setMontantCreditRenover(Number(e.target.value))
              }
              step={5_000}
              className="mt-1"
            />
          </div>
          <div>
            <Label className="text-xs text-muted-foreground">
              Taux crédit travaux (%)
            </Label>
            <Input
              type="number"
              value={tauxRenover}
              onChange={(e) => setTauxRenover(Number(e.target.value))}
              step={0.05}
              className="mt-1"
            />
          </div>
          <div>
            <Label className="text-xs text-muted-foreground">
              Durée crédit travaux (ans)
            </Label>
            <Input
              type="number"
              value={dureeRenover}
              onChange={(e) => setDureeRenover(Number(e.target.value))}
              min={3}
              max={25}
              className="mt-1"
            />
          </div>
          <div>
            <Label className="text-xs text-muted-foreground">
              Durée nouveau crédit (ans)
            </Label>
            <Input
              type="number"
              value={dureeDemenager}
              onChange={(e) => setDureeDemenager(Number(e.target.value))}
              min={10}
              max={30}
              className="mt-1"
            />
          </div>
        </CardContent>
      </Card>

      {/* Tableau comparatif */}
      <Card>
        <CardContent className="pt-4">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="py-3 pr-4 text-left font-medium text-muted-foreground w-1/3">
                    Critère
                  </th>
                  <th
                    className={cn(
                      "py-3 px-4 text-center font-semibold",
                      renoverGagne ? "text-green-600 dark:text-green-400" : ""
                    )}
                  >
                    🏠 Rénover{renoverGagne ? " ★" : ""}
                  </th>
                  <th
                    className={cn(
                      "py-3 pl-4 text-center font-semibold",
                      !renoverGagne ? "text-green-600 dark:text-green-400" : ""
                    )}
                  >
                    🚗 Déménager{!renoverGagne ? " ★" : ""}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {lignes.map((ligne) => (
                  <tr key={ligne.label} className="hover:bg-muted/30">
                    <td className="py-3 pr-4 font-medium text-muted-foreground">
                      {ligne.label}
                    </td>
                    <td
                      className={cn(
                        "py-3 px-4 text-center",
                        ligne.ok
                          ? "font-semibold text-green-700 dark:text-green-300"
                          : ""
                      )}
                    >
                      {ligne.r}
                    </td>
                    <td
                      className={cn(
                        "py-3 pl-4 text-center",
                        !ligne.ok
                          ? "font-semibold text-green-700 dark:text-green-300"
                          : ""
                      )}
                    >
                      {ligne.d}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Break-even */}
      {dem.breakEvenMois !== null && dem.breakEvenMois > 0 && (
        <Card className="border-amber-200 bg-amber-50/50 dark:border-amber-900 dark:bg-amber-950/20">
          <CardContent className="flex items-start gap-2 pt-4 text-sm">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600 dark:text-amber-400" />
            <span>
              <strong>Break-even :</strong> les frais de notaire (
              {eur(dem.fraisNotaire)}) seraient compensés par les économies
              mensuelles en{" "}
              <strong>
                {dem.breakEvenMois} mois (
                {(Math.round((dem.breakEvenMois / 12) * 10) / 10).toFixed(1)}{" "}
                ans)
              </strong>
              {dem.breakEvenMois > 60
                ? " — retour à long terme."
                : " — retour rapide."}
            </span>
          </CardContent>
        </Card>
      )}

      {/* Recommandation */}
      <Card
        className={cn(
          "border-2",
          renoverGagne ? "border-green-500" : "border-blue-500"
        )}
      >
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2">
            {renoverGagne
              ? "🏆 Recommandation financière : Rénover"
              : "🏆 Recommandation financière : Déménager"}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-1.5 text-sm text-muted-foreground">
          {renoverGagne ? (
            <>
              <p>
                • Mensualité inférieure — conserve votre taux exceptionnel de
                1,20 %
              </p>
              <p>• Moins d'intérêts payés sur la durée totale</p>
              <p>
                • Patrimoine valorisé par les travaux (70 % de la valeur
                récupérée)
              </p>
              <p>
                • ⚠️ Disruption : chantier 6–12 mois, financement partiel sur
                crédit travaux
              </p>
            </>
          ) : (
            <>
              <p>• Maison adaptée immédiatement à vos besoins</p>
              <p>
                • Patrimoine potentiellement plus élevé selon le marché local
              </p>
              <p>
                • ⚠️ Taux 3,5 % vs 1,20 % actuels = surcoût significatif
                d'intérêts
              </p>
              <p>• ⚠️ Mensualité plus élevée sur toute la durée du crédit</p>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// Page principale
// ═══════════════════════════════════════════════════════════
export default function SimulateurImmobilierPage() {
  const equiteNette = SITUATION.valeurEstimee - SITUATION.creditRestant;

  return (
    <div className="space-y-6">
      <EntetePageHabitat
        badge="Vision Maison — Décision"
        titre="Simulateur Rester vs Déménager"
        description="Comparer le coût réel de rénover votre maison actuelle versus acheter une nouvelle maison. Toutes les données de votre dossier sont pré-remplies."
        stats={[
          { label: "Valeur estimée", valeur: eur(SITUATION.valeurEstimee) },
          { label: "Crédit restant", valeur: eur(SITUATION.creditRestant) },
          { label: "Equity nette", valeur: eur(equiteNette) },
          {
            label: "Mensualité actuelle",
            valeur: eur(SITUATION.mensualiteActuelle, 2),
          },
        ]}
      />

      <Tabs defaultValue="demenager">
        <TabsList>
          <TabsTrigger value="demenager" className="flex items-center gap-1.5">
            <TrendingUp className="h-4 w-4" />
            Déménager
          </TabsTrigger>
          <TabsTrigger value="renover" className="flex items-center gap-1.5">
            <Hammer className="h-4 w-4" />
            Rénover
          </TabsTrigger>
          <TabsTrigger value="comparaison" className="flex items-center gap-1.5">
            <Calculator className="h-4 w-4" />
            Comparaison
          </TabsTrigger>
        </TabsList>

        <TabsContent value="demenager" className="mt-6">
          <TabDemenager />
        </TabsContent>
        <TabsContent value="renover" className="mt-6">
          <TabRenover />
        </TabsContent>
        <TabsContent value="comparaison" className="mt-6">
          <TabComparaison />
        </TabsContent>
      </Tabs>
    </div>
  );
}
