import os
from datetime import date, datetime
from pathlib import Path

import boto3


def parse_schedule(input_filename: str, output_filename: str) -> list:
    # Use the safety trick to ensure it always finds the file
    script_dir = Path(__file__).parent
    input_path = script_dir / input_filename
    output_path = script_dir / output_filename

    if not input_path.exists():
        print(f"[ERROR] Could not find the file: {input_filename}")
        return []

    # This list will temporarily hold our parsed stream objects
    streams = []
    today = date.today()

    # --- Phase 1: Parse Data into Structures ---
    with open(input_path, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            parts = line.split("|")
            if len(parts) < 3:
                continue

            date_raw = parts[0].replace("date:", "").strip()
            game = parts[1].replace("game:", "").strip()
            notes = parts[2].replace("notes:", "").strip()

            try:
                stream_date = datetime.strptime(date_raw, "%Y-%m-%d").date()
            except ValueError:
                print(f"[WARNING] Skipping line due to invalid date format: {date_raw}")
                continue

            # Create a structured dictionary for this stream
            stream_data = {"date": stream_date, "game": game, "notes": notes}
            streams.append(stream_data)

    # --- Phase 2: Sort Chronologically ---
    # Lambda tells Python to sort the list of dictionaries by their 'date' key
    streams.sort(key=lambda x: x["date"])

    # --- Phase 3: Calculate Status & Build Markdown ---
    markdown_lines = [
        "# 🎮 Upcoming Stream Schedule & Content Plan\n",
        f"Updated automatically on: **{today.strftime('%b %d, %Y')}**\n",
        "| Status | Date | Game / Category | Stream Focus & Notes |",
        "| :--- | :--- | :--- | :--- |",
    ]

    for stream in streams:
        # Calculate the relative time difference
        days_until = (stream["date"] - today).days

        # Dynamic Status Logic
        if days_until == 0:
            status = "🔴 **[LIVE TODAY]**"
        elif days_until == 1:
            status = "⏳ *[TOMORROW]*"
        elif days_until > 1:
            status = f"📅 [In {days_until} days]"
        else:
            status = "✅ *[PAST]*"

        friendly_date = stream["date"].strftime("%b %d, %Y")

        # Append the new row including the Status column
        markdown_lines.append(
            f"| {status} | **{friendly_date}** | {stream['game']} | {stream['notes']} |"
        )

    # Write the compiled Markdown
    with open(output_path, "w", encoding="utf-8") as file:
        file.write("\n".join(markdown_lines))

    print(f"[SUCCESS] Upgraded schedule exported to: {output_path.resolve()}")

    # This return is explicitly for returning structured list back to caller!
    return streams


def upload_schedule_to_cloud():
    print("\n[CLOUD] Preparing to cloud sync...")

    # 1. Connect to LocalStack S3 (Using Mac loopback address)
    aws_endpoint = os.getenv(
        "AWS_ENDPOINT_URL", "host.docker.internal:4566"
    )  # For Docker use 'host.docker.internal' for local use 'http://127.0.0.1:4566'

    s3 = boto3.client("s3", endpoint_url=aws_endpoint)

    bucket_name = "stream-schedule-bucket"
    local_file = "SCHEDULE_v2.md"
    cloud_filename = "live_schedule.md"

    try:
        # 2. Upload file to virtual s3 bucket
        s3.upload_file(local_file, bucket_name, cloud_filename)
        print(f"[SUCCESS] Schedule uploaded to virtual AWS S3 as '{cloud_filename}'!")

    except Exception as e:
        print(f"[ERROR] Cloud upload has failed: {e}")


# Call the function at the very end of your script execution
if __name__ == "__main__":
    # parse_schedule("messy_notes.txt", "SCHEDULE.md")

    # with open("SCHEDULE_v2.md", "w") as f:
    # f.write(Path("SCHEDULE_v2.md").read_text())
    # print("[SYSTEM] SCHEDULE_v2.md successfully generated on disk.")

    # upload_schedule_to_cloud()
    pass
