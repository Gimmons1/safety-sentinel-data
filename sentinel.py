import json
import requests
from datetime import datetime

JSON_FILE = "safety_feed.json"

def get_epidemics_3_years():
    alerts = []
    # Query per Epidemie dal 2023-01-01 ad oggi
    # Filtriamo per primary_type.id: 462 (Epidemic)
    url = "https://api.reliefweb.int/v1/disasters?appname=sentinel&profile=full&limit=100&sort[]=date:desc&query[value]=primary_type.id:462 AND date.created:[2023-01-01T00:00:00Z TO 2026-12-31T23:59:59Z]"
    
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            data = r.json()
            for d in data.get("data", []):
                f = d.get("fields", {})
                countries = f.get("country", [])
                primary = f.get("primary_country", countries[0] if countries else {})
                
                # Pulizia data per l'app
                full_date = f.get("date", {}).get("created", "2023-01-01")
                short_date = full_date[:10]
                
                alerts.append({
                    "id": f"OMS-{d['id']}",
                    "category": "Salute",
                    "title": f.get("name", "Epidemia Verificata"),
                    "description": f"Evento sanitario registrato il {short_date}. Fonte ufficiale OMS/ONU.",
                    "latitude": float(primary.get("location", {}).get("lat", 0)),
                    "longitude": float(primary.get("location", {}).get("lon", 0)),
                    "source": "World Health Organization",
                    "countryCode": primary.get("iso3", "UN")[:2].upper()
                })
            print(f"✅ Storico caricato: {len(alerts)} epidemie trovate dal 2023.")
        else:
            print(f"❌ Errore Server OMS: {r.status_code}")
    except Exception as e:
        print(f"❌ Errore: {e}")
    return alerts

if __name__ == "__main__":
    data = get_epidemics_3_years()
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
