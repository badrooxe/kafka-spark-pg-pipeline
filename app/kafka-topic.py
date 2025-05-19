from kafka.admin import KafkaAdminClient, NewTopic

admin_client = KafkaAdminClient(bootstrap_servers="kafka:9092")

topic_name = "sensor-data"
topic_list = [NewTopic(name=topic_name, num_partitions=1, replication_factor=1)]

try:
    admin_client.create_topics(new_topics=topic_list, validate_only=False)
    print(f"Topic '{topic_name}' created successfully")
except Exception as e:
    print(f"Topic creation failed or already exists")
    print("Topics:", admin_client.list_topics())
admin_client.close()
