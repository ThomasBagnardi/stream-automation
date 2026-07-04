FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY metrics_server.py .
COPY start.sh .

EXPOSE 8501
EXPOSE 8000

CMD ["/bin/sh", "start.sh"]
