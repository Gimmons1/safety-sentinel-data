import json
import requests
from datetime import datetime

JSON_FILE = "safety_feed.json"

# Mappa di salvataggio per i terremoti in mare aperto (quando il GPS fallisce)
COUNTRY_MAP = {
    "TONGA": "TO", "INDONESIA": "ID", "PHILIPPINES": "PH", "PAPUA NEW GUINEA": "PG", 
    "JAPAN": "JP", "CHILE": "CL", "FIJI": "FJ", "VANUATU": "VU", "SOLOMON ISLANDS": "SB",
    "NEW ZEALAND": "NZ", "ITALY": "IT", "CALIFORNIA": "US", "ALASKA": "US", 
    "HAWAII": "US", "TAIWAN": "TW", "MYANMAR": "MM", "BURMA": "MM", "MEXICO": "MX",
    "ARGENTINA": "AR", "PERU": "PE", "GREECE": "GR", "TURKEY": "TR", "RUSSIA": "RU"
}

def get_country(lat, lon, place):
    # 1. Prova con le coordinate GPS
    try:
        url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=it"
        r = requests.get(url, timeout=3).json()
        code = r.get("countryCode", "")
        if code and code != "UN": return code
    except: pass
    
    # 2. Se è in mare aperto, cerca il nome della nazione nel testo
    place_upper = place.upper()
    for country, code in COUNTRY_MAP.items():
        if country in place_upper:
            return code
            
    return "UN" # Mappamondo se tutto fallisce

def get_usgs():
    alerts = []
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
    try:
        r = requests.get(url, timeout=10).json()
        for f in r.get("features", []):
            mag = f["properties"]["mag"]
            place = f["properties"]["place"] or "Località ignota"
            clean_place = place.split(" of ")[-1] if " of " in place else place
            
            lon = f["geometry"]["coordinates"][0]
            lat = f["geometry"]["coordinates"][1]
            depth = f["geometry"]["coordinates"][2] # Nuovo dato: Profondità!
            
            alerts.append({
                "id": f["id"],
                "category": "Sismi",
                "severity": "RED" if mag >= 6.0 else "ORANGE",
                "title": f"Sisma M{mag:.1f}",
                "description": clean_place.strip(),
                "latitude": lat,
                "longitude": lon,
                "depth_km": depth, # Passiamo la profondità all'app
                "source": "USGS (Gov USA)",
                "timestamp": datetime.fromtimestamp(f["properties"]["time"]/1000).strftime("%d/%m %H:%M"),
                "countryCode": get_country(lat, lon, place)
            })
    except Exception as e:
        print(f"Errore USGS: {e}")
    return alerts

def main():
    print("Avvio Radar Sismico...")
    alerts = get_usgs() # Ora scarica SOLO i terremoti

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {len(alerts)} terremoti salvati con successo.")

if __name__ == "__main__":
    main()
