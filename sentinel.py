import json
import requests
import os
from datetime import datetime

JSON_FILE = "safety_feed.json"

def get_health_alerts():
    """Recupera epidemie in tempo reale da ReliefWeb (OMS/ONU)"""
    alerts = []
    # Query specifica per epidemie attive
    url = "https://api.reliefweb.int/v1/disasters?appname=sentinel&query[value]=type:epidemic&profile=full&limit=20&sort[]=date:desc"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for d in data.get("data", []):
                f = d.get("fields", {})
                countries = f.get("country", [])
                primary = f.get("primary_country", countries[0] if countries else {})
                
                alerts.append({
                    "id": f"H-{d['id']}",
                    "category": "Salute",
                    "severity": "RED",
                    "title": f.get("name", "Allerta Sanitaria"),
                    "description": "Focolaio epidemico segnalato dalle agenzie internazionali.",
                    "latitude": primary.get("location", {}).get("lat", 0),
                    "longitude": primary.get("location", {}).get("lon", 0),
                    "source": "OMS / ReliefWeb",
                    "timestamp": f.get("date", {}).get("created", "")[:10],
                    "countryCode": primary.get("iso3", "UN")[:2].upper()
                })
    except Exception as e:
        print(f"Errore Salute: {e}")
    return alerts

def get_nature_alerts():
    """Recupera disastri naturali da GDACS (ONU/UE)"""
    alerts = []
    url = "https://www.gdacs.org/xml/rss.geojson"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for f in data.get("features", []):
                props = f.get("properties", {})
                if props.get("eventtype") == "EQ": continue # Saltiamo i sismi
                
                alerts.append({
                    "id": f"N-{props.get('eventid')}",
                    "category": "Natura",
                    "severity": props.get("alertlevel", "Green").upper(),
                    "title": props.get("eventname", "Emergenza Naturale"),
                    "description": props.get("description", "").split('<')[0],
                    "latitude": f["geometry"]["coordinates"][1],
                    "longitude": f["geometry"]["coordinates"][0],
                    "source": "GDACS (ONU)",
                    "timestamp": datetime.now().strftime("%Y-%m-%d"),
                    "countryCode": props.get("country", "UN")[:2].upper()
                })
    except Exception as e:
        print(f"Errore Natura: {e}")
    return alerts

if __name__ == "__main__":
    print("Inizio scansione...")
    results = []
    results.extend(get_health_alerts())
    results.extend(get_nature_alerts())
    
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Scansione terminata: {len(results)} eventi trovati.")
