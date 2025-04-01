import json
import base64
from datetime import datetime
import requests

def main(request):
    try:
        # Query parametresini al
        user_id = request.args.get('id')
        
        if not user_id:
            return json.dumps({"error": "Please provide a Discord user ID!"}), 400

        # Discord API isteği
        url = f"https://discordlookup.mesalytic.moe/v1/user/{user_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Yanıtı oluştur
        result = {
            "user_info": data,
            "token_info": {
                "user_token_first_part": base64.b64encode(user_id.encode()).decode('utf-8')
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        return json.dumps(result), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return json.dumps({"error": str(e)}), 500

# Vercel özel export
def vercel_handler(request):
    body, status_code, headers = main(request)
    return body, {
        'statusCode': status_code,
        'headers': headers
    }
