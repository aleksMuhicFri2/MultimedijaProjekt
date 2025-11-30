import requests

BASE_URL = "https://pxweb.stat.si/SiStatData/api/v1/sl/Data"


def fetch_px(table_id, query=None):
    url = f"{BASE_URL}/{table_id}"

    body = {
        "query": query or [],
        "response": {"format": "JSON"}
    }

    res = requests.post(url, json=body)

    if not res.ok:
        print("SURS API ERROR:", res.text)
        return None

    return res.json()


def get_population_per_obcina():
    return fetch_px("05C4003S", [
        {
            "code": "OBČINE",
            "selection": {"filter": "all", "values": ["*"]}
        },
        {
            "code": "POLLETJE",
            "selection": {"filter": "item", "values": ["2024H2"]}
        },
        {
            "code": "STAROST",
            "selection": {"filter": "all", "values": ["*"]}
        }
    ])