import os

import boto3
from dotenv import load_dotenv

from app import LOCALSTACK_ENDPOINT

load_dotenv()

# Pull configuration strings safely
LOCALSTACK_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME", "automated-stream-payloads")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")


def bootstrap_storage():
    """Connects to LocalStack and forces the target S3 bucket into existence."""
    s3 = boto3.client(
        "s3",
        region_name=REGION,
        endpoint_url=LOCALSTACK_ENDPOINT,
        aws_access_key_id="mock",
        aws_secret_access_key="mock",
    )

    try:
        # Check if bucket already exists
        s3.head_bucket(Bucket=BUCKET_NAME)
        print(
            f"🌟 Cloud Storage Verification: Bucket '{BUCKET_NAME}' is already online."
        )
    except Exception:
        print(
            f"📦 Bucket '{BUCKET_NAME}' not found. Initializing fresh mock cloud bucket..."
        )
        s3.create_bucket(Bucket=BUCKET_NAME)
        print("✅ Success: Fresh bucket ready for stream telemetry data dispatches!")


if __name__ == "__main__":
    bootstrap_storage()
