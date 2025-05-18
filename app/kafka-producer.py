from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime, timezone

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic = 'sensor-data'

while True:
    data = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'sensor_id': random.randint(1, 10),
        'temperature': round(random.uniform(20.0, 30.0), 2),
        'humidity': round(random.uniform(30.0, 60.0), 2)
    }
    producer.send(topic, value=data)
    print(f"Sent: {data}")
    time.sleep(1)
