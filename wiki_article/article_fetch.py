import requests
import ssl
import certifi
from bs4 import BeautifulSoup

ssl_context = ssl.create_default_context(cafile=certifi.where())

def truncate_summary(text,length):
    clean_text = text.strip() 
    return clean_text[:length] + "..." if len(clean_text) > length else clean_text

def fetch_summary(page_id):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "exintro": True,
        "pageids": page_id
    }

    response = requests.get(url, params=params, verify=False)
    
    if response.status_code == 200:
        data = response.json()
        pages = data["query"]["pages"]
        raw_summary=next(iter(pages.values()))["extract"]
        soup = BeautifulSoup(raw_summary, "html.parser")
        clean_text = soup.get_text().strip()

        return clean_text
    else:
        return "Summary not available."
    
def search_wikipedia(query):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query
    }
    response = requests.get(url, params=params, verify=False)
    
    wiki_articles = [] 
    
    if response.status_code == 200:
        data = response.json()
        search_results = data["query"]["search"]
        
        for result in search_results:
            title = result["title"]
            page_id = result["pageid"]
            page_url = f"https://en.wikipedia.org/?curid={page_id}"
            
            summary = fetch_summary(page_id)
            truncated_summary = truncate_summary(summary, 250)  
            
            wiki_articles.append({
                "title": title,
                "summary": truncated_summary,
                "url": page_url
            })
    
    return wiki_articles

#test
#print(search_wikipedia("Artificial Intelligence"))