# 🤖 Assistant MaTanne v2

Assistant familial intelligent avec IA Mistral - Déployé sur Streamlit Cloud + Supabase

## 🚀 Stack Technique

- **Frontend**: Streamlit
- **Base de données**: Supabase (PostgreSQL)
- **IA**: Mistral AI API
- **Hébergement**: Streamlit Cloud

## 📦 Installation locale (développement)

### Prérequis

- Python 3.11+
- Compte Supabase (gratuit)
- Clé API Mistral

### Installation

```bash
# 1. Cloner le repo
git clone https://github.com/ton-compte/assistant-matanne-v2
cd assistant-matanne-v2

# 2. Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Installer dépendances
pip install -r requirements.txt

# 4. Configurer secrets
# Créer .streamlit/secrets.toml avec tes identifiants

# 5. Lancer l'app
streamlit run src/app.py
```

## 🔧 Configuration Secrets

### Local (`.streamlit/secrets.toml`)

```toml
[db]
host = "db.xxxxx.supabase.co"
port = "5432"
name = "postgres"
user = "postgres"
password = "ton_mot_de_passe"

[mistral]
api_key = "ta_cle_api_mistral"
```

### Streamlit Cloud

1. Va dans **Settings** > **Secrets**
2. Copie le contenu ci-dessus
3. Remplace par tes vrais identifiants

## 🗄️ Base de données Supabase

### Initialiser le schéma

```bash
# Appliquer les migrations
alembic upgrade head
```

### Créer la base manuellement

Si besoin, exécute dans l'éditeur SQL de Supabase :

```sql
-- Voir alembic/versions/001_initial_schema.py
```

## 🎯 Fonctionnalités

### 🍲 Cuisine
- Suggestions recettes par IA
- Gestion inventaire
- Batch cooking
- Liste de courses optimisée

### 👶 Famille
- Suivi développement Jules
- Analyse bien-être
- Routines quotidiennes

### 🏡 Maison
- Gestion projets
- Jardin intelligent
- Planning entretien

### 📅 Planning
- Calendrier unifié
- Vue d'ensemble

## 🧪 Tests

```bash
# Lancer les tests
pytest

# Avec couverture
pytest --cov=src
```

## 📚 Structure du projet

```
assistant-matanne-v2/
├── src/
│   ├── app.py              # Point d'entrée
│   ├── core/
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # Connexion Supabase
│   │   ├── models.py       # Modèles SQLAlchemy
│   │   └── ai_agent.py     # Agent Mistral IA
│   └── modules/
│       ├── cuisine/
│       ├── famille/
│       ├── maison/
│       └── planning/
├── alembic/                # Migrations DB
├── tests/
├── .streamlit/
│   └── secrets.toml        # Secrets (local)
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 🚢 Déploiement Streamlit Cloud

1. **Push sur GitHub**
   ```bash
   git add .
   git commit -m "Deploy"
   git push
   ```

2. **Connecter à Streamlit Cloud**
    - Va sur [share.streamlit.io](https://share.streamlit.io)
    - Sélectionne ton repo
    - Branche : `main`
    - Fichier : `src/app.py`

3. **Configurer les secrets**
    - Dans **Settings** > **Secrets**
    - Colle tes identifiants Supabase et Mistral

4. **Déployer !**

## 🔑 Obtenir les clés API

### Supabase (gratuit)
1. Crée un compte sur [supabase.com](https://supabase.com)
2. Crée un nouveau projet
3. Va dans **Settings** > **Database**
4. Copie les infos de connexion

### Mistral AI
1. Crée un compte sur [console.mistral.ai](https://console.mistral.ai)
2. Va dans **API Keys**
3. Crée une nouvelle clé
4. Choisis le modèle `mistral-small` (économique)

## 📝 Migrations Alembic

```bash
# Créer une nouvelle migration
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🐛 Dépannage

### Erreur connexion Supabase
- Vérifie que le host commence par `db.`
- Vérifie le mot de passe
- Active SSL (`?sslmode=require`)

### Erreur Mistral API
- Vérifie la clé API
- Vérifie le quota (gratuit limité)

### Secrets non trouvés
- Vérifie `.streamlit/secrets.toml` (local)
- Vérifie les secrets dans Streamlit Cloud

## 📄 Licence

MIT

## 👨‍💻 Auteur

Anne - Assistant Familial Intelligent