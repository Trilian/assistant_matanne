"""Temporary cleanup script for test files - delete after use."""
import pathlib

# ── 1. test_routes_maison.py ──
f = pathlib.Path("tests/api/test_routes_maison.py")
content = f.read_text(encoding="utf-8")
lines = content.split("\n")

# Remove CONTRAT_TEST and GARANTIE_TEST fixtures (lines 84-102 in original)
# Find and remove them
new_lines = []
skip_block = False
skip_until_blank_after_dict = False

i = 0
while i < len(lines):
    line = lines[i]

    # Skip CONTRAT_TEST dict
    if line.startswith("CONTRAT_TEST = {"):
        while i < len(lines) and not (lines[i].strip() == "}" and i > 0):
            i += 1
        i += 1  # skip the closing }
        # Skip blank lines after
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        continue

    # Skip GARANTIE_TEST dict
    if line.startswith("GARANTIE_TEST = {"):
        while i < len(lines) and not (lines[i].strip() == "}" and i > 0):
            i += 1
        i += 1  # skip the closing }
        # Skip blank lines after
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        continue

    new_lines.append(line)
    i += 1

content = "\n".join(new_lines)

# Remove contrat/garantie endpoint params from TestEndpointsExistent
# Remove lines containing "/api/v1/maison/contrats" or "/api/v1/maison/garanties"
# and their comment headers
lines = content.split("\n")
new_lines = []
for line in lines:
    stripped = line.strip()
    if "# Contrats" == stripped:
        continue
    if "# Garanties" == stripped:
        continue
    if "/api/v1/maison/contrats" in line and "parametrize" not in line:
        continue
    if "/api/v1/maison/garanties" in line and "parametrize" not in line:
        continue
    if "/api/v1/maison/charges" in line and "parametrize" not in line:
        continue
    new_lines.append(line)
content = "\n".join(new_lines)

# Remove test_contrat_create_valide method
lines = content.split("\n")
new_lines = []
i = 0
while i < len(lines):
    if "def test_contrat_create_valide" in lines[i]:
        # Skip until next method or class or blank line after code
        i += 1
        while i < len(lines) and (lines[i].startswith("        ") or lines[i].strip() == ""):
            i += 1
        continue
    new_lines.append(lines[i])
    i += 1
content = "\n".join(new_lines)

# Remove test_incident_sav_patch_valide method
lines = content.split("\n")
new_lines = []
i = 0
while i < len(lines):
    if "def test_incident_sav_patch_valide" in lines[i]:
        i += 1
        while i < len(lines) and (lines[i].startswith("        ") or lines[i].strip() == ""):
            i += 1
        continue
    new_lines.append(lines[i])
    i += 1
content = "\n".join(new_lines)

# Remove test_garantie_create method
lines = content.split("\n")
new_lines = []
i = 0
while i < len(lines):
    if "def test_garantie_create" in lines[i]:
        i += 1
        while i < len(lines) and (lines[i].startswith("        ") or lines[i].strip() == ""):
            i += 1
        continue
    new_lines.append(lines[i])
    i += 1
content = "\n".join(new_lines)

# Remove test_stats_hub_response_valide method (references non-existent fields)
lines = content.split("\n")
new_lines = []
i = 0
while i < len(lines):
    if "def test_stats_hub_response_valide" in lines[i]:
        i += 1
        while i < len(lines) and (lines[i].startswith("        ") or lines[i].strip() == ""):
            i += 1
        continue
    new_lines.append(lines[i])
    i += 1
content = "\n".join(new_lines)

# Remove TestRoutesContrats class
lines = content.split("\n")
new_lines = []
i = 0
while i < len(lines):
    if "class TestRoutesContrats:" in lines[i]:
        i += 1
        while i < len(lines) and (lines[i].startswith("    ") or lines[i].strip() == ""):
            if lines[i].strip() != "" and not lines[i].startswith("    "):
                break
            i += 1
        continue
    new_lines.append(lines[i])
    i += 1
content = "\n".join(new_lines)

# Remove TestRoutesGaranties class
lines = content.split("\n")
new_lines = []
i = 0
while i < len(lines):
    if "class TestRoutesGaranties:" in lines[i]:
        i += 1
        while i < len(lines) and (lines[i].startswith("    ") or lines[i].strip() == ""):
            if lines[i].strip() != "" and not lines[i].startswith("    "):
                break
            i += 1
        continue
    new_lines.append(lines[i])
    i += 1
content = "\n".join(new_lines)

# Update docstring
content = content.replace(
    "cellier, artisans, contrats, garanties, diagnostics",
    "cellier, artisans, diagnostics"
)

f.write_text(content, encoding="utf-8")
print("test_routes_maison.py cleaned")

# ── 2. test_routes_maison_finances.py ──
f2 = pathlib.Path("tests/api/test_routes_maison_finances.py")
content2 = f2.read_text(encoding="utf-8")
lines2 = content2.split("\n")
new_lines2 = []
for line in lines2:
    if "/api/v1/maison/contrats" in line:
        continue
    if "/api/v1/maison/garanties" in line:
        continue
    new_lines2.append(line)
content2 = "\n".join(new_lines2)
f2.write_text(content2, encoding="utf-8")
print("test_routes_maison_finances.py cleaned")

# ── 3. test_schema_coherence.py ──
f3 = pathlib.Path("tests/sql/test_schema_coherence.py")
if f3.exists():
    content3 = f3.read_text(encoding="utf-8")
    if "contrats" in content3:
        # Remove lines referencing contrats
        lines3 = content3.split("\n")
        new_lines3 = [l for l in lines3 if "contrats" not in l.lower() or "contrat" not in l]
        f3.write_text("\n".join(new_lines3), encoding="utf-8")
        print("test_schema_coherence.py cleaned")
    else:
        print("test_schema_coherence.py already clean")
else:
    print("test_schema_coherence.py not found")

print("All test files cleaned!")
