# Live Streaming Analytics Pipeline

A production-grade data pipeline that parses stream schedule data, generates analytics records, uploads them to AWS S3, and surfaces them on a live public dashboard. Deployed to real cloud infrastructure — not a mock environment.

**Live Demo:** https://stream-automation-we63gp6v3jzbfbpfokd4q3.streamlit.app

---

## Architecture

```
messy_notes.txt
      │
      ▼
stream_planner_v2.py     ← parses schedule, generates SCHEDULE.md
      │
      ▼
generate_analytics.py    ← generates JSON analytics records
      │
      ▼
AWS S3 (us-east-2)       ← stores analytics JSON
      │
      ▼
app.py (Streamlit)       ← reads from S3, renders dashboard
      │
      ▼
Streamlit Community Cloud ← live public URL
```

**Kubernetes cluster (kind):**
```
CronJob (hourly)
      │
      ▼
analytics-generator pod  ← runs generate_analytics.py on schedule
      │
      ▼
AWS S3
      │
      ▼
streamlit-dashboard pod  ← serves the dashboard
      │
      ▼
ClusterIP Service        ← internal cluster networking

Prometheus               ← scrapes custom metrics every 30s
      │
      ▼
Grafana                  ← Stream Pipeline Monitoring dashboard
```

---

## Tech Stack

| Category | Tools |
|---|---|
| Language | Python 3.11 |
| Cloud | AWS S3 (boto3), IAM |
| Containers | Docker, Docker Compose |
| Orchestration | Kubernetes (kind, kubectl) |
| Package Management | Helm |
| Infrastructure | Terraform |
| Monitoring | Prometheus, Grafana |
| CI/CD | GitHub Actions |
| Dashboard | Streamlit, Plotly |
| Data Quality | Pydantic, Watchdog, Pytest |
| Deployment | Streamlit Community Cloud |

---

## Features

- **Real AWS S3** — production cloud storage with IAM-scoped credentials and environment-based secret management
- **Kubernetes deployment** — six resource types: Namespace, Secret, ConfigMap, Deployment, Service, CronJob
- **Helm monitoring stack** — kube-prometheus-stack with custom Prometheus metrics and a five-panel Grafana dashboard
- **Scheduled data generation** — CronJob runs generate_analytics.py hourly, pushing fresh records to S3
- **Data quality gate** — Watchdog file monitoring + Pydantic schema validation blocks bad records before they enter the pipeline
- **CI/CD** — GitHub Actions rebuilds containers and runs the full Pytest suite on every push
- **Live public dashboard** — deployed to Streamlit Community Cloud

---

## Custom Prometheus Metrics

The pipeline exposes the following metrics at `:8000/metrics`:

| Metric | Type | Description |
|---|---|---|
| `streamlit_s3_fetch_total` | Counter | Total S3 fetch operations |
| `streamlit_s3_fetch_errors_total` | Counter | Total S3 fetch errors |
| `streamlit_s3_records_fetched` | Gauge | Records fetched in last cycle |
| `streamlit_s3_fetch_duration_seconds` | Histogram | S3 fetch latency |
| `stream_pipeline_app_info` | Gauge | App version info |

---

## Local Setup

### Prerequisites

- Python 3.11+
- Docker Desktop
- AWS account with S3 bucket and IAM credentials

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment

Create a `.env` file in the project root:

```
AWS_ACCESS_KEY_ID=your_key_id
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-2
AMAZON_S3_BUCKET_NAME=your_bucket_name
```

### Generate and upload analytics data

```bash
cd v2_upgraded
python generate_analytics.py
```

### Run the dashboard locally

```bash
streamlit run app.py
```

---

## Kubernetes Deployment

### Prerequisites

- kind
- kubectl
- Helm

### Create cluster

```bash
kind create cluster --name stream-pipeline
```

### Deploy pipeline

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create credentials secret
kubectl create secret generic aws-credentials \
  --namespace stream-pipeline \
  --from-literal=AWS_ACCESS_KEY_ID="your_key" \
  --from-literal=AWS_SECRET_ACCESS_KEY="your_secret" \
  --from-literal=AMAZON_S3_BUCKET_NAME="your_bucket"

# Deploy config, dashboard, and scheduler
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/cronjob.yaml
```

### Deploy monitoring stack

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set grafana.adminPassword=admin \
  --set prometheus.prometheusSpec.scrapeInterval=30s

kubectl apply -f k8s/servicemonitor.yaml
```

### Access the dashboard

```bash
kubectl port-forward service/streamlit-dashboard 8080:80 -n stream-pipeline
```

Open http://localhost:8080

### Access Grafana

```bash
kubectl port-forward -n monitoring service/kube-prometheus-stack-grafana 3000:80
```

Open http://localhost:3000 — login: `admin` / `admin`

Import `k8s/grafana/stream-pipeline-dashboard.json` to load the Stream Pipeline Monitoring dashboard.

---

## Project Structure

```
├── app.py                        # Streamlit dashboard
├── metrics_server.py             # Prometheus metrics server
├── start.sh                      # Container startup script
├── Dockerfile                    # Dashboard image
├── Dockerfile.generator          # Analytics generator image
├── requirements.txt
├── v2_upgraded/
│   ├── stream_planner_v2.py      # Schedule parser
│   ├── generate_analytics.py     # Analytics generator
│   ├── upload_payloads.py        # S3 upload utility
│   └── messy_notes.txt           # Raw schedule input
├── k8s/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── cronjob.yaml
│   ├── servicemonitor.yaml
│   └── grafana/
│       └── stream-pipeline-dashboard.json
└── .github/
    └── workflows/                # GitHub Actions CI/CD
```

---

## CI/CD

GitHub Actions runs on every push to `main`:
- Rebuilds Docker containers
- Runs the full Pytest suite including Pydantic schema validation tests
- Catches regressions before they reach the main branch
