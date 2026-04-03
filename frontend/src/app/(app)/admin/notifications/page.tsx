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
  listerHistoriqueNotifications,
  listerQueueNotifications,
  listerTemplatesNotifications,
  previsualiserTemplateNotification,
  relancerQueueNotifications,
  simulerNotificationAdmin,
  supprimerQueueNotifications,
} from "@/bibliotheque/api/admin";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { format } from "date-fns";
import { fr } from "date-fns/locale";

type Canal = "ntfy" | "push" | "email" | "telegram";

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
  const [actionQueueUser, setActionQueueUser] = useState<string | null>(null);
  const [templateCanal, setTemplateCanal] = useState<"telegram" | "email">("telegram");
  const [templateId, setTemplateId] = useState("");
  const [preview, setPreview] = useState("");
  const [simulationRetour, setSimulationRetour] = useState("");

  const { data: queueData, refetch: rafraichirQueue } = utiliserRequete(
    ["admin", "notifications", "queue"],
    () => listerQueueNotifications({ limit: 30 })
  );
  const { data: templatesData } = utiliserRequete(
    ["admin", "notifications", "templates"],
    () => listerTemplatesNotifications()
  );
  const { data: historiqueAdmin, refetch: rafraichirHistoriqueAdmin } = utiliserRequete(
    ["admin", "notifications", "history"],
    () => listerHistoriqueNotifications(30)
  );

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
        inclure_telegram: true,
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
    telegram: "Telegram",
  };

  const templatesActifs = templatesData?.templates?.[templateCanal] ?? [];

  const chargerPreview = async () => {
    if (!templateId) return;
    const data = await previsualiserTemplateNotification(templateCanal, templateId);
    setPreview(data.preview);
  };

  const simulerTemplate = async () => {
    if (!templateId) return;
    const data = await simulerNotificationAdmin({
      canal: templateCanal,
      template_id: templateId,
      dry_run: true,
    });
    setSimulationRetour(data.message ?? "Simulation effectuée.");
    await rafraichirHistoriqueAdmin();
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
                  <SelectItem value="telegram">Telegram</SelectItem>
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
                canal: "Telegram",
                vars: [
                  "TELEGRAM_BOT_TOKEN",
                  "TELEGRAM_CHAT_ID",
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

        <Card>
          <CardHeader>
            <CardTitle>Templates notifications</CardTitle>
            <CardDescription>
              Templates WhatsApp et Email actuellement disponibles côté backend.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <p className="text-sm font-medium">Telegram</p>
              <div className="space-y-1">
                {(templatesData?.templates?.telegram ?? []).map((t) => (
                  <div key={t.id} className="text-sm flex items-center justify-between gap-2 rounded border p-2">
                    <span>{t.label}</span>
                    <Badge variant="outline">{t.trigger}</Badge>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <p className="text-sm font-medium">Email</p>
              <div className="space-y-1">
                {(templatesData?.templates?.email ?? []).map((t) => (
                  <div key={t.id} className="text-sm flex items-center justify-between gap-2 rounded border p-2">
                    <span>{t.label}</span>
                    <Badge variant="outline">{t.trigger}</Badge>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-3 rounded-md border p-3">
              <p className="text-sm font-medium">Prévisualisation / simulation</p>
              <div className="grid gap-2 md:grid-cols-3">
                <Select value={templateCanal} onValueChange={(value) => {
                  setTemplateCanal(value as "telegram" | "email");
                  setTemplateId("");
                  setPreview("");
                }}>
                  <SelectTrigger>
                    <SelectValue placeholder="Canal template" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="telegram">Telegram</SelectItem>
                    <SelectItem value="email">Email</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={templateId} onValueChange={setTemplateId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Template" />
                  </SelectTrigger>
                  <SelectContent>
                    {templatesActifs.map((t) => (
                      <SelectItem key={t.id} value={t.id}>{t.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <div className="flex gap-2">
                  <Button type="button" variant="outline" onClick={() => void chargerPreview()} disabled={!templateId}>
                    Preview
                  </Button>
                  <Button type="button" variant="outline" onClick={() => void simulerTemplate()} disabled={!templateId}>
                    Dry-run
                  </Button>
                </div>
              </div>
              {preview && <pre className="rounded bg-muted p-3 text-xs whitespace-pre-wrap">{preview}</pre>}
              {simulationRetour && <p className="text-xs text-muted-foreground">{simulationRetour}</p>}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>File d&apos;attente digest</CardTitle>
            <CardDescription>
              Utilisateurs avec notifications consolidées en attente
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>{queueData?.total_users_pending ?? 0} utilisateur(s) en attente</span>
              <Button variant="outline" size="sm" onClick={() => rafraichirQueue()}>
                Rafraîchir
              </Button>
            </div>

            {!queueData?.items?.length ? (
              <p className="text-sm text-muted-foreground">Aucune file en attente.</p>
            ) : (
              <div className="space-y-2">
                {queueData.items.map((item) => (
                  <div key={item.user_id} className="rounded-md border p-3 space-y-2">
                    <div className="flex items-center justify-between gap-2">
                      <div>
                        <p className="font-mono text-xs">{item.user_id}</p>
                        <p className="text-xs text-muted-foreground">
                          {item.taille_queue} message(s) en file
                        </p>
                      </div>
                      <Badge variant="secondary">Digest</Badge>
                    </div>
                    {item.dernier_message && (
                      <p className="text-xs text-muted-foreground truncate">{item.dernier_message}</p>
                    )}
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={actionQueueUser !== null}
                        onClick={async () => {
                          setActionQueueUser(item.user_id + ":retry");
                          try {
                            await relancerQueueNotifications(item.user_id);
                            await rafraichirQueue();
                          } finally {
                            setActionQueueUser(null);
                          }
                        }}
                      >
                        {actionQueueUser === item.user_id + ":retry" ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          "Retry"
                        )}
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        disabled={actionQueueUser !== null}
                        onClick={async () => {
                          setActionQueueUser(item.user_id + ":delete");
                          try {
                            await supprimerQueueNotifications(item.user_id);
                            await rafraichirQueue();
                          } finally {
                            setActionQueueUser(null);
                          }
                        }}
                      >
                        {actionQueueUser === item.user_id + ":delete" ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          "Delete"
                        )}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
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

      <Card>
        <CardHeader>
          <CardTitle>Historique admin notifications</CardTitle>
          <CardDescription>Dernières actions notifications journalisées côté backend.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {(historiqueAdmin?.items ?? []).map((item) => (
              <div key={item.id} className="rounded-md border px-3 py-2 text-sm">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium">{item.action}</span>
                  <span className="text-xs text-muted-foreground">
                    {item.created_at ? format(new Date(item.created_at), "dd/MM HH:mm:ss", { locale: fr }) : "-"}
                  </span>
                </div>
                <pre className="mt-2 whitespace-pre-wrap text-xs text-muted-foreground">{JSON.stringify(item.details, null, 2)}</pre>
              </div>
            ))}
            {!(historiqueAdmin?.items?.length) && (
              <p className="text-sm text-muted-foreground">Aucun historique backend disponible.</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
