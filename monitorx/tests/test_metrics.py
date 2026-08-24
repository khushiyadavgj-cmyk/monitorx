from fastapi.testclient import TestClient
from main import app, check_alerts

client = TestClient(app)


def test_home_page_status():
    """Verify that the dashboard HTML page loads with HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200
    assert "MonitorX" in response.text


def test_metrics_endpoint_structure():
    """Verify that /metrics returns valid JSON with all required keys."""
    response = client.get("/metrics")
    assert response.status_code == 200

    data = response.json()

    # Check that all expected monitoring keys exist
    expected_keys = [
        "cpu_percent",
        "memory_percent",
        "disk_percent",
        "bytes_sent",
        "bytes_received",
        "packets_sent",
        "packets_received",
        "uptime_seconds",
        "docker",
        "alerts",
        "alert_history"
    ]

    for key in expected_keys:
        assert key in data, f"Missing expected key: {key}"


def test_metrics_value_ranges():
    """Verify that CPU, Memory, and Disk percentages are within valid [0, 100] ranges."""
    response = client.get("/metrics")
    assert response.status_code == 200

    data = response.json()

    assert 0.0 <= data["cpu_percent"] <= 100.0
    assert 0.0 <= data["memory_percent"] <= 100.0
    assert 0.0 <= data["disk_percent"] <= 100.0
    assert data["uptime_seconds"] >= 0


def test_docker_metrics_structure():
    """Verify Docker data returns standard dictionary fields."""
    response = client.get("/metrics")
    assert response.status_code == 200

    data = response.json()
    docker_data = data["docker"]

    assert "available" in docker_data
    assert "total" in docker_data
    assert "running" in docker_data
    assert "stopped" in docker_data
    assert isinstance(docker_data["containers"], list)


def test_alert_evaluation_logic():
    """Verify that the check_alerts function triggers alerts on high resource spikes."""
    dummy_docker = {"available": True, "stopped": 0}

    # 1. Healthy system -> 0 alerts
    healthy_alerts = check_alerts(cpu=20.0, memory=40.0, disk=50.0, docker_data=dummy_docker)
    assert len(healthy_alerts) == 0

    # 2. High CPU (95%) -> Critical CPU alert
    spike_alerts = check_alerts(cpu=95.0, memory=40.0, disk=50.0, docker_data=dummy_docker)
    assert len(spike_alerts) >= 1
    assert any(a["type"] == "CPU" and a["level"] == "critical" for a in spike_alerts)


def test_prometheus_metrics_endpoint():
    """Verify that /prometheus-metrics endpoint is reachable."""
    response = client.get("/prometheus-metrics")
    assert response.status_code == 200