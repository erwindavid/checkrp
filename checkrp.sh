#!/bin/bash
# --- commentaire IPAD
# --- commentaire MAC MINI
# --- CONFIGURATION DYNAMIQUE ---
# Cherche automatiquement le premier fichier .plist présent dans le dossier actuel
PLIST_NAME=$(ls *.plist 2>/dev/null | head -n 1)
TARGET_DIR="$HOME/Library/LaunchAgents"

echo "🔄 Mise à jour de votre moniteur automatisé..."

# 1. Vérifier si un fichier plist a bien été trouvé
if [ -z "$PLIST_NAME" ]; then
    echo "❌ Erreur : Aucun fichier .plist n'a été trouvé dans ce dossier."
    exit 1
fi

# Extraction automatique du label (ex: "com.moniteur.ee") en enlevant le ".plist"
LABEL_NAME=$(basename "$PLIST_NAME" .plist)
echo "📦 Projet détecté : $LABEL_NAME ($PLIST_NAME)"

# 2. Décharger l'ancienne version si elle est déjà active
if launchctl list | grep -q "$LABEL_NAME"; then
    echo "🧹 Arrêt de l'ancienne planification en cours..."
    launchctl bootout gui/$(id -u) "$TARGET_DIR/$PLIST_NAME" 2>/dev/null
fi

# 3. Copier le fichier de configuration vers le dossier système de macOS
echo "📂 Copie du fichier de configuration vers les LaunchAgents..."
cp "$PLIST_NAME" "$TARGET_DIR/"

# 4. Charger et activer la nouvelle planification
echo "🚀 Activation de l'horaire dans Launchd..."
launchctl bootstrap gui/$(id -u) "$TARGET_DIR/$PLIST_NAME"

if [ $? -eq 0 ]; then
    echo "✅ Succès ! Votre Mac mini est synchronisé avec votre configuration."
else
    echo "❌ Un problème est survenu lors de l'activation par launchctl."
fi