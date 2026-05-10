import json
import requests
import os
import reverse_geocoder as rg
from datetime import datetime

JSON_FILE = "safety_feed.json"
WAQI_TOKEN = os.getenv("WAQI_TOKEN", "demo")

def get_country_from_coords(lat, lon):
    try:
        if lat == 0 and lon == 0: return "UN"
        results = rg.search((lat, lon))
        if results and len(results) > 0:
            return results[0]['cc'].upper() 
    except:
        pass
    return "UN" 

def get_usgs():
    alerts = []
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
    try:
        r = requests.get(url, timeout=10).json()
        for f in r.get("features", []):
            mag = f["properties"]["mag"]
            place = f["properties"]["place"]
            clean_place = place.split(" of ")[-1] if " of " in place else place
            lat = f["geometry"]["coordinates"][1]
            lon = f["geometry"]["coordinates"][0]
            
            alerts.append({
                "id": f["id"],
                "category": "Sismi",
                "severity": "RED" if mag >= 6.0 else "ORANGE",
                "title": f"Sisma Magnitudo {mag:.1f}",
                "description": clean_place.strip(),
                "latitude": lat,
                "longitude": lon,
                "source": "USGS Gov",
                "timestamp": datetime.fromtimestamp(f["properties"]["time"]/1000).strftime("%d/%m %H:%M"),
                "countryCode": get_country_from_coords(lat, lon)
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
            props = f.get("properties", {})
            alert_level = props.get("alertlevel", "Green")

            if alert_level.lower() in ["red", "orange"]:
                event_type = props.get("eventtype", "")
                if event_type == "EQ": continue 
                
                tipo_ita = "Allerta Natura"
                if event_type == "TC": tipo_ita = "Ciclone / Uragano"
                elif event_type == "FL": tipo_ita = "Alluvione Estesa"
                elif event_type == "DR": tipo_ita = "Siccità Severa"
                elif event_type == "VO": tipo_ita = "Eruzione Vulcanica"

                desc = props.get("description", "").split('<')[0]
                lat = f["geometry"]["coordinates"][1]
                lon = f["geometry"]["coordinates"][0]
                
                alerts.append({
                    "id": f"GDACS-{props.get('eventid', '0')}",
                    "category": "Natura",
                    "severity": "RED" if alert_level.lower() == "red" else "ORANGE",
                    "title": tipo_ita,
                    "description": f"{props.get('name', '')} - {desc}",
                    "latitude": lat,
                    "longitude": lon,
                    "source": "GDACS (ONU)",
                    "timestamp": props.get("fromdate", "")[:10],
                    "countryCode": get_country_from_coords(lat, lon)
                })
    except Exception as e:
        print(f"Errore GDACS: {e}")
    return alerts

def get_health():
    alerts = []
    url = "https://api.reliefweb.int/v1/disasters?appname=sentinel&query[value]=epidemic&profile=full&limit=15&sort[]=date:desc"
    try:
        headers = {'Accept': 'application/json'}
        r = requests.get(url, headers=headers, timeout=10).json()
        for d in r.get("data", []):
            f = d.get("fields", {})
            country_info = f.get("primary_country", {})
            name = f.get("name", "Allerta Epidemica")
            
            lat = country_info.get("location", {}).get("lat", 0)
            lon = country_info.get("location", {}).get("lon", 0)
            
            alerts.append({
                "id": f"RW-{d.get('id', '0')}",
                "category": "Salute",
                "severity": "RED",
                "title": "Focolaio Virale (OMS)",
                "description": name,
                "latitude": lat,
                "longitude": lon,
                "source": "ReliefWeb / OMS",
                "timestamp": f.get("date", {}).get("created", "")[:10],
                "countryCode": get_country_from_coords(lat, lon) if lat != 0 else "UN"
            })
    except Exception as e:
        print(f"Errore Health: {e}")
    return alerts

def get_waqi():
    cities = ["beijing", "delhi", "milan", "los angeles", "new york", "paris", "london", "tokyo", "mexico city", "sao paulo", "bangkok"]
    alerts = []
    try:
        for city in cities:
            url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
            r = requests.get(url, timeout=5).json()
            if r.get("status") == "ok":
                aqi = r.get("data", {}).get("aqi", 0)
                if aqi > 100: 
                    lat = r["data"]["city"]["geo"][0]
                    lon = r["data"]["city"]["geo"][1]
                    alerts.append({
                        "id": f"WAQI-{city}",
                        "category": "Aria",
                        "severity": "RED" if aqi > 150 else "ORANGE",
                        "title": f"Qualità Aria: {aqi} AQI",
                        "description": f"Inquinamento a {r['data']['city']['name']}",
                        "latitude": lat,
                        "longitude": lon,
                        "source": "WAQI API",
                        "timestamp": r["data"].get("time", {}).get("s", "")[:10],
                        "countryCode": get_country_from_coords(lat, lon)
                    })
    except Exception as e:
        print(f"Errore WAQI: {e}")
    return alerts

def main():
    print("Avvio Radar Globale...")
    alerts = []
    alerts.extend(get_usgs())
    alerts.extend(get_gdacs())
    alerts.extend(get_health())
    alerts.extend(get_waqi())

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2, ensure_ascii=False)
    
    print(f"Finito! {len(alerts)} allerte salvate con bandiere accurate.")

if __name__ == "__main__":
    main()
