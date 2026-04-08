// ═══════════════════════════════════════════════════════════
// Page Auth Callback — Traitement du lien de confirmation Supabase
// ═══════════════════════════════════════════════════════════
// Supabase redirige ici après confirmation d'email avec le token
// dans le hash : #access_token=...&type=signup
// Le middleware laisse passer cette route sans authentification.
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function AuthCallbackPage() {
  const router = useRouter();
  const [message, setMessage] = useState("Confirmation en cours…");

  useEffect(() => {
    // Le hash est uniquement côté client — jamais envoyé au serveur.
    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);

    const accessToken = params.get("access_token");
    const refreshToken = params.get("refresh_token");
    const errorCode = params.get("error_code");
    const errorDesc = params.get("error_description");

    // Supabase peut rediriger ici avec une erreur
    if (errorCode || !accessToken) {
      setMessage(errorDesc ?? "Lien invalide ou expiré.");
      setTimeout(() => router.replace("/connexion"), 3000);
      return;
    }

    // Stocker le token Supabase dans localStorage ET cookie
    // Le cookie est lu par le middleware Next.js pour protéger les routes.
    localStorage.setItem("access_token", accessToken);
    if (refreshToken) localStorage.setItem("refresh_token", refreshToken);
    const secure = window.location.protocol === "https:" ? "; Secure" : "";
    document.cookie = `access_token=${accessToken}; path=/; SameSite=Lax; max-age=86400${secure}`;

    // Vérifier le token auprès du backend (valide via valider_token_supabase)
    setMessage("Validation du compte…");
    fetch(
      `${process.env.NEXT_PUBLIC_API_URL ?? ""}/api/v1/auth/me`,
      {
        headers: { Authorization: `Bearer ${accessToken}` },
      }
    )
      .then((res) => {
        if (res.ok) {
          setMessage("Compte confirmé ! Redirection…");
          router.replace("/");
        } else {
          setMessage("Erreur de validation. Veuillez vous reconnecter.");
          setTimeout(() => router.replace("/connexion"), 2000);
        }
      })
      .catch(() => {
        // Fallback : token stocké, on laisse le dashboard gérer
        router.replace("/");
      });
  }, [router]);

  return (
    <div className="flex flex-col items-center gap-4 text-center">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      <p className="text-muted-foreground">{message}</p>
    </div>
  );
}
