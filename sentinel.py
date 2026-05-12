import json
import requests
import xml.etree.ElementTree as ET
import hashlib

JSON_FILE = "safety_feed.json"

def scrape_who_website():
    alerts = []
    # Indirizzo pubblico delle notizie del sito OMS (Feed XML)
    url = "https://www.who.int/rss-feeds/news-english.xml"
    
    try:
        # Fingiamo di essere un Mac con Safari per non farci bloccare dai sistemi anti-bot
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        print("📡 Connessione al sito dell'OMS in corso...")
        r = requests.get(url, headers=headers, timeout=15)
        
        if r.status_code == 200:
            # Leggiamo la struttura della pagina
            root = ET.fromstring(r.content)
            
            # Cerchiamo tutti i blocchi "item" (che sono i singoli articoli)
            for item in root.findall('.//item')[:40]: # Prendiamo i 40 più recenti
                title = item.find('title').text if item.find('title') is not None else "Articolo OMS"
                desc = item.find('description').text if item.find('description') is not None else ""
                
                # Creiamo un ID univoco basato sul titolo
                article_id = hashlib.md5(title.encode()).hexdigest()[:8]
                
                # Puliamo un po' il testo da eventuali codici HTML residui
                clean_desc = desc.replace("<p>", "").replace("</p>", "").replace("&nbsp;", " ").strip()
                
                alerts.append({
                    "id": f"OMS-{article_id}",
                    "category": "Salute",
                    "title": title,
                    "description": clean_desc,
                    "latitude": 46.204391, # Coordinate della Sede Centrale OMS a Ginevra
                    "longitude": 6.143158, 
                    "source": "WHO Website Scraper",
                    "countryCode": "CH" # Mostrerà la bandiera Svizzera (Sede ONU/OMS)
                })
            print(f"✅ Scraping riuscito: estratti {len(alerts)} articoli direttamente dal sito!")
        else:
            print(f"❌ Il sito ha bloccato la richiesta: {r.status_code}")
    except Exception as e:
        print(f"❌ Errore durante l'estrazione: {e}")
        
    return alerts

if __name__ == "__main__":
    data = scrape_who_website()
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
