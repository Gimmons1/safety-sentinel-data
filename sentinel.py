import json
import requests
import xml.etree.ElementTree as ET
import hashlib

JSON_FILE = "safety_feed.json"

def scrape_who_details():
    alerts = []
    url = "https://www.who.int/rss-feeds/news-english.xml"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        r = requests.get(url, headers=headers, timeout=15)
        
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            for item in root.findall('.//item')[:20]:
                title = item.find('title').text if item.find('title') is not None else ""
                # Prendiamo la descrizione e puliamola per creare un riassunto concreto
                raw_desc = item.find('description').text if item.find('description') is not None else ""
                clean_desc = raw_desc.split('<')[0].replace('&nbsp;', ' ').strip()
                
                # Creiamo un "Punto Chiave" simulato per il riassunto se la descrizione è breve
                summary = f"IMPORTANTE: {clean_desc} Monitoraggio attivo dei protocolli di sicurezza e coordinamento internazionale."

                article_id = hashlib.md5(title.encode()).hexdigest()[:8]
                
                alerts.append({
                    "id": f"OMS-{article_id}",
                    "category": "EMERGENZA SANITARIA",
                    "title": title.upper(),
                    "description": summary,
                    "latitude": 46.204391,
                    "longitude": 6.143158,
                    "source": "WHO Official",
                    "countryCode": "CH"
                })
            print(f"✅ Estratti {len(alerts)} articoli con riassunto.")
    except Exception as e:
        print(f"❌ Errore: {e}")
    return alerts

if __name__ == "__main__":
    data = scrape_who_details()
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
