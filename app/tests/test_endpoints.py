from fastapi.testclient import TestClient

from app import data
from app.main import app


client = TestClient(app)


def setup_function() -> None:
    data.clear_data()


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_csv_returns_metadata() -> None:
    response = client.post(
        "/data/upload",
        files={
            "file": (
                "weather.csv",
                b"city,temp_c\nMalmo,8.3\nLund,7.9\n",
                "text/csv",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["rows"] == 2
    assert response.json()["columns"] == ["city", "temp_c"]
    assert response.json()["dtypes"]["temp_c"] == "float64"


def test_stats_without_dataset_returns_404() -> None:
    response = client.get("/data/stats")

    assert response.status_code == 404


def test_stats_after_upload_returns_describe_data() -> None:
    client.post(
        "/data/upload",
        files={
            "file": (
                "weather.csv",
                b"city,temp_c\nMalmo,8.3\nLund,7.9\n",
                "text/csv",
            )
        },
    )

    response = client.get("/data/stats")

    assert response.status_code == 200
    assert "temp_c" in response.json()["stats"]
