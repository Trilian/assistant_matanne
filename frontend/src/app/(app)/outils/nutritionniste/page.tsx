"use client";

import { useState, useRef, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { ScrollArea } from "@/composants/ui/scroll-area";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import {
  Apple,
  Bot,
  Send,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import {
  envoyerMessageChat,
  obtenirActionsRapides,
} from "@/bibliotheque/api/outils";
import type { ActionRapide } from "@/bibliotheque/api/outils";
import type { MessageChat } from "@/types/outils";
import { toast } from "sonner";
import { BoutonVocal } from "@/composants/ui/bouton-vocal";

const ACTIONS_RAPIDES_NUTRITION = [
  { label: "Analyser mon repas", message: "Analyse la valeur nutritionnelle de ce repas pour moi" },
  { label: "Équilibre de la semaine", message: "Comment équilibrer mon planning repas cette semaine ?" },
  { label: "Astuces pour Jules", message: "Conseils nutrition pour un enfant de 3 ans qui refuse les légumes" },
  { label: "Réduire sucre ajouté", message: "Comment réduire le sucre dans mes recettes familiales ?" },
];

export default function NutritionistePage() {
  const [messages, setMessages] = useState<MessageChat[]>([]);
  const [saisie, setSaisie] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  const { mutate: envoyer, isPending } = utiliserMutation(
    (message: string) =>
      envoyerMessageChat({
        message,
        contexte: "cuisine",
        historique: messages,
      }),
    {
      onSuccess: (data: { reponse: string }) => {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", contenu: data.reponse, horodatage: new Date().toISOString() },
        ]);
      },
      onError: () => toast.error("Erreur lors de la communication avec le nutritionniste IA"),
    }
  );

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function gererEnvoi(e: React.FormEvent) {
    e.preventDefault();
    if (!saisie.trim() || isPending) return;
    const message = saisie.trim();
    setMessages((prev) => [...prev, { role: "user", contenu: message, horodatage: new Date().toISOString() }]);
    setSaisie("");
    envoyer(message);
  }

  function gererActionRapide(msg: string) {
    setMessages((prev) => [...prev, { role: "user", contenu: msg, horodatage: new Date().toISOString() }]);
    envoyer(msg);
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          🥗 Nutritionniste IA
        </h1>
        <p className="text-muted-foreground">
          Conseils personnalisés en nutrition pour votre famille
        </p>
      </div>

      <div className="rounded-lg border bg-amber-50 dark:bg-amber-950 border-amber-200 dark:border-amber-800 p-3 flex gap-2 text-sm">
        <AlertCircle className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
        <span className="text-amber-800 dark:text-amber-200">
          Cet assistant fournit des informations générales. Pour un suivi médical personnalisé, consultez un diététicien-nutritionniste.
        </span>
      </div>

      <Card className="flex flex-col" style={{ height: "65vh" }}>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-base">
            <Apple className="h-5 w-5 text-green-500" />
            Chat Nutritionniste
          </CardTitle>
        </CardHeader>

        <CardContent className="flex-1 overflow-hidden flex flex-col gap-3 p-4">
          {/* Actions rapides */}
          {messages.length === 0 && (
            <div className="flex flex-wrap gap-2">
              {ACTIONS_RAPIDES_NUTRITION.map((a) => (
                <Button
                  key={a.label}
                  variant="outline"
                  size="sm"
                  className="text-xs h-8"
                  onClick={() => gererActionRapide(a.message)}
                  disabled={isPending}
                >
                  {a.label}
                </Button>
              ))}
            </div>
          )}

          {/* Messages */}
          <ScrollArea className="flex-1">
            <div className="space-y-4 pr-3">
              {messages.length === 0 && (
                <div className="flex items-center gap-3 text-muted-foreground text-sm py-8 justify-center">
                  <Bot className="h-6 w-6" />
                  Bonjour ! Je suis votre nutritionniste IA. Comment puis-je vous aider ?
                </div>
              )}
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-2 text-sm ${
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    }`}
                  >
                    {msg.contenu}
                  </div>
                </div>
              ))}
              {isPending && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-lg px-4 py-2">
                    <Skeleton className="h-4 w-32" />
                  </div>
                </div>
              )}
              <div ref={scrollRef} />
            </div>
          </ScrollArea>

          {/* Input */}
          <form onSubmit={gererEnvoi} className="flex gap-2">
            <BoutonVocal
              onResultat={(texte) =>
                setSaisie((prev) => (prev ? `${prev} ${texte}` : texte))
              }
              placeholder="Dicter votre question"
            />
            <Input
              value={saisie}
              onChange={(e) => setSaisie(e.target.value)}
              placeholder="Posez votre question sur la nutrition..."
              disabled={isPending}
            />
            <Button
              type="submit"
              disabled={isPending || !saisie.trim()}
              size="icon"
              aria-label="Envoyer"
            >
              {isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
