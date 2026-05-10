import json
import requests
from datetime import datetime

JSON_FILE = "safety_feed.json"

def get_oms_medical_news():
    alerts = []
    # Query che filtra per tipo: 'epidemic' (Salute) ed esclude terremoti/disastri naturali
    url = "https://api.reliefweb.int/v1/disasters?appname=sentinel&query[value]=type:epidemic&profile=full&limit=40&sort[]=date:desc"
    
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            for d in data.get("data", []):
                f = d.get("fields", {})
                countries = f.get("country", [])
                primary = f.get("primary_country", countries[0] if countries else {})
                
                # Creiamo l'articolo sanitario
                alerts.append({
                    "id": f"OMS-{d['id']}",
                    "category": "Salute",
                    "title": f.get("name", "Report Medico Internazionale"),
                    "description": "Aggiornamento ufficiale monitorato dall'OMS. Verifica dello stato epidemico e dei protocolli sanitari.",
                    "latitude": float(primary.get("location", {}).get("lat", 0)),
                    "longitude": float(primary.get("location", {}).get("lon", 0)),
                    "source": "World Health Organization",
                    "countryCode": primary.get("iso3", "UN")[:2].upper()
                })
            print(f"✅ OMS: Caricati {len(alerts)} articoli sanitari.")
        else:
            print(f"❌ Errore Server: {r.status_code}")
    except Exception as e:
        print(f"❌ Errore: {e}")
    return alerts

if __name__ == "__main__":
    # Scarichiamo solo notizie mediche
    data = get_oms_medical_news()
    
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
