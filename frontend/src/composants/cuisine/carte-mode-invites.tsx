"use client";

import { RotateCcw, Sparkles, Users } from "lucide-react";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Input } from "@/composants/ui/input";
import type { ContexteModeInvites } from "@/crochets/utiliser-mode-invites";

interface CarteModeInvitesProps {
  contexte: ContexteModeInvites;
  onChange: (patch: Partial<ContexteModeInvites>) => void;
  onReset: () => void;
  suggestionsEvenements?: string[];
  description?: string;
}

export function CarteModeInvites({
  contexte,
  onChange,
  onReset,
  suggestionsEvenements = [],
  description = "Adaptez portions, planning et suggestions quand vous recevez.",
}: CarteModeInvitesProps) {
  const suggestionsDisponibles = suggestionsEvenements.filter(
    (suggestion) => !contexte.evenements.includes(suggestion)
  );

  return (
    <Card className={contexte.actif ? "border-amber-300 bg-amber-50/60 dark:border-amber-800 dark:bg-amber-950/20" : ""}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle className="flex items-center gap-2 text-base">
              <Users className="h-4 w-4 text-amber-600" />
              Mode invites
            </CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
          <Button variant="ghost" size="sm" onClick={onReset}>
            <RotateCcw className="mr-1 h-4 w-4" />
            Reinit.
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <label className="flex items-center gap-2 text-sm font-medium cursor-pointer">
          <input
            type="checkbox"
            checked={contexte.actif}
            onChange={(e) => onChange({ actif: e.target.checked })}
            className="rounded"
          />
          Activer l'adaptation invites
        </label>

        <div className="grid gap-3 sm:grid-cols-2">
          <div>
            <p className="text-sm font-medium mb-1">Nombre d&apos;invites</p>
            <Input
              type="number"
              min={0}
              max={20}
              value={contexte.nbInvites}
              onChange={(e) => onChange({ nbInvites: Number(e.target.value) || 0 })}
              disabled={!contexte.actif}
            />
          </div>
          <div>
            <p className="text-sm font-medium mb-1">Occasion</p>
            <Input
              value={contexte.occasion}
              onChange={(e) => onChange({ occasion: e.target.value })}
              placeholder="Anniversaire, apero, brunch..."
              disabled={!contexte.actif}
            />
          </div>
        </div>

        {(contexte.evenements.length > 0 || suggestionsDisponibles.length > 0) && (
          <div className="space-y-2">
            <p className="text-sm font-medium flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-amber-600" />
              Contexte evenementiel
            </p>

            {contexte.evenements.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {contexte.evenements.map((evenement) => (
                  <button
                    key={evenement}
                    type="button"
                    onClick={() =>
                      onChange({
                        evenements: contexte.evenements.filter((item) => item !== evenement),
                      })
                    }
                    className="rounded-full border bg-background px-2 py-1 text-xs"
                  >
                    {evenement} x
                  </button>
                ))}
              </div>
            )}

            {suggestionsDisponibles.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {suggestionsDisponibles.slice(0, 6).map((suggestion) => (
                  <Badge
                    key={suggestion}
                    variant="outline"
                    className="cursor-pointer hover:bg-accent"
                    onClick={() =>
                      onChange({ evenements: [...contexte.evenements, suggestion] })
                    }
                  >
                    + {suggestion}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}