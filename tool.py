import httpx
import json
import os
from langchain_core.tools import tool
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

#load environment variables
load_dotenv
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# =========================
#  INTERNAL HELPERS
# =========================
def _weather_code_to_text(code: int) -> str:
    weather_codes = {
        0: "clear sky",
        1: "mainly clear",
        2: "partly cloudy",
        3: "overcast",
        45: "fog",
        48: "depositing rime fog",
        51: "light drizzle",
        53: "moderate drizzle",
        55: "dense drizzle",
        56: "light freezing drizzle",
        57: "dense freezing drizzle",
        61: "slight rain",
        63: "moderate rain",
        65: "heavy rain",
        66: "light freezing rain",
        67: "heavy freezing rain",
        71: "slight snow fall",
        73: "moderate snow fall",
        75: "heavy snow fall",
        77: "snow grains",
        80: "slight rain showers",
        81: "moderate rain showers",
        82: "violent rain showers",
        85: "slight snow showers",
        86: "heavy snow showers",
        95: "thunderstorm",
        96: "thunderstorm with slight hail",
        99: "thunderstorm with heavy hail",
    }
    return weather_codes.get(code, f"weather code {code}")


def _travel_advice(
    max_temp: float,
    min_temp: float,
    max_precip_prob: float,
    total_rain_mm: float,
    max_wind_kmh: float,
) -> str:
    issues = []

    if max_precip_prob >= 70 or total_rain_mm >= 15:
        issues.append("high chance of rain")
    elif max_precip_prob >= 40 or total_rain_mm >= 5:
        issues.append("some rain possible")

    if max_temp >= 34:
        issues.append("very hot daytime temperatures")
    elif max_temp <= 18:
        issues.append("cool conditions")

    if max_wind_kmh >= 35:
        issues.append("strong winds")

    if not issues:
        return "Good time to visit for general outdoor activities."
    if len(issues) == 1 and issues[0] == "some rain possible":
        return "Generally fine to visit, but bring rain protection."
    return "Visit is possible, but conditions may be less ideal due to " + ", ".join(issues) + "."


def get_coordinates(city: str):
    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    response = httpx.get(GEOCODE_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    results = data.get("results")
    if not results:
        return None

    top = results[0]
    return {
        "name": top.get("name"),
        "country": top.get("country"),
        "admin1": top.get("admin1"),
        "latitude": top.get("latitude"),
        "longitude": top.get("longitude"),
        "timezone": top.get("timezone"),
    }

# =========================
# TOOL FUNCTION
# =========================

@tool
def search_flights_skyline(
    departure_id: Optional[str] = None,
    arrival_id: Optional[str] = None,
    outbound_date: Optional[str] = None,
    return_date: Optional[str] = None,
    trip_type: int = 2,
    travel_class: int = 1,
    adults: int = 1,
    children: int = 0,
    infants_in_seat: int = 0,
    infants_on_lap: int = 0,
    currency: str = "MYR",
    hl: str = "en",
    gl: Optional[str] = None,
    sort_by: int = 1,
    stops: int = 0,
    bags: int = 0,
    max_price: Optional[int] = None,
    include_airlines: Optional[str] = None,
    exclude_airlines: Optional[str] = None,
    outbound_times: Optional[str] = None,
    return_times: Optional[str] = None,
    emissions: Optional[int] = None,
    layover_duration: Optional[str] = None,
    exclude_conns: Optional[str] = None,
    max_duration: Optional[int] = None,
    show_hidden: bool = False,
    exclude_basic: bool = False,
    deep_search: bool = True,
    no_cache: bool = False,
    departure_token: Optional[str] = None,
    booking_token: Optional[str] = None,
    multi_city_json: Optional[str] = None,
) -> str:

    """
    Search holiday flight options using Google Flights via SerpApi.

    Use this tool when the user asks for:
    - flight prices
    - cheapest flights
    - one-way or round-trip holiday flights
    - multi-city itineraries
    - airline filtering
    - nonstop flights
    - budget-based flight searches

    Inputs can include departure airport, arrival airport, dates, passengers, class, stops, budget, airline preferences, and timing preferences.
    """

    if not SERPAPI_KEY:
        return "Error: SERPAPI_KEY is missing."

    if include_airlines and exclude_airlines:
        return "Error: include_airlines and exclude_airlines cannot be used together."

    if booking_token and departure_token:
        return "Error: booking_token and departure_token cannot be used together."

    if trip_type == 1 and not return_date and not departure_token and not booking_token:
        return "Error: return_date is required for round-trip searches."

    if trip_type in (1, 2) and not booking_token and not departure_token:
        if not departure_id or not arrival_id or not outbound_date:
            return "Error: departure_id, arrival_id, and outbound_date are required."

    if trip_type == 3 and not multi_city_json and not departure_token and not booking_token:
        return "Error: multi_city_json is required for multi-city searches."

    url = "https://serpapi.com/search.json"

    params: Dict[str, Any] = {
        "engine": "google_flights",
        "api_key": SERPAPI_KEY,
        "currency": currency,
        "hl": hl,
        "type": trip_type,
        "travel_class": travel_class,
        "adults": adults,
        "children": children,
        "infants_in_seat": infants_in_seat,
        "infants_on_lap": infants_on_lap,
        "sort_by": sort_by,
        "stops": stops,
        "bags": bags,
        "show_hidden": str(show_hidden).lower(),
        "exclude_basic": str(exclude_basic).lower(),
        "deep_search": str(deep_search).lower(),
        "no_cache": str(no_cache).lower(),
        "output": "json",
    }

    if gl:
        params["gl"] = gl

    if departure_id:
        params["departure_id"] = departure_id
    if arrival_id:
        params["arrival_id"] = arrival_id
    if outbound_date:
        params["outbound_date"] = outbound_date
    if return_date:
        params["return_date"] = return_date
    if max_price is not None:
        params["max_price"] = max_price
    if include_airlines:
        params["include_airlines"] = include_airlines
    if exclude_airlines:
        params["exclude_airlines"] = exclude_airlines
    if outbound_times:
        params["outbound_times"] = outbound_times
    if return_times:
        params["return_times"] = return_times
    if emissions is not None:
        params["emissions"] = emissions
    if layover_duration:
        params["layover_duration"] = layover_duration
    if exclude_conns:
        params["exclude_conns"] = exclude_conns
    if max_duration is not None:
        params["max_duration"] = max_duration
    if departure_token:
        params["departure_token"] = departure_token
    if booking_token:
        params["booking_token"] = booking_token
    if multi_city_json:
        params["multi_city_json"] = multi_city_json

    try:
        response = httpx.get(url, params=params, timeout=40.0)
        response.raise_for_status()
        data = response.json()

        if data.get("error"):
            return f"SerpApi error: {data['error']}"

        search_status = data.get("search_metadata", {}).get("status")
        if search_status and search_status not in {"Success", "Cached"}:
            return f"Search status: {search_status}"

        flights = data.get("best_flights") or data.get("other_flights") or []

        if not flights:
            return json.dumps({
                "query_used": params,
                "message": "No flights found for these criteria."
            }, ensure_ascii=False, indent=2)

        simplified_results = []

        for flight in flights[:5]:
            segments = flight.get("flights", [])
            first_segment = segments[0] if segments else {}
            last_segment = segments[-1] if segments else {}

            simplified_results.append({
                "price": flight.get("price"),
                "type": flight.get("type"),
                "airline": first_segment.get("airline"),
                "departure_airport": first_segment.get("departure_airport", {}).get("id"),
                "departure_time": first_segment.get("departure_airport", {}).get("time"),
                "arrival_airport": last_segment.get("arrival_airport", {}).get("id"),
                "arrival_time": last_segment.get("arrival_airport", {}).get("time"),
                "duration_minutes": flight.get("total_duration"),
                "stops": len(segments) - 1 if segments else None,
                "carbon_emissions_kg": flight.get("carbon_emissions", {}).get("this_flight"),
                "booking_token": flight.get("booking_token"),
                "segments": [
                    {
                        "airline": s.get("airline"),
                        "flight_number": s.get("flight_number"),
                        "departure_airport": s.get("departure_airport", {}).get("id"),
                        "departure_time": s.get("departure_airport", {}).get("time"),
                        "arrival_airport": s.get("arrival_airport", {}).get("id"),
                        "arrival_time": s.get("arrival_airport", {}).get("time"),
                        "duration_minutes": s.get("duration"),
                        "airplane": s.get("airplane"),
                        "travel_class": s.get("travel_class"),
                        "legroom": s.get("legroom"),
                        "extensions": s.get("extensions", []),
                    }
                    for s in segments
                ]
            })

        output = {
            "search_summary": {
                "departure_id": departure_id,
                "arrival_id": arrival_id,
                "outbound_date": outbound_date,
                "return_date": return_date,
                "trip_type": trip_type,
                "travel_class": travel_class,
                "adults": adults,
                "children": children,
                "currency": currency,
                "sort_by": sort_by,
                "stops": stops,
            },
            "price_insights": data.get("price_insights"),
            "top_flights": simplified_results,
        }

        return json.dumps(output, ensure_ascii=False, indent=2)

    except httpx.HTTPStatusError as e:
        return f"HTTP error from SerpApi: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error fetching flights from Google Flights: {str(e)}"
    
@tool
def research_vacation_vibe(location: str) -> str:
    """
    Research the travel vibe, quiet areas, hidden gems, and practical local tips
    for a destination. Input should be a city, island, or region name.
    Example: "Langkawi"
    """
    if not TAVILY_API_KEY:
        return "Error: TAVILY_API_KEY is missing."

    url = "https://api.tavily.com/search"

    payload = {
        "api_key": TAVILY_API_KEY,
        "query": (
            f"best quiet areas to stay, hidden gems, safe neighborhoods, "
            f"and local travel tips in {location} for a holiday"
        ),
        "search_depth": "advanced",
        "max_results": 5,
        "topic": "general"
    }

    try:
        response = httpx.post(url, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()

        if data.get("error"):
            return f"Error researching location: {data['error']}"

        results = data.get("results", [])
        if not results:
            return f"No useful travel research found for {location}."

        lines = []
        for r in results[:5]:
            title = r.get("title", "No title")
            content = r.get("content", "No content")
            lines.append(f"- {title}: {content}")

        return "\n".join(lines)

    except httpx.HTTPStatusError as e:
        return f"HTTP error researching location: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error researching location: {str(e)}"
    
import httpx
from langchain_core.tools import tool

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


@tool
def get_destination_weather(city: str, forecast_days: int = 3) -> str:
    """
    Get current weather, short forecast, rain risk, and travel recommendation
    for a destination using Open-Meteo.
    
    Args:
        city: City, island, or region name, e.g. 'Langkawi'
        forecast_days: Number of forecast days to summarize, default 3
    """
    try:
        location = get_coordinates(city)
        if not location:
            return f"Location not found: {city}"

        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "timezone": "auto",
            "forecast_days": max(1, min(forecast_days, 7)),
            "current": ",".join([
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
            ]),
            "hourly": ",".join([
                "precipitation_probability",
                "precipitation",
            ]),
            "daily": ",".join([
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max",
            ]),
        }

        response = httpx.get(FORECAST_URL, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        dates = daily.get("time", [])
        tmax = daily.get("temperature_2m_max", [])
        tmin = daily.get("temperature_2m_min", [])
        rain_sum = daily.get("precipitation_sum", [])
        rain_prob = daily.get("precipitation_probability_max", [])
        wind_max = daily.get("wind_speed_10m_max", [])
        daily_codes = daily.get("weather_code", [])

        current_desc = _weather_code_to_text(current.get("weather_code", -1))

        lines = []
        lines.append(
            f"Weather for {location['name']}, "
            f"{location.get('admin1') + ', ' if location.get('admin1') else ''}"
            f"{location.get('country', '')}:"
        )
        lines.append(
            f"- Current: {current.get('temperature_2m')}°C, feels like {current.get('apparent_temperature')}°C, "
            f"{current_desc}, humidity {current.get('relative_humidity_2m')}%, "
            f"wind {current.get('wind_speed_10m')} km/h"
        )

        lines.append("- Forecast:")
        for i in range(min(len(dates), forecast_days)):
            desc = _weather_code_to_text(daily_codes[i]) if i < len(daily_codes) else "unknown"
            advice = _travel_advice(
                tmax[i] if i < len(tmax) else 0,
                tmin[i] if i < len(tmin) else 0,
                rain_prob[i] if i < len(rain_prob) else 0,
                rain_sum[i] if i < len(rain_sum) else 0,
                wind_max[i] if i < len(wind_max) else 0,
            )
            lines.append(
                f"  - {dates[i]}: {desc}; {tmin[i]}–{tmax[i]}°C; "
                f"rain chance up to {rain_prob[i]}%; rain {rain_sum[i]} mm; "
                f"max wind {wind_max[i]} km/h. {advice}"
            )

        return "\n".join(lines)

    except httpx.HTTPStatusError as e:
        return f"HTTP error fetching weather: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error fetching weather: {str(e)}"
    

@tool
def check_exchange_rate(amount: float, from_curr: str = "USD", to_curr: str = "MYR") -> str:
    """
    Convert currency using real-time exchange rates.
    Example: convert 100 USD to MYR
    """

    # Normalize inputs
    from_curr = from_curr.upper()
    to_curr = to_curr.upper()

    if amount <= 0:
        return "Error: Amount must be greater than 0."

    url = f"https://open.er-api.com/v6/latest/{from_curr}"

    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # API-level error
        if data.get("result") != "success":
            return f"Exchange API error: {data.get('error-type', 'Unknown error')}"

        rates = data.get("rates", {})

        if to_curr not in rates:
            return f"Currency '{to_curr}' not supported."

        rate = rates[to_curr]
        converted = amount * rate

        return (
            f"{amount:.2f} {from_curr} ≈ {converted:.2f} {to_curr}\n"
            f"(Rate: 1 {from_curr} = {rate:.4f} {to_curr})"
        )

    except httpx.HTTPStatusError as e:
        return f"HTTP error fetching exchange rate: {e.response.status_code}"
    except Exception as e:
        return f"Error converting currency: {str(e)}"
    
    