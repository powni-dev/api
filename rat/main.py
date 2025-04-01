from flask import Flask, jsonify
import base64
import requests
from datetime import datetime

# Flask uygulamasını oluştur
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

        # Yanıtı oluştur
        result = {
            "User_Info": {
                "ID": data.get('id'),
                "Username": data.get('username'),
                "Global_Name": data.get('global_name'),
                "Created_At": data.get('created_at')
            },
            "Token_Info": {
                "User_Token_First_Part": token_fp
            }
        }

        return jsonify(result)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Discord API error: {str(e)}"}), 502
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# WSGI uyumluluğu için
def create_app():
    return app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
