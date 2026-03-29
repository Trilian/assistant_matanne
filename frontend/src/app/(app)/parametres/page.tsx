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
  Mail,
  MessageCircle,
  Smartphone,
  UtensilsCrossed,
  GraduationCap,
  ShieldCheck,
  Download,
  Copy,
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
import { Switch } from "@/composants/ui/switch";
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
import { demanderPermissionNotificationsJeux } from "@/crochets/utiliser-notifications-jeux";
import type { Preferences } from "@/bibliotheque/api/preferences";
import { toast } from "sonner";
import { resetOnboarding, TourOnboarding } from "@/composants/disposition/tour-onboarding";

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
          <TabsTrigger value="securite" className="flex items-center gap-1">
            <ShieldCheck className="h-4 w-4" />
            Sécurité
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

        <TabsContent value="securite">
          <OngletSecurite />
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
  const [afficherTour, setAfficherTour] = useState(false);

  const themes = [
    { valeur: "light", label: "Clair", Icone: Sun },
    { valeur: "dark", label: "Sombre", Icone: Moon },
    { valeur: "system", label: "Système", Icone: Monitor },
  ] as const;

  const rejouerTour = () => {
    resetOnboarding();
    setAfficherTour(true);
  };

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Affichage</CardTitle>
          <CardDescription>Thème et préférences visuelles</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
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

          <div className="space-y-2 pt-2 border-t">
            <Label>Aide & Onboarding</Label>
            <div className="flex flex-col gap-2">
              <div className="rounded-lg border bg-muted/50 p-3">
                <div className="flex items-start gap-3">
                  <GraduationCap className="size-5 text-primary mt-0.5" />
                  <div className="flex-1 space-y-2">
                    <p className="text-sm font-medium">Tour de bienvenue</p>
                    <p className="text-xs text-muted-foreground">
                      Redécouvrez les fonctionnalités principales de l'application
                    </p>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={rejouerTour}
                      className="mt-1"
                    >
                      Rejouer le tour
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {afficherTour && (
        <TourOnboarding 
          forcer={true} 
          onTerminer={() => setAfficherTour(false)} 
        />
      )}
    </>
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

// ─── Canaux par catégorie (Sprint 13 — W4) ────────────────

const CANAUX_DISPONIBLES = [
  { id: "push", label: "Push navigateur", icon: Smartphone },
  { id: "ntfy", label: "Ntfy.sh", icon: Bell },
  { id: "email", label: "Email", icon: Mail },
  { id: "whatsapp", label: "WhatsApp", icon: MessageCircle },
] as const;

const CATEGORIES = [
  {
    id: "rappels" as const,
    label: "Rappels",
    description: "Rappels courses, entretien, médicaments…",
  },
  {
    id: "alertes" as const,
    label: "Alertes critiques",
    description: "Péremptions, garanties, dépassement budget…",
  },
  {
    id: "resumes" as const,
    label: "Résumés",
    description: "Résumé hebdomadaire, rapport mensuel…",
  },
];

function OngletCanauxNotifications() {
  const invalider = utiliserInvalidation();

  const { data: prefs, isLoading } = utiliserRequete(
    ["preferences", "notifications"],
    async () => {
      const { obtenirPreferencesNotifications } = await import("@/bibliotheque/api/preferences");
      return obtenirPreferencesNotifications();
    }
  );

  const { mutate: sauvegarder, isPending } = utiliserMutation(
    async (data: Parameters<typeof import("@/bibliotheque/api/preferences").sauvegarderPreferencesNotifications>[0]) => {
      const { sauvegarderPreferencesNotifications } = await import("@/bibliotheque/api/preferences");
      return sauvegarderPreferencesNotifications(data);
    },
    {
      onSuccess: () => {
        invalider(["preferences", "notifications"]);
        toast.success("Préférences de notification sauvegardées");
      },
      onError: () => toast.error("Erreur lors de la sauvegarde"),
    }
  );

  const [canaux, setCanaux] = useState<Record<string, string[]>>({
    rappels: ["push", "ntfy"],
    alertes: ["push", "ntfy", "email"],
    resumes: ["email"],
  });

  useEffect(() => {
    if (prefs?.canaux_par_categorie) {
      setCanaux({
        rappels: prefs.canaux_par_categorie.rappels ?? ["push", "ntfy"],
        alertes: prefs.canaux_par_categorie.alertes ?? ["push", "ntfy", "email"],
        resumes: prefs.canaux_par_categorie.resumes ?? ["email"],
      });
    }
  }, [prefs]);

  const toggleCanal = (categorie: string, canal: string) => {
    setCanaux((prev) => {
      const actuels = prev[categorie] ?? [];
      const nouveau = actuels.includes(canal)
        ? actuels.filter((c) => c !== canal)
        : [...actuels, canal];
      return { ...prev, [categorie]: nouveau };
    });
  };

  const handleSave = () => {
    sauvegarder({
      canaux_par_categorie: canaux as unknown as Parameters<typeof sauvegarder>[0]["canaux_par_categorie"],
    });
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">Chargement…</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Canaux par catégorie</CardTitle>
        <CardDescription>
          Choisissez les canaux de notification pour chaque type d&apos;alerte.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6 max-w-lg">
        {CATEGORIES.map((cat) => (
          <div key={cat.id} className="space-y-3">
            <div>
              <p className="font-medium text-sm">{cat.label}</p>
              <p className="text-xs text-muted-foreground">{cat.description}</p>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {CANAUX_DISPONIBLES.map(({ id, label, icon: Icon }) => {
                const actif = (canaux[cat.id] ?? []).includes(id);
                return (
                  <div
                    key={id}
                    className="flex items-center justify-between rounded-md border px-3 py-2"
                  >
                    <div className="flex items-center gap-2">
                      <Icon className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">{label}</span>
                    </div>
                    <Switch
                      checked={actif}
                      onCheckedChange={() => toggleCanal(cat.id, id)}
                      aria-label={`${label} pour ${cat.label}`}
                    />
                  </div>
                );
              })}
            </div>
          </div>
        ))}

        <Button onClick={handleSave} disabled={isPending} className="w-full">
          {isPending ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Save className="mr-2 h-4 w-4" />
          )}
          Sauvegarder les canaux
        </Button>
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
    <div className="space-y-6">
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

              {/* Notifications Jeux (Phase W) */}
              <div className="border-t pt-4 space-y-3">
                <div>
                  <p className="font-medium text-sm">🎮 Notifications Jeux</p>
                  <p className="text-xs text-muted-foreground">
                    Recevez des alertes pour les résultats de paris et tirages loto
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={async () => {
                    try {
                      const granted = await demanderPermissionNotificationsJeux();
                      if (granted) {
                        toast.success("Notifications jeux activées");
                      } else {
                        toast.error("Permission refusée");
                      }
                    } catch (error) {
                      toast.error("Erreur lors de l'activation");
                    }
                  }}
                >
                  <Bell className="mr-2 h-4 w-4" />
                  Activer les notifications jeux
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Canaux par catégorie — Sprint 13 W4 */}
      <OngletCanauxNotifications />
    </div>
  );
}

// ─── Données ──────────────────────────────────────────────

function OngletDonnees() {
  const [confirmation, setConfirmation] = useState(false);
  const [motDePasseBackup, setMotDePasseBackup] = useState("");
  const [fichierImport, setFichierImport] = useState<File | null>(null);
  const [motDePasseImport, setMotDePasseImport] = useState("");
  const [texteConfirmation, setTexteConfirmation] = useState("");
  const [motifSuppression, setMotifSuppression] = useState("");
  const [suppressionOuverte, setSuppressionOuverte] = useState(false);
  const invalider = utiliserInvalidation();

  const { data: resume, isLoading: chargementResume } = utiliserRequete(
    ["rgpd", "resume"],
    async () => {
      const { obtenirResumeDonnees } = await import("@/bibliotheque/api/rgpd");
      return obtenirResumeDonnees();
    }
  );

  const exportMutation = utiliserMutation(
    async () => {
      const { exporterDonnees } = await import("@/bibliotheque/api/rgpd");
      return exporterDonnees();
    },
    {
      onSuccess: (blob: Blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `mes-donnees-${new Date().toISOString().slice(0, 10)}.zip`;
        a.click();
        URL.revokeObjectURL(url);
        toast.success("Export téléchargé avec succès");
      },
      onError: () => toast.error("Erreur lors de l'export des données"),
    }
  );

  const suppressionMutation = utiliserMutation(
    async () => {
      const { supprimerCompte } = await import("@/bibliotheque/api/rgpd");
      return supprimerCompte(texteConfirmation, motifSuppression || undefined);
    },
    {
      onSuccess: () => {
        toast.success("Compte supprimé. Déconnexion...");
        setTimeout(() => {
          window.location.href = "/connexion";
        }, 2000);
      },
      onError: () => toast.error("Erreur lors de la suppression du compte"),
    }
  );

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

        {/* ─── RGPD — Export des données ─── */}
                {/* ─── Backup JSON chiffré ─── */}
                <div className="border-t pt-6 space-y-3">
                  <Label className="flex items-center gap-2">
                    <Download className="h-4 w-4" />
                    Backup données (JSON)
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    Exportez toutes vos données en JSON. Ajoutez un mot de passe pour chiffrer le fichier (AES-256).
                  </p>
                  <div className="flex items-center gap-2">
                    <Input
                      type="password"
                      placeholder="Mot de passe (optionnel)"
                      value={motDePasseBackup}
                      onChange={(e) => setMotDePasseBackup(e.target.value)}
                      className="max-w-xs"
                    />
                  </div>
                  <Button
                    variant="outline"
                    onClick={async () => {
                      const { telechargerBackupJson, DOMAINES_DEFAUT } = await import(
                        "@/bibliotheque/api/export"
                      );
                      try {
                        await telechargerBackupJson(
                          [...DOMAINES_DEFAUT],
                          motDePasseBackup || undefined
                        );
                        toast.success(
                          motDePasseBackup ? "Backup chiffré téléchargé" : "Backup téléchargé"
                        );
                      } catch {
                        toast.error("Erreur lors du téléchargement du backup");
                      }
                    }}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    {motDePasseBackup ? "Télécharger (.json.enc)" : "Télécharger (.json)"}
                  </Button>
                  <div className="space-y-2 pt-2">
                    <Label>Restaurer depuis un backup</Label>
                    <Input
                      type="file"
                      accept=".json,.json.enc"
                      onChange={(e) => setFichierImport(e.target.files?.[0] ?? null)}
                    />
                    {fichierImport?.name.endsWith(".enc") && (
                      <Input
                        type="password"
                        placeholder="Mot de passe du fichier chiffré"
                        value={motDePasseImport}
                        onChange={(e) => setMotDePasseImport(e.target.value)}
                      />
                    )}
                    {fichierImport && (
                      <Button
                        variant="outline"
                        onClick={async () => {
                          const { restaurerDepuisJson } = await import(
                            "@/bibliotheque/api/export"
                          );
                          try {
                            await restaurerDepuisJson(fichierImport, {
                              motDePasse: motDePasseImport || undefined,
                            });
                            toast.success("Données restaurées avec succès");
                            setFichierImport(null);
                            setMotDePasseImport("");
                          } catch {
                            toast.error("Erreur lors de la restauration");
                          }
                        }}
                      >
                        Restaurer
                      </Button>
                    )}
                  </div>
                </div>

                {/* ─── RGPD — Export des données ─── */}
        <div className="border-t pt-6 space-y-2">
          <Label className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            Export de vos données (RGPD)
          </Label>
          <p className="text-sm text-muted-foreground">
            Téléchargez une archive ZIP contenant toutes vos données personnelles.
          </p>
          {resume && !chargementResume && (
            <p className="text-xs text-muted-foreground">
              {resume.total_elements} éléments répartis sur{" "}
              {resume.categories.length} catégories
            </p>
          )}
          <Button
            variant="outline"
            onClick={() => exportMutation.mutate(undefined)}
            disabled={exportMutation.isPending}
          >
            {exportMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Export en cours...
              </>
            ) : (
              <>
                <Download className="mr-2 h-4 w-4" />
                Télécharger mes données
              </>
            )}
          </Button>
        </div>

        {/* ─── RGPD — Suppression du compte ─── */}
        <div className="border-t pt-6 space-y-4">
          <Label className="flex items-center gap-2 text-destructive">
            <Trash2 className="h-4 w-4" />
            Supprimer mon compte
          </Label>
          <p className="text-sm text-muted-foreground">
            Cette action est irréversible. Toutes vos données seront définitivement supprimées.
          </p>
          {!suppressionOuverte ? (
            <Button
              variant="destructive"
              onClick={() => setSuppressionOuverte(true)}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Supprimer mon compte
            </Button>
          ) : (
            <div className="space-y-3 rounded-lg border border-destructive/50 p-4">
              <div className="space-y-2">
                <Label>Motif (optionnel)</Label>
                <Input
                  value={motifSuppression}
                  onChange={(e) => setMotifSuppression(e.target.value)}
                  placeholder="Pourquoi souhaitez-vous supprimer votre compte ?"
                />
              </div>
              <div className="space-y-2">
                <Label>
                  Tapez <strong>SUPPRIMER MON COMPTE</strong> pour confirmer
                </Label>
                <Input
                  value={texteConfirmation}
                  onChange={(e) => setTexteConfirmation(e.target.value)}
                  placeholder="SUPPRIMER MON COMPTE"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  variant="destructive"
                  disabled={
                    texteConfirmation !== "SUPPRIMER MON COMPTE" ||
                    suppressionMutation.isPending
                  }
                  onClick={() => suppressionMutation.mutate(undefined)}
                >
                  {suppressionMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Suppression...
                    </>
                  ) : (
                    "Confirmer la suppression"
                  )}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setSuppressionOuverte(false);
                    setTexteConfirmation("");
                    setMotifSuppression("");
                  }}
                >
                  Annuler
                </Button>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Sécurité (2FA) ───────────────────────────────────────

function OngletSecurite() {
  const [etape, setEtape] = useState<"idle" | "setup" | "confirm" | "disable">("idle");
  const [qrCode, setQrCode] = useState("");
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [code, setCode] = useState("");
  const [erreur, setErreur] = useState("");

  const { data: statut, isLoading } = utiliserRequete(
    ["2fa", "status"],
    async () => {
      const { statut2FA } = await import("@/bibliotheque/api/auth");
      return statut2FA();
    }
  );
  const invalider = utiliserInvalidation();

  const initier2FA = async () => {
    setErreur("");
    try {
      const { activer2FA } = await import("@/bibliotheque/api/auth");
      const data = await activer2FA();
      setQrCode(data.qr_code);
      setBackupCodes(data.backup_codes);
      setEtape("setup");
    } catch {
      setErreur("Erreur lors de l'initialisation 2FA");
    }
  };

  const confirmer2FA = async () => {
    setErreur("");
    try {
      const { verifierSetup2FA } = await import("@/bibliotheque/api/auth");
      await verifierSetup2FA(code);
      setEtape("idle");
      setCode("");
      invalider(["2fa", "status"]);
      toast.success("2FA activé avec succès");
    } catch {
      setErreur("Code invalide. Vérifiez votre application.");
    }
  };

  const desactiver = async () => {
    setErreur("");
    try {
      const { desactiver2FA } = await import("@/bibliotheque/api/auth");
      await desactiver2FA(code);
      setEtape("idle");
      setCode("");
      invalider(["2fa", "status"]);
      toast.success("2FA désactivé");
    } catch {
      setErreur("Code invalide");
    }
  };

  const telechargerBackupCodes = () => {
    const contenu = [
      "Assistant Matanne — Codes de récupération 2FA",
      "Conservez ces codes en lieu sûr. Chaque code est à usage unique.",
      "",
      ...backupCodes.map((c, i) => `${i + 1}. ${c}`),
    ].join("\n");
    const blob = new Blob([contenu], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "matanne-2fa-backup-codes.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  if (isLoading) {
    return <Card><CardContent className="py-8 text-center text-muted-foreground">Chargement…</CardContent></Card>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5" />
          Authentification à deux facteurs (2FA)
        </CardTitle>
        <CardDescription>
          Sécurisez votre compte avec une application d&apos;authentification
          (Google Authenticator, Authy, etc.)
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6 max-w-lg">
        {erreur && (
          <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
            {erreur}
          </div>
        )}

        {/* État: 2FA activé */}
        {statut?.enabled && etape === "idle" && (
          <div className="space-y-4">
            <div className="flex items-center gap-3 rounded-lg border bg-green-50 dark:bg-green-950/20 p-4">
              <ShieldCheck className="h-5 w-5 text-green-600" />
              <div>
                <p className="font-medium text-green-800 dark:text-green-400">2FA activé</p>
                <p className="text-xs text-muted-foreground">
                  {statut.backup_codes_remaining} codes de récupération restants
                </p>
              </div>
            </div>
            <Button
              variant="destructive"
              size="sm"
              onClick={() => setEtape("disable")}
            >
              Désactiver le 2FA
            </Button>
          </div>
        )}

        {/* État: 2FA non activé */}
        {!statut?.enabled && etape === "idle" && (
          <div className="space-y-4">
            <div className="rounded-lg border bg-muted/50 p-4">
              <p className="text-sm">
                Le 2FA ajoute une couche de sécurité supplémentaire.
                Après l&apos;activation, un code à 6 chiffres sera demandé à chaque connexion.
              </p>
            </div>
            <Button onClick={initier2FA}>
              <ShieldCheck className="mr-2 h-4 w-4" />
              Activer le 2FA
            </Button>
          </div>
        )}

        {/* Étape: Setup — QR code + backup codes */}
        {etape === "setup" && (
          <div className="space-y-6">
            <div className="space-y-3">
              <Label>1. Scannez ce QR code</Label>
              <p className="text-xs text-muted-foreground">
                Ouvrez Google Authenticator ou Authy et scannez le QR code ci-dessous.
              </p>
              {qrCode && (
                <div className="flex justify-center rounded-lg border bg-white p-4">
                  <img src={qrCode} alt="QR code 2FA" className="h-48 w-48" />
                </div>
              )}
            </div>

            <div className="space-y-3">
              <Label>2. Sauvegardez vos codes de récupération</Label>
              <p className="text-xs text-muted-foreground">
                Ces codes sont utilisables une seule fois si vous perdez votre téléphone.
              </p>
              <div className="grid grid-cols-2 gap-1 rounded-lg border bg-muted/50 p-3 font-mono text-sm">
                {backupCodes.map((c) => (
                  <span key={c} className="px-2 py-1">{c}</span>
                ))}
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={telechargerBackupCodes}>
                  <Download className="mr-2 h-3.5 w-3.5" />
                  Télécharger
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    navigator.clipboard.writeText(backupCodes.join("\n"));
                    toast.success("Codes copiés");
                  }}
                >
                  <Copy className="mr-2 h-3.5 w-3.5" />
                  Copier
                </Button>
              </div>
            </div>

            <div className="space-y-3">
              <Label htmlFor="code-verification">3. Entrez un code pour confirmer</Label>
              <Input
                id="code-verification"
                type="text"
                inputMode="numeric"
                placeholder="000000"
                maxLength={6}
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
                className="max-w-[200px] text-center text-lg tracking-widest"
              />
            </div>

            <div className="flex gap-2">
              <Button onClick={confirmer2FA} disabled={code.length < 6}>
                Activer le 2FA
              </Button>
              <Button variant="ghost" onClick={() => { setEtape("idle"); setCode(""); }}>
                Annuler
              </Button>
            </div>
          </div>
        )}

        {/* Étape: Désactiver */}
        {etape === "disable" && (
          <div className="space-y-4">
            <Label htmlFor="code-disable">Entrez un code TOTP pour confirmer la désactivation</Label>
            <Input
              id="code-disable"
              type="text"
              inputMode="numeric"
              placeholder="000000"
              maxLength={6}
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
              className="max-w-[200px] text-center text-lg tracking-widest"
            />
            <div className="flex gap-2">
              <Button variant="destructive" onClick={desactiver} disabled={code.length < 6}>
                Confirmer la désactivation
              </Button>
              <Button variant="ghost" onClick={() => { setEtape("idle"); setCode(""); }}>
                Annuler
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
