import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.shl.com"
CATALOG_URL = BASE_URL + "/solutions/products/product-catalog/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(CATALOG_URL, headers=headers)

print("Status Code:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

cards = soup.find_all("a")

results = []

visited = set()

for card in cards:

    text = " ".join(card.get_text(strip=True).split())

    href = card.get("href")

    if href and "/products/product-catalog/view/" in href:

        if text.lower() in ["next", "previous"]:
            continue

        if text.isdigit():
            continue

        if len(text) < 3:
            continue

        full_url = href

        if not href.startswith("http"):
            full_url = BASE_URL + href

        if full_url in visited:
            continue

        visited.add(full_url)

        print("Scraping:", text)

        try:

            page = requests.get(full_url, headers=headers)

            page_soup = BeautifulSoup(page.text, "html.parser")

            paragraphs = page_soup.find_all("p")

            description = " ".join(
                p.get_text(strip=True)
                for p in paragraphs[:5]
            )

            item = {
                "name": text,
                "url": full_url,
                "description": description
            }

            results.append(item)

            time.sleep(1)

        except Exception as e:
            print("Error:", e)

print("Total Assessments:", len(results))

with open("data/shl_catalog.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("Detailed catalog saved successfully!")