import json
import requests
from datetime import datetime

JSON_FILE = "safety_feed.json"

def get_test_data():
    alerts = []
    # API USGS: Terremoti mondiali di magnitudo 4.5+ nelle ultime 24 ore
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
    
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            for f in data.get("features", []):
                props = f.get("properties", {})
                geom = f.get("geometry", {}).get("coordinates", [0, 0])
                
                alerts.append({
                    "id": str(f.get("id")),
                    "category": "Salute", # Lasciamo Salute per non dover cambiare l'App iOS ora
                    "title": f"Sisma M{props.get('mag')}",
                    "description": props.get("place", "Località sconosciuta"),
                    "latitude": float(geom[1]),
                    "longitude": float(geom[0]),
                    "countryCode": "US" # Codice generico per il test
                })
            print(f"✅ TEST RIUSCITO: Trovati {len(alerts)} eventi USGS.")
        else:
            print(f"❌ Errore USGS: {r.status_code}")
    except Exception as e:
        print(f"❌ Errore Connessione: {e}")
    return alerts

if __name__ == "__main__":
    data = get_test_data()
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
