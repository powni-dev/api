from flask import Flask, jsonify
import base64
import requests
from datetime import datetime

app = Flask(__name__)

@app.route('/api/<userid>', methods=['GET'])
def get_discord_user(userid):
    try:
        # Discord API isteği
        url = f"https://discordlookup.mesalytic.moe/v1/user/{userid}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Base64 token oluştur
        token_fp = base64.b64encode(userid.encode()).decode('utf-8')

        # İstenen formatta yanıt oluştur
        result = {
            "User Info": {
                "ID": data['id'],
                "Created At": data['created_at'],
                "Username": data['username'],
                "Global Name": data.get('global_name'),
                "Accent Color": data.get('accent_color'),
                "Badges": data.get('badges', []),
                "Avatar Decoration": data.get('avatar_decoration')
            },
            "Avatar Info": {
                "ID": data['avatar']['id'],
                "Animated": data['avatar']['is_animated'],
                "Link": data['avatar']['link']
            },
            "Banner Info": {
                "ID": data.get('banner', {}).get('id'),
                "Animated": data.get('banner', {}).get('is_animated', False),
                "Link": data.get('banner', {}).get('link'),
                "Color": data.get('banner', {}).get('color')
            },
            "Raw Data": {
                "Discriminator": 0,  # Yeni Discord sisteminde artık yok
                "Public Flags": data.get('public_flags', 0),
                "Flags": data.get('flags', 0),
                "Banner Color": data.get('banner_color'),
                "Clan": None,
                "Primary Guild": None,
                "Collectibles": None
            },
            "Token Info": {
                "User Token First Part": token_fp
            }
        }

        return jsonify(result)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Discord API error: {str(e)}"}), 502
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
