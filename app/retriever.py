import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

with open("data/shl_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

documents = []

for item in catalog:
    text = (
        item.get("name", "") + " " +
        item.get("description", "") + " " +
        item.get("category", "")
    )
    documents.append(text)

vectorizer = TfidfVectorizer(stop_words="english")

tfidf_matrix = vectorizer.fit_transform(documents)

def search_assessments(query, top_k=5):

    query_vector = vectorizer.transform([query])

    similarities = cosine_similarity(
        query_vector,
        tfidf_matrix
    ).flatten()

    top_indices = similarities.argsort()[-top_k:][::-1]

    results = []

    for idx in top_indices:

        item = catalog[idx]

        results.append({
            "name": item["name"],
            "url": item["url"]
        })

    return results


if __name__ == "__main__":

    query = "Java developer communication"

    results = search_assessments(query)

    print("\nTop Results:\n")

    for r in results:
        print("NAME:", r["name"])
        print("URL:", r["url"])
        print()