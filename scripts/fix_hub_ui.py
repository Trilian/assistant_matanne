import re

with open(
    "d:/Projet_streamlit/assistant_matanne/src/modules/maison/hub/ui.py", encoding="utf-8"
) as f:
    text = f.read()

new_text = re.sub(
    r"def afficher_hub_grid\(modules: list\[dict\]\):.*?def afficher_modules_fallback\(stats: dict\):",
    '''def afficher_hub_grid(modules: list[dict]):
    """Affiche une grille de modules."""
    st.markdown("#### 📂 Modules")
    if not modules:
        return
    cols = st.columns(3)
    for i, m in enumerate(modules):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{m['icon']} {m['title']}**")
                st.caption(m['subtitle'])
                if st.button("Ouvrir", key=f"btn_nav_{m['key']}", use_container_width=True):
                    from src.core.state import GestionnaireEtat, rerun
                    GestionnaireEtat.naviguer_vers(m["key"])
                    rerun()

def afficher_modules_fallback(stats: dict):''',
    text,
    flags=re.DOTALL,
)

with open(
    "d:/Projet_streamlit/assistant_matanne/src/modules/maison/hub/ui.py", "w", encoding="utf-8"
) as f:
    f.write(new_text)
