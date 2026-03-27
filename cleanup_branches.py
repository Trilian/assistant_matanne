import subprocess, os

repo = r"C:\Users\menar\Documents\Projet_perso\assistant_matanne"

def run(args, cwd=None):
    r = subprocess.run(args, cwd=cwd or repo, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.stdout.strip(): print(r.stdout.strip())
    if r.stderr.strip(): print("[STDERR]", r.stderr.strip())
    print(f"[RC={r.returncode}]")
    return r

worktrees_to_remove = [
    r"C:\Users\menar\Documents\Projet_perso\assistant_matanne.worktrees\copilot-worktree-2026-03-27T11-28-30.worktrees\copilot-worktree-2026-03-27T11-29-15",
    r"C:\Users\menar\Documents\Projet_perso\assistant_matanne.worktrees\copilot-worktree-2026-03-27T11-28-30",
    r"C:\Users\menar\Documents\Projet_perso\assistant_matanne.worktrees\copilot-worktree-2026-03-27T12-03-16",
    r"C:\Users\menar\Documents\Projet_perso\assistant_matanne.worktrees\copilot-worktree-2026-03-27T12-20-47",
    r"C:\Users\menar\Documents\Projet_perso\assistant_matanne.worktrees\copilot-worktree-2026-03-27T12-21-14",
    r"C:\Users\menar\Documents\Projet_perso\assistant_matanne.worktrees\copilot-worktree-2026-03-27T12-26-35",
    r"C:\Users\menar\Documents\Projet_perso\assistant_matanne.worktrees\copilot-worktree-2026-03-27T12-29-06",
    r"C:\Users\menar\Documents\Projet_perso\assistant_matanne.worktrees\copilot-worktree-2026-03-27T13-21-01",
]

branches_to_delete = [
    "copilot/worktree-2026-03-27T11-28-30",
    "copilot/worktree-2026-03-27T11-29-15",
    "copilot/worktree-2026-03-27T12-03-16",
    "copilot/worktree-2026-03-27T12-20-47",
    "copilot/worktree-2026-03-27T12-21-14",
    "copilot/worktree-2026-03-27T12-26-35",
    "copilot/worktree-2026-03-27T12-29-06",
    "copilot/worktree-2026-03-27T13-21-01",
]

print("=== REMOVING WORKTREES ===")
for wt in worktrees_to_remove:
    print(f"\n-- Removing: {wt}")
    run(["git", "worktree", "remove", "--force", wt])

print("\n=== PRUNING WORKTREES ===")
run(["git", "worktree", "prune", "-v"])

print("\n=== DELETING LOCAL BRANCHES ===")
for b in branches_to_delete:
    print(f"\n-- Deleting branch: {b}")
    run(["git", "branch", "-D", b])

print("\n=== FINAL STATE ===")
run(["git", "branch", "-v"])
run(["git", "worktree", "list"])

print("\n=== DELETING REMOTE DEPENDABOT BRANCHES ===")
dependabot_branches = [
    "dependabot/github_actions/actions/checkout-6",
    "dependabot/github_actions/actions/setup-python-6",
    "dependabot/github_actions/actions/upload-artifact-6",
    "dependabot/pip/cachetools-7.0.4",
    "dependabot/pip/certifi-2026.2.25",
    "dependabot/pip/minor-and-patch-0000c844af",
    "dependabot/pip/pillow-12.1.1",
    "dependabot/pip/websockets-16.0",
]
for b in dependabot_branches:
    print(f"\n-- Deleting remote: {b}")
    run(["git", "push", "origin", "--delete", b])

print("\n=== FINAL REMOTE BRANCHES ===")
run(["git", "branch", "-r"])
