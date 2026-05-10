import json
import requests
import os
from datetime import datetime

JSON_FILE = "safety_feed.json"

def get_oms_verified_news():
    """Pescaggio diretto da ReliefWeb (Fonte ufficiale OMS/ONU)"""
    alerts = []
    # Query specifica per Epidemie e focolai verificati
    url = "https://api.reliefweb.int/v1/disasters?appname=sentinel&query[value]=type:epidemic%20AND%20status:current&profile=full&limit=30&sort[]=date:desc"
    
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            for d in data.get("data", []):
                f = d.get("fields", {})
                countries = f.get("country", [])
                primary = f.get("primary_country", countries[0] if countries else {})
                
                # Creazione pacchetto dati sanitario
                alerts.append({
                    "id": f"OMS-{d['id']}",
                    "category": "Salute",
                    "severity": "RED",
                    "title": f.get("name", "Avviso Sanitario Internazionale"),
                    "description": f.get("headline", {}).get("title", "Nuovo focolaio monitorato dall'OMS."),
                    "latitude": primary.get("location", {}).get("lat", 0),
                    "longitude": primary.get("location", {}).get("lon", 0),
                    "source": "World Health Organization (WHO)",
                    "timestamp": f.get("date", {}).get("created", "")[:10],
                    "countryCode": primary.get("iso3", "UN")[:2].upper()
                })
    except Exception as e:
        print(f"Errore connessione OMS: {e}")
    return alerts

if __name__ == "__main__":
    print("📡 Collegamento ai server OMS in corso...")
    news = get_oms_verified_news()
    
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(news, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Backup completato: {len(news)} notizie verificate caricate.")
