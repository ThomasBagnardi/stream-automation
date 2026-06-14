import json
import os

from pydantic import BaseModel, Field


class StreamTelemetry(BaseModel):
    viewer_count: int = Field(ge=0)
    bitrate_kbps: int = Field(ge=1000, le=12000)


print("🔍 --- STEP 1: SCANNING DIRECTORY ---")
target_dir = "./stream_drops"
files = os.listdir(target_dir)
print(f"Files found in {target_dir}: {files}")

print("\n🔍 --- STEP 2: TESTING RE-READ & VALIDATION ---")
for f in files:
    if f.endswith(".json"):
        file_path = os.path.join(target_dir, f)
        print(f"\n📄 Reading file: {f}")
        try:
            with open(file_path, "r") as file:
                content = file.read()
                print(f"Raw Content: '{content.strip()}")

                # Try parsing raw json
                data = json.loads(content)
                print("JSON Parse: Success ✅")

                # Try validation
                validated = StreamTelemetry(**data)
                print(f"Pydantic Validation: Passed ✅ -> {validated.dict()}")
        except Exception as e:
            print(f"❌ Error processing {f}: {type(e).__name__} - {e}")
