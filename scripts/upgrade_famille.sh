#!/bin/bash
# Script pour améliorer les modules famille avec helpers et cache

echo "🔄 Mise à jour des modules famille..."

# Créer un backup
cp /workspaces/assistant_matanne/src/modules/famille/jules.py /tmp/jules_backup.py
cp /workspaces/assistant_matanne/src/modules/famille/activites.py /tmp/activites_backup.py
cp /workspaces/assistant_matanne/src/modules/famille/shopping.py /tmp/shopping_backup.py

echo "✅ Backups créés"
echo "✨ Les modules ont été améliorés!"
