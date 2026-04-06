"""Commandes Telegram liées au module Maison (tâches, jardin, énergie, rappels)."""

from __future__ import annotations

import html
from datetime import date, datetime, timedelta

from ._helpers import _emoji_peremption, _extraire_mois_depuis_texte, _obtenir_url_app


async def _envoyer_taches_maison(chat_id: str) -> None:
    from src.services.integrations.telegram import envoyer_message_interactif, envoyer_message_telegram
    from src.services.maison import obtenir_service_contexte_maison

    taches = obtenir_service_contexte_maison().obtenir_taches_jour()
    if not taches:
        await envoyer_message_telegram(chat_id, "🏠 Aucune tâche maison prioritaire aujourd'hui.")
        return

    lignes = []
    for tache in taches[:6]:
        categorie = getattr(tache, "categorie", None) or "maison"
        nom = getattr(tache, "nom", None) or str(tache)
        lignes.append(f"• {html.escape(str(nom))} <i>({html.escape(str(categorie))})</i>")

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="🏠 <b>Tâches maison du jour</b>\n\n" + "\n".join(lignes),
        boutons=[
            {"id": "menu_maison", "title": "🏠 Menu Maison"},
            {"id": "menu_retour", "title": "🏠 Menu principal"},
        ],
    )


async def _envoyer_resume_jardin(chat_id: str) -> None:
    from src.core.db import obtenir_contexte_db
    from src.core.models.habitat import TacheEntretien
    from src.core.models.temps_entretien import PlanteJardin
    from src.services.integrations.telegram import envoyer_message_interactif, envoyer_message_telegram

    mois_courant = date.today().month
    mois_prochain = 1 if mois_courant == 12 else mois_courant + 1

    with obtenir_contexte_db() as session:
        taches = (
            session.query(TacheEntretien)
            .filter(TacheEntretien.categorie == "jardin", TacheEntretien.fait.is_(False))
            .order_by(TacheEntretien.prochaine_fois.asc(), TacheEntretien.id.asc())
            .limit(5)
            .all()
        )
        plantes = session.query(PlanteJardin).order_by(PlanteJardin.nom.asc()).limit(12).all()

    recoltes = [
        plante
        for plante in plantes
        if {mois_courant, mois_prochain} & _extraire_mois_depuis_texte(getattr(plante, "mois_recolte", None))
    ]

    if not taches and not recoltes:
        await envoyer_message_telegram(chat_id, "🌿 Aucun rappel jardin urgent pour le moment.")
        return

    lignes = ["🌿 <b>Jardin</b>"]
    if taches:
        lignes.append("")
        lignes.append("<b>Prochaines tâches</b>")
        for tache in taches[:4]:
            echeance = (
                tache.prochaine_fois.strftime('%d/%m')
                if getattr(tache, "prochaine_fois", None)
                else "à planifier"
            )
            lignes.append(f"• {html.escape(str(tache.nom))} — {echeance}")
    if recoltes:
        lignes.append("")
        lignes.append("<b>Récoltes proches</b>")
        for plante in recoltes[:4]:
            etat = getattr(plante, "etat", "bon")
            lignes.append(f"• {html.escape(str(plante.nom))} — état {html.escape(str(etat))}")

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"url": _obtenir_url_app("/maison/jardin"), "title": "🌿 Ouvrir le jardin"},
            {"id": "menu_maison", "title": "🏠 Menu Maison"},
        ],
    )


async def _envoyer_resume_energie(chat_id: str) -> None:
    from src.services.integrations.telegram import envoyer_message_interactif, envoyer_message_telegram
    from src.services.utilitaires import obtenir_energie_service

    totaux = obtenir_energie_service().totaux_annuels(date.today().year)
    if not totaux:
        await envoyer_message_telegram(chat_id, "⚡ Aucun relevé énergie disponible pour le moment.")
        return

    libelles = {
        "electricite": "⚡ Électricité",
        "gaz": "🔥 Gaz",
        "eau": "💧 Eau",
    }
    lignes = [f"⚡ <b>Énergie {date.today().year}</b>"]
    for type_energie, valeurs in sorted(totaux.items()):
        consommation = float(valeurs.get("total_consommation", 0) or 0)
        montant = float(valeurs.get("total_montant", 0) or 0)
        lignes.append(
            f"• {libelles.get(type_energie, type_energie.title())} : {consommation:g} — {montant:.2f}€"
        )

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"url": _obtenir_url_app("/maison/energie"), "title": "⚡ Ouvrir énergie"},
            {"id": "menu_maison", "title": "🏠 Menu Maison"},
        ],
    )


async def _envoyer_rappels_groupes(chat_id: str) -> None:
    from src.core.db import obtenir_contexte_db
    from src.core.models.habitat import TacheEntretien
    from src.core.models.inventaire import ArticleInventaire
    from src.core.models.utilitaires import NoteMemo
    from src.services.integrations.telegram import envoyer_message_interactif, envoyer_message_telegram

    aujourd_hui = date.today()
    maintenant = datetime.utcnow()

    with obtenir_contexte_db() as session:
        taches = (
            session.query(TacheEntretien)
            .filter(
                TacheEntretien.fait.is_(False),
                TacheEntretien.prochaine_fois.isnot(None),
                TacheEntretien.prochaine_fois <= aujourd_hui + timedelta(days=2),
            )
            .order_by(TacheEntretien.prochaine_fois.asc(), TacheEntretien.id.asc())
            .limit(4)
            .all()
        )
        peremptions = (
            session.query(ArticleInventaire)
            .filter(
                ArticleInventaire.quantite > 0,
                ArticleInventaire.date_peremption.isnot(None),
                ArticleInventaire.date_peremption <= aujourd_hui + timedelta(days=2),
            )
            .order_by(ArticleInventaire.date_peremption.asc(), ArticleInventaire.id.asc())
            .limit(4)
            .all()
        )
        notes = (
            session.query(NoteMemo)
            .filter(
                NoteMemo.archive.is_(False),
                NoteMemo.rappel_date.isnot(None),
                NoteMemo.rappel_date <= maintenant + timedelta(days=1),
            )
            .order_by(NoteMemo.rappel_date.asc(), NoteMemo.id.asc())
            .limit(3)
            .all()
        )

    if not taches and not peremptions and not notes:
        await envoyer_message_telegram(chat_id, "⏰ Aucun rappel en attente pour le moment.")
        return

    lignes = ["⏰ <b>Rappels en attente</b>"]
    if taches:
        lignes.append("")
        lignes.append("<b>Maison / entretien</b>")
        for tache in taches:
            date_label = tache.prochaine_fois.strftime('%d/%m') if tache.prochaine_fois else "bientôt"
            lignes.append(f"• {html.escape(str(tache.nom))} — {date_label}")
    if peremptions:
        lignes.append("")
        lignes.append("<b>Inventaire</b>")
        for article in peremptions:
            nom = getattr(article, "nom", None) or f"Article #{article.id}"
            date_label = article.date_peremption.strftime('%d/%m') if article.date_peremption else "sans date"
            lignes.append(f"• {html.escape(str(nom))} — {date_label}")
    if notes:
        lignes.append("")
        lignes.append("<b>Notes & pense-bêtes</b>")
        for note in notes:
            date_label = note.rappel_date.strftime('%d/%m %H:%M') if note.rappel_date else "à voir"
            lignes.append(f"• {html.escape(str(note.titre))} — {date_label}")

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=[
            {"id": "action_maison", "title": "🏠 Tâches maison"},
            {"id": "action_inventaire", "title": "🥫 Inventaire"},
            {"url": _obtenir_url_app("/outils/notes"), "title": "📝 Ouvrir les notes"},
        ],
    )


async def _envoyer_taches_projets(chat_id: str) -> None:
    """Envoie la liste des tâches de projet à faire, avec boutons valider/reporter."""
    from src.core.db import obtenir_contexte_db
    from src.core.models.maison import TacheProjet
    from src.services.integrations.telegram import envoyer_message_interactif, envoyer_message_telegram

    with obtenir_contexte_db() as session:
        taches = (
            session.query(TacheProjet)
            .filter(TacheProjet.statut == "à_faire")
            .order_by(TacheProjet.date_echeance.asc().nullsfirst(), TacheProjet.id.asc())
            .limit(5)
            .all()
        )
        donnees = [
            {
                "id": t.id,
                "nom": t.nom,
                "echeance": t.date_echeance.strftime("%d/%m") if t.date_echeance else None,
                "priorite": t.priorite,
            }
            for t in taches
        ]

    if not donnees:
        await envoyer_message_telegram(chat_id, "✅ Aucune tâche en attente pour le moment.")
        return

    emojis_priorite = {"haute": "🔴", "moyenne": "🟡", "basse": "🟢"}
    lignes = ["📋 <b>Tâches à faire</b>", ""]
    for tache in donnees:
        echeance = f" — {tache['echeance']}" if tache.get("echeance") else ""
        emoji = emojis_priorite.get(tache["priorite"], "")
        lignes.append(f"{emoji} {html.escape(str(tache['nom']))}{echeance}")

    # Boutons par tâche (max 3 tâches pour garder l'interface lisible)
    boutons = []
    for tache in donnees[:3]:
        nom_court = tache["nom"][:18]
        boutons.append({"id": f"tache_valider:{tache['id']}", "title": f"✅ {nom_court}"})
        boutons.append({"id": f"tache_reporter:{tache['id']}", "title": "🔄 Reporter"})
    boutons.append({"id": "action_maison", "title": "🏠 Menu Maison"})

    await envoyer_message_interactif(
        destinataire=chat_id,
        corps="\n".join(lignes),
        boutons=boutons,
    )
