// ═══════════════════════════════════════════════════════════
// Page Paramètres (onglets)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
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
} from "lucide-react";
import { useTheme } from "next-themes";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { utiliserAuth } from "@/hooks/utiliser-auth";
import { utiliserMutation, utiliserInvalidation } from "@/hooks/utiliser-api";
import { clientApi } from "@/lib/api/client";

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

        {/* Onglet Profil */}
        <TabsContent value="profil">
          <OngletProfil utilisateur={utilisateur} />
        </TabsContent>

        {/* Onglet Affichage */}
        <TabsContent value="affichage">
          <OngletAffichage />
        </TabsContent>

        {/* Onglet IA */}
        <TabsContent value="ia">
          <OngletIA />
        </TabsContent>

        {/* Onglet Données */}
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
    { onSuccess: () => invalider(["auth", "profil"]) }
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
