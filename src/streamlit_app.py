# src/streamlit_app.py
import os
import time
import pandas as pd
import streamlit as st
import plotly.express as px

# Path to the processed CSV (consumer writes to this)
PROCESSED_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "processed_reviews.csv")

st.set_page_config(page_title="Real-Time Product Review Analyzer", layout="wide")
st.title("Real-Time Product Review Analyzer (E-commerce)")

# Sidebar controls
auto_refresh = st.sidebar.checkbox("Auto-refresh (5s)", value=True)
st.sidebar.markdown("Data source: `data/processed_reviews.csv` appended by consumer")
st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Test: Post a review")
with st.sidebar.form("post_review_form"):
    p_id = st.text_input("Product ID", value="p101")
    p_title = st.text_input("Product Title", value="Demo Product")
    p_brand = st.text_input("Brand", value="DemoBrand")
    p_text = st.text_area("Review text", value="This product is fantastic and works as expected.")
    p_rating = st.selectbox("Rating", options=[1,2,3,4,5], index=4)
    submit_review = st.form_submit_button("POST review to API")
if submit_review:
    # Try to post to the API; if requests missing or API down, notify user
    try:
        import requests
        api_url = os.getenv("INGEST_API", "http://localhost:8000/reviews")
        payload = {
            "product_id": p_id,
            "product_title": p_title,
            "brand": p_brand,
            "review_text": p_text,
            "rating": p_rating
        }
        resp = requests.post(api_url, json=payload, timeout=5)
        if resp.status_code in (200, 201):
            st.sidebar.success(f"Posted (source: {resp.json().get('source')}) id={resp.json().get('id')}")
        else:
            st.sidebar.error(f"API returned {resp.status_code}: {resp.text}")
    except Exception as e:
        st.sidebar.error(f"Failed to post review: {e}")
st.sidebar.markdown("---")
st.sidebar.markdown("Tips: Start the consumer first so posted reviews get processed and appear in the dashboard.")

# --- Data loader
@st.cache_data(ttl=5)
def load_data():
    if os.path.exists(PROCESSED_CSV):
        df = pd.read_csv(PROCESSED_CSV)
        # ensure timestamp column parsed
        if "timestamp" in df.columns:
            try:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            except:
                pass
        return df
    else:
        return pd.DataFrame(columns=["review_id","product_id","product_title","brand","review_text","rating","timestamp","polarity","sentiment"])

df = load_data()

st.markdown("### Live Summary")
if df.empty:
    st.write("No processed reviews yet. Start producer and consumer (or post a review from the sidebar).")
else:
    # sentiment distribution
    sentiment_counts = df["sentiment"].value_counts().reset_index()
    sentiment_counts.columns = ["sentiment","count"]
    fig1 = px.pie(sentiment_counts, names="sentiment", values="count", title="Sentiment Distribution")
    st.plotly_chart(fig1, use_container_width=True)

    # brand comparison
    brand_sent = df.groupby(["brand","sentiment"]).size().reset_index(name="count")
    fig2 = px.bar(brand_sent, x="brand", y="count", color="sentiment", title="Brand-wise Sentiment Counts")
    st.plotly_chart(fig2, use_container_width=True)

    # trend over time (polarity mean)
    if "timestamp" in df.columns:
        try:
            trend = df.set_index("timestamp").resample("1T")["polarity"].mean().dropna().reset_index()
            if not trend.empty:
                fig3 = px.line(trend, x="timestamp", y="polarity", title="Average Polarity Over Time (1min windows)")
                st.plotly_chart(fig3, use_container_width=True)
        except Exception:
            pass

    # PRODUCT-WISE CARDS
    st.markdown("### Product-wise summary")
    try:
        prod_stats = df.groupby("product_title").agg(
            total_reviews=("review_id","count"),
            avg_polarity=("polarity","mean"),
            positive_cnt=("sentiment", lambda s: (s=="positive").sum()),
            negative_cnt=("sentiment", lambda s: (s=="negative").sum()),
            avg_rating=("rating","mean")
        ).reset_index().sort_values("total_reviews", ascending=False)
        if not prod_stats.empty:
            # compute percentages
            prod_stats["positive_pct"] = prod_stats["positive_cnt"] / prod_stats["total_reviews"] * 100
            prod_stats["negative_pct"] = prod_stats["negative_cnt"] / prod_stats["total_reviews"] * 100

            top_n = min(6, len(prod_stats))
            cards = prod_stats.head(top_n).to_dict(orient="records")

            cols = st.columns(top_n)
            for c, card in zip(cols, cards):
                with c:
                    st.metric(label=card["product_title"], value=f"{int(card['total_reviews'])} reviews")
                    st.write(f"Avg polarity: {card['avg_polarity']:.2f}")
                    st.write(f"Positive: {card['positive_pct']:.0f}%  |  Negative: {card['negative_pct']:.0f}%")
                    if card["avg_rating"] is not None and not pd.isna(card["avg_rating"]):
                        st.write(f"Avg rating: {card['avg_rating']:.2f}/5")
                    # show latest review for this product
                    latest = df[df["product_title"] == card["product_title"]].sort_values("timestamp", ascending=False).head(1)
                    if not latest.empty:
                        txt = latest.iloc[0]["review_text"]
                        sent = latest.iloc[0]["sentiment"]
                        st.caption(f"Latest ({sent}): {txt[:120]}{'...' if len(txt)>120 else ''}")
        else:
            st.write("No product stats available yet.")
    except Exception as e:
        st.write("Could not compute product stats:", e)

    st.markdown("### Latest Processed Reviews")
    st.dataframe(df.sort_values(by="timestamp", ascending=False).head(20))

# Auto-refresh
if auto_refresh:
    time.sleep(5)
    st.rerun()
