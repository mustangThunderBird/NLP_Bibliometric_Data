import requests
import pandas as pd
import time


def fetch_crossref_results(query, start_year, end_year, rows=1000, offset=0):
    url = "https://api.crossref.org/works"
    headers = {"User-Agent": "NFacciola@my.gcu.edu"}
    
    params = {
        "query": query,
        "filter": f"from-pub-date:{start_year}-01-01,until-pub-date:{end_year}-12-31",
        "rows": rows,
        "offset": offset,
        "mailto": "NFacciola@my.gcu.edu"
    }
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    # Check if data is a dictionary and contains "message"
    if isinstance(data, dict) and "message" in data:
        # Check if "items" is present and is a list
        if isinstance(data["message"], dict) and "items" in data["message"]:
            return data["message"]["items"]
        else:
            print("No 'items' found in 'message'.")
            return []
    else:
        print("Unexpected data format received from CrossRef API:")
        print(data)
        return []
    
def get_article_snipet(doi):
    if doi != None:
        url = f"http://doi.org/{doi}"
        

def extract_metadata(item):
    metadata = {
        "title": item.get("title", [None])[0],
        "doi": item.get("DOI"),
        "authors": ", ".join([f"{author.get('given')} {author.get('family')}" for author in item.get("author", [])]) if item.get("author") else None,
        "publication_date": item.get("created", {}).get("date-time"),
        "journal": item.get("container-title", [None])[0],
        "publisher": item.get("publisher"),
        "abstract": item.get("abstract"),
        "keywords": ", ".join(item.get("subject", [])) if "subject" in item else None,
        "references_count": item.get("reference-count"),
        "cited_by_count": item.get("is-referenced-by-count"),
        "funders": ", ".join([funder.get("name") for funder in item.get("funder", [])]) if "funder" in item else None,
        "license": item.get("license", [{}])[0].get("URL") if "license" in item else None,
        "url": item.get("URL"),
        "affiliations": ", ".join([affil.get("name") for affil in item.get("author", [{}])[0].get("affiliation", [])]) if "author" in item else None,
        "snippet" : get_article_snipet(item.get("DOI"))
    }
    return metadata

def collect_metadata(query, start_year=2014, end_year=2024, rows_per_request=1000, max_results=20000):
    all_metadata = []
    total_results = 0
    offset = 0
    
    while total_results < max_results:
        results = fetch_crossref_results(query, start_year, end_year, rows=rows_per_request, offset=offset)
        
        if not results:
            break
        
        for item in results:
            metadata = extract_metadata(item)
            all_metadata.append(metadata)
        
        total_results += len(results)
        offset += rows_per_request
        time.sleep(1)  # Avoid hitting rate limits
    
    return all_metadata

def save_metadata_to_csv(metadata, filename="crossref_nlp_metadata.csv"):
    df = pd.DataFrame(metadata)
    df.to_csv(filename, index=False)
    print(f"Saved {len(metadata)} records to {filename}")

query = "Natural Language Processing"
metadata = collect_metadata(query, start_year=2014, end_year=2024, max_results=20000)
save_metadata_to_csv(metadata)


