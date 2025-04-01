from flask import Flask, request, jsonify
import aiohttp
import json
import base64
import os
from datetime import datetime
import requests

app = Flask(__name__)

LOG_FILE = "command_logs.json"  # Vercel’de dosya yazma geçici olduğundan dikkatli olun
WEATHER_API_KEY = "5e60d261dad9c3825ee5f7ffabc983b8"  # OpenWeatherMap API key

# Log dosyası yoksa oluştur (Vercel’de geçici dosya sistemi var)
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as f:
        json.dump([], f)

# Discord User Info Functions
async def get_discord_info(user_id):
    url = f"https://discordlookup.mesalytic.moe/v1/user/{user_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return None

async def get_token_info(user_id):
    encoded_bytes = base64.b64encode(user_id.encode("utf-8"))
    token_fp = str(encoded_bytes, "utf-8")
    return token_fp

def save_to_json(query_id, queried_id, results, token_fp):
    log_entry = {
        "query_id": query_id,
        "queried_id": queried_id,
        "timestamp": datetime.utcnow().isoformat(),
        "results": results,
        "token_first_part": token_fp
    }
    
    try:
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
    except:
        logs = []
    
    logs.append(log_entry)
    
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=4)

# API Endpoint: Discord Kullanıcı Bilgisi
@app.route('/api/query', methods=['GET'])
async def discord_query():
    user_id = request.args.get('user_id')
    query_id = str(datetime.now().timestamp())

    if not user_id:
        response = {"error": "Please provide a Discord user ID!"}
        save_to_json(query_id, None, response, None)
        return jsonify(response), 400

    data = await get_discord_info(user_id)
    token_fp = await get_token_info(user_id)

    if not data:
        response = {"error": "Invalid ID or user not found!"}
        save_to_json(query_id, user_id, response, token_fp)
        return jsonify(response), 404

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

    save_to_json(query_id, user_id, data, token_fp)
    return jsonify(response), 200

# API Endpoint: IP Bilgisi
@app.route('/api/ip', methods=['GET'])
def ip_query():
    ip_address = request.args.get('ip_address')

    if not ip_address:
        return jsonify({"error": "Please provide an IP address!"}), 400

    ip_api_response = requests.get(f"http://ip-api.com/json/{ip_address}")
    json_ip_data = json.loads(ip_api_response.text)

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
            f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&APPID={WEATHER_API_KEY}&units=metric"
        )
        json_weather_data = json.loads(weather_api_response.text)
        response["temperature"] = f"{json_weather_data['main']['temp']}°C"
    except Exception as e:
        print(f"Error retrieving temperature: {e}")

    return jsonify(response), 200

# Vercel için gerekli başlatma
if __name__ == "__main__":
    app.run()