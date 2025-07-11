"""
Système de maintien d'activité spécifique à Railway.app
Gère la communication Railway ↔ Replit et le réveil automatique
"""

import asyncio
import aiohttp
import time
import os
import logging
from datetime import datetime
from telethon import TelegramClient

logger = logging.getLogger(__name__)

class RailwayKeepAliveSystem:
    """Système de maintien d'activité pour Railway avec communication Replit"""

    def __init__(self, bot_client, admin_id):
        self.bot_client = bot_client
        self.admin_id = admin_id
        self.last_activity = time.time()
        self.check_interval = 60  # 1 minute
        self.timeout_threshold = 180  # 3 minutes
        self.railway_url = os.getenv('RAILWAY_STATIC_URL', 'http://localhost:8080')
        self.replit_url = os.getenv('REPLIT_URL', '')
        self.is_running = False
        self.wake_up_active = False

    async def start_railway_keep_alive(self):
        """Démarrer le système de maintien d'activité Railway"""
        if self.is_running:
            return

        self.is_running = True
        logger.info("🚂 Système de maintien d'activité Railway démarré")

        # Notifier le déploiement réussi
        await self.notify_deployment_success()

        # Démarrer les tâches de monitoring
        await asyncio.gather(
            self.monitor_railway_activity(),
            self.monitor_replit_communication(),
            self.periodic_railway_health_check()
        )

    async def notify_deployment_success(self):
        """Notifie le succès du déploiement Railway"""
        try:
            # Message pour l'admin Telegram
            deployment_message = f"""
🚂 **DÉPLOIEMENT RAILWAY RÉUSSI !**

✅ **TeleFeed Bot opérationnel sur Railway.app**

📊 **Détails :**
• Platform: Railway.app
• URL: {self.railway_url}
• Déployé le: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
• Statut: ✅ Opérationnel

🔄 **Fonctionnalités actives :**
• Communication Railway ↔ Replit
• Système de réveil automatique
• Monitoring de santé en continu

🎉 **Le bot est maintenant hébergé en permanence !**
            """

            # Envoyer à l'admin via le bot
            if self.admin_id and self.bot_client:
                await self.bot_client.send_message(int(self.admin_id), deployment_message)
                logger.info("✅ Notification déploiement envoyée à l'admin")

            # Notifier le serveur Replit
            await self.notify_replit_server()

        except Exception as e:
            logger.error(f"❌ Erreur notification déploiement: {e}")

    async def notify_replit_server(self):
        """Notifie le serveur Replit du déploiement Railway"""
        if not self.replit_url:
            logger.warning("⚠️ URL Replit non configurée pour notification")
            return

        try:
            async with aiohttp.ClientSession() as session:
                notification_data = {
                    "event": "railway_deployment_success",
                    "message": "déploiement réussi",
                    "railway_url": self.railway_url,
                    "timestamp": datetime.now().isoformat(),
                    "source": "railway_bot"
                }

                async with session.post(
                    f"{self.replit_url}/railway-notification",
                    json=notification_data,
                    timeout=15
                ) as response:
                    if response.status == 200:
                        logger.info("🔄 Serveur Replit notifié du déploiement Railway")
                    else:
                        logger.warning(f"⚠️ Réponse Replit: {response.status}")

        except Exception as e:
            logger.error(f"❌ Erreur notification Replit: {e}")

    async def monitor_railway_activity(self):
        """Surveiller l'activité Railway et réveiller si nécessaire"""
        while self.is_running:
            try:
                current_time = time.time()
                inactivity_duration = current_time - self.last_activity

                if inactivity_duration > self.timeout_threshold and not self.wake_up_active:
                    logger.info(f"🚨 Railway inactif détecté ({inactivity_duration:.0f}s)")
                    self.wake_up_active = True
                    await self.wake_up_railway()
                elif inactivity_duration <= self.timeout_threshold and self.wake_up_active:
                    logger.info("✅ Railway redevenu actif - Arrêt du réveil")
                    self.wake_up_active = False

                await asyncio.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"❌ Erreur monitoring Railway: {e}")
                await asyncio.sleep(30)

    async def monitor_replit_communication(self):
        """Surveiller la communication avec Replit et réveiller si nécessaire"""
        while self.is_running:
            try:
                if self.replit_url:
                    # Test de connectivité Replit
                    replit_responsive = await self.test_replit_connectivity()
                    
                    if not replit_responsive:
                        logger.info("🔔 Réveil du serveur Replit depuis Railway")
                        await self.wake_up_replit_from_railway()

                await asyncio.sleep(120)  # Check toutes les 2 minutes

            except Exception as e:
                logger.error(f"❌ Erreur communication Replit: {e}")
                await asyncio.sleep(60)

    async def test_replit_connectivity(self):
        """Teste si le serveur Replit répond"""
        if not self.replit_url:
            return False

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.replit_url}/ping",
                    timeout=10
                ) as response:
                    return response.status == 200

        except Exception:
            return False

    async def wake_up_replit_from_railway(self):
        """Réveille le serveur Replit depuis Railway"""
        if not self.replit_url:
            return

        try:
            async with aiohttp.ClientSession() as session:
                wake_data = {
                    "source": "railway_bot",
                    "message": "Réveil depuis Railway",
                    "railway_url": self.railway_url,
                    "timestamp": datetime.now().isoformat()
                }

                async with session.post(
                    f"{self.replit_url}/wake-up",
                    json=wake_data,
                    timeout=15
                ) as response:
                    if response.status == 200:
                        logger.info("🔔 Serveur Replit réveillé depuis Railway")
                        
                        # Notifier l'admin du réveil
                        wake_message = f"""
🔔 **RÉVEIL AUTOMATIQUE**

🚂 Railway a réveillé le serveur Replit
⏰ {datetime.now().strftime('%H:%M:%S')}

✅ Communication Railway ↔ Replit active
                        """
                        
                        if self.admin_id and self.bot_client:
                            await self.bot_client.send_message(int(self.admin_id), wake_message)

        except Exception as e:
            logger.error(f"❌ Erreur réveil Replit: {e}")

    async def wake_up_railway(self):
        """Auto-réveil de Railway"""
        try:
            # Ping interne pour réveiller Railway
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.railway_url}/ping",
                    timeout=10
                ) as response:
                    if response.status == 200:
                        logger.info("🔄 Railway auto-réveillé")
                        self.last_activity = time.time()
                        self.wake_up_active = False

        except Exception as e:
            logger.error(f"❌ Erreur auto-réveil Railway: {e}")

    async def periodic_railway_health_check(self):
        """Vérification périodique de santé Railway"""
        while self.is_running:
            try:
                # Health check Railway
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.railway_url}/health",
                        timeout=10
                    ) as response:
                        if response.status == 200:
                            self.update_activity()
                            logger.info("✅ Railway health check OK")

                await asyncio.sleep(300)  # Check toutes les 5 minutes

            except Exception as e:
                logger.error(f"❌ Railway health check failed: {e}")
                await asyncio.sleep(60)

    def update_activity(self):
        """Met à jour l'activité Railway"""
        self.last_activity = time.time()

    def stop_railway_keep_alive(self):
        """Arrêter le système de maintien d'activité Railway"""
        self.is_running = False
        logger.info("🔴 Système Railway keep-alive arrêté")

    def get_railway_status(self):
        """Obtenir le statut du système Railway"""
        current_time = time.time()
        return {
            "platform": "railway.app",
            "last_activity": datetime.fromtimestamp(self.last_activity).strftime("%Y-%m-%d %H:%M:%S"),
            "inactive_duration": int(current_time - self.last_activity),
            "railway_url": self.railway_url,
            "replit_url": self.replit_url,
            "is_running": self.is_running,
            "wake_up_active": self.wake_up_active
        }