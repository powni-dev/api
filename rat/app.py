from flask import Flask, jsonify
import base64
import requests
from datetime import datetime

# Flask uygulamasını oluştur (Render için 'application' ismi şart)
application = Flask(__name__)

@application.route('/api/<userid>', methods=['GET'])
def get_discord_user(userid):
    try:
        url = f"https://discordlookup.mesalytic.moe/v1/user/{userid}"
        response = requests.get(url, timeout=10)
        data = response.json()

        return jsonify({
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
            "Token Info": {
                "User Token First Part": base64.b64encode(userid.encode()).decode('utf-8')
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=10000)
