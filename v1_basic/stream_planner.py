from datetime import datetime
from pathlib import Path


def parse_schedule(input_filename: str, output_filename: str) -> None:
    input_path = Path(input_filename)
    output_path = Path(output_filename)

    # Safety check: Ensure the input file actually exists
    if not input_path.exists():
        print(f"[ERROR] Could not find the file: {input_filename}")
        print(
            f"[DEBUG] Python is currently looking in this exact folder:\n {Path.cwd()}"
        )
        return

    markdown_lines = [
        "# 🎮 Upcoming Stream Schedule & Content Plan\n",
        "Generated automatically via Python script.\n",
        "| Date | Game / Category | Stream Focus & Notes |",
        "| :--- | :--- | :--- |",
    ]

    # Read and parse the raw text file
    with open(input_path, "r", encoding="utf-8") as file:
        for line in file:
            # Skip empty lines
            if not line.strip():
                continue

            # Split the line by the pipe character '|'
            parts = line.split("|")
            if len(parts) < 3:
                continue

            # Extract and clean up the data fields
            date_raw = parts[0].replace("date:", "").strip()
            game = parts[1].replace("game:", "").strip()
            notes = parts[2].replace("notes:", "").strip()

            # Format the date to look cleaner (e.g., "Jun 08, 2026")
            try:
                date_obj = datetime.strptime(date_raw, "%Y-%m-%d")
                friendly_date = date_obj.strftime("%b %d, %Y")
            except ValueError:
                friendly_date = date_raw  # Fallback if date format is weird

            # Append a formatted markdown table row
            markdown_lines.append(f"| **{friendly_date}** | {game} | {notes} |")

    # Write the compiled lines out to the Markdown file
    with open(output_path, "w", encoding="utf-8") as file:
        file.write("\n".join(markdown_lines))

    print(f"[SUCCESS] Beautiful schedule exported to: {output_path.resolve()}")


if __name__ == "__main__":
    parse_schedule("messy_notes.txt", "SCHEDULE.md")
