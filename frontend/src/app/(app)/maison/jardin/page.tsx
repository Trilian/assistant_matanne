// ═══════════════════════════════════════════════════════════
// Jardin — Plantes, calendrier des semis et éco-gestes
// ═══════════════════════════════════════════════════════════

"use client";

import { Suspense, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Sprout, Flower2, Calendar, Leaf, Sun, Sparkles, Loader2, Recycle, Plus, Pencil, Trash2, Euro } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Skeleton } from "@/composants/ui/skeleton";
import { Switch } from "@/composants/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { utiliserDialogCrud } from "@/crochets/utiliser-crud";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerElementsJardin,
  obtenirCalendrierSemis,
  obtenirSuggestionsIAJardin,
  listerEcoTips,
  creerEcoTip,
  modifierEcoTip,
  supprimerEcoTip,
} from "@/bibliotheque/api/maison";
import type { ActionEcologique } from "@/types/maison";
import { toast } from "sonner";
import { BoutonAchat } from "@/composants/bouton-achat";

const NOMS_MOIS = [
  "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
  "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
];

// ─── Onglet Éco-Gestes ────────────────────────────────────────
function OngletEco() {
  const queryClient = useQueryClient();
  const [actifOnly, setActifOnly] = useState(false);

  const formVide: Omit<ActionEcologique, "id"> = {
    titre: "",
    description: "",
    categorie: "",
    impact: "",
    economie_estimee: undefined,
    actif: true,
  };
  const [form, setForm] = useState(formVide);

  const { data: ecoTips, isLoading } = utiliserRequete(
    ["maison", "eco-tips", actifOnly],
    () => listerEcoTips(actifOnly)
  );

  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<ActionEcologique>({
      onOuvrirCreation: () => setForm(formVide),
      onOuvrirEdition: (item) =>
        setForm({
          titre: item.titre,
          description: item.description ?? "",
          categorie: item.categorie ?? "",
          impact: item.impact ?? "",
          economie_estimee: item.economie_estimee,
          actif: item.actif,
        }),
    });

  const { mutate: creer, isPending: creation } = utiliserMutation(
    () => creerEcoTip(form),
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["maison", "eco-tips"] });
        fermerDialog();
        toast.success("Action éco ajoutée");
      },
    }
  );

  const { mutate: modifier, isPending: modification } = utiliserMutation(
    () => modifierEcoTip(enEdition!.id, form),
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["maison", "eco-tips"] });
        fermerDialog();
        toast.success("Action éco modifiée");
      },
    }
  );

  const { mutate: supprimer } = utiliserMutation(
    (id: number) => supprimerEcoTip(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["maison", "eco-tips"] });
        toast.success("Action éco supprimée");
      },
    }
  );

  const { mutate: toggleActif } = utiliserMutation(
    ({ id, actif }: { id: number; actif: boolean }) => modifierEcoTip(id, { actif }),
    {
      onSuccess: () => queryClient.invalidateQueries({ queryKey: ["maison", "eco-tips"] }),
    }
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Switch
            checked={actifOnly}
            onCheckedChange={setActifOnly}
            id="actif-only"
          />
          <label htmlFor="actif-only">Actions actives seulement</label>
        </div>
        <Button size="sm" onClick={ouvrirCreation}>
          <Plus className="h-4 w-4 mr-1.5" />
          Ajouter
        </Button>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-20" />)}
        </div>
      ) : !ecoTips?.length ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            <Recycle className="h-8 w-8 mx-auto mb-2 opacity-50" />
            Aucune action éco enregistrée
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {ecoTips.map((tip) => (
            <Card key={tip.id} className={tip.actif ? "" : "opacity-60"}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <CardTitle className="text-sm">{tip.titre}</CardTitle>
                    {tip.categorie && (
                      <CardDescription className="text-xs mt-0.5">{tip.categorie}</CardDescription>
                    )}
                  </div>
                  <div className="flex items-center gap-1 shrink-0">
                    <Switch
                      checked={tip.actif}
                      onCheckedChange={(actif) => toggleActif({ id: tip.id, actif })}
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-2">
                {tip.description && (
                  <p className="text-xs text-muted-foreground">{tip.description}</p>
                )}
                <div className="flex items-center justify-between">
                  <div className="flex flex-wrap gap-2">
                    {tip.impact && (
                      <Badge variant="secondary" className="text-xs">
                        <Leaf className="h-3 w-3 mr-1" />
                        {tip.impact}
                      </Badge>
                    )}
                    {tip.economie_estimee != null && (
                      <Badge variant="outline" className="text-xs">
                        <Euro className="h-3 w-3 mr-1" />
                        {tip.economie_estimee} €/an
                      </Badge>
                    )}
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => ouvrirEdition(tip)}>
                      <Pencil className="h-3 w-3" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 text-destructive hover:text-destructive"
                      onClick={() => supprimer(tip.id)}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <DialogueFormulaire
        ouvert={dialogOuvert}
        onOuvertChange={setDialogOuvert}
        titre={enEdition ? "Modifier l'action éco" : "Nouvelle action éco"}
        description="Documentez vos gestes écologiques quotidiens"
        onSubmit={() => (enEdition ? modifier() : creer())}
        enChargement={enEdition ? modification : creation}
      >
        <div className="space-y-3">
          <div>
            <label className="text-sm font-medium">Titre *</label>
            <input
              className="w-full mt-1 rounded-md border px-3 py-2 text-sm"
              value={form.titre}
              onChange={(e) => setForm({ ...form, titre: e.target.value })}
              placeholder="Ex: Compostage des déchets alimentaires"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Description</label>
            <textarea
              className="w-full mt-1 rounded-md border px-3 py-2 text-sm"
              rows={2}
              value={form.description ?? ""}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Décrivez l'action et son bénéfice"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium">Catégorie</label>
              <input
                className="w-full mt-1 rounded-md border px-3 py-2 text-sm"
                value={form.categorie ?? ""}
                onChange={(e) => setForm({ ...form, categorie: e.target.value })}
                placeholder="Ex: Alimentation, Énergie"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Économie estimée (€/an)</label>
              <input
                type="number"
                className="w-full mt-1 rounded-md border px-3 py-2 text-sm"
                value={form.economie_estimee ?? ""}
                onChange={(e) => setForm({ ...form, economie_estimee: e.target.value ? Number(e.target.value) : undefined })}
                placeholder="Ex: 120"
              />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium">Impact</label>
            <input
              className="w-full mt-1 rounded-md border px-3 py-2 text-sm"
              value={form.impact ?? ""}
              onChange={(e) => setForm({ ...form, impact: e.target.value })}
              placeholder="Ex: -30kg CO₂/an"
            />
          </div>
        </div>
      </DialogueFormulaire>
    </div>
  );
}

// ─── Page principale (avec URL sync) ─────────────────────────
function ContenuJardin() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const ongletActif = searchParams.get("tab") ?? "plantes";

  const moisCourant = new Date().getMonth() + 1;
  const [moisSemis, setMoisSemis] = useState(String(moisCourant));

  const { data: elements, isLoading: chargementElements } = utiliserRequete(
    ["maison", "jardin", "elements"],
    () => listerElementsJardin()
  );

  const { data: calendrier, isLoading: chargementCalendrier } = utiliserRequete(
    ["maison", "jardin", "semis", moisSemis],
    () => obtenirCalendrierSemis(Number(moisSemis))
  );

  const [chargerIA, setChargerIA] = useState(false);
  const { data: suggestionsIA, isLoading: chargementIA } = utiliserRequete(
    ["maison", "jardin", "suggestions-ia"],
    obtenirSuggestionsIAJardin,
    { enabled: chargerIA }
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🌱 Jardin</h1>
        <p className="text-muted-foreground">
          Plantes, calendrier des semis et éco-gestes
        </p>
      </div>

      {/* Tâches du moment — IA saisonnière */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-emerald-500" />
            Tâches du moment
          </CardTitle>
          <CardDescription className="text-xs">
            Conseils jardin générés par IA pour la saison en cours
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!chargerIA ? (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setChargerIA(true)}
              className="text-emerald-600 border-emerald-300"
            >
              <Sparkles className="mr-2 h-4 w-4" />
              Obtenir les conseils IA
            </Button>
          ) : chargementIA ? (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Génération des conseils en cours…
            </div>
          ) : suggestionsIA?.taches.length ? (
            <ul className="space-y-2">
              {suggestionsIA.taches.map((t, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-500" />
                  {t.tache}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-muted-foreground">Aucune suggestion disponible</p>
          )}
        </CardContent>
      </Card>

      <Tabs
        value={ongletActif}
        onValueChange={(val) => router.replace(`?tab=${val}`)}
      >
        <TabsList>
          <TabsTrigger value="plantes">
            <Sprout className="mr-2 h-4 w-4" />
            Mes plantes
          </TabsTrigger>
          <TabsTrigger value="semis">
            <Calendar className="mr-2 h-4 w-4" />
            Calendrier semis
          </TabsTrigger>
          <TabsTrigger value="eco">
            <Recycle className="mr-2 h-4 w-4" />
            Éco-gestes
          </TabsTrigger>
        </TabsList>
        <TabsContent value="plantes" className="space-y-4 mt-4">
          {chargementElements ? (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-32 w-full" />
              ))}
            </div>
          ) : !elements?.length ? (
            <Card>
              <CardContent className="py-10 text-center text-muted-foreground">
                <Flower2 className="h-8 w-8 mx-auto mb-2 opacity-50" />
                Aucune plante enregistrée
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {elements.map((el) => (
                <Card key={el.id}>
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm">{el.nom}</CardTitle>
                      {el.statut && (
                        <Badge variant="secondary" className="text-xs">
                          {el.statut}
                        </Badge>
                      )}
                    </div>
                    {el.type && (
                      <CardDescription className="text-xs">
                        {el.type}
                      </CardDescription>
                    )}
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
                      {el.location && (
                        <span className="flex items-center gap-1">
                          <Sun className="h-3 w-3" />
                          {el.location}
                        </span>
                      )}
                      {el.date_plantation && (
                        <span>
                          Planté le{" "}
                          {new Date(el.date_plantation).toLocaleDateString("fr-FR")}
                        </span>
                      )}
                    </div>
                    {el.notes && (
                      <p className="mt-2 text-xs text-muted-foreground line-clamp-2">
                        {el.notes}
                      </p>
                    )}
                    <div className="mt-2">
                      <BoutonAchat article={{ nom: el.nom }} taille="xs" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* ─── Onglet Calendrier Semis ────────────────── */}
        <TabsContent value="semis" className="space-y-4 mt-4">
          <div className="flex items-center gap-3">
            <Select value={moisSemis} onValueChange={setMoisSemis}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {NOMS_MOIS.map((nom, i) => (
                  <SelectItem key={i + 1} value={String(i + 1)}>
                    {nom}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {chargementCalendrier ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-24" />
              ))}
            </div>
          ) : calendrier ? (
            <div className="grid gap-4 sm:grid-cols-3">
              {/* À semer */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Sprout className="h-4 w-4 text-green-600" />
                    À semer
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {calendrier.a_semer.length === 0 ? (
                    <p className="text-xs text-muted-foreground">
                      Rien à semer ce mois
                    </p>
                  ) : (
                    <ul className="space-y-1">
                      {calendrier.a_semer.map((p) => (
                        <li
                          key={p.nom}
                          className="text-sm flex items-center gap-2"
                        >
                          <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                          {p.nom}
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>

              {/* À planter */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Leaf className="h-4 w-4 text-emerald-600" />
                    À planter
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {calendrier.a_planter.length === 0 ? (
                    <p className="text-xs text-muted-foreground">
                      Rien à planter ce mois
                    </p>
                  ) : (
                    <ul className="space-y-1">
                      {calendrier.a_planter.map((p) => (
                        <li
                          key={p.nom}
                          className="text-sm flex items-center gap-2"
                        >
                          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                          {p.nom}
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>

              {/* À récolter */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Flower2 className="h-4 w-4 text-amber-600" />
                    À récolter
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {calendrier.a_recolter.length === 0 ? (
                    <p className="text-xs text-muted-foreground">
                      Rien à récolter ce mois
                    </p>
                  ) : (
                    <ul className="space-y-1">
                      {calendrier.a_recolter.map((p) => (
                        <li
                          key={p.nom}
                          className="text-sm flex items-center gap-2"
                        >
                          <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                          {p.nom}
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>
            </div>
          ) : null}
        </TabsContent>

        {/* ─── Onglet Éco-Gestes ────────────────── */}
        <TabsContent value="eco" className="space-y-4 mt-4">
          <OngletEco />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default function PageJardin() {
  return (
    <Suspense>
      <ContenuJardin />
    </Suspense>
  );
}
