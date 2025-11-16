# Real-Time Product Review Analyzer

## Overview
Real-Time Product Review Analyzer streams product reviews (from a local CSV or dataset) into Apache Kafka, processes them with TextBlob to determine sentiment, and visualizes results on a live dashboard (Streamlit). The project demonstrates real-time data ingestion, processing, and analytics for e-commerce.

## Tech stack
- Python, TextBlob, Pandas
- Apache Kafka (via Docker Compose)
- Streamlit + Plotly for visualization

## Setup (local)
1. Clone repo
2. Create virtual env and install dependencies:
