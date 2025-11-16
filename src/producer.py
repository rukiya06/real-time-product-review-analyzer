# src/producer.py
import os
import time
import json
import pandas as pd
from confluent_kafka import Producer
from tqdm import tqdm

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "reviews_stream")
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_reviews.csv")

p_conf = {"bootstrap.servers": KAFKA_BROKER}
producer = Producer(p_conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    # else:
    #     print(f"Delivered message to {msg.topic()} [{msg.partition()}]")

def produce_reviews(rate_per_sec=1):
    df = pd.read_csv(CSV_PATH)
    for _, row in df.iterrows():
        payload = {
            "review_id": str(row.get("review_id", "")),
            "product_id": str(row.get("product_id", "")),
            "product_title": str(row.get("product_title", "")),
            "brand": str(row.get("brand", "")),
            "review_text": str(row.get("review_text", "")),
            "rating": row.get("rating", None),
            "timestamp": str(row.get("timestamp", ""))
        }
        producer.produce(TOPIC, json.dumps(payload).encode("utf-8"), callback=delivery_report)
        producer.poll(0)
        time.sleep(1.0 / rate_per_sec)
    producer.flush()

# quick loop change (append to existing file or replace)
if __name__ == "__main__":
    print(f"Producing reviews to topic '{TOPIC}' at broker {KAFKA_BROKER}")
    while True:
        produce_reviews(rate_per_sec=1)
