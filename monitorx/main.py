from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pathlib import Path
from datetime import datetime
import asyncio
import psutil
import time
import docker

app = FastAPI(title="MonitorX")
start_time = time.time()

try:
    from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
    HAS_PROMETHEUS = True
    PROM_CPU = Gauge("monitorx_cpu_percent", "System CPU Usage Percentage")
    PROM_MEMORY = Gauge("monitorx_memory_percent", "System Memory Usage Percentage")
    PROM_DISK = Gauge("monitorx_disk_percent", "Root Disk Usage Percentage")
    PROM_NET_SENT = Gauge("monitorx_network_bytes_sent", "Total Network Bytes Sent")
    PROM_NET_RECV = Gauge("monitorx_network_bytes_recv", "Total Network Bytes Received")
    PROM_DOCKER_TOTAL = Gauge("monitorx_docker_containers_total", "Total Docker Containers")
    PROM_DOCKER_RUNNING = Gauge("monitorx_docker_containers_running", "Running Docker Containers")
except ImportError:
    HAS_PROMETHEUS = False

# Store recent alert history (capped at last 10)
alert_history = []

THRESHOLDS = {
    "cpu_warning": 80.0,
    "cpu_critical": 90.0,
    "memory_warning": 80.0,
    "memory_critical": 90.0,
    "disk_warning": 85.0,
    "disk_critical": 95.0,
}


def get_top_processes(limit=6):
    """Retrieve top running processes sorted by CPU usage."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
        try:
            info = proc.info
            if info['name']:
                processes.append({
                    "pid": info['pid'],
                    "name": info['name'],
                    "cpu_percent": info['cpu_percent'] or 0.0,
                    "memory_percent": round(info['memory_percent'] or 0.0, 1),
                    "status": info['status'] or "running"
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    processes.sort(key=lambda p: p['cpu_percent'], reverse=True)
    return processes[:limit]


def get_docker_stats():
    """Fetch live Docker container statistics safely."""
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        container_list = []
        running_count = 0

        for c in containers:
            is_running = c.status == "running"
            if is_running:
                running_count += 1

            image_name = c.image.tags[0] if c.image.tags else c.image.short_id

            container_list.append({
                "id": c.short_id,
                "name": c.name,
                "image": image_name,
                "status": c.status,
            })

        return {
            "available": True,
            "total": len(containers),
            "running": running_count,
            "stopped": len(containers) - running_count,
            "containers": container_list
        }
    except Exception:
        return {
            "available": False,
            "total": 0,
            "running": 0,
            "stopped": 0,
            "containers": [],
            "error": "Docker daemon is offline or unreachable"
        }


def check_alerts(cpu, memory, disk, docker_data):
    """Evaluate system metrics against alert thresholds."""
    current_alerts = []
    now_str = datetime.now().strftime("%H:%M:%S")

    if cpu >= THRESHOLDS["cpu_critical"]:
        current_alerts.append({
            "type": "CPU", "level": "critical",
            "message": f"Critical CPU spike: {cpu:.1f}%", "time": now_str
        })
    elif cpu >= THRESHOLDS["cpu_warning"]:
        current_alerts.append({
            "type": "CPU", "level": "warning",
            "message": f"High CPU usage: {cpu:.1f}%", "time": now_str
        })

    if memory >= THRESHOLDS["memory_critical"]:
        current_alerts.append({
            "type": "Memory", "level": "critical",
            "message": f"Critical RAM usage: {memory:.1f}%", "time": now_str
        })
    elif memory >= THRESHOLDS["memory_warning"]:
        current_alerts.append({
            "type": "Memory", "level": "warning",
            "message": f"High RAM usage: {memory:.1f}%", "time": now_str
        })

    if disk >= THRESHOLDS["disk_critical"]:
        current_alerts.append({
            "type": "Disk", "level": "critical",
            "message": f"Critical disk space: {disk:.1f}% used", "time": now_str
        })
    elif disk >= THRESHOLDS["disk_warning"]:
        current_alerts.append({
            "type": "Disk", "level": "warning",
            "message": f"High disk space: {disk:.1f}% used", "time": now_str
        })

    if docker_data.get("available") and docker_data.get("stopped", 0) > 0:
        current_alerts.append({
            "type": "Docker", "level": "warning",
            "message": f"{docker_data['stopped']} container(s) stopped/unhealthy", "time": now_str
        })

    for alert in current_alerts:
        if not alert_history or alert_history[-1]["message"] != alert["message"]:
            alert_history.append(alert)
            if len(alert_history) > 10:
                alert_history.pop(0)

    return current_alerts


def collect_metrics_payload():
    """Build full metrics dictionary."""
    network = psutil.net_io_counters()
    uptime_seconds = int(time.time() - start_time)

    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    docker_data = get_docker_stats()
    top_processes = get_top_processes(limit=6)

    if HAS_PROMETHEUS:
        PROM_CPU.set(cpu)
        PROM_MEMORY.set(memory)
        PROM_DISK.set(disk)
        PROM_NET_SENT.set(network.bytes_sent)
        PROM_NET_RECV.set(network.bytes_recv)
        PROM_DOCKER_TOTAL.set(docker_data.get("total", 0))
        PROM_DOCKER_RUNNING.set(docker_data.get("running", 0))

    active_alerts = check_alerts(cpu, memory, disk, docker_data)

    return {
        "cpu_percent": cpu,
        "memory_percent": memory,
        "disk_percent": disk,
        "bytes_sent": network.bytes_sent,
        "bytes_received": network.bytes_recv,
        "packets_sent": network.packets_sent,
        "packets_received": network.packets_recv,
        "uptime_seconds": uptime_seconds,
        "docker": docker_data,
        "processes": top_processes,
        "alerts": active_alerts,
        "alert_history": list(reversed(alert_history))
    }


@app.get("/", response_class=HTMLResponse)
def home():
    html_file = Path("templates/index.html")
    return html_file.read_text()


@app.get("/metrics")
def metrics():
    return collect_metrics_payload()


@app.websocket("/ws/metrics")
async def websocket_metrics_endpoint(websocket: WebSocket):
    """Real-time bi-directional WebSocket streaming endpoint."""
    await websocket.accept()
    try:
        while True:
            payload = collect_metrics_payload()
            await websocket.send_json(payload)
            await asyncio.sleep(1)  # Stream updates every 1 second
    except (WebSocketDisconnect, Exception):
        pass


@app.get("/prometheus-metrics")
def prometheus_metrics():
    """Endpoint for Prometheus scraper."""
    if not HAS_PROMETHEUS:
        return Response(content="prometheus_client not installed", media_type="text/plain")
    collect_metrics_payload()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)