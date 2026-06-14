# 🚀 Real-Time Event-Driven Streaming Telemetry Pipeline

An enterprise-grade, local-first data engineering pipeline designed to safely ingest, validate, and analyze live broadcast telemetry streams. This system leverages event-driven automatic architectures to parse edge payloads, validate metrics against a strict organizational schema, and dispatch metrics cleanly to a simulated cloud storage ecosystem for real-time analytics.

---

## 🏗️ System Architecture

The pipeline processing flow is engineered as follows:

1. **Telemetry Edge Generation:** Simulated or actual live broadcast statistics are saved as raw payloads in an edge folder directory.
2. **Heartbeat Polling Ingestion Daemon:** A lightweight, localized background engine continually scans the ingestion directory to intercept newly deployed files.
3. **Pydantic Validation Guard:** Edge schemas are strictly checked for anomalies (e.g., negative viewer limits, corrupted boundaries) before network operations execute.
4. **Mock Cloud Dispatch** Validated streams are cleanly shipped via an encrypted/isolated Boto3 worker into a Dockerized LocalStack S3 bucket environment.
5. **Interactive Analytical UI:** A live Streamlit application automatically visualizes stream metrics over time using Plotly-driven interactive time-series plots.

---

## 🛠️ Techincal Stack & Frameworks

* **Primary Language:** Python 3.x
* **Validation & Security:** Pydantic V2, Python-Dotenv
* **Infrastructure & Containerization:** Docker, Docker-Compose, Terraform, LocalStack (S3)
* **Frontend Analytics:** Streamlit, Plotly Express
* **Quality Assurance Suites:** Pytest

---

## 🚀 Local Installation & Deployment Guide

Follow these steps to run the complete end-to-end cloud pipeline environment natively on your machine:

### 1. Initialize Local Infrastructure
Ensure Docker Desktop is running, then spin up your mock cloud infrastructure environment:
```bash
docker-compose up -d