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
                "ID": data.get('id', ''),
                "Created At": data.get('created_at', ''),
                "Username": data.get('username', ''),
                "Global Name": data.get('global_name'),
                "Accent Color": data.get('accent_color'),
                "Badges": data.get('badges', []),
                "Avatar Decoration": data.get('avatar_decoration')
            },
            "Avatar Info": {
                "ID": data.get('avatar', {}).get('id', ''),
                "Animated": data.get('avatar', {}).get('is_animated', False),
                "Link": data.get('avatar', {}).get('link', '')
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

        # JSON yerine düz metin formatında çıktı
        response_text = (
            f"User Info\n"
            f"ID: {result['User Info']['ID']}\n"
            f"Created At: {result['User Info']['Created At']}\n"
            f"Username: {result['User Info']['Username']}\n"
            f"Global Name: {result['User Info']['Global Name']}\n"
            f"Accent Color: {result['User Info']['Accent Color'] or 'None'}\n"
            f"Badges: {', '.join(result['User Info']['Badges']) if result['User Info']['Badges'] else 'None'}\n"
            f"Avatar Decoration: {result['User Info']['Avatar Decoration'] or 'None'}\n\n"
            
            f"Avatar Info\n"
            f"ID: {result['Avatar Info']['ID']}\n"
            f"Animated: {result['Avatar Info']['Animated']}\n"
            f"Link: {result['Avatar Info']['Link']}\n\n"
            
            f"Banner Info\n"
            f"ID: {result['Banner Info']['ID'] or 'None'}\n"
            f"Animated: {result['Banner Info']['Animated']}\n"
            f"Link: {result['Banner Info']['Link'] or 'None'}\n"
            f"Color: {result['Banner Info']['Color'] or 'None'}\n\n"
            
            f"Raw Data\n"
            f"Discriminator: {result['Raw Data']['Discriminator']}\n"
            f"Public Flags: {result['Raw Data']['Public Flags']}\n"
            f"Flags: {result['Raw Data']['Flags']}\n"
            f"Banner Color: {result['Raw Data']['Banner Color'] or 'None'}\n"
            f"Clan: {result['Raw Data']['Clan'] or 'None'}\n"
            f"Primary Guild: {result['Raw Data']['Primary Guild'] or 'None'}\n"
            f"Collectibles: {result['Raw Data']['Collectibles'] or 'None'}\n\n"
            
            f"Token Info\n"
            f"User Token First Part: {result['Token Info']['User Token First Part']}"
        )

        return response_text, 200, {'Content-Type': 'text/plain'}

    except requests.exceptions.RequestException as e:
        return f"Discord API error: {str(e)}", 502
    except Exception as e:
        return f"Internal server error: {str(e)}", 500

def create_app():
    return app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
