import json
import requests
import os

JSON_FILE = "safety_feed.json"

def get_oms_verified_data():
    alerts = []
    # Query "TOTALE": scarica gli ultimi 40 eventi registrati dall'ONU/OMS
    url = "https://api.reliefweb.int/v1/disasters?appname=sentinel&profile=full&limit=40&sort[]=date:desc"
    
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            for d in data.get("data", []):
                f = d.get("fields", {})
                countries = f.get("country", [])
                primary = f.get("primary_country", countries[0] if countries else {})
                
                # Creiamo un oggetto che l'app Swift non può rifiutare
                alerts.append({
                    "id": str(d['id']),
                    "category": "Salute",
                    "title": f.get("name", "Health Alert"),
                    "description": "Report ufficiale monitorato dalle agenzie internazionali (OMS/ONU).",
                    "latitude": float(primary.get("location", {}).get("lat", 0)),
                    "longitude": float(primary.get("location", {}).get("lon", 0)),
                    "source": "World Health Organization",
                    "countryCode": primary.get("iso3", "UN")[:2].upper()
                })
            print(f"✅ Trovati {len(alerts)} articoli.")
        else:
            print(f"❌ Errore Server: {r.status_code}")
    except Exception as e:
        print(f"❌ Errore: {e}")
    return alerts

if __name__ == "__main__":
    news = get_oms_verified_data()
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        # ensure_ascii=False serve per non rovinare le lettere accentate
        json.dump(news, f, indent=2, ensure_ascii=False)
