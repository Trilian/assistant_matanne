// ═══════════════════════════════════════════════════════════
// Error boundary global — Sentry intégré
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Button } from "@/composants/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Envoyer l'erreur à Sentry si configuré
    try {
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      const Sentry = require("@sentry/nextjs");
      Sentry.captureException(error);
    } catch {
      // Sentry non installé — log console
      console.error("Erreur non gérée:", error);
    }
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="max-w-md w-full">
        <CardHeader>
          <CardTitle className="text-destructive">
            ⚠️ Une erreur est survenue
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {error.message || "Une erreur inattendue s'est produite."}
          </p>
        </CardContent>
        <CardFooter className="flex gap-2">
          <Button onClick={reset}>Réessayer</Button>
          <Button variant="outline" asChild>
            <Link href="/">Retour à l&apos;accueil</Link>
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
