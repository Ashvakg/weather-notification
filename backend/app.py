from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, db
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__)

# --- Load environment variables ---
load_dotenv()
api_key = os.getenv('OPENWEATHER_API_KEY')

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

        # Save preferences under user's Firebase ID
        user_id = data["user_id"]
        db.reference(f'users/{user_id}/preferences').push(data)  # Allow multiple alerts
        
        return jsonify({"message": "Preferences saved successfully!"}), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to save preferences: {str(e)}"}), 500

# --- WEATHER FORECAST ROUTE ---
@app.route('/get-weather/<city>', methods=['GET'])
def get_weather(city):
    if not api_key:
        return jsonify({"error": "Missing API key"}), 500

    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Ensure response contains valid data
        if "city" not in data or "list" not in data:
            return jsonify({"error": "Invalid response from API"}), 500

        # Extract forecast details
        forecasts = [
            {
                "date": forecast["dt_txt"],
                "temperature": forecast["main"]["temp"],
                "description": forecast["weather"][0]["description"]
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
