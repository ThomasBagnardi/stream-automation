import os

import boto3
from dotenv import load_dotenv

# Force load environment variables
load_dotenv()

# --- Configuration Constants with Strict String Fallbacks ---
LOCALSTACK_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME", "automated-stream-payloads")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "mock_access_key")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY", "mock_secret_key")


def upload_stream_data(file_path):
    """Uploads a validated file to the local mock S3 bucket safely."""

    # Defensive check: Ensure no configuration values accidentally passed as None
    s3 = boto3.client(
        "s3",
        region_name=str(REGION),
        aws_access_key_id=str(AWS_KEY),
        aws_secret_access_key=str(AWS_SECRET),
        endpoint_url=str(LOCALSTACK_ENDPOINT),
        use_ssl=False,
    )

    file_name = os.path.basename(file_path)
    try:
        s3.upload_file(file_path, str(BUCKET_NAME), file_name)
        print(f"📦 Successfully dispatched {file_name} to mock cloud storage.")
        return True
    except Exception as e:
        print(f"❌ Core Upload Failure: {e}")
        raise e
