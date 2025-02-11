from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, db, messaging
import requests
import os
import time
from dotenv import load_dotenv
import threading

app = Flask(__name__)

# --- Load environment variables ---
load_dotenv()
API_KEY = os.getenv('OPENWEATHER_API_KEY')
FCM_SERVER_KEY = os.getenv('FCM_SERVER_KEY')

# --- Initialize Firebase (Only if not already initialized) ---
if not firebase_admin._apps:
    cred = credentials.Certificate("C:/Blue card/project/weather-notification/backend/weather-notification.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://weather-notification-7826b-default-rtdb.europe-west1.firebasedatabase.app'
    })

# --- SAVE USER PREFERENCES ROUTE ---
@app.route('/save-preferences', methods=['POST'])
def save_preferences():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Missing JSON payload"}), 400
        
        required_fields = ["user_id", "city", "notification_frequency"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_id = data["user_id"]
        db.reference(f'users/{user_id}/preferences').push(data)
        
        return jsonify({"message": "Preferences saved successfully!"}), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to save preferences: {str(e)}"}), 500

# --- SAVE FCM TOKEN ROUTE ---
@app.route('/save-fcm-token', methods=['POST'])
def save_fcm_token():
    try:
        data = request.get_json()
        user_id = data["user_id"]
        fcm_token = data["fcm_token"]
        
        # Save token under user's node
        db.reference(f'users/{user_id}/fcm_tokens').push(fcm_token)
        
        return jsonify({"message": "FCM token saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save FCM token: {str(e)}"}), 500

# --- WEATHER FORECAST ROUTE ---
@app.route('/get-weather/<city>', methods=['GET'])
def get_weather(city):
    if not API_KEY:
        return jsonify({"error": "Missing API key"}), 500

    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "city" not in data or "list" not in data:
            return jsonify({"error": "Invalid response from API"}), 500

        forecasts = [
            {
                "date": forecast["dt_txt"],
                "temperature": forecast["main"]["temp"],
                "description": forecast["weather"][0]["description"],
                "icon": forecast["weather"][0]["icon"]  # Include OpenWeather's icon code
            }
            for forecast in data["list"][:5]  # Show next 5 forecasts
        ]

        return jsonify({
            "city": data["city"]["name"],
            "country": data["city"]["country"],
            "forecasts": forecasts
        })
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request error: {str(e)}"}), 500

# --- WEATHER ALERT SCHEDULER ---
def check_weather_and_notify():
    users = db.reference('users').get()
    if not users:
        return
    
    for user_id, user_data in users.items():
        if "preferences" in user_data:
            for pref_key, pref in user_data["preferences"].items():
                city = pref.get("city", "Berlin")  # Default to Berlin
                url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
                response = requests.get(url)
                
                if response.status_code == 200:
                    weather_data = response.json()
                    forecast = weather_data["list"][0]
                    condition = forecast["weather"][0]["description"]
                    
                    if "clear sky" in condition or "sunny" in condition:
                        send_push_notification(user_id, city, condition)

# --- SEND PUSH NOTIFICATION ---
def send_push_notification(user_id, city, condition):
    # Get all FCM tokens for the user
    tokens = db.reference(f'users/{user_id}/fcm_tokens').get()
    
    if not tokens:
        return  # No tokens registered
    
    # Send to all devices
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title="🌞 Perfect Weather Alert!",
            body=f"The weather in {city} is **{condition}**! Enjoy a great day outside! 🌤️",
        ),
        tokens=list(tokens.values())
    )
    messaging.send_multicast(message)

# --- SCHEDULE WEATHER ALERTS ROUTE ---
@app.route('/schedule-weather-alerts', methods=['GET'])
def schedule_alerts():
    def scheduler():
        while True:
            check_weather_and_notify()
            time.sleep(21600)  # Run every 6 hours
    
    thread = threading.Thread(target=scheduler, daemon=True)
    thread.start()
    return jsonify({"message": "Weather alerts scheduler started."})

# --- DEBUG ROUTE ---
@app.route("/", methods=['GET'])
def home():
    return jsonify({"message": "Flask Server is Running!"})

# --- SHOW AVAILABLE ROUTES ---
@app.route('/routes', methods=['GET'])
def list_routes():
    return jsonify({"routes": [str(rule) for rule in app.url_map.iter_rules()]})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)