# src/consumer.py
import os
import json
import time
import pandas as pd
from textblob import TextBlob
from confluent_kafka import Consumer, KafkaError

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "reviews_stream")
GROUP_ID = os.getenv("KAFKA_GROUP", "reviews_consumer_group")
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "processed_reviews.csv")

c_conf = {
    "bootstrap.servers": KAFKA_BROKER,
    "group.id": GROUP_ID,
    "auto.offset.reset": "earliest"
}
consumer = Consumer(c_conf)
consumer.subscribe([TOPIC])

# initialize small CSV if not exists
if not os.path.exists(OUTPUT_CSV):
    pd.DataFrame(columns=["review_id","product_id","product_title","brand","review_text","rating","timestamp","polarity","sentiment"]).to_csv(OUTPUT_CSV, index=False)

def classify_sentiment(text):
    tb = TextBlob(text)
    polarity = tb.sentiment.polarity
    if polarity > 0.1:
        lbl = "positive"
    elif polarity < -0.1:
        lbl = "negative"
    else:
        lbl = "neutral"
    return polarity, lbl

def run_consumer():
    print(f"Consuming from topic '{TOPIC}' on {KAFKA_BROKER}")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print("Consumer error: ", msg.error())
                    continue

            payload = json.loads(msg.value().decode("utf-8"))
            text = payload.get("review_text", "")
            polarity, sentiment = classify_sentiment(text)
            output_row = {
                "review_id": payload.get("review_id"),
                "product_id": payload.get("product_id"),
                "product_title": payload.get("product_title"),
                "brand": payload.get("brand"),
                "review_text": text,
                "rating": payload.get("rating"),
                "timestamp": payload.get("timestamp"),
                "polarity": polarity,
                "sentiment": sentiment
            }
            # append to CSV
            df = pd.DataFrame([output_row])
            df.to_csv(OUTPUT_CSV, mode="a", header=False, index=False)
            print(f"Processed review {output_row['review_id']} | sentiment: {sentiment} ({polarity:.2f})")
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    run_consumer()
