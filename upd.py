import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('docs/PLANNING_IMPLEMENTATION.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Sprint 4 progress bar: 0% -> 100%
html = html.replace(
    '<div class="progress-bar tall"><div class="progress-fill fill-purple" style="width:0%">0%</div></div>',
    '<div class="progress-bar tall"><div class="progress-fill fill-purple" style="width:100%">100%</div></div>'
)

# Sprint 4 checklist: replace the single I line with 8 done items
old_i_line = '<li class="todo">I: Onboarding, search global, quick capture, offline, rollback auto, CSP, rapport PDF, vocal</li>'
new_i_lines = (
    '<li>I1: Onboarding interactif - fait (tour-onboarding.tsx)</li>\n'
    '      <li>I2: Search global cmdk - fait (recherche-globale.tsx)</li>\n'
    '      <li>I3: Quick capture FAB - fait (fab-actions-rapides.tsx)</li>\n'
    '      <li>I4: Rapport mensuel auto - fait (rapport_mensuel_auto cron 1er/mois 8h30)</li>\n'
    '      <li>I5: Raccourci vocal - fait (routes/assistant.py)</li>\n'
    '      <li>I6: Mode offline - fait (public/sw.js)</li>\n'
    '      <li>I7: Rollback CI/CD - fait (deploy-production.yml + health check + Vercel rollback)</li>\n'
    '      <li>I8: CSP strict + rotation JWT - fait (security.py + auth.py 2-cles + CSP report-uri)</li>'
)
html = html.replace(old_i_line, new_i_lines)

# Roadmap table: Phase I row status
html = html.replace(
    '<td><span class="tag tag-phase">I</span></td><td>Innovations (optionnel)</td><td>\U0001f7e2 Nice-to-have</td><td>~25h</td><td>8</td><td>UX, DevOps, S\xe9curit\xe9</td>',
    '<td><span class="tag tag-phase">I</span></td><td>Innovations (optionnel)</td><td><span class="tag tag-done">\u2705 Termin\xe9</span></td><td>~9h r\xe9elles</td><td>8</td><td>UX, DevOps, S\xe9curit\xe9</td>'
)

# Sprint 4 header: add phase I done note (replace first occurrence only)
html = html.replace(
    'Score: 8.7 \u2192 9.2</span>',
    'Score: 8.7 \u2192 9.2 \u2014 Phase I \u2705 termin\xe9e</span>',
    1
)

with open('docs/PLANNING_IMPLEMENTATION.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Validate
ok = True
checks = [
    ('width:100%">100%', 'Sprint4Progress100'),
    ('I8: CSP strict + rotation JWT - fait', 'I8done'),
    ('Termin\xe9', 'PhaseITermine'),
    ('Phase I \u2705 termin\xe9e', 'Sprint4Note'),
]
for pat, label in checks:
    found = pat in html
    print(('OK' if found else 'FAIL'), label)
    if not found:
        ok = False

print('Global:', 'SUCCESS' if ok else 'PARTIAL')
