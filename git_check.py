import subprocess
repo = r"c:\Users\menar\Documents\Projet_perso\assistant_matanne.worktrees\copilot-worktree-2026-03-27T12-26-35"

# Check status
r = subprocess.run(["git", "-C", repo, "status", "--short"], capture_output=True, text=True)
print("STATUS:\n", r.stdout)

# Show last commit details
r2 = subprocess.run(["git", "-C", repo, "show", "--stat", "HEAD"], capture_output=True, text=True)
print("LAST COMMIT:\n", r2.stdout[:3000])
