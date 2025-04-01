from flask import Flask, request, jsonify
import requests
import base64
import os

app = Flask(__name__)

def get_discord_info(user_id):
    url = f"https://discordlookup.mesalytic.moe/v1/user/{user_id}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        print(f"Error fetching Discord info: {e}")
        return None

def get_token_info(user_id):
    encoded_bytes = base64.b64encode(user_id.encode("utf-8"))
    return str(encoded_bytes, "utf-8")

@app.route('/api/', methods=['GET'])
def discord_query():
    user_id = request.args.get('id')
    if not user_id:
        return jsonify({"error": "Please provide a Discord user ID using ?id="}), 400

    data = get_discord_info(user_id)
    token_fp = get_token_info(user_id)

    if not data:
        return jsonify({"error": "Invalid ID or user not found!"}), 404

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

    return jsonify(response), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to Ratistan API! Use /api/?id=<Discord_ID> to get user info"}), 200

if __name__ == "__main__":
    app.run()
