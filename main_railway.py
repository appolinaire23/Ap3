"""
Point d'entrée principal pour le déploiement Railway
Modifie le comportement pour Railway.app au lieu de Replit
SANS DÉPENDANCES CONFIG/ - Configuration directe
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

# Charger les variables d'environnement directement
load_dotenv()

# Configuration Railway directe (sans config/)
API_ID = int(os.getenv('API_ID', '29177661'))
API_HASH = os.getenv('API_HASH', 'a8639172fa8d35dbfd8ea46286d349ab')
BOT_TOKEN = os.getenv('BOT_TOKEN', '8168829272:AAEdBli_8E0Du_uHVTGLRLCN6KV7Gwox0WQ')
ADMIN_ID = int(os.getenv('ADMIN_ID', '1190237801'))

# Configuration Railway
RAILWAY_PORT = int(os.getenv('PORT', 8080))
REPLIT_URL = os.getenv('REPLIT_URL', 'https://telefeed-bot.kouamappoloak.repl.co')

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_with_railway_integration():
    """Démarrage avec intégration Railway"""
    try:
        # Import des modules bot sans config/
        from telethon import TelegramClient
        from bot.handlers import handle_start, handle_connect, handle_validation, handle_payment, handle_deploy
        from bot.handlers import handle_admin_commands, handle_redirection, handle_transformation
        from bot.handlers import handle_whitelist, handle_blacklist, handle_chats
        from auto_communication import AutoCommunicationSystem
        from railway_keep_alive import RailwayKeepAliveSystem
        
        print("🚂 Démarrage TeleFeed Bot sur Railway.app")
        
        # Créer le client Telegram
        client = TelegramClient('bot', API_ID, API_HASH)
        
        # Connexion avec le token du bot
        await client.start(bot_token=BOT_TOKEN)
        
        # Enregistrer les handlers
        client.add_event_handler(handle_start)
        client.add_event_handler(handle_connect) 
        client.add_event_handler(handle_validation)
        client.add_event_handler(handle_payment)
        client.add_event_handler(handle_deploy)
        client.add_event_handler(handle_admin_commands)
        client.add_event_handler(handle_redirection)
        client.add_event_handler(handle_transformation)
        client.add_event_handler(handle_whitelist)
        client.add_event_handler(handle_blacklist)
        client.add_event_handler(handle_chats)
        
        # Démarrer le système de communication automatique
        auto_comm = AutoCommunicationSystem(client, ADMIN_ID)
        await auto_comm.start_auto_communication()
        
        # Démarrer le système Railway keep-alive en parallèle
        railway_keep_alive = RailwayKeepAliveSystem(client, ADMIN_ID)
        railway_task = asyncio.create_task(railway_keep_alive.start_railway_keep_alive())
        
        print(f"🚂 Bot Railway démarré sur le port {RAILWAY_PORT}")
        print(f"🔗 Communication avec Replit: {REPLIT_URL}")
        
        # Exécuter le bot
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"Erreur démarrage Railway: {e}")

if __name__ == "__main__":
    # Configuration Railway
    os.environ['RAILWAY_DEPLOYMENT'] = 'true'
    os.environ['PORT'] = str(RAILWAY_PORT)
    
    print("✅ Configuration Railway activée")
    print(f"🚂 Port Railway: {RAILWAY_PORT}")
    
    # Démarrer avec Railway
    asyncio.run(start_with_railway_integration())