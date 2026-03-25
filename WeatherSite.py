from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from collections import defaultdict
from datetime import datetime
import pandas as pd
from matplotlib import pyplot as plt
from statistics import mode

# Weather forecast, call app.py for FastAPI, sur siteweb

app = FastAPI()
API_KEY = "66f2e97b7f70d2617f9c6d2e513a1b4b"

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
        date_key = dt_txt.split(" ")[0] if dt_txt else datetime.utcfromtimestamp(item["dt"]).date().isoformat()
        grouped[date_key].append(item)

    # return only needed fields for each date
    grouped_summary = {date: [
        {"dt": p["dt"], "temp": p["main"]["temp"], "humidity": p["main"]["humidity"], "weather": p["weather"][0]["main"]}
        for p in points
    ] for date, points in grouped.items()}

    return dict(grouped_summary)

templates = Jinja2Templates(directory="Templates")

@app.get("/forecast/{cityName}", response_class=HTMLResponse)
async def read_root(cityName: str, request: Request):
    lat, lon = find_loc(cityName)
    data = find_weather(lat, lon)

    sorted_dates = sorted(data.keys())
    # for i, date in enumerate(sorted_dates, 1):
    #     globals()[f'day{i}'] = [[p['temp'] for p in data[date]], [p['humidity'] for p in data[date]]]
    for i in range(1, len(sorted_dates)+1):
        globals()[f'temp{i}'] = [p['temp'] for p in data[sorted_dates[i-1]]]
        globals()[f'hum{i}'] = [p['humidity'] for p in data[sorted_dates[i-1]]]
        globals()[f'weather{i}'] = [p['weather'] for p in data[sorted_dates[i-1]]]
        globals()[f'w{i}'] = mode(globals()[f'weather{i}'])

        # Add dates

    return templates.TemplateResponse("forecastIndex.html", {"cityName":cityName, "request": request, "hum1": hum1, "temp1": temp1, "w1": w1, "hum2": hum2, "temp2": temp2, "w2": w2, "hum3": hum3, "temp3": temp3, "w3": w3, "hum4": hum4, "temp4": temp4, "w4": w4, "hum5": hum5, "temp5": temp5, "w5": w5})