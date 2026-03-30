// ═══════════════════════════════════════════════════════════
// Error boundary global
// ═══════════════════════════════════════════════════════════

"use client";

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
