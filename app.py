import json
import os
from pathlib import Path

import boto3
import pandas as pd
import plotly.express as px
import streamlit as st
from botocore.exceptions import EndpointConnectionError
from dotenv import load_dotenv

# Load environment variables
dotenv_path = Path(__file__).parent / ".env"
if not dotenv_path.exists():
    dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# --- Configuration ---
BUCKET_NAME = os.environ.get("AMAZON_S3_BUCKET_NAME") or "streaming-analytics-pipeline-thomasbagnardi"

try:
    aws_access_key_id = st.secrets["AWS_ACCESS_KEY_ID"]
    aws_secret_access_key = st.secrets["AWS_SECRET_ACCESS_KEY"]
except Exception:
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")


def fetch_s3_data():
    s3 = boto3.client(
        "s3",
        region_name="us-east-2",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    payloads = []

    try:
        # Step 1: List all objects in the bucket
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)

        # Step 2: If bucket is empty, return early
        if "Contents" not in response:
            st.info("✨ No stream data found yet. Run generate_analytics.py to populate the dashboard.")
            return payloads

        # Step 3: Loop through files and parse JSON
        for item in response["Contents"]:
            key = item["Key"]

            # Skip non-JSON files
            if not key.endswith(".json"):
                print(f"[DEBUG] Skipping non-JSON file: {key}")
                continue

            obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
            file_content = obj["Body"].read().decode("utf-8")
            data = json.loads(file_content)
            data["filename"] = key
            payloads.append(data)

    except EndpointConnectionError:
        st.error("❌ Unable to connect to AWS S3. Check your credentials and region.")
    except Exception as e:
        st.error(f"❌ Error fetching data from cloud storage: {e}")

    return payloads


# --- Streamlit Dashboard Layout ---
st.set_page_config(page_title="Stream Automation Analytics", layout="wide")
st.title("🎮 Stream Performance Analytics Dashboard")
st.subheader("Real-time telemetry ingestion from AWS S3")

raw_data = fetch_s3_data()

if not raw_data:
    st.info("✨ No stream data found yet. Run the data generator to populate the dashboard.")
else:
    df = pd.DataFrame(raw_data)

    # --- Metrics ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Payloads Ingested", value=len(df))
    with col2:
        if "viewer_count" in df.columns:
            st.metric(label="Peak Viewer Count", value=int(df["viewer_count"].max()))
    with col3:
        if "bitrate_kbps" in df.columns:
            avg_bitrate = int(df["bitrate_kbps"].mean())
            st.metric(label="Avg Bitrate (Kbps)", value=f"{avg_bitrate} kbps")

    st.markdown("---")

    # --- Charts ---
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        if "viewer_count" in df.columns:
            st.write("### 📈 Audience Growth Loop")
            fig_viewers = px.line(
                df,
                x="filename",
                y="viewer_count",
                markers=True,
                labels={"filename": "Payload Timeline", "viewer_count": "Viewers"},
                title="Viewer Count Over Time",
            )
            st.plotly_chart(fig_viewers, use_container_width=True)

    with chart_col2:
        if "bitrate_kbps" in df.columns:
            st.write("### ⚡ Stream Health & Stability")
            fig_bitrate = px.bar(
                df,
                x="filename",
                y="bitrate_kbps",
                labels={"filename": "Payload Timeline", "bitrate_kbps": "Bitrate (Kbps)"},
                title="Bitrate Allocation per Event",
                color_discrete_sequence=["#00CC96"],
            )
            st.plotly_chart(fig_bitrate, use_container_width=True)

    # --- Raw Data Inspector ---
    with st.expander("🔍 Inspect Raw S3 Dataframe"):
        st.dataframe(df)
