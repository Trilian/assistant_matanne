"use client";

import { useCallback, useMemo, useState } from "react";
import { CheckCircle2, GraduationCap, Monitor, Moon, Sparkles, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Label } from "@/composants/ui/label";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { resetOnboarding, TourOnboarding } from "@/composants/disposition/tour-onboarding";

type ThemeAvecTransition = Document & {
  startViewTransition?: (callback: () => void) => void;
};

export function OngletAffichage() {
  const { theme, setTheme } = useTheme();
  const [afficherTour, setAfficherTour] = useState(false);

  const themes = [
    { valeur: "light", label: "Clair", Icone: Sun },
    { valeur: "dark", label: "Sombre", Icone: Moon },
    { valeur: "system", label: "Système", Icone: Monitor },
  ] as const;

  const themeActif = useMemo(() => {
    if (theme === "dark") return "Sombre";
    if (theme === "light") return "Clair";
    return "Système";
  }, [theme]);

  const appliquerThemeAvecTransition = useCallback(
    (valeur: "light" | "dark" | "system") => {
      if (typeof document === "undefined") {
        setTheme(valeur);
        return;
      }

      const documentAvecTransition = document as ThemeAvecTransition;
      if (typeof documentAvecTransition.startViewTransition === "function") {
        documentAvecTransition.startViewTransition(() => setTheme(valeur));
        return;
      }

      setTheme(valeur);
    },
    [setTheme]
  );

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
          <div className="space-y-3">
            <div className="space-y-2">
              <Label>Thème</Label>
              <div className="flex gap-2">
                {themes.map(({ valeur, label, Icone }) => (
                  <Button
                    key={valeur}
                    variant={theme === valeur ? "default" : "outline"}
                    className="flex-1"
                    onClick={() => appliquerThemeAvecTransition(valeur)}
                  >
                    <Icone className="mr-2 h-4 w-4" />
                    {label}
                  </Button>
                ))}
              </div>
            </div>

            <div className="rounded-xl border bg-muted/30 p-4 space-y-3">
              <div className="flex items-center justify-between gap-2">
                <div>
                  <p className="text-sm font-semibold">Aperçu en direct</p>
                  <p className="text-xs text-muted-foreground">
                    Le thème s&apos;applique immédiatement avec transition fluide si le navigateur le supporte.
                  </p>
                </div>
                <Badge variant="secondary">Mode actif : {themeActif}</Badge>
              </div>

              <div className="grid gap-3 md:grid-cols-[1.2fr_.8fr]">
                <div className="rounded-xl border bg-card p-3 shadow-sm space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <div>
                      <p className="text-sm font-medium">Dashboard famille</p>
                      <p className="text-xs text-muted-foreground">Vue de contrôle rapide</p>
                    </div>
                    <Sparkles className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Badge className="bg-emerald-500/10 text-emerald-700 dark:text-emerald-300" variant="outline">Cuisine OK</Badge>
                    <Badge className="bg-sky-500/10 text-sky-700 dark:text-sky-300" variant="outline">3 rappels</Badge>
                  </div>
                </div>

                <div className="rounded-xl border border-dashed bg-background p-3 text-sm space-y-2">
                  <div className="flex items-center gap-2 font-medium">
                    <CheckCircle2 className="h-4 w-4 text-primary" />
                    Contraste validé
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Lisibilité optimisée pour mobile, tablette et mode nuit cuisine.
                  </p>
                </div>
              </div>
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
                      Redécouvrez les fonctionnalités principales de l&apos;application
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
        <TourOnboarding forcer={true} onTerminer={() => setAfficherTour(false)} />
      )}
    </>
  );
}
