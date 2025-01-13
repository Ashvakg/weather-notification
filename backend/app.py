from flask import Flask, jsonify, request
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv('OPENWEATHER_API_KEY')

app = Flask(__name__)

@app.route('/get-weather/<city>', methods=['GET'])
def get_weather(city):
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        forecasts = [
            {
                "date": forecast["dt_txt"],
                "temperature": forecast["main"]["temp"],
                "description": forecast["weather"][0]["description"]
            }
            for forecast in data["list"]
        ]

        return jsonify({
            "city": data["city"]["name"],
            "country": data["city"]["country"],
            "forecasts": forecasts
        })
    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": f"HTTP error occurred: {http_err}"}), 400
    except requests.exceptions.RequestException as req_err:
        return jsonify({"error": f"Request error occurred: {req_err}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
