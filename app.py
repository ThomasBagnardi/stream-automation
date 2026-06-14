import json
import os

import boto3
import pandas as pd
import plotly.express as px
import streamlit as tf_stream
from botocore.exceptions import EndpointConnectionError
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# --- Configuration Constants Decoupled from Code ---
LOCALSTACK_ENDPOINT = os.getenv("AWS_ENDPOINT_URL")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
REGION = os.getenv("AWS_DEFAULT_REGION")
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")


def fetch_s3_data():
    """Connects to LocalStack and retrieves all stream JSON payloads safely."""
    s3 = boto3.client(
        "s3",
        region_name=REGION,
        aws_access_key_id=AWS_KEY,
        aws_secret_access_key=AWS_SECRET,
        endpoint_url=LOCALSTACK_ENDPOINT,
        use_ssl=False,
    )

    payloads = []
    # FIX: Explicitly initialize the response variable so it always exists
    response = {}

    try:
        # List all objects in the bucket
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        if "Contents" in response:
            for item in response["Contents"]:
                obj = s3.get_object(Bucket=BUCKET_NAME, Key=item["Key"])
                file_content = obj["Body"].read().decode("utf-8")
                data = json.loads(file_content)
                data["filename"] = item["Key"]
                payloads.append(data)
    except EndpointConnectionError:
        tf_stream.error(
            "❌ Unable to connect to LocalStack. Is your Docker container running?"
        )
    except Exception as e:
        tf_stream.error(f"❌ Error fetching data from cloud storage: {e}")

    return payloads


# --- Streamlit Dashboard Layout ---
# CRITICAL: This MUST stay as the absolute first Streamlit visual command
tf_stream.set_page_config(page_title="Stream Automation Analytics", layout="wide")
tf_stream.title("🎮 Stream Performance Analytics Dashboard")
tf_stream.subheader("Real-time telemetry ingestion from LocalStack S3")

# Fetch data from our mock cloud storage
raw_data = fetch_s3_data()

if not raw_data:
    tf_stream.info(
        "✨ S3 Bucket is currently empty or LocalStack is initializing. Drop some files into 'stream_drops' to see them here!"
    )
else:
    # Convert list of JSON payloads into a structured DataFrame
    df = pd.DataFrame(raw_data)

    # --- Metrics Section ---
    col1, col2, col3 = tf_stream.columns(3)
    with col1:
        tf_stream.metric(label="Total Payloads Ingested", value=len(df))
    with col2:
        if "viewer_count" in df.columns:
            tf_stream.metric(
                label="Peak Viewer Count", value=int(df["viewer_count"].max())
            )
    with col3:
        if "bitrate_kbps" in df.columns:
            avg_bitrate = int(df["bitrate_kbps"].mean())
            tf_stream.metric(label="Avg Bitrate (Kbps)", value=f"{avg_bitrate} kbps")

    tf_stream.markdown("---")

    # --- Charts Section ---
    chart_col1, chart_col2 = tf_stream.columns(2)

    with chart_col1:
        if "viewer_count" in df.columns:
            tf_stream.write("### 📈 Audience Growth Loop")
            fig_viewers = px.line(
                df,
                x="filename",
                y="viewer_count",
                markers=True,
                labels={"filename": "Payload Timeline", "viewer_count": "Viewers"},
                title="Viewer Count Over Time",
            )
            tf_stream.plotly_chart(fig_viewers, use_container_width=True)

    with chart_col2:
        if "bitrate_kbps" in df.columns:
            tf_stream.write("### ⚡ Stream Health & Stability")
            fig_bitrate = px.bar(
                df,
                x="filename",
                y="bitrate_kbps",
                labels={
                    "filename": "Payload Timeline",
                    "bitrate_kbps": "Bitrate (Kbps)",
                },
                title="Bitrate Allocation per Event",
                color_discrete_sequence=["#00CC96"],
            )
            tf_stream.plotly_chart(fig_bitrate, use_container_width=True)

    # --- Raw Data Inspector ---
    with tf_stream.expander("🔍 Inspect Raw S3 Dataframe"):
        tf_stream.dataframe(df)
