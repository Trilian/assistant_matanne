import json

try:
    with open('coverage.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extraire les métriques globales
    if 'totals' in data:
        totals = data['totals']
        covered = totals.get('covered_lines', 0)
        total = totals.get('num_statements', 0)
        pct = totals.get('percent_covered', 0)
        
        print('=' * 50)
        print('✅ COUVERTURE GLOBALE (Phase 14-15)')
        print('=' * 50)
        print(f'Lignes couvertes: {covered}')
        print(f'Lignes totales: {total}')
        print(f'Pourcentage: {pct:.2f}%')
        print()
        
        # Évaluation par rapport à l'objectif
        target = 35.0
        delta_baseline = pct - 14.51  # baseline avant Phase 14
        delta_target = pct - target
        
        print(f'Baseline (avant Phase 14): 14.51%')
        print(f'Progression: +{delta_baseline:.2f}%')
        print(f'Objectif Phase 15: 35.00%')
        print(f'Écart à l\'objectif: {delta_target:+.2f}%')
        print()
        
        if pct >= target:
            print(f'🎉 OBJECTIF ATTEINT: {pct:.2f}% >= 35.00%')
        else:
            pct_needed = target - pct
            lines_needed = int(total * pct_needed / 100)
            print(f'⚠️  À améliorer: +{pct_needed:.2f}% (≈ {lines_needed} lignes)')
    else:
        print('Clés dans le fichier:', list(data.keys()))
except Exception as e:
    print(f'Erreur: {e}')
    import traceback
    traceback.print_exc()
