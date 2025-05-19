import requests
import json
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
params = {
    "format": "geojson",
    "eventtype": "earthquake",
    "orderby": "time",
    "limit": 5
}

seen_ids = set()

while True:
    response = requests.get(url, params=params)
    data = response.json()

    for feature in data["features"]:
        quake_id = feature["id"]
        if quake_id not in seen_ids:
            seen_ids.add(quake_id)
            props = feature["properties"]
            payload = {
                "id": quake_id,
                "place": props["place"],
                "magnitude": props["mag"],
                "time": props["time"],
                "updated": props["updated"]
            }
            producer.send("sensor-data", value=payload)
            print("Sent:", payload)

    time.sleep(30)  # check every 30 seconds
