"use client";

import { useState } from "react";
import { GraduationCap, Monitor, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Label } from "@/composants/ui/label";
import { Button } from "@/composants/ui/button";
import { resetOnboarding, TourOnboarding } from "@/composants/disposition/tour-onboarding";

export function OngletAffichage() {
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
