// ═══════════════════════════════════════════════════════════
// Contacts — Répertoire familial
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Users, Phone, Mail, Search, MapPin } from "lucide-react";
import {
  Card,
  CardContent,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

interface Contact {
  nom: string;
  telephone?: string;
  email?: string;
  ville?: string;
  categorie: string;
}

// Données statiques de démarrage — à connecter au backend plus tard
const CONTACTS: Contact[] = [
  {
    nom: "Pédiatre — Dr Martin",
    telephone: "01 23 45 67 89",
    categorie: "Santé",
  },
  {
    nom: "Crèche Les Petits Loups",
    telephone: "01 98 76 54 32",
    email: "creche@example.com",
    ville: "Paris",
    categorie: "Garde",
  },
  {
    nom: "Mamie Françoise",
    telephone: "06 12 34 56 78",
    ville: "Lyon",
    categorie: "Famille",
  },
];

const CATEGORIES = ["Tous", "Famille", "Santé", "Garde", "Amis", "Pro"];

export default function PageContacts() {
  const [recherche, setRecherche] = useState("");
  const [categorie, setCategorie] = useState("Tous");

  const contactsFiltres = CONTACTS.filter((c) => {
    const matchRecherche =
      !recherche || c.nom.toLowerCase().includes(recherche.toLowerCase());
    const matchCategorie =
      categorie === "Tous" || c.categorie === categorie;
    return matchRecherche && matchCategorie;
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">📇 Contacts</h1>
        <p className="text-muted-foreground">
          Répertoire familial et contacts utiles
        </p>
      </div>

      {/* Filtres */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Rechercher un contact..."
            value={recherche}
            onChange={(e) => setRecherche(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((cat) => (
            <Badge
              key={cat}
              variant={categorie === cat ? "default" : "outline"}
              className="cursor-pointer"
              onClick={() => setCategorie(cat)}
            >
              {cat}
            </Badge>
          ))}
        </div>
      </div>

      {/* Liste */}
      <div className="space-y-3">
        {contactsFiltres.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              <Users className="h-8 w-8 mx-auto mb-2 opacity-50" />
              Aucun contact trouvé
            </CardContent>
          </Card>
        ) : (
          contactsFiltres.map((contact) => (
            <Card key={contact.nom}>
              <CardContent className="flex items-start justify-between py-4">
                <div className="space-y-1">
                  <p className="font-medium">{contact.nom}</p>
                  <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
                    {contact.telephone && (
                      <span className="flex items-center gap-1">
                        <Phone className="h-3.5 w-3.5" />
                        {contact.telephone}
                      </span>
                    )}
                    {contact.email && (
                      <span className="flex items-center gap-1">
                        <Mail className="h-3.5 w-3.5" />
                        {contact.email}
                      </span>
                    )}
                    {contact.ville && (
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5" />
                        {contact.ville}
                      </span>
                    )}
                  </div>
                </div>
                <Badge variant="secondary">{contact.categorie}</Badge>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
