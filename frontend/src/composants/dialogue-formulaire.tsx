// ═══════════════════════════════════════════════════════════
// DialogueFormulaire — Composant réutilisable CRUD dialog
// ═══════════════════════════════════════════════════════════

"use client";

import { type ReactNode, useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/composants/ui/dialog";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Textarea } from "@/composants/ui/textarea";
import type { ObjetDonnees } from "@/types/commun";

interface OptionChamp {
  valeur: string;
  label: string;
}

interface ChampFormulaire {
  id?: string;
  nom?: string;
  label: string;
  type: "text" | "number" | "date" | "email" | "textarea" | "select";
  value?: string | number;
  defaut?: string | number;
  onChange?: (value: string) => void;
  required?: boolean;
  requis?: boolean;
  obligatoire?: boolean;
  options?: OptionChamp[];
}

interface DialogueFormulaireProps {
  ouvert: boolean;
  titre: string;
  description?: string;
  children?: ReactNode;
  champs?: ChampFormulaire[];
  valeurInitiale?: ObjetDonnees;
  onClose?: () => void;
  onFermer?: () => void;
  onChangerOuvert?: (ouvert: boolean) => void;
  onOuvertChange?: (ouvert: boolean) => void;
  onSubmit?: () => void;
  onSoumettre?: (donnees: ObjetDonnees) => void;
  enCours?: boolean;
  chargement?: boolean;
  enChargement?: boolean;
  texteBouton?: string;
  stockageSuggestionsCle?: string;
}

export function DialogueFormulaire({
  ouvert,
  titre,
  description,
  children,
  champs,
  valeurInitiale,
  onClose,
  onFermer,
  onChangerOuvert,
  onOuvertChange,
  onSubmit,
  onSoumettre,
  enCours = false,
  chargement,
  enChargement,
  texteBouton = "Enregistrer",
  stockageSuggestionsCle = "dialogue-formulaire-suggestions",
}: DialogueFormulaireProps) {
  const [valeursInternes, setValeursInternes] = useState<ObjetDonnees>({});
  const [suggestions, setSuggestions] = useState<Record<string, string[]>>({});

  useEffect(() => {
    if (!ouvert || !champs) return;

    setValeursInternes(
      champs.reduce<ObjetDonnees>((acc, champ) => {
        const cle = champ.id ?? champ.nom;
        if (!cle) return acc;
        acc[cle] = champ.value ?? champ.defaut ?? valeurInitiale?.[cle] ?? "";
        return acc;
      }, {})
    );
  }, [champs, ouvert, valeurInitiale]);

  useEffect(() => {
    if (!ouvert || typeof window === "undefined") return;
    try {
      const brut = window.localStorage.getItem(stockageSuggestionsCle);
      if (!brut) return;
      const parsed = JSON.parse(brut) as Record<string, string[]>;
      setSuggestions(parsed);
    } catch {
      setSuggestions({});
    }
  }, [ouvert, stockageSuggestionsCle]);

  const fermer = onClose ?? onFermer ?? (() => onChangerOuvert?.(false) ?? onOuvertChange?.(false));
  const estEnCours = enCours || chargement || enChargement;

  function obtenirCle(champ: ChampFormulaire) {
    return champ.id ?? champ.nom ?? champ.label;
  }

  function obtenirValeur(champ: ChampFormulaire) {
    const cle = obtenirCle(champ);
    return String(champ.value ?? valeursInternes[cle] ?? champ.defaut ?? "");
  }

  function changerValeur(champ: ChampFormulaire, valeur: string) {
    const cle = obtenirCle(champ);
    setValeursInternes((precedent) => ({ ...precedent, [cle]: valeur }));
    champ.onChange?.(valeur);
  }

  function soumettre() {
    if (typeof window !== "undefined" && champs?.length) {
      const prochain: Record<string, string[]> = { ...suggestions };
      for (const champ of champs) {
        if (champ.type !== "text" && champ.type !== "email") continue;
        const cle = obtenirCle(champ);
        const valeur = obtenirValeur(champ).trim();
        if (!valeur) continue;
        const existants = prochain[cle] ?? [];
        const fusion = [valeur, ...existants.filter((v) => v !== valeur)].slice(0, 10);
        prochain[cle] = fusion;
      }
      setSuggestions(prochain);
      window.localStorage.setItem(stockageSuggestionsCle, JSON.stringify(prochain));
    }

    if (onSubmit) {
      onSubmit();
      return;
    }

    if (onSoumettre) {
      const donnees = (champs ?? []).reduce<ObjetDonnees>((acc, champ) => {
        acc[obtenirCle(champ)] = obtenirValeur(champ);
        return acc;
      }, {});
      onSoumettre(donnees);
    }
  }

  return (
    <Dialog open={ouvert} onOpenChange={(v) => !v && fermer?.()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{titre}</DialogTitle>
          {description ? <p className="text-sm text-muted-foreground">{description}</p> : null}
        </DialogHeader>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            soumettre();
          }}
          className="space-y-4"
        >
          {children ??
            champs?.map((champ) => (
              <div key={obtenirCle(champ)} className="space-y-2">
                <Label>{champ.label}</Label>
                {champ.type === "textarea" ? (
                  <Textarea
                    aria-label={champ.label}
                    value={obtenirValeur(champ)}
                    onChange={(e) => changerValeur(champ, e.target.value)}
                    required={champ.required || champ.requis || champ.obligatoire}
                  />
                ) : champ.type === "select" ? (
                  <select
                    title={champ.label}
                    aria-label={champ.label}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={obtenirValeur(champ)}
                    onChange={(e) => changerValeur(champ, e.target.value)}
                    required={champ.required || champ.requis || champ.obligatoire}
                  >
                    <option value="">Sélectionner</option>
                    {champ.options?.map((option) => (
                      <option key={option.valeur} value={option.valeur}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                ) : (
                  <Input
                    aria-label={champ.label}
                    type={champ.type}
                    value={obtenirValeur(champ)}
                    onChange={(e) => changerValeur(champ, e.target.value)}
                    required={champ.required || champ.requis || champ.obligatoire}
                    list={
                      (champ.type === "text" || champ.type === "email")
                        ? `suggestions-${obtenirCle(champ)}`
                        : undefined
                    }
                  />
                )}
                {(champ.type === "text" || champ.type === "email") && (
                  <datalist id={`suggestions-${obtenirCle(champ)}`}>
                    {(suggestions[obtenirCle(champ)] ?? []).map((suggestion) => (
                      <option key={suggestion} value={suggestion} />
                    ))}
                  </datalist>
                )}
              </div>
            ))}
          <Button type="submit" className="w-full" disabled={estEnCours}>
            {estEnCours ? "En cours..." : texteBouton}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
