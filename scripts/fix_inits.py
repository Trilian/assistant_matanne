"""Fix module __init__.py files with simple imports."""

modules = {
    'cuisine': '''"""Module Cuisine - Structure Feature-First."""

from . import courses, inventaire, planificateur_repas, recettes

__all__ = ['courses', 'inventaire', 'planificateur_repas', 'recettes']
''',
    'famille': '''"""Module Famille - Structure Feature-First."""

from . import achats_famille, jules, suivi_perso, weekend, hub_famille

__all__ = ['achats_famille', 'jules', 'suivi_perso', 'weekend', 'hub_famille']
''',
    'maison': '''"""Module Maison - Structure Feature-First."""

from . import depenses, hub_maison

__all__ = ['depenses', 'hub_maison']
''',
    'jeux': '''"""Module Jeux - Paris sportifs et Loto."""

from . import loto, paris

__all__ = ['loto', 'paris']
''',
    'planning': '''"""Module Planning - Calendrier et organisation."""

from . import calendrier_unifie, vue_semaine, vue_ensemble

__all__ = ['calendrier_unifie', 'vue_semaine', 'vue_ensemble']
''',
    'outils': '''"""Module Outils - Accueil, parametres, rapports."""

from . import accueil, parametres, rapports, barcode

__all__ = ['accueil', 'parametres', 'rapports', 'barcode']
'''
}

for name, content in modules.items():
    path = f'src/modules/{name}/__init__.py'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Fixed {path}')

print('Done!')
