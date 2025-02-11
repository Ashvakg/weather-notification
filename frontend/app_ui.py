import streamlit as st
import requests
import geocoder
import pycountry
import pyrebase
import time

# --- SET PAGE CONFIG ---
st.set_page_config(page_title="🌦️ Weather Notification App", page_icon="☀️", layout="centered")

st.write("Easily check the weather forecast and set alerts for sunny days! 🌞")

# --- FIREBASE CONFIGURATION ---
firebase_config = {
    "apiKey": "AIzaSyDEjuWoxX2XeZ9s4djLAU8YN0tdamyRt20",
    "authDomain": "weather-notification-7826b.firebaseapp.com",
    "databaseURL": "https://weather-notification-7826b-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "weather-notification-7826b",
    "storageBucket": "weather-notification-7826b.appspot.com",
    "messagingSenderId": "421548442919",
    "appId": "1:421548442919:web:8e4e19846cc67bfde29502"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# OpenWeather's Icon URL format
OPENWEATHER_ICON_URL = "http://openweathermap.org/img/wn/{}.png"

# --- FUNCTION TO REGISTER A NEW USER ---
def register_user():
    st.title("📝 Register")

    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Password", type="password")
    confirm_password = st.text_input("🔑 Confirm Password", type="password")

    if st.button("🚀 Register"):
        if password == confirm_password:
            try:
                user = auth.create_user_with_email_and_password(email, password)
                st.success(f"✅ Account Created for {email}! Please log in.")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            st.error("❌ Passwords do not match!")

# --- FUNCTION TO LOGIN A USER ---
def login_user():
    st.title("🔑 Login")

    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Password", type="password")

    if st.button("🔓 Login"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state["user"] = user
            st.success(f"✅ Logged in as {email}!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {e}")

# --- FUNCTION TO GET GPS LOCATION ---
def get_location():
    g = geocoder.ip("me")
    if g.ok:
        return g.city
    return None

# Fetch weather data
def fetch_weather(city):
    url = f"http://127.0.0.1:5000/get-weather/{city}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return None

# Display Weather
def display_weather(weather_data):
    if not weather_data:
        st.error("❌ Could not fetch weather data.")
        return

    city = weather_data["city"]
    country = weather_data["country"]
    forecasts = weather_data["forecasts"]

    st.subheader(f"📍 Weather in {city}, {country}")

    for forecast in forecasts:
        date = forecast["date"]
        temp = forecast["temperature"]
        condition = forecast["description"].capitalize()  # Ensure proper capitalization
        icon_code = forecast.get("icon", "01d")  # Default to clear sky if missing

        # Construct OpenWeather's official icon URL
        icon_url = OPENWEATHER_ICON_URL.format(icon_code)

        # Display the forecast with the correct icon
        st.markdown(
            f"""
            <div style="display: flex; align-items: center;">
                <img src="{icon_url}" width="50" height="50">
                <span style="margin-left: 10px;"><b>{date}:</b> {condition} ({temp}°C)</span>
            </div>
            """,
            unsafe_allow_html=True
        )

# --- FUNCTION TO DISPLAY MAIN APP ---
def weather_app():
    st.title("☀️ Weather Notification App")
    user_email = st.session_state["user"]["email"]
    st.write(f"Welcome, **{user_email}**!")

    # --- CHOOSE LOCATION ---
    st.subheader("🌍 Choose Your Location")
    city = st.text_input("Enter City Name", get_location())

    # --- GET WEATHER FORECAST ---
    if st.button("🔍 Get Weather Forecast"):
        weather_data = fetch_weather(city)
        display_weather(weather_data)

    # --- SET WEATHER ALERTS ---
    st.subheader("🔔 Set Alerts")
    notification_frequency = st.selectbox("⏳ Notification Frequency", ["Daily", "Every 3 Days", "Weekly"])

    # --- SAVE PREFERENCES ---
    if st.button("💾 Save Preferences"):
        user_id = st.session_state["user"]["localId"]
        url = "http://localhost:5000/save-preferences"
        data = {"user_id": user_id, "city": city, "notification_frequency": notification_frequency}

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                st.success("✅ Preferences saved successfully!")
            else:
                st.error(f"❌ Failed to save preferences: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"🚨 Server error: {e}")

    # --- FCM SUBSCRIPTION ---
    st.subheader("🔔 Notification Subscription")
    if st.button("🔔 Enable Weather Notifications"):
        show_fcm_script(st.session_state["user"]["localId"])

    # --- LOGOUT ---
    if st.button("🚪 Logout"):
        del st.session_state["user"]
        st.success("✅ Logged out successfully!")
        st.rerun()

    # Animated Ticker
    st.markdown(
        f"""
        <marquee style="color: yellow; font-size: 20px;">☀️ Stay Updated! Plan Your Weekend Based on the Best Weather Forecasts! 🌤️</marquee>
        """,
        unsafe_allow_html=True,
    )

# --- FUNCTION TO SHOW FCM SCRIPT ---
def show_fcm_script(user_id):
    st.markdown(f"""
    <script src="https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js"></script>
    <script>
      const firebaseConfig = {{
        {",".join(f'"{k}": "{v}"' for k, v in firebase_config.items())}
      }};
      
      const app = firebase.initializeApp(firebaseConfig);
      const messaging = firebase.messaging();
      
      Notification.requestPermission().then(permission => {{
        if (permission === 'granted') {{
          messaging.getToken({{ vapidKey: 'YOUR_VAPID_KEY_HERE' }})
            .then(token => {{
              fetch('http://localhost:5000/save-fcm-token', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                  user_id: '{user_id}',
                  fcm_token: token
                }})
              }});
            }})
            .catch(error => console.error('Error getting token:', error));
        }}
      }});
    </script>
    """, unsafe_allow_html=True)
    
    st.success("Check your browser for notification permission popup!")

# --- MAIN APP FLOW ---
if "user" not in st.session_state:
    option = st.radio("Select an option:", ["Login", "Register"])
    login_user() if option == "Login" else register_user()
else:
    weather_app()