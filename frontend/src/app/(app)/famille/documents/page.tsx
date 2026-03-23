// ═══════════════════════════════════════════════════════════
// Documents — Fichiers et documents familiaux
// ═══════════════════════════════════════════════════════════

"use client";

import { FileText, Upload, FolderOpen, Shield, Heart, Home } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const DOSSIERS = [
  {
    nom: "Administratif",
    description: "Papiers d'identité, attestations",
    icone: Shield,
    count: 0,
  },
  {
    nom: "Santé",
    description: "Carnets de santé, ordonnances",
    icone: Heart,
    count: 0,
  },
  {
    nom: "Maison",
    description: "Bail, assurance, factures",
    icone: Home,
    count: 0,
  },
];

export default function PageDocuments() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">📄 Documents</h1>
        <p className="text-muted-foreground">
          Stockage et gestion des documents familiaux
        </p>
      </div>

      {/* Upload placeholder */}
      <Card className="border-dashed">
        <CardContent className="flex flex-col items-center gap-3 py-10 text-center">
          <Upload className="h-10 w-10 text-muted-foreground/50" />
          <div>
            <p className="font-medium">Glisser-déposer vos documents</p>
            <p className="text-sm text-muted-foreground">
              Intégration Supabase Storage à venir
            </p>
          </div>
          <Button variant="outline" disabled>
            <FileText className="mr-2 h-4 w-4" />
            Parcourir
          </Button>
        </CardContent>
      </Card>

      {/* Dossiers */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Dossiers</h2>
        <div className="grid gap-3 sm:grid-cols-3">
          {DOSSIERS.map((d) => {
            const Icone = d.icone;
            return (
              <Card key={d.nom} className="hover:bg-accent/50 transition-colors">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <FolderOpen className="h-4 w-4 text-primary" />
                    {d.nom}
                  </CardTitle>
                  <CardDescription className="text-xs">
                    {d.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Icone className="h-3.5 w-3.5" />
                    {d.count} document{d.count !== 1 ? "s" : ""}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
