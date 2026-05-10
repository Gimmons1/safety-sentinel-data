import json
import requests
import os
from datetime import datetime

JSON_FILE = "safety_feed.json"
WAQI_TOKEN = os.getenv("WAQI_TOKEN", "demo") 

# Funzione di supporto per estrarre il codice nazione
def get_country_code(text):
    # Una versione semplificata: le API migliori forniscono già il codice,
    # per USGS cerchiamo di estrarlo dalla fine della stringa "place".
    testo = text.upper()
    if "SWITZERLAND" in testo: return "CH"
    if "ITALY" in testo: return "IT"
    if "JAPAN" in testo: return "JP"
    if "INDONESIA" in testo: return "ID"
    if "USA" in testo or "CALIFORNIA" in testo: return "US"
    # (In una versione finale si usa una libreria come 'pycountry')
    return "🌐"

def get_usgs():
    alerts = []
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
    try:
        r = requests.get(url, timeout=10).json()
        for f in r.get("features", []):
            mag = f["properties"]["mag"]
            place = f["properties"]["place"]
            alerts.append({
                "id": f["id"],
                "category": "Sismi",
                "severity": "RED" if mag >= 6.0 else "ORANGE",
                "title": f"Sisma M{mag}",
                "description": place,
                "latitude": f["geometry"]["coordinates"][1],
                "longitude": f["geometry"]["coordinates"][0],
                "source": "USGS Gov",
                "timestamp": datetime.fromtimestamp(f["properties"]["time"]/1000).strftime("%d/%m %H:%M"),
                "countryCode": get_country_code(place)
            })
    except Exception as e:
        print(f"Errore USGS: {e}")
    return alerts

def get_gdacs():
    alerts = []
    url = "https://www.gdacs.org/xml/rss.geojson"
    try:
        r = requests.get(url, timeout=10).json()
        for f in r.get("features", []):
            props = f.get("properties", {})
            event_type = props.get("eventtype", "")
            
            # Traduzione e classificazione accurata
            tipo_ita = "Disastro Naturale"
            if event_type == "TC": tipo_ita = "Ciclone / Uragano"
            elif event_type == "FL": tipo_ita = "Alluvione Estesa"
            elif event_type == "DR": tipo_ita = "Siccità Severa"
            elif event_type == "VO": tipo_ita = "Eruzione Vulcanica"

            alerts.append({
                "id": f"GDACS-{props.get('eventid', '0')}",
                "category": "Natura",
                "severity": "RED",
                "title": tipo_ita,
                "description": props.get("name", "") + " - " + props.get("description", "").split('<')[0],
                "latitude": f["geometry"]["coordinates"][1],
                "longitude": f["geometry"]["coordinates"][0],
                "source": "GDACS ONU",
                "timestamp": "In corso",
                "countryCode": props.get("country", "🌐")[:2].upper()
            })
    except Exception as e:
        print(f"Errore GDACS: {e}")
    return alerts

def get_health():
    alerts = []
    # API di ReliefWeb (ONU) filtrata solo per "Epidemic" (EP)
    url = "https://api.reliefweb.int/v1/disasters?appname=sentinel&filter[field]=primary_type.code&filter[value]=EP&profile=full&limit=15"
    try:
        r = requests.get(url, timeout=10).json()
        for d in r.get("data", []):
            f = d.get("fields", {})
            country_info = f.get("primary_country", {})
            
            alerts.append({
                "id": f"RW-{d['id']}",
                "category": "Salute",
                "severity": "RED",
                "title": f.get("name", "Allerta Epidemica"),
                "description": "Focolaio infettivo confermato e monitorato dalle agenzie sanitarie internazionali.",
                "latitude": country_info.get("location", {}).get("lat", 0),
                "longitude": country_info.get("location", {}).get("lon", 0),
                "source": "ReliefWeb / OMS",
                "timestamp": f.get("date", {}).get("created", "")[:10], # Prende solo YYYY-MM-DD
                "countryCode": country_info.get("iso3", "🌐")[:2].upper()
            })
    except Exception as e:
        print(f"Errore Health: {e}")
    return alerts

def main():
    alerts = []
    alerts.extend(get_usgs())
    alerts.extend(get_gdacs())
    alerts.extend(get_health()) # Aggiunte le vere allerte OMS
    # (La funzione WAQI per l'aria rimane identica, l'ho omessa qui per brevità, aggiungila se vuoi mantenerla)

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Aggiornamento completato con Dati OMS e Nazioni.")

if __name__ == "__main__":
    main()
