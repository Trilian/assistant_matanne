import subprocess

worktree = r"C:\Users\menar\Documents\Projet_perso\assistant_matanne.worktrees\copilot-worktree-2026-03-27T13-21-01"
main_repo = r"C:\Users\menar\Documents\Projet_perso\assistant_matanne"
worktree_branch = "copilot/worktree-2026-03-27T13-21-01"

def run(args, cwd=None):
    r = subprocess.run(args, cwd=cwd or worktree, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = r.stdout.strip()
    err = r.stderr.strip()
    if out: print(out)
    if err: print("[STDERR]", err)
    print(f"[RC={r.returncode}]\n")
    return r.returncode

print("=== STATUS ===")
run(["git", "status"])

print("=== BRANCH ===")
run(["git", "branch"])

print("=== STAGE ALL ===")
run(["git", "add", "-A"])

print("=== COMMIT ===")
commit_msg = """feat(famille): finaliser module famille M-R + Sprint 3

Correctifs: AchatFamille ORM model cree, ArticleAchat repare
Phases O/P/Q: badges urgence hub, widget achats IA, auto-prefill activites
Sprint 2: subscribers evenementiels budget/document/jalon
Sprint 3: ScoringPertinenceService, scorer_et_trier, raison_suggestion
Nettoyage: album.py, journal_ia.py, endpoints journal supprimes
Docs: ROADMAP.md + STATUS_PHASES.md mis a jour phases O/P/Q/R + Sprint 3

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"""
run(["git", "commit", "-m", commit_msg])

print("=== WORKTREE LOG ===")
run(["git", "log", "--oneline", "-5"])

print("=== MERGE INTO MAIN ===")
run(["git", "fetch", "."], cwd=main_repo)
run([
    "git", "-C", main_repo, "merge", "--no-ff",
    worktree_branch,
    "-m", f"Merge worktree: module famille M-R finalise + Sprint 3\n\nCo-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
])

print("=== MAIN REPO LOG ===")
run(["git", "-C", main_repo, "log", "--oneline", "-5"])
