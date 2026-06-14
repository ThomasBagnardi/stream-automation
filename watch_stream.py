import json
import logging
import os
import shutil
import time

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from upload_payloads import upload_stream_data

load_dotenv()
WATCH_DIR = os.getenv("WATCH_DIR", "./stream_drops")
ARCHIVE_DIR = os.path.join(WATCH_DIR, "archive")

# Create directories if they don't exist
os.makedirs(WATCH_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


class StreamTelemetry(BaseModel):
    viewer_count: int = Field(ge=0)
    bitrate_kbps: int = Field(ge=1000, le=12000)


def process_files():
    """Manually scans the directory for new payloads."""
    for filename in os.listdir(WATCH_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(WATCH_DIR, filename)

            try:
                with open(file_path, "r") as f:
                    data = json.load(f)

                # Validation
                validated_telemetry = StreamTelemetry(**data)
                logging.info(f"✅ Verified: {filename}")

                # Upload and Move to archive to prevent duplicate processing
                upload_stream_data(file_path)
                shutil.move(file_path, os.path.join(ARCHIVE_DIR, filename))

            except Exception as e:
                logging.error(f"❌ Failed to process {filename}: {e}")
                # Move bad files to a 'failed' subfolder so they don't block the loop
                failed_dir = os.path.join(WATCH_DIR, "failed")
                os.makedirs(failed_dir, exist_ok=True)
                shutil.move(file_path, os.path.join(failed_dir, filename))


if __name__ == "__main__":
    logging.info("🚀 Heartbeat Monitor Active...")
    while True:
        process_files()
        time.sleep(2)  # Scans every 2 seconds
