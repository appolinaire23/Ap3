import asyncio
import aiohttp
import time
from datetime import datetime
import logging
from telethon import TelegramClient
import os

logger = logging.getLogger(__name__)

class KeepAliveSystem:
    """Système de maintien d'activité pour Replit"""

    def __init__(self, bot_client, admin_id):
        self.bot_client = bot_client
        self.admin_id = admin_id
        self.last_bot_activity = time.time()
        self.last_server_activity = time.time()
        self.check_interval = 60  # 1 minute (plus fréquent)
        self.timeout_threshold = 120  # 2 minutes (plus sensible)
        self.server_url = os.getenv('REPLIT_URL', 'http://localhost:5000')  # URL automatique Replit
        self.is_running = False
        self.continuous_mode = False  # Mode normal par défaut - réveil seulement si inactif
        self.message_count = 0
        self.wake_up_active = False  # Indique si une séquence de réveil est en cours

    async def start_keep_alive(self):
        """Démarrer le système de maintien d'activité"""
        if self.is_running:
            return

        self.is_running = True
        logger.info("🔄 Système de maintien d'activité démarré")

        # Démarrer les tâches en parallèle
        await asyncio.gather(
            self.monitor_bot_activity(),
            self.monitor_server_activity(),
            self.periodic_health_check()
        )

    async def monitor_bot_activity(self):
        """Surveiller l'activité du bot - réveil SEULEMENT si vraiment inactif"""
        while self.is_running:
            try:
                current_time = time.time()
                inactivity_duration = current_time - self.last_bot_activity

                if self.continuous_mode:
                    # Mode continu forcé : envoyer des messages régulièrement
                    await self.send_continuous_messages()
                else:
                    # Vérifier si le bot est VRAIMENT inactif ET le système n'est pas déjà en mode réveil
                    if inactivity_duration > self.timeout_threshold and not self.wake_up_active:
                        logger.info(f"🚨 BOT VRAIMENT INACTIF détecté ({inactivity_duration:.0f}s) - Activation du réveil")
                        self.wake_up_active = True
                        self.message_count = 0
                        # Démarrer UNE SEULE séquence de réveil
                        await self.wake_up_bot()
                    elif inactivity_duration <= self.timeout_threshold and self.wake_up_active:
                        # Bot redevenu actif - arrêter le réveil automatiquement
                        logger.info("✅ Activité bot détectée - Arrêt automatique du réveil")
                        self.wake_up_active = False
                        self.message_count = 0

                # Surveillance normale - pas de messages continus
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Erreur dans monitor_bot_activity: {e}")
                await asyncio.sleep(30)

    async def monitor_server_activity(self):
        """Surveiller l'activité du serveur - réveil SEULEMENT si vraiment inactif"""
        while self.is_running:
            try:
                current_time = time.time()
                inactivity_duration = current_time - self.last_server_activity

                if self.continuous_mode:
                    # Mode continu forcé
                    await self.wake_up_server()
                else:
                    # Vérifier si le serveur est VRAIMENT inactif ET pas déjà en mode réveil
                    if inactivity_duration > self.timeout_threshold and not self.wake_up_active:
                        # Tester si le serveur répond avant de le considérer comme inactif
                        server_responsive = await self.test_server_connectivity()
                        
                        if not server_responsive:
                            logger.info(f"🚨 SERVEUR VRAIMENT INACTIF détecté ({inactivity_duration:.0f}s) - Activation du réveil")
                            self.wake_up_active = True
                            self.message_count = 0
                            # UNE SEULE tentative de réveil
                            await self.wake_up_server()
                        else:
                            # Serveur répond - mise à jour silencieuse
                            self.last_server_activity = current_time
                            logger.info("✅ Serveur répond - Activité mise à jour")
                    elif inactivity_duration <= self.timeout_threshold and self.wake_up_active:
                        # Serveur redevenu actif - arrêter le réveil
                        logger.info("✅ Activité serveur détectée - Arrêt automatique du réveil")
                        self.wake_up_active = False
                        self.message_count = 0

                # Surveillance normale - pas de réveil continu
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Erreur dans monitor_server_activity: {e}")
                await asyncio.sleep(30)

    async def wake_up_bot(self):
        """Réveiller le bot via message du serveur"""
        try:
            # Déclencher un message depuis le serveur Replit
            await self.trigger_server_message_to_bot()
            logger.info("📨 Message de réveil déclenché depuis le SERVEUR REPLIT")

            # Ping silencieux - pas de réponse visible
            await asyncio.sleep(1)

            self.last_bot_activity = time.time()
            logger.info("🤖 Bot réveillé par le SERVEUR REPLIT")

        except Exception as e:
            logger.error(f"Erreur lors du réveil du bot: {e}")

    async def wake_up_server(self):
        """Réveiller le serveur Replit via requête HTTP"""
        try:
            # Ping silencieux - pas de message visible
            logger.info("🔄 Ping silencieux du serveur (pas de message visible)")

            # Faire une requête HTTP pour que le serveur réponde
            await self.make_server_request_with_response()

            self.last_server_activity = time.time()
            logger.info("🖥️ Serveur réveillé et a répondu")

        except Exception as e:
            logger.error(f"Erreur lors du réveil du serveur: {e}")

    async def trigger_server_message_to_bot(self):
        """Déclencher un message du serveur vers le bot"""
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(
                        f"{self.server_url}/send-message",
                        json={
                            "admin_id": self.admin_id,
                            "message": "🔔 Replit: Kouamé réveil toi",
                            "bot_token": os.getenv("BOT_TOKEN")
                        },
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            logger.info("🌐 Serveur Replit a envoyé le message de réveil")
                        else:
                            logger.warning(f"Échec message réveil serveur: {response.status}")
                except Exception as e:
                    logger.debug(f"Erreur message réveil serveur: {e}")
        except:
            pass

    async def make_server_request_with_response(self):
        """Faire une requête au serveur pour qu'il réponde"""
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(
                        f"{self.server_url}/send-message",
                        json={
                            "admin_id": self.admin_id,
                            "message": "✅ Replit: D'accord Kouamé",
                            "bot_token": os.getenv("BOT_TOKEN")
                        },
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            logger.info("🌐 Serveur Replit a répondu avec succès")
                        else:
                            logger.warning(f"Échec réponse serveur: {response.status}")
                except Exception as e:
                    logger.debug(f"Erreur réponse serveur: {e}")
        except:
            pass

    async def send_continuous_messages(self):
        """Envoyer des messages continus SEULEMENT en mode forcé"""
        try:
            # SEULEMENT si mode continu forcé explicitement activé
            if not self.continuous_mode:
                return
                
            self.message_count += 1

            # Messages plus agressifs pour forcer le réveil
            if self.message_count % 2 == 1:
                # Bot vers Serveur - Messages plus insistants
                await self.bot_client.send_message(
                    self.admin_id,
                    f"🚨 Bot: REPLIT RÉVEIL-TOI MAINTENANT ! (Forçage #{self.message_count})"
                )
                logger.info(f"🚨 Message FORCÉ #{self.message_count} envoyé au serveur")

                # Faire plusieurs requêtes HTTP pour forcer le réveil
                await self.make_server_request()
                await asyncio.sleep(1)
                await self.make_server_request()

                # Réponse simulée du serveur
                await asyncio.sleep(2)
                await self.bot_client.send_message(
                    self.admin_id,
                    f"💪 Replit: OUI KOUAMÉ, JE RESTE ÉVEILLÉ ! #{self.message_count}"
                )
            else:
                # Serveur vers Bot - Messages insistants
                await self.bot_client.send_message(
                    self.admin_id,
                    f"🔥 Replit: KOUAMÉ RESTE CONNECTÉ ! (Forçage #{self.message_count})"
                )
                logger.info(f"🔥 Message FORCÉ #{self.message_count} envoyé au bot")

                # Réponse du bot
                await asyncio.sleep(2)
                await self.bot_client.send_message(
                    self.admin_id,
                    f"⚡ Bot: TOUJOURS LÀ REPLIT ! #{self.message_count}"
                )

            # Forcer la mise à jour des activités
            self.last_bot_activity = time.time()
            self.last_server_activity = time.time()

            # Log du forçage
            logger.info(f"🔥 FORÇAGE CONTINU ACTIF - Message #{self.message_count}")

        except Exception as e:
            logger.error(f"Erreur lors des messages continus: {e}")
            # Même en cas d'erreur, continuer le forçage
            self.last_bot_activity = time.time()
            self.last_server_activity = time.time()

    async def test_server_connectivity(self):
        """Tester si le serveur répond (sans le réveiller)"""
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        f"{self.server_url}/ping",
                        timeout=aiohttp.ClientTimeout(total=3)
                    ) as response:
                        if response.status == 200:
                            return True
                except:
                    return False
        except:
            return False
        return False

    async def make_server_request(self):
        """Faire une requête au serveur"""
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        f"{self.server_url}/wake-up",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            logger.info("🌐 Serveur contacté avec succès")
                            self.last_server_activity = time.time()
                except:
                    pass  # Ignorer les erreurs de connexion
        except:
            pass

    async def periodic_health_check(self):
        """Vérification périodique de santé - surveillance intelligente"""
        while self.is_running:
            try:
                current_time = time.time()
                
                # Vérification silencieuse - pas de messages de réveil inutiles
                bot_inactive = (current_time - self.last_bot_activity) > self.timeout_threshold
                server_inactive = (current_time - self.last_server_activity) > self.timeout_threshold
                
                if not bot_inactive and not server_inactive and not self.continuous_mode:
                    # Tout va bien - surveillance normale
                    await self.ping_bot_silent()
                    await self.ping_server_silent()
                    await asyncio.sleep(120)  # Vérification toutes les 2 minutes
                elif self.wake_up_active or self.continuous_mode:
                    # Mode réveil actif - surveillance accélérée
                    await self.ping_bot_silent()
                    await self.ping_server_silent()
                    await asyncio.sleep(30)  # Vérification toutes les 30 secondes
                else:
                    # Inactivité détectée mais pas encore en mode réveil
                    await self.ping_bot_silent()
                    await self.ping_server_silent()
                    await asyncio.sleep(60)  # Vérification chaque minute

            except Exception as e:
                logger.error(f"Erreur dans periodic_health_check: {e}")
                await asyncio.sleep(30)

    async def ping_bot(self):
        """Ping silencieux pour maintenir l'activité du bot"""
        try:
            # Mettre à jour l'activité du bot
            self.last_bot_activity = time.time()

            # Log d'activité
            logger.info(f"🤖 Bot ping - {datetime.now().strftime('%H:%M:%S')}")

        except Exception as e:
            logger.error(f"Erreur ping bot: {e}")

    async def ping_bot_silent(self):
        """Ping silencieux du bot - mise à jour d'activité seulement"""
        try:
            # Mise à jour silencieuse de l'activité sans log
            self.last_bot_activity = time.time()
        except Exception as e:
            logger.error(f"Erreur ping bot silencieux: {e}")

    async def ping_server_silent(self):
        """Ping silencieux du serveur - test de connectivité sans log"""
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        f"{self.server_url}/ping",
                        timeout=aiohttp.ClientTimeout(total=3)
                    ) as response:
                        if response.status == 200:
                            self.last_server_activity = time.time()
                except:
                    pass  # Silence - pas de log d'erreur pour les pings
        except:
            pass

    async def ping_server(self):
        """Ping serveur avec log"""
        try:
            # Faire une requête HTTP légère
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        f"{self.server_url}/ping",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            self.last_server_activity = time.time()
                            logger.info(f"🌐 Serveur ping - {datetime.now().strftime('%H:%M:%S')}")
                        else:
                            logger.warning(f"Ping serveur failed: {response.status}")
                except asyncio.TimeoutError:
                    logger.warning("Timeout ping serveur")
                except Exception as e:
                    logger.debug(f"Erreur ping serveur: {e}")

        except Exception as e:
            logger.error(f"Erreur ping serveur: {e}")

    def update_bot_activity(self):
        """Mettre à jour l'activité du bot (à appeler lors des commandes)"""
        self.last_bot_activity = time.time()

    def update_server_activity(self):
        """Mettre à jour l'activité du serveur (à appeler lors des requêtes HTTP)"""
        self.last_server_activity = time.time()

    def stop_continuous_mode(self):
        """Arrêter le mode continu et la séquence de réveil"""
        self.continuous_mode = False
        self.wake_up_active = False
        self.message_count = 0
        logger.info("⏸️ FORÇAGE ARRÊTÉ - Mode surveillance activé")
        return "⏸️ **FORÇAGE DE RÉVEIL ARRÊTÉ**\n\n✅ Le système revient en mode surveillance intelligent.\n\n**Nouveau fonctionnement :**\n🔍 Surveillance active en permanence\n⚡ Dès qu'inactivité détectée → FORÇAGE IMMÉDIAT\n🔥 Messages continus FORCÉS jusqu'à `/stop`\n💪 Aucun arrêt automatique - réveil persistant\n\n**Le système restera vigilant et forcera le réveil dès la moindre inactivité !**"

    def start_continuous_mode(self):
        """Démarrer le mode continu"""
        self.continuous_mode = True
        self.wake_up_active = True
        self.message_count = 0
        logger.info("🔥 Mode continu ULTRA-FORCÉ activé")
        return "🔥 **MODE CONTINU ULTRA-FORCÉ ACTIVÉ**\n\n⚡ Messages de réveil FORCÉS en permanence\n💪 Bot et serveur maintenus éveillés de force\n🚨 Réveil agressif et persistant\n🔄 Échanges continus jusqu'à `/stop`\n\n**Le système va maintenant FORCER le réveil en permanence !**"

    def stop_keep_alive(self):
        """Arrêter le système de maintien d'activité"""
        self.is_running = False
        logger.info("🔴 Système de maintien d'activité arrêté")

    def get_status(self):
        """Obtenir le statut du système"""
        current_time = time.time()
        return {
            "bot_last_activity": datetime.fromtimestamp(self.last_bot_activity).strftime("%Y-%m-%d %H:%M:%S"),
            "server_last_activity": datetime.fromtimestamp(self.last_server_activity).strftime("%Y-%m-%d %H:%M:%S"),
            "bot_inactive_duration": int(current_time - self.last_bot_activity),
            "server_inactive_duration": int(current_time - self.last_server_activity),
            "is_running": self.is_running,
            "continuous_mode": self.continuous_mode,
            "wake_up_active": self.wake_up_active,
            "message_count": self.message_count
        }