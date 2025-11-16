# 📦 Real-Time Product Review Analyzer  
### 🔍 A Kafka-based live sentiment analysis pipeline for e-commerce reviews

This project is an **end-to-end real-time data processing system** that streams product reviews, performs **NLP sentiment analysis**, stores results, and visualizes insights on a **live interactive dashboard**.

It demonstrates production-level skills in **stream processing, APIs, NLP, dashboarding, and microservices**.

---

## 🚀 Features

### ✅ **Real-time Review Ingestion**
- Accepts live product reviews via REST API (`/reviews`)
- Streams each review instantly to **Apache Kafka**

### ✅ **NLP Sentiment Analysis**
- Consumer application reads Kafka messages
- Uses TextBlob to compute:
  - Sentiment polarity
  - Sentiment label (positive/neutral/negative)
- Adds processed reviews to a CSV data store

### ✅ **Interactive Streamlit Dashboard**
- Live auto-refresh every 5 seconds
- Sentiment distribution chart  
- Brand-wise sentiment comparison  
- Time-based polarity trend  
- Product-wise summary cards  
- Latest reviews table  
- Sidebar form to POST new reviews to API

### ✅ **Fallback Mode (No Kafka? No Problem!)**
If Kafka is unavailable:
- API writes to `stream.jsonl`
- Fallback consumer processes the file
- Dashboard still updates regularly  
**→ Your project always works**, even without Kafka.

---

## 🏗️ Architecture
    ┌──────────────┐       ┌───────────────┐
    │ Review Input  │       │ Streamlit UI  │
    │ (User/API)    │       │ (Dashboard)   │
    └──────┬────────┘       └───────┬──────┘
           │                        │
           ▼                        │
   ┌───────────────┐                │
   │  FastAPI API  │  <─────────────┘
   └──────┬────────┘
           │
     (Kafka Producer)
           │
           ▼
   ┌───────────────┐
   │ Kafka Topic    │  reviews_stream
   └──────┬────────┘
           │
           ▼
   ┌───────────────┐
   │ Python Consumer│ (sentiment analysis)
   └──────┬────────┘
           │
           ▼
 ┌─────────────────────┐
 │ processed_reviews.csv│
 └─────────────────────┘

---

## 🛠️ Tech Stack

### **Languages & Tools**
- Python 3.x
- Streamlit
- FastAPI
- Apache Kafka
- Docker & Docker Compose
- Pandas
- TextBlob (sentiment analysis)
- Plotly (visualization)

---







