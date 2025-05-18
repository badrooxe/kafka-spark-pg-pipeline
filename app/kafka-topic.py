from kafka.admin import KafkaAdminClient

admin_client = KafkaAdminClient(bootstrap_servers="kafka:9092")
print("Topics:", admin_client.list_topics())
admin_client.close()
