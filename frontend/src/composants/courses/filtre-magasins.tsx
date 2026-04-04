"use client";

import { Send, ShoppingCart, Store } from "lucide-react";

import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import {
  COULEURS_MAGASINS,
  LIBELLES_MAGASINS,
  type MagasinCible,
} from "@/types/courses";

type FiltreMagasinsProps = {
  compteurs: Record<string, number>;
  magasinActif: string | null;
  onChangerMagasin: (magasin: string | null) => void;
  onEnvoyerTelegram?: (magasin: MagasinCible) => void;
  onSyncDrive?: () => void;
  enEnvoiTelegram?: boolean;
};

const MAGASINS_ORDRE: MagasinCible[] = [
  "bio_coop",
  "grand_frais",
  "carrefour_drive",
];

export function FiltreMagasins({
  compteurs,
  magasinActif,
  onChangerMagasin,
  onEnvoyerTelegram,
  onSyncDrive,
  enEnvoiTelegram,
}: FiltreMagasinsProps) {
  const totalArticles = Object.values(compteurs).reduce((s, c) => s + c, 0);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap gap-2">
        {/* Onglet Tous */}
        <Button
          variant={magasinActif === null ? "default" : "outline"}
          size="sm"
          onClick={() => onChangerMagasin(null)}
        >
          <Store className="mr-1 h-4 w-4" />
          Tous
          <Badge variant="secondary" className="ml-1.5">
            {totalArticles}
          </Badge>
        </Button>

        {/* Onglets par magasin */}
        {MAGASINS_ORDRE.map((magasin) => {
          const count = compteurs[magasin] ?? 0;
          const estActif = magasinActif === magasin;
          const couleurs = COULEURS_MAGASINS[magasin];

          return (
            <Button
              key={magasin}
              variant={estActif ? "default" : "outline"}
              size="sm"
              onClick={() => onChangerMagasin(estActif ? null : magasin)}
              className={estActif ? "" : ""}
            >
              {LIBELLES_MAGASINS[magasin]}
              {count > 0 && (
                <Badge
                  variant="secondary"
                  className={`ml-1.5 ${!estActif ? couleurs : ""}`}
                >
                  {count}
                </Badge>
              )}
            </Button>
          );
        })}
      </div>

      {/* Boutons d'action contextuels */}
      {magasinActif && (
        <div className="flex gap-2">
          {(magasinActif === "bio_coop" || magasinActif === "grand_frais") &&
            onEnvoyerTelegram && (
              <Button
                size="sm"
                variant="outline"
                onClick={() =>
                  onEnvoyerTelegram(magasinActif as MagasinCible)
                }
                disabled={enEnvoiTelegram || (compteurs[magasinActif] ?? 0) === 0}
              >
                <Send className="mr-1 h-4 w-4" />
                📱 Envoyer sur Telegram
              </Button>
            )}

          {magasinActif === "carrefour_drive" && onSyncDrive && (
            <Button
              size="sm"
              variant="outline"
              onClick={onSyncDrive}
              disabled={(compteurs["carrefour_drive"] ?? 0) === 0}
            >
              <ShoppingCart className="mr-1 h-4 w-4" />
              🛒 Ajouter au Drive
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
