"""Audit API parameter naming in route files."""
import re
import os
import glob

route_dir = "src/api/routes"
files = sorted(glob.glob(os.path.join(route_dir, "*.py")))

results = []

for fpath in files:
    if "__init__" in fpath or "__pycache__" in fpath:
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        match = re.match(r"@router\.(post|put|patch)\s*\(", line)
        if match:
            method = match.group(1).upper()
            j = i + 1
            while j < len(lines):
                defline = lines[j].strip()
                if defline.startswith("def ") or defline.startswith("async def "):
                    break
                j += 1
            if j >= len(lines):
                i += 1
                continue

            func_sig = ""
            k = j
            paren_count = 0
            while k < len(lines):
                func_sig += lines[k] + " "
                paren_count += lines[k].count("(") - lines[k].count(")")
                if paren_count <= 0 and "(" in func_sig:
                    break
                k += 1

            fname_match = re.search(r"(?:async\s+)?def\s+(\w+)", func_sig)
            fname = fname_match.group(1) if fname_match else "???"

            skip_types = {
                "int", "str", "float", "bool", "dict", "list",
                "Optional", "Query", "Path", "Request", "Response",
                "UploadFile", "BackgroundTasks", "HTTPAuthorizationCredentials",
                "WebSocket", "Session",
            }
            skip_params = {
                "user", "page", "page_size", "taille_page", "db", "session",
                "request", "response", "background_tasks", "fichier", "file",
                "credentials",
            }

            param_matches = re.findall(r"(\w+)\s*:\s*([A-Z]\w+)", func_sig)
            body_params = []
            for pname, ptype in param_matches:
                if pname in skip_params:
                    continue
                if ptype in skip_types:
                    continue
                depends_pattern = pname + r"\s*:\s*" + ptype + r"\s*=\s*Depends"
                if re.search(depends_pattern, func_sig):
                    continue
                # Skip path params (typically _id params)
                body_params.append((pname, ptype))

            if body_params:
                for pname, ptype in body_params:
                    results.append((fpath.replace("\\", "/"), fname, method, pname, ptype, i + 1))
        i += 1

# Print results
print(f"Found {len(results)} route handlers with Pydantic body params:\n")

non_conforming = []
conforming = []

for fpath, fname, method, pname, ptype, line_num in results:
    short = fpath.replace("src/api/routes/", "")
    if method == "PATCH":
        expected = "maj"
    else:
        expected = "donnees"
    
    is_ok = pname == expected
    status = "OK" if is_ok else f"SHOULD BE: {expected}"
    
    entry = f"  {short:<40} {fname:<45} {method:<7} {pname:<20} {ptype:<40} L{line_num}"
    if is_ok:
        conforming.append(entry)
    else:
        non_conforming.append(entry)

print("=" * 50)
print(f"NON-CONFORMING ({len(non_conforming)}):")
print("=" * 50)
header = f"  {'FILE':<40} {'FUNCTION':<45} {'METHOD':<7} {'PARAM':<20} {'TYPE':<40} LINE"
print(header)
print("  " + "-" * 155)
for e in non_conforming:
    print(e)

print()
print("=" * 50)
print(f"CONFORMING ({len(conforming)}):")
print("=" * 50)
print(header)
print("  " + "-" * 155)
for e in conforming:
    print(e)

print(f"\nSUMMARY: {len(non_conforming)} non-conforming, {len(conforming)} conforming out of {len(results)} total")
