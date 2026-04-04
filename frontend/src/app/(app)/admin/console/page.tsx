// ═══════════════════════════════════════════════════════════
// Page Admin — Console Commande Rapide (D1)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Terminal, Send, Loader2, HelpCircle } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Badge } from "@/composants/ui/badge";
import { executerCommandeRapide, type QuickCommandResponse } from "@/bibliotheque/api/admin";

interface HistoryEntry {
  commande: string;
  resultat: QuickCommandResponse;
  timestamp: Date;
}

export default function PageAdminConsole() {
  const [commande, setCommande] = useState("");
  const [chargement, setChargement] = useState(false);
  const [historique, setHistorique] = useState<HistoryEntry[]>([]);
  const [indexHistorique, setIndexHistorique] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [historique]);

  const executer = useCallback(async () => {
    const cmd = commande.trim();
    if (!cmd || chargement) return;

    setChargement(true);
    setCommande("");
    setIndexHistorique(-1);

    try {
      const resultat = await executerCommandeRapide(cmd);
      setHistorique((prev) => [
        ...prev,
        { commande: cmd, resultat, timestamp: new Date() },
      ]);
    } catch (error) {
      setHistorique((prev) => [
        ...prev,
        {
          commande: cmd,
          resultat: {
            status: "error",
            type: "error",
            message: error instanceof Error ? error.message : "Erreur inconnue",
          },
          timestamp: new Date(),
        },
      ]);
    } finally {
      setChargement(false);
      inputRef.current?.focus();
    }
  }, [commande, chargement]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") {
        executer();
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        if (historique.length > 0) {
          const newIndex =
            indexHistorique < historique.length - 1
              ? indexHistorique + 1
              : indexHistorique;
          setIndexHistorique(newIndex);
          setCommande(historique[historique.length - 1 - newIndex].commande);
        }
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        if (indexHistorique > 0) {
          const newIndex = indexHistorique - 1;
          setIndexHistorique(newIndex);
          setCommande(historique[historique.length - 1 - newIndex].commande);
        } else {
          setIndexHistorique(-1);
          setCommande("");
        }
      }
    },
    [executer, historique, indexHistorique]
  );

  const renderResultat = (entry: HistoryEntry) => {
    const { resultat } = entry;
    const isError = resultat.type === "error";

    return (
      <div className="space-y-1">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span className="text-green-500">❯</span>
          <span className="font-mono">{entry.commande}</span>
          <span className="ml-auto text-xs">
            {entry.timestamp.toLocaleTimeString("fr-FR")}
          </span>
        </div>
        <div
          className={`pl-4 text-sm ${
            isError ? "text-red-500" : "text-foreground"
          }`}
        >
          <Badge variant={isError ? "destructive" : "secondary"} className="mb-1">
            {resultat.type}
          </Badge>
          <p className="mt-1">{resultat.message}</p>

          {resultat.type === "help" && resultat.commandes && (
            <div className="mt-2 space-y-1">
              {Object.entries(resultat.commandes).map(([cmd, desc]) => (
                <div key={cmd} className="flex gap-2">
                  <code className="text-blue-500 dark:text-blue-400 shrink-0">
                    {cmd}
                  </code>
                  <span className="text-muted-foreground">— {desc}</span>
                </div>
              ))}
            </div>
          )}

          {resultat.type === "list_jobs" && resultat.jobs && (
            <div className="mt-2 grid grid-cols-2 md:grid-cols-3 gap-1 text-xs">
              {resultat.jobs.map((job) => (
                <code key={job} className="bg-muted px-1 py-0.5 rounded">
                  {job}
                </code>
              ))}
            </div>
          )}

          {resultat.type === "job_result" && resultat.result && (
            <pre className="mt-2 bg-muted p-2 rounded text-xs overflow-x-auto">
              {JSON.stringify(resultat.result, null, 2)}
            </pre>
          )}

          {resultat.type === "health" && resultat.result && (
            <pre className="mt-2 bg-muted p-2 rounded text-xs overflow-x-auto">
              {JSON.stringify(resultat.result, null, 2)}
            </pre>
          )}

          {resultat.type === "cache_stats" && resultat.result && (
            <pre className="mt-2 bg-muted p-2 rounded text-xs overflow-x-auto">
              {JSON.stringify(resultat.result, null, 2)}
            </pre>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <Terminal className="h-5 w-5" />
            Console Admin
          </CardTitle>
          <CardDescription>
            Exécutez des commandes rapides. Tapez <code>help</code> pour la
            liste des commandes.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Terminal output */}
          <div
            ref={scrollRef}
            className="bg-muted/50 border rounded-lg p-4 h-[500px] overflow-y-auto space-y-3 font-mono text-sm mb-4"
          >
            {historique.length === 0 && (
              <div className="text-muted-foreground flex items-center gap-2">
                <HelpCircle className="h-4 w-4" />
                Bienvenue dans la console admin. Tapez{" "}
                <code className="bg-muted px-1 rounded">help</code> pour
                commencer.
              </div>
            )}
            {historique.map((entry, i) => (
              <div key={i}>{renderResultat(entry)}</div>
            ))}
            {chargement && (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="h-3 w-3 animate-spin" />
                Exécution en cours...
              </div>
            )}
          </div>

          {/* Input */}
          <div className="flex gap-2">
            <div className="relative flex-1">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-green-500 font-mono">
                ❯
              </span>
              <Input
                ref={inputRef}
                value={commande}
                onChange={(e) => setCommande(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="run job rappels_famille"
                className="pl-8 font-mono"
                disabled={chargement}
              />
            </div>
            <Button onClick={executer} disabled={!commande.trim() || chargement}>
              {chargement ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* Quick actions */}
          <div className="flex flex-wrap gap-2 mt-3">
            {["help", "list jobs", "health", "stats cache"].map((cmd) => (
              <Button
                key={cmd}
                variant="outline"
                size="sm"
                onClick={() => {
                  setCommande(cmd);
                  setTimeout(() => executer(), 0);
                }}
                disabled={chargement}
              >
                {cmd}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
