import os

from dotenv import load_dotenv

load_dotenv()

env_val = os.getenv("WATCH_DIR")
absolute_path = os.path.abspath(env_val) if env_val else "None"

print(f"1. Raw '.env' WATCH_DIR value: {env_val}")
print(f"2. Absolute path Python is looking for {absolute_path}")
print(f"3. Does that physical folder exist? {os.path.exists(absolute_path)}")
print(f"4. Current Working Directory of terminal: {os.getcwd()}")
