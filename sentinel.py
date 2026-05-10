import json
import requests
import os
import uuid
from datetime import datetime

JSON_FILE = "safety_feed.json"
# Il token viene letto in sicurezza dai Secrets di GitHub
WAQI_TOKEN = os.getenv("WAQI_TOKEN", "demo") 

def get_usgs():
    alerts = []
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
    try:
        r = requests.get(url, timeout=10).json()
        for f in r.get("features", []):
            mag = f["properties"]["mag"]
            alerts.append({
                "id": f["id"],
                "category": "Sismi",
                "severity": "RED" if mag >= 6.0 else "ORANGE",
                "title": f"Sisma M{mag}",
                "description": f["properties"]["place"],
                "latitude": f["geometry"]["coordinates"][1],
                "longitude": f["geometry"]["coordinates"][0],
                "source": "USGS Gov",
                "timestamp": datetime.fromtimestamp(f["properties"]["time"]/1000).strftime("%d/%m %H:%M")
            })
    except Exception as e:
        print(f"Errore USGS: {e}")
    return alerts

def get_gdacs():
    alerts = []
    url = "https://www.gdacs.org/xml/rss.geojson"
    try:
        r = requests.get(url, timeout=10).json()
        for f in r.get("features", []):
            alerts.append({
                "id": f"GDACS-{str(uuid.uuid4())[:8]}",
                "category": "Natura",
                "severity": "RED",
                "title": f["properties"].get("name", "Disastro Naturale"),
                "description": f["properties"].get("description", "").split('<')[0],
                "latitude": f["geometry"]["coordinates"][1],
                "longitude": f["geometry"]["coordinates"][0],
                "source": "GDACS ONU",
                "timestamp": "In corso"
            })
    except Exception as e:
        print(f"Errore GDACS: {e}")
    return alerts

def get_waqi():
    cities = ["beijing", "delhi", "milan", "los angeles", "new york", "paris"]
    alerts = []
    try:
        for city in cities:
            url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
            r = requests.get(url, timeout=5).json()
            if r.get("status") == "ok":
                aqi = r["data"]["aqi"]
                if aqi > 150:
                    alerts.append({
                        "id": f"WAQI-{city}",
                        "category": "Aria",
                        "severity": "RED" if aqi > 200 else "ORANGE",
                        "title": f"Smog Pericoloso: {aqi} AQI",
                        "description": f"Aria inquinata a {r['data']['city']['name']}",
                        "latitude": r["data"]["city"]["geo"][0],
                        "longitude": r["data"]["city"]["geo"][1],
                        "source": "WAQI API",
                        "timestamp": "Recente"
                    })
    except Exception as e:
        print(f"Errore WAQI: {e}")
    return alerts

def get_health():
    return [{
        "id": "HEALTH-001",
        "category": "Salute",
        "severity": "ORANGE",
        "title": "Avviso Sanitario",
        "description": "Possibile circolazione virale anomala segnalata nelle strutture sanitarie.",
        "latitude": 46.778, 
        "longitude": 6.641,
        "source": "Ministero / OMS",
        "timestamp": datetime.now().strftime("%d/%m")
    }]

def main():
    print("Avvio scansione Sentinel Globale...")
    alerts = []
    alerts.extend(get_usgs())
    alerts.extend(get_gdacs())
    alerts.extend(get_waqi())
    alerts.extend(get_health())

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Scansione completata. {len(alerts)} allerte globali salvate.")

if __name__ == "__main__":
    main()
