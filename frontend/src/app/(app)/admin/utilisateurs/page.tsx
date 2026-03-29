// ═══════════════════════════════════════════════════════════
// Page Admin — Utilisateurs
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  Users,
  RefreshCw,
  Ban,
  Loader2,
  CheckCircle2,
  XCircle,
  Shield,
  UserRound,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/composants/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/composants/ui/dialog";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { clientApi } from "@/bibliotheque/api/client";
import { format } from "date-fns";
import { fr } from "date-fns/locale";

interface UtilisateurAdmin {
  id: string;
  email: string;
  nom: string | null;
  role: string;
  actif: boolean;
  cree_le: string | null;
}

export default function PageAdminUtilisateurs() {
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [cibleUserId, setCibleUserId] = useState<string | null>(null);
  const [raison, setRaison] = useState("");
  const [desactivant, setDesactivant] = useState(false);
  const [resultat, setResultat] = useState<{ ok: boolean; message: string } | null>(null);

  const {
    data: utilisateurs,
    isLoading,
    refetch,
  } = utiliserRequete(["admin", "users"], async (): Promise<UtilisateurAdmin[]> => {
    const { data } = await clientApi.get("/admin/users?par_page=100");
    return data;
  });

  const ouvrirDialogDesactivation = (userId: string) => {
    setCibleUserId(userId);
    setRaison("");
    setResultat(null);
    setDialogOuvert(true);
  };

  const confirmerDesactivation = async () => {
    if (!cibleUserId) return;
    setDesactivant(true);
    setResultat(null);
    try {
      const { data } = await clientApi.post(`/admin/users/${cibleUserId}/disable`, {
        raison: raison || null,
      });
      setResultat({ ok: true, message: data.message ?? "Compte désactivé." });
      refetch();
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Erreur lors de la désactivation.";
      setResultat({ ok: false, message: detail });
    } finally {
      setDesactivant(false);
    }
  };

  const utilisateurCible = utilisateurs?.find((u) => u.id === cibleUserId);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Users className="h-6 w-6" />
            Gestion des utilisateurs
          </h1>
          <p className="text-muted-foreground">
            Liste des comptes et actions de modération
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => refetch()} aria-label="Actualiser">
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      {/* Résumé */}
      {utilisateurs && (
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total comptes</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold">{utilisateurs.length}</span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Actifs</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold text-green-600">
                {utilisateurs.filter((u) => u.actif).length}
              </span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Admins</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold">
                {utilisateurs.filter((u) => u.role === "admin").length}
              </span>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tableau */}
      <Card>
        <CardHeader>
          <CardTitle>Comptes utilisateurs</CardTitle>
          <CardDescription>
            {isLoading
              ? "Chargement…"
              : utilisateurs
              ? `${utilisateurs.length} compte(s) enregistré(s)`
              : "—"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="mr-2 h-5 w-5 animate-spin" /> Chargement…
            </div>
          ) : !utilisateurs || utilisateurs.length === 0 ? (
            <p className="text-center py-8 text-muted-foreground text-sm">
              Aucun utilisateur trouvé.
            </p>
          ) : (
            <div className="overflow-x-auto rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID / Username</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Nom</TableHead>
                    <TableHead>Rôle</TableHead>
                    <TableHead>Statut</TableHead>
                    <TableHead>Créé le</TableHead>
                    <TableHead className="text-right">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {utilisateurs.map((u) => (
                    <TableRow key={u.id} className={!u.actif ? "opacity-60" : undefined}>
                      <TableCell className="font-mono text-xs">{u.id}</TableCell>
                      <TableCell className="text-sm">{u.email || "—"}</TableCell>
                      <TableCell className="text-sm">{u.nom ?? "—"}</TableCell>
                      <TableCell>
                        <Badge variant={u.role === "admin" ? "default" : "secondary"}>
                          {u.role === "admin" ? (
                            <Shield className="mr-1 h-3 w-3" />
                          ) : (
                            <UserRound className="mr-1 h-3 w-3" />
                          )}
                          {u.role}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant={u.actif ? "default" : "outline"}>
                          {u.actif ? (
                            <><CheckCircle2 className="mr-1 h-3 w-3" />Actif</>
                          ) : (
                            <><XCircle className="mr-1 h-3 w-3" />Inactif</>
                          )}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {u.cree_le
                          ? format(new Date(u.cree_le), "dd/MM/yyyy", { locale: fr })
                          : "—"}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-destructive hover:text-destructive"
                          disabled={!u.actif}
                          onClick={() => ouvrirDialogDesactivation(u.id)}
                          aria-label={`Désactiver ${u.nom ?? u.id}`}
                          title={u.actif ? "Désactiver ce compte" : "Compte déjà inactif"}
                        >
                          <Ban className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog confirmation désactivation */}
      <Dialog open={dialogOuvert} onOpenChange={setDialogOuvert}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Désactiver le compte</DialogTitle>
            <DialogDescription>
              Vous allez désactiver le compte de{" "}
              <strong>{utilisateurCible?.nom ?? utilisateurCible?.id}</strong>. Cette action
              est réversible par un admin.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-3 py-2">
            <div className="space-y-1">
              <Label htmlFor="raison-desact">Raison (optionnel)</Label>
              <Input
                id="raison-desact"
                value={raison}
                onChange={(e) => setRaison(e.target.value)}
                placeholder="Ex : Compte compromis, inactivité…"
              />
            </div>

            {resultat && (
              <p
                className={`text-sm ${
                  resultat.ok ? "text-green-600" : "text-destructive"
                }`}
              >
                {resultat.ok ? "✅" : "❌"} {resultat.message}
              </p>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOuvert(false)}>
              Annuler
            </Button>
            <Button
              variant="destructive"
              onClick={confirmerDesactivation}
              disabled={desactivant || resultat?.ok === true}
            >
              {desactivant && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Désactiver
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
