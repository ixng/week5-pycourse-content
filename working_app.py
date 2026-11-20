"""Terminal weather app: Workshop 6, complete version.

Run it with:  python3 weather_app.py
Needs:        pip install requests

Weather data by Open-Meteo.com (CC BY 4.0).
"""

import requests


# =============================================================================
# 1. Settings
# =============================================================================

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

CAMPUS_NAME = "Campus"
CAMPUS_LATITUDE = 52.38
CAMPUS_LONGITUDE = -1.56

DAILY_VALUES = "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code"
FORECAST_DAYS = 10

# Set to True to use the saved data below instead of calling the API
USE_SAMPLE_DATA = False


# =============================================================================
# 2. Saved data (a real Open-Meteo response from 19 Nov 2026)
# =============================================================================

SAMPLE_FORECAST = {
    "daily": {
        "time": ["2026-11-19", "2026-11-20", "2026-11-21", "2026-11-22", "2026-11-23"],
        "temperature_2m_max": [8.6, 7.0, 6.2, 7.3, 7.7],
        "temperature_2m_min": [6.4, 1.3, -1.6, 3.7, 2.7],
        "precipitation_probability_max": [100, 18, 0, 24, 24],
        "weather_code": [61, 53, 45, 3, 61],
    }
}


# =============================================================================
# 3. Weather codes into words
# =============================================================================

WEATHER_WORDS = {
    0: "Clear sky",
    1: "Mostly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Freezing fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    56: "Light freezing drizzle",
    57: "Freezing drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Freezing rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Showers",
    81: "Heavy showers",
    82: "Violent showers",
    85: "Snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}


def code_to_words(code):
    if code in WEATHER_WORDS:
        return WEATHER_WORDS[code]
    else:
        return "Unknown weather"


# =============================================================================
# 4. The DayForecast class
# =============================================================================

class DayForecast:
    def __init__(self, day, high, low, rain_chance, weather_code):
        self.day = day
        self.high = high
        self.low = low
        self.rain_chance = rain_chance
        self.weather_code = weather_code

    def describe(self):
        words = code_to_words(self.weather_code)
        return f"{self.day}: {self.high}°C / {self.low}°C ({self.rain_chance}% rain), {words}"

    def needs_coat(self):
        if self.high < 12 or self.rain_chance >= 50:
            return True
        else:
            return False

    def is_warm(self):
        if self.high >= 15:
            return True
        else:
            return False


# =============================================================================
# 5. Talking to the API
# =============================================================================

def fetch_daily_data(latitude, longitude):
    # Returns the "daily" dictionary of lists, or None if the request failed
    if USE_SAMPLE_DATA:
        return SAMPLE_FORECAST["daily"]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": DAILY_VALUES,
        "timezone": "Europe/London",
        "forecast_days": FORECAST_DAYS,
    }
    try:
        response = requests.get(FORECAST_URL, params=params, timeout=10)
    except requests.RequestException:
        print("Couldn't reach the weather service. Check your internet connection.")
        return None

    data = response.json()
    if response.status_code != 200:
        print("The weather service sent back an error:", data.get("reason"))
        return None
    return data["daily"]


def get_forecast(latitude, longitude):
    # Turns the lists from the API into one DayForecast object per day
    daily = fetch_daily_data(latitude, longitude)
    if daily is None:
        return []

    week = []
    for i in range(len(daily["time"])):
        day = DayForecast(
            daily["time"][i],
            daily["temperature_2m_max"][i],
            daily["temperature_2m_min"][i],
            daily["precipitation_probability_max"][i],
            daily["weather_code"][i],
        )
        week.append(day)
    return week


def find_place(name):
    # Returns the best match as a dictionary, or None if nothing matched
    params = {"name": name, "count": 1}
    try:
        response = requests.get(GEOCODING_URL, params=params, timeout=10)
    except requests.RequestException:
        print("Couldn't reach the place search. Check your internet connection.")
        return None

    data = response.json()
    if "results" in data:
        return data["results"][0]
    else:
        return None


# =============================================================================
# 6. Showing the forecast
# =============================================================================

def show_week(week):
    for day in week:
        print(day.describe())


def show_coat_days(week):
    coat_days = []
    for day in week:
        if day.needs_coat():
            coat_days.append(day.day)

    if len(coat_days) == 0:
        print("No coat needed this week.")
    else:
        print("Bring a coat on:")
        for day_name in coat_days:
            print(f"  {day_name}")


def show_warmest_day(week):
    warmest = week[0]
    for day in week:
        if day.high > warmest.high:
            warmest = day

    print(f"Warmest day: {warmest.day} ({warmest.high}°C)")
    if warmest.is_warm():
        print("That counts as warm!")


# =============================================================================
# 7. The menu
# =============================================================================

def show_menu(place_name):
    print()
    print(f"=== {place_name} weather ===")
    print("1  Show the week")
    print("2  Which days need a coat?")
    print("3  Warmest day")
    print("4  Change place")
    print("q  Quit")


def run_app():
    place_name = CAMPUS_NAME
    week = get_forecast(CAMPUS_LATITUDE, CAMPUS_LONGITUDE)

    running = True
    while running:
        show_menu(place_name)
        choice = input("Choose an option: ").strip().lower()

        if choice in ["1", "2", "3"] and len(week) == 0:
            print("No forecast loaded. Try option 4, or set USE_SAMPLE_DATA = True.")
        elif choice == "1":
            show_week(week)
        elif choice == "2":
            show_coat_days(week)
        elif choice == "3":
            show_warmest_day(week)
        elif choice == "4":
            search = input("Type a city or town: ").strip()
            place = find_place(search)
            if place is None:
                print(f"Couldn't find {search}.")
            else:
                place_name = f"{place['name']}, {place['country']}"
                week = get_forecast(place["latitude"], place["longitude"])
        elif choice == "q":
            print("Bye!")
            running = False
        else:
            print("Please type 1, 2, 3, 4 or q.")


# =============================================================================
# Run it
# =============================================================================

run_app()
