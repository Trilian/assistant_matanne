# 📷 Guide Scanner Codes-barres

Scannez les codes-barres pour ajouter rapidement des articles à votre inventaire ou liste de courses.

## 🎯 Concept

Le scanner de codes-barres permet de:

- Identifier automatiquement les produits
- Ajouter rapidement à l'inventaire
- Vérifier les stocks existants
- Obtenir les informations nutritionnelles

## 📱 Méthodes de scan

### 1. Scanner WebRTC (Webcam)

**Le plus fluide** - Scan en temps réel via la webcam.

1. Allez dans **🛠️ Utilitaires > 📷 Scanner**
2. Autorisez l'accès à la caméra
3. Approchez le code-barres de la webcam
4. Le code est détecté automatiquement

#### Dépendances requises

```bash
pip install streamlit-webrtc opencv-python-headless pyzbar
```

### 2. Scanner Photo

**Plus simple** - Prenez une photo du code.

1. Cliquez sur **📸 Photographier le code-barres**
2. Prenez la photo
3. Le code est analysé automatiquement

### 3. Saisie manuelle

**Fallback** - Tapez le code directement.

1. Entrez le code dans le champ texte
2. Sélectionnez le type (EAN-13, EAN-8, etc.)
3. Cliquez **✅ Valider**

## 📊 Types de codes supportés

| Type        | Format         | Exemple       |
| ----------- | -------------- | ------------- |
| **EAN-13**  | 13 chiffres    | 3017620422003 |
| **EAN-8**   | 8 chiffres     | 96385074      |
| **UPC**     | 12 chiffres    | 012345678905  |
| **QR Code** | Variable       | PROD-2024-XYZ |
| **CODE128** | Alphanumérique | ABC123456     |

## 🔄 Workflow typique

### Inventaire après courses

1. Rentrez vos courses
2. Ouvrez le scanner
3. Scannez chaque article
4. L'inventaire est mis à jour automatiquement

### Vérification de stock

1. En cuisine, scannez un produit
2. Voyez immédiatement la quantité en stock
3. Ajoutez à la liste si nécessaire

### Import de produits

1. Scannez un nouveau produit
2. Si inconnu, les infos sont récupérées (OpenFoodFacts)
3. Complétez les détails manquants
4. Enregistrez pour les prochaines fois

## 💡 Astuces pour un bon scan

### ✅ Bonnes pratiques

- Bonne luminosité (évitez les reflets)
- Code-barres propre et non endommagé
- Distance appropriée (10-30 cm)
- Tenez stable pendant le scan

### ❌ À éviter

- Codes-barres pliés ou froissés
- Éclairage trop fort ou trop faible
- Mouvements pendant le scan
- Codes partiellement masqués

## 🔗 Intégration OpenFoodFacts

Pour les produits alimentaires, on récupère automatiquement:

- 📛 Nom du produit
- 🏷️ Marque
- 📊 Valeurs nutritionnelles
- 🥗 Nutri-Score
- ⚠️ Allergènes
- 🌍 Origine

## 📱 Compatibilité mobile

Le scanner fonctionne sur mobile:

1. Ouvrez Assistant Matanne dans Chrome/Safari
2. Allez au scanner
3. Utilisez la caméra arrière
4. Scannez comme d'habitude

## 🔧 Dépannage

### La caméra ne s'active pas

1. Vérifiez les permissions du navigateur
2. Utilisez HTTPS (requis pour l'accès caméra)
3. Essayez un autre navigateur
4. Utilisez le mode photo ou manuel

### Le code n'est pas détecté

1. Améliorez l'éclairage
2. Rapprochez/éloignez la caméra
3. Essayez un autre angle
4. Utilisez la saisie manuelle

### Produit non reconnu

1. Vérifiez que le code est correct
2. Le produit n'existe peut-être pas dans la base
3. Ajoutez-le manuellement avec les détails

## ⚙️ Configuration

### Paramètres disponibles

- **Caméra par défaut**: Avant/Arrière (mobile)
- **Vibration au scan**: Oui/Non
- **Son de confirmation**: Oui/Non
- **Auto-ajout inventaire**: Oui/Non

## 🔮 Fonctionnalités futures

- Scan multi-codes simultané
- Reconnaissance de tickets de caisse
- Import par lot depuis fichier
- Historique des scans

## 🔗 Liens utiles

- [Guide Inventaire](../cuisine/inventaire.md)
- [Guide Courses](../cuisine/courses.md)
- [Guide Commandes Vocales](vocal.md)
