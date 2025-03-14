# Weather Notification App

## ✨ Overview
The **Weather Notification App** is a Flask-based application that retrieves 5-day weather forecasts from the OpenWeatherMap API. It processes and refines the data to deliver relevant weather details, helping users plan their sunny days effectively.

---

## ✨ Features
- **City-Based Forecasts**: Fetches weather forecasts for any city worldwide.
- **Detailed Weather Data**:
  - Date and time.
  - Temperature (in Celsius).
  - Weather description.
- **Secure API Keys**: Protects sensitive API keys using environment variables.

---

## 🛠 Setup

### Prerequisites
- Python 3.x installed on your system.
- An OpenWeatherMap API key. You can get one [here](https://openweathermap.org/).

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/weather-notification.git
   cd weather-notification/backend
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   python -m venv env
   # For Windows
   .\env\Scripts\activate
   # For macOS/Linux
   source env/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the root of the `backend` directory and add:
   ```bash
   API_KEY=your_openweathermap_api_key
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```

6. **Access the Application**:
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 🔧 Usage
- Send a GET request to the `/weather` endpoint with a city name as a query parameter.
- Example:
  ```
  http://127.0.0.1:5000/weather?city=London
  ```

The response will include:
```json
{
  "city": "London",
  "forecast": [
    {
      "date_time": "2025-01-14 15:00:00",
      "temperature": "12°C",
      "description": "Clear sky"
    },
    ...
  ]
}
```

---

## 📂 Project Structure
```
weather-notification/
│
├── backend/
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables (not committed)
│
└── README.md               # Project documentation
```

---

## 🤝 Contributions
Contributions are welcome! If you'd like to contribute:
1. Fork the repository.
2. Create a new branch.
3. Submit a pull request with a detailed description.

---

## 📜 License
This project is licensed under the [MIT License](LICENSE).

---

## 🌟 Acknowledgments
- [OpenWeatherMap](https://openweathermap.org/) for providing the weather API.
- Flask documentation for guidance on building RESTful APIs.
