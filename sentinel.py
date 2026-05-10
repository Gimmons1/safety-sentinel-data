import json
import requests
import os

JSON_FILE = "safety_feed.json"

def get_oms_news():
    alerts = []
    # Query semplificata al massimo: prendi gli ultimi 40 disastri sanitari registrati
    url = "https://api.reliefweb.int/v1/disasters?appname=sentinel&profile=full&limit=40&sort[]=date:desc"
    
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            for d in data.get("data", []):
                f = d.get("fields", {})
                # Estraiamo il paese primario o il primo disponibile
                countries = f.get("country", [])
                primary = f.get("primary_country", countries[0] if countries else {})
                
                alerts.append({
                    "id": str(d['id']),
                    "category": "Salute",
                    "title": f.get("name", "Health Alert"),
                    "description": "Notifica sanitaria ufficiale monitorata dall'OMS/ONU.",
                    "latitude": float(primary.get("location", {}).get("lat", 0)),
                    "longitude": float(primary.get("location", {}).get("lon", 0)),
                    "source": "World Health Organization",
                    "countryCode": primary.get("iso3", "UN")[:2].upper()
                })
            print(f"✅ Successo! Trovati {len(alerts)} articoli.")
        else:
            print(f"❌ Errore Server OMS: {r.status_code}")
    except Exception as e:
        print(f"❌ Errore Connessione: {e}")
    return alerts

if __name__ == "__main__":
    news = get_oms_news()
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(news, f, indent=2, ensure_ascii=False)
