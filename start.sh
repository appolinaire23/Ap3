#!/bin/bash

echo "Démarrage de TeleFeed (Render)..."

# Lancer le serveur Flask pour /health
gunicorn app:app --bind 0.0.0.0:$PORT &

# Lancer le bot Telegram
python3 main_railway.py
