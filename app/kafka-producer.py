import time
import requests
import json
from kafka import KafkaProducer

# Set up Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

API_URL = "https://disease.sh/v3/covid-19/countries"
TOPIC = "covid-countries"

def fetch_covid_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching COVID-19 data: {e}")
        return []

def send_to_kafka(data):
    for country in data:
        try:
            print(f"Sending data for {country['country']} to Kafka...")
            #print(f"Data: {country}")
            producer.send(TOPIC, value=country)
        except Exception as e:
            print(f"Failed to send data to Kafka: {e}")

if __name__ == "__main__":
    while True:
        print("Fetching and sending COVID-19 data...")
        covid_data = fetch_covid_data()
        if covid_data:
            send_to_kafka(covid_data)
            print(f"Sent {len(covid_data)} records to Kafka.")
        else:
            print("No data sent.")
        
        # Wait for 10 minutes before next call
        time.sleep(600)
