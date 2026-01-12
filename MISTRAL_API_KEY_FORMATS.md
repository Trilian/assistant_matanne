# 🔐 Formats de clés API Mistral

## ✅ Tous les formats sont acceptés

Le code **accepte n'importe quel format de clé API Mistral**. 

Voici quelques exemples de clés valides:

```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
msk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
mv_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
x_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
...
```

## 🤔 Pourquoi différents formats?

Mistral utilise différents préfixes selon:
- Le type de compte
- La date de création de la clé
- La région
- L'API utilisée

**C'est complètement normal!**

## 📋 Comment identifier votre clé

1. **Allez sur** https://console.mistral.ai/
2. **Connectez-vous** avec vos identifiants
3. **API Keys** (menu gauche)
4. **+ Create API Key** ou voir vos clés existantes
5. **Copiez la clé complète** (elle commence par un préfixe, peu importe lequel)

Exemple de console Mistral:
```
Key Name: my-api-key
Key: msk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Copiez le texte `msk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx` (ou quel que soit votre préfixe)

## ✨ Utilisation dans votre app

### Option 1: Fichier `.env.local`

```bash
# .env.local
MISTRAL_API_KEY="msk_votre_clé_complète"
```

### Option 2: Streamlit Cloud

```toml
# Dans Settings → Secrets
[mistral]
api_key = "msk_votre_clé_complète"
```

### Option 3: Variable d'environnement

```bash
export MISTRAL_API_KEY="msk_votre_clé_complète"
```

## 🚨 Points importants

- ✅ **La clé fonctionne** quel que soit son préfixe
- ✅ **Copiez-collez intégralement** (ne supprimez rien)
- ✅ **Gardez les espaces** (s'il y en a)
- 🚫 **Ne modifiez PAS** le format
- 🚫 **Ne supprimez PAS** le préfixe
- 🚫 **Ne partagez JAMAIS** votre clé

## 🧪 Vérifier votre clé

Pour tester si votre clé fonctionne:

```bash
python check_mistral_config.py
```

Vous devriez voir:
```
✅ MISTRAL_API_KEY: msk_xxxxxxxxxxxx...
✅ Configuration OK
```

## ❓ FAQ

**Q: Ma clé commence par `msk_` au lieu de `sk-`, c'est un problème?**
R: Non, c'est normal! Mistral utilise différents préfixes.

**Q: Je dois modifier le préfixe?**
R: Non! Utilisez la clé exactement comme donnée par console.mistral.ai

**Q: La clé change selon mon région?**
R: Le format peut varier, mais c'est toujours valide.

**Q: Quel format est "meilleur"?**
R: Tous les formats fonctionnent exactement pareil.

---

**Créé:** 2026-01-12
**Version:** 1.0
