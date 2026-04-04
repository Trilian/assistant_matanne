"use client";

import { useEffect, useState } from "react";
import { BrainCircuit, Loader2, Save, Sparkles } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Label } from "@/composants/ui/label";
import { Input } from "@/composants/ui/input";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { utiliserInvalidation, utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirPreferences, sauvegarderPreferences } from "@/bibliotheque/api/preferences";
import { obtenirApprentissageHabitudes, obtenirPreferencesApprises } from "@/bibliotheque/api/avance";
import { toast } from "sonner";

export function OngletCuisine() {
  const { data: prefs, isLoading } = utiliserRequete(
    ["preferences"],
    obtenirPreferences
  );
  const { data: habitudes } = utiliserRequete(
    ["preferences", "apprentissage-habitudes"],
    obtenirApprentissageHabitudes,
    { staleTime: 30 * 60 * 1000 }
  );
  const { data: preferencesApprises } = utiliserRequete(
    ["preferences", "apprises"],
    obtenirPreferencesApprises,
    { staleTime: 30 * 60 * 1000 }
  );
  const invalider = utiliserInvalidation();

  const [form, setForm] = useState({
    nb_adultes: 2,
    jules_present: true,
    temps_semaine: 30,
    temps_weekend: 60,
    poisson_par_semaine: 2,
    vegetarien_par_semaine: 1,
    viande_rouge_max: 2,
    aliments_exclus: "",
    aliments_favoris: "",
    robots: "",
    magasins_preferes: "",
  });

  useEffect(() => {
    if (prefs) {
      setForm({
        nb_adultes: prefs.nb_adultes,
        jules_present: prefs.jules_present,
        temps_semaine: prefs.temps_semaine,
        temps_weekend: prefs.temps_weekend,
        poisson_par_semaine: prefs.poisson_par_semaine,
        vegetarien_par_semaine: prefs.vegetarien_par_semaine,
        viande_rouge_max: prefs.viande_rouge_max,
        aliments_exclus: prefs.aliments_exclus.join(", "),
        aliments_favoris: prefs.aliments_favoris.join(", "),
        robots: prefs.robots.join(", "),
        magasins_preferes: prefs.magasins_preferes.join(", "),
      });
    }
  }, [prefs]);

  const { mutate: sauvegarder, isPending } = utiliserMutation(
    () =>
      sauvegarderPreferences({
        nb_adultes: form.nb_adultes,
        jules_present: form.jules_present,
        jules_age_mois: prefs?.jules_age_mois ?? null,
        temps_semaine: form.temps_semaine,
        temps_weekend: form.temps_weekend,
        poisson_par_semaine: form.poisson_par_semaine,
        vegetarien_par_semaine: form.vegetarien_par_semaine,
        viande_rouge_max: form.viande_rouge_max,
        aliments_exclus: form.aliments_exclus.split(",").map((s) => s.trim()).filter(Boolean),
        aliments_favoris: form.aliments_favoris.split(",").map((s) => s.trim()).filter(Boolean),
        robots: form.robots.split(",").map((s) => s.trim()).filter(Boolean),
        magasins_preferes: form.magasins_preferes.split(",").map((s) => s.trim()).filter(Boolean),
      }),
    {
      onSuccess: () => {
        invalider(["preferences"]);
        toast.success("Préférences sauvegardées");
      },
      onError: () => toast.error("Erreur lors de la sauvegarde"),
    }
  );

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-muted-foreground">Chargement…</CardContent>
      </Card>
    );
  }

  const habitudesDetectees = habitudes?.habitudes_detectees ?? [];
  const ajustementsSysteme = habitudes?.ajustements_systeme ?? [];
  const preferencesFavorites = preferencesApprises?.preferences_favorites ?? [];
  const preferencesAEviter = preferencesApprises?.preferences_a_eviter ?? [];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Préférences cuisine</CardTitle>
        <CardDescription>Configuration pour les suggestions de repas</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 max-w-lg">
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <Label>Adultes</Label>
            <Input type="number" min={1} max={10} value={form.nb_adultes} onChange={(e) => setForm({ ...form, nb_adultes: Number(e.target.value) })} />
          </div>
          <div className="space-y-1">
            <Label htmlFor="jules-present-select">Jules présent</Label>
            <select
              id="jules-present-select"
              aria-label="Jules présent"
              title="Jules présent"
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              value={form.jules_present ? "oui" : "non"}
              onChange={(e) => setForm({ ...form, jules_present: e.target.value === "oui" })}
            >
              <option value="oui">Oui</option>
              <option value="non">Non</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <Label>Temps semaine (min)</Label>
            <Input type="number" min={5} max={180} value={form.temps_semaine} onChange={(e) => setForm({ ...form, temps_semaine: Number(e.target.value) })} />
          </div>
          <div className="space-y-1">
            <Label>Temps weekend (min)</Label>
            <Input type="number" min={5} max={300} value={form.temps_weekend} onChange={(e) => setForm({ ...form, temps_weekend: Number(e.target.value) })} />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div className="space-y-1">
            <Label>Poisson/sem.</Label>
            <Input type="number" min={0} max={7} value={form.poisson_par_semaine} onChange={(e) => setForm({ ...form, poisson_par_semaine: Number(e.target.value) })} />
          </div>
          <div className="space-y-1">
            <Label>Végétarien/sem.</Label>
            <Input type="number" min={0} max={7} value={form.vegetarien_par_semaine} onChange={(e) => setForm({ ...form, vegetarien_par_semaine: Number(e.target.value) })} />
          </div>
          <div className="space-y-1">
            <Label>Viande rouge max</Label>
            <Input type="number" min={0} max={7} value={form.viande_rouge_max} onChange={(e) => setForm({ ...form, viande_rouge_max: Number(e.target.value) })} />
          </div>
        </div>
        <div className="space-y-1">
          <Label>Aliments exclus</Label>
          <Input placeholder="ex: coriandre, foie gras" value={form.aliments_exclus} onChange={(e) => setForm({ ...form, aliments_exclus: e.target.value })} />
          <p className="text-xs text-muted-foreground">Séparés par des virgules</p>
        </div>
        <div className="space-y-1">
          <Label>Aliments favoris</Label>
          <Input placeholder="ex: pâtes, poulet" value={form.aliments_favoris} onChange={(e) => setForm({ ...form, aliments_favoris: e.target.value })} />
        </div>
        <div className="space-y-1">
          <Label>Robots cuisine</Label>
          <Input placeholder="ex: Thermomix, Cookeo" value={form.robots} onChange={(e) => setForm({ ...form, robots: e.target.value })} />
        </div>
        <div className="space-y-1">
          <Label>Magasins préférés</Label>
          <Input placeholder="ex: Leclerc, Carrefour" value={form.magasins_preferes} onChange={(e) => setForm({ ...form, magasins_preferes: e.target.value })} />
        </div>

        <div className="rounded-xl border bg-muted/30 p-4 space-y-3">
          <div className="flex items-center justify-between gap-2">
            <div>
              <p className="text-sm font-semibold flex items-center gap-2">
                <BrainCircuit className="h-4 w-4 text-primary" />
                Préférences apprises par l&apos;IA
              </p>
              <p className="text-xs text-muted-foreground">
                Les habitudes repas stables sont maintenant analysées automatiquement sur plusieurs semaines.
              </p>
            </div>
            <Badge variant={preferencesApprises?.influence_active ? "default" : "secondary"}>
              {preferencesApprises?.influence_active ? "Actif" : "En observation"}
            </Badge>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded-lg border bg-background p-3 space-y-2">
              <p className="text-sm font-medium">Habitudes détectées</p>
              {habitudesDetectees.length > 0 ? (
                <ul className="space-y-1 text-xs text-muted-foreground">
                  {habitudesDetectees.slice(0, 3).map((habitude) => (
                    <li key={habitude}>• {habitude}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-muted-foreground">L&apos;IA continue d&apos;apprendre vos routines.</p>
              )}
              <p className="text-[11px] text-muted-foreground">
                Confiance : {Math.round((habitudes?.niveau_confiance ?? 0) * 100)}%
              </p>
            </div>

            <div className="rounded-lg border bg-background p-3 space-y-2">
              <p className="text-sm font-medium flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                Ajustements proposés
              </p>
              {(preferencesFavorites.length > 0 || preferencesAEviter.length > 0 || ajustementsSysteme.length > 0 || (preferencesApprises?.ajustements_suggestions?.length ?? 0) > 0) ? (
                <div className="space-y-2 text-xs text-muted-foreground">
                  {preferencesFavorites.length > 0 && (
                    <p>Favoris récurrents : {preferencesFavorites.slice(0, 2).map((item) => item.valeur).join(", ")}</p>
                  )}
                  {preferencesAEviter.length > 0 && (
                    <p>À limiter : {preferencesAEviter.slice(0, 2).map((item) => item.valeur).join(", ")}</p>
                  )}
                  {[...ajustementsSysteme, ...(preferencesApprises?.ajustements_suggestions ?? [])].slice(0, 2).map((ajustement) => (
                    <p key={ajustement}>• {ajustement}</p>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-muted-foreground">Les recommandations personnalisées apparaîtront après plus d&apos;historique.</p>
              )}
            </div>
          </div>
        </div>

        <Button onClick={() => sauvegarder(undefined)} disabled={isPending}>
          {isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
          Enregistrer
        </Button>
      </CardContent>
    </Card>
  );
}
