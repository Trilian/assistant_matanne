import subprocess

repo = r"c:\Users\menar\Documents\Projet_perso\assistant_matanne"

# Step 1: current branch
r = subprocess.run(["git", "-C", repo, "branch", "--show-current"], capture_output=True, text=True)
print("Current branch:", r.stdout.strip(), r.stderr.strip())

# Step 2: log main
r = subprocess.run(["git", "-C", repo, "log", "--oneline", "-3"], capture_output=True, text=True)
print("Main log:", r.stdout.strip())

# Step 3: log worktree branch
r = subprocess.run(["git", "-C", repo, "log", "--oneline", "-5", "copilot/worktree-2026-03-27T12-26-35"], capture_output=True, text=True)
print("Worktree branch log:", r.stdout.strip(), r.stderr.strip())

# Step 4: merge
r = subprocess.run([
    "git", "-C", repo, "merge", "--no-ff",
    "copilot/worktree-2026-03-27T12-26-35",
    "-m", "Merge worktree: module Maison phases restantes completes (5B/9A/9F/11B/11C/6/12)"
], capture_output=True, text=True)
print("Merge stdout:", r.stdout.strip())
print("Merge stderr:", r.stderr.strip())
print("Merge return code:", r.returncode)
