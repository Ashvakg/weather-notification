from flask import Flask, jsonify, request
import requests

# Step 1: Create Flask application instance
app = Flask(__name__)

# Step 2: Define the route for fetching weather data
@app.route('/get-weather/<city>', methods=['GET'])
def get_weather(city):
    # Use your OpenWeatherMap API key
    api_key = 'eee8974565d3ca59cbc537b0775a458d'
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}'

    try:
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Parse and return the weather data
        weather_data = response.json()
        return jsonify(weather_data)

    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': f'HTTP error occurred: {http_err}'}), 400
    except requests.exceptions.RequestException as req_err:
        return jsonify({'error': f'Request error occurred: {req_err}'}), 500

# Step 3: Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
