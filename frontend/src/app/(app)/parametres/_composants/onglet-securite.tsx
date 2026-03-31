"use client";

import { useState } from "react";
import { Copy, Download, ShieldCheck } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Label } from "@/composants/ui/label";
import { Input } from "@/composants/ui/input";
import { Button } from "@/composants/ui/button";
import { utiliserInvalidation, utiliserRequete } from "@/crochets/utiliser-api";
import { toast } from "sonner";

export function OngletSecurite() {
  const [etape, setEtape] = useState<"idle" | "setup" | "confirm" | "disable">("idle");
  const [qrCode, setQrCode] = useState("");
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [code, setCode] = useState("");
  const [erreur, setErreur] = useState("");

  const { data: statut, isLoading } = utiliserRequete(
    ["2fa", "status"],
    async () => {
      const { statut2FA } = await import("@/bibliotheque/api/auth");
      return statut2FA();
    }
  );
  const invalider = utiliserInvalidation();

  const initier2FA = async () => {
    setErreur("");
    try {
      const { activer2FA } = await import("@/bibliotheque/api/auth");
      const data = await activer2FA();
      setQrCode(data.qr_code);
      setBackupCodes(data.backup_codes);
      setEtape("setup");
    } catch {
      setErreur("Erreur lors de l'initialisation 2FA");
    }
  };

  const confirmer2FA = async () => {
    setErreur("");
    try {
      const { verifierSetup2FA } = await import("@/bibliotheque/api/auth");
      await verifierSetup2FA(code);
      setEtape("idle");
      setCode("");
      invalider(["2fa", "status"]);
      toast.success("2FA activé avec succès");
    } catch {
      setErreur("Code invalide. Vérifiez votre application.");
    }
  };

  const desactiver = async () => {
    setErreur("");
    try {
      const { desactiver2FA } = await import("@/bibliotheque/api/auth");
      await desactiver2FA(code);
      setEtape("idle");
      setCode("");
      invalider(["2fa", "status"]);
      toast.success("2FA désactivé");
    } catch {
      setErreur("Code invalide");
    }
  };

  const telechargerBackupCodes = () => {
    const contenu = [
      "Assistant Matanne — Codes de récupération 2FA",
      "Conservez ces codes en lieu sûr. Chaque code est à usage unique.",
      "",
      ...backupCodes.map((c, i) => `${i + 1}. ${c}`),
    ].join("\n");
    const blob = new Blob([contenu], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "matanne-2fa-backup-codes.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-muted-foreground">Chargement…</CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5" />
          Authentification à deux facteurs (2FA)
        </CardTitle>
        <CardDescription>
          Sécurisez votre compte avec une application d&apos;authentification
          (Google Authenticator, Authy, etc.)
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6 max-w-lg">
        {erreur && (
          <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
            {erreur}
          </div>
        )}

        {statut?.enabled && etape === "idle" && (
          <div className="space-y-4">
            <div className="flex items-center gap-3 rounded-lg border bg-green-50 dark:bg-green-950/20 p-4">
              <ShieldCheck className="h-5 w-5 text-green-600" />
              <div>
                <p className="font-medium text-green-800 dark:text-green-400">2FA activé</p>
                <p className="text-xs text-muted-foreground">
                  {statut.backup_codes_remaining} codes de récupération restants
                </p>
              </div>
            </div>
            <Button
              variant="destructive"
              size="sm"
              onClick={() => setEtape("disable")}
            >
              Désactiver le 2FA
            </Button>
          </div>
        )}

        {!statut?.enabled && etape === "idle" && (
          <div className="space-y-4">
            <div className="rounded-lg border bg-muted/50 p-4">
              <p className="text-sm">
                Le 2FA ajoute une couche de sécurité supplémentaire.
                Après l&apos;activation, un code à 6 chiffres sera demandé à chaque connexion.
              </p>
            </div>
            <Button onClick={initier2FA}>
              <ShieldCheck className="mr-2 h-4 w-4" />
              Activer le 2FA
            </Button>
          </div>
        )}

        {etape === "setup" && (
          <div className="space-y-6">
            <div className="space-y-3">
              <Label>1. Scannez ce QR code</Label>
              <p className="text-xs text-muted-foreground">
                Ouvrez Google Authenticator ou Authy et scannez le QR code ci-dessous.
              </p>
              {qrCode && (
                <div className="flex justify-center rounded-lg border bg-white p-4">
                  <img src={qrCode} alt="QR code 2FA" className="h-48 w-48" />
                </div>
              )}
            </div>

            <div className="space-y-3">
              <Label>2. Sauvegardez vos codes de récupération</Label>
              <p className="text-xs text-muted-foreground">
                Ces codes sont utilisables une seule fois si vous perdez votre téléphone.
              </p>
              <div className="grid grid-cols-2 gap-1 rounded-lg border bg-muted/50 p-3 font-mono text-sm">
                {backupCodes.map((c) => (
                  <span key={c} className="px-2 py-1">{c}</span>
                ))}
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={telechargerBackupCodes}>
                  <Download className="mr-2 h-3.5 w-3.5" />
                  Télécharger
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    navigator.clipboard.writeText(backupCodes.join("\n"));
                    toast.success("Codes copiés");
                  }}
                >
                  <Copy className="mr-2 h-3.5 w-3.5" />
                  Copier
                </Button>
              </div>
            </div>

            <div className="space-y-3">
              <Label htmlFor="code-verification">3. Entrez un code pour confirmer</Label>
              <Input
                id="code-verification"
                type="text"
                inputMode="numeric"
                placeholder="000000"
                maxLength={6}
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
                className="max-w-[200px] text-center text-lg tracking-widest"
              />
            </div>

            <div className="flex gap-2">
              <Button onClick={confirmer2FA} disabled={code.length < 6}>
                Activer le 2FA
              </Button>
              <Button variant="ghost" onClick={() => { setEtape("idle"); setCode(""); }}>
                Annuler
              </Button>
            </div>
          </div>
        )}

        {etape === "disable" && (
          <div className="space-y-4">
            <Label htmlFor="code-disable">Entrez un code TOTP pour confirmer la désactivation</Label>
            <Input
              id="code-disable"
              type="text"
              inputMode="numeric"
              placeholder="000000"
              maxLength={6}
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
              className="max-w-[200px] text-center text-lg tracking-widest"
            />
            <div className="flex gap-2">
              <Button variant="destructive" onClick={desactiver} disabled={code.length < 6}>
                Confirmer la désactivation
              </Button>
              <Button variant="ghost" onClick={() => { setEtape("idle"); setCode(""); }}>
                Annuler
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
