import os
import requests

def send_render_url_to_admin():
    bot_token = os.getenv("BOT_TOKEN")
    admin_id = os.getenv("ADMIN_ID")
    render_url = os.getenv("RENDER_EXTERNAL_URL")

    if not all([bot_token, admin_id, render_url]):
        print("BOT_TOKEN, ADMIN_ID ou RENDER_EXTERNAL_URL manquant.")
        return

    message = f"✅ Ton bot TeleFeed est maintenant en ligne :\n{render_url}"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    data = {
        "chat_id": admin_id,
        "text": message
    }

    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("URL envoyée à l'admin avec succès.")
        else:
            print(f"Erreur lors de l'envoi : {response.text}")
    except Exception as e:
        print(f"Exception : {e}")
