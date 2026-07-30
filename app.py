import requests
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """Render the landing page and handle city-based weather searches."""
    weather_data = None
    error_message = None

    if request.method == "POST":
        city = request.form.get("city", "").strip()

        if not city:
            error_message = "Please enter a city name to search."
        else:
            try:
                geocode_url = "https://nominatim.openstreetmap.org/search"
                geocode_params = {
                    "q": city,
                    "format": "json",
                    "limit": 1,
                }
                geocode_headers = {"User-Agent": "SkyCast-Flask-App/1.0"}
                geocode_response = requests.get(
                    geocode_url,
                    params=geocode_params,
                    headers=geocode_headers,
                    timeout=10,
                )
                geocode_response.raise_for_status()
                geocode_results = geocode_response.json()

                if not geocode_results:
                    error_message = f"We couldn't find a location matching '{city}'."
                else:
                    # Convert the city query into coordinates using Nominatim.
                    location = geocode_results[0]
                    lat = float(location["lat"])
                    lon = float(location["lon"])
                    place_details = extract_location_details(location)

                    # Fetch the live forecast using the coordinates from the geocoder.
                    forecast_url = "https://api.open-meteo.com/v1/forecast"
                    forecast_params = {
                        "latitude": lat,
                        "longitude": lon,
                        "current": [
                            "temperature_2m",
                            "relative_humidity_2m",
                            "apparent_temperature",
                            "weather_code",
                            "wind_speed_10m",
                            "pressure_msl",
                        ],
                        "timezone": "auto",
                    }
                    forecast_response = requests.get(
                        forecast_url,
                        params=forecast_params,
                        timeout=10,
                    )
                    forecast_response.raise_for_status()
                    forecast_data = forecast_response.json()

                    current = forecast_data.get("current", {})
                    weather_code = current.get("weather_code")
                    weather_condition = map_weather_code(weather_code)
                    weather_data = {
                        "city": place_details["city"],
                        "country": place_details["country"],
                        "temperature": current.get("temperature_2m"),
                        "feels_like": current.get("apparent_temperature"),
                        "condition": weather_condition,
                        "humidity": current.get("relative_humidity_2m"),
                        "wind_speed": current.get("wind_speed_10m"),
                        "pressure": current.get("pressure_msl"),
                        "latitude": lat,
                        "longitude": lon,
                        "weather_icon": get_weather_icon(weather_code),
                    }
            except requests.RequestException:
                error_message = "Weather service is temporarily unavailable. Please try again shortly."
            except ValueError:
                error_message = "The location data could not be processed. Please try a different city."

    return render_template("index.html", weather_data=weather_data, error_message=error_message)


def extract_location_details(location):
    """Extract a readable city and country name from a Nominatim result."""
    address = location.get("address") or {}
    if not isinstance(address, dict):
        address = {}

    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("suburb")
        or address.get("state")
        or address.get("county")
        or address.get("province")
        or address.get("state_district")
    )

    country = address.get("country")
    display_name = (location.get("display_name") or "").strip()
    display_parts = [part.strip() for part in display_name.split(",") if part.strip()]

    if not city and display_parts:
        city = display_parts[0]

    if not country and len(display_parts) > 1:
        country = display_parts[-1]

    return {
        "city": city.title() if city else "Unknown",
        "country": country or "Unknown",
    }


def map_weather_code(code):
    weather_map = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Rain showers",
        81: "Heavy rain showers",
        82: "Violent rain showers",
        85: "Snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with heavy hail",
    }
    return weather_map.get(code, "Weather conditions unavailable")


def get_weather_icon(code):
    icon_map = {
        0: "☀️",
        1: "🌤️",
        2: "⛅",
        3: "☁️",
        45: "🌫️",
        48: "🌫️",
        51: "🌦️",
        53: "🌦️",
        55: "🌧️",
        61: "🌧️",
        63: "🌧️",
        65: "⛈️",
        71: "🌨️",
        73: "🌨️",
        75: "🌨️",
        77: "🌨️",
        80: "🌦️",
        81: "🌧️",
        82: "⛈️",
        85: "🌨️",
        95: "⛈️",
        96: "⛈️",
        99: "⛈️",
    }
    return icon_map.get(code, "🌍")


if __name__ == "__main__":
    app.run(debug=True)
