from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'sensor-data',
    bootstrap_servers='kafka:9092',
    auto_offset_reset='earliest',
    group_id='sensor-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Starting consumer...")

for message in consumer:
    data = message.value
    print(f"Received: {data}")
