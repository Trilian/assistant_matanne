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
  UtensilsCrossed,
  Users,
  Home,
  Wallet,
  Bot,
  Send,
  Sparkles,
  Loader2,
} from "lucide-react";
import { utiliserMutation } from "@/crochets/utiliser-api";
import {
  envoyerMessageChat,
  obtenirActionsRapides,
} from "@/bibliotheque/api/outils";
import type {
  ContexteChat,
  ActionRapide,
} from "@/bibliotheque/api/outils";
import type { MessageChat } from "@/types/outils";
import { toast } from "sonner";
import { utiliserRequete } from "@/crochets/utiliser-api";

const CONTEXTES: { id: ContexteChat; label: string; icon: typeof Bot; color: string }[] = [
  { id: "general", label: "Général", icon: Bot, color: "bg-primary/10 text-primary" },
  { id: "cuisine", label: "Cuisine", icon: UtensilsCrossed, color: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300" },
  { id: "famille", label: "Famille", icon: Users, color: "bg-pink-100 text-pink-700 dark:bg-pink-900 dark:text-pink-300" },
  { id: "maison", label: "Maison", icon: Home, color: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300" },
  { id: "budget", label: "Budget", icon: Wallet, color: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300" },
];

export default function ChatIAPage() {
  const [messages, setMessages] = useState<MessageChat[]>([]);
  const [saisie, setSaisie] = useState("");
  const [contexte, setContexte] = useState<ContexteChat>("general");
  const refScroll = useRef<HTMLDivElement>(null);

  const { data: actionsData } = utiliserRequete(
    ["chat-ia", "actions", contexte],
    () => obtenirActionsRapides(contexte)
  );
  const actions: ActionRapide[] = actionsData?.actions ?? [];

  const { mutate: envoyer, isPending } = utiliserMutation(
    async (question: string) => {
      const historique = messages.map((m) => ({
        role: m.role,
        contenu: m.contenu,
      }));
      return envoyerMessageChat({
        message: question,
        contexte,
        historique,
      });
    },
    {
      onSuccess: (data) => {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            contenu: data.reponse,
            horodatage: new Date().toISOString(),
          },
        ]);
      },
      onError: () => toast.error("Erreur lors de l'envoi"),
    }
  );

  useEffect(() => {
    refScroll.current?.scrollTo({
      top: refScroll.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  function gererEnvoi(e: React.FormEvent) {
    e.preventDefault();
    const texte = saisie.trim();
    if (!texte || isPending) return;

    setMessages((prev) => [
      ...prev,
      { role: "user", contenu: texte, horodatage: new Date().toISOString() },
    ]);
    setSaisie("");
    envoyer(texte);
  }

  function gererActionRapide(msg: string) {
    setMessages((prev) => [
      ...prev,
      { role: "user", contenu: msg, horodatage: new Date().toISOString() },
    ]);
    envoyer(msg);
  }

  function changerContexte(ctx: ContexteChat) {
    setContexte(ctx);
    setMessages([]);
  }

  const contexteActif = CONTEXTES.find((c) => c.id === contexte) ?? CONTEXTES[0];

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)]">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Bot className="h-6 w-6" />
            Chat IA
            <Sparkles className="h-5 w-5 text-yellow-500" />
          </h1>
          <p className="text-sm text-muted-foreground">
            Assistant multi-contexte pour toute la famille
          </p>
        </div>
      </div>

      {/* Sélecteur de contexte */}
      <div className="flex gap-2 mb-4 flex-wrap">
        {CONTEXTES.map((ctx) => {
          const Icon = ctx.icon;
          return (
            <Button
              key={ctx.id}
              variant={contexte === ctx.id ? "default" : "outline"}
              size="sm"
              onClick={() => changerContexte(ctx.id)}
              className="gap-1.5"
            >
              <Icon className="h-4 w-4" />
              {ctx.label}
            </Button>
          );
        })}
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden">
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <Badge className={contexteActif.color}>
              {contexteActif.label}
            </Badge>
            Conversation
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col overflow-hidden p-0">
          <ScrollArea ref={refScroll} className="flex-1 px-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full py-12 gap-4">
                <Bot className="h-12 w-12 text-muted-foreground/50" />
                <p className="text-muted-foreground text-center text-sm">
                  Posez une question ou choisissez une action rapide
                </p>
                {/* Actions rapides */}
                {actions.length > 0 && (
                  <div className="flex flex-wrap gap-2 justify-center max-w-md">
                    {actions.map((a, i) => (
                      <Button
                        key={i}
                        variant="outline"
                        size="sm"
                        className="text-xs"
                        onClick={() => gererActionRapide(a.message)}
                        disabled={isPending}
                      >
                        {a.label}
                      </Button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div
                className="space-y-4 py-4"
                role="log"
                aria-live="polite"
                aria-label="Messages du chat"
              >
                {messages.map((m, i) => (
                  <div
                    key={i}
                    className={`flex ${
                      m.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-xl px-4 py-2.5 whitespace-pre-wrap text-sm ${
                        m.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted"
                      }`}
                    >
                      {m.contenu}
                    </div>
                  </div>
                ))}
                {isPending && (
                  <div className="flex justify-start">
                    <div className="bg-muted rounded-xl px-4 py-2.5 flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span className="text-sm text-muted-foreground">
                        Réflexion en cours…
                      </span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </ScrollArea>

          {/* Actions rapides visibles quand il y a déjà des messages */}
          {messages.length > 0 && actions.length > 0 && (
            <div className="flex gap-1.5 px-4 py-2 overflow-x-auto border-t">
              {actions.map((a, i) => (
                <Button
                  key={i}
                  variant="ghost"
                  size="sm"
                  className="text-xs shrink-0 h-7"
                  onClick={() => gererActionRapide(a.message)}
                  disabled={isPending}
                >
                  {a.label}
                </Button>
              ))}
            </div>
          )}

          <form onSubmit={gererEnvoi} className="flex gap-2 p-4 border-t">
            <Input
              value={saisie}
              onChange={(e) => setSaisie(e.target.value)}
              placeholder={`Posez votre question (${contexteActif.label})…`}
              disabled={isPending}
            />
            <Button type="submit" disabled={isPending || !saisie.trim()} size="icon" aria-label="Envoyer le message">
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
