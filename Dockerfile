# Step 1: Use an official, lightweight Python runtime as a parent image
FROM python:3.11-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy your local script and date file into the container's /app folder
COPY v2_upgraded/stream_planner_v2.py ./stream_planner.py
COPY v2_upgraded/messy_notes.txt ./messy_notes.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Run the script automatically when the container starts
CMD ["python", "stream_planner.py"]