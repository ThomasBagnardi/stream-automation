import os
import time
import boto3
import threading
from pathlib import Path
from dotenv import load_dotenv
from prometheus_client import start_http_server, Gauge, Counter, Histogram

# Load env
dotenv_path = Path(__file__).parent / ".env"
if not dotenv_path.exists():
    dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# --- Metrics ---
APP_INFO = Gauge(
    'stream_pipeline_app_info',
    'Stream pipeline application info',
    ['version']
)
S3_RECORDS_FETCHED = Gauge(
    'streamlit_s3_records_fetched',
    'Number of records fetched from S3 in the last fetch'
)
S3_FETCH_TOTAL = Counter(
    'streamlit_s3_fetch_total',
    'Total number of times S3 data has been fetched'
)
S3_FETCH_ERRORS = Counter(
    'streamlit_s3_fetch_errors_total',
    'Total number of S3 fetch errors'
)
S3_FETCH_DURATION = Histogram(
    'streamlit_s3_fetch_duration_seconds',
    'Time taken to fetch data from S3'
)

APP_INFO.labels(version='1.0').set(1)


def fetch_s3_metrics():
    """Fetch S3 data and update Prometheus metrics."""
    bucket_name = os.environ.get("AMAZON_S3_BUCKET_NAME") or "streaming-analytics-pipeline-thomasbagnardi"
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=region,
    )

    S3_FETCH_TOTAL.inc()
    start_time = time.time()

    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        count = len([
            obj for obj in response.get("Contents", [])
            if obj["Key"].endswith(".json")
        ])
        S3_RECORDS_FETCHED.set(count)
        S3_FETCH_DURATION.observe(time.time() - start_time)
        print(f"[METRICS] S3 fetch ok — {count} records", flush=True)
    except Exception as e:
        S3_FETCH_ERRORS.inc()
        print(f"[METRICS] S3 fetch error: {e}", flush=True)


def metrics_loop():
    """Fetch S3 metrics every 60 seconds."""
    while True:
        fetch_s3_metrics()
        time.sleep(60)


if __name__ == "__main__":
    port = int(os.environ.get("METRICS_PORT", 8000))
    start_http_server(port)
    print(f"[METRICS] Server running on port {port}", flush=True)

    # Run first fetch immediately
    fetch_s3_metrics()

    # Start polling loop in background thread
    thread = threading.Thread(target=metrics_loop, daemon=True)
    thread.start()

    # Keep main thread alive
    while True:
        time.sleep(60)
