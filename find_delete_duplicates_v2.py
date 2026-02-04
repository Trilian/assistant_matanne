#!/usr/bin/env python3
"""Find and delete remaining duplicate test files."""
from pathlib import Path

print("FINDING DUPLICATE TEST FILES:")
print("="*60)

# Check for duplicates
duplicates = {
    "test_parametres.py": [],
    "test_rapports.py": [],
    "test_recettes_import.py": [],
    "test_vue_ensemble.py": [],
}

for filename, locations in duplicates.items():
    matches = list(Path("tests").rglob(filename))
    for match in matches:
        locations.append(str(match))

# Display findings
for filename, locations in duplicates.items():
    if len(locations) > 1:
        print(f"\n{filename}: {len(locations)} instances found")
        for i, loc in enumerate(locations, 1):
            print(f"  {i}. {loc}")

# Determine which to keep and which to delete
print("\n" + "="*60)
print("DELETION STRATEGY:")
print("="*60)

to_delete = []
for filename, locations in duplicates.items():
    if len(locations) > 1:
        # Keep the one in tests/ root, delete others in subdirs
        root_version = [l for l in locations if l.count('\\') == 1][0] if any(l.count('\\') == 1 for l in locations) else None
        
        if root_version:
            print(f"\nKeeping:  {root_version}")
            for loc in locations:
                if loc != root_version:
                    to_delete.append(loc)
                    print(f"Deleting: {loc}")

# Delete the files
print("\n" + "="*60)
print("DELETING DUPLICATES:")
print("="*60)

for filepath in to_delete:
    path = Path(filepath)
    if path.exists():
        path.unlink()
        print(f"✓ Deleted: {filepath}")
    else:
        print(f"⊘ Not found: {filepath}")

print("\n" + "="*60)
print(f"Total deleted: {len(to_delete)} files")
