from flask import Flask, jsonify, request
import threading
import time
import os
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Variables globales pour le statut
server_status = {
    "last_activity": time.time(),
    "start_time": time.time(),
    "requests_count": 0,
    "wake_up_calls": 0
}

@app.route('/')
def home():
    """Page d'accueil"""
    server_status["last_activity"] = time.time()
    server_status["requests_count"] += 1
    
    return jsonify({
        "status": "TeleFeed Bot Server Active",
        "uptime": int(time.time() - server_status["start_time"]),
        "last_activity": datetime.fromtimestamp(server_status["last_activity"]).strftime("%Y-%m-%d %H:%M:%S"),
        "requests_count": server_status["requests_count"]
    })

@app.route('/ping')
def ping():
    """Endpoint pour les pings de maintien d'activité"""
    server_status["last_activity"] = time.time()
    server_status["requests_count"] += 1
    
    logger.info(f"📡 Ping reçu - {datetime.now().strftime('%H:%M:%S')}")
    
    return jsonify({
        "status": "pong",
        "timestamp": datetime.now().isoformat(),
        "server_active": True
    })

@app.route('/wake-up')
def wake_up():
    """Endpoint pour réveiller le serveur"""
    server_status["last_activity"] = time.time()
    server_status["requests_count"] += 1
    server_status["wake_up_calls"] += 1
    
    logger.info("🔔 Serveur réveillé par le bot")
    
    return jsonify({
        "status": "D'accord Kouamé",
        "message": "Serveur Replit réveillé",
        "timestamp": datetime.now().isoformat(),
        "wake_up_calls": server_status["wake_up_calls"]
    })

@app.route('/status')
def status():
    """Statut détaillé du serveur"""
    server_status["last_activity"] = time.time()
    server_status["requests_count"] += 1
    
    return jsonify({
        "server_status": "active",
        "uptime_seconds": int(time.time() - server_status["start_time"]),
        "last_activity": datetime.fromtimestamp(server_status["last_activity"]).strftime("%Y-%m-%d %H:%M:%S"),
        "requests_count": server_status["requests_count"],
        "wake_up_calls": server_status["wake_up_calls"],
        "current_time": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    server_status["last_activity"] = time.time()
    
    return jsonify({
        "status": "healthy",
        "service": "TeleFeed Bot",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/send-message', methods=['POST'])
def send_message():
    """Endpoint pour que le serveur envoie un message via le bot"""
    server_status["last_activity"] = time.time()
    server_status["requests_count"] += 1
    
    try:
        data = request.json
        admin_id = data.get('admin_id')
        message = data.get('message')
        bot_token = data.get('bot_token')
        
        if not all([admin_id, message, bot_token]):
            return jsonify({"error": "Paramètres manquants"}), 400
        
        # Envoyer le message via l'API Telegram HTTP
        import requests
        
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": admin_id,
            "text": message
        }
        
        response = requests.post(telegram_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"📨 Message envoyé depuis le SERVEUR REPLIT: {message}")
            return jsonify({
                "status": "success",
                "message": "Message envoyé par le serveur Replit",
                "timestamp": datetime.now().isoformat()
            })
        else:
            logger.error(f"Échec envoi message Telegram: {response.status_code}")
            return jsonify({"error": "Échec envoi Telegram"}), 500
            
    except Exception as e:
        logger.error(f"Erreur envoi message: {e}")
        return jsonify({"error": "Erreur serveur"}), 500

@app.route('/trigger-message', methods=['POST'])
def trigger_message():
    """Endpoint pour déclencher un message depuis le serveur"""
    server_status["last_activity"] = time.time()
    server_status["requests_count"] += 1
    
    try:
        data = request.json
        admin_id = data.get('admin_id')
        message = data.get('message')
        bot_token = data.get('bot_token')
        
        if not all([admin_id, message, bot_token]):
            return jsonify({"error": "Paramètres manquants"}), 400
        
        # Envoyer le message via l'API Telegram HTTP
        import requests
        
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": admin_id,
            "text": message
        }
        
        response = requests.post(telegram_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"🔥 Message déclenché depuis le SERVEUR REPLIT: {message}")
            return jsonify({
                "status": "success",
                "message": "Message déclenché par le serveur Replit",
                "timestamp": datetime.now().isoformat(),
                "source": "Serveur Replit HTTP"
            })
        else:
            logger.error(f"Échec déclenchement message Telegram: {response.status_code}")
            return jsonify({"error": "Échec déclenchement Telegram"}), 500
            
    except Exception as e:
        logger.error(f"Erreur déclenchement message: {e}")
        return jsonify({"error": "Erreur serveur"}), 500

@app.route('/railway-notification', methods=['POST'])
def railway_notification():
    """Endpoint pour recevoir les notifications de Railway"""
    server_status["last_activity"] = time.time()
    server_status["requests_count"] += 1
    
    try:
        data = request.json
        event = data.get('event', 'unknown')
        message = data.get('message', '')
        railway_url = data.get('railway_url', '')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        if event == 'railway_deployment_success':
            logger.info(f"🚂 Notification Railway reçue: {message}")
            logger.info(f"🌐 URL Railway: {railway_url}")
            
            # Log du succès du déploiement
            success_log = f"""
DÉPLOIEMENT RAILWAY CONFIRMÉ:
- Event: {event}
- Message: {message}
- URL Railway: {railway_url}
- Timestamp: {timestamp}
- Statut Replit: Opérationnel
            """
            logger.info(success_log)
            
            return jsonify({
                "status": "notification_received",
                "message": "Déploiement Railway confirmé",
                "replit_status": "operational",
                "timestamp": datetime.now().isoformat()
            })
        
        return jsonify({
            "status": "notification_received",
            "event": event,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erreur notification Railway: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/sync', methods=['POST'])
def sync_endpoint():
    """Endpoint pour synchronisation croisée des plateformes"""
    server_status["last_activity"] = time.time()
    server_status["requests_count"] += 1
    
    try:
        data = request.json
        platform = data.get('platform', 'unknown')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        logger.debug(f"🔄 Sync reçu de {platform}")
        
        return jsonify({
            "status": "sync_received",
            "platform": "replit",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erreur sync: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

def start_http_server():
    """Démarrer le serveur HTTP"""
    port = int(os.environ.get('PORT', 8080))  # Port 8080 pour Replit
    logger.info(f"🌐 Démarrage du serveur HTTP sur le port {port}")
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except OSError as e:
        if "Address already in use" in str(e):
            logger.info(f"⚠️ Port {port} occupé, tentative port {port+1}")
            app.run(
                host='0.0.0.0',
                port=port+1,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        else:
            raise

def start_server_in_background():
    """Démarrer le serveur HTTP en arrière-plan"""
    server_thread = threading.Thread(target=start_http_server, daemon=True)
    server_thread.start()
    logger.info("🔄 Serveur HTTP démarré en arrière-plan")
    return server_thread

if __name__ == "__main__":
    start_http_server()