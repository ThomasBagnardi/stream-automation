# 1. Official, lightweight Python base image
FROM python:3.9-slim

# 2. Set working directory inside container
WORKDIR /app

# 3. Copy dependency manifest and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy entire v2_upgraded development folder into container
COPY v2_upgraded/ .

# 5. Execute stream planner script automatically when container boots!
CMD ["python", "stream_planner_v2.py"]