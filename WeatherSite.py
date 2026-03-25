from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from collections import defaultdict
from datetime import datetime
from statistics import mode, StatisticsError

app = FastAPI()
API_KEY = "66f2e97b7f70d2617f9c6d2e513a1b4b"

templates = Jinja2Templates(directory="Templates")


def find_loc(city_name: str):
    url = (
        "https://api.openweathermap.org/geo/1.0/direct"
        f"?q={city_name}&appid={API_KEY}&limit=1"
    )
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    hits = r.json()

    if not hits:
        raise HTTPException(status_code=404, detail="City not found")

    return hits[0]["lat"], hits[0]["lon"]


def find_weather(lat: float, lon: float):
    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    )
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()

    grouped = defaultdict(list)

    for item in data.get("list", []):
        dt_txt = item.get("dt_txt", "")
        date_key = (
            dt_txt.split(" ")[0]
            if dt_txt
            else datetime.utcfromtimestamp(item["dt"]).date().isoformat()
        )

        grouped[date_key].append(
            {
                "dt": item["dt"],
                "temp": item["main"]["temp"],
                "humidity": item["main"]["humidity"],
                "weather": item["weather"][0]["main"],
            }
        )

    return dict(grouped)


@app.get("/forecast/{cityName}", response_class=HTMLResponse)
async def read_root(cityName: str, request: Request):
    lat, lon = find_loc(cityName)
    data = find_weather(lat, lon)

    sorted_dates = sorted(data.keys())[:5]
    days = []

    for date in sorted_dates:
        temps = [p["temp"] for p in data[date]]
        humidity = [p["humidity"] for p in data[date]]
        weathers = [p["weather"] for p in data[date]]

        try:
            weather_summary = mode(weathers)
        except StatisticsError:
            weather_summary = weathers[0] if weathers else "Unknown"

        days.append(
            {
                "date": date,
                "weather": weather_summary,
                "temps": temps,
                "humidity": humidity,
            }
        )

    return templates.TemplateResponse(
        request,
        "forecastIndex.html",
        {
            "cityName": cityName,
            "days": days,
        },
    )