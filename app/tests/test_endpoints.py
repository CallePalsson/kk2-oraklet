from fastapi.testclient import TestClient

from app import data
from app.main import app
from app.schemas import ResponseParserOutput


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
                "water.csv",
                b"place,water_temp_c\nBryggan,21.4\nStranden,19.8\n",
                "text/csv",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["rows"] == 2
    assert response.json()["columns"] == ["place", "water_temp_c"]
    assert response.json()["dtypes"]["water_temp_c"] == "float64"


def test_stats_without_dataset_returns_404() -> None:
    response = client.get("/data/stats")

    assert response.status_code == 404


def test_stats_after_upload_returns_describe_data() -> None:
    client.post(
        "/data/upload",
        files={
            "file": (
                "water.csv",
                b"place,water_temp_c\nBryggan,21.4\nStranden,19.8\n",
                "text/csv",
            )
        },
    )

    response = client.get("/data/stats")

    assert response.status_code == 200
    assert "water_temp_c" in response.json()["stats"]


def test_ask_without_dataset_returns_400() -> None:
    response = client.post(
        "/ai/ask",
        json={"question": "Vilken badplats har varmast vatten?"},
    )

    assert response.status_code == 400


def test_ask_returns_answer_from_chain(monkeypatch) -> None:
    class FakeChain:
        def invoke(self, value) -> ResponseParserOutput:
            return ResponseParserOutput(
                question=value.question,
                answer="Bryggan har varmast vatten.",
                model="fake-model",
            )

    data.save_csv(
        b"place,water_temp_c\nBryggan,21.4\nStranden,19.8\n"
    )
    monkeypatch.setattr("app.main.build_chain", lambda: FakeChain())

    response = client.post(
        "/ai/ask",
        json={"question": "Vilken badplats har varmast vatten?"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "question": "Vilken badplats har varmast vatten?",
        "answer": "Bryggan har varmast vatten.",
        "model": "fake-model",
    }
