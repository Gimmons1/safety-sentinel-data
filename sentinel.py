import json
import requests
import os
from datetime import datetime

JSON_FILE = "safety_feed.json"

def get_country_from_coords(lat, lon):
    try:
        url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=it"
        r = requests.get(url, timeout=5).json()
        return r.get("countryCode", "UN")
    except:
        return "UN"

def get_health_alerts():
    """Recupera i focolai e le epidemie dall'ONU/OMS"""
    alerts = []
    # Interroghiamo ReliefWeb specificamente per epidemie (tipo 4624)
    url = "https://api.reliefweb.int/v1/disasters?appname=sentinel&query[value]=status:current%20AND%20type:epidemic&profile=full&limit=40&sort[]=date:desc"
    try:
        r = requests.get(url, timeout=10).json()
        for d in r.get("data", []):
            f = d.get("fields", {})
            country = f.get("primary_country", {})
            
            alerts.append({
                "id": f"HEALTH-{d['id']}",
                "category": "Salute",
                "severity": "RED",
                "title": f.get("name", "Allerta Sanitaria"),
                "description": f"Focolaio monitorato dall'OMS in {country.get('name', 'Area Globale')}",
                "latitude": country.get("location", {}).get("lat", 0),
                "longitude": country.get("location", {}).get("lon", 0),
                "source": "OMS / ReliefWeb",
                "timestamp": f.get("date", {}).get("created", "")[:10],
                "countryCode": country.get("iso3", "UN")[:2].upper()
            })
    except Exception as e:
        print(f"Errore Salute: {e}")
    return alerts

def get_natural_disasters():
    """Cicloni, Alluvioni e Siccità dall'ONU"""
    alerts = []
    url = "https://www.gdacs.org/xml/rss.geojson"
    try:
        r = requests.get(url, timeout=10).json()
        for f in r.get("features", []):
            props = f.get("properties", {})
            if props.get("eventtype") == "EQ": continue # Ignora i sismi qui
            
            lat = f["geometry"]["coordinates"][1]
            lon = f["geometry"]["coordinates"][0]
            
            alerts.append({
                "id": f"NAT-{props.get('eventid')}",
                "category": "Natura",
                "severity": props.get("alertlevel", "Green").upper(),
                "title": props.get("eventname", "Emergenza Naturale"),
                "description": props.get("description", ""),
                "latitude": lat,
                "longitude": lon,
                "source": "GDACS (ONU/UE)",
                "timestamp": datetime.now().strftime("%Y-%m-%d"),
                "countryCode": get_country_from_coords(lat, lon)
            })
    except: pass
    return alerts

def main():
    print("Aggiornamento Radar Sanitario...")
    all_data = []
    all_data.extend(get_health_alerts())
    all_data.extend(get_natural_disasters())
    
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print(f"Fatto! {len(all_data)} allerte caricate.")

if __name__ == "__main__":
    main()
