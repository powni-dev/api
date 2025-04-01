from flask import Flask, request, jsonify
import requests
import base64
import os

app = Flask(__name__)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "5e60d261dad9c3825ee5f7ffabc983b8")

# Discord User Info Functions
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

# API Endpoint: Discord Kullanıcı Bilgisi
@app.route('/api/query', methods=['GET'])
def discord_query():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Please provide a Discord user ID!"}), 400

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

# API Endpoint: IP Bilgisi
@app.route('/api/ip', methods=['GET'])
def ip_query():
    ip_address = request.args.get('ip_address')
    if not ip_address:
        return jsonify({"error": "Please provide an IP address!"}), 400

    try:
        ip_api_response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=5)
        json_ip_data = ip_api_response.json()
    except requests.RequestException as e:
        return jsonify({"error": f"IP lookup failed: {str(e)}"}), 500

    if json_ip_data["status"] != "success":
        return jsonify({"error": "Invalid IP address or lookup failed!"}), 404

    lat = str(json_ip_data["lat"])
    lon = str(json_ip_data["lon"])
    coords = f"{lat}, {lon}"

    response = {
        "country": json_ip_data["country"],
        "region": json_ip_data["regionName"],
        "city": json_ip_data["city"],
        "zip_code": json_ip_data["zip"],
        "coordinates": coords,
        "isp": json_ip_data["isp"]
    }

    try:
        weather_api_response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&APPID={WEATHER_API_KEY}&units=metric",
            timeout=5
        )
        json_weather_data = weather_api_response.json()
        response["temperature"] = f"{json_weather_data['main']['temp']}°C"
    except requests.RequestException as e:
        print(f"Error retrieving temperature: {e}")

    return jsonify(response), 200

# Kök dizin için basit bir yanıt
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to Ratistan API! Use /api/query or /api/ip"}), 200

if __name__ == "__main__":
    app.run()
