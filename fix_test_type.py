import json

with open(
    "data/shl_catalog.json",
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

for item in data:

    name = item.get("name", "").lower()

    if "manager" in name:
        item["test_type"] = "B"

    elif "apprentice" in name:
        item["test_type"] = "C"

    else:
        item["test_type"] = "K"

with open(
    "data/shl_catalog.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(data, f, indent=2)

print("test_type added successfully!")