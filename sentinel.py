import json
import requests
import os
from datetime import datetime

JSON_FILE = "safety_feed.json"
WAQI_TOKEN = os.getenv("WAQI_TOKEN", "demo")

def get_country_code(text):
    t = text.upper()
    if "ITALY" in t or "ITALIA" in t: return "IT"
    if "SWITZERLAND" in t or "SUISSE" in t: return "CH"
    if "JAPAN" in t: return "JP"
    if "INDONESIA" in t: return "ID"
    if "USA" in t or "CALIFORNIA" in t: return "US"
    if "CHINA" in t: return "CN"
    if "MEXICO" in t: return "MX"
    if "PHILIPPINES" in t: return "PH"
    if "PAPUA NEW GUINEA" in t: return "PG"
    if "TONGA" in t: return "TO"
    if "PORTUGAL" in t: return "PT"
    return "🌐"

def get_usgs():
    alerts = []
    # Prendiamo i terremoti più rilevanti (sopra magnitudo 4.5)
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
    try:
        r = requests.get(url, timeout=10).json()
        for f in r.get("features", []):
            mag = f["properties"]["mag"]
            place = f["properties"]["place"]
            
            # Pulizia del nome brutto del governo USA (Togliamo il "74km W of...")
            clean_place = place.split(" of ")[-1] if " of " in place else place
            
            alerts.append({
                "id": f["id"],
                "category": "Sismi",
                "severity": "RED" if mag >= 6.0 else "ORANGE",
                "title": f"Sisma Magnitudo {mag:.1f}",
                "description": clean_place,
                "latitude": f["geometry"]["coordinates"][1],
                "longitude": f["geometry"]["coordinates"][0],
                "source": "USGS (Governo USA)",
                "timestamp": datetime.fromtimestamp(f["properties"]["time"]/1000).strftime("%d/%m %H:%M"),
                "countryCode": get_country_code(place)
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

            # Ora prendiamo anche le allerte ARANCIONI, non solo le rosse!
            if alert_level.lower() in ["red", "orange"]:
                event_type = props.get("eventtype", "")
                if event_type == "EQ": continue # Saltiamo i terremoti qui perché li fa già USGS
                
                tipo_ita = "Allerta Natura"
                if event_type == "TC": tipo_ita = "Ciclone / Uragano"
                elif event_type == "FL": tipo_ita = "Alluvione"
                elif event_type == "DR": tipo_ita = "Siccità Estrema"
                elif event_type == "VO": tipo_ita = "Eruzione Vulcanica"

                desc = props.get("description", "").split('<')[0]
                
                alerts.append({
                    "id": f"GDACS-{props.get('eventid', '0')}",
                    "category": "Natura",
                    "severity": "RED" if alert_level.lower() == "red" else "ORANGE",
                    "title": tipo_ita,
                    "description": f"{props.get('name', '')} - {desc}",
                    "latitude": f["geometry"]["coordinates"][1],
                    "longitude": f["geometry"]["coordinates"][0],
                    "source": "GDACS (ONU/UE)",
                    "timestamp": props.get("fromdate", "")[:10],
                    "countryCode": props.get("country", "🌐")[:2].upper()
                })
    except Exception as e:
        print(f"Errore GDACS: {e}")
    return alerts

def get_health():
    alerts = []
    # API Corretta di ReliefWeb (Ufficio ONU). Filtro "EP" sta per Epidemics.
    url = "https://api.reliefweb.int/v1/disasters?appname=sentinel&filter[field]=primary_type.code&filter[value]=EP&profile=full&limit=15&sort[]=date:desc"
    try:
        r = requests.get(url, timeout=10).json()
        for d in r.get("data", []):
            f = d.get("fields", {})
            country_info = f.get("primary_country", {})
            name = f.get("name", "Allerta Epidemica")
            
            alerts.append({
                "id": f"RW-{d.get('id', '0')}",
                "category": "Salute",
                "severity": "RED",
                "title": "Focolaio OMS / Epidemia",
                "description": name, # Conterrà ad es. "Cholera - Zimbabwe" o "Dengue - Brazil"
                "latitude": country_info.get("location", {}).get("lat", 0),
                "longitude": country_info.get("location", {}).get("lon", 0),
                "source": "ReliefWeb (OMS/ONU)",
                "timestamp": f.get("date", {}).get("created", "")[:10],
                "countryCode": country_info.get("iso3", "🌐")[:2].upper()
            })
    except Exception as e:
        print(f"Errore Health: {e}")
    return alerts

def get_waqi():
    # Moltiplichiamo le stazioni monitorate e abbassiamo la soglia a 100 (Insalubre)
    cities = ["beijing", "delhi", "milan", "los angeles", "new york", "paris", "london", "tokyo", "mexico city", "sao paulo", "bangkok"]
    alerts = []
    try:
        for city in cities:
            url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
            r = requests.get(url, timeout=5).json()
            if r.get("status") == "ok":
                aqi = r.get("data", {}).get("aqi", 0)
                if aqi > 100: 
                    alerts.append({
                        "id": f"WAQI-{city}",
                        "category": "Aria",
                        "severity": "RED" if aqi > 150 else "ORANGE",
                        "title": f"Qualità Aria: {aqi} AQI",
                        "description": f"Inquinamento a {r['data']['city']['name']}",
                        "latitude": r["data"]["city"]["geo"][0],
                        "longitude": r["data"]["city"]["geo"][1],
                        "source": "WAQI (World Air Quality Index)",
                        "timestamp": r["data"].get("time", {}).get("s", "")[:10],
                        "countryCode": "🌐" 
                    })
    except Exception as e:
        print(f"Errore WAQI: {e}")
    return alerts

def main():
    alerts = []
    alerts.extend(get_usgs())
    alerts.extend(get_gdacs())
    alerts.extend(get_health())
    alerts.extend(get_waqi())

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2, ensure_ascii=False)
    
    print(f"Scansione globale completata. {len(alerts)} allerte salvate.")

if __name__ == "__main__":
    main()
