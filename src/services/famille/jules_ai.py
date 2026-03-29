"""
Service IA pour suggestions Jules (développement enfant).

Déplacé depuis src/modules/famille/jules/ai_service.py vers la couche services.
"""

from typing import Literal
from pydantic import BaseModel, Field

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory


# ── Modèles Pydantic pour suggestions structurées ──


class SuggestionActivite(BaseModel):
    """Modèle pour une suggestion d'activité structurée"""

    nom: str = Field(..., description="Nom de l'activité")
    description: str = Field(..., description="Description courte de l'activité")
    duree_minutes: int = Field(..., ge=5, le=180, description="Durée estimée en minutes")
    budget: float = Field(..., ge=0, description="Budget estimé en euros")
    lieu: Literal["interieur", "exterieur", "mixte"] = Field(
        ..., description="Lieu de l'activité"
    )
    competences: list[str] = Field(..., description="Compétences développées")
    materiel: list[str] = Field(default_factory=list, description="Matériel nécessaire")
    niveau_effort: Literal["faible", "moyen", "eleve"] = Field(
        ..., description="Niveau d'effort physique"
    )
    adapte_pour: list[int] = Field(
        ..., description="Tranche d'âge en mois (ex: [12, 24] = 12-24 mois)"
    )


class JulesAIService(BaseAIService):
    """Service IA pour suggestions Jules.

    Note (S12): Hérite de BaseAIService uniquement. Les données DB sont
    gérées côté module, ce service est purement IA/read-heavy.
    """

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="jules",
            default_ttl=7200,
            service_name="jules_ai",
        )

    async def suggerer_activites(self, age_mois: int, meteo: str = "intérieur", nb: int = 3) -> str:
        """Suggère des activités adaptées à l'âge"""
        prompt = f"""Pour un enfant de {age_mois} mois, suggère {nb} activités {meteo}.

Format pour chaque activité:
🎯 [Nom de l'activité]
⏱️ Durée: X min
📝 Description: Une phrase
⏰ Bénéfice: Ce que ça développe

Activités adaptées à cet âge, stimulantes et réalisables à la maison."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en développement de la petite enfance. Réponds en français.",
            max_tokens=600,
        )

    async def conseil_developpement(self, age_mois: int, theme: str) -> str:
        """Donne un conseil sur un thème de développement"""
        themes_detail = {
            "proprete": "l'apprentissage de la propreté et du pot",
            "sommeil": "le sommeil et les routines du coucher",
            "alimentation": "l'alimentation et l'autonomie à table",
            "langage": "le développement du langage et la parole",
            "motricite": "la motricité (marche, coordination, équilibre)",
            "social": "le développement social et la gestion des émotions",
        }

        detail = themes_detail.get(theme, theme)

        prompt = f"""Pour un enfant de {age_mois} mois, donne des conseils pratiques sur {detail}.

Inclure:
1. Ce qui est normal à cet âge
2. 3 conseils pratiques
3. Ce qu'il faut éviter
4. Quand consulter si besoin

Ton bienveillant, rassurant et pratique."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es pédiatre et expert en développement de l'enfant. Réponds en français de manière concise.",
            max_tokens=700,
        )

    async def suggerer_jouets(self, age_mois: int, budget: int = 30) -> str:
        """Suggère des jouets adaptés à l'âge"""
        prompt = f"""Pour un enfant de {age_mois} mois, suggère 5 jouets éducatifs avec un budget de {budget}€ max par jouet.

Format:
🎁 [Nom du jouet]
💰 Prix estimé: X€
🎯 Développe: [compétence]
📝 Pourquoi: Une phrase

Jouets sûrs, éducatifs et adaptés à cet âge."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en jouets éducatifs pour enfants. Réponds en français.",
            max_tokens=600,
        )

    # ── Méthodes streaming ──

    def stream_activites(self, age_mois: int, meteo: str = "intérieur", nb: int = 3):
        """Streaming de suggestions d'activités."""
        prompt = f"""Pour un enfant de {age_mois} mois, suggère {nb} activités {meteo}.

Format pour chaque activité:
🎯 [Nom de l'activité]
⏱️ Durée: X min
📝 Description: Une phrase
⏰ Bénéfice: Ce que ça développe

Activités adaptées à cet âge, stimulantes et réalisables à la maison."""

        return self.call_with_streaming_sync(
            prompt=prompt,
            system_prompt="Tu es expert en développement de la petite enfance. Réponds en français.",
            max_tokens=600,
        )

    def stream_conseil(self, age_mois: int, theme: str):
        """Streaming de conseils développement."""
        themes_detail = {
            "proprete": "l'apprentissage de la propreté et du pot",
            "sommeil": "le sommeil et les routines du coucher",
            "alimentation": "l'alimentation et l'autonomie à table",
            "langage": "le développement du langage et la parole",
            "motricite": "la motricité (marche, coordination, équilibre)",
            "social": "le développement social et la gestion des émotions",
        }
        detail = themes_detail.get(theme, theme)

        prompt = f"""Pour un enfant de {age_mois} mois, donne des conseils pratiques sur {detail}.

Inclure:
1. Ce qui est normal à cet âge
2. 3 conseils pratiques
3. Ce qu'il faut éviter
4. Quand consulter si besoin

Ton bienveillant, rassurant et pratique."""

        return self.call_with_streaming_sync(
            prompt=prompt,
            system_prompt="Tu es pédiatre et expert en développement de l'enfant. Réponds en français de manière concise.",
            max_tokens=700,
        )

    def stream_jouets(self, age_mois: int, budget: int = 30):
        """Streaming de suggestions jouets."""
        prompt = f"""Pour un enfant de {age_mois} mois, suggère 5 jouets éducatifs avec un budget de {budget}€ max par jouet.

Format:
🎁 [Nom du jouet]
💰 Prix estimé: X€
🎯 Développe: [compétence]
📝 Pourquoi: Une phrase

Jouets sûrs, éducatifs et adaptés à cet âge."""

        return self.call_with_streaming_sync(
            prompt=prompt,
            system_prompt="Tu es expert en jouets éducatifs pour enfants. Réponds en français.",
            max_tokens=600,
        )

    def suggerer_activites_enrichies(
        self,
        age_mois: int,
        meteo: str = "interieur",
        budget_max: float = 50.0,
        duree_min: int = 30,
        duree_max: int = 120,
        preferences: list[str] | None = None,
        nb_suggestions: int = 5,
    ) -> list[SuggestionActivite]:
        """
        Suggère des activités enrichies avec paramètres avancés.
        
        Args:
            age_mois: Âge de l'enfant en mois
            meteo: Type de météo ("pluie", "soleil", "nuageux", "mixte")
            budget_max: Budget maximum par activité en euros
            duree_min: Durée minimum souhaitée en minutes
            duree_max: Durée maximum souhaitée en minutes
            preferences: Tags de préférences (ex: ["creatif", "sportif", "educatif"])
            nb_suggestions: Nombre de suggestions à retourner
            
        Returns:
            Liste de suggestions d'activités structurées
        """
        # Mapping météo vers lieu
        lieu_mapping = {
            "pluie": "interieur",
            "soleil": "exterieur",
            "nuageux": "mixte",
            "mixte": "mixte",
            "interieur": "interieur",
            "exterieur": "exterieur",
        }
        lieu = lieu_mapping.get(meteo.lower(), "mixte")

        # Construction prompt enrichi
        preferences_text = (
            f"Préférences: {', '.join(preferences)}"
            if preferences
            else "Variété d'activités (créatif, sportif, éducatif, sensoriel)"
        )

        prompt = f"""Suggère {nb_suggestions} activités pour un enfant de {age_mois} mois.

Contraintes:
- Lieu: {lieu}
- Budget max par activité: {budget_max}€
- Durée: entre {duree_min} et {duree_max} minutes
- {preferences_text}

Pour chaque activité, fournis:
- nom: titre accrocheur et clair
- description: 1-2 phrases sur comment faire l'activité
- duree_minutes: durée estimée réaliste
- budget: coût estimé (0 si gratuit/matériel déjà présent)
- lieu: "interieur", "exterieur" ou "mixte"
- competences: liste des compétences développées (motricité fine, langage, créativité, etc.)
- materiel: liste du matériel nécessaire
- niveau_effort: "faible", "moyen" ou "eleve" (effort physique requis)
- adapte_pour: tranche d'âge en mois [min, max]

Activités adaptées à cet âge, sûres, stimulantes et faciles à réaliser."""

        system_prompt = """Tu es expert en développement de la petite enfance et activités Montessori. 
Réponds UNIQUEMENT avec du JSON valide, sans markdown ni texte supplémentaire.
Assure-toi que les activités sont sécuritaires, adaptées à l'âge et faciles à mettre en place."""

        return self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=SuggestionActivite,
            system_prompt=system_prompt,
            max_tokens=2000,
        )

    def generer_coaching_hebdo(
        self,
        age_mois: int,
        jalons_recents: list[str] | None = None,
        preoccupations: list[str] | None = None,
    ) -> str:
        """Génère un bilan de coaching hebdomadaire pour Jules (CT-05).

        Retourne un texte personnalisé avec:
        - Bilan du développement à l'âge actuel
        - 3 activités à privilégier cette semaine
        - Conseil alimentation de la semaine
        - Point vigilance / rappel santé

        Args:
            age_mois: Âge de Jules en mois
            jalons_recents: Jalons atteints récemment (optionnel)
            preoccupations: Préoccupations parentales de la semaine (optionnel)

        Returns:
            Texte de coaching hebdomadaire formaté
        """
        jalons_txt = (
            f"\nJalons récents atteints : {', '.join(jalons_recents)}"
            if jalons_recents
            else ""
        )
        preoc_txt = (
            f"\nPréoccupations parentales : {', '.join(preoccupations)}"
            if preoccupations
            else ""
        )

        prompt = f"""Jules a {age_mois} mois aujourd'hui.{jalons_txt}{preoc_txt}

Génère un coaching hebdomadaire personnalisé avec ces 4 sections :

## 🌱 Bilan développement
Ce qui est attendu / normal à {age_mois} mois. Ce que Jules fait probablement maintenant.

## 🎯 3 activités de la semaine
Des activités concrètes adaptées à {age_mois} mois. Chaque activité : nom + description courte (1 ligne) + bénéfice.

## 🥣 Conseil alimentation
Un conseil pratique sur l'alimentation à {age_mois} mois (diversification, textures, portions, aliments à introduire).

## ⚠️ Point vigilance
Un rappel santé ou sécurité important pour cette tranche d'âge.

Ton bienveillant, positif et pratique. Tutoie les parents (vous êtes parents de Jules)."""

        return self.call_with_streaming_sync(
            prompt=prompt,
            system_prompt="Tu es pédiatre et coach parental expert. Réponds en français de manière chaleureuse et concrète.",
            max_tokens=900,
        )


@service_factory("jules_ai", tags={"famille", "ia", "enfant"})
def obtenir_jules_ai_service() -> JulesAIService:
    """Factory singleton pour JulesAIService."""
    return JulesAIService()


# Alias anglais
def obtenir_jules_ai_service() -> JulesAIService:
    """English alias for obtenir_jules_ai_service."""
    return obtenir_jules_ai_service()


# ─── Aliases rétrocompatibilité (Sprint 12 A3) ───────────────────────────────
get_jules_ai_service = obtenir_jules_ai_service  # alias rétrocompatibilité Sprint 12 A3
