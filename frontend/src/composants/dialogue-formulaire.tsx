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
  valeurInitiale?: object;
  onClose?: () => void;
  onFermer?: () => void;
  onChangerOuvert?: (ouvert: boolean) => void;
  onOuvertChange?: (ouvert: boolean) => void;
  onSubmit?: () => void;
  onSoumettre?: (donnees: Record<string, unknown>) => void;
  enCours?: boolean;
  chargement?: boolean;
  enChargement?: boolean;
  texteBouton?: string;
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
}: DialogueFormulaireProps) {
  const [valeursInternes, setValeursInternes] = useState<Record<string, unknown>>({});

  useEffect(() => {
    if (!ouvert || !champs) return;

    setValeursInternes(
      champs.reduce<Record<string, unknown>>((acc, champ) => {
        const cle = champ.id ?? champ.nom;
        if (!cle) return acc;
        acc[cle] = champ.value ?? champ.defaut ?? (valeurInitiale as Record<string, unknown> | undefined)?.[cle] ?? "";
        return acc;
      }, {})
    );
  }, [champs, ouvert, valeurInitiale]);

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
    if (onSubmit) {
      onSubmit();
      return;
    }

    if (onSoumettre) {
      const donnees = (champs ?? []).reduce<Record<string, unknown>>((acc, champ) => {
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
                <Label htmlFor={obtenirCle(champ)}>{champ.label}</Label>
                {champ.type === "textarea" ? (
                  <Textarea
                    id={obtenirCle(champ)}
                    value={obtenirValeur(champ)}
                    onChange={(e) => changerValeur(champ, e.target.value)}
                    required={champ.required || champ.requis || champ.obligatoire}
                  />
                ) : champ.type === "select" ? (
                  <select
                    id={obtenirCle(champ)}
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
                    id={obtenirCle(champ)}
                    type={champ.type}
                    value={obtenirValeur(champ)}
                    onChange={(e) => changerValeur(champ, e.target.value)}
                    required={champ.required || champ.requis || champ.obligatoire}
                  />
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
