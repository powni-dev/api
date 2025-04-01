import json
import base64
from datetime import datetime
import requests

def app(request):
    try:
        # Query parametresini al
        user_id = request.args.get('id')
        
        if not user_id:
            return json.dumps({"error": "Please provide a Discord user ID!"}), 400, {'Content-Type': 'application/json'}

        # Discord API isteği
        url = f"https://discordlookup.mesalytic.moe/v1/user/{user_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Base64 token oluştur
        token_fp = base64.b64encode(user_id.encode()).decode('utf-8')

        # Yanıtı oluştur
        result = {
            "user_info": {
                "id": data.get('id'),
                "username": data.get('username'),
                "global_name": data.get('global_name'),
                "created_at": data.get('created_at'),
                "accent_color": data.get('accent_color'),
                "badges": data.get('badges', []),
                "avatar_decoration": data.get('avatar_decoration')
            },
            "avatar": {
                "id": data.get('avatar', {}).get('id'),
                "is_animated": data.get('avatar', {}).get('is_animated', False),
                "link": data.get('avatar', {}).get('link')
            },
            "banner": {
                "id": data.get('banner', {}).get('id'),
                "is_animated": data.get('banner', {}).get('is_animated', False),
                "link": data.get('banner', {}).get('link'),
                "color": data.get('banner', {}).get('color')
            },
            "token_info": {
                "user_token_first_part": token_fp
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        return json.dumps(result), 200, {'Content-Type': 'application/json'}

    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Discord API error: {str(e)}"}), 502, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": f"Internal server error: {str(e)}"}), 500, {'Content-Type': 'application/json'}

# Vercel'in beklediği ana export
handler = app
