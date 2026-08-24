# 🖥️ MonitorX — Real-Time Cloud & System Monitoring Platform

[![MonitorX CI/CD Pipeline](https://github.com/khushiyadavgj-cmyk/monitorx/actions/workflows/ci.yml/badge.svg)](https://github.com/khushiyadavgj-cmyk/monitorx/actions)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Exporter-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-Configured-F46800?logo=grafana&logoColor=white)](https://grafana.com/)

A modern, real-time system and cloud container monitoring platform built with **FastAPI**, **Docker**, **Prometheus**, **Grafana**, and **WebSockets**.

---

## ✨ Features

- 📊 **Real-Time System Metrics**: Live CPU, Memory, Root Disk usage, Network I/O, and Uptime tracking.
- ⚡ **Task Manager (Top Processes)**: Displays the highest CPU and RAM-consuming active processes.
- 🐳 **Docker Container Monitoring**: Inspects active and stopped containers directly via the Docker SDK.
- 🚨 **Automated Incident & Alert Engine**: Configurable safety thresholds with visual pulsating warning banners and timestamped incident logs.
- 📈 **Time-Series Charts**: Dynamic historical graphs powered by Chart.js.
- 🔌 **Prometheus & Grafana Ready**: Exposes `/prometheus-metrics` and orchestrates a complete monitoring stack via Docker Compose.
- 🧪 **Automated Testing Suite**: Comprehensive unit and integration tests using `pytest` and FastAPI `TestClient`.
- ⚙️ **CI/CD Pipeline**: Automated GitHub Actions testing and Docker container build verification on every push.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn, Psutil, Docker SDK, Prometheus Client
- **Frontend**: HTML5, CSS3 (Slate Dark Theme), Vanilla JS, WebSockets, Chart.js
- **DevOps & Containers**: Docker, Docker Compose, Prometheus, Grafana
- **CI/CD & Testing**: Pytest, Httpx, GitHub Actions

---

## 🚀 Getting Started

### 1. Local Setup

```bash
# Clone the repository
git clone https://github.com/khushiyadavgj-cmyk/monitorx.git
cd monitorx

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the development server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at **`http://localhost:8000`**.

---

### 2. Run with Docker Compose (Full Cloud Stack)

```bash
docker compose up --build -d
```

- **MonitorX Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Prometheus Targets**: [http://localhost:9090/targets](http://localhost:9090/targets)
- **Grafana UI**: [http://localhost:3000](http://localhost:3000) *(User: `admin` / Password: `admin`)*

---

### 3. Run Automated Tests

```bash
pytest -v
```

---

## 📄 License
MIT License
