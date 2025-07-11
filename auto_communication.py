"""
Système de communication automatique Railway ↔ Replit ↔ Bot
Communication silencieuse et automatique sans messages visibles
"""

import os
import asyncio
import aiohttp
import logging
import time
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AutoCommunicationSystem:
    """Système de communication automatique entre Railway, Replit et Bot"""
    
    def __init__(self, bot_client, admin_id):
        self.bot_client = bot_client
        self.admin_id = admin_id
        self.replit_url = os.getenv('REPLIT_URL', 'https://telefeed-bot.kouamappoloak.repl.co')
        self.railway_url = os.getenv('RAILWAY_STATIC_URL', '')
        self.bot_token = os.getenv('BOT_TOKEN')
        self.is_railway = os.getenv('RAILWAY_DEPLOYMENT') == 'true'
        self.last_ping_time = time.time()
        self.communication_active = True
        
    async def start_auto_communication(self):
        """Démarrer le système de communication automatique"""
        logger.info("🔄 Démarrage du système de communication automatique")
        
        # Démarrer les tâches en parallèle
        tasks = [
            asyncio.create_task(self.ping_loop()),
            asyncio.create_task(self.health_monitor()),
            asyncio.create_task(self.cross_platform_sync())
        ]
        
        if self.is_railway:
            # Notifier le déploiement Railway réussi
            await self.notify_railway_deployment_success()
        
        # Exécuter toutes les tâches
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def notify_railway_deployment_success(self):
        """Notifier automatiquement le déploiement Railway réussi"""
        try:
            # Attendre que le bot soit complètement démarré
            await asyncio.sleep(5)
            
            # Message de confirmation de déploiement
            success_message = f"""
🚂 **DÉPLOIEMENT RAILWAY RÉUSSI**

✅ Bot TeleFeed déployé avec succès sur Railway.app
🌐 URL Railway: {self.railway_url or 'Configurée automatiquement'}
🔗 Communication Replit: Active
⏰ Déployé le: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}

🔄 **Statut des communications:**
• Railway → Bot: ✅ Opérationnel
• Bot → Replit: ✅ Actif
• Replit → Railway: ✅ Configuré

🎯 Toutes les redirections sont actives et le système de maintien d'activité fonctionne automatiquement.
            """
            
            # Envoyer via l'API Telegram
            await self.send_telegram_message(success_message)
            logger.info("✅ Notification de déploiement Railway envoyée")
            
            # Notifier Replit du déploiement
            await self.notify_replit_deployment()
            
        except Exception as e:
            logger.error(f"Erreur notification déploiement: {e}")
    
    async def notify_replit_deployment(self):
        """Notifier Replit du déploiement Railway"""
        try:
            notification_data = {
                'event': 'railway_deployment_success',
                'message': 'Bot TeleFeed déployé avec succès sur Railway',
                'railway_url': self.railway_url,
                'timestamp': datetime.now().isoformat(),
                'bot_status': 'operational'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.replit_url}/railway-notification",
                    json=notification_data,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        logger.info("✅ Replit notifié du déploiement Railway")
                    else:
                        logger.warning(f"Notification Replit failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Erreur notification Replit: {e}")
    
    async def ping_loop(self):
        """Boucle de ping automatique silencieux"""
        while self.communication_active:
            try:
                await asyncio.sleep(60)  # Ping toutes les 60 secondes
                
                # Ping silencieux Replit
                await self.silent_ping_replit()
                
                # Ping Railway si on est sur Replit
                if not self.is_railway and self.railway_url:
                    await self.silent_ping_railway()
                
                self.last_ping_time = time.time()
                
            except Exception as e:
                logger.error(f"Erreur dans ping loop: {e}")
                await asyncio.sleep(30)
    
    async def silent_ping_replit(self):
        """Ping silencieux vers Replit pour maintenir l'activité"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.replit_url}/ping",
                    timeout=10
                ) as response:
                    if response.status == 200:
                        logger.debug("🔄 Ping Replit silencieux réussi")
                    
        except Exception as e:
            logger.debug(f"Ping Replit failed: {e}")
    
    async def silent_ping_railway(self):
        """Ping silencieux vers Railway"""
        try:
            if not self.railway_url:
                return
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.railway_url}/health",
                    timeout=10
                ) as response:
                    if response.status == 200:
                        logger.debug("🚂 Ping Railway silencieux réussi")
                    
        except Exception as e:
            logger.debug(f"Ping Railway failed: {e}")
    
    async def health_monitor(self):
        """Surveillance de santé automatique"""
        while self.communication_active:
            try:
                await asyncio.sleep(300)  # Vérification toutes les 5 minutes
                
                # Vérifier si les services sont actifs
                replit_ok = await self.check_replit_health()
                railway_ok = await self.check_railway_health() if self.railway_url else True
                
                if not replit_ok:
                    await self.wake_up_replit()
                
                if not railway_ok and not self.is_railway:
                    await self.wake_up_railway()
                
            except Exception as e:
                logger.error(f"Erreur health monitor: {e}")
                await asyncio.sleep(60)
    
    async def check_replit_health(self):
        """Vérifier la santé de Replit"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.replit_url}/health",
                    timeout=5
                ) as response:
                    return response.status == 200
        except:
            return False
    
    async def check_railway_health(self):
        """Vérifier la santé de Railway"""
        try:
            if not self.railway_url:
                return True
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.railway_url}/health",
                    timeout=5
                ) as response:
                    return response.status == 200
        except:
            return False
    
    async def wake_up_replit(self):
        """Réveiller Replit silencieusement"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.replit_url}/wake-up",
                    timeout=10
                ) as response:
                    if response.status == 200:
                        logger.info("🔔 Replit réveillé automatiquement")
        except Exception as e:
            logger.error(f"Erreur réveil Replit: {e}")
    
    async def wake_up_railway(self):
        """Réveiller Railway silencieusement"""
        try:
            if not self.railway_url:
                return
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.railway_url}/health",
                    timeout=10
                ) as response:
                    if response.status == 200:
                        logger.info("🚂 Railway réveillé automatiquement")
        except Exception as e:
            logger.error(f"Erreur réveil Railway: {e}")
    
    async def cross_platform_sync(self):
        """Synchronisation croisée des plateformes"""
        while self.communication_active:
            try:
                await asyncio.sleep(180)  # Sync toutes les 3 minutes
                
                # Synchroniser les statuts
                sync_data = {
                    'timestamp': datetime.now().isoformat(),
                    'bot_active': True,
                    'platform': 'railway' if self.is_railway else 'replit',
                    'last_ping': self.last_ping_time
                }
                
                # Envoyer aux plateformes
                if self.is_railway:
                    await self.sync_to_replit(sync_data)
                else:
                    await self.sync_to_railway(sync_data)
                
            except Exception as e:
                logger.error(f"Erreur sync croisé: {e}")
                await asyncio.sleep(60)
    
    async def sync_to_replit(self, data):
        """Synchroniser vers Replit"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.replit_url}/sync",
                    json=data,
                    timeout=10
                ) as response:
                    logger.debug("🔄 Sync vers Replit réussi")
        except:
            pass  # Sync silencieux
    
    async def sync_to_railway(self, data):
        """Synchroniser vers Railway"""
        try:
            if not self.railway_url:
                return
                
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.railway_url}/sync",
                    json=data,
                    timeout=10
                ) as response:
                    logger.debug("🚂 Sync vers Railway réussi")
        except:
            pass  # Sync silencieux
    
    async def send_telegram_message(self, message):
        """Envoyer un message Telegram via API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                data = {
                    'chat_id': self.admin_id,
                    'text': message,
                    'parse_mode': 'Markdown'
                }
                
                async with session.post(url, json=data, timeout=10) as response:
                    if response.status == 200:
                        logger.info("📨 Message Telegram envoyé")
                    else:
                        logger.error(f"Erreur envoi Telegram: {response.status}")
                        
        except Exception as e:
            logger.error(f"Erreur envoi message: {e}")
    
    def stop_communication(self):
        """Arrêter le système de communication"""
        self.communication_active = False
        logger.info("🛑 Système de communication automatique arrêté")
    
    def get_communication_status(self):
        """Obtenir le statut de communication"""
        return {
            'active': self.communication_active,
            'platform': 'railway' if self.is_railway else 'replit',
            'replit_url': self.replit_url,
            'railway_url': self.railway_url,
            'last_ping': datetime.fromtimestamp(self.last_ping_time).strftime('%H:%M:%S')
        }