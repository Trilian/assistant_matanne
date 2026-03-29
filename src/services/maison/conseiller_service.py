"""
ConseillierMaisonService — Conseils IA contextuels par section.

Génère des conseils personnalisés en agrégeant les données de chaque section
(travaux, finances, provisions, jardin, documents, équipements) et en interrogeant
Mistral pour formuler 3-5 conseils actionnables et pertinents.
"""

import logging
from typing import Any

from src.core.ai import ClientIA, obtenir_client_ia
from src.core.decorators import avec_cache, avec_gestion_erreurs
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


PROMPTS_SECTION: dict[str, str] = {
    "travaux": (
        "Tu es un expert en gestion de travaux domestiques. "
        "Donne 3 à 5 conseils pratiques et actionnables pour prioriser les travaux, "
        "planifier l'entretien et choisir les bons artisans. Sois concis et direct."
    ),
    "finances": (
        "Tu es un conseiller financier pour la maison. "
        "Donne 3 à 5 conseils pour optimiser les charges, réduire les dépenses "
        "et maîtriser la consommation d'énergie. Sois concis et direct."
    ),
    "provisions": (
        "Tu es un expert en gestion des stocks alimentaires et ménagers. "
        "Donne 3 à 5 conseils pour gérer le cellier, éviter le gaspillage, "
        "optimiser les achats et gérer les dates de péremption. Sois concis et direct."
    ),
    "jardin": (
        "Tu es un jardinier expert. "
        "Donne 3 à 5 conseils saisonniers pratiques pour entretenir le jardin, "
        "planter et adopter des pratiques éco-responsables. Sois concis et direct."
    ),
    "documents": (
        "Tu es un expert en gestion administrative immobilière. "
        "Donne 3 à 5 conseils pour gérer les contrats, surveiller les dates d'expiration, "
        "maintenir les diagnostics à jour et optimiser les assurances. Sois concis et direct."
    ),
    "equipements": (
        "Tu es un expert en équipements domestiques et domotique. "
        "Donne 3 à 5 conseils pour gérer les garanties, entretenir les appareils "
        "et optimiser la domotique. Sois concis et direct."
    ),
    "default": (
        "Tu es un assistant maison polyvalent. "
        "Donne 3 à 5 conseils pratiques et actionnables pour bien gérer sa maison. "
        "Sois concis et direct."
    ),
}


class ConseillierMaisonService(BaseAIService):
    """Génère des conseils IA contextuels par section Maison."""

    def __init__(self, client: ClientIA | None = None) -> None:
        if client is None:
            client = obtenir_client_ia()
        super().__init__(
            client=client,
            cache_prefix="conseiller_maison",
            default_ttl=600,
            service_name="conseiller_maison",
        )

    @avec_cache(ttl=600)
    @avec_gestion_erreurs(default_return=None)
    def obtenir_conseil(self, section: str) -> dict[str, Any]:
        """Retourne 3-5 conseils IA pour la section demandée.

        Args:
            section: Nom de la section (travaux, finances, provisions, etc.)

        Returns:
            dict avec clés: section, conseils (liste), message
        """
        prompt_systeme = PROMPTS_SECTION.get(section.lower(), PROMPTS_SECTION["default"])
        prompt_utilisateur = (
            f"Génère exactement 3 à 5 conseils courts et actionnables "
            f"pour la section '{section}' d'une application de gestion de maison familiale. "
            f"Retourne UNIQUEMENT une liste JSON de chaînes de texte, sans aucun autre texte. "
            f"Exemple: [\"Conseil 1\", \"Conseil 2\", \"Conseil 3\"]"
        )

        try:
            import json as _json
            # Appel IA synchrone via la version auto-générée par sync_wrapper
            reponse_brute: str | None = self.call_with_cache_sync(  # type: ignore[attr-defined]
                prompt=prompt_utilisateur,
                system_prompt=prompt_systeme,
                temperature=0.7,
                max_tokens=500,
                use_cache=True,
            )
            if not reponse_brute:
                raise ValueError("Réponse IA vide")

            # Tenter de parser comme JSON
            contenu = reponse_brute.strip()
            # Extraire le tableau JSON si entouré de texte
            debut = contenu.find("[")
            fin = contenu.rfind("]") + 1
            if debut >= 0 and fin > debut:
                contenu = contenu[debut:fin]
            conseils: list[str] = _json.loads(contenu)
            if not isinstance(conseils, list):
                raise ValueError("Format inattendu")
        except Exception as exc:
            logger.warning("Erreur IA ConseillierMaison pour '%s': %s", section, exc)
            conseils = _conseils_fallback(section)

        return {
            "section": section,
            "conseils": [str(c) for c in conseils[:5]],
            "message": f"Conseils pour la section {section}",
        }

    @avec_cache(ttl=7200)
    @avec_gestion_erreurs(default_return=None)
    def obtenir_conseils_hub(self) -> list[dict[str, Any]]:
        """Génère 3-6 conseils structurés pour le hub maison, triés par urgence.

        Appelle Mistral avec contexte maison complet et demande un JSON structuré.

        Returns:
            Liste de ConseilMaison dicts (titre, description, niveau, module_source, action_type, action_payload, icone)
        """
        prompt_systeme = (
            "Tu es un assistant intelligent spécialisé dans la gestion de la maison familiale. "
            "Tu génères des conseils actionnables, pratiques et priorisés. "
            "Réponds impérativement en français."
        )
        prompt_utilisateur = (
            "Génère exactement 4 conseils actionnables pour le hub de gestion de maison familiale. "
            "Retourne UNIQUEMENT un tableau JSON avec ces 4 objets, sans aucun autre texte. "
            "Chaque objet doit avoir ces champs: "
            "titre (string court ≤40 chars), "
            "description (string ≤80 chars), "
            "niveau (string: 'urgent' | 'warning' | 'info'), "
            "module_source (string: 'travaux' | 'finances' | 'provisions' | 'jardin' | 'documents' | 'equipements' | 'menage'), "
            "action_type (string: 'voir' | 'planifier_entretien' | 'acheter'), "
            "action_payload (object: {chemin?:string, nom?:string, categorie?:string}). "
            "Inclure au moins 1 conseil 'urgent', 1 'warning' et 2 'info'. "
            'Exemple: [{"titre":"Vérifier filtre chaudière","description":"La révision annuelle est recommandée avant l\'hiver",'
            '"niveau":"warning","module_source":"travaux","action_type":"planifier_entretien",'
            '"action_payload":{"nom":"Révision chaudière","categorie":"chauffage"}}]'
        )

        import json as _json
        try:
            reponse_brute: str | None = self.call_with_cache_sync(  # type: ignore[attr-defined]
                prompt=prompt_utilisateur,
                system_prompt=prompt_systeme,
                temperature=0.5,
                max_tokens=800,
                use_cache=True,
            )
            if not reponse_brute:
                raise ValueError("Réponse IA vide")
            contenu = reponse_brute.strip()
            debut = contenu.find("[")
            fin = contenu.rfind("]") + 1
            if debut >= 0 and fin > debut:
                contenu = contenu[debut:fin]
            conseils = _json.loads(contenu)
            if not isinstance(conseils, list):
                raise ValueError("Format inattendu")
            # Valider et nettoyer les champs
            niveaux_valides = {"info", "warning", "urgent"}
            actions_valides = {"voir", "planifier_entretien", "acheter"}
            result = []
            for c in conseils[:6]:
                if not isinstance(c, dict) or not c.get("titre"):
                    continue
                result.append({
                    "titre": str(c.get("titre", ""))[:60],
                    "description": str(c.get("description", ""))[:120],
                    "niveau": c.get("niveau", "info") if c.get("niveau") in niveaux_valides else "info",
                    "module_source": str(c.get("module_source", "general")),
                    "action_type": c.get("action_type", "voir") if c.get("action_type") in actions_valides else "voir",
                    "action_payload": c.get("action_payload") if isinstance(c.get("action_payload"), dict) else {},
                    "icone": str(c.get("icone", "")),
                })
            if result:
                return result
            raise ValueError("Aucun conseil valide")
        except Exception as exc:
            logger.warning("Erreur IA ConseillierMaison hub: %s", exc)
            return _conseils_hub_fallback()

    def chat_assistant(self, message: str, contexte: str = "maison") -> str:
        """Répond à une question libre dans le contexte maison.

        Args:
            message: Question de l'utilisateur.
            contexte: Contexte pour le système (défaut: "maison").

        Returns:
            Texte de la réponse IA.
        """
        prompt_systeme = (
            "Tu es un assistant intelligent spécialisé dans la gestion de la maison. "
            "Tu aides avec les travaux, les finances, les provisions, le jardin, "
            "les contrats et les équipements. "
            "Tes réponses sont courtes, précises et actionnables. "
            "Réponds impérativement en français."
        )
        try:
            reponse: str | None = self.call_with_cache_sync(  # type: ignore[attr-defined]
                prompt=message,
                system_prompt=prompt_systeme,
                temperature=0.6,
                max_tokens=400,
                use_cache=False,  # Pas de cache pour le chat interactif
            )
            return reponse or "Désolé, je ne peux pas répondre pour le moment."
        except Exception as exc:
            logger.warning("Erreur IA chat_assistant: %s", exc)
            return "Désolé, je ne peux pas répondre pour le moment. Veuillez réessayer."

    def auto_completer(
        self, champ_nom: str, valeur_partielle: str, contexte_page: str = "general"
    ) -> dict[str, Any]:
        """Suggère des complétions contextuelles pour un champ de formulaire.

        Args:
            champ_nom: Nom du champ (ex: nom, description, categorie)
            valeur_partielle: Valeur partielle saisie par l'utilisateur
            contexte_page: Page de contexte (ex: travaux, menage, jardin)

        Returns:
            dict avec suggestions: {categorie, description, tags}
        """
        import json as _json

        prompt = (
            f"Pour un champ '{champ_nom}' sur la page '{contexte_page}' d'une application de gestion de maison, "
            f"l'utilisateur a saisi: '{valeur_partielle}'. "
            f"Suggère une catégorie, une description courte et 3 tags pertinents. "
            f"Réponds UNIQUEMENT en JSON: "
            f'{{\"categorie\": \"...\", \"description\": \"...\", \"tags\": [\"...\", \"...\", \"...\"]}}'
        )
        try:
            reponse = self.chat_assistant(prompt, contexte="auto-completion")
            debut = reponse.find("{")
            fin = reponse.rfind("}") + 1
            if debut >= 0 and fin > debut:
                parsed = _json.loads(reponse[debut:fin])
                return {
                    "categorie": parsed.get("categorie"),
                    "description": parsed.get("description"),
                    "tags": parsed.get("tags", []),
                }
        except Exception as exc:
            logger.warning("Erreur auto_completer: %s", exc)
        return {"categorie": None, "description": None, "tags": []}


def _conseils_hub_fallback() -> list[dict]:
    """Conseils de secours structurés pour le hub en cas de panne IA."""
    return [
        {
            "titre": "Vérifier les contrats d'énergie",
            "description": "Comparez vos offres chaque année pour réduire vos charges",
            "niveau": "warning",
            "module_source": "finances",
            "action_type": "voir",
            "action_payload": {"chemin": "/maison/finances?tab=charges"},
            "icone": "💰",
        },
        {
            "titre": "Contrôle des stocks alimentaires",
            "description": "Inventoriez les produits proches de leur date de péremption",
            "niveau": "info",
            "module_source": "provisions",
            "action_type": "voir",
            "action_payload": {"chemin": "/maison/provisions?tab=cellier"},
            "icone": "📦",
        },
        {
            "titre": "Entretien préventif recommandé",
            "description": "Planifiez une inspection de votre installation électrique",
            "niveau": "warning",
            "module_source": "travaux",
            "action_type": "planifier_entretien",
            "action_payload": {"nom": "Inspection électrique", "categorie": "electricite"},
            "icone": "🔧",
        },
        {
            "titre": "Tâches jardin de saison",
            "description": "Consultez le calendrier des semis pour le mois en cours",
            "niveau": "info",
            "module_source": "jardin",
            "action_type": "voir",
            "action_payload": {"chemin": "/maison/jardin?tab=semis"},
            "icone": "🌱",
        },
    ]


def _conseils_fallback(section: str) -> list[str]:
    """Conseils de secours statiques en cas de panne IA."""
    fallbacks: dict[str, list[str]] = {
        "travaux": [
            "Planifiez vos travaux en dehors des périodes de forte demande.",
            "Demandez au moins 3 devis comparatifs avant de choisir un artisan.",
            "Priorisez les travaux d'entretien préventif pour éviter les urgences.",
        ],
        "finances": [
            "Comparez vos contrats d'énergie chaque année.",
            "Relevez vos compteurs mensuellement pour détecter les anomalies.",
            "Constituez une réserve de 1 à 3 mois de charges pour les imprévus.",
        ],
        "provisions": [
            "Faites un inventaire hebdomadaire pour réduire le gaspillage.",
            "Rangez les aliments selon la règle FIFO (premier entré, premier sorti).",
            "Planifiez vos menus à l'avance pour optimiser vos achats.",
        ],
        "jardin": [
            "Adaptez l'arrosage à la saison et à la météo locale.",
            "Composez vos déchets verts pour enrichir le sol naturellement.",
            "Plantez des espèces locales résistantes à la sécheresse.",
        ],
        "documents": [
            "Vérifiez les dates d'expiration de vos contrats chaque trimestre.",
            "Gardez des copies numériques de tous vos diagnostics.",
            "Renégociez vos assurances tous les 2 ans.",
        ],
        "equipements": [
            "Conservez les manuels et preuves d'achat pour toutes les garanties.",
            "Planifiez une révision annuelle des appareils de chauffage.",
            "Mettez à jour le firmware de vos appareils domotiques régulièrement.",
        ],
    }
    return fallbacks.get(section.lower(), [
        "Organisez régulièrement votre espace pour gagner en efficacité.",
        "Anticipez les dépenses annuelles pour mieux budgétiser.",
        "Créez des routines de maintenance préventive.",
    ])


@service_factory("conseiller_maison")
def obtenir_conseiller_maison_service() -> ConseillierMaisonService:
    """Retourne l'instance singleton du service conseiller IA."""
    return ConseillierMaisonService()


# ─── Aliases rétrocompatibilité (Sprint 12 A3) ───────────────────────────────
get_conseiller_maison_service = obtenir_conseiller_maison_service  # alias rétrocompatibilité Sprint 12 A3
