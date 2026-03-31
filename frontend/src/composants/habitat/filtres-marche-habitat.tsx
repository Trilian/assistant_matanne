"use client";

import { Search } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";

interface FiltresMarcheHabitatProps {
  commune: string;
  codePostal: string;
  typeLocal: string;
  isFetching: boolean;
  onCommuneChange: (value: string) => void;
  onCodePostalChange: (value: string) => void;
  onTypeLocalChange: (value: string) => void;
  onRefresh: () => void;
}

export function FiltresMarcheHabitat({
  commune,
  codePostal,
  typeLocal,
  isFetching,
  onCommuneChange,
  onCodePostalChange,
  onTypeLocalChange,
  onRefresh,
}: FiltresMarcheHabitatProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Filtres DVF</CardTitle>
        <CardDescription>Ajuste la zone et la typologie avant de relancer le chargement.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="commune-habitat">Commune</Label>
            <Input id="commune-habitat" value={commune} onChange={(event) => onCommuneChange(event.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="cp-habitat">Code postal</Label>
            <Input id="cp-habitat" value={codePostal} onChange={(event) => onCodePostalChange(event.target.value)} inputMode="numeric" />
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="type-habitat">Type local</Label>
          <Input id="type-habitat" value={typeLocal} onChange={(event) => onTypeLocalChange(event.target.value)} placeholder="Maison, Appartement..." />
        </div>
        <Button onClick={onRefresh} disabled={isFetching} className="w-full sm:w-auto">
          <Search className="mr-2 h-4 w-4" />
          {isFetching ? "Chargement..." : "Actualiser l'analyse"}
        </Button>
      </CardContent>
    </Card>
  );
}
