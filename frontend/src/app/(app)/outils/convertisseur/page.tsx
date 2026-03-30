"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";

// ─── Masse ──────────────────────────────────────────────────────

const UNITES_MASSE = {
  g: 1,
  kg: 1000,
  mg: 0.001,
  lb: 453.592,
  oz: 28.3495,
} as const;

// ─── Volume ─────────────────────────────────────────────────────

const UNITES_VOLUME = {
  mL: 1,
  L: 1000,
  cL: 10,
  "tasse": 240,
  "c. à soupe": 15,
  "c. à café": 5,
} as const;

// ─── Longueur ───────────────────────────────────────────────────

const UNITES_LONGUEUR = {
  m: 1,
  cm: 0.01,
  mm: 0.001,
  km: 1000,
  in: 0.0254,
  ft: 0.3048,
} as const;

// ─── Température ────────────────────────────────────────────────

function convertirTemperature(valeur: number, de: string, vers: string): number {
  let celsius = valeur;
  if (de === "°F") celsius = (valeur - 32) * (5 / 9);
  else if (de === "K") celsius = valeur - 273.15;

  if (vers === "°C") return celsius;
  if (vers === "°F") return celsius * (9 / 5) + 32;
  return celsius + 273.15;
}

const UNITES_TEMPERATURE = ["°C", "°F", "K"];

// ─── Composant générique ────────────────────────────────────────

function ConvertisseurUnite({
  unites,
}: {
  unites: Record<string, number>;
  titre: string;
}) {
  const cles = Object.keys(unites);
  const [valeur, setValeur] = useState(1);
  const [de, setDe] = useState(cles[0]);
  const [vers, setVers] = useState(cles[1]);

  const resultat = (valeur * unites[de]) / unites[vers];

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-[1fr_auto] gap-2 items-end">
        <div>
          <Label>Valeur</Label>
          <Input
            type="number"
            value={valeur}
            onChange={(e) => setValeur(Number(e.target.value))}
          />
        </div>
        <Select value={de} onValueChange={setDe}>
          <SelectTrigger className="w-28">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {cles.map((u) => (
              <SelectItem key={u} value={u}>
                {u}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <p className="text-center text-muted-foreground">↓</p>
      <div className="grid grid-cols-[1fr_auto] gap-2 items-end">
        <div>
          <Label>Résultat</Label>
          <Input value={resultat.toFixed(4)} readOnly className="bg-muted" />
        </div>
        <Select value={vers} onValueChange={setVers}>
          <SelectTrigger className="w-28">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {cles.map((u) => (
              <SelectItem key={u} value={u}>
                {u}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}

function ConvertisseurTemperature() {
  const [valeur, setValeur] = useState(100);
  const [de, setDe] = useState("°C");
  const [vers, setVers] = useState("°F");

  const resultat = convertirTemperature(valeur, de, vers);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-[1fr_auto] gap-2 items-end">
        <div>
          <Label>Valeur</Label>
          <Input
            type="number"
            value={valeur}
            onChange={(e) => setValeur(Number(e.target.value))}
          />
        </div>
        <Select value={de} onValueChange={setDe}>
          <SelectTrigger className="w-28">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {UNITES_TEMPERATURE.map((u) => (
              <SelectItem key={u} value={u}>
                {u}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <p className="text-center text-muted-foreground">↓</p>
      <div className="grid grid-cols-[1fr_auto] gap-2 items-end">
        <div>
          <Label>Résultat</Label>
          <Input value={resultat.toFixed(2)} readOnly className="bg-muted" />
        </div>
        <Select value={vers} onValueChange={setVers}>
          <SelectTrigger className="w-28">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {UNITES_TEMPERATURE.map((u) => (
              <SelectItem key={u} value={u}>
                {u}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}

export default function ConvertisseurPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">🔄 Convertisseur</h1>

      <Card className="max-w-lg mx-auto">
        <CardHeader>
          <CardTitle>Convertisseur d&apos;unités</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="masse">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="masse">Masse</TabsTrigger>
              <TabsTrigger value="volume">Volume</TabsTrigger>
              <TabsTrigger value="longueur">Longueur</TabsTrigger>
              <TabsTrigger value="temperature">Temp.</TabsTrigger>
            </TabsList>
            <TabsContent value="masse" className="pt-4">
              <ConvertisseurUnite unites={UNITES_MASSE} titre="Masse" />
            </TabsContent>
            <TabsContent value="volume" className="pt-4">
              <ConvertisseurUnite unites={UNITES_VOLUME} titre="Volume" />
            </TabsContent>
            <TabsContent value="longueur" className="pt-4">
              <ConvertisseurUnite unites={UNITES_LONGUEUR} titre="Longueur" />
            </TabsContent>
            <TabsContent value="temperature" className="pt-4">
              <ConvertisseurTemperature />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
