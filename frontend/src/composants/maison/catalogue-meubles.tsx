'use client'

import React, { useState } from 'react'
import { Input, Card, Tabs, TabsContent, TabsList, TabsTrigger, Badge } from '@/composants/ui'
import { Search, Armchair, UtensilsCrossed, Sofa, Bed, Wind, Lightbulb } from 'lucide-react'

interface Meuble {
  id: string
  nom: string
  type: string
  categorie: string
  largeur: number
  hauteur: number
  couleur: string
  icone: React.ReactNode
}

interface CatalogueMeublesProps {
  onAjouterMeuble?: (meuble: Meuble) => void
  readOnly?: boolean
}

// Catalogue de meubles par catégorie
const CATALOGUE: Record<string, Meuble[]> = {
  'Chambre': [
    {
      id: 'lit-1p',
      nom: 'Lit 1 place',
      type: 'lit',
      categorie: 'Chambre',
      largeur: 90,
      hauteur: 190,
      couleur: '#D4A574',
      icone: <Bed size={16} />,
    },
    {
      id: 'lit-2p',
      nom: 'Lit 2 places',
      type: 'lit',
      categorie: 'Chambre',
      largeur: 140,
      hauteur: 190,
      couleur: '#D4A574',
      icone: <Bed size={16} />,
    },
    {
      id: 'armoire',
      nom: 'Armoire',
      type: 'rangement',
      categorie: 'Chambre',
      largeur: 80,
      hauteur: 200,
      couleur: '#8B6F47',
      icone: <Armchair size={16} />,
    },
    {
      id: 'table-nuit',
      nom: 'Table de nuit',
      type: 'table',
      categorie: 'Chambre',
      largeur: 40,
      hauteur: 50,
      couleur: '#CD853F',
      icone: <Lightbulb size={16} />,
    },
    {
      id: 'commode',
      nom: 'Commode',
      type: 'rangement',
      categorie: 'Chambre',
      largeur: 60,
      hauteur: 80,
      couleur: '#A0826D',
      icone: <Armchair size={16} />,
    },
  ],
  'Séjour': [
    {
      id: 'canapé-3p',
      nom: 'Canapé 3 places',
      type: 'canapé',
      categorie: 'Séjour',
      largeur: 200,
      hauteur: 90,
      couleur: '#8B7355',
      icone: <Sofa size={16} />,
    },
    {
      id: 'canapé-2p',
      nom: 'Canapé 2 places',
      type: 'canapé',
      categorie: 'Séjour',
      largeur: 150,
      hauteur: 80,
      couleur: '#A0826D',
      icone: <Sofa size={16} />,
    },
    {
      id: 'table-basse',
      nom: 'Table basse',
      type: 'table',
      categorie: 'Séjour',
      largeur: 120,
      hauteur: 60,
      couleur: '#8B6F47',
      icone: <UtensilsCrossed size={16} />,
    },
    {
      id: 'tv-meuble',
      nom: 'Meuble TV',
      type: 'rangement',
      categorie: 'Séjour',
      largeur: 150,
      hauteur: 50,
      couleur: '#654321',
      icone: <Armchair size={16} />,
    },
    {
      id: 'bibliothèque',
      nom: 'Bibliothèque',
      type: 'rangement',
      categorie: 'Séjour',
      largeur: 90,
      hauteur: 200,
      couleur: '#8B4513',
      icone: <Armchair size={16} />,
    },
    {
      id: 'fauteuil',
      nom: 'Fauteuil',
      type: 'fauteuil',
      categorie: 'Séjour',
      largeur: 80,
      hauteur: 80,
      couleur: '#A0826D',
      icone: <Armchair size={16} />,
    },
  ],
  'Cuisine': [
    {
      id: 'table-cuisine',
      nom: 'Table de cuisine',
      type: 'table',
      categorie: 'Cuisine',
      largeur: 100,
      hauteur: 80,
      couleur: '#D4AF37',
      icone: <UtensilsCrossed size={16} />,
    },
    {
      id: 'chaise-cuisine',
      nom: 'Chaise de cuisine',
      type: 'chaise',
      categorie: 'Cuisine',
      largeur: 45,
      hauteur: 80,
      couleur: '#CD853F',
      icone: <Armchair size={16} />,
    },
    {
      id: 'îlot',
      nom: 'Îlot central',
      type: 'îlot',
      categorie: 'Cuisine',
      largeur: 120,
      hauteur: 65,
      couleur: '#8B7355',
      icone: <UtensilsCrossed size={16} />,
    },
    {
      id: 'buffet-cuisine',
      nom: 'Buffet de cuisine',
      type: 'rangement',
      categorie: 'Cuisine',
      largeur: 120,
      hauteur: 90,
      couleur: '#654321',
      icone: <Armchair size={16} />,
    },
    {
      id: 'frigo',
      nom: 'Réfrigérateur',
      type: 'électroménager',
      categorie: 'Cuisine',
      largeur: 70,
      hauteur: 170,
      couleur: '#D3D3D3',
      icone: <Wind size={16} />,
    },
    {
      id: 'four-cuisinière',
      nom: 'Four / Cuisinière',
      type: 'électroménager',
      categorie: 'Cuisine',
      largeur: 60,
      hauteur: 90,
      couleur: '#505050',
      icone: <UtensilsCrossed size={16} />,
    },
  ],
  'Salle de bain': [
    {
      id: 'baignoire',
      nom: 'Baignoire',
      type: 'sanitaire',
      categorie: 'Salle de bain',
      largeur: 70,
      hauteur: 150,
      couleur: '#F0F8FF',
      icone: <Wind size={16} />,
    },
    {
      id: 'douche',
      nom: 'Douche',
      type: 'sanitaire',
      categorie: 'Salle de bain',
      largeur: 80,
      hauteur: 80,
      couleur: '#E0E0E0',
      icone: <Wind size={16} />,
    },
    {
      id: 'lavabo',
      nom: 'Lavabo',
      type: 'sanitaire',
      categorie: 'Salle de bain',
      largeur: 60,
      hauteur: 60,
      couleur: '#FFFACD',
      icone: <Lightbulb size={16} />,
    },
    {
      id: 'wc',
      nom: 'WC',
      type: 'sanitaire',
      categorie: 'Salle de bain',
      largeur: 40,
      hauteur: 60,
      couleur: '#F5F5DC',
      icone: <Wind size={16} />,
    },
    {
      id: 'meuble-sdb',
      nom: 'Meuble sous-lavabo',
      type: 'rangement',
      categorie: 'Salle de bain',
      largeur: 60,
      hauteur: 50,
      couleur: '#8B7355',
      icone: <Armchair size={16} />,
    },
  ],
  'Bureau': [
    {
      id: 'bureau',
      nom: 'Bureau',
      type: 'bureau',
      categorie: 'Bureau',
      largeur: 120,
      hauteur: 60,
      couleur: '#8B6F47',
      icone: <UtensilsCrossed size={16} />,
    },
    {
      id: 'chaise-bureau',
      nom: 'Chaise de bureau',
      type: 'chaise',
      categorie: 'Bureau',
      largeur: 60,
      hauteur: 90,
      couleur: '#505050',
      icone: <Armchair size={16} />,
    },
    {
      id: 'étagère-bureau',
      nom: 'Étagère',
      type: 'rangement',
      categorie: 'Bureau',
      largeur: 80,
      hauteur: 150,
      couleur: '#8B7355',
      icone: <Armchair size={16} />,
    },
  ],
}

/**
 * Catalogue de meubles draggables
 * Permet de rechercher et ajouter des meubles au plan
 */
export function CatalogueMeubles({
  onAjouterMeuble,
  readOnly = false,
}: CatalogueMeublesProps) {
  const [recherche, setRecherche] = useState('')
  const [categorie, setCategorie] = useState<string>('Chambre')
  const [meublesFiltrés, setMeublesFiltrés] = useState<Meuble[]>(
    CATALOGUE[categorie] || []
  )

  const handleCategorieChange = (newCategorie: string) => {
    setCategorie(newCategorie)
    setMeublesFiltrés(CATALOGUE[newCategorie] || [])
  }

  const handleRecherche = (terme: string) => {
    setRecherche(terme)
    const meublesCat = CATALOGUE[categorie] || []
    if (!terme) {
      setMeublesFiltrés(meublesCat)
    } else {
      const terme_lower = terme.toLowerCase()
      setMeublesFiltrés(
        meublesCat.filter(
          (m) =>
            m.nom.toLowerCase().includes(terme_lower) ||
            m.type.toLowerCase().includes(terme_lower)
        )
      )
    }
  }

  const handleDragStart = (e: React.DragEvent<HTMLDivElement>, meuble: Meuble) => {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('meuble', JSON.stringify(meuble))
    
    // Créer une image personnalisée pour le drag
    const dragImage = document.createElement('div')
    dragImage.style.backgroundColor = meuble.couleur
    dragImage.style.width = '60px'
    dragImage.style.height = '60px'
    dragImage.style.padding = '5px'
    dragImage.style.borderRadius = '4px'
    dragImage.style.color = '#fff'
    dragImage.style.fontSize = '12px'
    dragImage.textContent = meuble.nom
    dragImage.style.position = 'absolute'
    dragImage.style.left = '-1000px'
    document.body.appendChild(dragImage)
    e.dataTransfer.setDragImage(dragImage, 30, 30)
    setTimeout(() => document.body.removeChild(dragImage), 0)
  }

  return (
    <Card className="w-full h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b bg-gradient-to-r from-blue-50 to-blue-100">
        <h3 className="font-semibold text-lg mb-3">Catalogue Meubles</h3>
        <div className="relative">
          <Search size={16} className="absolute left-3 top-3 text-gray-400" />
          <Input
            placeholder="Chercher un meuble..."
            value={recherche}
            onChange={(e) => handleRecherche(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* Contenu */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <Tabs
          value={categorie}
          onValueChange={handleCategorieChange}
          className="flex-1 flex flex-col"
        >
          <TabsList className="w-full rounded-none border-b bg-gray-50 p-0 h-auto overflow-x-auto">
            {Object.keys(CATALOGUE).map((cat) => (
              <TabsTrigger
                key={cat}
                value={cat}
                className="rounded-none border-b-2 border-transparent"
              >
                {cat}
              </TabsTrigger>
            ))}
          </TabsList>

          {Object.entries(CATALOGUE).map(([cat]) => (
            <TabsContent
              key={cat}
              value={cat}
              className="flex-1 overflow-y-auto p-2 m-0"
            >
              <div className="space-y-2">
                {meublesFiltrés.length === 0 ? (
                  <div className="p-8 text-center text-gray-400">
                    Aucun meuble trouvé
                  </div>
                ) : (
                  meublesFiltrés.map((meuble) => (
                    <div
                      key={meuble.id}
                      draggable={!readOnly}
                      onDragStart={(e) => !readOnly && handleDragStart(e, meuble)}
                      onClick={() => !readOnly && onAjouterMeuble?.(meuble)}
                      className={`p-3 rounded border-2 transition-all ${
                        readOnly
                          ? 'opacity-50 cursor-not-allowed'
                          : 'cursor-move hover:shadow-md hover:border-blue-400'
                      } bg-white`}
                      style={{
                        borderColor: meuble.couleur,
                        backgroundColor: `${meuble.couleur}10`,
                      }}
                    >
                      <div className="flex items-center gap-3">
                        {/* Icône */}
                        <div
                          className="w-10 h-10 rounded flex items-center justify-center text-white flex-shrink-0"
                          style={{ backgroundColor: meuble.couleur }}
                        >
                          {meuble.icone}
                        </div>

                        {/* Infos */}
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-sm">{meuble.nom}</div>
                          <div className="text-xs text-gray-500">
                            {meuble.largeur}×{meuble.hauteur} cm
                          </div>
                        </div>

                        {/* Badge type */}
                        <Badge variant="outline" className="text-xs flex-shrink-0">
                          {meuble.type}
                        </Badge>
                      </div>

                      {/* Info drag/drop */}
                      {!readOnly && (
                        <div className="text-xs text-gray-400 mt-2 text-center">
                          Glisser ou cliquer
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </TabsContent>
          ))}
        </Tabs>
      </div>

      {/* Footer avec info */}
      <div className="p-3 border-t bg-gray-50 text-xs text-gray-500">
        <div className="flex gap-4">
          <div>📌 Glisser vers le plan</div>
          <div>🖱️ Ou cliquer</div>
        </div>
      </div>
    </Card>
  )
}
