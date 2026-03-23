// ═══════════════════════════════════════════════════════════
// Album — Galerie photos famille
// ═══════════════════════════════════════════════════════════

"use client";

import { Camera, Upload, Image as ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";

export default function PageAlbum() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">📸 Album</h1>
          <p className="text-muted-foreground">Galerie photos familiale</p>
        </div>
        <Button disabled>
          <Upload className="mr-1 h-4 w-4" />
          Ajouter des photos
        </Button>
      </div>

      <Card>
        <CardContent className="flex flex-col items-center gap-4 py-16">
          <Camera className="h-16 w-16 text-muted-foreground" />
          <div className="text-center">
            <p className="text-lg font-medium">Album en préparation</p>
            <p className="text-sm text-muted-foreground mt-1">
              L&apos;upload de photos via Supabase Storage sera disponible
              prochainement.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Placeholder catégories */}
      <div className="grid gap-3 sm:grid-cols-3">
        {[
          { label: "Jules", count: 0, emoji: "👶" },
          { label: "Vacances", count: 0, emoji: "🏖️" },
          { label: "Événements", count: 0, emoji: "🎉" },
        ].map(({ label, count, emoji }) => (
          <Card key={label} className="opacity-60">
            <CardHeader>
              <div className="flex items-center gap-2">
                <span className="text-xl">{emoji}</span>
                <div>
                  <CardTitle className="text-base">{label}</CardTitle>
                  <CardDescription>{count} photos</CardDescription>
                </div>
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>
    </div>
  );
}
