# src/create_topic.py
import os
from confluent_kafka.admin import AdminClient, NewTopic

broker = os.getenv("KAFKA_BROKER", "localhost:9092")
topic = os.getenv("KAFKA_TOPIC", "reviews_stream")

admin_conf = {"bootstrap.servers": broker}
admin = AdminClient(admin_conf)

new_topic = NewTopic(topic, num_partitions=1, replication_factor=1)
fs = admin.create_topics([new_topic])

for t, f in fs.items():
    try:
        f.result()
        print(f"Topic '{t}' created")
    except Exception as e:
        print(f"Failed to create topic {t}: {e}")
