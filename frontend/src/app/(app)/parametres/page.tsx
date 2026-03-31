"use client";

import { Bell, Bot, Database, Palette, ShieldCheck, User, UtensilsCrossed } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { utiliserAuth } from "@/crochets/utiliser-auth";
import { OngletProfil } from "./_composants/onglet-profil";
import { OngletCuisine } from "./_composants/onglet-cuisine";
import { OngletNotifications } from "./_composants/onglet-notifications";
import { OngletAffichage } from "./_composants/onglet-affichage";
import { OngletIA } from "./_composants/onglet-ia";
import { OngletDonnees } from "./_composants/onglet-donnees";
import { OngletSecurite } from "./_composants/onglet-securite";

export default function PageParametres() {
  const { utilisateur } = utiliserAuth();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">⚙️ Paramètres</h1>
        <p className="text-muted-foreground">Configuration de l&apos;application</p>
      </div>

      <Tabs defaultValue="profil">
        <TabsList>
          <TabsTrigger value="profil" className="flex items-center gap-1">
            <User className="h-4 w-4" />
            Profil
          </TabsTrigger>
          <TabsTrigger value="cuisine" className="flex items-center gap-1">
            <UtensilsCrossed className="h-4 w-4" />
            Cuisine
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-1">
            <Bell className="h-4 w-4" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="affichage" className="flex items-center gap-1">
            <Palette className="h-4 w-4" />
            Affichage
          </TabsTrigger>
          <TabsTrigger value="ia" className="flex items-center gap-1">
            <Bot className="h-4 w-4" />
            IA
          </TabsTrigger>
          <TabsTrigger value="donnees" className="flex items-center gap-1">
            <Database className="h-4 w-4" />
            Données
          </TabsTrigger>
          <TabsTrigger value="securite" className="flex items-center gap-1">
            <ShieldCheck className="h-4 w-4" />
            Sécurité
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profil">
          <OngletProfil utilisateur={utilisateur} />
        </TabsContent>

        <TabsContent value="cuisine">
          <OngletCuisine />
        </TabsContent>

        <TabsContent value="notifications">
          <OngletNotifications />
        </TabsContent>

        <TabsContent value="affichage">
          <OngletAffichage />
        </TabsContent>

        <TabsContent value="ia">
          <OngletIA />
        </TabsContent>

        <TabsContent value="donnees">
          <OngletDonnees />
        </TabsContent>

        <TabsContent value="securite">
          <OngletSecurite />
        </TabsContent>
      </Tabs>
    </div>
  );
}
