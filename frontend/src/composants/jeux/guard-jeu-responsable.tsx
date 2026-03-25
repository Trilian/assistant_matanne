"use client";

import { Shield } from "lucide-react";
import Link from "next/link";
import { Button } from "@/composants/ui/button";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirSuiviResponsable } from "@/bibliotheque/api/jeux";
import type { SuiviResponsable } from "@/types/jeux";

interface GuardJeuResponsableProps {
  children: React.ReactNode;
}

export function GuardJeuResponsable({ children }: GuardJeuResponsableProps) {
  const { data: suivi } = utiliserRequete<SuiviResponsable>(
    ["jeux", "responsable", "suivi"],
    obtenirSuiviResponsable,
    // Ne pas lancer d'erreur si pas de session — l'overlay ne doit pas bloquer la page entière si l'API est indisponible
    { retry: false }
  );

  const exclusionActive =
    !!suivi?.auto_exclusion_jusqu_a &&
    new Date(suivi.auto_exclusion_jusqu_a) > new Date();

  const cooldownActif = !!suivi?.cooldown_actif;

  if (!exclusionActive && !cooldownActif) {
    return <>{children}</>;
  }

  const jusquAu = suivi?.auto_exclusion_jusqu_a
    ? new Date(suivi.auto_exclusion_jusqu_a).toLocaleDateString("fr-FR", {
        day: "numeric",
        month: "long",
        year: "numeric",
      })
    : null;

  return (
    <div className="relative">
      {/* Contenu flouté */}
      <div className="pointer-events-none blur-sm select-none" aria-hidden>
        {children}
      </div>

      {/* Overlay bloquant */}
      <div className="absolute inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm rounded-lg z-50">
        <div className="text-center space-y-4 p-8 max-w-sm">
          <Shield className="h-12 w-12 mx-auto text-muted-foreground" />
          {exclusionActive ? (
            <>
              <h2 className="text-xl font-bold">Auto-exclusion active</h2>
              <p className="text-muted-foreground">
                Vous avez activé une auto-exclusion jusqu&apos;au{" "}
                <span className="font-semibold text-foreground">{jusquAu}</span>.
              </p>
              <p className="text-sm text-muted-foreground">
                Cette période de pause est là pour vous protéger.
              </p>
            </>
          ) : (
            <>
              <h2 className="text-xl font-bold">Période de réflexion</h2>
              <p className="text-muted-foreground">
                Un cooldown est actuellement actif sur votre compte.
              </p>
            </>
          )}
          <Link href="/jeux/responsable">
            <Button variant="outline" className="mt-2">
              Gérer mon compte
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
