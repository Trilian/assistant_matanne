// ═══════════════════════════════════════════════════════════
// Layout Admin — Protection par rôle admin
// ═══════════════════════════════════════════════════════════

"use client";

import { utiliserAuth } from "@/crochets/utiliser-auth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function LayoutAdmin({
  children,
}: {
  children: React.ReactNode;
}) {
  const { utilisateur, estChargement } = utiliserAuth();
  const router = useRouter();

  useEffect(() => {
    if (!estChargement && utilisateur && utilisateur.role !== "admin") {
      router.replace("/");
    }
  }, [utilisateur, estChargement, router]);

  if (estChargement) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-muted-foreground">Vérification des accès…</div>
      </div>
    );
  }

  if (!utilisateur || utilisateur.role !== "admin") {
    return null;
  }

  return <>{children}</>;
}
