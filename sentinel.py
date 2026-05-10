import json
import requests
import os
from datetime import datetime

JSON_FILE = "safety_feed.json"

def get_oms_news():
    alerts = []
    # Query ampia: cerchiamo TUTTI i report sanitari recenti (non solo epidemie)
    url = "https://api.reliefweb.int/v1/disasters?appname=sentinel&profile=full&limit=40&sort[]=date:desc"
    
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            for d in data.get("data", []):
                f = d.get("fields", {})
                countries = f.get("country", [])
                primary = f.get("primary_country", countries[0] if countries else {})
                
                # Prendiamo il titolo originale
                title = f.get("name", "WHO Health Report")
                
                alerts.append({
                    "id": f"OMS-{d['id']}",
                    "category": "Salute",
                    "title": title,
                    "description": f"Report ufficiale verificato. Luogo: {primary.get('name', 'Globale')}.",
                    "latitude": primary.get("location", {}).get("lat", 0),
                    "longitude": primary.get("location", {}).get("lon", 0),
                    "source": "World Health Organization",
                    "timestamp": f.get("date", {}).get("created", "")[:10],
                    "countryCode": primary.get("iso3", "UN")[:2].upper()
                })
        print(f"Trovati {len(alerts)} articoli.")
    except Exception as e:
        print(f"Errore: {e}")
    return alerts

if __name__ == "__main__":
    data = get_oms_news()
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
