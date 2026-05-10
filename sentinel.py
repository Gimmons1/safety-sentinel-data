import json
import requests

JSON_FILE = "safety_feed.json"

def get_who_europe_data():
    alerts = []
    # Usiamo un indicatore d'esempio: "Health for All" 
    # Questo endpoint restituisce i dati di base del catalogo
    url = "https://gateway.euro.who.int/api/v5/measures"
    
    try:
        # Chiediamo i metadati in formato JSON
        headers = {'Accept': 'application/json'}
        r = requests.get(url, headers=headers, timeout=20)
        
        if r.status_code == 200:
            data = r.json()
            # Prendiamo i primi 30 indicatori per testare se il "tubo" funziona
            measures = data.get("measures", [])[:30]
            
            for m in measures:
                alerts.append({
                    "id": f"WHO-EU-{m.get('id')}",
                    "category": "Statistiche",
                    "title": m.get("full_name", "Indicatore OMS"),
                    "description": f"Codice: {m.get('code')}. Definizione: {m.get('definition', 'Dati statistici europei')}.",
                    "latitude": 46.8, # Centro Europa (Svizzera/Francia) come segnaposto
                    "longitude": 8.2,
                    "source": "WHO Europe Gateway",
                    "countryCode": "EU"
                })
            print(f"✅ OMS Europa: Caricati {len(alerts)} indicatori.")
        else:
            print(f"❌ Errore Server OMS EU: {r.status_code}")
    except Exception as e:
        print(f"❌ Errore: {e}")
    return alerts

if __name__ == "__main__":
    data = get_who_europe_data()
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
