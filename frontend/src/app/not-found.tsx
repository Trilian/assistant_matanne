// ═══════════════════════════════════════════════════════════
// Page 404
// ═══════════════════════════════════════════════════════════

import Link from "next/link";
import { Button } from "@/composants/ui/button";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 p-4 text-center">
      <p className="text-6xl">🔍</p>
      <h1 className="text-2xl font-bold">Page introuvable</h1>
      <p className="text-muted-foreground max-w-sm">
        La page que vous recherchez n&apos;existe pas ou a été déplacée.
      </p>
      <Button asChild>
        <Link href="/">Retour à l&apos;accueil</Link>
      </Button>
    </div>
  );
}
