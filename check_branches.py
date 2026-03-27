import subprocess

repo = r"C:\Users\menar\Documents\Projet_perso\assistant_matanne"

def run(args):
    r = subprocess.run(args, cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.stdout.strip(): print(r.stdout.strip())
    if r.stderr.strip(): print("[STDERR]", r.stderr.strip())
    return r

print("=== ALL LOCAL BRANCHES ===")
run(["git", "branch", "-v"])

print("\n=== ALL REMOTE/TRACKING BRANCHES ===")
run(["git", "branch", "-r"])

print("\n=== WORKTREES ===")
run(["git", "worktree", "list"])
