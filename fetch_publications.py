"""
Fetch publications from Google Scholar and save as publications.json
"""
import json, time, sys
from datetime import datetime

try:
    from scholarly import scholarly
except ImportError:
    print("Error: pip install scholarly"); sys.exit(1)

SCHOLAR_ID = "a1c7tYcAAAAJ"
OUTPUT_FILE = "publications.json"

def fetch_publications():
    print(f"Fetching author profile for Scholar ID: {SCHOLAR_ID}")
    try:
        author = scholarly.search_author_id(SCHOLAR_ID)
        author = scholarly.fill(author, sections=["publications"])
    except Exception as e:
        print(f"Error: {e}"); sys.exit(1)

    publications = []
    for i, pub in enumerate(author.get("publications", [])):
        print(f"  Fetching publication {i + 1}...")
        try:
            pub_filled = scholarly.fill(pub); time.sleep(1)
        except Exception:
            pub_filled = pub
        bib = pub_filled.get("bib", {})
        publications.append({
            "title": bib.get("title", "Untitled"),
            "authors": bib.get("author", ""),
            "year": bib.get("pub_year", ""),
            "venue": bib.get("venue", bib.get("journal", bib.get("conference", ""))),
            "citations": pub_filled.get("num_citations", 0),
            "url": pub_filled.get("pub_url", ""),
            "scholar_url": f"https://scholar.google.com/citations?view_op=view_citation&hl=en&user={SCHOLAR_ID}&citation_for_view={pub_filled.get('author_pub_id', '')}",
        })

    publications.sort(key=lambda x: (-(int(x["year"]) if x["year"] else 0), -x["citations"]))
    return {
        "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "author": author.get("name", "Joseph Helsing"),
        "total_citations": author.get("citedby", 0),
        "h_index": author.get("hindex", 0),
        "i10_index": author.get("i10index", 0),
        "publications": publications,
    }

if __name__ == "__main__":
    data = fetch_publications()
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(data['publications'])} publications to {OUTPUT_FILE}")
