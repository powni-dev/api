import os
import base64
import requests
import json
from http import HTTPStatus

def handler(request):
    user_id = request.args.get('id')
    if not user_id:
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": '{"error": "Please provide a Discord user ID using ?id="}'
        }

    # Discord bilgisi alma
    url = f"https://discordlookup.mesalytic.moe/v1/user/{user_id}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return {
                "statusCode": HTTPStatus.NOT_FOUND,
                "body": '{"error": "Invalid ID or user not found!"}'
            }
        data = response.json()
    except requests.RequestException as e:
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "body": f'{{"error": "Failed to fetch Discord info: {str(e)}"}}'
        }

    # Token bilgisi
    token_fp = base64.b64encode(user_id.encode("utf-8")).decode("utf-8")

    # Yanıt oluştur
    response = {
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
        }
    }

    return {
        "statusCode": HTTPStatus.OK,
        "body": json.dumps(response),
        "headers": {"Content-Type": "application/json"}
    }
