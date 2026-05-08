import json
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Load full catalog
with open(
    "data/shl_catalog.json",
    "r",
    encoding="utf-8"
) as f:

    assessments = json.load(f)

documents = []

for item in assessments:

    text = f"""
    Assessment Name:
    {item.get('name', '')}

    Description:
    {item.get('description', '')}

    Job Levels:
    {' '.join(item.get('job_levels', []))}

    Skills Category:
    {' '.join(item.get('keys', []))}

    Duration:
    {item.get('duration', '')}

    Languages:
    {' '.join(item.get('languages', []))}

    Adaptive:
    {item.get('adaptive', '')}

    Remote:
    {item.get('remote', '')}
    """

    documents.append(text)

# Generate embeddings
embeddings = model.encode(documents)

embeddings = np.array(
    embeddings
).astype("float32")

# Create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

# Save index
faiss.write_index(
    index,
    "embeddings/shl.index"
)

# Save metadata
with open(
    "embeddings/metadata.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        assessments,
        f,
        indent=2
    )

print("FAISS index created successfully!")