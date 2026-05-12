import json
import requests
import xml.etree.ElementTree as ET
import hashlib
from email.utils import parsedate_to_datetime

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
                raw_desc = item.find('description').text if item.find('description') is not None else ""
                clean_desc = raw_desc.split('<')[0].replace('&nbsp;', ' ').strip()
                
                # Estrazione e formattazione della data e ora
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                formatted_date = "--"
                if pub_date:
                    try:
                        # Converte la data RSS nel formato "12/05/2026 - 14:30"
                        dt = parsedate_to_datetime(pub_date)
                        formatted_date = dt.strftime("%d/%m/%Y - %H:%M")
                    except:
                        formatted_date = pub_date[:16]

                article_id = hashlib.md5(title.encode()).hexdigest()[:8]
                
                alerts.append({
                    "id": f"OMS-{article_id}",
                    "category": "REPORT",
                    "title": title.upper(),
                    "description": clean_desc,
                    "date": formatted_date, # Nuovo campo Data
                    "countryCode": "CH"
                })
            print(f"✅ Estratti {len(alerts)} articoli con data.")
    except Exception as e:
        print(f"❌ Errore: {e}")
    return alerts

if __name__ == "__main__":
    data = scrape_who_details()
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
