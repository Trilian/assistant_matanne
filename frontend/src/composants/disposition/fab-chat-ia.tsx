// ═══════════════════════════════════════════════════════════
// FAB Chat IA — Bouton flottant omniprésent (AC2)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { MessageCircle, X } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Textarea } from "@/composants/ui/textarea";
import { clientApi } from "@/bibliotheque/api/client";
import type { ReponseChatIA } from "@/bibliotheque/api/outils";

/**
 * Bouton flottant d'accès rapide au chat IA.
 *
 * - Mode compact : icône en bas à droite (évite le conflit avec la nav mobile)
 * - Clic sur fond desktop → popout mini-chat (envoi vers /outils/chat-ia)
 * - Sur mobile, redirige directement vers /outils/chat-ia
 */
export function FabChatIA() {
  const router = useRouter();
  const pathname = usePathname();
  const [ouvert, setOuvert] = useState(false);
  const [message, setMessage] = useState("");
  const [reponse, setReponse] = useState<string | null>(null);
  const [chargement, setChargement] = useState(false);

  // Ne pas afficher sur la page chat-ia elle-même
  if (pathname === "/outils/chat-ia") return null;

  // Détection du contexte page pour le chat IA contextuel
  const segments = pathname.split("/").filter(Boolean);
  const contexteDetecte = segments[0] ?? "general";

  const SUGGESTIONS_CONTEXTUELLES: Record<string, string[]> = {
    cuisine: ["Quoi manger ce soir ?", "Idée batch cooking", "Que faire avec mes restes ?"],
    famille: ["Activité pour Jules ?", "Idée sortie weekend", "Routine du soir"],
    maison: ["Entretien ce mois-ci ?", "Que faire au jardin ?", "Projet bricolage facile"],
    jeux: ["Analyse mes paris", "Statistiques bankroll"],
    outils: ["Organiser ma semaine", "Conseil du jour"],
  };

  const suggestions = SUGGESTIONS_CONTEXTUELLES[contexteDetecte] ?? [];

  const ACCUEIL_CONTEXTUEL: Record<string, string> = {
    cuisine: "🍽️ Besoin d'aide en cuisine ?",
    famille: "👨‍👩‍👦 Comment aider la famille ?",
    maison: "🏠 Une question sur la maison ?",
    jeux: "🎮 Analyse de jeux ?",
  };

  const messageAccueil = ACCUEIL_CONTEXTUEL[contexteDetecte] ?? "✨ Comment puis-je vous aider ?";

  async function envoyer(texte?: string) {
    const msg = texte ?? message;
    if (!msg.trim()) return;
    setChargement(true);
    setReponse(null);
    try {
      const { data } = await clientApi.post<ReponseChatIA>("/assistant/chat", {
        message: msg.trim(),
        contexte: contexteDetecte,
        historique: [],
      });
      setReponse(data.reponse);
      setMessage("");
    } catch {
      setReponse("Erreur : impossible de joindre l'IA. Réessayez dans quelques instants.");
    } finally {
      setChargement(false);
    }
  }

  function ouvrirChatComplet() {
    router.push("/outils/chat-ia");
    setOuvert(false);
  }

  return (
    <div className="fixed bottom-[5.5rem] right-4 md:bottom-6 z-40 flex flex-col items-end gap-2">
      {/* Mini-chat popout */}
      {ouvert && (
        <Card className="w-80 shadow-xl border animate-in slide-in-from-bottom-4">
          <CardHeader className="pb-2 flex-row items-center justify-between">
            <CardTitle className="text-sm font-semibold">{messageAccueil}</CardTitle>
            <div className="flex gap-1">
              <Button
                variant="ghost"
                size="sm"
                className="text-xs h-7"
                onClick={ouvrirChatComplet}
              >
                Ouvrir
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7"
                onClick={() => setOuvert(false)}
                aria-label="Fermer"
              >
                <X className="h-3.5 w-3.5" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-2 pb-3">
            {/* Suggestions contextuelles */}
            {!reponse && suggestions.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {suggestions.map((s) => (
                  <button
                    key={s}
                    type="button"
                    className="text-[11px] px-2 py-1 rounded-full bg-muted hover:bg-muted/80 transition-colors text-muted-foreground"
                    onClick={() => void envoyer(s)}
                    disabled={chargement}
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
            {reponse && (
              <div className="rounded-md bg-muted p-2 text-sm max-h-40 overflow-y-auto">
                {reponse}
              </div>
            )}
            <Textarea
              placeholder="Posez une question…"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="resize-none text-sm min-h-[60px]"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  void envoyer();
                }
              }}
            />
            <Button
              onClick={() => void envoyer()}
              disabled={chargement || !message.trim()}
              size="sm"
              className="w-full"
            >
              {chargement ? "Envoi…" : "Envoyer"}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Bouton FAB principal */}
      <Button
        size="icon"
        className="h-12 w-12 rounded-full shadow-lg bg-primary hover:bg-primary/90"
        onClick={() => setOuvert((o) => !o)}
        aria-label={ouvert ? "Fermer le chat IA" : "Ouvrir le chat IA"}
      >
        {ouvert ? (
          <X className="h-5 w-5" />
        ) : (
          <MessageCircle className="h-5 w-5" />
        )}
      </Button>
    </div>
  );
}
