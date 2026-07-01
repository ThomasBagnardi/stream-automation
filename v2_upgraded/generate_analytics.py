import json
import os
import random
import tempfile
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

dotenv_path = Path(__file__).parent / ".env"
if not dotenv_path.exists():
    dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)
print(f"[ENV] Loaded .env from: {dotenv_path}")

BUCKET_NAME = os.environ.get("AMAZON_S3_BUCKET_NAME")
print(f"[ENV] Bucket name: {BUCKET_NAME}")

# --- Import existing pipeline modules ---
from stream_planner_v2 import parse_schedule
from upload_payloads import upload_stream_data


def generate_analytics(streams: list) -> list:
    """Takes a list of parsed stream dictionaries from parse_schedule() and generates realistic analytics JSON for each one.

    Each record contains fields the Streamlit dashboard expects: viewer_count, bitrate_kbps, plus additional context fields."""

    analytics = []

    for i, stream in enumerate(streams):
        record = {
            # --- Core fields the dashboard charts ---
            "viewer_count": random.randint(500, 5000),
            "bitrate_kbps": random.randint(3000, 6000),
            # --- Stream context fields ---
            "date": stream["date"].isoformat(),
            "game": stream["game"],
            "notes": stream["notes"],
            "stream_title": f"{stream['game']} - {stream['notes']}",
            # ---Simulated engagement metrics ---
            "duration_minutes": random.randint(60, 240),
            "chat_messages": random.randint(100, 2000),
            "new_followers": random.randint(5, 150),
            "peak_viewers": random.randint(500, 7000),
            # --- Pipeline metadata ---
            "generated_at": datetime.now().isoformat(),
            "record_index": i,
        }
        analytics.append(record)
    return analytics


def upload_analytics(analytics: list) -> None:
    """
    Writes each analytics record to a temporary JSON file and uploads it to S3 using upload_stream_data().
    Cleans up temporary files after each upload.
    """

    success_count = 0
    fail_count = 0

    for record in analytics:
        # Build a unique filename using date and index
        filename = (
            f"stream_analytics_{record['date']}_{record['record_index']:03d}.json"
        )
        temp_path = Path(tempfile.gettempdir()) / filename

        try:
            # Write the record to a temporary local file
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2)

            # Upload to S3 using the existing upload function
            upload_stream_data(str(temp_path), bucket_name=BUCKET_NAME)
            print(f"✅ Uploaded: {filename}")
            success_count += 1

        except Exception as e:
            print(f"❌ Failed to upload {filename}: {e}")
            fail_count += 1
        finally:
            # Always clean up the temp file whether upload succeeded or not
            if temp_path.exists():
                temp_path.unlink()

    print(
        f"\n[PIPELINE] Upload complete - {success_count} succeeded, {fail_count} failed."
    )


if __name__ == "__main__":
    print("\n[PIPELINE] Starting analytics generation...\n")

    # Step 1: Parse schedule from messy_notes.txt
    # Path is resolved relative to this script's location
    script_dir = Path(__file__).parent
    streams = parse_schedule(
        str(script_dir / "messy_notes.txt"), str(script_dir / "SCHEDULE.md")
    )

    if not streams:
        print(
            "[ERROR] No streams found. Check that messy_notes.txt exists and has valid data."
        )
        exit(1)

    print(f"[PIPELINE] Parsed {len(streams)} streams from schedule.\n")

    # Step 2: Generate analytics records
    analytics = generate_analytics(streams)
    print(f"[PIPELINE] Generated {len(analytics)} analytics records.\n")

    # Step 3: Upload each record to AWS S3
    print("[PIPELINE] Uploading to AWS S3...")
    upload_analytics(analytics)

    print("\n[PIPELINE] All done! Refresh your Streamlit dashboard to see the data.")
