import json
import requests
import os
from datetime import datetime

JSON_FILE = "safety_feed.json"

def get_oms_data():
    alerts = []
    # Query ufficiale ReliefWeb (ONU/OMS) per epidemie correnti
    url = "https://api.reliefweb.int/v1/disasters?appname=sentinel&query[value]=type:epidemic%20AND%20status:current&profile=full&limit=40&sort[]=date:desc"
    
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            for d in data.get("data", []):
                f = d.get("fields", {})
                countries = f.get("country", [])
                primary = f.get("primary_country", countries[0] if countries else {})
                
                alerts.append({
                    "id": f"OMS-{d['id']}",
                    "category": "Salute",
                    "title": f.get("name", "WHO Health Alert"),
                    "description": f.get("headline", {}).get("title", "International health emergency monitored by WHO."),
                    "latitude": primary.get("location", {}).get("lat", 0),
                    "longitude": primary.get("location", {}).get("lon", 0) ,
                    "source": "World Health Organization",
                    "timestamp": f.get("date", {}).get("created", "")[:10],
                    "countryCode": primary.get("iso3", "UN")[:2].upper()
                })
        print(f"Scaricati {len(alerts)} articoli.")
    except Exception as e:
        print(f"Errore: {e}")
    return alerts

if __name__ == "__main__":
    data = get_oms_data()
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
