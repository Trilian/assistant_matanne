"use client";

import { useState } from "react";
import { Save } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Label } from "@/composants/ui/label";
import { Input } from "@/composants/ui/input";
import { Button } from "@/composants/ui/button";

export function OngletIA() {
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
