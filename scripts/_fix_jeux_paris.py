"""Script temporaire pour retirer sync BudgetFamille de jeux_paris.py."""

with open("src/api/routes/jeux_paris.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the BudgetFamille import
content = content.replace(
    "from src.core.models import BudgetFamille, HistoriqueJeux, PariSportif",
    "from src.core.models import HistoriqueJeux, PariSportif",
)

# Replace the sync_budget block
old_block = '''            statut_change = ancien_statut != pari.statut
            sync_budget = False
            mise = Decimal(str(pari.mise or 0))
            gain = Decimal(str(pari.gain or 0))
            event_payload: dict[str, Any] | None = None

            # IM-8 : synchroniser pertes + gains vers budget/finances avec logique idempotente.
            if statut_change and not pari.est_virtuel:
                marqueur_sync = f"sync_jeux_budget:auto:pari:{pari.id}:"
                (
                    session.query(BudgetFamille)
                    .filter(BudgetFamille.notes.like(f"{marqueur_sync}%"))
                    .delete(synchronize_session=False)
                )

                if pari.statut == "perdu" and mise > 0:
                    session.add(
                        BudgetFamille(
                            date=date.today(),
                            categorie="jeux_paris_perte",
                            description=f"Perte pari #{pari.id}",
                            montant=float(mise),
                            notes=f"{marqueur_sync}perte",
                        )
                    )
                    sync_budget = True
                elif pari.statut == "gagne" and gain > 0:
                    session.add(
                        BudgetFamille(
                            date=date.today(),
                            categorie="jeux_paris_gain",
                            description=f"Gain pari #{pari.id}",
                            montant=float(gain),
                            notes=f"{marqueur_sync}gain",
                        )
                    )
                    sync_budget = True

                historique = ('''

new_block = '''            statut_change = ancien_statut != pari.statut
            mise = Decimal(str(pari.mise or 0))
            gain = Decimal(str(pari.gain or 0))
            event_payload: dict[str, Any] | None = None

            # Mise \u00e0 jour de l'historique jeux (budgets jeux/famille s\u00e9par\u00e9s).
            if statut_change and not pari.est_virtuel:
                historique = ('''

if old_block in content:
    content = content.replace(old_block, new_block)
    print("Block replaced OK")
else:
    print("ERROR: block not found")

# Remove sync_budget from the return dict
content = content.replace(
    '                "sync_budget": sync_budget,\n',
    "",
)

with open("src/api/routes/jeux_paris.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Done")
