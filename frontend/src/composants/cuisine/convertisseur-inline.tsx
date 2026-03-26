"use client";

import { useState } from "react";
import { ArrowLeftRight } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "../ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";

// ─── Conversions définies ──────────────────────────────────

type Unite = {
  label: string;
  /** Facteur de conversion vers l'unité de base du groupe (g ou ml) */
  facteur: number;
};

const GROUPES: { nom: string; base: string; unites: Unite[] }[] = [
  {
    nom: "Masse",
    base: "g",
    unites: [
      { label: "g", facteur: 1 },
      { label: "kg", facteur: 1000 },
      { label: "mg", facteur: 0.001 },
      { label: "oz", facteur: 28.3495 },
      { label: "lb", facteur: 453.592 },
    ],
  },
  {
    nom: "Volume",
    base: "ml",
    unites: [
      { label: "ml", facteur: 1 },
      { label: "cl", facteur: 10 },
      { label: "dl", facteur: 100 },
      { label: "L", facteur: 1000 },
      { label: "c. à café", facteur: 5 },
      { label: "c. à soupe", facteur: 15 },
      { label: "tasse", facteur: 250 },
      { label: "fl oz", facteur: 29.5735 },
    ],
  },
];

function toutes_unites(): string[] {
  return GROUPES.flatMap((g) => g.unites.map((u) => u.label));
}

function trouver_unite(label: string): (Unite & { base: string }) | null {
  for (const groupe of GROUPES) {
    const unite = groupe.unites.find((u) => u.label === label);
    if (unite) return { ...unite, base: groupe.base };
  }
  return null;
}

function meme_groupe(a: string, b: string): boolean {
  for (const groupe of GROUPES) {
    const labels = groupe.unites.map((u) => u.label);
    if (labels.includes(a) && labels.includes(b)) return true;
  }
  return false;
}

function convertir(valeur: number, de: string, vers: string): number | null {
  if (!meme_groupe(de, vers)) return null;
  const uDe = trouver_unite(de);
  const uVers = trouver_unite(vers);
  if (!uDe || !uVers) return null;
  const enBase = valeur * uDe.facteur;
  return enBase / uVers.facteur;
}

// ─── Composant ────────────────────────────────────────────

interface ConvertisseurInlineProps {
  /** Valeur initiale à pré-remplir */
  valeurInitiale?: number;
  /** Unité de départ à pré-sélectionner */
  uniteInitiale?: string;
  /** Texte affiché sur le déclencheur (si undefined → icône seule) */
  label?: string;
  className?: string;
}

export function ConvertisseurInline({
  valeurInitiale,
  uniteInitiale = "g",
  label,
  className = "",
}: ConvertisseurInlineProps) {
  const [valeur, setValeur] = useState(valeurInitiale?.toString() ?? "");
  const [de, setDe] = useState(uniteInitiale);
  const [vers, setVers] = useState(() => {
    // Choisir une unité de destination pertinente par défaut
    if (uniteInitiale === "g") return "oz";
    if (uniteInitiale === "kg") return "lb";
    if (uniteInitiale === "ml") return "c. à soupe";
    if (uniteInitiale === "L") return "tasse";
    return toutes_unites().find((u) => u !== uniteInitiale) ?? uniteInitiale;
  });

  const valeurNum = parseFloat(valeur);
  const resultat = !isNaN(valeurNum) && valeur !== "" ? convertir(valeurNum, de, vers) : null;

  const inverser = () => {
    const tmp = de;
    setDe(vers);
    setVers(tmp);
  };

  // Filtrer les unités compatibles avec l'unité source
  const unitesCible = toutes_unites().filter(
    (u) => u !== de && meme_groupe(de, u)
  );

  // Si on change de source et que la cible n'est plus compatible, réinitialiser
  const changerSource = (nouvelleUnite: string) => {
    setDe(nouvelleUnite);
    if (!meme_groupe(nouvelleUnite, vers)) {
      const compatible = toutes_unites().find(
        (u) => u !== nouvelleUnite && meme_groupe(nouvelleUnite, u)
      );
      setVers(compatible ?? nouvelleUnite);
    }
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className={`h-6 gap-1 px-1.5 text-xs text-muted-foreground hover:text-foreground ${className}`}
          title="Convertir"
        >
          <ArrowLeftRight className="h-3 w-3" />
          {label}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-72 p-3" align="start">
        <p className="mb-3 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
          Convertisseur
        </p>
        <div className="space-y-3">
          {/* Ligne source */}
          <div className="flex gap-2">
            <Input
              type="number"
              step="any"
              min="0"
              placeholder="Valeur"
              value={valeur}
              onChange={(e) => setValeur(e.target.value)}
              className="h-8 text-sm"
            />
            <Select value={de} onValueChange={changerSource}>
              <SelectTrigger className="h-8 w-32 text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {toutes_unites().map((u) => (
                  <SelectItem key={u} value={u} className="text-sm">
                    {u}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Bouton inverser + sélectionner la cible */}
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8 shrink-0"
              onClick={inverser}
              title="Inverser"
            >
              <ArrowLeftRight className="h-3.5 w-3.5" />
            </Button>
            <Select value={vers} onValueChange={setVers}>
              <SelectTrigger className="h-8 flex-1 text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {unitesCible.map((u) => (
                  <SelectItem key={u} value={u} className="text-sm">
                    {u}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Résultat */}
          <div className="rounded-md bg-muted px-3 py-2 text-sm">
            {resultat !== null ? (
              <>
                <span className="font-medium">
                  {valeurNum.toLocaleString("fr-FR")}&nbsp;{de}
                </span>
                {" = "}
                <span className="font-bold text-primary">
                  {resultat.toLocaleString("fr-FR", { maximumFractionDigits: 4 })}&nbsp;{vers}
                </span>
              </>
            ) : (
              <span className="text-muted-foreground">
                {valeur === "" ? "Entrez une valeur pour convertir" : "Unités incompatibles"}
              </span>
            )}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
