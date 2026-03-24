# 🎬 Video Walkthroughs

Documentation des démos vidéo des fonctionnalités clés d'Assistant Matanne.

## 📹 Vidéos disponibles

### 🍳 Cuisine

| Vidéo                                   | Durée | Description                       |
| --------------------------------------- | ----- | --------------------------------- |
| [Batch Cooking Complet](#batch-cooking) | 5 min | Session complète de batch cooking |
| [Planification Repas](#planification)   | 3 min | Créer un planning hebdomadaire    |
| [Gestion Inventaire](#inventaire)       | 2 min | Gérer son stock                   |

### 🛠️ Innovations Sprint 11

| Vidéo                             | Durée | Description                 |
| --------------------------------- | ----- | --------------------------- |
| [Exécution Live](#execution-live) | 4 min | st.status() en action       |
| [Commandes Vocales](#vocal)       | 2 min | Ajouter articles à la voix  |
| [Scanner WebRTC](#scanner)        | 2 min | Scanner codes-barres webcam |

---

## 🍳 Batch Cooking {#batch-cooking}

### Contenu de la vidéo

1. **Introduction** (0:00-0:30)
   - Présentation du module
   - Avantages du batch cooking

2. **Préparation** (0:30-1:30)
   - Sélection du type de session
   - Choix de la date et heure
   - Vérification du planning

3. **Génération IA** (1:30-2:30)
   - Clic sur "Générer les instructions"
   - Explication des étapes générées
   - Conseils d'organisation

4. **Session de cuisson** (2:30-4:00)
   - Timeline des étapes
   - Moments Jules
   - Recettes détaillées

5. **Finitions** (4:00-5:00)
   - Instructions jour J
   - Stockage des préparations

### Points clés montrés

- ✅ Génération des instructions en 1 clic
- ✅ Timeline optimisée par l'IA
- ✅ Export PDF des instructions
- ✅ Liste de courses automatique

---

## 🎬 Exécution Live {#execution-live}

### Contenu de la vidéo

1. **Introduction** (0:00-0:30)
   - Nouvelle fonctionnalité st.status()
   - Suivi en temps réel

2. **Démarrage** (0:30-1:00)
   - Bouton "Démarrer le Batch Cooking"
   - Métrique de progression

3. **Phases d'exécution** (1:00-3:00)
   - Phase 1: Préparation (vérification ingrédients)
   - Phase 2: Cuisson (barres de progression par étape)
   - Phase 3: Stockage

4. **Conclusion** (3:00-4:00)
   - Résumé final
   - Métriques de la session

### Code démontré

```python
with st.status("🍳 Batch Cooking en cours...", expanded=True) as status:
    # Phase 1
    status.update(label="📋 Phase 1: Préparation", state="running")
    st.write("✅ Ingrédients prêts")

    # Phase 2
    for etape in etapes:
        status.update(label=f"👩‍🍳 Étape {i}/{total}", state="running")
        st.progress(progression)

    # Terminé
    status.update(label="✅ Terminé!", state="complete")
```

---

## 🎤 Commandes Vocales {#vocal}

### Contenu de la vidéo

1. **Accès** (0:00-0:20)
   - Navigation vers le module
   - Interface principale

2. **Démonstration** (0:20-1:30)
   - "Ajouter lait à la liste"
   - "Cherche une recette de lasagnes"
   - "Va aux recettes"

3. **Fallback textuel** (1:30-2:00)
   - Saisie manuelle
   - Exécution de commande

### Commandes démontrées

- 📝 `"Ajouter 2L de lait à la liste"`
- 🔍 `"Comment faire une quiche?"`
- ↗️ `"Ouvre l'inventaire"`

---

## 📷 Scanner WebRTC {#scanner}

### Contenu de la vidéo

1. **Activation caméra** (0:00-0:30)
   - Autorisation navigateur
   - Interface de scan

2. **Scan en direct** (0:30-1:30)
   - Détection automatique
   - Feedback visuel (contour vert)
   - Affichage du code

3. **Utilisation** (1:30-2:00)
   - Bouton "Utiliser ce code"
   - Ajout à l'inventaire

### Codes testés

- EAN-13: 3017620422003 (Nutella)
- EAN-8: 96385074
- QR Code: PRODUIT-TEST-001

---

## 🎥 Enregistrement des vidéos

### Outils recommandés

- **OBS Studio**: Enregistrement écran gratuit
- **Loom**: Enregistrement + partage rapide
- **Screen recording navigateur**: Via DevTools

### Paramètres suggérés

- Résolution: 1920x1080 (Full HD)
- Format: MP4 / WebM
- Audio: Micro + système
- FPS: 30

### Hébergement

Les vidéos peuvent être hébergées sur:

- YouTube (non listé)
- Loom
- GitHub Releases
- Serveur interne

---

## 📝 Script type

### Structure recommandée

```
1. INTRO (10s)
   - "Bonjour, aujourd'hui je vous montre [fonctionnalité]"

2. CONTEXTE (20s)
   - Pourquoi cette fonctionnalité?
   - Quel problème résout-elle?

3. DÉMONSTRATION (2-4min)
   - Étape par étape
   - Montrer les cas d'usage principaux

4. CONCLUSION (20s)
   - Résumé des points clés
   - Liens vers la documentation
```

### Tips

- ✅ Parler lentement et clairement
- ✅ Zoomer sur les éléments importants
- ✅ Ajouter des annotations si nécessaire
- ✅ Garder les vidéos < 5 minutes

---

## 🔗 Liens

- [Guide Batch Cooking](guides/cuisine/batch_cooking.md)
- [Guide Commandes Vocales](guides/utilitaires/vocal.md)
- [Guide Scanner](guides/utilitaires/barcode.md)
