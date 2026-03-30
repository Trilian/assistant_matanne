// ═══════════════════════════════════════════════════════════
// Page Admin — Notifications
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Bell, Send, Loader2, CheckCircle2, XCircle } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Badge } from "@/composants/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { Alert, AlertDescription, AlertTitle } from "@/composants/ui/alert";
import {
  envoyerNotificationTest,
  envoyerNotificationTestTousCanaux,
} from "@/bibliotheque/api/admin";
import { format } from "date-fns";
import { fr } from "date-fns/locale";

type Canal = "ntfy" | "push" | "email" | "whatsapp";

interface HistoriqueNotif {
  canal: string;
  message: string;
  envoyeA: string;
  statut: "succes" | "erreur";
}

export default function PageAdminNotifications() {
  const [canal, setCanal] = useState<Canal>("ntfy");
  const [message, setMessage] = useState("");
  const [titre, setTitre] = useState("Test Matanne");
  const [email, setEmail] = useState("");
  const [envoyant, setEnvoyant] = useState(false);
  const [resultat, setResultat] = useState<{ ok: boolean; message: string } | null>(null);
  const [envoyantTous, setEnvoyantTous] = useState(false);
  const [resultatTous, setResultatTous] = useState<{ ok: boolean; message: string; details?: string } | null>(null);
  const [historique, setHistorique] = useState<HistoriqueNotif[]>([]);

  const envoyerTest = async () => {
    if (!message.trim()) {
      setResultat({ ok: false, message: "Le message ne peut pas être vide." });
      return;
    }

    setEnvoyant(true);
    setResultat(null);

    const body: Record<string, string> = { canal, message, titre };
    if (canal === "email" && email) body.email = email;

    try {
      const data = await envoyerNotificationTest(body as { canal: Canal; message: string; titre: string; email?: string });
      const msg = data.message ?? "Notification envoyée avec succès.";
      setResultat({ ok: true, message: msg });
      setHistorique((h) => [
        {
          canal,
          message,
          envoyeA: new Date().toISOString(),
          statut: "succes",
        },
        ...h.slice(0, 19),
      ]);
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Erreur lors de l'envoi.";
      setResultat({ ok: false, message: detail });
      setHistorique((h) => [
        { canal, message, envoyeA: new Date().toISOString(), statut: "erreur" },
        ...h.slice(0, 19),
      ]);
    } finally {
      setEnvoyant(false);
    }
  };

  const envoyerTousLesCanaux = async () => {
    if (!message.trim()) {
      setResultatTous({ ok: false, message: "Le message ne peut pas être vide." });
      return;
    }

    setEnvoyantTous(true);
    setResultatTous(null);

    try {
      const data = await envoyerNotificationTestTousCanaux({
        message,
        titre,
        email: email || undefined,
        inclure_whatsapp: true,
      });
      const details = `Succès: ${data.succes.join(", ") || "aucun"} · Échecs: ${data.echecs.join(", ") || "aucun"}`;
      setResultatTous({ ok: data.echecs.length === 0, message: data.message, details });
      setHistorique((h) => [
        {
          canal: "multi",
          message,
          envoyeA: new Date().toISOString(),
          statut: data.echecs.length === 0 ? "succes" : "erreur",
        },
        ...h.slice(0, 19),
      ]);
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Erreur lors du test multi-canal.";
      setResultatTous({ ok: false, message: detail });
    } finally {
      setEnvoyantTous(false);
    }
  };

  const canalLabel: Record<Canal, string> = {
    ntfy: "ntfy.sh (push natif)",
    push: "Web Push",
    email: "Email",
    whatsapp: "WhatsApp",
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Bell className="h-6 w-6" />
          Test des notifications
        </h1>
        <p className="text-muted-foreground">
          Envoyez des notifications de test pour vérifier les canaux configurés
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* ── Formulaire ───────────────────────────────────────── */}
        <Card>
          <CardHeader>
            <CardTitle>Envoyer un test</CardTitle>
            <CardDescription>
              Sélectionnez le canal et rédigez le message de test.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1">
              <Label htmlFor="canal">Canal</Label>
              <Select value={canal} onValueChange={(v) => setCanal(v as Canal)}>
                <SelectTrigger id="canal">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ntfy">ntfy.sh</SelectItem>
                  <SelectItem value="push">Web Push</SelectItem>
                  <SelectItem value="email">Email</SelectItem>
                  <SelectItem value="whatsapp">WhatsApp</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1">
              <Label htmlFor="titre">Titre</Label>
              <Input
                id="titre"
                value={titre}
                onChange={(e) => setTitre(e.target.value)}
                placeholder="Test Matanne"
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="message">Message</Label>
              <Input
                id="message"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Message de test…"
              />
            </div>

            {canal === "email" && (
              <div className="space-y-1">
                <Label htmlFor="email-dest">Destinataire email</Label>
                <Input
                  id="email-dest"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="email@exemple.fr"
                />
              </div>
            )}

            <Button onClick={envoyerTest} disabled={envoyant} className="w-full">
              {envoyant ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Send className="mr-2 h-4 w-4" />
              )}
              Envoyer sur {canalLabel[canal]}
            </Button>

            <Button variant="outline" onClick={envoyerTousLesCanaux} disabled={envoyantTous} className="w-full">
              {envoyantTous ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Bell className="mr-2 h-4 w-4" />
              )}
              Tester tous les canaux
            </Button>

            {resultat && (
              <div
                className={`flex items-start gap-2 text-sm rounded-md p-3 ${
                  resultat.ok
                    ? "bg-green-50 text-green-700 dark:bg-green-950/30 dark:text-green-400"
                    : "bg-red-50 text-red-700 dark:bg-red-950/30 dark:text-red-400"
                }`}
              >
                {resultat.ok ? (
                  <CheckCircle2 className="h-4 w-4 mt-0.5 shrink-0" />
                ) : (
                  <XCircle className="h-4 w-4 mt-0.5 shrink-0" />
                )}
                <span>{resultat.message}</span>
              </div>
            )}

            {resultatTous && (
              <Alert variant={resultatTous.ok ? "default" : "destructive"}>
                <AlertTitle>Test multi-canal</AlertTitle>
                <AlertDescription>
                  <div>{resultatTous.message}</div>
                  {resultatTous.details && <div className="mt-1 text-xs">{resultatTous.details}</div>}
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* ── Prérequis canaux ─────────────────────────────────── */}
        <Card>
          <CardHeader>
            <CardTitle>Configuration requise</CardTitle>
            <CardDescription>Variables d&apos;environnement nécessaires par canal</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            {[
              { canal: "ntfy.sh", vars: ["NTFY_URL", "NTFY_TOPIC"] },
              { canal: "Web Push", vars: ["VAPID_PUBLIC_KEY", "VAPID_PRIVATE_KEY"] },
              { canal: "Email", vars: ["RESEND_API_KEY", "EMAIL_FROM"] },
              {
                canal: "WhatsApp",
                vars: [
                  "META_WHATSAPP_TOKEN",
                  "META_PHONE_NUMBER_ID",
                  "WHATSAPP_USER_NUMBER",
                ],
              },
            ].map(({ canal: c, vars }) => (
              <div key={c}>
                <p className="font-medium mb-1">{c}</p>
                <div className="flex flex-wrap gap-1">
                  {vars.map((v) => (
                    <code
                      key={v}
                      className="text-xs bg-muted px-1.5 py-0.5 rounded font-mono"
                    >
                      {v}
                    </code>
                  ))}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* ── Historique ─────────────────────────────────────────── */}
      {historique.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Historique de session</CardTitle>
            <CardDescription>
              Notifications de test envoyées durant cette session ({historique.length})
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {historique.map((h, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between text-sm border rounded-md px-3 py-2"
                >
                  <div className="flex items-center gap-3">
                    <Badge variant={h.statut === "succes" ? "default" : "destructive"} className="shrink-0">
                      {h.canal}
                    </Badge>
                    <span className="text-muted-foreground truncate max-w-[300px]">
                      {h.message}
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground shrink-0">
                    {format(new Date(h.envoyeA), "HH:mm:ss", { locale: fr })}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
