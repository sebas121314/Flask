from app import FEATURE_NAMES, app


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_predict_endpoint_accepts_payload():
    client = app.test_client()
    sample_payload = {
        "Age": 45,
        "Sex": 1,
        "Estado_Civil": 1,
        "Ciudad": 2,
        "Steroid": 1,
        "Antivirals": 2,
        "Fatigue": 1,
        "Malaise": 1,
        "Anorexia": 2,
        "Liver_Big": 1,
        "Liver_Firm": 2,
        "Spleen_Palpable": 2,
        "Spiders": 2,
        "Ascites": 2,
        "Varices": 2,
        "Bilirubin": 1.2,
        "Alk_Phosphate": 85,
        "Sgot": 45,
        "Albumin": 4.0,
        "Protime": 60,
        "Histology": 1,
    }

    assert set(sample_payload.keys()) == set(FEATURE_NAMES)

    response = client.post("/predict", json=sample_payload)
    assert response.status_code == 200
    data = response.get_json()

    assert "prediction" in data
    assert "inputs" in data
    assert data["inputs"]["Age"] == sample_payload["Age"]
