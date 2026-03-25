// ═══════════════════════════════════════════════════════════
// Page Paramètres (onglets)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Palette,
  Database,
  Bot,
  User,
  Save,
  Loader2,
  Sun,
  Moon,
  Monitor,
  Trash2,
  Bell,
  UtensilsCrossed,
} from "lucide-react";
import { useTheme } from "next-themes";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Badge } from "@/composants/ui/badge";
import { utiliserAuth } from "@/crochets/utiliser-auth";
import { utiliserRequete, utiliserMutation, utiliserInvalidation } from "@/crochets/utiliser-api";
import { clientApi } from "@/bibliotheque/api/client";
import {
  obtenirPreferences,
  sauvegarderPreferences,
} from "@/bibliotheque/api/preferences";
import {
  statutPush,
  souscrirePush,
  desabonnerPush,
} from "@/bibliotheque/api/push";
import type { Preferences } from "@/bibliotheque/api/preferences";
import { toast } from "sonner";

export default function PageParametres() {
  const { utilisateur } = utiliserAuth();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">⚙️ Paramètres</h1>
        <p className="text-muted-foreground">Configuration de l&apos;application</p>
      </div>

      <Tabs defaultValue="profil">
        <TabsList>
          <TabsTrigger value="profil" className="flex items-center gap-1">
            <User className="h-4 w-4" />
            Profil
          </TabsTrigger>
          <TabsTrigger value="cuisine" className="flex items-center gap-1">
            <UtensilsCrossed className="h-4 w-4" />
            Cuisine
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-1">
            <Bell className="h-4 w-4" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="affichage" className="flex items-center gap-1">
            <Palette className="h-4 w-4" />
            Affichage
          </TabsTrigger>
          <TabsTrigger value="ia" className="flex items-center gap-1">
            <Bot className="h-4 w-4" />
            IA
          </TabsTrigger>
          <TabsTrigger value="donnees" className="flex items-center gap-1">
            <Database className="h-4 w-4" />
            Données
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profil">
          <OngletProfil utilisateur={utilisateur} />
        </TabsContent>

        <TabsContent value="cuisine">
          <OngletCuisine />
        </TabsContent>

        <TabsContent value="notifications">
          <OngletNotifications />
        </TabsContent>

        <TabsContent value="affichage">
          <OngletAffichage />
        </TabsContent>

        <TabsContent value="ia">
          <OngletIA />
        </TabsContent>

        <TabsContent value="donnees">
          <OngletDonnees />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// ─── Profil ───────────────────────────────────────────────

function OngletProfil({
  utilisateur,
}: {
  utilisateur: { id: string; email: string; nom: string; role: string } | null;
}) {
  const [nom, setNom] = useState(utilisateur?.nom ?? "");
  const [email] = useState(utilisateur?.email ?? "");
  const invalider = utiliserInvalidation();

  const { mutate: sauvegarder, isPending } = utiliserMutation(
    (_: void) => clientApi.put("/auth/me", { nom }),
    {
      onSuccess: () => { invalider(["auth", "profil"]); toast.success("Profil sauvegardé"); },
      onError: () => toast.error("Erreur lors de la sauvegarde"),
    }
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Profil</CardTitle>
        <CardDescription>Gérez vos informations personnelles</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 max-w-md">
        <div className="space-y-2">
          <Label htmlFor="profil-nom">Nom</Label>
          <Input
            id="profil-nom"
            value={nom}
            onChange={(e) => setNom(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="profil-email">Email</Label>
          <Input id="profil-email" value={email} disabled />
          <p className="text-xs text-muted-foreground">
            L&apos;email ne peut pas être modifié
          </p>
        </div>
        <div className="space-y-2">
          <Label>Rôle</Label>
          <div>
            <Badge variant="secondary">{utilisateur?.role ?? "—"}</Badge>
          </div>
        </div>
        <Button
          onClick={() => sauvegarder(undefined)}
          disabled={isPending || nom === utilisateur?.nom}
        >
          {isPending ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Save className="mr-2 h-4 w-4" />
          )}
          Enregistrer
        </Button>
      </CardContent>
    </Card>
  );
}

// ─── Affichage ────────────────────────────────────────────

function OngletAffichage() {
  const { theme, setTheme } = useTheme();

  const themes = [
    { valeur: "light", label: "Clair", Icone: Sun },
    { valeur: "dark", label: "Sombre", Icone: Moon },
    { valeur: "system", label: "Système", Icone: Monitor },
  ] as const;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Affichage</CardTitle>
        <CardDescription>Thème et préférences visuelles</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label>Thème</Label>
          <div className="flex gap-2">
            {themes.map(({ valeur, label, Icone }) => (
              <Button
                key={valeur}
                variant={theme === valeur ? "default" : "outline"}
                className="flex-1"
                onClick={() => setTheme(valeur)}
              >
                <Icone className="mr-2 h-4 w-4" />
                {label}
              </Button>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ─── IA ───────────────────────────────────────────────────

function OngletIA() {
  const [modele, setModele] = useState("mistral-large-latest");
  const [limiteJournaliere, setLimiteJournaliere] = useState("100");

  return (
    <Card>
      <CardHeader>
        <CardTitle>Intelligence Artificielle</CardTitle>
        <CardDescription>Configuration de Mistral AI</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 max-w-md">
        <div className="space-y-2">
          <Label htmlFor="ia-modele">Modèle IA</Label>
          <Input
            id="ia-modele"
            value={modele}
            onChange={(e) => setModele(e.target.value)}
          />
          <p className="text-xs text-muted-foreground">
            Modèle Mistral utilisé pour les suggestions
          </p>
        </div>
        <div className="space-y-2">
          <Label htmlFor="ia-limite">Limite journalière d&apos;appels</Label>
          <Input
            id="ia-limite"
            type="number"
            min={1}
            value={limiteJournaliere}
            onChange={(e) => setLimiteJournaliere(e.target.value)}
          />
        </div>
        <Button disabled>
          <Save className="mr-2 h-4 w-4" />
          Enregistrer
        </Button>
        <p className="text-xs text-muted-foreground">
          Ces paramètres sont définis côté serveur dans .env.local
        </p>
      </CardContent>
    </Card>
  );
}

// ─── Données ──────────────────────────────────────────────

// ─── Cuisine (Préférences alimentaires) ───────────────────

function OngletCuisine() {
  const { data: prefs, isLoading } = utiliserRequete(
    ["preferences"],
    obtenirPreferences
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
    { onSuccess: () => { invalider(["preferences"]); toast.success("Préférences sauvegardées"); }, onError: () => toast.error("Erreur lors de la sauvegarde") }
  );

  if (isLoading) return <Card><CardContent className="py-8 text-center text-muted-foreground">Chargement…</CardContent></Card>;

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
            <Label>Jules présent</Label>
            <select
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
        <Button onClick={() => sauvegarder(undefined)} disabled={isPending}>
          {isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
          Enregistrer
        </Button>
      </CardContent>
    </Card>
  );
}

// ─── Notifications ────────────────────────────────────────

function OngletNotifications() {
  const { data: status, isLoading } = utiliserRequete(
    ["push", "status"],
    statutPush
  );
  const invalider = utiliserInvalidation();

  const { mutate: activer, isPending: enActivation } = utiliserMutation(
    async (_: void) => {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY,
      });
      const json = subscription.toJSON();
      return souscrirePush({
        endpoint: json.endpoint!,
        keys: {
          p256dh: json.keys!.p256dh!,
          auth: json.keys!.auth!,
        },
      });
    },
    { onSuccess: () => { invalider(["push", "status"]); toast.success("Notifications activées"); }, onError: () => toast.error("Erreur lors de l'activation") }
  );

  const { mutate: desactiver, isPending: enDesactivation } = utiliserMutation(
    async (_: void) => {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      if (subscription) {
        await desabonnerPush(subscription.endpoint);
        await subscription.unsubscribe();
      }
    },
    { onSuccess: () => { invalider(["push", "status"]); toast.success("Notifications désactivées"); }, onError: () => toast.error("Erreur lors de la désactivation") }
  );

  const pushSupporte = typeof window !== "undefined" && "PushManager" in window;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Notifications Push</CardTitle>
        <CardDescription>
          Recevez des alertes pour les courses, entretien, péremptions, etc.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 max-w-md">
        {!pushSupporte ? (
          <p className="text-sm text-muted-foreground">
            Les notifications push ne sont pas supportées par votre navigateur.
          </p>
        ) : isLoading ? (
          <p className="text-sm text-muted-foreground">Chargement…</p>
        ) : (
          <>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-sm">Notifications</p>
                <p className="text-xs text-muted-foreground">
                  {status?.has_subscriptions
                    ? `${status.subscription_count} appareil(s) enregistré(s)`
                    : "Aucun appareil enregistré"}
                </p>
              </div>
              <Badge variant={status?.has_subscriptions ? "default" : "secondary"}>
                {status?.has_subscriptions ? "Activées" : "Désactivées"}
              </Badge>
            </div>

            {status?.has_subscriptions ? (
              <Button
                variant="outline"
                onClick={() => desactiver(undefined)}
                disabled={enDesactivation}
              >
                {enDesactivation ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Bell className="mr-2 h-4 w-4" />}
                Désactiver les notifications
              </Button>
            ) : (
              <Button
                onClick={() => activer(undefined)}
                disabled={enActivation}
              >
                {enActivation ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Bell className="mr-2 h-4 w-4" />}
                Activer les notifications
              </Button>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}

// ─── Données ──────────────────────────────────────────────

function OngletDonnees() {
  const [confirmation, setConfirmation] = useState(false);
  const invalider = utiliserInvalidation();

  const viderCache = () => {
    // Invalide tous les caches TanStack Query
    invalider([]);
    setConfirmation(true);
    setTimeout(() => setConfirmation(false), 2000);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Données</CardTitle>
        <CardDescription>Gestion du cache et des données</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label>Cache local</Label>
          <p className="text-sm text-muted-foreground">
            Videz le cache pour recharger toutes les données depuis le serveur.
          </p>
          <Button variant="outline" onClick={viderCache}>
            {confirmation ? (
              <>Cache vidé !</>
            ) : (
              <>
                <Trash2 className="mr-2 h-4 w-4" />
                Vider le cache
              </>
            )}
          </Button>
        </div>

        <div className="space-y-2">
          <Label>Stockage navigateur</Label>
          <p className="text-sm text-muted-foreground">
            Taille estimée des données stockées localement.
          </p>
          <Badge variant="secondary">
            {typeof window !== "undefined"
              ? `${(JSON.stringify(localStorage).length / 1024).toFixed(1)} KB`
              : "—"}
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}
