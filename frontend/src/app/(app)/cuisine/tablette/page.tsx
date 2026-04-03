'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ChefHat, Clock, ShoppingCart, Volume2, Pause, Play } from 'lucide-react';
import { Button } from '@/composants/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/composants/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/composants/ui/tabs';

/**
 * INNO-10: Widget Tablette Cuisine
 * 
 * Page optimisée pour affichage sur tablette Google (landscape ou portrait)
 * Éléments:
 * - Recette en cours + ingrédients
 * - Timer cuisson (grand affichage)
 * - Liste courses à côté
 * 
 * Utilisation: Poser la tablette sur la cuisine, elle se met à jour en temps réel
 * Navigation: Clavier/touches (flèches, espace pour pause)
 */

const TimerFull = ({ duree_secondes = 1800 }: { duree_secondes: number }) => {
  const [temps_restant, setTemps] = useState(duree_secondes);
  const [actif, setActif] = useState(false);

  useEffect(() => {
    if (!actif || temps_restant <= 0) return;
    const interval = setInterval(() => {
      setTemps(t => t - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [actif, temps_restant]);

  const minutes = Math.floor(temps_restant / 60);
  const secondes = temps_restant % 60;

  return (
    <div className="flex flex-col items-center justify-center gap-8">
      <div className="text-9xl font-bold font-mono text-orange-600">
        {String(minutes).padStart(2, '0')}:{String(secondes).padStart(2, '0')}
      </div>
      <div className="flex gap-4">
        <Button
          onClick={() => setActif(!actif)}
          size="lg"
          className="text-lg px-8 py-6"
          variant={actif ? 'secondary' : 'default'}
        >
          {actif ? <Pause className="mr-2" /> : <Play className="mr-2" />}
          {actif ? 'Pause' : 'Démarrer'}
        </Button>
        <Button
          onClick={() => setTemps(duree_secondes)}
          size="lg"
          variant="outline"
          className="text-lg px-8 py-6"
        >
          Réinitialiser
        </Button>
      </div>
    </div>
  );
};

const RecetteCourante = ({ recette_id = 1 }: { recette_id?: number }) => {
  // Simulation recette (en prod: appel API)
  const recette = {
    nom: "Poulet rôti au citron",
    temps_preparation: 30,
    temps_cuisson: 45,
    portions: 4,
    ingredients: [
      { nom: "Poulet entier", quantite: "1", unite: "kg" },
      { nom: "Citrons", quantite: "2", unite: "" },
      { nom: "Ail", quantite: "4", unite: "gousses" },
      { nom: "Thym", quantite: "2", unite: "branches" },
      { nom: "Huile d'olive", quantite: "4", unite: "cuil. à soupe" },
    ],
    etapes: [
      { numero: 1, description: "Préchauffer four à 200°C" },
      { numero: 2, description: "Frotter le poulet avec thym et ail pressé" },
      { numero: 3, description: "Placer dans le four" },
      { numero: 4, description: "Cuire 45 minutes" },
      { numero: 5, description: "Servir avec les agrumes" },
    ]
  };

  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-4xl">{recette.nom}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4 text-xl">
          <div className="flex items-center gap-2">
            <Clock className="text-orange-600" size={24} />
            <span>{recette.temps_preparation + recette.temps_cuisson} min (Prép: {recette.temps_preparation}min)</span>
          </div>
          <div className="flex items-center gap-2">
            <ChefHat className="text-orange-600" size={24} />
            <span>{recette.portions} portions</span>
          </div>
        </div>

        <div>
          <h3 className="text-2xl font-semibold mb-3">Ingrédients</h3>
          <ul className="space-y-2 text-lg">
            {recette.ingredients.map((ing, i) => (
              <li key={i} className="flex items-center gap-3">
                <input type="checkbox" className="w-6 h-6" />
                <span>{ing.quantite} {ing.unite} — {ing.nom}</span>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-2xl font-semibold mb-3">Étapes</h3>
          <ol className="space-y-2 text-lg">
            {recette.etapes.map((etape) => (
              <li key={etape.numero} className="flex gap-3">
                <span className="font-bold text-orange-600 w-8">{etape.numero}.</span>
                <span>{etape.description}</span>
              </li>
            ))}
          </ol>
        </div>
      </CardContent>
    </Card>
  );
};

const ListeCoursesWidget = () => {
  // Simulation liste courses
  const articles = [
    { id: 1, nom: "Poulet fermier 1kg", quantite: 1, unite: "kg", priorite: "haute" },
    { id: 2, nom: "Citrons jaunes", quantite: 3, unite: "", priorite: "haute" },
    { id: 3, nom: "Ail", quantite: "1", unite: "botte", priorite: "moyenne" },
    { id: 4, nom: "Thym frais", quantite: "1", unite: "botte", priorite: "moyenne" },
    { id: 5, nom: "Huile d'olive vierge extra", quantite: "1L", priorite: "moyenne" },
  ];

  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-2xl flex items-center gap-2">
          <ShoppingCart size={24} />
          Courses
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {articles.map((article) => (
            <div key={article.id} className="flex items-center gap-3 p-3 bg-slate-50 rounded border">
              <input type="checkbox" className="w-5 h-5" />
              <div className="flex-1">
                <p className="text-lg font-medium">{article.nom}</p>
                <p className="text-sm text-slate-600">{article.quantite} {article.unite}</p>
              </div>
              <div className={`text-xs px-2 py-1 rounded font-semibold ${
                article.priorite === 'haute' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
              }`}>
                {article.priorite}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default function PageTabletteCuisine() {
  const [layout, setLayout] = useState<'split' | 'full'>('split');

  // Gestion clavier pour navigation simple
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'l') setLayout(layout === 'split' ? 'full' : 'split');
      if (e.key === 'Escape') window.location.href = '/cuisine';
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [layout]);

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-orange-50 to-white flex flex-col">
      {/* En-tête minimal */}
      <div className="bg-orange-600 text-white px-6 py-3 flex justify-between items-center">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <ChefHat /> Widget Cuisine
        </h1>
        <div className="flex gap-2">
          <Button 
            onClick={() => setLayout(layout === 'split' ? 'full' : 'split')}
            size="sm"
            variant="ghost"
            className="text-white hover:bg-orange-700"
          >
            {layout === 'split' ? '📱 Plein écran' : '↔️ Split'}
          </Button>
          <Link href="/cuisine">
            <Button size="sm" variant="ghost" className="text-white hover:bg-orange-700">
              Fermer (Esc)
            </Button>
          </Link>
        </div>
      </div>

      {/* Contenu principal */}
      <div className="flex-1 overflow-auto p-6">
        {layout === 'split' ? (
          <div className="grid grid-cols-2 gap-6 h-full">
            {/* Left: Recette + Timer */}
            <div className="space-y-6">
              <RecetteCourante />
            </div>

            {/* Right: Courses + Timer */}
            <div className="space-y-6">
              <ListeCoursesWidget />
              <Card>
                <CardHeader>
                  <CardTitle className="text-2xl">⏱️ Minuteur</CardTitle>
                </CardHeader>
                <CardContent>
                  <TimerFull duree_secondes={45 * 60} />
                </CardContent>
              </Card>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <Tabs defaultValue="recette" className="w-full h-screen">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="recette">Recette</TabsTrigger>
                <TabsTrigger value="timer">Minuteur</TabsTrigger>
                <TabsTrigger value="courses">Courses</TabsTrigger>
              </TabsList>

              <TabsContent value="recette" className="mt-4">
                <RecetteCourante />
              </TabsContent>

              <TabsContent value="timer" className="mt-4 flex h-96">
                <Card className="w-full">
                  <CardContent className="pt-6 h-full">
                    <TimerFull duree_secondes={45 * 60} />
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="courses" className="mt-4">
                <ListeCoursesWidget />
              </TabsContent>
            </Tabs>
          </div>
        )}
      </div>

      {/* Aide clavier */}
      <div className="bg-slate-100 px-6 py-2 text-sm text-slate-600">
        <span className="font-mono">Clavier: [L] = Layout | [Esc] = Retour | [Espace] = Timer</span>
      </div>
    </div>
  );
}
