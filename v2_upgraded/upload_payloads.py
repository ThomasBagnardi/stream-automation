import os
from pathlib import Path

import boto3
from dotenv import load_dotenv

# Force load environment variables
dotenv_path = Path(__file__).parent / ".env"
if not dotenv_path.exists():
    dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")


def upload_stream_data(file_path, bucket_name=None):
    """Uploads a validated file to AWS S3."""

    if bucket_name is None:
        bucket_name = (
            os.environ.get("AWS_S3_BUCKET_NAME")
            or "streaming-analytics-pipeline-thomasbagnardi"
        )

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name="us-east-2",
    )

    file_name = os.path.basename(file_path)
    try:
        s3.upload_file(file_path, bucket_name, file_name)
        print(f"📦 Successfully dispatched {file_name} to AWS S3.")
        return True
    except Exception as e:
        print(f"❌ Core Upload Failure: {e}")
        raise e
