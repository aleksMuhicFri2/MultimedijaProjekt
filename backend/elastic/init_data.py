import elasticsearch

es = elasticsearch.Elasticsearch(hosts=["http://localhost:9200"])
INDEX = "regions"

if not es.indices.exists(index=INDEX):
    es.indices.create(index=INDEX)

sample = [
    {"region": "gorenjska", "salary": 1750, "housing": 2400, "pollution": 32, "health": 7},
    {"region": "primorska", "salary": 1800, "housing": 3100, "pollution": 30, "health": 8},
    {"region": "stajerska", "salary": 1600, "housing": 2000, "pollution": 45, "health": 6}
]

for entry in sample:
    es.index(index=INDEX, document=entry)

print("Loaded sample data")