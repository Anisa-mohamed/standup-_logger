"""
Weather service using the Open-Meteo free API (no API key required).

Architecture notes:
- Always returns a dict — never raises to callers.
- Timeout of 5 s prevents slow weather API from blocking standup submissions.
- WMO weather interpretation codes mapped to human-readable strings.
"""
import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)

# WMO Weather Interpretation Codes → readable labels
WMO_CODE_MAP = {
    0: 'Clear sky',
    1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
    45: 'Fog', 48: 'Depositing rime fog',
    51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle',
    61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
    71: 'Slight snow', 73: 'Moderate snow', 75: 'Heavy snow',
    77: 'Snow grains',
    80: 'Slight showers', 81: 'Moderate showers', 82: 'Violent showers',
    85: 'Slight snow showers', 86: 'Heavy snow showers',
    95: 'Thunderstorm', 96: 'Thunderstorm with slight hail',
    99: 'Thunderstorm with heavy hail',
}

OPEN_METEO_URL = 'https://api.open-meteo.com/v1/forecast'
FALLBACK = {'temperature': None, 'weather_condition': 'Unavailable'}


def fetch_current_weather(lat: float = None, lon: float = None) -> dict:
    """
    Fetch current temperature and weather condition from Open-Meteo.

    Args:
        lat: Latitude (defaults to app config OPEN_METEO_LAT)
        lon: Longitude (defaults to app config OPEN_METEO_LON)

    Returns:
        dict with keys 'temperature' (float|None) and 'weather_condition' (str)
    """
    try:
        lat = lat or current_app.config.get('OPEN_METEO_LAT', 1.2921)
        lon = lon or current_app.config.get('OPEN_METEO_LON', 36.8219)

        params = {
            'latitude': lat,
            'longitude': lon,
            'current_weather': True,
            'temperature_unit': 'celsius',
            'timezone': 'Africa/Nairobi',
        }

        response = requests.get(OPEN_METEO_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        current = data.get('current_weather', {})
        temp = current.get('temperature')
        wmo_code = int(current.get('weathercode', -1))
        condition = WMO_CODE_MAP.get(wmo_code, f'WMO code {wmo_code}')
        weather_time = current.get('time')

        return {
            'temperature': temp,
            'weather_condition': condition,
            'weather_time': weather_time,
        }

    except requests.exceptions.Timeout:
        logger.warning('Weather API timed out — using fallback values.')
        return FALLBACK
    except requests.exceptions.RequestException as exc:
        logger.warning('Weather API request failed: %s', exc)
        return FALLBACK
    except Exception as exc:
        logger.error('Unexpected error in weather service: %s', exc)
        return FALLBACK
