"use client";

import { Search } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";

const TYPES_LOCAL = [
  { value: "", label: "Toutes typologies" },
  { value: "Maison", label: "Maison" },
  { value: "Appartement", label: "Appartement" },
  { value: "Dépendance", label: "Dépendance" },
  { value: "Local industriel. commercial ou assimilé", label: "Local commercial" },
];

interface FiltresMarcheHabitatProps {
  commune: string;
  codePostal: string;
  typeLocal: string;
  nbPiecesMin?: string;
  isFetching: boolean;
  onCommuneChange: (value: string) => void;
  onCodePostalChange: (value: string) => void;
  onTypeLocalChange: (value: string) => void;
  onNbPiecesMinChange?: (value: string) => void;
  onRefresh: () => void;
}

export function FiltresMarcheHabitat({
  commune,
  codePostal,
  typeLocal,
  nbPiecesMin = "",
  isFetching,
  onCommuneChange,
  onCodePostalChange,
  onTypeLocalChange,
  onNbPiecesMinChange,
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
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="type-habitat">Type de bien</Label>
            <Select value={typeLocal} onValueChange={onTypeLocalChange}>
              <SelectTrigger id="type-habitat">
                <SelectValue placeholder="Toutes typologies" />
              </SelectTrigger>
              <SelectContent>
                {TYPES_LOCAL.map((t) => (
                  <SelectItem key={t.value} value={t.value}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {onNbPiecesMinChange && (
            <div className="space-y-2">
              <Label htmlFor="pieces-habitat">Pièces min.</Label>
              <Input
                id="pieces-habitat"
                value={nbPiecesMin}
                onChange={(event) => onNbPiecesMinChange(event.target.value)}
                inputMode="numeric"
                placeholder="ex. 3"
              />
            </div>
          )}
        </div>
        <Button onClick={onRefresh} disabled={isFetching} className="w-full sm:w-auto">
          <Search className="mr-2 h-4 w-4" />
          {isFetching ? "Chargement…" : "Actualiser l'analyse"}
        </Button>
      </CardContent>
    </Card>
  );
}
