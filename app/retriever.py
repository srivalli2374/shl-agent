import json
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer

# =========================
# LOAD MODEL
# =========================
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# =========================
# LOAD FAISS INDEX
# =========================
index = faiss.read_index(
    "embeddings/shl.index"
)

# =========================
# LOAD METADATA
# =========================
with open(
    "embeddings/metadata.json",
    "r",
    encoding="utf-8"
) as f:

    metadata = json.load(f)

# =========================
# TECHNICAL KEYWORD BOOSTING
# =========================
TECH_KEYWORDS = {

    "java": [
        "java",
        "developer",
        "programming",
        "software",
        "coding"
    ],

    "python": [
        "python",
        "developer",
        "coding",
        "software"
    ],

    "developer": [
        "developer",
        "programming",
        "software",
        "technical"
    ],

    "communication": [
        "communication",
        "personality",
        "behavior",
        "stakeholder"
    ],

    "leadership": [
        "leadership",
        "management",
        "decision making"
    ],

    "stakeholder": [
        "communication",
        "personality",
        "behavior"
    ]
}

# =========================
# SEARCH FUNCTION
# =========================
def search_assessments(query, top_k=5):

    query_lower = query.lower()

    boosted_keywords = []

    # Add boosted keywords
    for key, values in TECH_KEYWORDS.items():

        if key in query_lower:

            boosted_keywords.extend(values)

    all_keywords = (
        query_lower.split() + boosted_keywords
    )

    # Generate query embedding
    query_embedding = model.encode([query])

    query_embedding = np.array(
        query_embedding
    ).astype("float32")

    # Search FAISS
    distances, indices = index.search(
        query_embedding,
        top_k * 5
    )

    scored_results = []

    for idx in indices[0]:

        item = metadata[idx]

        combined_text = (
            item.get("name", "") + " " +
            item.get("description", "")
        ).lower()

        score = 0

        # Keyword scoring
        for keyword in all_keywords:

            if keyword in combined_text:
                score += 2

        scored_results.append(
            (
                score,
                {
                    "name": item.get("name"),
                    "url": item.get("url"),
                    "description": item.get("description")
                }
            )
        )

    # Sort results
    scored_results.sort(
        key=lambda x: x[0],
        reverse=True
    )

    final_results = []

    used = set()

    for score, item in scored_results:

        if item["name"] not in used:

            final_results.append(item)

            used.add(item["name"])

        if len(final_results) >= top_k:
            break

    return final_results

# =========================
# TEST SEARCH
# =========================
if __name__ == "__main__":

    query = "Java developer with communication skills"

    results = search_assessments(query)

    print("\nTop Results:\n")

    for r in results:

        print("NAME:", r["name"])
        print("URL:", r["url"])
        print()