import json
import base64
from datetime import datetime
import requests
from http import HTTPStatus

def handler(request):
    # Query parametresinden 'id' al
    user_id = request.args.get('id')

    if not user_id:
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": json.dumps({"error": "Please provide a Discord user ID!"})
        }

    # Discord API'den kullanıcı bilgisi alma
    url = f"https://discordlookup.mesalytic.moe/v1/user/{user_id}"
    response = requests.get(url)

    if response.status_code != 200:
        return {
            "statusCode": HTTPStatus.NOT_FOUND,
            "body": json.dumps({"error": "Invalid ID or user not found!"})
        }

    data = response.json()

    # Token'ın ilk kısmını hesaplama
    encoded_bytes = base64.b64encode(user_id.encode("utf-8"))
    token_fp = str(encoded_bytes, "utf-8")

    # Detaylı response oluşturma
    result = {
        "user_info": {
            "id": data['id'],
            "username": data['username'],
            "global_name": data['global_name'],
            "created_at": data['created_at'],
            "accent_color": data['accent_color'],
            "badges": data['badges'],
            "avatar_decoration": data['avatar_decoration']
        },
        "avatar": {
            "id": data['avatar']['id'],
            "is_animated": data['avatar']['is_animated'],
            "link": data['avatar']['link']
        },
        "banner": {
            "id": data['banner']['id'] if data['banner']['id'] else None,
            "is_animated": data['banner']['is_animated'],
            "link": data['banner']['link'] if data['banner']['link'] else None,
            "color": data['banner']['color'] if 'color' in data['banner'] else None
        },
        "token_info": {
            "user_token_first_part": token_fp
        },
        "timestamp": datetime.utcnow().isoformat()
    }

    return {
        "statusCode": HTTPStatus.OK,
        "body": json.dumps(result),
        "headers": {
            "Content-Type": "application/json"
        }
    }

# Vercel için gerekli yapı
def main(request):
    return handler(request)
