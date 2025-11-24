import json
import warnings
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
from flask import Flask, jsonify, render_template_string, request

BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "archivos"
MODEL_PATH = ARTIFACTS_DIR / "modelo_regresion_logistica.pkl"
SCALER_PATH = ARTIFACTS_DIR / "scaler.pkl"
INFO_PATH = ARTIFACTS_DIR / "modelo_regresion_logistica_info.json"


def load_artifacts() -> Tuple[object, object, List[str], Dict]:
    """Load model, scaler and feature metadata from disk."""
    with INFO_PATH.open(encoding="utf-8", errors="ignore") as fp:
        meta = json.load(fp)

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    features: List[str] = meta.get("features") or []
    if not features and hasattr(model, "feature_names_in_"):
        features = list(model.feature_names_in_)

    return model, scaler, features, meta


model, scaler, FEATURE_NAMES, MODEL_META = load_artifacts()

CLASS_LABELS = {
    1: "Fallece",  # dataset labels: 1=death, 2=live
    2: "Sobrevive",
}

app = Flask(__name__)


def prepare_features(payload: Dict) -> Tuple[np.ndarray, Dict[str, float]]:
    missing = [name for name in FEATURE_NAMES if name not in payload]
    if missing:
        raise ValueError(f"Faltan campos: {', '.join(missing)}")

    ordered_values: List[float] = []
    numeric_payload: Dict[str, float] = {}
    for name in FEATURE_NAMES:
        raw_value = payload[name]
        try:
            numeric_value = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Valor invalido para '{name}': {raw_value}") from exc
        ordered_values.append(numeric_value)
        numeric_payload[name] = numeric_value

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        scaled = scaler.transform([ordered_values])
    return scaled, numeric_payload


@app.get("/health")
def health() -> Tuple[Dict[str, str], int]:
    return {"status": "ok"}, 200


@app.post("/predict")
def predict() -> Tuple[object, int]:
    data = request.get_json(silent=True) or {}
    try:
        transformed, numeric_payload = prepare_features(data)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            prediction = model.predict(transformed)[0]
            proba = None
            if hasattr(model, "predict_proba"):
                proba = float(model.predict_proba(transformed)[0].max())

        response = {
            "prediction": int(prediction),
            "label": CLASS_LABELS.get(int(prediction), str(prediction)),
            "probability": proba,
            "inputs": numeric_payload,
            "model_meta": {
                "modelo": MODEL_META.get("modelo"),
                "n_features": MODEL_META.get("n_features"),
            },
        }
        return jsonify(response), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # pragma: no cover - safety net
        return jsonify({"error": "Error interno", "detail": str(exc)}), 500


@app.get("/")
def index() -> str:
    template = """
    <!doctype html>
    <html lang="es">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Hepatitis - Regresion Logistica</title>
      <style>
        :root { color-scheme: light; }
        body {
          margin: 0;
          font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
          background: radial-gradient(circle at 10% 20%, #eef2ff 0, #f8fafc 35%, #ffffff 100%);
          color: #0f172a;
        }
        header { padding: 24px 16px 12px; text-align: center; }
        h1 { margin: 0; font-size: 28px; letter-spacing: -0.02em; }
        p.lead { margin: 4px 0 0; color: #475569; }
        main {
          max-width: 900px;
          margin: 0 auto;
          padding: 16px;
          display: grid;
          gap: 12px;
          grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        }
        section { background: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06); }
        h2 { margin-top: 0; font-size: 18px; }
        form { display: grid; gap: 10px; }
        label { font-weight: 600; font-size: 14px; display: flex; justify-content: space-between; }
        input, select {
          width: 100%;
          padding: 10px 12px;
          border-radius: 10px;
          border: 1px solid #cbd5e1;
          background: #f8fafc;
          font-size: 14px;
        }
        .help { font-size: 12px; color: #64748b; margin-top: 2px; }
        button {
          margin-top: 4px;
          padding: 12px 14px;
          background: linear-gradient(120deg, #0ea5e9, #6366f1);
          color: #fff;
          border: none;
          border-radius: 10px;
          font-weight: 700;
          cursor: pointer;
          transition: transform 120ms ease, box-shadow 120ms ease;
        }
        button:hover { transform: translateY(-1px); box-shadow: 0 10px 20px rgba(99, 102, 241, 0.25); }
        pre { background: #0f172a; color: #e2e8f0; padding: 12px; border-radius: 10px; font-size: 12px; overflow-x: auto; min-height: 120px; }
      </style>
    </head>
    <body>
      <header>
        <h1>Prediccion de Hepatitis</h1>
        <p class="lead">Modelo: {{ model_name }} ({{ feature_count }} variables)</p>
        <p class="lead">Valores binarios usan 1/2 del dataset; los numericos requieren escala original.</p>
      </header>
      <main>
        <section>
          <h2>Formulario rapido</h2>
          <form id="predict-form">
            {% for name in feature_names %}
              <div>
                <label for="{{ name }}">{{ name }}</label>
                <input id="{{ name }}" name="{{ name }}" type="number" step="any" required />
                <div class="help">{{ helper.get(name, "Ingrese valor numerico segun dataset") }}</div>
              </div>
            {% endfor %}
            <button type="submit">Predecir</button>
          </form>
        </section>
        <section>
          <h2>Respuesta</h2>
          <pre id="result">Pendiente...</pre>
        </section>
      </main>
      <script>
        const helper = {{ helper|tojson }};
        const form = document.getElementById('predict-form');
        const resultEl = document.getElementById('result');

        form.addEventListener('submit', async (event) => {
          event.preventDefault();
          const formData = new FormData(form);
          const payload = Object.fromEntries([...formData.entries()].map(([k,v]) => [k, v || null]));
          resultEl.textContent = 'Calculando...';
          try {
            const resp = await fetch('/predict', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify(payload),
            });
            const data = await resp.json();
            resultEl.textContent = JSON.stringify(data, null, 2);
          } catch (err) {
            resultEl.textContent = 'Error: ' + err;
          }
        });
      </script>
    </body>
    </html>
    """
    helpers = {
        "Sex": "1=masculino, 2=femenino",
        "Steroid": "1=si, 2=no",
        "Antivirals": "1=si, 2=no",
        "Fatigue": "1=si, 2=no",
        "Malaise": "1=si, 2=no",
        "Anorexia": "1=si, 2=no",
        "Liver_Big": "1=si, 2=no",
        "Liver_Firm": "1=si, 2=no",
        "Spleen_Palpable": "1=si, 2=no",
        "Spiders": "1=si, 2=no",
        "Ascites": "1=si, 2=no",
        "Varices": "1=si, 2=no",
        "Histology": "1=si, 2=no",
        "Estado_Civil": "Codificacion numerica usada en el dataset original",
        "Ciudad": "Codificacion numerica usada en el dataset original",
    }
    return render_template_string(
        template,
        feature_names=FEATURE_NAMES,
        model_name=MODEL_META.get("modelo", "Regresion Logistica"),
        feature_count=len(FEATURE_NAMES),
        helper=helpers,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
