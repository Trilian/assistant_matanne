"""
Constantes pour le package courses.

Mappings rayons et priorités pour la catégorisation des articles.
"""

# Mapping ingrédients -> rayons magasin
MAPPING_RAYONS: dict[str, str] = {
    # Fruits & Légumes
    "tomate": "Fruits & Légumes",
    "carotte": "Fruits & Légumes", 
    "oignon": "Fruits & Légumes",
    "ail": "Fruits & Légumes",
    "pomme de terre": "Fruits & Légumes",
    "courgette": "Fruits & Légumes",
    "poivron": "Fruits & Légumes",
    "salade": "Fruits & Légumes",
    "haricot": "Fruits & Légumes",
    
    # Viandes
    "poulet": "Boucherie",
    "boeuf": "Boucherie",
    "porc": "Boucherie",
    "veau": "Boucherie",
    "agneau": "Boucherie",
    "steak": "Boucherie",
    "escalope": "Boucherie",
    
    # Poissons
    "saumon": "Poissonnerie",
    "cabillaud": "Poissonnerie",
    "crevette": "Poissonnerie",
    "thon": "Poissonnerie",
    
    # Crèmerie
    "lait": "Crèmerie",
    "beurre": "Crèmerie",
    "crème": "Crèmerie",
    "fromage": "Crèmerie",
    "yaourt": "Crèmerie",
    "oeuf": "Crèmerie",
    
    # Épicerie
    "pâtes": "Épicerie",
    "riz": "Épicerie",
    "huile": "Épicerie",
    "vinaigre": "Épicerie",
    "sel": "Épicerie",
    "poivre": "Épicerie",
    "farine": "Épicerie",
    "sucre": "Épicerie",
    "conserve": "Épicerie",
    
    # Surgelés
    "surgelé": "Surgelés",
    "glace": "Surgelés",
}

# Priorités par rayon (1 = haute, 3 = basse)
PRIORITES: dict[str, int] = {
    "Boucherie": 1,      # Priorité haute (périme vite)
    "Poissonnerie": 1,
    "Crèmerie": 1,
    "Fruits & Légumes": 2,
    "Surgelés": 2,
    "Épicerie": 3,       # Priorité basse (se conserve)
    "Autre": 3,
}

__all__ = ["MAPPING_RAYONS", "PRIORITES"]
