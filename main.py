import os
from dotenv import load_dotenv
from bot.handlers import start_bot_sync
from http_server import start_server_in_background
import threading

if __name__ == "__main__":
    # Charger les variables d'environnement
    load_dotenv()
    print("✅ Fichier .env chargé")

    # Détection de la plateforme de déploiement
    is_railway = os.getenv('RAILWAY_DEPLOYMENT') == 'true' or os.getenv('RAILWAY_STATIC_URL')
    is_replit = os.getenv('REPL_SLUG') or os.getenv('REPLIT_URL')
    
    if is_railway:
        # Configuration pour Railway.app
        railway_port = int(os.environ.get('PORT', 8080))
        os.environ['PORT'] = str(railway_port)
        print("🚂 Bot TeleFeed déployé avec succès sur Railway.app")
        
        # Import du système Railway
        from railway_keep_alive import RailwayKeepAliveSystem
        
        # Start HTTP server in background
        server_thread = start_server_in_background()
        
        # Start the bot (main process)
        start_bot_sync()
        
    else:
        # Configuration par défaut (Replit)
        replit_port = int(os.environ.get('PORT', 8080))
        os.environ['PORT'] = str(replit_port)
        print("🚀 bot déployé avec succès")

        # Start HTTP server in background
        server_thread = start_server_in_background()
        
        # Start the bot (main process)
        start_bot_sync()