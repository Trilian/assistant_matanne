from __future__ import annotations

import inspect
from pathlib import Path

import mutmut.__main__ as mutmut_main


CORRECTIONS = [
    (
        "    module_name = strip_prefix(module_name, prefix='src.')\n",
        "",
        "Conserver le prefixe 'src.' pour aligner les noms de mutants avec les imports reels du projet.",
    ),
    (
        "        assert not name.startswith('src.'), f'Failed trampoline hit. Module name starts with \"src.\", which is invalid: {name}'\n",
        "",
        "Autoriser les modules projet nommes sous le package top-level 'src'.",
    ),
]


def appliquer_patch() -> int:
    fichier = Path(inspect.getsourcefile(mutmut_main) or "")
    if not fichier.exists():
        raise FileNotFoundError("Impossible de localiser mutmut.__main__")

    contenu = fichier.read_text(encoding="utf-8")
    contenu_original = contenu
    modifications: list[str] = []

    for ancien, nouveau, description in CORRECTIONS:
        if ancien in contenu:
            contenu = contenu.replace(ancien, nouveau)
            modifications.append(description)

    if contenu == contenu_original:
        print(f"Aucun patch a appliquer dans {fichier}")
        return 0

    fichier.write_text(contenu, encoding="utf-8")
    print(f"Patch mutmut applique dans {fichier}")
    for description in modifications:
        print(f"- {description}")
    return 0


if __name__ == "__main__":
    raise SystemExit(appliquer_patch())
