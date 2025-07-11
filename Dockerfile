FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers requirements en premier pour le cache Docker
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tous les fichiers de l'application
COPY . .

# Créer le répertoire de logs
RUN mkdir -p logs

# Exposer le port
EXPOSE 8080

# Variables d'environnement
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV RAILWAY_DEPLOYMENT=true

# Commande de démarrage
CMD ["python", "main.py"]
