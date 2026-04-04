// ═══════════════════════════════════════════════════════════
// Page configuration famille
// Tabs: Anniversaires | Routines | Contacts | Documents | Calendriers | Garde | Préférences
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useEffect } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Settings,
  Cake,
  RotateCw,
  BookUser,
  FileText,
  Calendar,
  Baby,
  Plus,
  Trash2,
  Save,
  CheckCircle2,
  SlidersHorizontal,
  X,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Badge } from "@/composants/ui/badge";
import { lireConfigGarde, sauvegarderConfigGarde, lirePreferencesFamille, sauvegarderPreferencesFamille } from "@/bibliotheque/api/famille";
import { toast } from "sonner";
import Link from "next/link";

// ─────────────────────────────────────────────
// Types locaux
// ─────────────────────────────────────────────

interface SemaineFermeture {
  debut: string;
  fin: string;
  label: string;
}

const ONGLETS_CONFIG = [
  { id: "garde", label: "Garde & Crèche", Icone: Baby },
  { id: "preferences", label: "Préférences", Icone: SlidersHorizontal },
  { id: "anniversaires", label: "Anniversaires", Icone: Cake, href: "/famille/anniversaires" },
  { id: "routines", label: "Routines", Icone: RotateCw, href: "/famille/routines" },
  { id: "contacts", label: "Contacts", Icone: BookUser, href: "/famille/contacts" },
  { id: "documents", label: "Documents", Icone: FileText, href: "/famille/documents" },
  { id: "calendriers", label: "Calendriers", Icone: Calendar, href: "/famille/calendriers" },
] as const;

// ─────────────────────────────────────────────
// Composant principal
// ─────────────────────────────────────────────

export default function PageConfigFamille() {
  const [ongletActif, setOngletActif] = useState<string>("garde");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Settings className="h-6 w-6" />
          Configuration Famille
        </h1>
        <p className="text-muted-foreground">
          Paramètres de garde, routines et préférences familiales
        </p>
      </div>

      {/* Onglets */}
      <div className="flex gap-2 flex-wrap">
        {ONGLETS_CONFIG.map((o) => (
          'href' in o ? (
            <Link key={o.id} href={o.href}>
              <Button variant="outline" size="sm" className="gap-1.5">
                <o.Icone className="h-4 w-4" />
                {o.label}
              </Button>
            </Link>
          ) : (
            <Button
              key={o.id}
              variant={ongletActif === o.id ? "default" : "outline"}
              size="sm"
              className="gap-1.5"
              onClick={() => setOngletActif(o.id)}
            >
              <o.Icone className="h-4 w-4" />
              {o.label}
            </Button>
          )
        ))}
      </div>

      {/* Contenu du tab actif */}
      {ongletActif === "garde" && <TabGarde />}
      {ongletActif === "preferences" && <TabPreferences />}
    </div>
  );
}

// ─────────────────────────────────────────────
// Tab Garde / Crèche
// ─────────────────────────────────────────────

function TabGarde() {
  const [nomCreche, setNomCreche] = useState("");
  const [zone, setZone] = useState("B");
  const [semaines, setSemaines] = useState<SemaineFermeture[]>([]);
  const [sauvegarde, setSauvegarde] = useState(false);

  const { data: config, isLoading } = useQuery({
    queryKey: ["famille", "config", "garde"],
    queryFn: lireConfigGarde,
    staleTime: 5 * 60 * 1000,
  });

  useEffect(() => {
    if (config) {
      setNomCreche(config.nom_creche ?? "");
      setZone(config.zone_academique ?? "B");
      setSemaines(
        (config.semaines_fermeture ?? []).map((s) => ({
          debut: s.debut ?? "",
          fin: s.fin ?? "",
          label: s.label ?? "",
        }))
      );
    }
  }, [config]);

  const mutation = useMutation({
    mutationFn: () =>
      sauvegarderConfigGarde({
        semaines_fermeture: semaines,
        nom_creche: nomCreche,
        zone_academique: zone,
      }),
    onSuccess: () => {
      toast.success("Configuration crèche sauvegardée ✅");
      setSauvegarde(true);
      setTimeout(() => setSauvegarde(false), 3000);
    },
    onError: () => toast.error("Erreur lors de la sauvegarde"),
  });

  const ajouterSemaine = () => {
    setSemaines([...semaines, { debut: "", fin: "", label: "" }]);
  };

  const supprimerSemaine = (idx: number) => {
    setSemaines(semaines.filter((_, i) => i !== idx));
  };

  const modifierSemaine = (idx: number, champ: keyof SemaineFermeture, valeur: string) => {
    setSemaines(semaines.map((s, i) => (i === idx ? { ...s, [champ]: valeur } : s)));
  };

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Chargement de la configuration...</p>;
  }

  return (
    <div className="space-y-6">
      {/* Infos crèche */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Baby className="h-4 w-4" />
            Informations crèche
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="nom_creche">Nom de la crèche</Label>
              <Input
                id="nom_creche"
                value={nomCreche}
                onChange={(e) => setNomCreche(e.target.value)}
                placeholder="Ex: Crèche Les Petits Loups"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="zone_acad">Zone académique</Label>
              <select
                id="zone_acad"
                title="Zone académique"
                value={zone}
                onChange={(e) => setZone(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="A">Zone A</option>
                <option value="B">Zone B</option>
                <option value="C">Zone C</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Semaines de fermeture */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base">Semaines de fermeture</CardTitle>
              <CardDescription className="text-xs mt-0.5">
                Ajoutez les fermetures annuelles de la crèche
              </CardDescription>
            </div>
            <Button size="sm" variant="outline" onClick={ajouterSemaine}>
              <Plus className="h-4 w-4 mr-1" />
              Ajouter
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {semaines.length === 0 && (
            <p className="text-sm text-muted-foreground text-center py-4">
              Aucune fermeture configurée. Cliquez "Ajouter" pour en saisir une.
            </p>
          )}
          {semaines.map((s, idx) => (
            <div key={idx} className="grid grid-cols-[1fr_1fr_2fr_auto] gap-2 items-end">
              <div className="space-y-1">
                <Label className="text-xs">Début</Label>
                <Input
                  type="date"
                  value={s.debut}
                  onChange={(e) => modifierSemaine(idx, "debut", e.target.value)}
                  className="text-xs h-9"
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Fin</Label>
                <Input
                  type="date"
                  value={s.fin}
                  onChange={(e) => modifierSemaine(idx, "fin", e.target.value)}
                  className="text-xs h-9"
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Libellé</Label>
                <Input
                  value={s.label}
                  onChange={(e) => modifierSemaine(idx, "label", e.target.value)}
                  placeholder="Ex: Vacances été"
                  className="text-xs h-9"
                />
              </div>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => supprimerSemaine(idx)}
                className="h-9 px-2"
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Aperçu des prochains jours sans crèche */}
      {config?.semaines_fermeture && config.semaines_fermeture.length > 0 && (
        <Card className="bg-blue-50/30 dark:bg-blue-950/10 border-blue-200/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Calendar className="h-4 w-4 text-blue-500" />
              Prochaines fermetures configurées
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {config.semaines_fermeture.slice(0, 5).map((s, i) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <Badge variant="outline" className="text-xs">
                    {s.label || "Fermeture"}
                  </Badge>
                  <span className="text-muted-foreground text-xs">
                    {s.debut} → {s.fin}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Bouton sauvegarder */}
      <div className="flex justify-end gap-2">
        <Button
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending}
          className="gap-2"
        >
          {sauvegarde ? (
            <>
              <CheckCircle2 className="h-4 w-4 text-green-400" />
              Sauvegardé !
            </>
          ) : (
            <>
              <Save className="h-4 w-4" />
              Sauvegarder
            </>
          )}
        </Button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// Tab Préférences familiales
// ─────────────────────────────────────────────

function TagInput({
  values,
  onChange,
  placeholder,
}: {
  values: string[];
  onChange: (v: string[]) => void;
  placeholder?: string;
}) {
  const [input, setInput] = useState("");

  const ajouter = () => {
    const val = input.trim();
    if (val && !values.includes(val)) {
      onChange([...values, val]);
    }
    setInput("");
  };

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") { e.preventDefault(); ajouter(); }
          }}
          placeholder={placeholder}
          className="h-8 text-sm"
        />
        <Button size="sm" variant="outline" onClick={ajouter} className="h-8 px-2">
          <Plus className="h-3.5 w-3.5" />
        </Button>
      </div>
      <div className="flex flex-wrap gap-1">
        {values.map((v) => (
          <span
            key={v}
            className="inline-flex items-center gap-1 bg-secondary text-secondary-foreground rounded-full px-2 py-0.5 text-xs"
          >
            {v}
            <button
              type="button"
              onClick={() => onChange(values.filter((x) => x !== v))}
              className="hover:text-destructive"
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
      </div>
    </div>
  );
}

function TabPreferences() {
  const [anne, setAnne] = useState<Record<string, string>>({});
  const [mathieu, setMathieu] = useState<Record<string, string>>({});
  const [styleAnne, setStyleAnne] = useState<Record<string, unknown>>({});
  const [styleMathieu, setStyleMathieu] = useState<Record<string, unknown>>({});
  const [gaming, setGaming] = useState<string[]>([]);
  const [culture, setCulture] = useState<string[]>([]);
  const [sauvegarde, setSauvegarde] = useState(false);

  const { data: prefs, isLoading } = useQuery({
    queryKey: ["famille", "config", "preferences"],
    queryFn: lirePreferencesFamille,
    staleTime: 5 * 60 * 1000,
  });

  useEffect(() => {
    if (prefs) {
      setAnne(prefs.taille_vetements_anne ?? {});
      setMathieu(prefs.taille_vetements_mathieu ?? {});
      setStyleAnne(prefs.style_achats_anne ?? {});
      setStyleMathieu(prefs.style_achats_mathieu ?? {});
      setGaming(prefs.interets_gaming ?? []);
      setCulture(prefs.interets_culture ?? []);
    }
  }, [prefs]);

  const mutation = useMutation({
    mutationFn: () =>
      sauvegarderPreferencesFamille({
        taille_vetements_anne: anne,
        taille_vetements_mathieu: mathieu,
        style_achats_anne: styleAnne,
        style_achats_mathieu: styleMathieu,
        interets_gaming: gaming,
        interets_culture: culture,
        equipement_activites: {},
      }),
    onSuccess: () => {
      toast.success("Préférences sauvegardées ✅");
      setSauvegarde(true);
      setTimeout(() => setSauvegarde(false), 3000);
    },
    onError: () => toast.error("Erreur lors de la sauvegarde"),
  });

  const taillesVetements = [
    { key: "tee_shirt", label: "T-shirt" },
    { key: "pantalon", label: "Pantalon" },
    { key: "pointure", label: "Pointure" },
  ];

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Chargement des préférences...</p>;
  }

  return (
    <div className="space-y-6">
      {/* Tailles Anne */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">👩 Tailles vêtements — Anne</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            {taillesVetements.map(({ key, label }) => (
              <div key={key} className="space-y-1">
                <Label className="text-xs">{label}</Label>
                <Input
                  value={(anne[key] as string) ?? ""}
                  onChange={(e) => setAnne({ ...anne, [key]: e.target.value })}
                  placeholder={key === "pointure" ? "Ex: 39" : "Ex: M / 38"}
                  className="h-8 text-sm"
                />
              </div>
            ))}
          </div>
          <div className="mt-4 flex flex-wrap gap-3">
            {["prefere_made_france", "prefere_qualite", "accepte_seconde_main"].map((flag) => (
              <label key={flag} className="flex items-center gap-2 text-sm cursor-pointer">
                <input
                  type="checkbox"
                  checked={Boolean(styleAnne[flag])}
                  onChange={(e) => setStyleAnne({ ...styleAnne, [flag]: e.target.checked })}
                  className="rounded"
                />
                {flag === "prefere_made_france" ? "Made in France" : flag === "prefere_qualite" ? "Qualité > Prix" : "Seconde main OK"}
              </label>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Tailles Mathieu */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">🧔 Tailles vêtements — Mathieu</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            {taillesVetements.map(({ key, label }) => (
              <div key={key} className="space-y-1">
                <Label className="text-xs">{label}</Label>
                <Input
                  value={(mathieu[key] as string) ?? ""}
                  onChange={(e) => setMathieu({ ...mathieu, [key]: e.target.value })}
                  placeholder={key === "pointure" ? "Ex: 44" : "Ex: L / 42"}
                  className="h-8 text-sm"
                />
              </div>
            ))}
          </div>
          <div className="mt-4 flex flex-wrap gap-3">
            {["prefere_made_france", "prefere_qualite", "accepte_seconde_main"].map((flag) => (
              <label key={flag} className="flex items-center gap-2 text-sm cursor-pointer">
                <input
                  type="checkbox"
                  checked={Boolean(styleMathieu[flag])}
                  onChange={(e) => setStyleMathieu({ ...styleMathieu, [flag]: e.target.checked })}
                  className="rounded"
                />
                {flag === "prefere_made_france" ? "Made in France" : flag === "prefere_qualite" ? "Qualité > Prix" : "Seconde main OK"}
              </label>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Intérêts gaming */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">🎮 Intérêts Gaming</CardTitle>
          <CardDescription className="text-xs">
            Consoles, jeux, accessoires suivis par l'IA pour les achats
          </CardDescription>
        </CardHeader>
        <CardContent>
          <TagInput
            values={gaming}
            onChange={setGaming}
            placeholder="Ex: Nintendo Switch, jeux de société..."
          />
        </CardContent>
      </Card>

      {/* Intérêts culture */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">🎭 Intérêts Culture</CardTitle>
          <CardDescription className="text-xs">
            Sorties et activités culturelles favorites
          </CardDescription>
        </CardHeader>
        <CardContent>
          <TagInput
            values={culture}
            onChange={setCulture}
            placeholder="Ex: cinéma, expositions, concerts..."
          />
        </CardContent>
      </Card>

      {/* Bouton sauvegarder */}
      <div className="flex justify-end gap-2">
        <Button onClick={() => mutation.mutate()} disabled={mutation.isPending} className="gap-2">
          {sauvegarde ? (
            <>
              <CheckCircle2 className="h-4 w-4 text-green-400" />
              Sauvegardé !
            </>
          ) : (
            <>
              <Save className="h-4 w-4" />
              Sauvegarder
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
