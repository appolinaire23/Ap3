#!/bin/bash
# Script de démarrage pour Railway.app

echo "🚂 Démarrage TeleFeed Bot sur Railway..."
echo "📅 $(date)"
echo "🌐 URL Railway: $RAILWAY_STATIC_URL"

# Configuration des variables d'environnement
export PORT=${PORT:-8080}
export PYTHONUNBUFFERED=1
export RAILWAY_DEPLOYMENT=true

# Vérification des variables critiques
if [ -z "$API_ID" ] || [ -z "$BOT_TOKEN" ]; then
    echo "❌ Variables d'environnement manquantes"
    exit 1
fi

echo "✅ Variables d'environnement configurées"

# Démarrage du bot
echo "🚀 Lancement du bot TeleFeed..."
python main.py
