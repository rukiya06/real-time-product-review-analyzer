# src/api_server.py
import os
import json
import time
from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer
import uuid

app = FastAPI()

# ---------- REQUEST MODEL ----------
class Review(BaseModel):
    product_id: str
    product_title: str
    brand: str
    review_text: str
    rating: int


# ---------- KAFKA SETUP ----------
USE_FALLBACK = os.getenv("USE_FALLBACK", "").lower() == "true"

producer = None
if not USE_FALLBACK:
    try:
        producer = KafkaProducer(
            bootstrap_servers=["localhost:9092"],
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        print("Kafka Producer initialized.")
    except Exception as e:
        print("Kafka ERROR, switching to fallback:", e)
        USE_FALLBACK = True


# ---------- API ENDPOINT ----------
@app.post("/reviews")
def add_review(review: Review):
    review_id = f"r_api_{int(time.time() * 1000)}"

    record = review.dict()
    record["review_id"] = review_id
    record["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

    if USE_FALLBACK:
        with open("data/stream.jsonl", "a") as f:
            f.write(json.dumps(record) + "\n")

        return {"status": "ok", "source": "fallback_file", "id": review_id}

    else:
        producer.send("reviews_stream", record)
        producer.flush()
        return {"status": "ok", "source": "kafka", "id": review_id}
